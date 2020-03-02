from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from slugify import slugify
from core.models import *
from member.forms import *
from .forms import *
from core.views import create_ref_code

# standardised variables

ADDRESS_CHOICES = [
    {'key': 'B', 'name': 'Fakturaaddress'},
    {'key': 'S', 'name': 'Leveransaddress'},
]

ADDRESS_CHOICES_EXTENDED = [
    {'key': 'B', 'name': 'Fakturaaddress'},
    {'key': 'S', 'name': 'Leveransaddress'},
    {'key': 'BOTH', 'name': 'Båda'},
]

# reused functions


def where_am_i(self):
    path = self.request.get_full_path()
    split_path = path.split("/")
    page = split_path[-1]
    if page == "":
        page = split_path[-2]
    return page


def test_slug_company(slug):
    test = False
    companyQuery = CompanyInfo.objects.filter(slug=slug)
    if len(companyQuery) > 0:
        test = True
    return test


def create_slug_address(address):
    toSlug = address.street_address + \
        "B" + str(address.user.id)
    testSlug = slugify(toSlug)
    existingSlug = test_slug_address(testSlug)
    i = 1
    while existingSlug:
        toSlug = address.street_address + \
            "B" + str(address.user.id) + "_" + str(i)
        testSlug = slugify(toSlug)
        existingSlug = test_slug_address(testSlug)
        i += 1

    return testSlug


def test_slug_address(slug):
    test = False
    addressQuery = Address.objects.filter(slug=slug)
    if len(addressQuery) > 0:
        test = True
    return test


def new_address_default(address):
    # remove default from any other default address of the same type
    otherAddresses = Address.objects.filter(
        address_type=address.address_type, default=True)
    for otherAddress in otherAddresses:
        otherAddress.default = False
        otherAddress.save()


def get_next_order_date(subdate, intervall):
    if intervall == '001':
        # add a week
        d = timedelta(days=7)
        add_date = subdate
        next_date = add_date + d

        return next_date

    elif intervall == '002':
        # add two weeks
        d = timedelta(days=14)
        add_date = subdate
        next_date = add_date + d

        return next_date

    elif intervall == '010':
        # add a month
        d = timedelta(days=30)
        add_date = subdate
        next_date = add_date + d

        return next_date
    elif intervall == '020':
        # add two months
        d = timedelta(days=60)
        add_date = subdate
        next_date = add_date + d

        return next_date
    elif intervall == '100':
        # add six months
        d = timedelta(days=182)
        add_date = subdate
        next_date = add_date + d

        return next_date
    elif intervall == '200':
        # add a year
        d = timedelta(days=365)
        add_date = subdate
        next_date = add_date + d

        return next_date
    else:
        # this shouldnt be able to happen. do nothing
        return subdate


def save_subItems_and_orderItems(theUser, sub, amount, product):
    # create a subscription item object
    subItem = SubscriptionItem()
    subItem.user = theUser
    subItem.subscription = sub
    subItem.item = product
    subItem.item_title = product.title
    subItem.price = product.price
    discount_price = 1
    if product.discount_price is not None:
        discount_price = product.discount_price
    subItem.discount_price = discount_price
    subItem.quantity = amount
    total_price = product.price * discount_price * amount
    subItem.total_price = total_price

    # new orderItem object
    orderItem = OrderItem()
    # set basic valeus
    orderItem.user = sub.user
    orderItem.ordered = True
    orderItem.item = product
    orderItem.title = product.title
    orderItem.quantity = subItem.quantity
    orderItem.price = product.price
    orderItem.discount_price = discount_price
    orderItem.total_price = total_price
    # save orderitem
    orderItem.save()
    # save subitems
    subItem.save()
    return orderItem


def sameAddress_moderator(theUser, form_street_address, form_post_town, form_address_type):
    # start by checking that we dont already have this address
    sameBilling = 0
    sameShipping = 0
    message = ''
    addresses = Address.objects.filter(user=theUser)
    for anAddress in addresses:
        if form_street_address == anAddress.street_address:
            if form_post_town == anAddress.post_town:
                if form_address_type == "A":
                    if anAddress.address_type == "S":
                        sameShipping = anAddress.id
                    elif anAddress.address_type == "B":
                        sameBilling = anAddress.id
                    return sameShipping, sameBilling, message

                elif anAddress.address_type == form_address_type:
                    message = "Address already exists"
                    if default and not anAddress.default:
                        # remove default from other addresses of same type

                        compAddresses = Address.objects.filter(
                            user=theUser, address_type=anAddress.address_type)
                        for sameAddress in compAddresses:
                            if sameAddress.default:
                                sameAddress.default = False
                                sameAddress.save()
                                testAddress = Address.objects.get(
                                    id=sameAddress.id)
                        # add default to this address
                        anAddress.default = True
                        anAddress.save()
                        message = "Address already exists. Default changed."
                    return sameShipping, sameBilling, message


# view classes

class Overview(View):
    def get(self, *args, **kwargs):
        try:

            # get the first ten unanswered support errands and the count of the unanswerd support errands

            try:
                support = SupportThread.objects.filter(last_responce=2)[:10]
                number_support = SupportThread.objects.filter(
                    last_responce=2).count()
            except ObjectDoesNotExist:
                support = {}
                number_support = 0

            # figure out how many pages of 10 there are
            # if there are only 10 or fewer pages will be 1

            pages = 1

            if number_support > 10:
                # if there are more we divide by ten
                pages = number_support / 10
                # see if there is a decimal
                numType = type(pages)
                # if there isn't an even number of ten make an extra page for the last group
                if numType == "Float":
                    pages += 1

            # create a list for a ul to work through

            more_support = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(pages):
                i += 1
                more_support.append({'number': i})

            # get the first ten unsent orders and the count of all unsent orders

            try:
                orders = Order.objects.filter(being_delivered=False)[:10]
                number_orders = Order.objects.filter(
                    being_delivered=False).count()
            except ObjectDoesNotExist:
                orders = {}
                number_orders = 0

            # figure out how many pages of 10 there are
            # if there are only 10 or fewer pages will be 1

            o_pages = 1

            if number_support > 10:
                # if there are more we divide by ten
                o_pages = number_support / 10
                # see if there is a decimal
                numType = type(o_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if numType == "Float":
                    o_pages += 1

            # create a list for a ul to work through

            more_orders = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(o_pages):
                i += 1
                more_orders.append({'number': i})

            # we are on the first page so set the page to that

            current_page_support = 1
            current_page_orders = 1

            context = {
                'support': support,
                'more_support': more_support,
                'orders': orders,
                'more_orders': more_orders,
                'current_page_support': current_page_support,
                'current_page_orders': current_page_orders,
            }

            """if len(responces_a) < 0:
                context.update({'responces_a': responces_a})

            if len(responces_r) < 0:
                context.update({'responces_r': responces_r})"""

            return render(self.request, "moderator/mod_overview.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing the overview. Contact the support for assistance.")
            return redirect("core:home")

    def post(self, *args, **kwargs):
        try:
            # get where we are

            current_page_support = int(
                self.request.POST['current_page_support'])
            current_page_orders = int(self.request.POST['current_page_orders'])

            if 'whichPageSupport' in self.request.POST.keys():
                whichPageSupport = int(self.request.POST['whichPageSupport'])
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    offset = whichPageSupport * 10
                    support = SupportThread.objects.filter(last_responce=2)[
                        10:offset]
                    number_support = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something is wrong in the page function. Report this issue to IT support.")
                    support = {}
                    number_support = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    pages = number_support / 10
                    # see if there is a decimal
                    numType = type(pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        pages += 1

                # create a list for a ul to work through

                more_support = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(pages):
                    i += 1
                    more_support.append({'number': i})

                # get the first ten unsent orders and the count of all unsent orders

                try:
                    offset = 0
                    if current_page_orders > 1:
                        offset = current_page_orders * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                    number_orders = Order.objects.filter(
                        being_delivered=False).count()
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                o_pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    o_pages = number_support / 10
                    # see if there is a decimal
                    numType = type(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        o_pages += 1

                # create a list for a ul to work through

                more_orders = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(o_pages):
                    i += 1
                    more_orders.append({'number': i})

                # fix the current pages
                current_page_support = whichPageSupport

                context = {
                    'support': support,
                    'more_support': more_support,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_support': current_page_support,
                    'current_page_orders': current_page_orders,
                }

                """if len(responces_a) < 0:
                    context.update({'responces_a': responces_a})

                if len(responces_r) < 0:
                    context.update({'responces_r': responces_r})"""

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'whichPageOrder' in self.request.POST.keys():
                whichPageOrder = int(self.request.POST['whichPageOrder'])
                current_page_order = whichPageOrder
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    offset = 0
                    if current_page_support > 1:
                        offset = current_page_support * 10
                    support = SupportThread.objects.filter(
                        last_responce=2)[10:offset]
                    number_support = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something is wrong in the page function. Report this issue to IT support.")
                    support = {}
                    number_support = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    pages = number_support / 10
                    # see if there is a decimal
                    numType = type(pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        pages += 1

                # create a list for a ul to work through

                more_support = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(pages):
                    i += 1
                    more_support.append({'number': i})

                # get the first ten unsent orders and the count of all unsent orders

                try:
                    offset = whichPageOrder * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                    number_orders = Order.objects.filter(
                        being_delivered=False).count()
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                o_pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    o_pages = number_support / 10
                    # see if there is a decimal
                    numType = type(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        o_pages += 1

                # create a list for a ul to work through

                more_orders = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(o_pages):
                    i += 1
                    more_orders.append({'number': i})

                context = {
                    'support': support,
                    'more_support': more_support,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_support': current_page_support,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'nextPageOrder' in self.request.POST.keys():
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    offset = 0
                    if current_page_support > 1:
                        offset = current_page_support * 10
                    support = SupportThread.objects.filter(
                        last_responce=2)[10:offset]
                    number_support = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something is wrong in the page function. Report this issue to IT support.")
                    support = {}
                    number_support = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    pages = number_support / 10
                    # see if there is a decimal
                    numType = type(pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        pages += 1

                # create a list for a ul to work through

                more_support = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(pages):
                    i += 1
                    more_support.append({'number': i})

                # get the first ten unsent orders and the count of all unsent orders

                try:
                    number_orders = Order.objects.filter(
                        being_delivered=False).count()
                    whichPageOrder = 1
                    if current_page_orders < (number_orders / 10):
                        whichPageOrder = current_page_orders + 1
                    offset = whichPageOrder * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                o_pages = 1

                if number_orders > 10:
                    # if there are more we divide by ten
                    o_pages = number_orders / 10
                    # see if there is a decimal
                    numType = type(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        o_pages += 1

                # create a list for a ul to work through

                more_orders = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(o_pages):
                    i += 1
                    more_orders.append({'number': i})

                context = {
                    'support': support,
                    'more_support': more_support,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_support': current_page_support,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'previousPageOrder' in self.request.POST.keys():
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    offset = 0
                    if current_page_support > 1:
                        offset = current_page_support * 10
                    support = SupportThread.objects.filter(
                        last_responce=2)[10:offset]
                    number_support = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something is wrong in the page function. Report this issue to IT support.")
                    support = {}
                    number_support = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    pages = number_support / 10
                    # see if there is a decimal
                    numType = type(pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        pages += 1

                # create a list for a ul to work through

                more_support = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(pages):
                    i += 1
                    more_support.append({'number': i})

                # get the first ten unsent orders and the count of all unsent orders

                try:
                    whichPageOrder = 1
                    if current_page_orders > 1:
                        whichPageOrder = current_page_orders - 1
                    offset = whichPageOrder * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                    number_orders = Order.objects.filter(
                        being_delivered=False).count()
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                o_pages = 1

                if number_orders > 10:
                    # if there are more we divide by ten
                    o_pages = number_orders / 10
                    # see if there is a decimal
                    numType = type(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        o_pages += 1

                # create a list for a ul to work through

                more_orders = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(o_pages):
                    i += 1
                    more_orders.append({'number': i})

                context = {
                    'support': support,
                    'more_support': more_support,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_support': current_page_support,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'nextPageSupport' in self.request.POST.keys():
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    number_support = Order.objects.filter(
                        being_delivered=False).count()
                    whichPageSupport = 1
                    if current_page_support < (number_support / 10):
                        whichPageSupport = current_page_support + 1
                    offset = whichPageSupport * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something is wrong in the page function. Report this issue to IT support.")
                    support = {}
                    number_support = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    pages = number_support / 10
                    # see if there is a decimal
                    numType = type(pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        pages += 1

                # create a list for a ul to work through

                more_support = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(pages):
                    i += 1
                    more_support.append({'number': i})

                # get the first ten unsent orders and the count of all unsent orders

                try:
                    offset = 0
                    if current_page_orders > 1:
                        offset = current_page_orders * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                    number_orders = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                o_pages = 1

                if number_orders > 10:
                    # if there are more we divide by ten
                    o_pages = number_orders / 10
                    # see if there is a decimal
                    numType = type(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        o_pages += 1

                # create a list for a ul to work through

                more_orders = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(o_pages):
                    i += 1
                    more_orders.append({'number': i})

                context = {
                    'support': support,
                    'more_support': more_support,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_support': current_page_support,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'previousPageSupport' in self.request.POST.keys():
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    whichPageSupport = 1
                    if current_page_support > 1:
                        whichPageSupport = current_page_support - 1
                    offset = whichPageSupport * 10
                    support = SupportThread.objects.filter(
                        last_responce=2)[10:offset]
                    number_support = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something is wrong in the page function. Report this issue to IT support.")
                    support = {}
                    number_support = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                pages = 1

                if number_support > 10:
                    # if there are more we divide by ten
                    pages = number_support / 10
                    # see if there is a decimal
                    numType = type(pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        pages += 1

                # create a list for a ul to work through

                more_support = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(pages):
                    i += 1
                    more_support.append({'number': i})

                # get the first ten unsent orders and the count of all unsent orders

                try:
                    offset = 0
                    if current_page_orders > 1:
                        offset = current_page_orders * 10
                    orders = Order.objects.filter(
                        being_delivered=False)[10:offset]
                    number_orders = SupportThread.objects.filter(
                        last_responce=2).count()
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages of 10 there are
                # if there are only 10 or fewer pages will be 1

                o_pages = 1

                if number_orders > 10:
                    # if there are more we divide by ten
                    o_pages = number_orders / 10
                    # see if there is a decimal
                    numType = type(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if numType == "Float":
                        o_pages += 1

                # create a list for a ul to work through

                more_orders = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(o_pages):
                    i += 1
                    more_orders.append({'number': i})

                context = {
                    'support': support,
                    'more_support': more_support,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_support': current_page_support,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing the next page in overview. Contact the support for assistance.")
            return redirect("moderator:overview")


class MultipleOrdersView(View):
    def get(self, *args, **kwargs):
        try:
            # get the first 20 orders and a count of all orders

            try:
                orders = Order.objects.all()[:20]
                number_orders = Order.objects.all().count()
            except ObjectDoesNotExist:
                orders = {}
                number_orders = 0

            # figure out how many pages of 20 there are
            # if there are only 20 or fewer pages will be 1

            o_pages = 1

            if number_orders > 20:
                # if there are more we divide by ten
                o_pages = number_orders / 20
                # see if there is a decimal
                numType = type(o_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if numType == "Float":
                    o_pages += 1

            # create a list for a ul to work through

            more_orders = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(o_pages):
                i += 1
                more_orders.append({'number': i})

            # make search for specific order or customer

            form = searchOrderForm()

            # set current page to 1
            current_page = 1

            # set a bool to check if we are showing one or multiple orders

            multiple = True

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = "None"

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'orders': orders,
                'more_orders': more_orders,
                'form': form,
                'current_page': current_page,
            }

            return render(self.request, "moderator/mod_order_search.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the page that displays orders. Contact IT support for assistance.")
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys():
                # make a form and populate so we can clean the data
                form = searchOrderForm(self.request.POST)

                if form.is_valid():
                    # get the values
                    order_ref = form.cleaned_data.get('order_ref')
                    order_id = form.cleaned_data.get('order_id')
                    user_id = form.cleaned_data.get('user_id')

                    if len(order_ref) == 20:
                        # search done on order reference
                        search_value = order_ref

                        try:
                            order = Order.objects.get(order_ref=order_ref)

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False
                            more_orders = [{'number': 1}]

                            # set the search type

                            search_type = "Reference"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'order': order,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': 1,
                            }

                            return render(self.request, "moderator:mod_vieworder", context)
                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "Order does not exist.")
                            return redirect("moderator:orders")

                    elif order_id != 0:
                        # search on order id
                        search_value = order_id

                        try:
                            order = Order.objects.get(id=order_id)

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False
                            more_orders = [{'number': 1}]

                            # set the search type

                            search_type = "orderID"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'order': order,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': 1,
                            }

                            return render(self.request, "moderator:mod_vieworder", context)
                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "Order does not exist.")
                            return redirect("moderator:orders")

                    elif user_id != 0:
                        # search done on user
                        search_value = user_id
                        # get the user

                        try:
                            the_user = User.objects.get(id=user_id)
                            orders = Order.objects.filter(
                                user=the_user)
                            number_orders = Order.objects.filter(
                                user=the_user).count()

                            # figure out how many pages of 10 there are
                            # if there are only 10 or fewer pages will be 1

                            o_pages = 1

                            if number_orders > 10:
                                # if there are more we divide by ten
                                o_pages = number_orders / 10
                                # see if there is a decimal
                                numType = type(o_pages)
                                # if there isn't an even number of ten make an extra page for the last group
                                if numType == "Float":
                                    o_pages += 1

                            # create a list for a ul to work through

                            more_orders = []

                            i = 0
                            # populate the list with the amount of pages there are
                            for i in range(o_pages):
                                i += 1
                                more_orders.append({'number': i})

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = True

                            # set the search type

                            search_type = "userID"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'orders': orders,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': current_page,
                            }

                            return render(self.request, "moderator:mod_vieworder", context)

                        except ObjectDoesNotExist:
                            messages.info(self.request, "User does not exist.")
                            return redirect("moderator:orders")
                    else:
                        messages.info(
                            self.request, "Var god fyll i Referens, order id eller kund id.")
                        return redirect("moderator:orders")

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what kind of search
                if search_type == "None":

                    try:
                        number_orders = Order.objects.all(
                        ).count()
                        offset = current_page
                        if current_page < (number_orders / 20):
                            current_page += 1
                            offset = current_page
                        orders = Order.objects.all()[20:offset]
                    except ObjectDoesNotExist:
                        orders = {}
                        number_orders = 0

                    # figure out how many pages of 20 there are
                    # if there are only 20 or fewer pages will be 1

                    o_pages = 1

                    if number_orders > 20:
                        # if there are more we divide by ten
                        o_pages = number_orders / 20
                        # see if there is a decimal
                        numType = type(o_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if numType == "Float":
                            o_pages += 1

                    # create a list for a ul to work through

                    more_orders = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(o_pages):
                        i += 1
                        more_orders.append({'number': i})

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # set a bool to check if we are showing one or multiple orders

                    multiple = True

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = "None"

                    context = {
                        'search_type': search_type,
                        'search_value': search_value,
                        'multiple': multiple,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                    }

                    return render(self.request, "moderator/mod_order_search.html", context)

                elif search_type == "Reference":
                    # get the search value
                    search_value = int(self.request.POST['search_value'])

                    try:
                        order = Order.objects.get(order_ref=search_value)

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = False
                        more_orders = [{'number': 1}]

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'order': order,
                            'more_orders': more_orders,
                            'form': form,
                            'current_page': 1,
                        }

                        return render(self.request, "moderator:mod_vieworder", context)
                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Order does not exist.")
                        return redirect("moderator:orders")
                elif search_type == "OrderID":
                    # get the search value
                    search_value = int(self.request.POST['search_value'])

                    try:
                        order = Order.objects.get(id=search_value)

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = False
                        more_orders = [{'number': 1}]

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'order': order,
                            'more_orders': more_orders,
                            'form': form,
                            'current_page': 1,
                        }

                        return render(self.request, "moderator:mod_vieworder", context)
                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Order does not exist.")
                        return redirect("moderator:orders")
                elif search_type == "UserID":
                    search_value = int(self.request.POST['search_value'])

                    try:
                        theUser = User.objects.get(id=search_value)
                        number_orders = Order.objects.filter(
                            user=theUser).count()
                        offset = current_page
                        if current_page < (number_orders / 20):
                            current_page += 1
                            offset = current_page
                        orders = Order.objects.filter(user=theUser)[20:offset]
                    except ObjectDoesNotExist:
                        orders = {}
                        number_orders = 0

                    # figure out how many pages of 20 there are
                    # if there are only 20 or fewer pages will be 1

                    o_pages = 1

                    if number_orders > 20:
                        # if there are more we divide by ten
                        o_pages = number_orders / 20
                        # see if there is a decimal
                        numType = type(o_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if numType == "Float":
                            o_pages += 1

                    # create a list for a ul to work through

                    more_orders = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(o_pages):
                        i += 1
                        more_orders.append({'number': i})

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # set a bool to check if we are showing one or multiple orders

                    multiple = True

                    context = {
                        'search_type': search_type,
                        'search_value': search_value,
                        'multiple': multiple,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                    }

                    return render(self.request, "moderator/mod_order_search.html", context)
                else:
                    messages.info(
                        self.request, "Something is wrong with the order search page. Contact IT support for assistance.")
                    return redirect("moderator:orders")

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what kind of search
                if search_type == "None":

                    try:
                        offset = current_page
                        if current_page > 1:
                            current_page -= 1
                            offset = current_page
                        orders = Order.objects.all()[20:offset]
                        number_orders = Order.objects.all(
                        ).count()
                    except ObjectDoesNotExist:
                        orders = {}
                        number_orders = 0

                    # figure out how many pages of 20 there are
                    # if there are only 20 or fewer pages will be 1

                    o_pages = 1

                    if number_orders > 20:
                        # if there are more we divide by ten
                        o_pages = number_orders / 20
                        # see if there is a decimal
                        numType = type(o_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if numType == "Float":
                            o_pages += 1

                    # create a list for a ul to work through

                    more_orders = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(o_pages):
                        i += 1
                        more_orders.append({'number': i})

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # set a bool to check if we are showing one or multiple orders

                    multiple = True

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = "None"

                    context = {
                        'search_type': search_type,
                        'search_value': search_value,
                        'multiple': multiple,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                    }

                    return render(self.request, "moderator/mod_order_search.html", context)

                elif search_type == "Reference":
                    # get the search value
                    search_value = int(self.request.POST['search_value'])

                    try:
                        order = Order.objects.get(order_ref=search_value)

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = False
                        more_orders = [{'number': 1}]

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'order': order,
                            'more_orders': more_orders,
                            'form': form,
                            'current_page': 1,
                        }

                        return render(self.request, "moderator:mod_vieworder", context)
                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Order does not exist.")
                        return redirect("moderator:orders")
                elif search_type == "OrderID":
                    # get the search value
                    search_value = int(self.request.POST['search_value'])

                    try:
                        order = Order.objects.get(id=search_value)

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = False
                        more_orders = [{'number': 1}]

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'order': order,
                            'more_orders': more_orders,
                            'form': form,
                            'current_page': 1,
                        }

                        return render(self.request, "moderator:mod_vieworder", context)
                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Order does not exist.")
                        return redirect("moderator:orders")
                elif search_type == "UserID":
                    search_value = int(self.request.POST['search_value'])

                    try:
                        theUser = User.objects.get(id=search_value)
                        offset = current_page
                        if current_page > 1:
                            current_page -= 1
                            offset = current_page
                        orders = Order.objects.filter(user=theUser)[20:offset]
                        number_orders = Order.objects.filter(
                            user=theUser).count()
                    except ObjectDoesNotExist:
                        orders = {}
                        number_orders = 0

                    # figure out how many pages of 20 there are
                    # if there are only 20 or fewer pages will be 1

                    o_pages = 1

                    if number_orders > 20:
                        # if there are more we divide by ten
                        o_pages = number_orders / 20
                        # see if there is a decimal
                        numType = type(o_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if numType == "Float":
                            o_pages += 1

                    # create a list for a ul to work through

                    more_orders = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(o_pages):
                        i += 1
                        more_orders.append({'number': i})

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # set a bool to check if we are showing one or multiple orders

                    multiple = True

                    context = {
                        'search_type': search_type,
                        'search_value': search_value,
                        'multiple': multiple,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                    }

                    return render(self.request, "moderator/mod_order_search.html", context)
                else:
                    messages.info(
                        self.request, "Something is wrong with the order search page. Contact IT support for assistance.")
                    return redirect("moderator:orders")

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the order search page. Contact IT support for assistance.")
            return redirect("moderator:overview")


class Users(View):
    def get(self, *args, **kwargs):
        try:
            # get the first 20 users and a count of all users

            try:
                users = User.objects.filter(groups__name='client')[:20]
                number_users = User.objects.filter(
                    groups__name='client').count()
            except ObjectDoesNotExist:
                users = {}
                number_users = 0

            # figure out how many pages of 20 there are
            # if there are only 20 or fewer pages will be 1

            u_pages = 1

            if number_users > 20:
                # if there are more we divide by ten
                u_pages = number_users / 20
                # see if there is a decimal
                testU = int(u_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if testU != u_pages:
                    u_pages = int(u_pages)
                    u_pages += 1

            # create a list for a ul to work through

            more_users = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(u_pages):
                i += 1
                more_users.append({'number': i})

            # make search for specific order or customer

            form = searchUserForm()

            # set current page to 1
            current_page = 1

            # set a bool to check if we are showing one or multiple orders

            multiple = True

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = "None"

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'users': users,
                'more_users': more_users,
                'form': form,
                'current_page': current_page,
                'max_pages': u_pages,
            }

            return render(self.request, "moderator/mod_user_search.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the search for user page. Contact IT support for assistance.")
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "None":
                # make a form and populate so we can clean the data
                if 'previousPage' in self.request.POST.keys() or 'nextPage' in self.request.POST.keys() or 'page' in self.request.POST.keys():
                    # we only have one page when doing a search on user id, show that page
                    user_id = int(self.request.POST['search_value'])

                    if user_id != 0:
                        # next page on a single user is the same as the search for single user
                        # get the user

                        try:
                            the_user = User.objects.get(id=user_id)
                            userProfile = UserProfile.objects.get(
                                user=the_user)

                            # there is only one
                            u_pages = 1
                            more_users = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "userID"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'person': the_user,
                                'more_users': more_users,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': u_pages,
                            }

                            return render(self.request, "moderator/mod_user_search.html", context)

                        except ObjectDoesNotExist:
                            messages.info(self.request, "User does not exist.")
                            return redirect("moderator:search_users")
                else:
                    form = searchUserForm(self.request.POST)

                    if form.is_valid():
                        # get the values
                        user_id = form.cleaned_data.get('user_id')
                        # search done on user
                        search_value = user_id
                        # get the user

                        try:
                            the_user = User.objects.get(id=user_id)

                            # there is only one
                            u_pages = 1
                            more_users = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "userID"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'person': the_user,
                                'more_users': more_users,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': u_pages,
                            }

                            return render(self.request, "moderator/mod_user_search.html", context)

                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "User does not exist.")
                            return redirect("moderator:search_users")
                    else:
                        return redirect("moderator:search_users")

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                try:
                    number_users = User.objects.filter(
                        groups__name='client').count()
                    number_pages = number_users / 20
                    if current_page < number_pages:
                        current_page += 1
                    offset = current_page * 20
                    users = User.objects.filter(
                        groups__name='client')[20:offset]
                except ObjectDoesNotExist:
                    users = {}
                    number_users = 0

                # figure out how many pages of 20 there are
                # if there are only 20 or fewer pages will be 1

                u_pages = 1

                if number_users > 20:
                    # if there are more we divide by ten
                    u_pages = number_users / 20
                    # see if there is a decimal
                    testU = int(u_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testU != u_pages:
                        u_pages = int(u_pages)
                        u_pages += 1

                # create a list for a ul to work through

                more_users = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(u_pages):
                    i += 1
                    more_users.append({'number': i})

                # make search for specific order or customer

                form = searchOrderForm()

                # set a bool to check if we are showing one or multiple orders

                multiple = True

                # set the hidden value for wether or not we have done a search

                search_type = "None"
                search_value = "None"

                context = {
                    'search_type': search_type,
                    'search_value': search_value,
                    'multiple': multiple,
                    'users': users,
                    'more_users': more_users,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': u_pages,
                }

                return render(self.request, "moderator/mod_user_search.html", context)

            elif 'previousPage' in self.request.POST.keys():
                search_type = self.request.POST['search']

                # check what kind of search
                if current_page > 2:
                    try:
                        if current_page > 1:
                            current_page -= 1
                        offset = current_page * 20
                        users = User.objects.filter(
                            groups__name='client')[20:offset]
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        u_pages = 1

                        if number_users > 20:
                            # if there are more we divide by ten
                            u_pages = number_users / 20
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'users': users,
                            'more_users': more_users,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': u_pages,
                        }

                        return render(self.request, "moderator/mod_user_search.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Something is wrong with the user search page. Contact IT support for assistance.")
                        return redirect("moderator:search_users")

                else:
                    try:
                        if current_page > 1:
                            current_page -= 1
                        users = User.objects.filter(
                            groups__name='client')[:20]
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        u_pages = 1

                        if number_users > 20:
                            # if there are more we divide by ten
                            u_pages = number_users / 20
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'users': users,
                            'more_users': more_users,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': u_pages,
                        }

                        return render(self.request, "moderator/mod_user_search.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Something is wrong with the user search page. Contact IT support for assistance.")
                        return redirect("moderator:search_users")

            elif 'page' in self.request.POST.keys():
                # paging through the pagination using specific offset
                # get what type of search
                search_type = self.request.POST['search']
                current_page = int(self.request.POST['page'])

                if int(self.request.POST['page']) > 1:
                    try:
                        offset = int(self.request.POST['page']) * 20
                        users = User.objects.filter(
                            groups__name='client')[20:offset]
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        u_pages = 1

                        if number_users > 20:
                            # if there are more we divide by ten
                            u_pages = number_users / 20
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'users': users,
                            'more_users': more_users,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': u_pages,
                        }

                        return render(self.request, "moderator/mod_user_search.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Something is wrong with the user search page. Contact IT support for assistance.")
                        return redirect("moderator:search_users")

                else:
                    try:
                        users = User.objects.filter(
                            groups__name='client')[:20]
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        u_pages = 1

                        if number_users > 20:
                            # if there are more we divide by ten
                            u_pages = number_users / 20
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'users': users,
                            'more_users': more_users,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': u_pages,
                        }

                        return render(self.request, "moderator/mod_user_search.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Something is wrong with the user search page. Contact IT support for assistance.")
                        return redirect("moderator:search_users")

            messages.info(
                self.request, "Something is wrong with the user search page.")
            return redirect("moderator:search_users")
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the order search page. Contact IT support for assistance.")
            return redirect("moderator:overview")


class OrderView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            # get the user's specific order

            context = {
                'order': order,
                'all_order_items': all_order_items,
                'all_items': all_items,
                'discounts': discounts,
                'shipping_adress': shipping_adress,
                'billing_adress': billing_adress,
                'coupons': coupons,
                'payment': payment,
            }

            return render(self.request, "moderator:mod_vieworder", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Can't find this order. Contact the support for assistance.")
            return redirect("moderator:orders")


class SupportView(View):
    def get(self, *args, **kwargs):
        try:
            # get all unanswered errands and a count of them
            # make a search avaiable for specific errand, order or customer

            context = {
                'support': errands,
                'errands_a': errands_a,
            }

            return render(self.request, "member/my_support.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing this page. Contact the support for assistance.")
            return redirect("moderator:overview")


class Errand(View):
    def get(self, *args, **kwargs):
        try:
            # get the specific errand. Show all answers and responces as well as a responce form

            context = {
                'errand': errand,
                'responces': responces,
            }

            return render(self.request, "member/my_errand.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Can't find this errand. Contact the support for assistance.")
            return redirect("moderator:support")


class EditUser(View):
    def post(self, *args, **kwargs):
        try:
            # get the specific user's profile
            if 'lookAtProfile' in self.request.POST.keys():
                search_id = int(self.request.POST['lookAtProfile'])
                form = UserInformationForm()
                the_user = User.objects.get(id=search_id)

                form.populate(the_user)

                context = {
                    'form': form,
                    'person': the_user
                }

                return render(self.request, "moderator/edit_user.html", context)
            elif 'saveProfile' in self.request.POST.keys():
                form = UserInformationForm(self.request.POST)
                if form.is_valid():
                    if 'theUser' in self.request.POST.keys():
                        the_user = int(self.request.POST['theUser'])
                        person = User.objects.get(id=the_user)
                        userInfo = UserInfo.objects.get(user=person)
                        person.first_name = form.cleaned_data.get(
                            'first_name')
                        userInfo.first_name = form.cleaned_data.get(
                            'first_name')
                        person.last_name = form.cleaned_data.get(
                            'last_name')
                        userInfo.last_name = form.cleaned_data.get(
                            'last_name')
                        userInfo.email = form.cleaned_data.get(
                            'email')
                        userInfo.telephone = form.cleaned_data.get(
                            'telephone')
                        person.save()
                        userInfo.save()
                        messages.info(
                            self.request, "Information saved.")
                        return redirect("moderator:search_users")
                    else:
                        context = {
                            'form': form,
                        }

                        messages.info(
                            self.request, "Id check went wrong, talk to IT support.")
                        return render(self.request, "moderator/edit_user.html", context)
                else:
                    context = {
                        'form': form,
                    }

                    messages.info(
                        self.request, "Check information something you did was invalid.")
                    return render(self.request, "moderator/edit_user.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing the profile. Contact the IT support for assistance.")
            return redirect("moderator:overview")


class EditCompany(View):
    def post(self, *args, **kwargs):
        if 'lookAtCompany' in self.request.POST.keys():
            # take in the id nr
            user_id = int(self.request.POST['lookAtCompany'])
            # get the user
            theUser = User.objects.get(id=user_id)
            # check for company
            try:
                theCompany = CompanyInfo.objects.get(user=theUser)
                newOrOld = True
            except ObjectDoesNotExist:
                newOrOld = False

            # create the forms
            c_form = CompanyInfoForm()
            a_form = SetupAddressForm()
            if newOrOld:
                c_form.populate(theUser)
                a_form.populate(theCompany)

            context = {
                'a_form': a_form,
                'c_form': c_form,
                'person': theUser,
                'newOrOld': newOrOld,
            }

            return render(self.request, "moderator/company.html", context)
        elif 'saveCompany' in self.request.POST.keys():
            if 'theUser' in self.request.POST.keys():
                user_id = int(self.request.POST['theUser'])
                try:
                    theUser = User.objects.get(id=user_id)
                    if 'newOrOld' in self.request.POST.keys():
                        newOrOld = self.request.POST['newOrOld']
                        c_form = CompanyInfoForm(self.request.POST)
                        a_form = SetupAddressForm(self.request.POST)
                        if c_form.is_valid():
                            if a_form.is_valid():
                                if newOrOld:
                                    # save in old instances
                                    try:
                                        theCompany = CompanyInfo.objects.get(
                                            user=theUser)
                                    except ObjectDoesNotExist:
                                        messages.warning(
                                            self.request, "Company does not seem to exist. Something is wrong in the change company info form. Contact IT support for assistance.")

                                        return redirect("moderator:search_users")
                                    address = theCompany.addressID

                                    theCompany.company = c_form.cleaned_data.get(
                                        'company')
                                    theCompany.organisation_number = c_form.cleaned_data.get(
                                        'organisation_number')

                                    address.street_address = a_form.cleaned_data.get(
                                        'street_address')
                                    address.apartment_address = a_form.cleaned_data.get(
                                        'apartment_address')
                                    address.zip = a_form.cleaned_data.get(
                                        'zip')
                                    address.post_town = a_form.cleaned_data.get(
                                        'post_town')

                                    address.save()
                                    theCompany.save()
                                    messages.info(
                                        self.request, "Company information updated and saved.")

                                    return redirect("moderator:search_users")

                                else:
                                    # create new
                                    theCompany = CompanyInfo()
                                    address = Address()

                                    theCompany.user = theUser
                                    theCompany.company = c_form.cleaned_data.get(
                                        'company')
                                    theCompany.organisation_number = c_form.cleaned_data.get(
                                        'organisation_number')

                                    address.user = theUser
                                    address.street_address = a_form.cleaned_data.get(
                                        'street_address')
                                    address.apartment_address = a_form.cleaned_data.get(
                                        'apartment_address')
                                    address.zip = a_form.cleaned_data.get(
                                        'zip')
                                    address.post_town = a_form.cleaned_data.get(
                                        'post_town')
                                    address.default = True
                                    address.address_type = "B"
                                    address.country = "Sverige"
                                    # create a slug

                                    toSlug = address.street_address + \
                                        "B" + str(address.user.id)
                                    testSlug = slugify(toSlug)
                                    existingSlug = test_slug_address(testSlug)
                                    i = 1
                                    while existingSlug:
                                        toSlug = address.street_address + \
                                            "B" + str(address.user.id) + \
                                            "_" + str(i)
                                        testSlug = slugify(toSlug)
                                        existingSlug = test_slug_address(
                                            testSlug)
                                        i += 1

                                    address.slug = testSlug
                                    address.save()
                                    # add this address to the company
                                    theCompany.addressID = address
                                    # company needs a slug
                                    slug = theCompany.company + \
                                        str(theCompany.user.id)
                                    makeSlug = slugify(slug)
                                    test = test_slug_company(makeSlug)
                                    i = 1
                                    while test:
                                        slug = theCompany.company + \
                                            str(theCompany.user.id) + str(i)
                                        makeSlug = slugify(slug)
                                        test = test_slug_company(makeSlug)
                                        i += 1
                                    theCompany.slug = makeSlug
                                    theCompany.save()
                                    messages.info(
                                        self.request, "Company created and information saved.")
                                    return redirect("moderator:search_users")

                            else:

                                context = {
                                    'a_form': a_form,
                                    'c_form': c_form,
                                    'person': theUser,
                                    'newOrOld': newOrOld,
                                }
                                messages.info(
                                    self.request, "Check the address information. Something might be missing. If this problem persists contact IT support.")

                                return render(self.request, "moderator/company.html", context)
                        else:

                            context = {
                                'a_form': a_form,
                                'c_form': c_form,
                                'person': theUser,
                                'newOrOld': newOrOld,
                            }
                            messages.info(
                                self.request, "Check the company information. Something might be missing. If this problem persists contact IT support.")

                            return render(self.request, "moderator/company.html", context)
                except ObjectDoesNotExist:
                    messages.warning(
                        self.request, "Something is wrong in the change company info form. Contact IT support for assistance.")

                    return redirect("moderator:search_users")


class EditAdresses(View):
    def post(self, *args, **kwargs):
        try:
            if 'lookAtAddresses' in self.request.POST.keys():
                # get the client
                user_id = int(self.request.POST['lookAtAddresses'])
                theUser = User.objects.get(id=user_id)

                # get the specific user's addresses
                try:
                    addresses = Address.objects.filter(user=theUser)
                except ObjectDoesNotExist:
                    addresses = {}

                context = {
                    'addresses': addresses,
                    'person': theUser,
                }

                return render(self.request, "moderator/edit_addresses.html", context)
            elif 'delete' in self.request.POST.keys():
                # deleting adress
                if 'id' in self.request.POST.keys() and 'u_id' in self.request.POST.keys():
                    a_id = int(self.request.POST['id'])
                    theAddress = Address.objects.get(id=a_id)
                    u_id = int(self.request.POST['u_id'])
                    theUser = User.objects.get(id=u_id)
                    # check that this address isn't connected to a company
                    addressUnconnected = False
                    try:
                        numberOfCompanies = CompanyInfo.objects.filter(
                            addressID=theAddress).count()
                        if numberOfCompanies >= 1:
                            # a company with that address exists, redisplay page without changes
                            messages.info(
                                self.request, "This address is connected to the users company. Please change the company's address before deleting this address.")
                            try:
                                addresses = Address.objects.filter(
                                    user=theUser)
                            except ObjectDoesNotExist:
                                addresses = {}

                            context = {
                                'addresses': addresses,
                                'person': theUser,
                            }

                            return render(self.request, "moderator/edit_addresses.html", context)
                        else:
                            # no companies with that address
                            addressUnconnected = True
                    except ObjectDoesNotExist:
                        # no companies with that address
                        addressUnconnected = True
                    # check that this address isn't connected to a subscription
                    try:
                        numberOfSubscriptionsShipping = Subscription.objects.filter(
                            shipping_address=theAddress).count()
                        numberOfSubscriptionsBilling = Subscription.objects.filter(
                            billing_address=theAddress).count()
                        if numberOfSubscriptionsBilling >= 1 or numberOfSubscriptionsShipping >= 1:
                            # a subscription is tied to this address
                            messages.info(
                                self.request, "This address is connected to at least one of the users subscriptions. Please change the subscriptions's address before deleting this address.")
                            try:
                                addresses = Address.objects.filter(
                                    user=theUser)
                            except ObjectDoesNotExist:
                                addresses = {}

                            context = {
                                'addresses': addresses,
                                'person': theUser,
                            }

                            return render(self.request, "moderator/edit_addresses.html", context)
                        else:
                            # no subsriptions with that address set conenction to true
                            addressUnconnected = True
                    except ObjectDoesNotExist:
                        # no subscriptions with that address
                        addressUnconnected = True

                    theAddress.delete()
                    messages.info(
                        self.request, "Address deleted")
                    # get the specific user's addresses
                    try:
                        addresses = Address.objects.filter(user=theUser)
                    except ObjectDoesNotExist:
                        addresses = {}

                    context = {
                        'addresses': addresses,
                        'person': theUser,
                    }

                    return render(self.request, "moderator/edit_addresses.html", context)
            else:
                messages.info(
                    self.request, "Something went wrong when accessing this clients addresses. Contact IT support for assistance.")
                return redirect("moderator:search_users")

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing this clients addresses. Contact IT support for assistance.")
            return redirect("moderator:search_users")


class EditAdress(View):
    def get(self, *args, **kwargs):
        # return to search

        messages.info(
            self.request, "Something went wrong when accessing the address. Contact it support for assistance if the problem persists.")
        return redirect("moderator:search_users")

    def post(self, *args, **kwargs):
        if "theClient" in self.request.POST.keys():
            user_id = int(self.request.POST['theClient'])
            theUser = User.objects.get(id=user_id)
            # which one are we looking for
            where = where_am_i(self)
            # get this address
            hasAddress = False
            try:
                address = Address.objects.get(slug=where)
                hasAddress = True
            except ObjectDoesNotExist:
                address = Address()

            form = addressForm(address)

            context = {
                'person': theUser,
                'form': form,
                'address': address,
                'address_choices': ADDRESS_CHOICES
            }

            return render(self.request, "moderator/edit_address.html", context)

        elif 'saveAddress' in self.request.POST.keys():
            # client
            user_id = 0
            if 'u_id' in self.request.POST['u_id']:
                user_id = int(self.request.POST['u_id'])
            theUser = User.objects.get(id=user_id)
            # which one are we looking for
            where = where_am_i(self)
            # get this address
            hasAddress = False
            try:
                address = Address.objects.get(slug=where)
                hasAddress = True
            except ObjectDoesNotExist:
                address = Address()
            # get the form
            form = addressForm(data=self.request.POST, address=address)
            # check form
            if form.is_valid():

                address.street_address = form.cleaned_data.get(
                    'street_address')
                address.apartment_address = form.cleaned_data.get(
                    'apartment_address')
                address.post_town = form.cleaned_data.get('post_town')
                address.zip = form.cleaned_data.get('zip')
                address.country = "Sverige"
                if 'address_type' in self.request.POST.keys():
                    address_type = self.request.POST['address_type']
                    if address_type == "B":
                        address.address_type = "B"
                    elif address_type == "S":
                        address.address_type = "B"
                    else:
                        # someone is manipulating the code
                        messages.info(
                            self.request, "Something went wrong when saving the address. Contact IT support for assistance.")
                        return redirect("moderator:user_search")
                else:
                    # rerender form

                    context = {
                        'form': form,
                        'address': address,
                        'address_choices': ADDRESS_CHOICES
                    }

                    return render(self.request, "moderator/edit_address.html", context)
                if address.default is True:
                    if 'default_address' in self.request.POST.keys():
                        address.default = True
                        new_address_default(address)

                testString = address.street_address + \
                    address.address_type + str(address.user.id)
                toSlug = slugify(testString)
                if toSlug != address.slug:
                    # street address has changed. Create new slug

                    address.slug = create_slug_address(address)

                # save the address and return to list
                address.save()

                messages.info(self.request, "Address have been saved.")

                # render the users addresses for a soft redirect
                # get the specific user's addresses
                try:
                    addresses = Address.objects.filter(user=theUser)
                except ObjectDoesNotExist:
                    addresses = {}

                context = {
                    'addresses': addresses,
                    'person': theUser,
                }

                return render(self.request, "moderator/edit_addresses.html", context)
            else:
                # rerender form

                context = {
                    'form': form,
                    'address': address,
                    'address_choices': ADDRESS_CHOICES
                }

                return render(self.request, "moderator/edit_address.html", context)


class NewAddress(View):
    def get(self, *args, **kwargs):
        # return to search as we dont know the user

        messages.info(
            self.request, "Something went wrong when accessing the new address page. Contact IT support for assistance if the problem persists.")
        return redirect("moderator:search_users")

    def post(self, *args, **kwargs):
        if "theClient" in self.request.POST.keys():
            user_id = int(self.request.POST['theClient'])
            theUser = User.objects.get(id=user_id)
            # get form for this using the user id
            form = NewAddressForm()

            context = {
                'form': form,
                'person': theUser,
                'address_choices': ADDRESS_CHOICES_EXTENDED
            }

            return render(self.request, "moderator/new_address.html", context)
        elif 'saveAddress' in self.request.POST.keys():
            # client
            user_id = 0
            if 'user_id' in self.request.POST.keys():
                user_id = int(self.request.POST['theUser'])
            theUser = User.objects.get(id=user_id)
            # make an address object
            address = Address()
            form = NewAddressForm(self.request.POST)

            if form.is_valid():
                # start by checking that we dont already have this address
                sameBilling = 0
                sameShipping = 0
                form_street_address = form.cleaned_data.get(
                    'form_street_address')
                form_post_town = form.cleaned_data.get('post_town')
                form_address_type = form.cleaned_data.get('address_type')
                default = False
                if 'default_address' in self.request.POST.keys():
                    default = True
                sameShipping, sameBilling, message = sameAddress_moderator(
                    theUser, form_street_address, form_post_town, form_address_type, default)
                if message != "":
                    # render the users addresses for a soft redirect
                    # get the specific user's addresses
                    try:
                        addresses = Address.objects.filter(user=theUser)
                    except ObjectDoesNotExist:
                        addresses = {}

                    context = {
                        'addresses': addresses,
                        'person': theUser,
                    }

                    messages.info(
                        self.request, "Something went wrong when accessing the new address page. Contact IT support for assistance if the problem persists.")
                    return render(self.request, "moderator/edit_addresses.html", context)

                # get values
                address = Address()

                address.user = theUser
                address.street_address = form_street_address
                address.apartment_address = form.cleaned_data.get(
                    'apartment_address')
                address.post_town = form_post_town
                address.zip = form.cleaned_data.get('zip')
                address.country = "Sverige"

                # check what kind of address we have
                address_type = form_address_type

                # confirm that it isn't the same type as we already have (this only happens when we save both) set the values to the one we don't already have unless we have both saved
                if sameBilling > 0 and sameShipping > 0:
                    # test for defaulting
                    testShipping = Address.objects.get(id=sameShipping)
                    testBilling = Address.objects.get(id=sameBilling)
                    message = "You already have these addresses saved."
                    if default:
                        message = message + " Default changed."
                        new_address_default(testShipping)
                        new_address_default(testBilling)

                    messages.info(
                        self.request, message)
                    # render the users addresses for a soft redirect
                    # get the specific user's addresses
                    try:
                        addresses = Address.objects.filter(user=theUser)
                    except ObjectDoesNotExist:
                        addresses = {}

                    context = {
                        'addresses': addresses,
                        'person': theUser,
                    }
                    return render(self.request, "moderator/edit_addresses.html", context)

                elif sameBilling > 0:
                    address_type = "S"
                elif sameShipping > 0:
                    address_type = "B"

                if address_type == "A":
                    # we want two copies of this address
                    address2 = Address()
                    address2.user = address.user
                    address2.street_address = address.street_address
                    address2.apartment_address = address.apartment_address
                    address2.post_town = address.post_town
                    address2.zip = address.zip
                    address2.country = address.country
                    if default:
                        address2.default = True
                        new_address_default(address2)

                    address2.address_type = "S"
                    address2.slug = create_slug_address(address2)

                    # save the second copy of the address
                    address2.save()
                    address.address_type = "B"
                else:
                    address.address_type = address_type

                if default:
                    address.default = True
                    new_address_default(address)
                # create a slug
                address.slug = create_slug_address(address)
                # save the address and return to list
                address.save()

                messages.info(self.request, "Address have been saved.")
                # render the users addresses for a soft redirect
                # get the specific user's addresses
                try:
                    addresses = Address.objects.filter(user=theUser)
                except ObjectDoesNotExist:
                    addresses = {}

                context = {
                    'addresses': addresses,
                    'person': theUser,
                }

                return render(self.request, "moderator/edit_addresses.html", context)
            else:

                context = {
                    'form': form,
                    'person': theUser,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }

                messages.info(
                    self.request, "Something in the information is incorrect or missing.")

                return render(self.request, "moderator/edit_address.html", context)


class SettingsView(View):
    def post(self, *args, **kwargs):
        try:
            if 'lookAtSettings' in self.request.POST.keys():
                user = int(self.request.POST['lookAtSettings'])
                theUser = User.objects.get(id=user)
                # get cookie model, fill in with previous info if there is any
                form = CookieSettingsForm()
                form.populate(theUser)

                context = {
                    'form': form,
                }

                return render(self.request, "moderator/client_settings.html", context)
        except ObjectDoesNotExist:
            message = "Something went wrong in the viewing of the clients settings. Contact IT support."
            messages.warning(self.request, message)
            return redirect("core:home")


class Subscriptions(View):
    def get(self, *args, **kwargs):
        # shouldnt be here redirect

        messages.info(
            self.request, "Something went wrong when accessing the subscriptions. Contact IT support for assistance if the problem persists.")
        return redirect("moderator:search_users")

    def post(self, *args, **kwargs):
        try:
            if 'lookAtSubscriptions' in self.request.POST.keys():
                # get the client
                user_id = int(self.request.POST['lookAtSubscriptions'])
                theUser = User.objects.get(id=user_id)
                # get the specific user's subscriptions
                try:
                    subscriptions = Subscription.objects.filter(user=theUser)
                except ObjectDoesNotExist:
                    subscriptions = {}

                context = {
                    'subscriptions': subscriptions,
                    'person': theUser,
                }

                return render(self.request, "moderator/subscriptions.html", context)
            elif 'delete' in self.request.POST.keys():
                # message for later
                message = ""
                # get the client
                if 'theUser' in self.request.POST.keys():
                    user_id = int(self.request.POST['theUser'])
                    theUser = User.objects.get(id=user_id)
                    # get the subscription id
                    sub_id = int(self.request.POST['id'])
                    try:
                        subscription = Subscription.objects.get(
                            user=theUser, id=sub_id)
                        # check that there is an order connected
                        if subscription.active:
                            # get the order
                            try:
                                order = Order.objects.get(
                                    id=subscription.next_order)
                                # get the orderItem
                                orderItemQuery = order.items.all()
                                # enter the query
                                for orderItem in orderItemQuery:
                                    # delete order item
                                    orderItem.delete()
                                # delete order
                                order.delete()
                                # delete subscription
                                subscription.delete()
                                message = 'subscription and corresponding order deleted'
                            except ObjectDoesNotExist:
                                message = "Subscription was active but had no connected order. Check that there isn't any subscription order connected to this one under orders. Contact IT support. This is a significant error."
                                messages.warning(
                                    self.request, message)
                                message = "Subscription was not deleted."
                        else:
                            # delete subscription
                            subscription.delete()
                            message = 'subscription deleted'
                    except ObjectDoesNotExist:
                        # no such subscription
                        message = 'Subscription does not exist. If you still see it contact IT support for assistance.'

                    # get the specific user's subscriptions
                    try:
                        subscriptions = Subscription.objects.filter(
                            user=theUser)
                    except ObjectDoesNotExist:
                        subscriptions = {}

                    context = {
                        'subscriptions': subscriptions,
                        'person': theUser,
                    }

                    messages.info(
                        self.request, message)
                    return render(self.request, "moderator/subscriptions.html", context)
                else:
                    messages.warning(
                        self.request, "Something went wrong when deleting this clients subscription. If this persists contact IT support for assistance.")
                    return redirect("moderator:search_users")
            else:
                messages.warning(
                    self.request, "Something went wrong when accessing this clients subscriptions. If this persists contact IT support for assistance.")
                return redirect("moderator:search_users")

        except ObjectDoesNotExist:
            messages.warning(
                self.request, "Something went wrong when accessing this clients subscriptions. If this persists contact IT support for assistance.")
            return redirect("moderator:search_users")


class SpecificSubscription(View):
    def get(self, *args, **kwargs):
        # shouldnt be here redirect

        messages.info(
            self.request, "Something went wrong when accessing the subscription. Contact IT support for assistance if the problem persists.")
        return redirect("moderator:search_users")

    def post(self, *args, **kwargs):
        try:
            if 'see' in self.request.POST.keys() and 'u_id' in self.request.POST.keys():
                # get the user
                user_id = int(self.request.POST['u_id'])
                theUser = User.objects.get(id=user_id)
                # where are we
                path = self.request.get_full_path()
                # we are editing a specific Subscription
                slug = where_am_i(self)
                try:
                    # get the subscription
                    subscription = Subscription.objects.get(slug=slug)
                    if subscription.active:
                        active = True
                    else:
                        active = False
                    old = True
                    sub_date = subscription.start_date.strftime("%Y-%m-%d")
                    number_of_products = subscription.number_of_items
                    # get the form
                    form = EditSubscriptionForm()
                    form.populate(theUser, subscription, old)

                    context = {
                        'form': form,
                        'sub_date': sub_date,
                        'subscription': subscription,
                        'number_of_products': number_of_products,
                        'old': old,
                        'active': active,
                        'path': path,
                        'person': theUser,
                    }

                    return render(self.request, "moderator/edit_subscription.html", context)

                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something went wrong when accessing your subscription. Contact the support for assistance.")
                    return redirect("moderator:my_subscriptions")

            elif 'saveSubscription' in self.request.POST.keys() and 'u_id' in self.request.POST.keys() and 'sub_id' in self.request.POST.keys():
                # saving subscription
                # get the user
                u_id = int(self.request.POST['u_id'])
                theUser = User.objects.get(id=u_id)
                sub_id = int(self.request.POST['sub_id'])
                # where are we
                path = self.request.get_full_path()
                # validate
                form = EditSubscriptionForm(self.request.POST)
                if form.is_valid():
                    # check if new or old
                    if self.request.POST['new_or_old'] == 'old':
                        # get the old subscription
                        try:
                            sub = Subscription.objects.get(id=sub_id)
                            message = ''
                            # take in the data

                            # start date
                            # make sure the date is in the correct format
                            sub.start_date = form.cleaned_data.get(
                                'start_date')
                            # intervall
                            sub.intervall = form.cleaned_data.get('intervall')
                            # all user addresses
                            addresses = Address.objects.filter(
                                user=self.request.user)
                            # shipping_address
                            shipping_address = form.cleaned_data.get(
                                'shipping_address')
                            # billing_address
                            billing_address = form.cleaned_data.get(
                                'billing_address')
                            for address in addresses:
                                if address.id == shipping_address:
                                    sub.shipping_address = address
                                elif address.id == billing_address:
                                    sub.billing_address = address
                            # number_of_products
                            sub.number_of_items = int(
                                self.request.POST['number_of_products'])

                            # calcuate the rest of the data
                            sub.updated_date = make_aware(datetime.now())
                            sub.active = True
                            sub.next_order_date = get_next_order_date(
                                sub.start_date, sub.intervall)

                            # save subscription
                            sub.save()

                            # get the connected order
                            if sub.next_order > 0:
                                theOrder = Order.objects.get(
                                    id=sub.next_order)

                                theOrder.subscription_date = sub.next_order_date
                                theOrder.updated_date = make_aware(
                                    datetime.now())
                                theOrder.sub_out_date = sub.start_date
                                theOrder.ordered = True
                                theOrder.received = False
                                theOrder.being_delivered = False
                                theOrder.shipping_address = sub.shipping_address
                                theOrder.billing_address = sub.shipping_address
                                theOrder.save()

                                # remove old order items and subitems
                                orderItems = theOrder.items.all()
                                for item in orderItems:
                                    item.delete()
                                subItems = SubscriptionItem.objects.filter(
                                    subscription=sub.id)
                                for subItem in subItems:
                                    subItem.delete()

                                # and then make new the order and sub items

                                i = 1
                                for i in range(sub.number_of_items):
                                    i += 1
                                    p_string = 'product%s' % (i,)
                                    a_string = 'amount%s' % (i,)
                                    product_id = int(
                                        self.request.POST[p_string])
                                    amount = int(self.request.POST[a_string])
                                    product = Item.objects.get(
                                        id=product_id)
                                    # saving subscription and order items

                                    orderItem = save_subItems_and_orderItems(theUser,
                                                                             sub, amount, product)
                                    theOrder.items.add(orderItem)
                                    message = "Subscription saved and activated."
                                    messages.info(self.request, message)

                                    # soft redirect
                                    # get the specific user's subscriptions
                                    try:
                                        subscriptions = Subscription.objects.filter(
                                            user=theUser)
                                    except ObjectDoesNotExist:
                                        subscriptions = {}

                                    context = {
                                        'subscriptions': subscriptions,
                                        'person': theUser,
                                    }

                                    return render(self.request, "moderator/subscriptions.html", context)

                            else:
                                # it isn't so we make a new one
                                theOrder = Order()

                                theOrder.user = sub.user

                                # create a reference code and check that there isnt already one before setting the orders ref code to the code
                                ref_code = create_ref_code()
                                ref_test = True

                                while ref_test:
                                    try:
                                        numberofOrders = Order.objects.filter(
                                            ref_code=ref_code).count()
                                        if numberofOrders >= 1:
                                            refcode = create_ref_code()
                                        else:
                                            ref_test = False
                                    except ObjectDoesNotExist:
                                        ref_test = False

                                theOrder.ref_code = ref_code
                                theOrder.subscription_order = True
                                theOrder.subscription_date = sub.next_order_date
                                theOrder.updated_date = make_aware(
                                    datetime.now())
                                theOrder.sub_out_date = sub.start_date
                                theOrder.ordered_date = sub.start_date
                                theOrder.sub_out_date = sub.start_date
                                theOrder.ordered = True
                                theOrder.received = False
                                theOrder.being_delivered = False
                                theOrder.shipping_address = sub.shipping_address
                                theOrder.billing_address = sub.shipping_address
                                theOrder.save()
                                sub.next_order = theOrder.id
                                sub.save()

                                # remove old subitems
                                subItems = SubscriptionItem.objects.filter(
                                    subscription=sub.id)
                                for subItem in subItems:
                                    subItem.delete()

                                i = 1
                                for i in range(sub.number_of_items):
                                    i += 1
                                    p_string = 'product%s' % (i,)
                                    a_string = 'amount%s' % (i,)
                                    product_id = int(
                                        self.request.POST[p_string])
                                    amount = int(self.request.POST[a_string])
                                    product = Item.objects.get(id=product_id)
                                    # saving subscription and order items
                                    orderItem = save_subItems_and_orderItems(theUser,
                                                                             sub, amount, product)
                                    theOrder.items.add(orderItem)
                                    message = "Subscription saved and activated."
                                    messages.info(self.request, message)
                                    # soft redirect
                                    # get the specific user's subscriptions
                                    try:
                                        subscriptions = Subscription.objects.filter(
                                            user=theUser)
                                    except ObjectDoesNotExist:
                                        subscriptions = {}

                                    context = {
                                        'subscriptions': subscriptions,
                                        'person': theUser,
                                    }

                                    return render(self.request, "moderator/subscriptions.html", context)
                        except ObjectDoesNotExist:
                            message = "We can't access the subscription right now. Please contact IT support for assistance."
                            messages.info(self.request, message)

                            # get the specific user's subscriptions
                            try:
                                subscriptions = Subscription.objects.filter(
                                    user=theUser)
                            except ObjectDoesNotExist:
                                subscriptions = {}

                            context = {
                                'subscriptions': subscriptions,
                                'person': theUser,
                            }

                            return render(self.request, "moderator/subscriptions.html", context)
                    else:
                        # somehow this is not an old subscription. Return to subscriptions
                        message = "It seems like you are trying to create a new subscription. If that is not the case please contact IT support for assistance. If it is the case it us up to the user to create a subscription. It should never be done by staff."
                        messages.info(self.request, message)

                        # get the specific user's subscriptions
                        try:
                            subscriptions = Subscription.objects.filter(
                                user=theUser)
                        except ObjectDoesNotExist:
                            subscriptions = {}

                        context = {
                            'subscriptions': subscriptions,
                            'person': theUser,
                        }

                        return render(self.request, "moderator/subscriptions.html", context)

                else:
                    # figure out how to rerender the form here
                    subscription = Subscription.objects.get(id=sub_id)
                    active = subscription.active
                    form.populate_from_submit(self.request.POST)
                    sub_date = make_aware(datetime.strptime(
                        self.request.POST['start_date'], '%Y-%m-%d'))
                    number_of_products = self.request.POST['number_of_products']
                    old = self.request.POST['new_or_old']

                    context = {
                        'form': form,
                        'sub_date': sub_date,
                        'number_of_products': number_of_products,
                        'old': old,
                        'subscription': subscription,
                        'path': path,
                        'person': theUser,
                        'active': active,
                    }

                    return render(self.request, "moderator/edit_subscription.html", context)

            elif 'deactivateSubscription' in self.request.POST.keys():
                user_id = 0
                if 'u_id' in self.request.POST.keys():
                    user_id = int(self.request.POST['u_id'])
                theUser = User.objects.get(id=user_id)

                if 'sub_id' in self.request.POST.keys():
                    sub_id = int(self.request.POST['sub_id'])
                    sub = Subscription.objects.get(
                        user=theUser, id=sub_id)
                    # deactivate subscription
                    if sub.active is False:
                        messages.info(
                            self.request, "Subscription already deactivated")
                        return redirect("member:my_subscriptions")
                    else:
                        sub.active = False

                        try:
                            # delete the order connected to the sub
                            theOrder = Order.objects.get(id=sub.next_order)
                            # first get the list of items
                            theOrderItems = theOrder.items.all()
                            # then go through the items one by one
                            for item in theOrderItems:
                                # delete the items
                                item.delete()
                            # delete order
                            theOrder.delete()
                            message = "Subscription deactivated."
                        except ObjectDoesNotExist:
                            message = "Subscription deactivated no order detected."
                        sub.next_order = 0
                        sub.save()

                        messages.info(
                            self.request, message)
                        # soft redirect
                        # get the specific user's subscriptions
                        try:
                            subscriptions = Subscription.objects.filter(
                                user=theUser)
                        except ObjectDoesNotExist:
                            subscriptions = {}

                        context = {
                            'subscriptions': subscriptions,
                            'person': theUser,
                        }

                        return render(self.request, "moderator/subscriptions.html", context)
                else:
                    messages.warning(
                        self.request, "Something is wrong with the subscription deactivation. Please contact IT support for assistance.")
                    # soft redirect
                    # get the specific user's subscriptions
                    try:
                        subscriptions = Subscription.objects.filter(
                            user=theUser)
                    except ObjectDoesNotExist:
                        subscriptions = {}

                    context = {
                        'subscriptions': subscriptions,
                        'person': theUser,
                    }

                    return render(self.request, "moderator/subscriptions.html", context)
            else:
                messages.info(
                    self.request, "You seem to have encountered a programatic error on the subscription page. Please contact IT support for assistance.")
                return redirect("moderator:search_user")
        except ObjectDoesNotExist:
            messages.info(
                self.request, "You seem to have encountered a programatic error on the subscription page. Please contact IT support for assistance.")
            return redirect("moderator:search_user")


class ProfileView(View):
    def get(self, *args, **kwargs):
        try:
            # get moderators own user info
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()
                info.company = False

            # place info in context and render page

            context = {
                'info': info,
            }

            return render(self.request, "moderator/my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact IT support for assistance.")
            return redirect("moderator:my_overview")


class InfoView(View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id

            form = UserInformationForm(the_User=self.request.user)

            context = {
                'form': form,
            }

            return render(self.request, "moderator/my_info.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your information. Contact IT support for assistance.")
            return redirect("moderator:my_profile")

    def post(self, *args, **kwargs):
        try:
            form = UserInformationForm(self.request.POST)

            if 'edit' in self.request.POST.keys():

                context = {
                    'form': form,
                }

                return render(self.request, "moderator/my_info.html", context)

            if form.is_valid():
                try:
                    info = UserInfo.objects.get(user=self.request.user)
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    info.save()
                    messages.info(
                        self.request, "User information saved.")
                    return redirect("moderator:my_profile")
                except ObjectDoesNotExist:
                    info = UserInfo()
                    info.user = self.request.user
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    info.save()
                    messages.info(
                        self.request, "User information saved.")
                    return redirect("moderator:my_profile")
            else:

                context = {
                    'form': form,
                }

                messages.info(
                    self.request, "Missing certain information.")

                return render(self.request, "moderator/my_info.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when saving your information. Contact IT support for assistance.")
            return redirect("moderator:my_profile")


# rewrite for products, add delete
class ProductsView(View):
    def get(self, *args, **kwargs):
        try:
            # get the first 20 products and a count of all products
            products = Item.objects.all()[:20]
            number_products = Item.objects.all().count()
            # figure out how many pages of 20 there are
            # if there are only 20 or fewer pages will be 1

            p_pages = 1

            if number_products > 20:
                # if there are more we divide by ten
                p_pages = number_products / 20
                # see if there is a decimal
                numType = type(p_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if numType == "Float":
                    p_pages += 1

            # create a list for a ul to work through

            more_products = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(p_pages):
                i += 1
                more_products.append({'number': i})

            # make search for specific order or customer

            form = searchProductForm()

            # set current page to 1
            current_page = 1

            # set a bool to check if we are showing one or multiple orders

            multiple = True

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = "None"

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'products': products,
                'more_products': more_products,
                'form': form,
                'current_page': current_page,
            }

            return render(self.request, "moderator/mod_products.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the products page. Contact IT support for assistance.")
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys():
                # make a form and populate so we can clean the data
                form = searchProductForm(self.request.POST)

                if form.is_valid():
                    # get the values
                    product_id = form.cleaned_data.get('product_id')
                    # search done on product id
                    search_value = product_id
                    # get the product
                    try:
                        product = Item.objects.get(id=product_id)

                        more_products = [{'number': 1}]
                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = False

                        # set the search type

                        search_type = "productID"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'product': product,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Product does not exist.")
                        return redirect("moderator:products")
                else:
                    # if we are paging after a search we need to render the same page again. Values will be in other places than a regular search
                    product_id = int(self.request.POST['search_value'])
                    # get the product
                    product = Item.objects.get(id=product_id)

                    # only one page

                    more_products = [{'number': 1}]

                    # set current page to 1
                    current_page = 1

                    # set a bool to check if we are showing one or multiple orders

                    multiple = False

                    # set the search type

                    search_type = "productID"
                    search_value = product_id

                    form = searchProductForm()
                    form.populate(product_id)

                    context = {
                        'search_type': search_type,
                        'search_value': search_value,
                        'multiple': multiple,
                        'product': product,
                        'more_products': more_products,
                        'form': form,
                        'current_page': current_page,
                    }

                    return render(self.request, "moderator/mod_products.html", context)

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what kind of search
                if search_type == "None":

                    try:
                        number_products = Item.objects.all(
                        ).count()
                        offset = current_page
                        if current_page < (number_products / 20):
                            current_page += 1
                            offset = current_page
                        products = Item.objects.all()[20:offset]
                    except ObjectDoesNotExist:
                        products = {}
                        number_products = 0

                    # figure out how many pages of 20 there are
                    # if there are only 20 or fewer pages will be 1

                    p_pages = 1

                    if number_products > 20:
                        # if there are more we divide by ten
                        p_pages = number_products / 20
                        # see if there is a decimal
                        numType = type(p_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if numType == "Float":
                            p_pages += 1

                    # create a list for a ul to work through

                    more_products = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(p_pages):
                        i += 1
                        more_products.append({'number': i})

                    # make search for specific order or customer

                    form = searchProductForm()

                    # set a bool to check if we are showing one or multiple orders

                    multiple = True

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = "None"

                    context = {
                        'search_type': search_type,
                        'search_value': search_value,
                        'multiple': multiple,
                        'products': products,
                        'more_products': more_products,
                        'form': form,
                        'current_page': current_page,
                    }

                    return render(self.request, "moderator/mod_products.html", context)

                elif search_type == "productID":
                    product_id = int(self.request.POST['search_value'])

                    if product_id != 0:
                        # next page on a single user is the same as the search for single user
                        # get the user

                        try:
                            # get the product
                            product = Item.objects.get(id=product_id)

                            # only one page

                            more_products = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "productID"
                            search_value = product_id

                            form = searchProductForm().populate(product_id)

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'product': product,
                                'more_products': more_products,
                                'form': form,
                                'current_page': current_page,
                            }

                            return render(self.request, "moderator/mod_products.html", context)

                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "Product does not exist.")
                            return redirect("moderator:search_users")
                else:
                    messages.info(
                        self.request, "Something is wrong with the products page. Contact IT support for assistance.")
                    return redirect("moderator:overview")

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what kind of search
                if search_type == "None":

                    try:
                        offset = current_page
                        if current_page > 1:
                            current_page -= 1
                            offset = current_page
                        products = Item.objects.all()[20:offset]
                        number_products = Item.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        p_pages = 1

                        if number_products > 20:
                            # if there are more we divide by ten
                            p_pages = number_products / 20
                            # see if there is a decimal
                            numType = type(p_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if numType == "Float":
                                p_pages += 1

                        # create a list for a ul to work through

                        more_products = [{'number': 1}]

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(p_pages):
                            i += 1
                            more_products.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Something is wrong with the product page. Contact IT support for assistance.")
                        return redirect("moderator:mod_products.html")

                elif search_type == "productID":
                    product_id = int(self.request.POST['search_value'])

                    if product_id != 0:
                        # previous page on a single user is the same as the search for single user
                        # get the user

                        try:
                            product = Item.objects.get(id=product_id)

                            # there is only one

                            more_products = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "productID"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'user': the_user,
                                'more_users': more_users,
                                'form': form,
                                'current_page': current_page,
                            }

                            return render(self.request, "moderator/mod_products.html", context)

                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "Product does not exist.")
                            return redirect("moderator:products")
                else:
                    messages.info(
                        self.request, "Something is wrong with the products page. Contact IT support for assistance.")
                    return redirect("moderator:products")

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the products page. Contact IT support for assistance.")
            return redirect("moderator:overview")


class SpecificProductsView(View):
    test = "test"


class CategoriesView(View):
    test = "test"


class SpecificCategoryView(View):
    test = "test"

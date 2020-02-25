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
from datetime import datetime
from core.models import *
from member.forms import *
from .forms import *


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
                print("we have a page")

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
                search_type = self.request.POST['search_type']

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
                search_type = self.request.POST['search_type']

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
                users = User.objects.all()[:20]
                number_users = User.objects.all().count()
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
                numType = type(u_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if numType == "Float":
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

            if 'search' in self.request.POST.keys():
                # make a form and populate so we can clean the data
                form = searchUserForm(self.request.POST)

                if form.is_valid():
                    # get the values
                    user_id = form.cleaned_data.get('user_id')

                    if type(user_id) == 'Int':
                        # search done on user
                        search_value = user_id
                        # get the user

                        try:
                            the_user = User.objects.get(id=user_id)

                            # there is only one

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
                            }

                            return render(self.request, "moderator/mod_user_search.html", context)

                        except ObjectDoesNotExist:
                            messages.info(self.request, "User does not exist.")
                            return redirect("moderator:search_users")
                    else:
                        return redirect("moderator:search_users")

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search_type']

                # check what kind of search
                if search_type == "None":

                    try:
                        number_users = User.objects.all(
                        ).count()
                        offset = current_page
                        if current_page < (number_users / 20):
                            current_page += 1
                            offset = current_page
                        users = User.objects.all()[20:offset]
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
                        numType = type(u_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if numType == "Float":
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
                    }

                    return render(self.request, "moderator/mod_user_search.html", context)

                elif search_type == "UserID":
                    user_id = int(self.request.POST['search_value'])

                    if user_id != 0:
                        # next page on a single user is the same as the search for single user
                        # get the user

                        try:
                            the_user = User.objects.get(id=user_id)
                            userProfile = UserProfile.objects.get(
                                user=the_user)

                            # there is only one

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
                            }

                            return render(self.request, "moderator/mod_user_search.html", context)

                        except ObjectDoesNotExist:
                            messages.info(self.request, "User does not exist.")
                            return redirect("moderator:search_users")
                else:
                    messages.info(
                        self.request, "Something is wrong with the users search page. Contact IT support for assistance.")
                    return redirect("moderator:overview")

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search_type']

                # check what kind of search
                if search_type == "None":

                    try:
                        offset = current_page
                        if current_page > 1:
                            current_page -= 1
                            offset = current_page
                        users = User.objects.all()[20:offset]
                        number_users = User.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        u_pages = 1

                        if number_users > 20:
                            # if there are more we divide by ten
                            u_pages = number_users / 20
                            # see if there is a decimal
                            numType = type(u_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if numType == "Float":
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
                        }

                        return render(self.request, "moderator/mod_user_search.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, "Something is wrong with the user search page. Contact IT support for assistance.")
                        return redirect("moderator:search_users")

                elif search_type == "UserID":
                    user_id = int(self.request.POST['search_value'])

                    if user_id != 0:
                        # previous page on a single user is the same as the search for single user
                        # get the user

                        try:
                            the_user = User.objects.get(id=user_id)

                            # there is only one

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
                                'user': the_user,
                                'more_users': more_users,
                                'form': form,
                                'current_page': current_page,
                            }

                            return render(self.request, "moderator/mod_user_search.html", context)

                        except ObjectDoesNotExist:
                            messages.info(self.request, "User does not exist.")
                            return redirect("moderator:search_users")
                else:
                    messages.info(
                        self.request, "Something is wrong with the order search page. Contact IT support for assistance.")
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


class Profile(View):
    def get(self, *args, **kwargs):
        try:
            # show the moderators own profile

            try:
                info = UserInfo().__class__.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = {}

            context = {
                'info': info,
            }

            return render(self.request, "member/my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("moderator:profile")


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
                                        print(theCompany.id)
                                    except ObjectDoesNotExist:
                                        messages.warning(
                                            self.request, "Company does not seem to exist. Something is wrong in the change company info form. Contact IT support for assistance.")

                                        return redirect("moderator:search_users")
                                    print(theCompany.id)
                                    address = theCompany.addressID
                                    print(address)

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
            else:
                messages.info(
                    self.request, "Something went wrong when accessing this clients addresses. Contact IT support for assistance.")
                return redirect("moderator:search_users")

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing this clients addresses. Contact IT support for assistance.")
            return redirect("moderator:search_users")


class EditAdress(View):
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

            form = SetupAddressForm()
            if hasAddress:
                form.populate_from_slug(where)
            else:
                messages.info(
                    self.request, "Something went wrong when accessing this clients address. Contact IT support for assistance.")
                return redirect("moderator:search_users")

            ADDRESS_CHOICES_EXTENDED = [
                {'key': 'B', 'name': 'Fakturaaddress'},
                {'key': 'S', 'name': 'Leveransaddress'},
            ]

            context = {
                'form': form,
                'address': address,
                'person': theUser,
                'address_choices': ADDRESS_CHOICES_EXTENDED
            }

            return render(self.request, "moderator/edit_address.html", context)
        elif 'saveAddress' in self.request.POST.keys():
            # client
            user_id = int(self.request.POST['theUser'])
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
            form = SetupAddressForm(self.request.POST)

            if form.is_valid():
                if address.user == theUser:
                    address.street_address = form.cleaned_data.get(
                        'street_address')
                    address.apartment_address = form.cleaned_data.get(
                        'apartment_address')
                    address.post_town = form.cleaned_data.get('post_town')
                    address.zip = form.cleaned_data.get('zip')
                    address_type = self.request.POST['address_type']
                    if address_type == "B":
                        address.address_type = "B"
                    elif address_type == "S":
                        address.address_type = "S"
                    else:
                        messages.info(
                            self.request, "Something is amiss. Contact IT support for assistance.")
                        return redirect("moderator:search_users")
                    if 'default' in self.request.POST.keys():
                        default = self.request.POST['default']
                        if default == "on":
                            # set this address to default
                            address.default = True
                            # remove default from any other default address of the same type
                            otherAddresses = Address.objects.filter(
                                address_type=address.address_type, default=True)
                            for otherAddress in otherAddresses:
                                otherAddresses.default = False
                                otherAddresses.save()
                    else:
                        address.default = False

                    # save address and notify user
                    address.save()
                    messages.info(
                        self.request, "Address updated and saved")
                    return redirect("moderator:search_users")
                else:
                    messages.info(
                        self.request, "Something is amiss. Contact IT support for assistance.")
                    return redirect("moderator:search_users")
            else:

                ADDRESS_CHOICES_EXTENDED = [
                    {'key': 'B', 'name': 'Fakturaaddress'},
                    {'key': 'S', 'name': 'Leveransaddress'},
                ]

                context = {
                    'form': form,
                    'address': address,
                    'person': theUser,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }

                messages.info(
                    self.request, "Something information is incorrect or missing.")
                return render(self.request, "moderator/edit_address.html", context)
        else:
            messages.warning(
                self.request, "Something went wrong when saving. Contact IT support.")
            return redirect("moderator:search_users")


class NewAddress(View):
    test = "test"


class SettingsView(View):
    def get(self, *args, **kwargs):
        try:
            if 'lookAtSettings' in self.request.POST.keys():
                user = int(self.request.POST['lookAtSettings'])
                # get cookie model, fill in with previous info if there is any
                form = CookieSettingsForm()
                if str(user) != 'AnonymousUser':
                    form.populate(user)

                try:
                    if str(user) == 'AnonymousUser':
                        cookie_settings = Cookies()
                    else:
                        cookie_settings = Cookies.objects.get(user=user)
                except ObjectDoesNotExist:
                    cookie_settings = Cookies()

                context = {
                    'cookie_settings': cookie_settings,
                    'form': form,
                }

                return render(self.request, "cookie_settings.html", context)
        except ObjectDoesNotExist:
            message = "Something went wrong in the viewing of the clients settings. Contact IT support."
            messages.warning(self.request, message)
            return redirect("core:home")

    def post(self, *args, **kwargs):
        try:
            user = self.request.user
            form = CookieSettingsForm(self.request.POST)
            message = ""
            if form.is_valid():
                if str(user) == 'AnonymousUser':
                    cookie_settings = Cookies()
                else:
                    try:
                        cookie_settings = Cookies.objects.get(user=user)
                    except ObjectDoesNotExist:
                        cookie_settings = Cookies()

                    cookie_settings.addapted_adds = form.cleaned_data.get(
                        'addapted_adds')
                    cookie_settings.save()

                    if not cookie_settings.addapted_adds:
                        # turn off addaptive adds and delete cookies here
                        test = ""

                    messages.info(
                        self.request, "Dina inställningar har sparats.")
                    return redirect("core:home")
            else:
                try:
                    if str(user) == 'AnonymousUser':
                        cookie_settings = Cookies()
                    else:
                        cookie_settings = Cookies.objects.get(user=user)
                except ObjectDoesNotExist:
                    cookie_settings = Cookies()

                context = {
                    'cookie_settings': cookie_settings,
                    'form': form,
                }

                return render(self.request, "cookie_settings.html", context)

        except ObjectDoesNotExist:
            message = "Something is wrong in the saving the clients settings. Contact IT support"
            messages.warning(self.request, message)
            return redirect("moderator:overview")


class Subscriptions(View):
    test = "test"

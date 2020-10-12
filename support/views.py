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
from urllib.parse import urlencode
from datetime import datetime
from slugify import slugify
from core.models import *
from member.forms import *
from .forms import *
from core.functions import *
from core.info_error_msg import *


class Overview(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:

            """ We are currently using the generic support form. This is for when we get to the next stage
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

            current_page_support = 1

            context = {
                'support': support,
                'more_support': more_support,
                'current_page_support': current_page_support,
            }"""

            context = {
                'context': '',
            }

            return render(self.request, "support/overview.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 35)
            messages.warning(
                self.request, message)
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
                    message = get_message('error', 36)
                    messages.warning(
                        self.request, message)
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

                return render(self.request, "support/overview.html", context)

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
                    message = get_message('error', 37)
                    messages.warning(
                        self.request, message)
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

                return render(self.request, "support/overview.html", context)

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
                    message = get_message('error', 38)
                    messages.warning(
                        self.request, message)
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

                return render(self.request, "support/overview.html", context)

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
                    message = get_message('error', 39)
                    messages.warning(
                        self.request, message)
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

                return render(self.request, "support/overview.html", context)

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
                    message = get_message('error', 40)
                    messages.warning(
                        self.request, message)
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

                return render(self.request, "support/overview.html", context)

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
                    message = get_message('error', 41)
                    messages.warning(
                        self.request, message)
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

                return render(self.request, "support/overview.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 42)
            messages.warning(
                self.request, message)
            return redirect("support:overview")


class MultipleOrdersView(LoginRequiredMixin, View):
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
                testO = int(o_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if testO != o_pages:
                    o_pages = int(o_pages)
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
                'max_pages': o_pages,
            }

            return render(self.request, "support/order_search.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 43)
            messages.warning(
                self.request, message)
            return redirect("support:overview")

    def post(self, *args, **kwargs):
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "None":
                if 'previousPage' in self.request.POST.keys() or 'nextPage' in self.request.POST.keys() or 'page' in self.request.POST.keys():
                    # fix this to display pagination for some types of searches and only one specific page for other others
                    user_id = int(self.request.POST['search_value'])
                else:
                    # make a form and populate so we can clean the data
                    form = searchOrderForm(self.request.POST)

                    if form.is_valid():
                        # get the values
                        order_ref = form.cleaned_data.get('order_ref')
                        order_id = form.cleaned_data.get('order_id')
                        user_id = form.cleaned_data.get('user_id')
                        # message for object does not exist
                        info_message = get_message('info', 19)
                        if len(order_ref) == 20:
                            # search done on order reference
                            search_value = order_ref

                            try:
                                order = Order.objects.get(ref_code=order_ref)

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
                                    'max_pages': 1,
                                }

                                return render(self.request, "support/order_search.html", context)
                            except ObjectDoesNotExist:
                                messages.info(
                                    self.request, info_message)
                                return redirect("support:orders")

                        elif order_id != None:
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
                                    'max_pages': 1,
                                }

                                return render(self.request, "support/order_search.html", context)
                            except ObjectDoesNotExist:
                                messages.info(
                                    self.request, info_message)
                                return redirect("support:orders")

                        elif user_id != None:
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
                                    'max_pages': o_pages,
                                }

                                return render(self.request, "support/order_search.html", context)

                            except ObjectDoesNotExist:
                                info_message = get_message(
                                    'info', 20)
                                messages.info(
                                    self.request, info_message)
                                return redirect("support:orders")
                        else:
                            return redirect("support:orders")

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                try:
                    number_orders = Order.objects.all(
                    ).count()
                    number_pages = number_users / 20
                    if current_page < number_pages:
                        current_page += 1
                    offset = current_page * 20
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
                    testO = int(o_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testO != o_pages:
                        o_pages = int(o_pages)
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
                    'max_pages': o_pages,
                }

                return render(self.request, "support/order_search.html", context)

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                if current_page > 2:
                    try:
                        if current_page > 1:
                            current_page -= 1
                            offset = current_page * 20
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
                        testO = int(o_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testO != o_pages:
                            o_pages = int(o_pages)
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
                        'max_pages': o_pages,
                    }

                    return render(self.request, "support/order_search.html", context)
                else:
                    try:
                        if current_page > 1:
                            current_page -= 1
                        orders = Order.objects.all()[:20]
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
                        testO = int(o_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testO != o_pages:
                            o_pages = int(o_pages)
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
                        'max_pages': o_pages,
                    }

                    return render(self.request, "support/order_search.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 44)
            messages.warning(
                self.request, message)
            return redirect("support:overview")


class Users(LoginRequiredMixin, View):
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

            return render(self.request, "support/user_search.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 45)
            messages.warning(
                self.request, message)
            return redirect("support:overview")

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

                            return render(self.request, "support/user_search.html", context)

                        except ObjectDoesNotExist:
                            info_message = get_message('info', 21)
                            messages.info(self.request, info_message)
                            return redirect("support:search_users")
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

                            return render(self.request, "support/user_search.html", context)

                        except ObjectDoesNotExist:
                            info_message = get_message('info', 22)
                            messages.info(
                                self.request, info_message)
                            return redirect("support:search_users")
                    else:
                        return redirect("support:search_users")

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

                return render(self.request, "support/user_search.html", context)

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

                        return render(self.request, "support/user_search.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 46)
                        messages.warning(
                            self.request, message)
                        return redirect("support:search_users")

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

                        return render(self.request, "support/user_search.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 47)
                        messages.warning(
                            self.request, message)
                        return redirect("support:search_users")

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

                        return render(self.request, "support/user_search.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 48)
                        messages.warning(
                            self.request, message)
                        return redirect("support:search_users")

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

                        return render(self.request, "support/user_search.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 49)
                        messages.warning(
                            self.request, message)
                        return redirect("support:search_users")
            else:
                message = get_message('error', 50)
                messages.warning(
                    self.request, message)
                return redirect("support:search_users")
        except ObjectDoesNotExist:
            message = get_message('error', 51)
            messages.warning(
                self.request, message)
            return redirect("support:overview")


class OrderView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # this is either a redirect or someone refreshing the page
        # if redirect
        if 'order_ref' in self.request.GET.keys():
            order_ref = self.request.GET['order_ref']
            message = ""

            # get the user's specific order
            try:
                order = Order.objects.get(ref_code=order_ref)
            except ObjectDoesNotExist:
                message = get_message('error', 52)
                messages.warning(
                    self.request, message)
                return redirect("support:orders")

            # get the order items
            orderItems = order.items.all()

            hasPayment = False
            if order.payment_type == "S":
                hasPayment = True
            elif order.paid:
                hasPayment = True
            coupon = order.coupon
            hasCoupon = False
            if coupon:
                hasCoupon = True
            billing_address = order.billing_address
            shipping_address = order.shipping_address
            theClient = order.user
            theClientInfo = UserInfo.objects.get(user=order.user)
            path = self.request.get_full_path()

            context = {
                'order': order,
                'orderItems': orderItems,
                'payment': payment,
                'coupon': coupon,
                'shipping_address': shipping_address,
                'billing_address': billing_address,
                'hasPayment': hasPayment,
                'hasCoupon': hasCoupon,
                'theClient': theClient,
                'theClientInfo': theClientInfo,
            }

            return render(self.request, "support/vieworder.html", context)
        else:
            # this is a refresh, we might loose valuable info if this is just refreshed after a long time so redirect
            message = get_message('error', 109)
            messages.warning(
                self.request, message)
            return redirect("support:orders")

    def post(self, *args, **kwargs):
        try:

            if 'lookAtOrder' in self.request.POST.keys():
                order_id = int(self.request.POST['lookAtOrder'])

                # get the user's specific order
                try:
                    order = Order.objects.get(id=order_id)
                except ObjectDoesNotExist:
                    message = get_message('error', 52)
                    messages.warning(
                        self.request, message)
                    return redirect("support:orders")

                # get the order items
                orderItems = order.items.all()
                payment = order.payment
                hasPayment = False
                if payment:
                    hasPayment = True
                coupon = order.coupon
                hasCoupon = False
                if coupon:
                    hasCoupon = True
                billing_address = order.billing_address
                shipping_address = order.shipping_address
                theClient = order.user
                theClientInfo = UserInfo.objects.get(user=order.user)
                path = self.request.get_full_path()

                context = {
                    'order': order,
                    'orderItems': orderItems,
                    'payment': payment,
                    'coupon': coupon,
                    'shipping_address': shipping_address,
                    'billing_address': billing_address,
                    'hasPayment': hasPayment,
                    'hasCoupon': hasCoupon,
                    'theClient': theClient,
                    'theClientInfo': theClientInfo,
                }

                return render(self.request, "support/vieworder.html", context)

            elif 'back' in self.request.POST.keys():
                # perhaps change this to a soft redirect with search paramaters later if this is found through a search
                return redirect("support:orders")

            elif 'save' in self.request.POST.keys():
                # we have granted or flagged either items or the either order for return.
                # startwith getting the order
                order_id = 0
                if 'order' in self.request.POST.keys():
                    order_id = int(self.request.POST['order'])
                try:
                    order = Order.objects.get(id=order_id)
                except ObjectDoesNotExist:
                    message = get_message('error', 111)
                    messages.warning(
                        self.request, message)
                    return redirect("support:orders")
                # and orderItems
                orderItems = order.items.all()
                # check that the order isnt currently being packed
                if order.being_read:
                    message = get_message('error', 113)
                    messages.warning(
                        self.request, message)
                    return redirect("support:orders")

                # Start with checking if we are returning the entire order
                if 'OrderReturned' in self.request.POST.keys():
                    # the entire order has been returned
                    order.returned = True
                    for item in orderItems:
                        item.returned = True
                        item.save()
                    info_message = get_message('info', 58)
                    messages.info(self.request, info_message)
                if 'OrderUnReturned' in self.request.POST.keys():
                    # the entire order has been returned
                    order.returned = False
                    for item in orderItems:
                        item.returned = False
                        item.save()
                    info_message = get_message('info', 59)
                    messages.info(self.request, info_message)
                if 'OrderToReturnUn' in self.request.POST.keys():
                    # we marked the entire order as being returned
                    order.returned_flag = False
                    # set all order items to returned
                    for item in orderItems:
                        item.returned_flag = False
                        item.save()
                    info_message = get_message('info', 57)
                    messages.info(self.request, info_message)
                if 'OrderToReturn' in self.request.POST.keys():
                    # we marked the entire order as being returned
                    order.returned_flag = True
                    # set all order items to returned
                    for item in orderItems:
                        item.returned_flag = True
                        item.save()
                    info_message = get_message('info', 56)
                    messages.info(self.request, info_message)
                if 'PaybackRequested' in self.request.POST.keys():
                    # we have returned the entire order
                    order.refund_requested = True
                    # set all order items to returned
                    for item in orderItems:
                        item.returned_flag = True
                        item.save()
                    info_message = get_message('info', 52)
                    messages.info(self.request, info_message)
                if 'PaybackRequestCancel' in self.request.POST.keys():
                    # we have returned the entire order
                    order.refund_requested = False
                    # set all order items to returned
                    for item in orderItems:
                        item.returned_flag = False
                        item.save()
                    info_message = get_message('info', 60)
                    messages.info(self.request, info_message)
                if 'PaybackApproved' in self.request.POST.keys():
                        # we have granted full money back without reutrn
                    order.refund_granted = True
                    # set refund for all orderItems
                    for item in orderItems:
                        item.refund = True
                        item.save()
                    info_message = get_message('info', 53)
                    messages.info(self.request, info_message)
                if 'PaybackCancel' in self.request.POST.keys():
                        # we have granted full money back without reutrn
                    order.refund_granted = False
                    # set refund for all orderItems
                    for item in orderItems:
                        item.refund = False
                        item.save()
                    info_message = get_message('info', 61)
                    messages.info(self.request, info_message)
                order.save()
                return redirect("support:orders")

        except ObjectDoesNotExist:
            message = get_message('error', 52)
            messages.warning(
                self.request, message)
            return redirect("support:orders")


class OrderItemView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 10)
        messages.warning(
            self.request, message)
        return redirect("support:orders")

    def post(self, *args, **kwargs):
        if 'handle' in self.request.POST.keys():
            # view item
            # get the ids for order and item
            order_id = 0
            item_id = 0
            if 'order' in self.request.POST.keys():
                order_id = int(self.request.POST['order'])
            if 'item' in self.request.POST.keys():
                item_id = int(self.request.POST['item'])

            # get the order and item

            order = Order()
            item = OrderItem()
            try:
                order = Order.objects.get(id=order_id)
                item = OrderItem.objects.get(id=item_id)
            except ObjectDoesNotExist:
                message = get_message('error', 127)
                messages.warning(
                    self.request, message)
                return redirect("support:orders")

            context = {
                'order': order,
                'item': item,
            }

            return render(self.request, "support/specific_orderItem.html", context)
        elif 'save' in self.request.POST.keys():
            # get the ids for order and item
            order_id = 0
            item_id = 0
            if 'order' in self.request.POST.keys():
                order_id = int(self.request.POST['order'])
            if 'item' in self.request.POST.keys():
                item_id = int(self.request.POST['item'])

            # get the order and item
            order = Order()
            item = OrderItem()
            try:
                order = Order.objects.get(id=order_id)
                item = OrderItem.objects.get(id=item_id)
            except ObjectDoesNotExist:
                message = get_message('error', 52)
                messages.warning(
                    self.request, message)
                return redirect("support:orders")
            if 'ItemToReturn' in self.request.POST.keys():
                item.returned_flag = True
                info_message = get_message('info', 64)
                messages.info(
                    self.request, item.title + info_message)
            if 'ItemToReturnUn' in self.request.POST.keys():
                item.returned_flag = False
                info_message = get_message('info', 65)
                messages.info(
                    self.request, item.title + info_message)
            if 'ItemReturned' in self.request.POST.keys():
                item.returned = True
                info_message = get_message('info', 66)
                messages.info(
                    self.request, item.title + info_message)
            if 'ItemUnReturned' in self.request.POST.keys():
                item.returned = False
                info_message = get_message('info', 67)
                messages.info(
                    self.request, item.title + info_message)
            if 'PaybackRequested' in self.request.POST.keys():
                item.refund_flag = True
                info_message = get_message('info', 68)
                messages.info(
                    self.request, info_message + item.title)
            if 'PaybackRequestCancel' in self.request.POST.keys():
                item.refund_flag = False
                info_message = get_message('info', 69)
                messages.info(
                    self.request, info_message + item.title)
            if 'PaybackApproved' in self.request.POST.keys():
                item.refund = True
                info_message = get_message('info', 70)
                messages.info(
                    self.request, info_message + item.title)
            if 'PaybackCancel' in self.request.POST.keys():
                item.refund = False
                info_message = get_message('info', 71)
                messages.info(
                    self.request, info_message + item.title)

            info_message = get_message('info', 72)
            messages.info(
                self.request, item.title + info_message)
            item.save()
            # changes made create redirect  with variable
            base_url = order.get_absolute_url_support()
            query_string = urlencode({'order_ref': order.ref_code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)


class SupportView(LoginRequiredMixin, View):
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
            message = get_message('error', 53)
            messages.warning(
                self.request, message)
            return redirect("support:overview")


class Errand(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            # get the specific errand. Show all answers and responces as well as a responce form

            context = {
                'errand': errand,
                'responces': responces,
            }

            return render(self.request, "member/my_errand.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 54)
            messages.warning(
                self.request, message)
            return redirect("support:support")


class EditUser(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 92)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

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

                return render(self.request, "support/edit_user.html", context)
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
                        info_message = get_message('info', 23)
                        messages.info(
                            self.request, info_message)
                        return redirect("support:search_users")
                    else:
                        context = {
                            'form': form,
                        }

                        message = get_message('error', 55)
                        messages.warning(
                            self.request, message)
                        return render(self.request, "support/edit_user.html", context)
                else:
                    context = {
                        'form': form,
                    }

                    info_message = get_message('info', 24)
                    messages.info(
                        self.request, info_message)
                    return render(self.request, "support/edit_user.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 56)
            messages.warning(
                self.request, message)
            return redirect("support:overview")


class EditCompany(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 93)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

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

            return render(self.request, "support/company.html", context)
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
                                        message = get_message('error', 57)
                                        messages.warning(
                                            self.request, message)
                                        return redirect("support:search_users")
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
                                    info_message = get_message(
                                        'info', 25)
                                    messages.info(
                                        self.request, info_message)

                                    return redirect("support:search_users")

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
                                    info_message = get_message('info', 25)
                                    messages.info(
                                        self.request, info_message)
                                    return redirect("support:search_users")

                            else:

                                context = {
                                    'a_form': a_form,
                                    'c_form': c_form,
                                    'person': theUser,
                                    'newOrOld': newOrOld,
                                }
                                message = get_message('error', 58)
                                messages.warning(
                                    self.request, message)

                                return render(self.request, "support/company.html", context)
                        else:

                            context = {
                                'a_form': a_form,
                                'c_form': c_form,
                                'person': theUser,
                                'newOrOld': newOrOld,
                            }
                            message = get_message('error', 59)
                            messages.warning(
                                self.request, message)
                            return render(self.request, "support/company.html", context)
                except ObjectDoesNotExist:
                    messages.warning(
                        self.request, "Användare finns inte")

                    return redirect("support:search_users")


class EditAdresses(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 94)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

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
                onsubmit = get_message('warning', 3)

                context = {
                    'addresses': addresses,
                    'person': theUser,
                    'onsubmit': onsubmit,
                }

                return render(self.request, "support/edit_addresses.html", context)
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
                            addressID=theAddress, user=theUser).count()
                        if numberOfCompanies >= 1:
                            # a company with that address exists, redisplay page without changes
                            # !!!!!!!!!!!!!!! this is the wrong message !!!!!!!!!!!
                            message = get_message('error', 128)
                            messages.warning(
                                self.request, message)
                            try:
                                addresses = Address.objects.filter(
                                    user=theUser)
                            except ObjectDoesNotExist:
                                addresses = {}

                            context = {
                                'addresses': addresses,
                                'person': theUser,
                            }

                            return render(self.request, "support/edit_addresses.html", context)
                        else:
                            # no companies with that address
                            addressUnconnected = True
                    except ObjectDoesNotExist:
                        # no companies with that address
                        addressUnconnected = True

                    theAddress.delete()
                    info_message = get_message('info', 26)
                    messages.info(
                        self.request, info_message)
                    # get the specific user's addresses
                    try:
                        addresses = Address.objects.filter(user=theUser)
                    except ObjectDoesNotExist:
                        addresses = {}

                    context = {
                        'addresses': addresses,
                        'person': theUser,
                    }

                    return render(self.request, "support/edit_addresses.html", context)
            else:
                message = get_message('error', 63)
                messages.warning(
                    self.request, message)
                return redirect("support:search_users")

        except ObjectDoesNotExist:
            message = get_message('error', 64)
            messages.warning(
                self.request, message)
            return redirect("support:search_users")


class EditAdress(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 65)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

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

            return render(self.request, "support/edit_address.html", context)

        elif 'saveAddress' in self.request.POST.keys():
            # client
            user_id = 0
            if 'theUser' in self.request.POST.keys():
                user_id = int(self.request.POST['theUser'])
            theUser = User.objects.get(id=user_id)
            # which one are we looking for
            address_id = int(self.request.POST['saveAddress'])
            address = Address.objects.get(id=address_id)
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
                        message = get_message('error', 66)
                        messages.warning(
                            self.request, message)
                        return redirect("support:user_search")
                else:
                    # rerender form

                    context = {
                        'form': form,
                        'address': address,
                        'address_choices': ADDRESS_CHOICES
                    }

                    return render(self.request, "support/edit_address.html", context)
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

                info_message = get_message('info', 27)
                messages.info(self.request, info_message)

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

                return render(self.request, "support/edit_addresses.html", context)
            else:
                # rerender form

                context = {
                    'form': form,
                    'address': address,
                    'address_choices': ADDRESS_CHOICES
                }
                info_message = get_message('info', 28)
                messages.info(self.request, info_message)

                return render(self.request, "support/edit_address.html", context)


class NewAddress(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search as we dont know the user

        message = get_message('error', 67)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

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

            return render(self.request, "support/new_address.html", context)
        elif 'saveAddress' in self.request.POST.keys():
            # client
            user_id = 0
            if 'theUser' in self.request.POST.keys():
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
                    'street_address')
                form_post_town = form.cleaned_data.get('post_town')
                form_address_type = form.cleaned_data.get('address_type')
                default = False
                if 'default_address' in self.request.POST.keys():
                    default = True
                sameShipping, sameBilling, message = sameAddress_support(
                    theUser, form_street_address, form_post_town, form_address_type, default)
                if message != "":
                    return redirect("support:search_users")

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
                    message = get_message('info', 29)
                    if default:
                        message = get_message('info', 30)
                        new_address_default(testShipping)
                        new_address_default(testBilling)

                    messages.info(
                        self.request, message)
                    # render the users addresses for a soft redirect
                    return redirect("support:search_users")

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
                info_message = get_message('info', 31)
                messages.info(self.request, info_message)
                # redirect

                return redirect("support:search_users")
            else:

                context = {
                    'form': form,
                    'person': theUser,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }
                message = get_message('error', 68)
                messages.warning(
                    self.request, message)

                return render(self.request, "support/edit_address.html", context)


class SettingsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 95)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

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

                return render(self.request, "support/client_settings.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 69)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class ProfileView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            # get supports own user info
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()
                info.company = False

            # place info in context and render page

            context = {
                'info': info,
            }

            return render(self.request, "support/my_profile.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 83)
            messages.warning(
                self.request, message)
            return redirect("support:my_overview")


class InfoView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id

            form = UserInformationForm(the_User=self.request.user)

            context = {
                'form': form,
            }

            return render(self.request, "support/my_info.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 84)
            messages.warning(
                self.request, message)
            return redirect("support:my_profile")

    def post(self, *args, **kwargs):
        try:
            form = UserInformationForm(self.request.POST)

            if 'edit' in self.request.POST.keys():

                context = {
                    'form': form,
                }

                return render(self.request, "support/my_info.html", context)

            if form.is_valid():
                try:
                    info = UserInfo.objects.get(user=self.request.user)
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    info.save()
                    info_message = get_message('info', 38)
                    messages.info(
                        self.request, info_message)
                    return redirect("support:my_profile")
                except ObjectDoesNotExist:
                    info = UserInfo()
                    info.user = self.request.user
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    info.save()
                    info_message = get_message('info', 39)
                    messages.info(
                        self.request, info_message)
                    return redirect("support:my_profile")
            else:

                context = {
                    'form': form,
                }

                info_message = get_message('info', 40)
                messages.info(
                    self.request, info_message)

                return render(self.request, "support/my_info.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 85)
            messages.warning(
                self.request, message)
            return redirect("support:my_profile")

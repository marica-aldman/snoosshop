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
from .forms import *


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
                whichPageSupport = self.request.POST['whichPageSupport']
                # get the next ten unanswered support errands and the count of the unanswerd support errands

                try:
                    offset = whichPageSupport * 10
                    support = SupportThread.objects.filter(last_responce=2)[
                        offset: 10]
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

            elif 'whichPageOrder' in self.request.POST.keys():
                whichPageOrder = self.request.POST['whichPageOrder']
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
                orders = Order.objects.filter(
                    being_delivered=False)[:10]
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

            # make search for specific order or customer

            form = searchOrderForm()

            # set current page to 1
            current_page = 1

            context = {
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

            current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys():
                # make a form and populate so we can clean the data
                form = searchOrderForm(self.request.POST)

                if form.is_valid():
                    # get the values
                    order_ref = form.cleaned_data.get('order_ref')
                    order_id = int(form.cleaned_data.get('order_id'))
                    user_id = int(form.cleaned_data.get('user_id'))

                    if len(order_ref) == 20:
                        # search done on order reference

                        try:
                            order = Order.object.get(order_ref=order_ref)

                            # set current page to 1
                            current_page = 1

                            context = {
                                'orders': orders,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': current_page,
                            }

                            return render(self.request, "moderator:mod_vieworder", context)
                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "Order does not exist.")
                            return redirect("moderator:orders")

                    if order_id != 0:
                        # search on order id

                        try:
                            order = Order.object.get(id=order_id)
                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "Order does not exist.")
                            return redirect("moderator:orders")

                    if user_id != 0:
                        # search done on user
                        # get the user

                        try:
                            the_user = User.object.get(id=user_id)
                            try:
                                order = Order.object.get(user=the_user)
                            except ObjectDoesNotExist:
                                order = Order()
                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, "User does not exist.")
                            return redirect("moderator:orders")

            elif 'nextPage' in self.request.POST.keys():
                test = "test"
            elif 'previousPage' in self.request.POST.keys():
                test = "test"

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something is wrong with the page that displays orders. Contact IT support for assistance.")
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


class Users(View):
    def get(self, *args, **kwargs):
        try:
            # get the first 20 users and a search bar for an induvidual.

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
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        try:
            # get the search result only and display buttons for settings, orders, support errands etc
            test = "test"
        except ObjectDoesNotExist:
            return redirect("moderator:search_users")


class EditUser(View):
    def get(self, *args, **kwargs):
        try:
            # get the specific user's profile

            form = ProfileForm()
            form = form.__init__(form, user=self.request.user)

            context = {
                'form': form,
            }

            return render(self.request, "member/edit_my_user_info.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("moderator:search_users")


class EditAdress(View):
    def get(self, *args, **kwargs):
        try:
            # get the specific user's address

            form = AdressForm()
            form = form.__init__(form, user=self.request.user)

            context = {
                'form': form,
            }

            return render(self.request, "member/edit_my_adress.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("moderator:search_users")


class CookieSettingsView(View):
    def get(self, *args, **kwargs):
        try:
            # get the moderators cookie settings

            try:
                cookie_settings = Cookies().__class__.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                cookie_settings = {}

            context = {
                'cookie_settings': cookie_settings,
            }

            return render(self.request, "cookie_settings.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing the cookie settings page. Contact the support for assistance.")
            return redirect("moderator:overview")


class SettingsView(View):
    def get(self, *args, **kwargs):
        try:
            # get the specific user's settings

            try:
                cookieSettings = Cookies().__class__.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                cookieSettings = {}

            context = {
                'cookies': cookieSettings,
            }

            return render(self.request, "member/my_settings.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your settings. Contact the support for assistance.")
            return redirect("moderator:search_users")

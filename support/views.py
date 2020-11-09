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


class Overview(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        context = {
            'gdpr_check': gdpr_check,
            'context': '',
        }

        return render(self.request, "support/overview.html", context)


class MultipleOrdersView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        limit = default_pagination_values
        try:
            # get the first orders and a count of all orders

            try:
                orders = Order.objects.filter(ordered=True)[:limit]
                number_orders = Order.objects.filter(ordered=True).count()
            except ObjectDoesNotExist:
                orders = {}
                number_orders = 0

            # figure out how many pages there are
            # if there are only the limit or fewer pages will be 1

            o_pages = 1

            if number_orders > limit:
                # if there are more we divide by the limit
                o_pages = number_orders / limit
                # see if there is a decimal
                testO = int(o_pages)
                # if there isn't an even number make an extra page for the last group
                if testO != o_pages:
                    o_pages = int(o_pages)
                    o_pages += 1
                # we need this to be an int
                if type(o_pages) != "int":
                    o_pages = int(o_pages)

            # set current page to 1
            current_page = 1

            # create a list for a ul to work through

            more_orders, where = get_list_of_pages(current_page, o_pages)

            # set next and previous pages
            # this is true
            previous_page = current_page - 1
            next_page = current_page + 1

            # unless

            previous_page = True
            next_page = True

            if current_page <= 1:
                previous_page = False
            if o_pages <= current_page:
                next_page = False
            # check if we are near an end point and need fancy looking start or end
            start = False
            end = False

            if where == "no extras":
                start = False
                end = False
            elif where == "start":
                start = False
                end = True
            elif where == "end":
                start = True
                end = False
            elif where == "mid":
                start = True
                end = True

            # make search for specific order or customer

            form = searchOrderForm()

            # when we are searching for user_id we will want to display it in the form up top otherwise not

            paging_search = False

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = ""

            context = {
                'gdpr_check': gdpr_check,
                'search_type': search_type,
                'search_value': search_value,
                'orders': orders,
                'more_orders': more_orders,
                'form': form,
                'current_page': current_page,
                'max_pages': o_pages,
                'previous_page': previous_page,
                'next_page': next_page,
                'end': end,
                'start': start,
            }

            return render(self.request, "support/order_search.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 43)
            messages.warning(
                self.request, message)
            return redirect("support:overview")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        limit = default_pagination_values
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "None":
                if 'previousPage' in self.request.POST.keys() or 'nextPage' in self.request.POST.keys() or 'page' in self.request.POST.keys():
                    print("here1")
                    # we are paginating a perticular users orders
                    user_id = int(self.request.POST['searchValue'])
                    theUser = User.objects.get(id=user_id)

                    if 'nextPage' in self.request.POST.keys():

                        try:
                            number_orders = Order.objects.filter(
                                user=theUser).count()
                        except ObjectDoesNotExist:
                            number_orders = 0

                        # figure out how many pages there are
                        # if there are only the limit or fewer pages will be 1

                        o_pages = 1

                        if number_orders > limit:
                            # if there are more we divide by the limit
                            o_pages = number_orders / limit
                            # see if there is a decimal
                            testO = int(o_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testO != o_pages:
                                o_pages = int(o_pages)
                                o_pages += 1
                            # we need this to be an int
                            if type(o_pages) != "int":
                                o_pages = int(o_pages)

                        try:
                            if current_page < o_pages:
                                current_page += 1
                            offset = (current_page - 1) * limit
                            o_l = offset + limit
                            orders = Order.objects.filter(
                                user=theUser)[offset:o_l]
                        except ObjectDoesNotExist:
                            orders = {}

                        # create a list for a ul to work through

                        more_orders, where = get_list_of_pages(
                            current_page, o_pages)

                        # set next and previous pages
                        # this is true

                        previous_page = True
                        next_page = True

                        # unless

                        if current_page <= 1:
                            previous_page = False
                        if o_pages <= current_page:
                            next_page = False

                        # check if we are near an end point and need fancy looking start or end

                        start = False
                        end = False

                        if where == "no extras":
                            start = False
                            end = False
                        elif where == "start":
                            start = False
                            end = True
                        elif where == "end":
                            start = True
                            end = False
                        elif where == "mid":
                            start = True
                            end = True

                        # make search for specific order or customer

                        form = searchOrderForm()

                        # when we are searching for user_id we will want to display it in the form up top otherwise not

                        paging_search = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "Search"
                        search_value = user_id

                        context = {
                            'gdpr_check': gdpr_check,
                            'search_type': search_type,
                            'search_value': search_value,
                            'orders': orders,
                            'more_orders': more_orders,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': o_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                            'paging_search': paging_search,
                        }

                        return render(self.request, "support/order_search.html", context)

                    elif 'previousPage' in self.request.POST.keys():

                        try:
                            number_orders = Order.objects.filter(
                                user=theUser).count()
                        except ObjectDoesNotExist:
                            number_orders = 0

                        # figure out how many pages there are
                        # if there are only the limit or fewer pages will be 1

                        o_pages = 1

                        if number_orders > limit:
                            # if there are more we divide by the limit
                            o_pages = number_orders / limit
                            # see if there is a decimal
                            testO = int(o_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testO != o_pages:
                                o_pages = int(o_pages)
                                o_pages += 1
                            # we need this to be an int
                            if type(o_pages) != "int":
                                o_pages = int(o_pages)

                        if current_page >= 3:
                            try:
                                current_page = current_page - 1
                                offset = (current_page - 1) * limit
                                o_l = offset + limit
                                orders = Order.objects.filter(
                                    user=theUser)[offset:o_l]
                            except ObjectDoesNotExist:
                                orders = {}

                            # create a list for a ul to work through

                            more_orders, where = get_list_of_pages(
                                current_page, o_pages)

                            # set next and previous pages
                            # this is true

                            previous_page = True
                            next_page = True

                            # unless

                            if current_page <= 1:
                                previous_page = False
                            if o_pages <= current_page:
                                next_page = False

                            # check if we are near an end point and need fancy looking start or end

                            start = False
                            end = False

                            if where == "no extras":
                                start = False
                                end = False
                            elif where == "start":
                                start = False
                                end = True
                            elif where == "end":
                                start = True
                                end = False
                            elif where == "mid":
                                start = True
                                end = True

                            # make search for specific order or customer

                            form = searchOrderForm()

                            # when we are searching for user_id we will want to display it in the form up top otherwise not

                            paging_search = True

                            # set the hidden value for wether or not we have done a search

                            search_type = "Search"
                            search_value = user_id

                            context = {
                                'gdpr_check': gdpr_check,
                                'search_type': search_type,
                                'search_value': search_value,
                                'orders': orders,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': o_pages,
                                'previous_page': previous_page,
                                'next_page': next_page,
                                'end': end,
                                'start': start,
                                'paging_search': paging_search,
                            }

                            return render(self.request, "support/order_search.html", context)
                        else:
                            try:
                                if current_page == 2:
                                    current_page -= 1
                                orders = Order.objects.filter(
                                    user=theUser)[:limit]
                            except ObjectDoesNotExist:
                                orders = {}

                            # create a list for a ul to work through

                            more_orders, where = get_list_of_pages(
                                current_page, o_pages)

                            # set next and previous pages
                            # this is true

                            previous_page = True
                            next_page = True

                            # unless

                            if current_page <= 1:
                                previous_page = False
                            if o_pages <= current_page:
                                next_page = False

                            # check if we are near an end point and need fancy looking start or end

                            start = False
                            end = False

                            if where == "no extras":
                                start = False
                                end = False
                            elif where == "start":
                                start = False
                                end = True
                            elif where == "end":
                                start = True
                                end = False
                            elif where == "mid":
                                start = True
                                end = True

                            # make search for specific order or customer

                            form = searchOrderForm()

                            # when we are searching for user_id we will want to display it in the form up top otherwise not

                            paging_search = True

                            # set the hidden value for wether or not we have done a search

                            search_type = "Search"
                            search_value = user_id

                            context = {
                                'gdpr_check': gdpr_check,
                                'search_type': search_type,
                                'search_value': search_value,
                                'orders': orders,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': o_pages,
                                'previous_page': previous_page,
                                'next_page': next_page,
                                'end': end,
                                'start': start,
                                'paging_search': paging_search,
                            }

                            return render(self.request, "support/order_search.html", context)

                    elif 'page' in self.request.POST.keys():
                        page = int(self.request.POST['page'])
                        try:
                            number_orders = Order.objects.filter(
                                user=theUser).count()
                        except ObjectDoesNotExist:
                            number_orders = 0

                        # figure out how many pages there are
                        # if there are only the limit or fewer pages will be 1

                        o_pages = 1

                        if number_orders > limit:
                            # if there are more we divide by the limit
                            o_pages = number_orders / limit
                            # see if there is a decimal
                            testO = int(o_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testO != o_pages:
                                o_pages = int(o_pages)
                                o_pages += 1
                            # we need this to be an int
                            if type(o_pages) != "int":
                                o_pages = int(o_pages)

                        if page >= 2:
                            try:
                                current_page = page
                                offset = (current_page - 1) * limit
                                o_l = offset + limit
                                orders = Order.objects.filter(
                                    user=theUser)[offset:o_l]
                            except ObjectDoesNotExist:
                                orders = {}

                            # create a list for a ul to work through

                            more_orders, where = get_list_of_pages(
                                current_page, o_pages)

                            # set next and previous pages
                            # this is true

                            previous_page = True
                            next_page = True

                            # unless

                            if current_page <= 1:
                                previous_page = False
                            if o_pages <= current_page:
                                next_page = False

                            # check if we are near an end point and need fancy looking start or end

                            start = False
                            end = False

                            if where == "no extras":
                                start = False
                                end = False
                            elif where == "start":
                                start = False
                                end = True
                            elif where == "end":
                                start = True
                                end = False
                            elif where == "mid":
                                start = True
                                end = True

                            # make search for specific order or customer

                            form = searchOrderForm()

                            # when we are searching for user_id we will want to display it in the form up top otherwise not

                            paging_search = True

                            # set the hidden value for wether or not we have done a search

                            search_type = "Search"
                            search_value = user_id

                            context = {
                                'gdpr_check': gdpr_check,
                                'search_type': search_type,
                                'search_value': search_value,
                                'orders': orders,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': o_pages,
                                'previous_page': previous_page,
                                'next_page': next_page,
                                'end': end,
                                'start': start,
                                'paging_search': paging_search,
                            }

                            return render(self.request, "support/order_search.html", context)
                        else:
                            try:
                                current_page = page
                                orders = Order.objects.filter(
                                    user=theUser)[:limit]
                            except ObjectDoesNotExist:
                                orders = {}

                            # create a list for a ul to work through

                            more_orders, where = get_list_of_pages(
                                current_page, o_pages)

                            # set next and previous pages
                            # this is true

                            previous_page = True
                            next_page = True

                            # unless

                            if current_page <= 1:
                                previous_page = False
                            if o_pages <= current_page:
                                next_page = False

                            # check if we are near an end point and need fancy looking start or end

                            start = False
                            end = False

                            if where == "no extras":
                                start = False
                                end = False
                            elif where == "start":
                                start = False
                                end = True
                            elif where == "end":
                                start = True
                                end = False
                            elif where == "mid":
                                start = True
                                end = True

                            # make search for specific order or customer

                            form = searchOrderForm()

                            # when we are searching for user_id we will want to display it in the form up top otherwise not

                            paging_search = False

                            # set the hidden value for wether or not we have done a search

                            search_type = "Search"
                            search_value = user_id

                            context = {
                                'gdpr_check': gdpr_check,
                                'search_type': search_type,
                                'search_value': search_value,
                                'orders': orders,
                                'more_orders': more_orders,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': o_pages,
                                'previous_page': previous_page,
                                'next_page': next_page,
                                'end': end,
                                'start': start,
                                'paging_search': paging_search,
                            }

                            return render(self.request, "support/order_search.html", context)
                    else:
                        # something went wrong but just redirect this shouldnt happen
                        return redirect("support:orders")

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

                            try:
                                orders = Order.objects.filter(
                                    ref_code=order_ref)
                                print(orders)
                                number_orders = Order.objects.filter(
                                    ref_code=order_ref).count()

                                # if there are only the limit or fewer pages will be 1

                                o_pages = 1

                                if number_orders > limit:
                                    # if there are more we divide by the limit
                                    o_pages = number_orders / limit
                                    # see if there is a decimal
                                    testO = int(o_pages)
                                    # if there isn't an even number make an extra page for the last group
                                    if testO != o_pages:
                                        o_pages = int(o_pages)
                                        o_pages += 1
                                    # we need this to be an int
                                    if type(o_pages) != "int":
                                        o_pages = int(o_pages)

                                # create a list for a ul to work through

                                more_orders, where = get_list_of_pages(
                                    current_page, o_pages)

                                # set next and previous pages
                                # this is true

                                previous_page = True
                                next_page = True

                                # unless

                                if current_page <= 1:
                                    previous_page = False
                                if o_pages <= current_page:
                                    next_page = False

                                # check if we are near an end point and need fancy looking start or end

                                start = False
                                end = False

                                if where == "no extras":
                                    start = False
                                    end = False
                                elif where == "start":
                                    start = False
                                    end = True
                                elif where == "end":
                                    start = True
                                    end = False
                                elif where == "mid":
                                    start = True
                                    end = True

                                # set current page to 1
                                current_page = 1

                                # when we are searching for user_id we will want to display it in the form up top otherwise not

                                paging_search = False

                                # set the search type

                                search_type = "search"
                                search_value = order_ref

                                context = {
                                    'gdpr_check': gdpr_check,
                                    'search_type': search_type,
                                    'search_value': search_value,
                                    'orders': orders,
                                    'more_orders': more_orders,
                                    'form': form,
                                    'current_page': current_page,
                                    'max_pages': o_pages,
                                    'previous_page': previous_page,
                                    'next_page': next_page,
                                    'end': end,
                                    'start': start,
                                    'paging_search': paging_search,
                                }

                                return render(self.request, "support/order_search.html", context)

                            except ObjectDoesNotExist:
                                info_message = get_message(
                                    'info', 20)
                                messages.info(
                                    self.request, info_message)
                                return redirect("support:orders")

                        elif order_id != None:

                            try:
                                orders = Order.objects.filter(
                                    id=order_id)
                                number_orders = Order.objects.filter(
                                    id=order_id).count()

                                # if there are only the limit or fewer pages will be 1

                                o_pages = 1

                                if number_orders > limit:
                                    # if there are more we divide by the limit
                                    o_pages = number_orders / limit
                                    # see if there is a decimal
                                    testO = int(o_pages)
                                    # if there isn't an even number make an extra page for the last group
                                    if testO != o_pages:
                                        o_pages = int(o_pages)
                                        o_pages += 1
                                    # we need this to be an int
                                    if type(o_pages) != "int":
                                        o_pages = int(o_pages)

                                # create a list for a ul to work through

                                more_orders, where = get_list_of_pages(
                                    current_page, o_pages)

                                # set next and previous pages
                                # this is true

                                previous_page = True
                                next_page = True

                                # unless

                                if current_page <= 1:
                                    previous_page = False
                                if o_pages <= current_page:
                                    next_page = False

                                # check if we are near an end point and need fancy looking start or end

                                start = False
                                end = False

                                if where == "no extras":
                                    start = False
                                    end = False
                                elif where == "start":
                                    start = False
                                    end = True
                                elif where == "end":
                                    start = True
                                    end = False
                                elif where == "mid":
                                    start = True
                                    end = True

                                # set current page to 1
                                current_page = 1

                                # when we are searching for user_id we will want to display it in the form up top otherwise not

                                paging_search = False

                                # set the search type

                                search_type = "search"
                                search_value = order_id

                                context = {
                                    'gdpr_check': gdpr_check,
                                    'search_type': search_type,
                                    'search_value': search_value,
                                    'orders': orders,
                                    'more_orders': more_orders,
                                    'form': form,
                                    'current_page': current_page,
                                    'max_pages': o_pages,
                                    'previous_page': previous_page,
                                    'next_page': next_page,
                                    'end': end,
                                    'start': start,
                                    'paging_search': paging_search,
                                }

                                return render(self.request, "support/order_search.html", context)

                            except ObjectDoesNotExist:
                                info_message = get_message(
                                    'info', 20)
                                messages.info(
                                    self.request, info_message)
                                return redirect("support:orders")

                        elif user_id != None:

                            try:
                                the_user = User.objects.get(id=user_id)
                                orders = Order.objects.filter(
                                    user=the_user)[:limit]
                                number_orders = Order.objects.filter(
                                    user=the_user).count()

                                # if there are only the limit or fewer pages will be 1

                                o_pages = 1

                                if number_orders > limit:
                                    # if there are more we divide by the limit
                                    o_pages = number_orders / limit
                                    # see if there is a decimal
                                    testO = int(o_pages)
                                    # if there isn't an even number make an extra page for the last group
                                    if testO != o_pages:
                                        o_pages = int(o_pages)
                                        o_pages += 1
                                    # we need this to be an int
                                    if type(o_pages) != "int":
                                        o_pages = int(o_pages)

                                # create a list for a ul to work through

                                more_orders, where = get_list_of_pages(
                                    current_page, o_pages)

                                # set next and previous pages
                                # this is true

                                previous_page = True
                                next_page = True

                                # unless

                                if current_page <= 1:
                                    previous_page = False
                                if o_pages <= current_page:
                                    next_page = False

                                # check if we are near an end point and need fancy looking start or end

                                start = False
                                end = False

                                if where == "no extras":
                                    start = False
                                    end = False
                                elif where == "start":
                                    start = False
                                    end = True
                                elif where == "end":
                                    start = True
                                    end = False
                                elif where == "mid":
                                    start = True
                                    end = True

                                # set current page to 1
                                current_page = 1

                                # when we are searching for user_id we will want to display it in the form up top otherwise not

                                paging_search = False

                                # set the search type

                                search_type = "search"
                                search_value = user_id

                                context = {
                                    'gdpr_check': gdpr_check,
                                    'search_type': search_type,
                                    'search_value': search_value,
                                    'orders': orders,
                                    'more_orders': more_orders,
                                    'form': form,
                                    'current_page': current_page,
                                    'max_pages': o_pages,
                                    'previous_page': previous_page,
                                    'next_page': next_page,
                                    'end': end,
                                    'start': start,
                                    'paging_search': paging_search,
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

                try:
                    number_orders = Order.objects.all(
                    ).count()
                except ObjectDoesNotExist:
                    number_orders = 0

                # figure out how many pages there are
                # if there are only the limit or fewer pages will be 1

                o_pages = 1

                if number_orders > limit:
                    # if there are more we divide by the limit
                    o_pages = number_orders / limit
                    # see if there is a decimal
                    testO = int(o_pages)
                    # if there isn't an even number make an extra page for the last group
                    if testO != o_pages:
                        o_pages = int(o_pages)
                        o_pages += 1
                    # we need this to be an int
                    if type(o_pages) != "int":
                        o_pages = int(o_pages)

                try:
                    if current_page < o_pages:
                        current_page += 1
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    orders = Order.objects.filter(ordered=True)[offset:o_l]
                except ObjectDoesNotExist:
                    orders = {}

                # create a list for a ul to work through

                more_orders, where = get_list_of_pages(current_page, o_pages)

                # set next and previous pages
                # this is true

                previous_page = True
                next_page = True

                # unless

                if current_page <= 1:
                    previous_page = False
                if o_pages <= current_page:
                    next_page = False

                # check if we are near an end point and need fancy looking start or end

                start = False
                end = False

                if where == "no extras":
                    start = False
                    end = False
                elif where == "start":
                    start = False
                    end = True
                elif where == "end":
                    start = True
                    end = False
                elif where == "mid":
                    start = True
                    end = True

                # make search for specific order or customer

                form = searchOrderForm()

                # when we are searching for user_id we will want to display it in the form up top otherwise not

                paging_search = False

                # set the hidden value for wether or not we have done a search

                search_type = "None"
                search_value = ""

                context = {
                    'gdpr_check': gdpr_check,
                    'search_type': search_type,
                    'search_value': search_value,
                    'orders': orders,
                    'more_orders': more_orders,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': o_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "support/order_search.html", context)

            elif 'previousPage' in self.request.POST.keys():

                try:
                    number_orders = Order.objects.all(
                    ).count()
                except ObjectDoesNotExist:
                    number_orders = 0

                # figure out how many pages there are
                # if there are only the limit or fewer pages will be 1

                o_pages = 1

                if number_orders > limit:
                    # if there are more we divide by the limit
                    o_pages = number_orders / limit
                    # see if there is a decimal
                    testO = int(o_pages)
                    # if there isn't an even number make an extra page for the last group
                    if testO != o_pages:
                        o_pages = int(o_pages)
                        o_pages += 1
                    # we need this to be an int
                    if type(o_pages) != "int":
                        o_pages = int(o_pages)

                if current_page >= 3:
                    try:
                        current_page = current_page - 1
                        offset = (current_page - 1) * limit
                        o_l = offset + limit
                        orders = Order.objects.filter(ordered=True)[offset:o_l]
                    except ObjectDoesNotExist:
                        orders = {}

                    # create a list for a ul to work through

                    more_orders, where = get_list_of_pages(
                        current_page, o_pages)

                    # set next and previous pages
                    # this is true

                    previous_page = True
                    next_page = True

                    # unless

                    if current_page <= 1:
                        previous_page = False
                    if o_pages <= current_page:
                        next_page = False

                    # check if we are near an end point and need fancy looking start or end

                    start = False
                    end = False

                    if where == "no extras":
                        start = False
                        end = False
                    elif where == "start":
                        start = False
                        end = True
                    elif where == "end":
                        start = True
                        end = False
                    elif where == "mid":
                        start = True
                        end = True

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # when we are searching for user_id we will want to display it in the form up top otherwise not

                    paging_search = False

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = ""

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_type': search_type,
                        'search_value': search_value,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                        'max_pages': o_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "support/order_search.html", context)
                else:
                    try:
                        if current_page == 2:
                            current_page -= 1
                        orders = Order.objects.filter(ordered=True)[:limit]
                    except ObjectDoesNotExist:
                        orders = {}

                    # create a list for a ul to work through

                    more_orders, where = get_list_of_pages(
                        current_page, o_pages)

                    # set next and previous pages
                    # this is true

                    previous_page = True
                    next_page = True

                    # unless

                    if current_page <= 1:
                        previous_page = False
                    if o_pages <= current_page:
                        next_page = False

                    # check if we are near an end point and need fancy looking start or end

                    start = False
                    end = False

                    if where == "no extras":
                        start = False
                        end = False
                    elif where == "start":
                        start = False
                        end = True
                    elif where == "end":
                        start = True
                        end = False
                    elif where == "mid":
                        start = True
                        end = True

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # when we are searching for user_id we will want to display it in the form up top otherwise not

                    paging_search = False

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = ""

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_type': search_type,
                        'search_value': search_value,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                        'max_pages': o_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "support/order_search.html", context)

            elif 'page' in self.request.POST.keys():
                page = int(self.request.POST['page'])
                try:
                    number_orders = Order.objects.all(
                    ).count()
                except ObjectDoesNotExist:
                    number_orders = 0

                # figure out how many pages there are
                # if there are only the limit or fewer pages will be 1

                o_pages = 1

                if number_orders > limit:
                    # if there are more we divide by the limit
                    o_pages = number_orders / limit
                    # see if there is a decimal
                    testO = int(o_pages)
                    # if there isn't an even number make an extra page for the last group
                    if testO != o_pages:
                        o_pages = int(o_pages)
                        o_pages += 1
                    # we need this to be an int
                    if type(o_pages) != "int":
                        o_pages = int(o_pages)

                if page >= 2:
                    try:
                        current_page = page
                        offset = (current_page - 1) * limit
                        o_l = offset + limit
                        orders = Order.objects.filter(ordered=True)[offset:o_l]
                    except ObjectDoesNotExist:
                        orders = {}

                    # create a list for a ul to work through

                    more_orders, where = get_list_of_pages(
                        current_page, o_pages)

                    # set next and previous pages
                    # this is true

                    previous_page = True
                    next_page = True

                    # unless

                    if current_page <= 1:
                        previous_page = False
                    if o_pages <= current_page:
                        next_page = False

                    # check if we are near an end point and need fancy looking start or end

                    start = False
                    end = False

                    if where == "no extras":
                        start = False
                        end = False
                    elif where == "start":
                        start = False
                        end = True
                    elif where == "end":
                        start = True
                        end = False
                    elif where == "mid":
                        start = True
                        end = True

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # when we are searching for user_id we will want to display it in the form up top otherwise not

                    paging_search = False

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = ""

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_type': search_type,
                        'search_value': search_value,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                        'max_pages': o_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "support/order_search.html", context)
                else:
                    try:
                        current_page = page
                        orders = Order.objects.filter(ordered=True)[:limit]
                    except ObjectDoesNotExist:
                        orders = {}

                    # create a list for a ul to work through

                    more_orders, where = get_list_of_pages(
                        current_page, o_pages)

                    # set next and previous pages
                    # this is true

                    previous_page = True
                    next_page = True

                    # unless

                    if current_page <= 1:
                        previous_page = False
                    if o_pages <= current_page:
                        next_page = False

                    # check if we are near an end point and need fancy looking start or end

                    start = False
                    end = False

                    if where == "no extras":
                        start = False
                        end = False
                    elif where == "start":
                        start = False
                        end = True
                    elif where == "end":
                        start = True
                        end = False
                    elif where == "mid":
                        start = True
                        end = True

                    # make search for specific order or customer

                    form = searchOrderForm()

                    # when we are searching for user_id we will want to display it in the form up top otherwise not

                    paging_search = False

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = ""

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_type': search_type,
                        'search_value': search_value,
                        'orders': orders,
                        'more_orders': more_orders,
                        'form': form,
                        'current_page': current_page,
                        'max_pages': o_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "support/order_search.html", context)
            else:
                # something went wrong but just redirect this shouldnt happen
                return redirect("support:orders")

        except ObjectDoesNotExist:
            message = get_message('error', 44)
            messages.warning(
                self.request, message)
            return redirect("support:overview")


class Users(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get the limit of users and a count of all users

            limit = default_pagination_values

            try:
                user_objects = User.objects.filter(
                    groups__name='client')[:limit]
                users = []
                for a_user in user_objects:
                    the_user = UserInfo.objects.get(user=a_user)
                    users.append({
                        'id': a_user.id,
                        'person': the_user})
                number_users = User.objects.filter(
                    groups__name='client').count()
            except ObjectDoesNotExist:
                users = []
                number_users = 0

            # figure out how many pages there are
            # if there are only the limit or fewer pages will be 1

            u_pages = 1

            if number_users > limit:
                # if there are more we divide by the limit
                u_pages = number_users / limit
                # see if there is a decimal
                testU = int(u_pages)
                # if there isn't an even number make an extra page for the last group
                if testU != u_pages:
                    u_pages = int(u_pages)
                    u_pages += 1
                if type(u_pages) != "int":
                    u_pages = int(u_pages)

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

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = ""

            context = {
                'gdpr_check': gdpr_check,
                'search_type': search_type,
                'search_value': search_value,
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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # GDPR check
            limit = default_pagination_values
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])
            else:
                messages.warning(
                    self.request, "Något har gått fel. Kontakta IT supporten.")
                return redirect("support:search_users")

            # what button did we press

            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "None":
                # make a form and populate so we can clean the data
                form = searchUserForm(self.request.POST)

                if form.is_valid():
                    # get the values
                    user_id = form.cleaned_data.get('user_id')
                    if user_id == None:
                        # resetting page
                        return redirect("support:search_users")
                    # search done on user
                    search_type = user_id
                    # get the user

                    try:
                        the_user = []
                        the_user_object = User.objects.get(id=user_id)

                        a_user = UserInfo.objects.get(
                            user=the_user_object)

                        the_user.append({
                            "id": the_user_object.id,
                            'person': a_user,
                        })

                        # there is only one
                        u_pages = 1
                        more_users = [{'number': 1}]

                        # set current page to 1
                        current_page = 1

                        context = {
                            'search_type': search_type,
                            'users': the_user,
                            'more_users': more_users,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': u_pages,
                        }

                        return render(self.request, "support/user_search.html", context)

                    except ObjectDoesNotExist:
                        info_message = get_message('info', 22)
                        print(info_message)
                        messages.info(
                            self.request, info_message)
                        return redirect("support:search_users")
                else:
                    messages.info(
                        self.request, "Formuläret ej korrekt ifyllt, var god använd siffror för id. Om problemet kvarstår kontakta IT supporten.")
                    return redirect("support:search_users")

            elif 'nextPage' in self.request.POST.keys():
                limit = default_pagination_values
                # get what type of search
                search_type = self.request.POST['searched']
                if search_type != "None":
                    try:
                        search_type = int(search_type)
                    except ValueError:
                        messages.warning(
                            self.request, "ID kan endast skrivas med siffror.")
                        return redirect("support:search_users")
                try:
                    current_page = int(self.request.POST['page'])
                except ValueError:
                    messages.warning(
                        self.request, "Något gick fel, om detta fortsätter kontakta it supporten.")
                    return redirect("support:search_users")

                if search_type == None:
                    try:
                        number_users = User.objects.filter(
                            groups__name='client').count()
                    except ObjectDoesNotExist:
                        users = {}
                        number_users = 0

                    # figure out how many pages there are
                    # if there are only the limit or fewer number of pages will be 1

                    u_pages = 1

                    if number_users > limit:
                        # if there are more we divide by the limit
                        u_pages = number_users / limit
                        # see if there is a decimal
                        testU = int(u_pages)
                        # if there isn't an even number make an extra page for the last group
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
                        try:
                            if current_page < u_pages:
                                current_page += 1

                            offset = current_page * limit
                            o_and_l = offset + limit
                            user_objects = User.objects.filter(
                                groups__name='client')[offset:o_and_l]
                            users = []
                            for a_user in user_objects:
                                the_user = UserInfo.objects.get(user=a_user)
                                users.append({
                                    'id': a_user.id,
                                    'person': the_user})
                        except ObjectDoesNotExist:
                            message = get_message('error', 48)
                            messages.warning(
                                self.request, message)
                            return redirect("support:search_users")

                    # make search for specific order or customer

                    form = searchUserForm()

                    # set the hidden value for wether or not we have done a search

                    search_type = "None"
                    search_value = ""

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_type': search_type,
                        'search_value': search_value,
                        'users': users,
                        'more_users': more_users,
                        'form': form,
                        'current_page': current_page,
                        'max_pages': u_pages,
                    }

                    return render(self.request, "support/user_search.html", context)
                else:
                    try:
                        user_objects = User.objects.filter(
                            id=search_type)
                        users = []
                        for a_user in user_objects:
                            the_user = UserInfo.objects.get(user=a_user)
                            users.append({
                                'id': a_user.id,
                                'person': the_user})
                    except ObjectDoesNotExist:
                        message = get_message('error', 48)
                        messages.warning(
                            self.request, message)
                        return redirect("support:search_users")

                    # there is only one
                    u_pages = 1
                    more_users = [{'number': 1}]

                    # set current page to 1
                    current_page = 1

                    # set the search type

                    search_type = "userID"

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_type': search_type,
                        'users': the_user,
                        'more_users': more_users,
                        'form': form,
                        'current_page': current_page,
                        'max_pages': u_pages,
                    }

                    return render(self.request, "support/user_search.html", context)

            elif 'previousPage' in self.request.POST.keys():
                search_type = self.request.POST['searched']
                if search_type != None:
                    try:
                        search_type = int(search_type)
                    except ValueError:
                        messages.warning(
                            self.request, "ID kan endast skrivas med siffror.")
                        return redirect("support:search_users")

                limit = default_pagination_values
                if current_page > 2:
                    try:
                        if current_page > 1:
                            current_page -= 1
                        offset = current_page * limit
                        o_and_l = offset + limit
                        users = User.objects.filter(
                            groups__name='client')[offset:o_and_l]
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages there are
                        # if there are only the limit or fewer number of pages will be 1

                        u_pages = 1

                        if number_users > limit:
                            # if there are more we divide by the limit
                            u_pages = number_users / limit
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1
                            if type(u_pages) != "int":
                                u_pages = int(u_pages)

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'gdpr_check': gdpr_check,
                            'search_type': search_type,
                            'search_value': search_value,
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
                        if current_page < 1:
                            current_page = 1
                        users = User.objects.filter(
                            groups__name='client')[:limit]
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages there are
                        # if there are only the limit or fewer number of pages will be 1

                        u_pages = 1

                        if number_users > limit:
                            # if there are more we divide by the limit
                            u_pages = number_users / 20
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1
                            if type(u_pages) != "int":
                                u_pages = int(u_pages)

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'gdpr_check': gdpr_check,
                            'search_type': search_type,
                            'search_value': search_value,
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
                search_type = self.request.POST['searched']
                if search_type != None:
                    try:
                        search_type = int(search_type)
                    except ValueError:
                        messages.warning(
                            self.request, "ID kan endast skrivas med siffror.")
                        return redirect("support:search_users")
                try:
                    current_page = int(self.request.POST['page'])
                except ValueError:
                    messages.warning(
                        self.request, "Något gick fel, om detta fortsätter kontakta it supporten.")
                    return redirect("support:search_users")

                if current_page > 1:
                    limit = default_pagination_values
                    try:
                        offset = current_page * limit
                        o_and_l = offset + limit
                        user_objects = User.objects.filter(
                            groups__name='client')[offset:o_and_l]
                        users = []
                        for a_user in user_objects:
                            the_user = UserInfo.objects.get(user=a_user)
                            users.append({
                                'id': a_user.id,
                                'person': the_user})
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages there are
                        # if there are only the limit or fewer number of pages will be 1

                        u_pages = 1

                        if number_users > limit:
                            # if there are more we divide by the limit
                            u_pages = number_users / limit
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1
                            if type(u_pages) != "int":
                                u_pages = int(u_pages)

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'gdpr_check': gdpr_check,
                            'search_type': search_type,
                            'search_value': search_value,
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

                    limit = default_pagination_values
                    try:
                        user_objects = User.objects.filter(
                            groups__name='client')[:limit]
                        users = []
                        for a_user in user_objects:
                            the_user = UserInfo.objects.get(user=a_user)
                            users.append({
                                'id': a_user.id,
                                'person': the_user})
                        number_users = User.objects.filter(
                            groups__name='client').count()

                        # figure out how many pages there are
                        # if there are only the limit or fewer number of pages will be 1

                        u_pages = 1

                        if number_users > limit:
                            # if there are more we divide by the limit
                            u_pages = number_users / limit
                            # see if there is a decimal
                            testU = int(u_pages)
                            # if there isn't an even number make an extra page for the last group
                            if testU != u_pages:
                                u_pages = int(u_pages)
                                u_pages += 1
                            if type(u_pages) != "int":
                                u_pages = int(u_pages)

                        # create a list for a ul to work through

                        more_users = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(u_pages):
                            i += 1
                            more_users.append({'number': i})

                        # make search for specific order or customer

                        form = searchUserForm()

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'gdpr_check': gdpr_check,
                            'search_type': search_type,
                            'search_value': search_value,
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

            elif 'search' in self.request.POST.keys() and self.request.POST['search'] == "None":
                # resetting form
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
        return redirect("support:orders")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                if order.billing_address != None:
                    billing_address = order.billing_address.street_address
                else:
                    billing_address = "Address borttagen"
                if order.shipping_address != None:
                    shipping_address = order.shipping_address.street_address
                else:
                    shipping_address = "Address borttagen"
                theClient = order.user
                theClientInfo = UserInfo.objects.get(user=order.user)
                path = self.request.get_full_path()

                context = {
                    'gdpr_check': gdpr_check,
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
                if 'CancelOrder' in self.request.POST.keys():
                    # we have granted full money back without reutrn
                    order.refund_granted = True
                    order.removed_order = True
                    order.comment = "Avbeställt hela ordern"
                    # set refund for all orderItems
                    for item in orderItems:
                        item.refund_granted = True
                        item.removed_from_order = True
                        item.save()
                    info_message = "Ordern har avbeställts"
                    messages.info(self.request, info_message)
                if 'CancelCancelOrder' in self.request.POST.keys():
                    if not order.refund_handled:
                        print("In refund handling")
                        # if we havent refunded the money we can return the order as was
                        order.refund_flag = False
                        order.refund_granted = False
                        order.removed_order = False
                        if order.comment == "Avbeställt hela ordern":
                            order.comment = ""
                        # set refund for all orderItems
                        for item in orderItems:
                            if not item.refund_handled:
                                item.refund_granted = False
                                item.removed_from_order = False
                                item.save()
                        info_message = "Ordern tillbaka lagd"
                        messages.info(self.request, info_message)
                    else:
                        warning_message = "Ordern har betalats tillbaka och kan inte bara läggas tillbaka som den är. Kunden måste lägga en ny order."
                        messages.warning(self.request, warning_message)
                order.updated_date = make_aware(datetime.now())
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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                'gdpr_check': gdpr_check,
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
                    self.request, item.title + " " + info_message)
            if 'ItemToReturnUn' in self.request.POST.keys():
                item.returned_flag = False
                info_message = get_message('info', 65)
                messages.info(
                    self.request, item.title + " " + info_message)
            if 'ItemReturned' in self.request.POST.keys():
                item.returned = True
                info_message = get_message('info', 66)
                messages.info(
                    self.request, item.title + " " + info_message)
            if 'ItemUnReturned' in self.request.POST.keys():
                item.returned = False
                info_message = get_message('info', 67)
                messages.info(
                    self.request, item.title + " " + info_message)
            if 'PaybackRequested' in self.request.POST.keys():
                item.refund_flag = True
                info_message = get_message('info', 68)
                messages.info(
                    self.request, info_message + " " + item.title)
            if 'PaybackRequestCancel' in self.request.POST.keys():
                item.refund_flag = False
                info_message = get_message('info', 69)
                messages.info(
                    self.request, info_message + " " + item.title)
            if 'PaybackApproved' in self.request.POST.keys():
                item.refund = True
                info_message = get_message('info', 70)
                messages.info(
                    self.request, info_message + " " + item.title)
            if 'PaybackCancel' in self.request.POST.keys():
                item.refund = False
                info_message = get_message('info', 71)
                messages.info(
                    self.request, info_message + " " + item.title)
            if 'CancelItem' in self.request.POST.keys():
                item.refund = True
                item.removed_from_order = True
                item.save()
                check_num = order.items.filter(
                    removed_from_order=False).count() - 1
                message = "Avbeställt " + item.title
                order.comment = "Avbeställt delar"
                if check_num <= 0:
                    # nothing left in the order, order should be canceled too and refunded, but we cant remove order until refund has been sorted
                    order.refund_granted = True
                    order.removed_order = True
                    order.comment = "Avbeställt order"
                    message = order.comment
                order.save()

                messages.info(
                    self.request, message)
            if 'CancelCancelItem' in self.request.POST.keys():
                item.refund = False
                item.removed_from_order = False
                item.save()
                message = "Åter i beställning: " + item.title
                order.comment = ""
                order.refund_granted = False
                order.removed_order = False
                order.save()

                messages.info(
                    self.request, message)

            info_message = get_message('info', 72)
            messages.info(
                self.request, item.title + " " + info_message)
            item.save()
            # changes made create redirect  with variable
            base_url = order.get_absolute_url_support()
            query_string = urlencode({'order_ref': order.ref_code})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
        else:
            return redirect("support:orders")


class SupportView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get all unanswered errands and a count of them
            # make a search avaiable for specific errand, order or customer

            context = {
                'gdpr_check': gdpr_check,
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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get the specific errand. Show all answers and responces as well as a responce form

            context = {
                'gdpr_check': gdpr_check,
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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get the specific user's profile
            if 'lookAtProfile' in self.request.POST.keys():
                search_id = int(self.request.POST['lookAtProfile'])
                form = UserInformationForm()
                the_user = User.objects.get(id=search_id)

                form.populate(the_user)

                context = {
                    'gdpr_check': gdpr_check,
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
                            'gdpr_check': gdpr_check,
                            'form': form,
                        }

                        message = get_message('error', 55)
                        messages.warning(
                            self.request, message)
                        return render(self.request, "support/edit_user.html", context)
                else:
                    context = {
                        'gdpr_check': gdpr_check,
                        'form': form,
                    }

                    info_message = get_message('info', 24)
                    messages.info(
                        self.request, info_message)
                    return render(self.request, "support/edit_user.html", context)
            else:
                message = get_message('error', 56)
                messages.warning(
                    self.request, message)
                return redirect("support:overview")

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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                'gdpr_check': gdpr_check,
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
                                    'gdpr_check': gdpr_check,
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
                                'gdpr_check': gdpr_check,
                                'a_form': a_form,
                                'c_form': c_form,
                                'person': theUser,
                                'newOrOld': newOrOld,
                            }
                            message = get_message('error', 59)
                            messages.warning(
                                self.request, message)
                            return render(self.request, "support/company.html", context)
                    else:
                        messages.warning(
                            self.request, "Variabel saknades. Detta är ett allvarligt fel kontakta IT supporten")

                        return redirect("support:search_users")
                except ObjectDoesNotExist:
                    messages.warning(
                        self.request, "Användaren finns inte")

                    return redirect("support:search_users")
            else:
                message.warning(
                    self.request, "Användarinformationen saknades. Detta är ett allvarligt fel kontakta IT supporten.")
                return redirect("support:search_users")

        else:
            message.warning(
                self.request, "Företagsinformation hittades inte. Om detta fortsätter hända vargod kontakta IT supporten.")
            return redirect("support:search_users")


class EditAdresses(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 94)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                    'gdpr_check': gdpr_check,
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
                                'gdpr_check': gdpr_check,
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
                        'gdpr_check': gdpr_check,
                        'addresses': addresses,
                        'person': theUser,
                    }

                    return render(self.request, "support/edit_addresses.html", context)
                else:
                    message.warning(
                        self.request, "Användarinformationen saknades. Detta är ett allvarligt fel kontakta IT supporten.")
                    return redirect("support:search_users")
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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                'gdpr_check': gdpr_check,
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
                        'gdpr_check': gdpr_check,
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
                    'gdpr_check': gdpr_check,
                    'addresses': addresses,
                    'person': theUser,
                }

                return render(self.request, "support/edit_addresses.html", context)
            else:
                # rerender form

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'address': address,
                    'address_choices': ADDRESS_CHOICES
                }
                info_message = get_message('info', 28)
                messages.info(self.request, info_message)

                return render(self.request, "support/edit_address.html", context)

        else:
            messages.warning(
                self.request, "Variabel saknades. Kontakta IT supporten")
            return redirect("support:search_users")


class NewAddress(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search as we dont know the user

        message = get_message('error', 67)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if "theClient" in self.request.POST.keys():
            user_id = int(self.request.POST['theClient'])
            theUser = User.objects.get(id=user_id)
            # get form for this using the user id
            form = NewAddressForm()

            context = {
                'gdpr_check': gdpr_check,
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
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'person': theUser,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }
                message = get_message('error', 68)
                messages.warning(
                    self.request, message)

                return render(self.request, "support/edit_address.html", context)
        else:
            messages.warning(
                self.request, "Information saknades. Kontakta IT support om detta upprepas.")
            return redirect("support:search_users")


class SettingsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # return to search

        message = get_message('error', 95)
        messages.warning(
            self.request, message)
        return redirect("support:search_users")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            if 'lookAtSettings' in self.request.POST.keys():
                user = int(self.request.POST['lookAtSettings'])
                theUser = User.objects.get(id=user)
                # get cookie model, fill in with previous info if there is any
                form = CookieSettingsForm()
                form.populate(theUser)

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                }

                return render(self.request, "support/client_settings.html", context)
            else:
                messages.warning(
                    self.request, "Något gick fel när vi hämtade denna vy. Kontakta IT supporten.")
                return redirect("core:home")
        except ObjectDoesNotExist:
            message = get_message('error', 69)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class ProfileView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get supports own user info
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()
                info.company = False

            # place info in context and render page

            context = {
                'gdpr_check': gdpr_check,
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
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get form for this using the user id

            form = UserInformationForm(the_User=self.request.user)

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
            }

            return render(self.request, "support/my_info.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 84)
            messages.warning(
                self.request, message)
            return redirect("support:my_profile")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            form = UserInformationForm(self.request.POST)

            if 'edit' in self.request.POST.keys():

                context = {
                    'gdpr_check': gdpr_check,
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
                    'gdpr_check': gdpr_check,
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

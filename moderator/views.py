from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
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
        path = self.request.get_full_path()
        is_post = False
        try:
            # get the limit we are currently#
            limit = default_pagination_values
            # get the orders and the count of all unsent orders

            try:
                orders = Order.objects.filter(
                    being_delivered=False,
                    removed_order=False, ordered=True)[:limit]
                number_orders = Order.objects.filter(
                    being_delivered=False,
                    removed_order=False, ordered=True).count()
            except ObjectDoesNotExist:
                orders = {}
                number_orders = 0

            # figure out how many pages there are
            # if there are only the limit  or fewer the number of pages will be 1

            o_pages = 1

            if number_orders > limit:
                # if there are more we divide by the limit
                o_pages = number_orders / limit
                # if there isn't an even number make an extra page for the last group
                testO = int(o_pages)
                if testO != o_pages:
                    o_pages = int(o_pages)
                    o_pages += 1
                if type(o_pages) != "int":
                    o_pages = int(o_pages)

            # create a list for a ul to work through

            current_page = 1
            more_orders, where = get_list_of_pages(current_page, o_pages)

            # pagination booleans

            if current_page == 1 or where == "no extras":
                start = False
            else:
                start = True

            if current_page == o_pages or where == "no extras":
                end = False
            else:
                end = True

            if current_page < o_pages:
                next_page = True
            else:
                next_page = False

            if current_page > 1:
                previous_page = True
            else:
                previous_page = False

            context = {
                'gdpr_check': gdpr_check,
                'orders': orders,
                'more_orders': more_orders,
                'current_page': int(current_page),
                'max': o_pages,
                'previous_page': previous_page,
                'next_page': next_page,
                'end': end,
                'start': start,
            }

            return render(self.request, "moderator/mod_overview.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 35)
            messages.warning(
                self.request, message)
            return redirect("core:home")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:

            if 'page' in self.request.POST.keys():
                current_page = int(self.request.POST['page'])
                # get the limit
                limit = default_pagination_values
                # get the first orders and the count of all unsent orders

                try:
                    if current_page > 1:
                        offset = (current_page - 1) * limit
                        o_l = offset + limit
                        orders = Order.objects.filter(
                            being_delivered=False, removed_order=False, ordered=True)[offset:o_l]
                    else:
                        orders = Order.objects.filter(
                            being_delivered=False,
                            removed_order=False, ordered=True)[:limit]
                    number_orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True).count()
                except ObjectDoesNotExist:
                    orders = {}
                    number_orders = 0

                # figure out how many pages there are
                # if there are only the limit or fewer number of pages will be 1

                o_pages = 1

                if number_orders > limit:
                    # if there are more we divide by the limit
                    o_pages = number_orders / limit
                    # see if there is a decimal
                    testO = int(o_pages)
                    if testO != o_pages:
                        o_pages = int(o_pages)
                        o_pages += 1
                    if type(o_pages) != "int":
                        o_pages = int(o_pages)

                # create a list for a ul to work through

                more_orders, where = get_list_of_pages(current_page, o_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == o_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if current_page < o_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                context = {
                    'gdpr_check': gdpr_check,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page': int(current_page),
                    'max': o_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'nextPage' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

                # get the limit
                limit = default_pagination_values
                # get the first unsent orders and the count of all unsent orders

                try:
                    number_orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True).count()
                except ObjectDoesNotExist:
                    number_orders = 0

                # figure out how many pages of there are
                # if there are only the limit or fewer the number of pages will be 1

                o_pages = 1

                if number_orders > limit:
                    # if there are more we divide by the limit
                    o_pages = number_orders / limit
                    # see if there is a decimal
                    testO = int(o_pages)
                    if testO != o_pages:
                        o_pages = int(o_pages)
                        o_pages += 1
                    if type(o_pages) != "int":
                        o_pages = int(o_pages)

                # orders

                if current_page < o_pages:
                    current_page += 1
                else:
                    current_page = o_pages

                if current_page > 1:
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True)[offset:o_l]
                else:
                    orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True)[:limit]

                # create a list for a ul to work through

                more_orders, where = get_list_of_pages(current_page, o_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == o_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if current_page < o_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                context = {
                    'gdpr_check': gdpr_check,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page': int(current_page),
                    'max': o_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'previousPage' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

                # get the limit
                limit = default_pagination_values
                # get the first unsent orders and the count of all unsent orders

                try:
                    number_orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True).count()
                except ObjectDoesNotExist:
                    number_orders = 0

                # figure out how many pages there are
                # if there are only the limit or fewer number of pages will be 1

                o_pages = 1

                if number_orders > limit:
                    # if there are more we divide by the limit
                    o_pages = number_orders / limit
                    # see if there is a decimal
                    testO = int(o_pages)
                    if testO != o_pages:
                        o_pages = int(o_pages)
                        o_pages += 1
                    if type(o_pages) != "int":
                        o_pages = int(o_pages)

                # orders

                if current_page > 1:
                    current_page -= 1
                else:
                    current_page = 1

                if current_page < 2:
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True)[offset:o_l]
                else:
                    orders = Order.objects.filter(
                        being_delivered=False,
                        removed_order=False, ordered=True)[:limit]

                # create a list for a ul to work through

                more_orders, where = get_list_of_pages(current_page, o_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == o_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if current_page < o_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                context = {
                    'gdpr_check': gdpr_check,
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page': int(current_page),
                    'max': o_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            else:
                messages.warning(
                    self.request, "Något gick fel i hämtningen av sidan. Om detta upprepas vargod kontakta IT support")
                return redirect("moderator:overview")
        except ObjectDoesNotExist:
            message = get_message('error', 42)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")


class ProfileView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        try:
            # get moderators own user info
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

            return render(self.request, "moderator/my_profile.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 83)
            messages.warning(
                self.request, message)
            return redirect("moderator:my_overview")


class InfoView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        try:
            # get form for this using the user id

            form = UserInformationForm(the_User=self.request.user)

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
            }

            return render(self.request, "moderator/my_info.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 84)
            messages.warning(
                self.request, message)
            return redirect("moderator:my_profile")

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

                return render(self.request, "moderator/my_info.html", context)

            if form.is_valid():
                try:
                    theUser = self.request.user
                    info = UserInfo.objects.get(user=theUser)
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    theUser.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    theUser.save()
                    info.save()
                    info_message = get_message('info', 38)
                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:my_profile")
                except ObjectDoesNotExist:
                    info = UserInfo()
                    theUser = self.request.user
                    info.user = theUser
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    theUser.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    theUser.save()
                    info.save()
                    info_message = get_message('info', 39)
                    return redirect("moderator:my_profile")
            else:

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                }

                info_message = get_message('info', 40)
                messages.info(
                    self.request, info_message)

                return render(self.request, "moderator/my_info.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 85)
            messages.warning(
                self.request, message)
            return redirect("moderator:my_profile")


class ProductsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        is_post = False
        try:
            # get the limit
            limit = default_pagination_values
            # get the first products and a count of all products
            products = Item.objects.all()[:limit]
            number_products = Item.objects.all().count()
            # figure out how many pages  there are
            # if there are only the limit or fewer number of pages will be 1

            p_pages = 1

            if number_products > limit:
                # if there are more we divide by the limit
                p_pages = number_products / limit
                # see if there is a decimal
                testP = int(p_pages)
                # if there isn't an even number make an extra page for the last group
                if testP != p_pages:
                    p_pages = int(p_pages)
                    p_pages += 1
                if type(p_pages) != "int":
                    p_pages = int(p_pages)

            # create a list for a ul to work through

            current_page = 1
            more_products, where = get_list_of_pages(current_page, p_pages)

            # pagination booleans

            if current_page == 1 or where == "no extras":
                start = False
            else:
                start = True

            if current_page == p_pages or where == "no extras":
                end = False
            else:
                end = True

            if current_page < p_pages:
                next_page = True
            else:
                next_page = False

            if current_page > 1:
                previous_page = True
            else:
                previous_page = False

            # make search for specific order or customer

            form = searchProductForm()

            # set the hidden value for wether or not we have done a search

            search_value = ""

            # onsubmit warning
            onsubmit = get_message('warning', 6)

            context = {
                'gdpr_check': gdpr_check,
                'search_value': search_value,
                'products': products,
                'more_products': more_products,
                'form': form,
                'current_page': current_page,
                'onsubmit': onsubmit,
                'current_page': int(current_page),
                'max': p_pages,
                'previous_page': previous_page,
                'next_page': next_page,
                'end': end,
                'start': start,
            }

            return render(self.request, "moderator/mod_products.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 86)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])
            page = 1
            if 'page' in self.request.POST.keys():
                page = int(self.request.POST['page'])

            # what button did we press

            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "":
                # make a form and populate so we can clean the data
                form = searchProductForm(self.request.POST)

                if form.is_valid():
                    # get the values
                    product_id = form.cleaned_data.get('product_id')
                    # search done on product id
                    search_value = product_id
                    # get the product
                    try:
                        product = Item.objects.filter(id=product_id)
                        p_pages = 1
                        # set current page to 1
                        current_page = 1

                        # create a list for a ul to work through

                        more_products, where = get_list_of_pages(
                            current_page, p_pages)

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == p_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if current_page < p_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # onsubmit warning
                        onsubmit = get_message('warning', 6)

                        context = {
                            'gdpr_check': gdpr_check,
                            'search_value': search_value,
                            'product': product,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'onsubmit': onsubmit,
                            'current_page': int(current_page),
                            'max': p_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        if product_id is not None:
                            info_message = get_message(
                                'info', 42)
                            messages.info(
                                self.request, info_message)
                        return redirect("moderator:products")
                else:

                    if self.request.POST['product_id'] is not None:
                        message = get_message('error', 103)
                        messages.warning(
                            self.request, message)
                    return redirect("moderator:products")

            elif 'page' in self.request.POST.keys():
                # get what type of search
                search_value = self.request.POST['search']
                # get what page
                page = int(self.request.POST['page'])
                # get the limit
                limit = default_pagination_values

                try:
                    number_products = Item.objects.all(
                    ).count()
                except ObjectDoesNotExist:
                    number_products = 0

                # figure out how many pages there are
                # if there are only the limit or fewer number of pages will be 1

                p_pages = 1

                if number_products > limit:
                    # if there are more we divide by the limit
                    p_pages = number_products / limit
                    # see if there is a decimal
                    testP = int(p_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testP != p_pages:
                        p_pages = int(p_pages)
                        p_pages += 1
                    if type(p_pages) != "int":
                        p_pages = int(p_pages)

                # get the products
                if page > 1:
                    offset = (page - 1) * limit
                    o_l = offset + limit
                    products = Item.objects.all()[offset:o_l]
                else:
                    products = Item.objects.all()[:limit]

                # create a list for a ul to work through

                current_page = page
                more_products, where = get_list_of_pages(current_page, p_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == p_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < p_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                # make search for specific order or customer

                form = searchProductForm()

                # onsubmit warning
                onsubmit = get_message('warning', 6)

                context = {
                    'gdpr_check': gdpr_check,
                    'search_value': search_value,
                    'products': products,
                    'more_products': more_products,
                    'form': form,
                    'current_page': current_page,
                    'onsubmit': onsubmit,
                    'current_page': int(current_page),
                    'max': p_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_products.html", context)

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_value = self.request.POST['search']
                # get previous current page
                current_page = int(self.request.POST['current_page'])
                # get the limit
                limit = default_pagination_values

                try:
                    number_products = Item.objects.all(
                    ).count()
                except ObjectDoesNotExist:
                    number_products = 0

                # figure out how many pages there are
                # if there are only the limit or fewer number of pages will be 1

                p_pages = 1

                if number_products > limit:
                    # if there are more we divide by the limit
                    p_pages = number_products / limit
                    # see if there is a decimal
                    testP = int(p_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testP != p_pages:
                        p_pages = int(p_pages)
                        p_pages += 1
                    if type(p_pages) != "int":
                        p_pages = int(p_pages)

                if current_page < p_pages:
                    current_page += 1
                else:
                    current_page = p_pages

                # get the products
                offset = (current_page - 1) * limit
                o_l = offset + limit
                products = Item.objects.all()[offset:o_l]

                # create a list for a ul to work through

                more_products, where = get_list_of_pages(
                    current_page, p_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == p_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < p_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                # make search for specific order or customer

                form = searchProductForm()

                # onsubmit warning
                onsubmit = get_message('warning', 6)

                context = {
                    'gdpr_check': gdpr_check,
                    'search_value': search_value,
                    'products': products,
                    'more_products': more_products,
                    'form': form,
                    'current_page': current_page,
                    'onsubmit': onsubmit,
                    'current_page': int(current_page),
                    'max': p_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_products.html", context)

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_value = self.request.POST['search']
                # get previous current page
                current_page = int(self.request.POST['current_page'])
                # get the limit
                limit = default_pagination_values

                if current_page > 1:
                    current_page -= 1

                try:
                    number_products = Item.objects.all(
                    ).count()

                    # figure out how many pages there are
                    # if there are only the limit or fewer number of pages will be 1

                    p_pages = 1

                    if number_products > limit:
                        # if there are more we divide by the limit
                        p_pages = number_products / limit
                        # see if there is a decimal
                        testP = int(p_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testP != p_pages:
                            p_pages = int(p_pages)
                            p_pages += 1
                        if type(p_pages) != "int":
                            p_pages = int(p_pages)

                    # get the products
                    if current_page > 1:
                        offset = (current_page - 1) * limit
                        o_l = offset + limit
                        products = Item.objects.all()[offset:o_l]
                    else:
                        products = Item.objects.all()[:limit]

                    # create a list for a ul to work through

                    more_products, where = get_list_of_pages(
                        current_page, p_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == 4:
                        start = False

                    if current_page == p_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if where == "end":
                        end = False

                    if current_page < p_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # make search for specific order or customer

                    form = searchProductForm()
                    # onsubmit warning
                    onsubmit = get_message('warning', 6)

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_value': search_value,
                        'products': products,
                        'more_products': more_products,
                        'form': form,
                        'onsubmit': onsubmit,
                        'current_page': int(current_page),
                        'max': p_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_products.html", context)

                except ObjectDoesNotExist:
                    message = get_message('error', 87)
                    messages.warning(
                        self.request, message)
                    return redirect("moderator:products")

            elif 'delete' in self.request.POST.keys():
                if 'id' in self.request.POST.keys():

                    product_id = int(self.request.POST['id'])
                    product = Item.objects.get(id=product_id)
                    product.delete()

                    info_message = get_message('info', 48)
                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:products")
                else:
                    return redirect("moderator:products")
            else:
                return redirect("moderator:overview")

        except ObjectDoesNotExist:
            message = get_message('error', 89)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")


class SpecificProductsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        message = get_message('error', 90)
        messages.warning(
            self.request, message)
        return redirect("moderator:products")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'lookAtProduct' in self.request.POST.keys():
            try:
                product_id = int(self.request.POST['lookAtProduct'])

                # get the form
                form = editOrCreateProduct()
                form.populate(product_id)

                old = product_id

                # we need all possible categories

                category = 0
                categories = Category.objects.all()

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'old': old,
                    'category': category,
                    'categories': categories,
                }

                return render(self.request, "moderator/mod_single_product.html", context)
            except ObjectDoesNotExist:
                message = get_message('error', 91)
                messages.warning(
                    self.request, message)
                return redirect("moderator:products")
        elif 'new' in self.request.POST.keys():

            # get the form
            form = editOrCreateProduct()

            old = 'new'

            # we need all possible categories
            category = 0
            categories = Category.objects.all()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'old': old,
                'category': category,
                'categories': categories,
            }

            return render(self.request, "moderator/mod_single_product.html", context)

        elif 'saveProduct' in self.request.POST.keys():

            form = editOrCreateProduct(self.request.POST, self.request.FILES)

            if form.is_valid():
                product_id = self.request.POST['old']
                info_message = get_message('info', 43)
                if product_id == "new":
                    product = Item()
                    product.title = form.cleaned_data.get('title')
                    product.price = form.cleaned_data.get('price')
                    product.discount_price = form.cleaned_data.get(
                        'discount_price')
                    product.description = form.cleaned_data.get('description')
                    if len(self.request.FILES) > 0:
                        product.image = form.cleaned_data['image']

                    if 'category' in self.request.POST.keys():
                        category_id = int(self.request.POST['category'])
                        category = Category.objects.get(id=category_id)
                        product.category = category
                    product.slug = "temp"
                    # save

                    product.save()

                    product.slug = "item" + str(product.id)

                    product.save()

                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:products")
                else:
                    product_id = int(product_id)
                    product = Item.objects.get(id=product_id)
                    product.title = form.cleaned_data.get('title')
                    product.price = form.cleaned_data.get('price')
                    product.discount_price = form.cleaned_data.get(
                        'discount_price')
                    product.description = form.cleaned_data.get('description')
                    if len(self.request.FILES) > 0:
                        img_file = self.request.FILES['image'].read()
                        img_name = str(self.request.FILES['image'])
                        file_data = {'img': SimpleUploadedFile(
                            img_name, img_file)}
                        product.image = form.cleaned_data['image']
                    if 'category' in self.request.POST.keys():
                        category_id = int(self.request.POST['category'])
                        category = Category.objects.get(id=category_id)
                        product.category = category

                    # save

                    product.save()

                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:products")

            else:
                # rerender page with form filled in

                old = int(self.request.POST['old'])

                # we also need the image and category to rerender the form properly

                category = self.request.POST['category']

                # we need all possible categories

                categories = Category.objects.all()

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'old': old,
                    'category': category,
                    'categories': categories,
                }

                return render(self.request, "moderator/mod_single_product.html", context)
        else:
            messages.warning(
                self.request, "Produkt hittades inte. Om detta återupprepas kontakta IT support.")
            return redirect("moderator:products")


class CategoriesView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        try:
            # get the limit
            limit = default_pagination_values
            # get the first categories and a count of all products
            categories = Category.objects.all()[:limit]
            number_categories = Category.objects.all().count()
            # figure out how many pages there are
            # if there are only the limit or fewer number of pages will be 1

            c_pages = 1

            if number_categories > limit:
                # if there are more we divide by the limit
                c_pages = number_categories / limit
                # see if there is a decimal
                testC = int(c_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if testC != c_pages:
                    c_pages = int(c_pages)
                    c_pages += 1
                if type(c_pages) != "int":
                    c_pages = int(c_pages)

            # create a list for a ul to work through

            current_page = 1
            more_categories, where = get_list_of_pages(current_page, c_pages)

            # pagination booleans

            if current_page == 1 or where == "no extras":
                start = False
            else:
                start = True

            if current_page == 4:
                start = False

            if current_page == c_pages or where == "no extras":
                end = False
            else:
                end = True

            if where == "end":
                end = False

            if current_page < c_pages:
                next_page = True
            else:
                next_page = False

            if current_page > 1:
                previous_page = True
            else:
                previous_page = False

            # make search for specific category

            form = searchCategoryForm()

            # set a bool to check if we are showing one or multiple categories

            multiple = True

            # set the hidden value for wether or not we have done a search

            search_value = "None"

            # delete warning
            onsubmit = get_message('warning', 4)

            context = {
                'gdpr_check': gdpr_check,
                'search_value': search_value,
                'multiple': multiple,
                'categories': categories,
                'more_categories': more_categories,
                'form': form,
                'onsubmit': onsubmit,
                'current_page': int(current_page),
                'max': c_pages,
                'previous_page': previous_page,
                'next_page': next_page,
                'end': end,
                'start': start,
            }

            return render(self.request, "moderator/mod_categories.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 96)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        # get the limit
        limit = default_pagination_values
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press
            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "" and self.request.POST['search'] != "None":
                # check if we are using the form
                search_test = self.request.POST['search']
                if search_test == "newSearch":
                    # make a form and populate so we can clean the data
                    if self.request.POST['category_id'] == "":
                        # resetting form
                        return redirect("moderator:categories")

                    form = searchCategoryForm(self.request.POST)

                    if form.is_valid():
                        # get the values
                        category_id = form.cleaned_data.get('category_id')
                        # search done on product id
                        search_value = category_id
                        # get the product
                        try:
                            category = Category.objects.get(id=category_id)
                            c_pages = 1

                            # create a list for a ul to work through

                            current_page = 1
                            more_categories, where = get_list_of_pages(
                                current_page, c_pages)

                            # pagination booleans

                            if current_page == 1 or where == "no extras":
                                start = False
                            else:
                                start = True

                            if current_page == 4:
                                start = False

                            if current_page == c_pages or where == "no extras":
                                end = False
                            else:
                                end = True

                            if where == "end":
                                end = False

                            if current_page < c_pages:
                                next_page = True
                            else:
                                next_page = False

                            if current_page > 1:
                                previous_page = True
                            else:
                                previous_page = False

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            onsubmit = get_message('warning', 4)

                            context = {
                                'gdpr_check': gdpr_check,
                                'search_value': search_value,
                                'multiple': multiple,
                                'category': category,
                                'more_categories': more_categories,
                                'form': form,
                                'onsubmit': onsubmit,
                                'current_page': int(current_page),
                                'max': c_pages,
                                'previous_page': previous_page,
                                'next_page': next_page,
                                'end': end,
                                'start': start,
                            }

                            return render(self.request, "moderator/mod_categories.html", context)

                        except ObjectDoesNotExist:
                            # couldn't find the category check if the id is empty
                            if category is None:
                                # most likely trying to reset the form
                                return redirect("moderator:categories")
                            else:
                                info_message = get_message(
                                    'info', 45)
                                messages.info(self.request, info_message)
                                return redirect("moderator:categories")
                    else:
                        if self.request.POST['category_id'] != "":
                            message = get_message('error', 97)
                            messages.warning(
                                self.request, message)
                        return redirect("moderator:categories")
                else:
                    # we shouldnt be here but just in case of later changes do a search on the value
                    # get the values
                    category_id = int(search_test)
                    # search done on product id
                    search_value = category_id
                    # get the product
                    category = Category.objects.get(id=category_id)
                    c_pages = 1

                    # create a list for a ul to work through

                    current_page = 1
                    more_categories, where = get_list_of_pages(
                        current_page, c_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == 4:
                        start = False

                    if current_page == c_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if where == "end":
                        end = False

                    if current_page < c_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # set a bool to check if we are showing one or multiple orders

                    multiple = False

                    onsubmit = get_message('warning', 4)

                    context = {
                        'gdpr_check': gdpr_check,
                        'search_value': search_value,
                        'multiple': multiple,
                        'category': category,
                        'more_categories': more_categories,
                        'form': form,
                        'onsubmit': onsubmit,
                        'current_page': int(current_page),
                        'max': c_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_categories.html", context)

            elif 'nextPage' in self.request.POST.keys():
                # get current page
                current_page = int(self.request.POST['current_page'])

                number_categories = Category.objects.all(
                ).count()

                # figure out how many pages there are
                # if there are only the limit or fewer number of pages will be 1

                c_pages = 1

                if number_categories > limit:
                    # if there are more we divide by the limit
                    c_pages = number_categories / limit
                    # see if there is a decimal
                    testC = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testC != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1
                    if type(c_pages) != "int":
                        c_pages = int(c_pages)

                # correct current page in accordance with c_pages

                if current_page < c_pages:
                    current_page += 1
                elif current_page >= c_pages:
                    current_page = c_pages

                # create a list for a ul to work through

                more_categories, where = get_list_of_pages(
                    current_page, c_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == 4:
                    start = False

                if current_page == c_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < c_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                if current_page > 1:
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    categories = Category.objects.all()[offset:o_l]
                else:
                    categories = Category.objects.all()[:limit]

                # make search for specific order or customer

                form = searchCategoryForm()

                # set a bool to check if we are showing one or multiple orders

                multiple = True

                # set the hidden value for wether or not we have done a search

                search_value = "None"

                onsubmit = get_message('warning', 4)

                context = {
                    'gdpr_check': gdpr_check,
                    'search_value': search_value,
                    'multiple': multiple,
                    'categories': categories,
                    'more_categories': more_categories,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': c_pages,
                    'onsubmit': onsubmit,
                    'current_page': int(current_page),
                    'max': c_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_categories.html", context)

            elif 'previousPage' in self.request.POST.keys():
                # get current page
                current_page = int(self.request.POST['current_page'])

                # figure out how many pages there are

                number_categories = Category.objects.all(
                ).count()

                # if there are only the limit or fewer number of pages will be 1

                c_pages = 1

                if number_categories > limit:
                    # if there are more we divide by the limit
                    c_pages = number_categories / limit
                    # see if there is a decimal
                    testC = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testC != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1
                    if type(c_pages) != "int":
                        c_pages = int(c_pages)

                # correct current page in accordance with c_pages

                if current_page > 1:
                    current_page -= 1
                elif current_page <= 1:
                    current_page = 1

                # create a list for a ul to work through

                more_categories, where = get_list_of_pages(
                    current_page, c_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == 4:
                    start = False

                if current_page == c_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < c_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                if current_page > 1:
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    categories = Category.objects.all()[offset:o_l]
                else:
                    categories = Category.objects.all()[:limit]

                # make search for specific order or customer

                form = searchCategoryForm()

                # set a bool to check if we are showing one or multiple orders

                multiple = True

                # set the hidden value for wether or not we have done a search

                search_value = "None"
                onsubmit = get_message('warning', 4)

                context = {
                    'gdpr_check': gdpr_check,
                    'search_value': search_value,
                    'multiple': multiple,
                    'categories': categories,
                    'more_categories': more_categories,
                    'form': form,
                    'onsubmit': onsubmit,
                    'current_page': int(current_page),
                    'max': c_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_categories.html", context)

            elif 'delete' in self.request.POST.keys():
                if 'id' in self.request.POST.keys():

                    category_id = int(self.request.POST['id'])
                    category = Category.objects.get(id=category_id)
                    category.delete()
                    info_message = get_message('info', 47)
                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:categories")

                    # might want to change this to rerender the page where we left off
                else:
                    return redirect("moderator:categories")
            elif 'page' in self.request.POST.keys():
                # get the page
                page = int(self.request.POST['page'])

                number_categories = Category.objects.all(
                ).count()

                # if there are only the limit or fewer number of pages will be 1

                c_pages = 1

                if number_categories > limit:
                    # if there are more we divide by the limit
                    c_pages = number_categories / limit
                    # see if there is a decimal
                    testC = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testC != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1
                    if type(c_pages) != "int":
                        c_pages = int(c_pages)

                # correct current page in accordance with c_pages

                current_page = page

                # create a list for a ul to work through

                more_categories, where = get_list_of_pages(
                    current_page, c_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == 4:
                    start = False

                if current_page == c_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < c_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                if current_page > 1:
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    categories = Category.objects.all()[offset:o_l]
                else:
                    categories = Category.objects.all()[:limit]

                # make search for specific order or customer

                form = searchCategoryForm()

                # set a bool to check if we are showing one or multiple orders

                multiple = True

                # set the hidden value for wether or not we have done a search

                search_value = "None"
                onsubmit = get_message('warning', 4)

                context = {
                    'gdpr_check': gdpr_check,
                    'search_value': search_value,
                    'multiple': multiple,
                    'categories': categories,
                    'more_categories': more_categories,
                    'form': form,
                    'onsubmit': onsubmit,
                    'current_page': int(current_page),
                    'max': c_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_categories.html", context)

            else:
                return redirect("moderator:categories")

        except ObjectDoesNotExist:
            message = get_message('error', 100)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")


class SpecificCategoryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        message = get_message('error', 104)
        messages.warning(
            self.request, message)
        return redirect("moderator:categories")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'lookAtCategory' in self.request.POST.keys():
            category_id = int(self.request.POST['lookAtCategory'])

            # get the form

            form = editOrCreateCategory()
            form.populate(category_id)

            old = category_id

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'old': old,
            }

            return render(self.request, "moderator/mod_single_category.html", context)

        elif 'new' in self.request.POST.keys():

            form = editOrCreateCategory()

            old = 'new'

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'old': old,
            }

            return render(self.request, "moderator/mod_single_category.html", context)
        elif 'saveCategory' in self.request.POST.keys():
            form = editOrCreateCategory(self.request.POST)

            if form.is_valid():
                category_id = self.request.POST['old']
                info_message = get_message('info', 46)
                if category_id == "new":
                    category = Category()

                    category.title = form.cleaned_data.get('title')
                    category.description = form.cleaned_data.get('description')
                    category.discount_price = form.cleaned_data.get(
                        'discount_price')
                    category.slug = "temp"
                    category.save()
                    category.slug = "c" + str(category.id)
                    category.save()
                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:categories")

                else:
                    category_id = int(category_id)
                    category = Category.objects.get(id=category_id)
                    category.title = form.cleaned_data.get('title')
                    category.description = form.cleaned_data.get('description')
                    category.discount_price = form.cleaned_data.get(
                        'discount_price')
                    category.save()
                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:categories")

            else:
                category_id = int(self.request.POST['old'])
                old = category_id

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'old': old,
                }
                message = get_message('error', 101)
                messages.warning(self.request, message)
                return render(self.request, "moderator/mod_single_category.html", context)
        else:
            # post with not correct varaibles
            message = get_message('error', 102)
            messages.warning(
                self.request, message)
            return redirect("moderator:categories")


class OrderHandlingView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        # get the limit
        limit = default_pagination_values
        # display all unsent orders, oldest first
        # first get the constants
        # get max pages regular orders
        o_pages = 1
        orders = Order.objects.filter(
            ordered=True, being_delivered=False, removed_order=False).order_by('id')[:limit]

        number_orders = Order.objects.filter(
            ordered=True, being_delivered=False, removed_order=False).count()

        if number_orders > limit:
            # if there are more we divide by the limit
            o_pages = number_orders / limit
            # see if there is a decimal
            testO = int(o_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testO != o_pages:
                o_pages = int(o_pages)
                o_pages += 1
            if type(o_pages) != "int":
                o_pages = int(o_pages)

        # create a list for a ul to work through

        current_page = 1
        more_orders, where = get_list_of_pages(current_page, o_pages)

        # pagination booleans

        if current_page == 1 or where == "no extras":
            start = False
        else:
            start = True

        if current_page == 4:
            start = False

        if current_page == o_pages or where == "no extras":
            end = False
        else:
            end = True

        if where == "end":
            end = False

        if current_page < o_pages:
            next_page = True
        else:
            next_page = False

        if current_page > 1:
            previous_page = True
        else:
            previous_page = False

        # make search form for specific order or customer

        form = searchOrderForm()

        # set the hidden value for wether or not we have done a search

        search_value = "0"

        context = {
            'gdpr_check': gdpr_check,
            'form': form,
            'search_value': search_value,
            'orders': orders,
            'more_orders': more_orders,
            'current_page': int(current_page),
            'max': o_pages,
            'previous_page': previous_page,
            'next_page': next_page,
            'end': end,
            'start': start,
        }

        return render(self.request, "moderator/mod_orderhandling.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        # get the limit
        limit = default_pagination_values
        # set the search type and value here before we go into the rest
        search_value = "0"
        if 'search' in self.request.POST.keys():
            search_value = int(self.request.POST['search'])
        # handle status change and pagination
        current_page = int(self.request.POST['current_page'])

        # get max pages
        o_pages = 1
        number_orders = Order.objects.filter(
            ordered=True, being_delivered=False, removed_order=False).count()

        if number_orders > limit:
            # if there are more we divide by the limit
            o_pages = number_orders / limit
            # see if there is a decimal
            testO = int(o_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testO != o_pages:
                o_pages = int(o_pages)
                o_pages += 1
            if type(o_pages) != "int":
                o_pages = int(o_pages)

        if 'search' in self.request.POST.keys() and self.request.POST['search'] == "newSearch":
            if ('order_ref' in self.request.POST.keys() and self.request.POST['order_ref'] != "") or ('order_id' in self.request.POST.keys() and self.request.POST['order_id'] != ""):
                # order id and order ref only retrievs a single item

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
                        # display all unsent orders, oldest first
                        # first get the constants
                        # get max pages regular orders
                        o_pages = 1
                        orders = Order.objects.filter(
                            ref_code=search_value)
                        if len(orders) == 0:
                            messages.info(
                                self.request, "Ordern med det referensnummret saknas.")
                            return redirect("moderator:orderhandling")
                        # we only have one page so change the bools etc
                        o_pages = 1
                        current_page = 1
                        start = False
                        end = False
                        next_page = False
                        previous_page = False
                        more_orders = []

                        # set the search type

                        search_type = "Reference"

                        context = {
                            'gdpr_check': gdpr_check,
                            'form': form,
                            'search_value': search_value,
                            'orders': orders,
                            'more_orders': more_orders,
                            'current_page': int(current_page),
                            'max': o_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_orderhandling.html", context)

                    elif order_id != None:
                        # search done on order reference
                        search_value = order_id
                        # display all unsent orders, oldest first
                        # first get the constants
                        # get max pages regular orders
                        o_pages = 1
                        orders = Order.objects.filter(
                            id=search_value)
                        if len(orders) == 0:
                            messages.info(
                                self.request, "Ordern med det id:t saknas.")
                            return redirect("moderator:orderhandling")
                        # we only have one page so change the bools etc
                        o_pages = 1
                        current_page = 1
                        start = False
                        end = False
                        next_page = False
                        previous_page = False
                        more_orders = []

                        # set the search type

                        search_type = "ID"

                        context = {
                            'gdpr_check': gdpr_check,
                            'form': form,
                            'search_value': search_value,
                            'orders': orders,
                            'more_orders': more_orders,
                            'current_page': int(current_page),
                            'max': o_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_orderhandling.html", context)
                    else:
                        messages.warning(
                            self.request, "Vargod fyll i sökformuläret korrekt. ID är endast siffror och referens nummer är alltid 20 tecken långt.")
                        return redirect("moderator:orderhandling")
                else:
                    messages.warning(
                        self.request, "Vargod fyll i sökformuläret korrekt. ID är endast siffror och referens nummer är alltid 20 tecken långt.")
                    redirect("moderator:orderhandling")
            else:
                # reset page
                return redirect("moderator:orderhandling")
        elif 'previousPage' in self.request.POST.keys():
            if current_page >= 2:
                current_page -= 1
            elif current_page <= 1:
                current_page = 1
        elif 'nextPage' in self.request.POST.keys():
            if current_page < o_pages:
                current_page += 1
            elif current_page >= o_pages:
                current_page = o_pages
        elif 'page' in self.request.POST.keys():
            page = int(self.request.POST['page'])
            current_page = page
        else:
            # bugg handle this
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            redirect("moderator:orderhandling")

        # create a list for a ul to work through

        more_orders, where = get_list_of_pages(
            current_page, o_pages)

        # pagination booleans

        if current_page == 1 or where == "no extras":
            start = False
        else:
            start = True

        if current_page == 4:
            start = False

        if current_page == o_pages or where == "no extras":
            end = False
        else:
            end = True

        if where == "end":
            end = False

        if current_page < o_pages:
            next_page = True
        else:
            next_page = False

        if current_page > 1:
            previous_page = True
        else:
            previous_page = False

        # after all these we need display the page again but with the current pages set correctly this will differ if we or have paged.
        if current_page > 1:
            offset = (current_page - 1) * limit
            o_l = offset + limit
            orders = Order.objects.filter(
                ordered=True, being_delivered=False, removed_order=False).order_by('id')[offset:o_l]
        else:
            orders = Order.objects.filter(
                ordered=True, being_delivered=False, removed_order=False).order_by('id')[:limit]

        # make search form for specific order or customer

        form = searchOrderForm()

        context = {
            'gdpr_check': gdpr_check,
            'form': form,
            'search_value': search_value,
            'orders': orders,
            'more_orders': more_orders,
            'current_page': int(current_page),
            'max': o_pages,
            'previous_page': previous_page,
            'next_page': next_page,
            'end': end,
            'start': start,
        }

        return render(self.request, "moderator/mod_orderhandling.html", context)


class SpecificOrderHandlingView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 105)
        messages.warning(
            self.request, message)
        return redirect("moderator:orderhandling")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'lookAtOrder' in self.request.POST.keys():
            order_id = int(self.request.POST['lookAtOrder'])
            not_same_person = False
            try:
                order = Order.objects.get(id=order_id)
                if order.being_read:
                    if order.who and order.who != self.request.user:
                        not_same_person = True
                else:
                    order.being_read = True
                    order.who = self.request.user
                order.updated_date = make_aware(datetime.now())
                order.save()
                orderItems = order.items.all()
                path = self.request.get_full_path()
            except ObjectDoesNotExist:
                message = get_message('error', 106)
                messages.warning(
                    self.request, message)
                return redirect("moderator:orderhandling")

            if order.comment == "Nothing":
                comment = "Inga varor packade"
            elif order.comment == "Partial":
                comment = "Vissa varor packade"
            else:
                comment = ""

            context = {
                'not_same_person': not_same_person,
                'gdpr_check': gdpr_check,
                'path': path,
                'order': order,
                'orderItems': orderItems,
                'comment': comment,
            }

            return render(self.request, "moderator/specificOrder.html", context)
        if 'send' in self.request.POST.keys():
            order_id = int(self.request.POST['send'])
            path = self.request.get_full_path()
            try:
                order = Order.objects.get(id=order_id)
                order.being_delivered = True
                if order.who == self.request.user:
                    order.being_read = False
                    not_same_person = False
                else:
                    # halt this isnt supposed to happen
                    message = "Endast den som först flaggade ordern för packning kan skicka ordern."
                    messages.warning(
                        self.request, message)
                    return redirect("moderator:orderhandling")

                order.updated_date = make_aware(datetime.now())
                orderItems = order.items.all()

                not_filled = False
                some_sent = False

                for item in orderItems:
                    if str(item.id) in self.request.POST.keys():
                        item.sent = True
                        some_sent = True
                        item.save()
                    else:
                        item.sent = False
                        item.save()
                        not_filled = True

                if not_filled:
                    if some_sent:
                        # we are sending part of the order not the entire thing
                        order.being_delivered = False
                        order.comment = 'Partial'
                    else:
                        # we havent packed anything, abort
                        order.comment = 'Nothing'
                        order.being_delivered = False

                if order.being_delivered:
                    order.save()
                    info_message = get_message('info', 51)
                    messages.info(
                        self.request, info_message)

                    return redirect("moderator:orderhandling")
                else:
                    if order.comment == "Nothing":
                        message = get_message('error', 108)
                        messages.warning(
                            self.request, message)
                    elif order.comment == "Partial":
                        message = "Order ej markerad som skickad, hela ordern är inte packad."
                        messages.warning(
                            self.request, message)

                    if order.comment == "Nothing":
                        comment = "Inga varor packade"
                        order.comment = ""
                        order.save()
                    elif order.comment == "Partial":
                        comment = "Vissa varor packade"
                        order.save()
                    else:
                        comment = ""
                        order.save()
                    context = {
                        'not_same_person': not_same_person,
                        'gdpr_check': gdpr_check,
                        'path': path,
                        'order': order,
                        'orderItems': orderItems,
                        'comment': comment,
                    }

                    return render(self.request, "moderator/specificOrder.html", context)
            except ObjectDoesNotExist:
                message = get_message('error', 106)
                messages.warning(
                    self.request, message)

                return redirect("moderator:orderhandling")
        elif 'back' in self.request.POST.keys():
            order = Order.objects.get(id=int(self.request.POST['back']))
            if order.being_read and not order.who:
                order.being_read = False
                order.save()
            if order.who == self.request.user:
                order.being_read = False
                order.save()
            return redirect("moderator:orderhandling")
        else:
            # something wrong redirect
            message = get_message('error', 107)
            messages.warning(
                self.request, message)
            return redirect("moderator:orderhandling")


class FreightView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        is_post = False
        # get the default_pagination_values of the current freights
        limit = default_pagination_values
        freights = Freight.objects.all().order_by('title')[:limit]
        number_of_freights = Freight.objects.all().count()
        try:
            number_of_old_freights = OldFreight.objects.all().count()
            if freights.count() < limit:
                left = limit - freights.count()
                oldfreights = OldFreight.objects.all().order_by('title')[:left]
            else:
                oldfreights = []
            number_of_freights = number_of_freights + number_of_old_freights
        except ObjectDoesNotExist:
            # there are no old freights
            oldfreights = []

        f_pages = 1

        if number_of_freights > limit:
            # if there are more we divide by the offset
            f_pages = number_of_freights / limit
            # see if there is a decimal
            testO = int(f_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testO != f_pages:
                f_pages = int(f_pages)
                f_pages += 1
            if type(f_pages) != "int":
                f_pages = int(f_pages)

        # create a list for a ul to work through

        current_page = 1
        more_freights, where = get_list_of_pages(current_page, f_pages)

        # pagination booleans

        if current_page == 1 or where == "no extras":
            start = False
        else:
            start = True

        if current_page == 4:
            start = False

        if current_page == f_pages or where == "no extras":
            end = False
        else:
            end = True

        if where == "end":
            end = False

        if current_page < f_pages:
            next_page = True
        else:
            next_page = False

        if current_page > 1:
            previous_page = True
        else:
            previous_page = False

        # search form
        form = searchFreightForm()
        form.startup()

        #  search type and search_value to start values
        search_type = "Not set"
        search_value = "Not set"

        onSubmit = get_message('warning', 5)

        # make an empty freight for new freight option
        emptyfreight = Freight()

        context = {
            'gdpr_check': gdpr_check,
            'warning': False,
            'freights': freights,
            'oldfreights': oldfreights,
            'form': form,
            'search_type': search_type,
            'search_value': search_value,
            'more_freights': more_freights,
            'onSubmit': onSubmit,
            'freight': emptyfreight,
            'current_page': int(current_page),
            'max': f_pages,
            'previous_page': previous_page,
            'next_page': next_page,
            'end': end,
            'start': start,
        }

        return render(self.request, "moderator/mod_freights.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        limit = default_pagination_values

        search_type = self.request.POST['search']
        if search_type != "current" and search_type != "old" and search_type != "freight_id_current" and search_type != "freight_id_old" and search_type != "Not set":
            messages.warning(
                self.request, "Något har gått fel, vargod kontakta IT supporten.")
            return redirect("moderator:freights")

        number_of_freights = Freight.objects.all().count()
        number_of_old_freights = OldFreight.objects.all().count()
        number_of_freights_total = number_of_freights + number_of_old_freights

        if number_of_freights_total > limit:
            # if there are more we divide by the limit
            tf_pages = number_of_freights_total / limit
            # see if there is a decimal
            testO = int(tf_pages)
            # if there isn't an even number make an extra page for the last group
            if testO != tf_pages:
                tf_pages = int(tf_pages)
                tf_pages += 1
            if type(tf_pages) != "int":
                tf_pages = int(tf_pages)

        if number_of_freights > limit:
            # if there are more we divide by the limit
            f_pages = number_of_freights / limit
            # see if there is a decimal
            testO = int(f_pages)
            # if there isn't an even number make an extra page for the last group
            if testO != f_pages:
                f_pages = int(f_pages)
                f_pages += 1
            if type(f_pages) != "int":
                f_pages = int(f_pages)

        if number_of_old_freights > limit:
            # if there are more we divide by the limit
            of_pages = number_of_old_freights / limit
            # see if there is a decimal
            testO = int(of_pages)
            # if there isn't an even number make an extra page for the last group
            if testO != of_pages:
                of_pages = int(of_pages)
                of_pages += 1
            if type(of_pages) != "int":
                of_pages = int(of_pages)

        if 'delete' in self.request.POST.keys():
            # delete freight
            # get id
            freight_id = int(self.request.POST['delete'])
            freight = Freight.objects.get(id=freight_id)
            saveInOld = OldFreight()
            saveInOld.title = freight.title
            saveInOld.slug = freight.slug
            saveInOld.description = freight.description
            saveInOld.amount = freight.amount
            saveInOld.save()
            freight.delete()
            info_message = get_message('info', 76)
            messages.info(self.request, info_message)
            return redirect("moderator:freights")
        elif 'paging' in self.request.POST.keys():
            search_value = self.request.POST['search_value']
            current_page = int(self.request.POST['current_page'])
            if 'previousPage' in self.request.POST.keys():
                if current_page < 1:
                    current_page = 1
                else:
                    if current_page > 1:
                        current_page -= 1

                if search_type == 1:
                    if search_value != "Not set":
                        # we are paginating a search if we are here we shouldnt have any page above 1 it also shouldnt be possible to be here so reload
                        messages.warning(
                            self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                        return redirect("moderator:freights")
                    else:
                        if current_page > 1:
                            # we are just looking for current freights we dont need aditionals
                            # get the right offset freights
                            # query[offset:offset + limit]
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            freights = Freight.objects.all().order_by('title')[
                                offset:o_and_l]
                            oldfreights = []

                            # create a list for a ul to work through

                            more_freights, where = get_list_of_pages(
                                current_page, f_pages)

                        else:
                            # we are just looking for current freights we dont need aditionals
                            # check if we have any current ones
                            if f_pages > 0:
                                freights = Freight.objects.all().order_by('title')[
                                    :limit]
                                oldfreights = []
                                # create a list for a ul to work through

                                more_freights, where = get_list_of_pages(
                                    current_page, f_pages)
                            else:
                                freights = []
                                oldfreigths = []
                                more_freights = []
                                where = "no extras"
                                f_pages = 1

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

                elif search_type == 2:
                    if search_value != "Not set":
                        # we are paginating a search if we are here we shouldnt have any page above 1 it also shouldnt be possible to be here so reload
                        messages.warning(
                            self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                        return redirect("moderator:freights")
                    else:
                        if current_page > 1:
                            # we are just looking for old freights we dont need aditionals
                            # get the right offset freights
                            # query[offset:offset + limit]
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            oldfreights = OldFreight.objects.all().order_by('title')[
                                offset:o_and_l]
                            freights = []

                            # create a list for a ul to work through

                            more_freights, where = get_list_of_pages(
                                current_page, of_pages)

                        else:
                            # we are just looking for current freights we dont need aditionals
                            # check if we have any current ones
                            if f_pages > 0:
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :limit]
                                freights = []
                                # create a list for a ul to work through

                                more_freights, where = get_list_of_pages(
                                    current_page, of_pages)
                            else:
                                freights = []
                                oldfreigths = []
                                more_freights = []
                                where = "no extras"
                                f_pages = 1

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

                else:

                    if current_page > 1:
                        # get the right offset freights
                        # query[offset:offset + limit]
                        if current_page <= f_pages:
                            # we are still showing currently active freigts and possibly some old ones, bet the current ones first
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            freights = Freight.objects.all().order_by('title')[
                                offset:o_and_l]
                            if freights.count() < limit:
                                # a check to see if we need to fill in with old ones
                                left = limit - freights.count()
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :left]
                            else:
                                oldfreights = []
                        else:
                            freights = []
                            # we have surpassed the current freights and only need the old ones
                            page = current_page - f_pages
                            if page == 1:
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :limit]
                            else:
                                offset = (page - 1) * limit
                                o_and_l = offset + limit
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    offset:o_and_l]

                        # create a list for a ul to work through

                        more_freights, where = get_list_of_pages(
                            current_page, tf_pages)

                    else:
                        # check if we have any current ones
                        if f_pages > 0:
                            freights = Freight.objects.all().order_by('title')[
                                :limit]
                            if freights.count() < limit:
                                left = limit - freights.count()
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :left]
                            else:
                                oldfreights = []
                        else:
                            freights = []
                            oldfreigths = OldFreight.objects.all().order_by('title')[
                                :limit]  # create a list for a ul to work through

                        more_freights, where = get_list_of_pages(
                            current_page, tf_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == 4:
                        start = False

                    if current_page == f_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if where == "end":
                        end = False

                    if current_page < f_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # make an empty freight for the new form
                    freight = Freight()
                    # search form
                    form = searchFreightForm()
                    form.startup()
                    onSubmit = get_message('warning', 5)

                    context = {
                        'gdpr_check': gdpr_check,
                        'warning': False,
                        'freights': freights,
                        'oldfreights': oldfreights,
                        'freight': freight,
                        'form': form,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_freights': more_freights,
                        'onSubmit': onSubmit,
                        'current_page': int(current_page),
                        'max': f_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_freights.html", context)

            elif 'page' in self.request.POST.keys():
                current_page = int(self.request.POST['page'])

                if search_type == 1:
                    if search_value != "Not set":
                        # we are paginating a specific search if we are here we shouldnt have any pageing it shouldnt be possible to be here so reload
                        messages.warning(
                            self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                        return redirect("moderator:freights")
                    else:
                        if current_page > 1:
                            # we are just looking for current freights we dont need aditionals
                            # get the right offset freights
                            # query[offset:offset + limit]
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            freights = Freight.objects.all().order_by('title')[
                                offset:o_and_l]
                            oldfreights = []

                            # create a list for a ul to work through

                            more_freights, where = get_list_of_pages(
                                current_page, f_pages)

                        else:
                            # we are just looking for current freights we dont need aditionals
                            # check if we have any current ones
                            if f_pages > 0:
                                freights = Freight.objects.all().order_by('title')[
                                    :limit]
                                oldfreights = []
                                # create a list for a ul to work through

                                more_freights, where = get_list_of_pages(
                                    current_page, f_pages)
                            else:
                                freights = []
                                oldfreigths = []
                                more_freights = []
                                where = "no extras"
                                f_pages = 1

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

                elif search_type == 2:
                    if search_value != "Not set":
                        # we are paginating a search if we are here we shouldnt have any page above 1 it also shouldnt be possible to be here so reload
                        messages.warning(
                            self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                        return redirect("moderator:freights")
                    else:
                        if current_page > 1:
                            # we are just looking for old freights we dont need aditionals
                            # get the right offset freights
                            # query[offset:offset + limit]
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            oldfreights = OldFreight.objects.all().order_by('title')[
                                offset:o_and_l]
                            freights = []

                            # create a list for a ul to work through

                            more_freights, where = get_list_of_pages(
                                current_page, of_pages)

                        else:
                            # we are just looking for current freights we dont need aditionals
                            # check if we have any current ones
                            if f_pages > 0:
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :limit]
                                freights = []
                                # create a list for a ul to work through

                                more_freights, where = get_list_of_pages(
                                    current_page, of_pages)
                            else:
                                freights = []
                                oldfreigths = []
                                more_freights = []
                                where = "no extras"
                                f_pages = 1

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

                else:
                    if current_page > 1:
                        # get the right offset freights
                        # query[offset:offset + limit]
                        if current_page <= f_pages:
                            # we are still showing currently active freigts and possibly some old ones, bet the current ones first
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            freights = Freight.objects.all().order_by('title')[
                                offset:o_and_l]
                            if freights.count() < limit:
                                # a check to see if we need to fill in with old ones
                                left = limit - freights.count()
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :left]
                            else:
                                oldfreights = []
                        else:
                            freights = []
                            # we have surpassed the current freights and only need the old ones
                            page = current_page - f_pages
                            if page == 1:
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :limit]
                            else:
                                offset = (page - 1) * limit
                                o_and_l = offset + limit
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    offset:o_and_l]

                        # create a list for a ul to work through

                        more_freights, where = get_list_of_pages(
                            current_page, tf_pages)

                    else:
                        # check if we have any current ones
                        if f_pages > 0:
                            freights = Freight.objects.all().order_by('title')[
                                :limit]
                            if freights.count() < limit:
                                left = limit - freights.count()
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :left]
                            else:
                                oldfreights = []
                        else:
                            freights = []
                            oldfreigths = OldFreight.objects.all().order_by('title')[
                                :limit]

                        # create a list for a ul to work through

                        more_freights, where = get_list_of_pages(
                            current_page, tf_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == 4:
                        start = False

                    if current_page == f_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if where == "end":
                        end = False

                    if current_page < f_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # make an empty freight for the new form
                    freight = Freight()
                    # search form
                    form = searchFreightForm()
                    form.startup()
                    onSubmit = get_message('warning', 5)

                    context = {
                        'gdpr_check': gdpr_check,
                        'warning': False,
                        'freights': freights,
                        'oldfreights': oldfreights,
                        'freight': freight,
                        'form': form,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_freights': more_freights,
                        'onSubmit': onSubmit,
                        'current_page': int(current_page),
                        'max': f_pages,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_freights.html", context)

            elif 'nextPage' in self.request.POST.keys():
                if current_page > tf_pages:
                    current_page = tf_pages
                else:
                    if current_page < tf_pages:
                        current_page += 1

                if search_type == 1:
                    if search_value != "Not set":
                        # we are paginating a specific search if we are here we shouldnt have any pageing it shouldnt be possible to be here so reload
                        messages.warning(
                            self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                        return redirect("moderator:freights")
                    else:
                        if current_page > 1:
                            # we are just looking for current freights we dont need aditionals
                            # get the right offset freights
                            # query[offset:offset + limit]
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            freights = Freight.objects.all().order_by('title')[
                                offset:o_and_l]
                            oldfreights = []

                            # create a list for a ul to work through

                            more_freights, where = get_list_of_pages(
                                current_page, f_pages)

                        else:
                            # we are just looking for current freights we dont need aditionals
                            # check if we have any current ones
                            if f_pages > 0:
                                freights = Freight.objects.all().order_by('title')[
                                    :limit]
                                oldfreights = []
                                # create a list for a ul to work through

                                more_freights, where = get_list_of_pages(
                                    current_page, f_pages)
                            else:
                                freights = []
                                oldfreigths = []
                                more_freights = []
                                where = "no extras"
                                f_pages = 1

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

                elif search_type == 2:
                    if search_value != "Not set":
                        # we are paginating a search if we are here we shouldnt have any page above 1 it also shouldnt be possible to be here so reload
                        messages.warning(
                            self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                        return redirect("moderator:freights")
                    else:
                        if current_page > 1:
                            # we are just looking for old freights we dont need aditionals
                            # get the right offset freights
                            # query[offset:offset + limit]
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            oldfreights = OldFreight.objects.all().order_by('title')[
                                offset:o_and_l]
                            freights = []

                            # create a list for a ul to work through

                            more_freights, where = get_list_of_pages(
                                current_page, of_pages)

                        else:
                            # we are just looking for current freights we dont need aditionals
                            # check if we have any current ones
                            if f_pages > 0:
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :limit]
                                freights = []
                                # create a list for a ul to work through

                                more_freights, where = get_list_of_pages(
                                    current_page, of_pages)
                            else:
                                freights = []
                                oldfreigths = []
                                more_freights = []
                                where = "no extras"
                                f_pages = 1

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

                else:
                    if current_page > 1:
                        # get the right offset freights
                        # query[offset:offset + limit]
                        if current_page <= f_pages:
                            # we are still showing currently active freigts and possibly some old ones, bet the current ones first
                            offset = (current_page - 1) * limit
                            o_and_l = offset + limit
                            freights = Freight.objects.all().order_by('title')[
                                offset:o_and_l]
                            if freights.count() < limit:
                                # a check to see if we need to fill in with old ones
                                left = limit - freights.count()
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :left]
                            else:
                                oldfreights = []
                        else:
                            freights = []
                            # we have surpassed the current freights and only need the old ones
                            page = current_page - f_pages
                            if page == 1:
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :limit]
                            else:
                                offset = (page - 1) * limit
                                o_and_l = offset + limit
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    offset:o_and_l]

                        # create a list for a ul to work through

                        more_freights, where = get_list_of_pages(
                            current_page, tf_pages)

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)
                    else:
                        # check if we have any current ones
                        if f_pages > 0:
                            freights = Freight.objects.all().order_by('title')[
                                :limit]
                            if freights.count() < limit:
                                left = limit - freights.count()
                                oldfreights = OldFreight.objects.all().order_by('title')[
                                    :left]
                            else:
                                oldfreights = []
                        else:
                            freights = []
                            oldfreigths = OldFreight.objects.all().order_by('title')[
                                :limit]  # create a list for a ul to work through

                        more_freights, where = get_list_of_pages(
                            current_page, tf_pages)

                        # pagination booleans

                        if current_page == 1 or where == "no extras":
                            start = False
                        else:
                            start = True

                        if current_page == 4:
                            start = False

                        if current_page == f_pages or where == "no extras":
                            end = False
                        else:
                            end = True

                        if where == "end":
                            end = False

                        if current_page < f_pages:
                            next_page = True
                        else:
                            next_page = False

                        if current_page > 1:
                            previous_page = True
                        else:
                            previous_page = False

                        # make an empty freight for the new form
                        freight = Freight()
                        # search form
                        form = searchFreightForm()
                        form.startup()
                        onSubmit = get_message('warning', 5)

                        context = {
                            'gdpr_check': gdpr_check,
                            'warning': False,
                            'freights': freights,
                            'oldfreights': oldfreights,
                            'freight': freight,
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'more_freights': more_freights,
                            'onSubmit': onSubmit,
                            'current_page': int(current_page),
                            'max': f_pages,
                            'previous_page': previous_page,
                            'next_page': next_page,
                            'end': end,
                            'start': start,
                        }

                        return render(self.request, "moderator/mod_freights.html", context)

        elif 'newSearch' in self.request.POST.keys():
            # get the default number of current freights
            warning = False
            allFreight = False
            form = searchFreightForm(self.request.POST)
            current_page = 1
            if form.is_valid():
                freight_id = form.cleaned_data.get('freight_id')
                if freight_id == None:
                    # we are searching for all of a type
                    allFreight = True
                freight_type = form.cleaned_data.get('freight_type')

                if freight_type == "1":
                    oldfreights = []
                    if allFreight:
                        # all current  we wont paginate here for now
                        freights = Freight.objects.all()[:limit]
                        if freights.count() == 0:
                            warning = True
                            where = "no extras"
                            more_freights = []
                            p_pages = 0
                        else:
                            more_freights, where = get_list_of_pages(
                                1, f_pages)
                            p_pages = f_pages
                    else:
                        freights = Freight.objects.filter(id=freight_id)
                        if freights.count() == 0:
                            warning = True
                            where = "no extras"
                            more_freights = []
                            p_pages = 0
                elif freight_type == "2":
                    freights = []
                    if allFreight:
                        # all old ones we wont paginate here for now
                        oldfreights = OldFreight.objects.all()
                        if oldfreights.count() == 0:
                            warning = True
                            where = "no extras"
                            more_freights = []
                            p_pages = 0
                        else:
                            more_freights, where = get_list_of_pages(
                                1, of_pages)
                            p_pages = f_pages
                    else:
                        oldfreights = OldFreight.objects.filter(id=freight_id)
                        if oldfreights.count() == 0:
                            warning = True
                            where = "no extras"
                            more_freights = []
                            p_pages = 0
                else:
                    # something is wrong just list some empty values
                    warning = False
                    freights = []
                    oldfreights = []
                    where = "no extras"
                    more_freights = []
                    p_pages = 0

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == 4:
                    start = False

                if current_page == p_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < p_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                search_value = freight_id
                search_type = "freight_id"
                if allFreight and freight_type == "1":
                    search_value = "Alla nuvarande"
                    search_type = "current"
                elif allFreight and freight_type == "2":
                    search_value = "Alla gamla"
                    search_type = "old"
                elif not allFreight and freight_type == "1":
                    search_value = "Id " + \
                        str(freight_id) + " nuvarande alternativ"
                    search_type = "freight_id_current"
                elif not allFreight and freight_type == "2":
                    search_value = "Id " + \
                        str(freight_id) + " gamla alternativ"
                    search_type = "freight_id_old"
                else:
                    search_value = ""

                search_done = True
                onSubmit = get_message('warning', 5)

                # make an empty freight for the new form
                freight = Freight()
                # update labels etc
                form.startup()

                context = {
                    'gdpr_check': gdpr_check,
                    'warning': warning,
                    'freights': freights,
                    'oldfreights': oldfreights,
                    'freight': freight,
                    'form': form,
                    'search_type': search_type,
                    'search_value': search_value,
                    'search_done': search_done,
                    'more_freights': more_freights,
                    'onSubmit': onSubmit,
                    'current_page': int(current_page),
                    'max': f_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_freights.html", context)
            else:
                # display just the regular page, show warning
                warning = True
                # GDPR check
                gdpr_check = check_gdpr_cookies(self)
                is_post = False
                # get the default_pagination_values of the current freights
                limit = default_pagination_values
                freights = Freight.objects.all().order_by('title')[:limit]
                try:
                    if freights.count() < limit:
                        left = limit - freights.count()
                        oldfreights = OldFreight.objects.all().order_by('title')[
                            :left]
                    else:
                        oldfreights = []
                except ObjectDoesNotExist:
                    # there are no old freights
                    oldfreights = []

                f_pages = 1

                if number_of_freights > limit:
                    # if there are more we divide by the offset
                    f_pages = number_of_freights / limit
                    # see if there is a decimal
                    testO = int(f_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testO != f_pages:
                        f_pages = int(f_pages)
                        f_pages += 1
                    if type(f_pages) != "int":
                        f_pages = int(f_pages)

                # create a list for a ul to work through

                current_page = 1
                more_freights, where = get_list_of_pages(current_page, f_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == 4:
                    start = False

                if current_page == f_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if where == "end":
                    end = False

                if current_page < f_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                # search form
                form = searchFreightForm()
                form.startup()

                #  search type and search_value to start values
                search_type = "Not set"
                search_value = "Not set"

                onSubmit = get_message('warning', 5)

                # make an empty freight for new freight option
                emptyfreight = Freight()

                context = {
                    'gdpr_check': gdpr_check,
                    'warning': warning,
                    'freights': freights,
                    'oldfreights': oldfreights,
                    'form': form,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_freights': more_freights,
                    'onSubmit': onSubmit,
                    'freight': emptyfreight,
                    'current_page': int(current_page),
                    'max': f_pages,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_freights.html", context)

        elif "resetFreightSearch" in self.request.POST.keys():
            # resetting form
            return redirect("moderator:freights")
        else:
            # something wrong
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:freights")


class SpecificFreightView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 8)
        messages.warning(
            self.request, message)
        return redirect("moderator:freights")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'see' in self.request.POST.keys():
            # get the id
            freight_id = int(self.request.POST['see'])
            freight_type = self.request.POST['freight_type']
            if freight_type == "current":
                # get freight form
                freight = Freight.objects.get(id=freight_id)
                form = freightForm(initial={
                    'title': freight.title, 'amount': freight.amount, 'description': freight.description}, instance=freight)
                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'new': False,
                    'old': False,
                    'freight': freight_id,
                }

                return render(self.request, "moderator/mod_single_freight.html", context)
            elif freight_type == "old":
                # get freight form
                oldFreight = OldFreight.objects.get(id=freight_id)
                form = oldFreightForm(initial={
                                      'title': oldFreight.title, 'amount': oldFreight.amount, 'description': oldFreight.description}, instance=oldFreight)
                context = {
                    'form': form,
                    'new': False,
                    'old': True,
                    'freight': freight_id,
                }

                return render(self.request, "moderator/mod_single_freight.html", context)
        elif 'new' in self.request.POST.keys():
            # get freight form
            form = freightForm()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'new': True,
                'old': False,
                'freight': '',
            }

            return render(self.request, "moderator/mod_single_freight.html", context)
        elif 'saveOld' in self.request.POST.keys():
            # get the id
            freight_id = int(self.request.POST['freight'])
            # check status
            inactive = self.request.POST['inactive']
            # populate a form
            form = freightForm(self.request.POST)
            if form.is_valid():
                # get the freight
                freight = Freight.objects.get(id=freight_id)
                if freight.title != form.cleaned_data.get('title'):
                    today = datetime.now()
                    toSlug = slugify(freight.title + str(today.date))
                    testSlug = True
                    i = 1
                    while(testSlug):
                        try:
                            freight = Freight.objects.get(slug=toSlug)
                            toSlug = toSlug + str(i)
                            i += 1
                        except ObjectDoesNotExist:
                            testSlug = False

                    freight.slug = toSlug
                freight.title = form.cleaned_data.get('title')
                freight.amount = form.cleaned_data.get('amount')
                freight.description = form.cleaned_data.get('description')
                freight.save()
                info_message = get_message('info', 74)
                messages.info(self.request, info_message)
                return redirect("moderator:freights")
            else:
                old = False
                if inactive == "yes":
                    old = True
                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'new': False,
                    'old': old,
                    'freight': freight_id,
                }
                message = get_message('error', 115)
                messages.warning(
                    self.request, message)
                return render(self.request, "moderator/mod_single_freight.html", context)

        elif 'saveNew' in self.request.POST.keys():
            # populate a form
            form = freightForm(self.request.POST)
            if form.is_valid():
                # get the freight
                freight = Freight()
                today = datetime.now()
                freight.title = form.cleaned_data.get('title')
                freight.amount = form.cleaned_data.get('amount')
                freight.description = form.cleaned_data.get('description')
                toSlug = slugify(freight.title + str(today.date))
                testSlug = True
                i = 1
                while(testSlug):
                    try:
                        freight = Freight.objects.get(slug=toSlug)
                        toSlug = toSlug + str(i)
                        i += 1
                    except ObjectDoesNotExist:
                        testSlug = False

                freight.slug = toSlug
                freight.save()
                info_message = get_message('info', 75)
                messages.info(self.request, info_message)
                return redirect("moderator:freights")
            else:
                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'new': True,
                    'freight': '',
                }
                message = get_message('error', 116)
                messages.warning(
                    self.request, message)
                return render(self.request, "moderator/mod_single_freight.html", context)
        elif 'reactivate' in self.request.POST.keys():
            reactivate = self.request.POST['reactivate']
            the_id = int(self.request.POST['freight'])
            if reactivate == "yes":
                # create a new freight post from the old one and delete the old one
                freight = Freight()
                oldFreight = OldFreight.objects.get(id=the_id)
                freight.title = oldFreight.title
                freight.amount = oldFreight.amount
                freight.slug = oldFreight.slug
                freight.description = oldFreight.description
                freight.save()
                oldFreight.delete()
                messages.info(self.request, "Frakt aktiverad")
                return redirect("moderator:freights")
            elif reactivate == "no":
                # create an old freight post from the new one and delete the new one
                oldFreight = OldFreight()
                freight = Freight.objects.get(id=the_id)
                oldFreight.title = freight.title
                oldFreight.amount = freight.amount
                oldFreight.slug = freight.slug
                oldFreight.description = freight.description
                oldFreight.save()
                freight.delete()
                messages.info(self.request, "Frakt borttagen")
                return redirect("moderator:freights")
        elif "cancel" in self.request.POST.keys():
            return redirect("moderator:freights")
        else:
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:freights")


class CouponsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        limit = default_pagination_values
        # get the 20 first current freights
        coupons = Coupon.objects.all().order_by('code')[:limit]
        number_of_coupons = Coupon.objects.all().count()

        c_pages = 1

        if number_of_coupons > limit:
            # if there are more we divide by the limit
            c_pages = number_of_coupons / limit
            # see if there is a decimal
            testC = int(c_pages)
            # if there isn't an even number make an extra page for the last group
            if testC != c_pages:
                c_pages = int(c_pages)
                c_pages += 1
            if type(c_pages) != "int":
                c_pages = int(c_pages)

        # set current page, search type and search_value to start values
        current_page = 1
        search_type = "None"
        search_value = ""

        # create a list for a ul to work through

        more_coupons, where = get_list_of_pages(1, c_pages)

        # pagination booleans

        if current_page == 1 or where == "no extras":
            start = False
        else:
            start = True

        if current_page == c_pages or where == "no extras":
            end = False
        else:
            end = True

        if current_page < c_pages:
            next_page = True
        else:
            next_page = False

        if current_page > 1:
            previous_page = True
        else:
            previous_page = False

        # make an empty coupon for the new form
        coupon = Coupon()
        # search form
        form = searchCouponForm()

        onSubmit = get_message('warning', 7)

        context = {
            'gdpr_check': gdpr_check,
            'coupons': coupons,
            'coupon': coupon,
            'form': form,
            'current_page': current_page,
            'search_type': search_type,
            'search_value': search_value,
            'more_coupons': more_coupons,
            'max_pages': c_pages,
            'onSubmit': onSubmit,
            'previous_page': previous_page,
            'next_page': next_page,
            'end': end,
            'start': start,
        }

        return render(self.request, "moderator/mod_coupons.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        limit = default_pagination_values
        if 'delete' in self.request.POST.keys():
            # delete coupon
            # get id
            coupon_id = int(self.request.POST['delete'])
            coupon = Coupon.objects.get(id=coupon_id)
            coupon.delete()
            # change to coupon message version
            info_message = get_message('info', 78)
            messages.info(self.request, info_message)
            return redirect("moderator:coupons")
        elif 'previousPage' in self.request.POST.keys():
            if 'search' in self.request.POST.keys() and 'searchValue' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = self.request.POST['search']
                search_value = self.request.POST['searchValue']
                current_page = int(self.request.POST['current_page'])

                if current_page >= 2:
                    # get the coupons
                    current_page -= 1
                    offset = (current_page - 1) * limit
                    o_l = offset + limit
                    coupons = Coupon.objects.all().order_by('code')[
                        offset:o_l]
                    number_of_coupons = Coupon.objects.all().count()

                    c_pages = 1

                    if number_of_coupons > limit:
                        # if there are more we divide by the limit
                        c_pages = number_of_coupons / limit
                        # see if there is a decimal
                        testO = int(c_pages)
                        # if there isn't an even number make an extra page for the last group
                        if testO != c_pages:
                            c_pages = int(c_pages)
                            c_pages += 1
                        if type(c_pages) != "int":
                            c_pages = int(c_pages)

                    # create a list for a ul to work through

                    more_coupons, where = get_list_of_pages(
                        current_page, c_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == c_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if current_page < c_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # make an empty coupon for the new form
                    coupon = Coupon()
                    # search form
                    form = searchCouponForm()
                    onSubmit = get_message('warning', 7)

                    context = {
                        'gdpr_check': gdpr_check,
                        'coupons': coupons,
                        'coupon': coupon,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_coupons': more_coupons,
                        'max_pages': c_pages,
                        'onSubmit': onSubmit,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_coupons.html", context)
                if current_page == 1:
                    # this shouldnt happen but to make sure
                    # get the coupons
                    coupons = Coupon.objects.all().order_by('code')[:limit]
                    number_of_coupons = Coupon.objects.all().count()

                    c_pages = 1

                    if number_of_coupons > limit:
                        # if there are more we divide by limit
                        c_pages = number_of_coupons / limit
                        # see if there is a decimal
                        testO = int(c_pages)
                        # if there isn't an even number make an extra page for the last group
                        if testO != c_pages:
                            c_pages = int(c_pages)
                            c_pages += 1
                        if type(c_pages) != "int":
                            c_pages = int(c_pages)

                    # create a list for a ul to work through

                    # create a list for a ul to work through

                    more_coupons, where = get_list_of_pages(1, c_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == c_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if current_page < c_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # make an empty coupon for the new form
                    coupon = Coupon()
                    # search form
                    form = searchCouponForm()
                    onSubmit = get_message('warning', 7)

                    context = {
                        'gdpr_check': gdpr_check,
                        'coupons': coupons,
                        'coupon': coupon,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_coupons': more_coupons,
                        'max_pages': c_pages,
                        'onSubmit': onSubmit,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_coupons.html", context)

            else:
                messages.warning(
                    self.request, "5 Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:overview")
        elif 'page' in self.request.POST.keys():
            if 'search' in self.request.POST.keys() and 'searchValue' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = self.request.POST['search']
                search_value = self.request.POST['searchValue']
                page = int(self.request.POST['page'])
                current_page = page

                # we need the max pages first

                number_of_coupons = Coupon.objects.all().count()

                c_pages = 1

                if number_of_coupons > limit:
                    # if there are more we divide by limit
                    c_pages = number_of_coupons / limit
                    # see if there is a decimal
                    testO = int(c_pages)
                    # if there isn't an even number make an extra page for the last group
                    if testO != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1
                    if type(c_pages) != "int":
                        c_pages = int(c_pages)

                if page == 1:

                    coupons = Coupon.objects.all().order_by('code')[
                        :limit]

                    # create a list for a ul to work through

                    more_coupons, where = get_list_of_pages(1, c_pages)

                    # pagination booleans

                    if current_page == 1 or where == "no extras":
                        start = False
                    else:
                        start = True

                    if current_page == c_pages or where == "no extras":
                        end = False
                    else:
                        end = True

                    if current_page < c_pages:
                        next_page = True
                    else:
                        next_page = False

                    if current_page > 1:
                        previous_page = True
                    else:
                        previous_page = False

                    # make an empty coupon for the new form
                    coupon = Coupon()
                    # search form
                    form = searchCouponForm()
                    onSubmit = get_message('warning', 7)

                    context = {
                        'gdpr_check': gdpr_check,
                        'coupons': coupons,
                        'coupon': coupon,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_coupons': more_coupons,
                        'max_pages': c_pages,
                        'onSubmit': onSubmit,
                        'previous_page': previous_page,
                        'next_page': next_page,
                        'end': end,
                        'start': start,
                    }

                    return render(self.request, "moderator/mod_coupons.html", context)

                if page > c_pages:
                    page = c_pages

                # get the coupons
                offset = limit * (page - 1)
                o_l = offset + limit
                coupons = Coupon.objects.all().order_by('code')[
                    offset:o_l]

                # create a list for a ul to work through

                more_coupons, where = get_list_of_pages(page, c_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == c_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if current_page < c_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                # make an empty coupon for the new form
                coupon = Coupon()
                # search form
                form = searchCouponForm()

                current_page = page
                onSubmit = get_message('warning', 7)

                context = {
                    'gdpr_check': gdpr_check,
                    'coupons': coupons,
                    'coupon': coupon,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_coupons': more_coupons,
                    'max_pages': c_pages,
                    'onSubmit': onSubmit,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_coupons.html", context)

            else:
                messages.warning(
                    self.request, "4 Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:overview")
        elif 'nextPage' in self.request.POST.keys():
            if 'search' in self.request.POST.keys() and 'searchValue' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():

                search_type = self.request.POST['search']
                search_value = self.request.POST['searchValue']
                current_page = int(self.request.POST['current_page'])

                # first we need the max amount of pages

                number_of_coupons = Coupon.objects.all().count()

                c_pages = 1

                if number_of_coupons > limit:
                    # if there are more we divide by limit
                    c_pages = number_of_coupons / limit
                    # see if there is a decimal
                    testO = int(c_pages)
                    # if there isn't an even number make an extra page for the last group
                    if testO != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1
                    if type(c_pages) != "int":
                        c_pages = int(c_pages)

                if current_page < c_pages:
                    current_page += 1

                offset = limit * (current_page - 1)
                o_l = offset + limit
                coupons = Coupon.objects.all().order_by('code')[
                    offset:o_l]

                # create a list for a ul to work through

                more_coupons, where = get_list_of_pages(current_page, c_pages)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == c_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if current_page < c_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                # make an empty coupon for the new form
                coupon = Coupon()
                # search form
                form = searchCouponForm()
                if search_type == "code":
                    form.populate(code=search_value)
                onSubmit = get_message('warning', 7)

                context = {
                    'gdpr_check': gdpr_check,
                    'coupons': coupons,
                    'coupon': coupon,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_coupons': more_coupons,
                    'max_pages': c_pages,
                    'onSubmit': onSubmit,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_coupons.html", context)
            else:
                messages.warning(
                    self.request, "3 Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:overview")
        elif 'search' in self.request.POST.keys():
            if 'code' in self.request.POST.keys():
                code = self.request.POST['code']
                if code == "":
                    # resetting form
                    return redirect("moderator:coupons")
                coupons = Coupon.objects.filter(code=code)
                c_pages = 1
                more_coupons = [1]

                # make an empty coupon for the new form
                coupon = Coupon()
                # search form
                form = searchCouponForm()
                form.populate(code)
                current_page = 1
                search_type = "code"
                search_value = code
                onSubmit = get_message('warning', 7)

                # pagination booleans

                if current_page == 1 or where == "no extras":
                    start = False
                else:
                    start = True

                if current_page == c_pages or where == "no extras":
                    end = False
                else:
                    end = True

                if current_page < c_pages:
                    next_page = True
                else:
                    next_page = False

                if current_page > 1:
                    previous_page = True
                else:
                    previous_page = False

                context = {
                    'gdpr_check': gdpr_check,
                    'coupons': coupons,
                    'coupon': coupon,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_coupons': more_coupons,
                    'max_pages': c_pages,
                    'onSubmit': onSubmit,
                    'previous_page': previous_page,
                    'next_page': next_page,
                    'end': end,
                    'start': start,
                }

                return render(self.request, "moderator/mod_coupons.html", context)
            else:
                messages.warning(
                    self.request, "1 Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:overview")
        else:
            messages.warning(
                self.request, "2 Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:overview")


class SpecificCouponView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 9)
        messages.warning(
            self.request, message)
        return redirect("moderator:coupons")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'see' in self.request.POST.keys():
            # get the id
            coupon_id = int(self.request.POST['see'])
            # get freight form
            form = couponForm()
            form.populate(coupon_id)
            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'new': False,
                'coupon': coupon_id,
                'coupon_type': '',
            }

            return render(self.request, "moderator/mod_single_coupon.html", context)
        elif 'new' in self.request.POST.keys():
            # get freight form
            form = couponForm()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'new': True,
                'coupon': '',
                'coupon_type': '',
            }

            return render(self.request, "moderator/mod_single_coupon.html", context)
        elif 'saveOld' in self.request.POST.keys():
            # get the id
            coupon_id = int(self.request.POST['saveOld'])
            # populate a form
            form = couponForm(self.request.POST)
            if form.is_valid():
                # get the freight
                coupon = Coupon.objects.get(id=coupon_id)
                if coupon.code != form.cleaned_data.get('code'):
                    today = datetime.now()
                    toSlug = slugify(coupon.code)
                    testSlug = True
                    i = 1
                    while(testSlug):
                        try:
                            someCoupons = Coupon.objects.get(slug=toSlug)
                            toSlug = toSlug + str(i)
                            i += 1
                        except ObjectDoesNotExist:
                            testSlug = False

                    freight.slug = toSlug
                coupon.code = form.cleaned_data.get('code')
                coupon_type = int(self.request.POST['coupon_type'])
                if coupon_type == 1:
                    coupon.coupon_type = 'Percent'
                elif coupon_type == 2:
                    coupon.coupon_type = 'Amount'
                coupon.amount = form.cleaned_data.get('amount')
                coupon.save()
                info_message = get_message('info', 79)
                messages.info(self.request, info_message)
                return redirect("moderator:coupons")
            else:
                coupon_type = int(self.request.POST['coupon_type'])
                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'new': False,
                    'coupon': coupon_id,
                    'coupon_type': coupon_type,
                }
                message = get_message('error', 129)
                messages.warning(
                    self.request, message)
                return render(self.request, "moderator/mod_single_coupon.html", context)
        elif 'saveNew' in self.request.POST.keys():
            # populate a form
            form = couponForm(self.request.POST)
            if form.is_valid():
                # get the freight
                coupon = Coupon()
                coupon.code = form.cleaned_data.get('code')
                coupon_type = int(self.request.POST['coupon_type'])
                if coupon_type == 1:
                    coupon.coupon_type = 'Percent'
                elif coupon_type == 2:
                    coupon.coupon_type = 'Amount'
                coupon.amount = form.cleaned_data.get('amount')
                toSlug = slugify(coupon.code)
                testSlug = True
                i = 1
                while(testSlug):
                    try:
                        someCoupons = Coupon.objects.get(slug=toSlug)
                        toSlug = toSlug + str(i)
                        i += 1
                    except ObjectDoesNotExist:
                        testSlug = False

                coupon.slug = toSlug
                coupon.save()
                info_message = get_message('info', 80)
                messages.info(self.request, info_message)
                return redirect("moderator:coupons")
            else:
                coupon_type = int(self.request.POST['coupon_type'])
                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'new': True,
                    'coupon': '',
                    'coupon_type': coupon_type,
                }
                message = get_message('error', 130)
                messages.warning(
                    self.request, message)
                return render(self.request, "moderator/mod_single_coupon.html", context)
        else:
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:coupons")


class FAQsView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        # get the limit
        limit = default_pagination_values
        # establish language first, this should later have a check
        theLang = "swe"
        comment = []
        try:
            theLanguage = LanguageChoices.objects.get(
                language_short=theLang)
            try:
                searchForm = SearchFAQForm()
                searchForm.language(theLanguage)
            except ObjectDoesNotExist:
                searchForm = SearchFAQForm()
            try:
                faqs = FAQ.objects.all()[:limit]
            except ObjectDoesNotExist:
                comment = "No FAQs found"
            try:
                aButtonType = ButtonType.objects.get(buttonType="search")
                searchButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=aButtonType)
            except ObjectDoesNotExist:
                searchButton = {"buttonText": "Search"}
                comment.append("No search Button found")
            try:
                bButtonType = ButtonType.objects.get(buttonType="add new")
                addButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=bButtonType)
            except ObjectDoesNotExist:
                addButton = {"buttonText": "Add"}
                comment.append("No add Button found")
            try:
                cButtonType = ButtonType.objects.get(buttonType="delete")
                deleteButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=cButtonType)
            except ObjectDoesNotExist:
                deleteButton = {"buttonText": "Delete"}
                comment.append("No add Button found")

            # set the hidden value for wether or not we have done a search

            current_page = 1
            search_type = "None"
            search_value = ""

            more_faqs = []
            c_faqs = FAQ.objects.all().count()
            d_faqs = 1
            if c_faqs > limit:
                # if there are more we divide by the limit
                d_faqs = c_faqs / limit
                # see if there is a decimal
                testF = int(d_faqs)
                # if there isn't an even number of ten make an extra page for the last group
                if testF != d_faqs:
                    d_faqs += 1
                if type(testF) != type(d_faqs):
                    d_faqs = int(d_faqs)

            # populate the list with the amount of pages there are
            more_faqs, where = get_list_of_pages(1, d_faqs)
            # some booleans to mark where we are in the pagination

            start = False

            if current_page == 1:
                previous_page = False
            else:
                previous_page = True

            if where == "start":
                end = True
            else:
                end = False

            if current_page == d_faqs:
                next_page = False
            else:
                next_page = True

            # for the new button
            empty_faq = FAQ()

            context = {
                'gdpr_check': gdpr_check,
                'searchform': searchForm,
                'search': False,
                'search_type': search_type,
                'search_value': search_value,
                'FAQS': faqs,
                'searchButton': searchButton,
                'addButton': addButton,
                'deleteButton': deleteButton,
                'comment': comment,
                'current_page': current_page,
                'more_faqs': more_faqs,
                'max': d_faqs,
                'start': start,
                'previous_page': previous_page,
                'end': end,
                'next_page': next_page,
                'empty_faq': empty_faq,
            }

            return render(self.request, "moderator/mod_faqs.html", context)
        except ObjectDoesNotExist:
            # we dont either dont have a chosen language or the language chosen doesnt exist, this is bad. You cant get error messages correctly here. Send to settings.
            message = "Vi kan inte hitta språket som är valt. Kontakta IT support för hjälp."
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        path = self.request.get_full_path()
        is_post = False
        # get the limit
        limit = default_pagination_values
        # establish language first, this should later have a check
        theLang = "swe"
        comment = []
        theLanguage = LanguageChoices.objects.get(language_short=theLang)
        try:
            aButtonType = ButtonType.objects.get(buttonType="search")
            searchButton = ButtonText.objects.filter(
                language=theLanguage, theButtonType=aButtonType)
        except ObjectDoesNotExist:
            searchButton = {"buttonText": "Search"}
            comment.append("No search Button found")
        try:
            bButtonType = ButtonType.objects.get(buttonType="add new")
            addButton = ButtonText.objects.filter(
                language=theLanguage, theButtonType=bButtonType)
        except ObjectDoesNotExist:
            addButton = {"buttonText": "Add"}
            comment.append("No add Button found")
        try:
            cButtonType = ButtonType.objects.get(buttonType="delete")
            deleteButton = ButtonText.objects.filter(
                language=theLanguage, theButtonType=cButtonType)
        except ObjectDoesNotExist:
            deleteButton = {"buttonText": "Delete"}
            comment.append("No add Button found")

        # for the new button
        empty_faq = FAQ()

        if "search" in self.request.POST.keys():
            search = self.request.POST['search']
            form = SearchFAQForm(self.request.POST)
            current_page = 1
            d_faqs = 1
            if search == "None":
                if 'paging' in self.request.POST.keys():
                    try:
                        searchForm = SearchFAQForm()
                        searchForm.language(theLanguage)
                    except ObjectDoesNotExist:
                        searchForm = SearchFAQForm()
                    search_type = "None"
                    search_value = ""
                    # we're paging not searching
                    previous_page = int(self.request.POST['current_page'])
                    # GDPR check
                    gdpr_check = check_gdpr_cookies(self)
                    path = self.request.get_full_path()
                    is_post = False
                    # get the limit
                    limit = default_pagination_values
                    # establish language first, this should later have a check
                    theLang = "swe"
                    comment = []
                    try:
                        theLanguage = LanguageChoices.objects.get(
                            language_short=theLang)

                        try:
                            aButtonType = ButtonType.objects.get(
                                buttonType="search")
                            searchButton = ButtonText.objects.filter(
                                language=theLanguage, theButtonType=aButtonType)
                        except ObjectDoesNotExist:
                            searchButton = {"buttonText": "Search"}
                            comment.append("No search Button found")
                        try:
                            bButtonType = ButtonType.objects.get(
                                buttonType="add new")
                            addButton = ButtonText.objects.filter(
                                language=theLanguage, theButtonType=bButtonType)
                        except ObjectDoesNotExist:
                            addButton = {"buttonText": "Add"}
                            comment.append("No add Button found")
                        try:
                            cButtonType = ButtonType.objects.get(
                                buttonType="delete")
                            deleteButton = ButtonText.objects.filter(
                                language=theLanguage, theButtonType=cButtonType)
                        except ObjectDoesNotExist:
                            deleteButton = {"buttonText": "Delete"}
                            comment.append("No add Button found")
                    except ObjectDoesNotExist:
                        # we dont either dont have a chosen language or the language chosen doesnt exist, this is bad. You cant get error messages correctly here. Send to settings.
                        message = "Vi kan inte hitta språket som är valt. Kontakta IT support för hjälp."
                        messages.warning(
                            self.request, message)
                        return redirect("moderator:faqs")
                    all_faqs = FAQ.objects.all()
                    more_faqs = []
                    c_faqs = len(all_faqs)
                    d_faqs = 1
                    if c_faqs > limit:
                        # if there are more we divide by the limit
                        d_faqs = c_faqs/limit
                        # see if there is a decimal
                        testF = int(d_faqs)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testF != d_faqs:
                            d_faqs += 1
                        if type(testF) != type(d_faqs):
                            d_faqs = int(d_faqs)

                    if 'nextPage' in self.request.POST.keys():
                        if previous_page < d_faqs and previous_page > 0:
                            current_page = previous_page + 1
                            offset = previous_page * limit
                            o_l = offset + limit
                            faqs = FAQ.objects.all()[offset:o_l]
                        elif precious_page == d_faqs:
                            current_page = d_faqs
                            offset = (current_page - 1) * limit
                            o_l = offset + limit
                            faqs = FAQ.objects.all()[offset:o_l]
                        else:
                            # something is off redirect
                            return redirect("moderator:faqs")
                    elif 'previousPage' in self.request.POST.keys():
                        if previous_page < 2:
                            # preventing paging down under 1
                            # just return page 1
                            faqs = FAQ.objects.all()[:limit]
                            current_page = 1

                        elif previous_page == 2:
                            # just return page 1
                            faqs = FAQ.objects.all()[:limit]
                            current_page = 1
                        else:
                            # not page 1
                            current_page = previous_page - 1
                            offset = (current_page - 1) * limit
                            o_l = offset + limit
                            faqs = FAQ.objects.all()[offset:o_l]
                    elif 'page' in self.request.POST.keys():
                        chosen_page = int(self.request.POST['page'])
                        if chosen_page > 0 and chosen_page <= d_faqs:
                            if chosen_page == 1:
                                faqs = FAQ.objects.all()[:limit]
                            else:
                                current_page = chosen_page
                                offset = (current_page - 1) * limit
                                o_l = offset + limit
                                faqs = FAQ.objects.all()[offset:o_l]
                        else:
                            # something is off redirect
                            return redirect("moderator:faqs")

                    else:
                        # something is off redirect
                        return redirect("moderator:faqs")

                    # populate the list with the amount of pages there are# populate the list with the amount of pages there are
                    more_faqs, where = get_list_of_pages(1, d_faqs)
                    # some booleans to mark where we are in the pagination

                    start = False

                    if current_page == 1:
                        previous_page = False
                    else:
                        previous_page = True

                    if where == "start":
                        end = True
                    else:
                        end = False

                    if current_page == d_faqs:
                        next_page = False
                    else:
                        next_page = True

                    context = {
                        'gdpr_check': gdpr_check,
                        'searchform': searchForm,
                        'search': False,
                        'search_type': search_type,
                        'search_value': search_value,
                        'FAQS': faqs,
                        'searchButton': searchButton,
                        'addButton': addButton,
                        'deleteButton': deleteButton,
                        'comment': comment,
                        'current_page': current_page,
                        'more_faqs': more_faqs,
                        'max': d_faqs,
                        'start': start,
                        'previous_page': previous_page,
                        'end': end,
                        'next_page': next_page,
                        'empty_faq': empty_faq,
                    }
                    return render(self.request, "moderator/mod_faqs.html", context)
                else:
                    # we're using the form
                    if form.is_valid():
                        searchID = form.cleaned_data.get('searchID')
                        searchTerm = form.cleaned_data.get('searchTerm')
                        language = form.cleaned_data.get('languages')
                        form.language(theLanguage)
                        if searchID != None:
                            searchID = int(searchID)
                            try:
                                faqs = FAQ.objects.filter(id=searchID)
                            except ObjectDoesNotExist:
                                faqs = []
                            search_type = "searchID"
                            search_value = searchID
                            more_faqs, where = get_list_of_pages(
                                current_page, d_faqs)
                            # some booleans to mark where we are in the pagination

                            start = False

                            if current_page == 1:
                                previous_page = False
                            else:
                                previous_page = True

                            if where == "start":
                                end = True
                            else:
                                end = False

                            if current_page == d_faqs:
                                next_page = False
                            else:
                                next_page = True

                            context = {
                                'gdpr_check': gdpr_check,
                                'searchform': form,
                                'search': False,
                                'search_type': search_type,
                                'search_value': search_value,
                                'FAQS': faqs,
                                'searchButton': searchButton,
                                'addButton': addButton,
                                'deleteButton': deleteButton,
                                'comment': comment,
                                'current_page': current_page,
                                'more_faqs': more_faqs,
                                'max': d_faqs,
                                'start': start,
                                'previous_page': previous_page,
                                'end': end,
                                'next_page': next_page,
                                'empty_faq': empty_faq,
                            }
                        elif searchTerm != None:
                            try:
                                faqs = FAQ.objects.filter(
                                    Q(subject__contains=searchTerm) | Q(content__contains=searchTerm))
                            except ObjectDoesNotExist:
                                faqs = []
                            search_type = "searchTerm"
                            search_value = searchTerm

                            more_faqs, where = get_list_of_pages(
                                current_page, d_faqs)
                            # some booleans to mark where we are in the pagination

                            start = False

                            if current_page == 1:
                                previous_page = False
                            else:
                                previous_page = True

                            if where == "start":
                                end = True
                            else:
                                end = False

                            if current_page == d_faqs:
                                next_page = False
                            else:
                                next_page = True
                            context = {
                                'gdpr_check': gdpr_check,
                                'searchform': form,
                                'search': False,
                                'search_type': search_type,
                                'search_value': search_value,
                                'FAQS': faqs,
                                'searchButton': searchButton,
                                'addButton': addButton,
                                'deleteButton': deleteButton,
                                'comment': comment,
                                'current_page': current_page,
                                'more_faqs': more_faqs,
                                'max': d_faqs,
                                'start': start,
                                'previous_page': previous_page,
                                'end': end,
                                'next_page': next_page,
                                'empty_faq': empty_faq,
                            }
                        else:
                            return redirect("moderator:faqs")
                        return render(self.request, "moderator/mod_faqs.html", context)
                    else:
                        # form invalid, not possible but for safeties sake
                        return redirect("moderator:faqs")
            elif search == "searchID":
                # check if we are paging
                if 'paging' in self.request.POST.keys():
                    # this hasnt been implemented
                    return redirect("moderator:faqs")
                elif 'newSearch' in self.request.POST.keys():
                    # we are doing a new search from the form
                    if form.is_valid():
                        searchID = form.cleaned_data.get('searchID')
                        searchTerm = form.cleaned_data.get('searchTerm')
                        language = form.cleaned_data.get('languages')
                        form.language(theLanguage)
                        if searchID != None:
                            searchID = int(searchID)
                            try:
                                faqs = FAQ.objects.filter(id=searchID)
                            except ObjectDoesNotExist:
                                faqs = []
                            search_type = "searchID"
                            search_value = searchID
                            context = {
                                'gdpr_check': gdpr_check,
                                'searchform': form,
                                'search': False,
                                'search_type': search_type,
                                'search_value': search_value,
                                'FAQS': faqs,
                                'searchButton': searchButton,
                                'addButton': addButton,
                                'deleteButton': deleteButton,
                                'comment': comment,
                                'current_page': current_page,
                                'more_faqs': [1],
                                'max': d_faqs,
                                'start': False,
                                'previous_page': False,
                                'end': False,
                                'next_page': False,
                                'empty_faq': empty_faq,
                            }
                        elif searchTerm != None:
                            try:
                                faqs = FAQ.objects.filter(
                                    Q(subject__contains=searchTerm) | Q(content__contains=searchTerm))
                            except ObjectDoesNotExist:
                                faqs = []
                            search_type = "searchTerm"
                            search_value = searchTerm
                            context = {
                                'gdpr_check': gdpr_check,
                                'searchform': form,
                                'search': False,
                                'search_type': search_type,
                                'search_value': search_value,
                                'FAQS': faqs,
                                'searchButton': searchButton,
                                'addButton': addButton,
                                'deleteButton': deleteButton,
                                'comment': comment,
                                'current_page': current_page,
                                'more_faqs': [1],
                                'max': d_faqs,
                                'start': False,
                                'previous_page': False,
                                'end': False,
                                'next_page': False,
                                'empty_faq': empty_faq,
                            }
                        else:
                            return redirect("moderator:faqs")
                        return render(self.request, "moderator/mod_faqs.html", context)
                    else:
                        # form invalid, not possible but for safeties sake
                        return redirect("moderator:faqs")
                else:
                    # something is off redirect
                    return redirect("moderator:faqs")
            elif search == "searchTerm":
                # check if we are paging
                if 'paging' in self.request.POST.keys():
                    # this hasnt been implemented
                    return redirect("moderator:faqs")
                elif 'newSearch' in self.request.POST.keys():
                    # we are doing a new search from the form
                    if form.is_valid():
                        searchID = form.cleaned_data.get('searchID')
                        searchTerm = form.cleaned_data.get('searchTerm')
                        language = form.cleaned_data.get('languages')
                        form.language(theLanguage)
                        if searchID != None:
                            searchID = int(searchID)
                            try:
                                faqs = FAQ.objects.filter(id=searchID)
                            except ObjectDoesNotExist:
                                faqs = []
                            search_type = "searchID"
                            search_value = searchID
                            context = {
                                'gdpr_check': gdpr_check,
                                'searchform': form,
                                'search': False,
                                'search_type': search_type,
                                'search_value': search_value,
                                'FAQS': faqs,
                                'searchButton': searchButton,
                                'addButton': addButton,
                                'deleteButton': deleteButton,
                                'comment': comment,
                                'current_page': current_page,
                                'more_faqs': [1],
                                'max': d_faqs,
                                'start': False,
                                'previous_page': False,
                                'end': False,
                                'next_page': False,
                                'empty_faq': empty_faq,
                            }
                        elif searchTerm != "":
                            try:
                                faqs = FAQ.objects.filter(
                                    Q(subject__contains=searchTerm) | Q(content__contains=searchTerm))
                            except ObjectDoesNotExist:
                                faqs = []
                            search_type = "searchTerm"
                            search_value = searchTerm
                            context = {
                                'gdpr_check': gdpr_check,
                                'searchform': form,
                                'search': False,
                                'search_type': search_type,
                                'search_value': search_value,
                                'FAQS': faqs,
                                'searchButton': searchButton,
                                'addButton': addButton,
                                'deleteButton': deleteButton,
                                'comment': comment,
                                'current_page': current_page,
                                'more_faqs': [1],
                                'max': d_faqs,
                                'start': False,
                                'previous_page': False,
                                'end': False,
                                'next_page': False,
                                'empty_faq': empty_faq,
                            }
                        else:
                            return redirect("moderator:faqs")
                        return render(self.request, "moderator/mod_faqs.html", context)
                    else:
                        # form invalid, not possible but for safeties sake
                        return redirect("moderator:faqs")
                else:
                    # something is off redirect
                    return redirect("moderator:faqs")
            else:
                # something is off redirect
                return redirect("moderator:faqs")
        else:
            return redirect("moderator:faqs")


class SpecificFAQView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # this shouldnt happen, send back to FAQS
        return redirect("moderator:faqs")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'lookAtFAQ' in self.request.POST.keys():
            # establish the users language first, this should later have a check
            theLang = "Svenska"
            comment = []
            try:
                theLanguage = LanguageChoices.objects.get(
                    language=theLang)
                try:
                    faqID = int(self.request.POST['lookAtFAQ'])
                    faq = FAQ.objects.select_related("language").get(id=faqID)
                    form = UpdateFAQ()
                    form.language(theLanguage, faq)
                    try:
                        aButtonType = ButtonType.objects.get(buttonType="save")
                        saveButton = ButtonText.objects.filter(
                            language=theLanguage, theButtonType=aButtonType)
                    except ObjectDoesNotExist:
                        searchButton = {"buttonText": "Save"}
                        comment.append("No save Button found")

                    context = {
                        'gdpr_check': gdpr_check,
                        'Title': faq.language.language,
                        'form': form,
                        'saveButton': saveButton,
                        'comment': comment,
                    }

                    return render(self.request, "moderator/mod_faq_update.html", context)
                except ObjectDoesNotExist:
                    messages.warning(
                        self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                    return redirect("moderator:faqs")
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:faqs")
        elif 'saveFAQ' in self.request.POST.keys():
            # establish the users language first, this should later have a check
            theLang = "Svenska"
            comment = []
            theLanguage = LanguageChoices.objects.get(
                language=theLang)
            if theLanguage == None:
                print("no language")
                return redirect("moderator:faqs")

            form = UpdateFAQ(self.request.POST)
            if form.is_valid():
                faqID = int(self.request.POST['check'])
                faq = FAQ.objects.get(id=faqID)
                faq.subject = form.cleaned_data.get('subject')
                faq.content = form.cleaned_data.get('content')
                faq.save()

                return redirect("moderator:faqs")
            else:
                messages.warning(
                    self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:faqs")
        else:
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:faqs")


class DeleteSpecificFAQView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        return redirect("moderator:faqs")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'deleteFAQ' in self.request.POST.keys():
            # establish the users language first, this should later have a check
            theLang = "Svenska"
            comment = []
            try:
                theLanguage = LanguageChoices.objects.get(
                    language=theLang)
            except ObjectDoesNotExist:
                return redirect("moderator:faqs")

            # text fields
            title = ""
            description = ""
            language = ""
            subject = ""
            content = ""
            try:
                textType = TextTypeChoices.objects.get(textType="title")
                atitle = TextField.objects.filter(
                    language=theLanguage, textType=textType, short_hand="deleteFAQ")
            except ObjectDoesNotExist:
                atitle = {"text": "Title"}
                comment.append("No title-textfield found")
            for t in atitle:
                title = t.text

            try:
                textType = TextTypeChoices.objects.get(textType="label")
                adescription = TextField.objects.filter(
                    language=theLanguage, textType=textType, short_hand="descriptionFAQ")
            except ObjectDoesNotExist:
                adescription = "Description"
                comment.append("No description-label found")
            for d in adescription:
                description = d.text

            try:
                textType = TextTypeChoices.objects.get(textType="label")
                alanguage = TextField.objects.filter(
                    language=theLanguage, textType=textType, short_hand="languageFAQ")
            except ObjectDoesNotExist:
                alanguage = "Language"
                comment.append("No Language-label found")
            for l in alanguage:
                language = l.text

            try:
                textType = TextTypeChoices.objects.get(textType="label")
                asubject = TextField.objects.filter(
                    language=theLanguage, textType=textType, short_hand="subjectFAQ")
            except ObjectDoesNotExist:
                asubject = "Subject"
                comment.append("No subject-label found")
            for s in asubject:
                subject = s.text

            try:
                textType = TextTypeChoices.objects.get(textType="label")
                acontent = TextField.objects.filter(
                    language=theLanguage, textType=textType, short_hand="contentFAQ")
            except ObjectDoesNotExist:
                acontent = "Content"
                comment.append("No content-label found")
            for c in acontent:
                content = c.text

            faqID = int(self.request.POST['deleteFAQ'])
            findTheDiscription = FAQ.objects.get(id=faqID)
            theDescription = findTheDiscription.description
            allFAQsWithDis = FAQ.objects.select_related(
                'language').filter(description=theDescription)

            try:
                aButtonType = ButtonType.objects.get(buttonType="delete")
                deleteButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=aButtonType)
            except ObjectDoesNotExist:
                deleteButton = {"buttonText": "delete"}
                comment.append("No save Button found")
            try:
                bButtonType = ButtonType.objects.get(buttonType="cancel")
                cancelButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=bButtonType)
            except ObjectDoesNotExist:
                cancelButton = {"buttonText": "cancel"}
                comment.append("No save Button found")

            context = {
                'gdpr_check': gdpr_check,
                'theTitle': title,
                'description': description,
                'language': language,
                'subject': subject,
                'content': content,
                'faqs': allFAQsWithDis,
                'theDescription': theDescription,
                'deleteButton': deleteButton,
                'cancelButton': cancelButton,
            }

            return render(self.request, "moderator/mod_faq_delete.html", context)

        elif 'delete' in self.request.POST.keys():
            theDescription = str(self.request.POST['desc'])

            try:
                faqs = FAQ.objects.filter(description=theDescription)
            except:
                return redirect("moderator:faqs")

            for faq in faqs:
                faq.delete()
            # info_message = get_message('info', code)
            messages.info(self.request, "FAQs borttagen")
            return redirect("moderator:faqs")

        elif 'cancel' in self.request.POST.keys():
            return redirect("moderator:faqs")
        else:
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:faqs")


class NewSpecificFAQView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # this shouldnt happen, send back to FAQS
        return redirect("moderator:faqs")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'createFAQ' in self.request.POST.keys():
            # establish the users language first, this should later have a check
            theLang = "Svenska"
            comment = []
            try:
                theLanguage = LanguageChoices.objects.get(
                    language=theLang)
                try:
                    textType = TextTypeChoices.objects.get(textType="title")
                    title = TextField.objects.filter(
                        language=theLanguage, textType=textType, short_hand="NewFAQ")
                except ObjectDoesNotExist:
                    title = {"text": "Title"}
                    comment.append("No title found")

                try:
                    form = NewFAQForm()
                    form.language(aLanguage=theLanguage)
                except ObjectDoesNotExist:
                    form = NewFAQForm()
                    comment.append("Form issue")

                try:
                    aButtonType = ButtonType.objects.get(buttonType="save")
                    saveButton = ButtonText.objects.filter(
                        language=theLanguage, theButtonType=aButtonType)
                except ObjectDoesNotExist:
                    searchButton = {"buttonText": "Save"}
                    comment.append("No save Button found")

                context = {
                    'gdpr_check': gdpr_check,
                    'theTitle': title,
                    'form': form,
                    'saveButton': saveButton,
                    'comment': comment,
                }

                return render(self.request, "moderator/mod_faq_new.html", context)
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:faqs")
        elif 'saveFAQ' in self.request.POST.keys():
            # establish the users language first, this should later have a check
            theLang = "Svenska"
            comment = []
            theLanguage = LanguageChoices.objects.get(
                language=theLang)
            try:
                theLanguage = LanguageChoices.objects.get(
                    language=theLang)
                form = NewFAQForm(self.request.POST)
                if form.is_valid():
                    faq = FAQ()
                    faq.description = form.cleaned_data.get('description')
                    faq.language = theLanguage
                    faq.subject = form.cleaned_data.get('subject')
                    faq.content = form.cleaned_data.get('content')
                    faq.save()
                    # info_message = get_message('info', code)
                    messages.info(self.request, "FAQs sparad")
                    return redirect("moderator:faqs")
                else:

                    try:
                        textType = TextTypeChoices.objects.get(
                            textType="title")
                        title = TextField.objects.filter(
                            language=theLanguage, textType=textType, short_hand="NewFAQ")
                    except ObjectDoesNotExist:
                        title = {"text": "Title"}
                        comment.append("No title found")

                    try:
                        form = NewFAQForm()
                        form.language(aLanguage=theLanguage)
                    except ObjectDoesNotExist:
                        form = NewFAQForm()
                        comment.append("Form issue")

                    try:
                        aButtonType = ButtonType.objects.get(buttonType="save")
                        saveButton = ButtonText.objects.filter(
                            language=theLanguage, theButtonType=aButtonType)
                    except ObjectDoesNotExist:
                        searchButton = {"buttonText": "Save"}
                        comment.append("No save Button found")

                    context = {
                        'gdpr_check': gdpr_check,
                        'theTitle': title,
                        'form': form,
                        'saveButton': saveButton,
                        'comment': comment,
                    }

                    return render(self.request, "moderator/mod_faq_new.html", context)

            except ObjectDoesNotExist:
                messages.warning(
                    self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
                return redirect("moderator:faqs")
        else:
            messages.warning(
                self.request, "Något gick fel. Om detta återupprepas kontakta IT supporten.")
            return redirect("moderator:faqs")

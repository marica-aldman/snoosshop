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


class Overview(View):
    def get(self, *args, **kwargs):
        try:

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

            # we are on the first page so set the page to that
            current_page_orders = 1

            context = {
                'orders': orders,
                'more_orders': more_orders,
                'current_page_orders': current_page_orders,
            }

            return render(self.request, "moderator/mod_overview.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 35)
            messages.warning(
                self.request, message)
            return redirect("core:home")

    def post(self, *args, **kwargs):
        try:
            # get where we are
            current_page_orders = int(self.request.POST['current_page_orders'])

            if 'whichPageOrder' in self.request.POST.keys():
                whichPageOrder = int(self.request.POST['whichPageOrder'])
                current_page_order = whichPageOrder

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
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'nextPageOrder' in self.request.POST.keys():

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
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

            elif 'previousPageOrder' in self.request.POST.keys():

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
                    'orders': orders,
                    'more_orders': more_orders,
                    'current_page_orders': current_page_orders,
                }

                return render(self.request, "moderator/mod_overview.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 42)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")


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
            message = get_message('error', 83)
            messages.warning(
                self.request, message)
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
            message = get_message('error', 84)
            messages.warning(
                self.request, message)
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
                    info_message = get_message('info', 38)
                    messages.info(
                        self.request, info_message)
                    return redirect("moderator:my_profile")
                except ObjectDoesNotExist:
                    info = UserInfo()
                    info.user = self.request.user
                    info.first_name = form.cleaned_data.get('first_name')
                    info.last_name = form.cleaned_data.get('last_name')
                    info.email = form.cleaned_data.get('email')
                    info.telephone = form.cleaned_data.get('telephone')

                    info.save()
                    info_message = get_message('info', 39)
                    return redirect("moderator:my_profile")
            else:

                context = {
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
                testP = int(p_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if testP != p_pages:
                    p_pages = int(p_pages)
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

            # onsubmit warning
            onsubmit = get_message('warning', 6)

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'products': products,
                'more_products': more_products,
                'form': form,
                'current_page': current_page,
                'max_pages': p_pages,
                'onsubmit': onsubmit,
            }

            return render(self.request, "moderator/mod_products.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 86)
            messages.warning(
                self.request, message)
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
                    # we only have one type of search for this we can only get one page.
                    product_id = int(self.request.POST['search_value'])

                    if product_id != 0:
                        # next page on a single user is the same as the search for single user
                        # get the user

                        try:
                            the_product = Item.objects.get(id=product_id)

                            # there is only one
                            p_pages = 1
                            more_products = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "productID"

                            # get the form
                            form = searchProductForm()
                            form.populate(product_id)
                            # onsubmit warning
                            onsubmit = get_message('warning', 6)

                            context = {
                                'search_type': search_type,
                                'search_value': product_id,
                                'multiple': multiple,
                                'product': the_product,
                                'more_products': more_products,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': p_pages,
                                'onsubmit': onsubmit,
                            }

                            return render(self.request, "moderator/mod_products.html", context)

                        except ObjectDoesNotExist:
                            info_message = get_message('info', 41)
                            messages.info(
                                self.request, info_message)
                            return redirect("moderator:products")
                    else:
                        # if the product id is 0 we are probably trying to reset the form
                        return redirect("moderator:products")

                else:
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
                            p_pages = 1
                            more_products = [{'number': 1}]
                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "productID"
                            # onsubmit warning
                            onsubmit = get_message('warning', 6)

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'product': product,
                                'more_products': more_products,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': p_pages,
                                'onsubmit': onsubmit,
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
                        # rerender page with error message
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
                            testP = int(p_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testP != p_pages:
                                p_pages = int(p_pages)
                                p_pages += 1

                        # create a list for a ul to work through

                        more_products = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(p_pages):
                            i += 1
                            more_products.append({'number': i})

                        # we already have the form

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"
                        # onsubmit warning
                        onsubmit = get_message('warning', 6)

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': p_pages,
                            'onsubmit': onsubmit,
                        }
                        if self.request.POST['product_id'] is not None:
                            message = get_message('error', 103)
                            messages.warning(
                                self.request, message)
                        return render(self.request, "moderator/mod_products.html", context)

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                try:
                    number_products = Item.objects.all(
                    ).count()
                    number_pages = number_products / 20
                    if current_page < number_pages:
                        current_page += 1
                    offset = current_page * 20
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
                    testP = int(p_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testP != p_pages:
                        p_pages = int(p_pages)
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
                # onsubmit warning
                onsubmit = get_message('warning', 6)

                context = {
                    'search_type': search_type,
                    'search_value': search_value,
                    'multiple': multiple,
                    'products': products,
                    'more_products': more_products,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': p_pages,
                    'onsubmit': onsubmit,
                }

                return render(self.request, "moderator/mod_products.html", context)

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what page
                if current_page > 2:

                    try:
                        if current_page > 1:
                            current_page -= 1
                        offset = current_page * 20
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
                            testP = int(p_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testP != p_pages:
                                p_pages = int(p_pages)
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
                        # onsubmit warning
                        onsubmit = get_message('warning', 6)

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': p_pages,
                            'onsubmit': onsubmit,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 87)
                        messages.warning(
                            self.request, message)
                        return redirect("moderator:products")

                else:

                    try:
                        if current_page > 1:
                            current_page -= 1
                        products = Item.objects.all()[:20]
                        number_products = Item.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        p_pages = 1

                        if number_products > 20:
                            # if there are more we divide by ten
                            p_pages = number_products / 20
                            # see if there is a decimal
                            testP = int(p_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testP != p_pages:
                                p_pages = int(p_pages)
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
                        # onsubmit warning
                        onsubmit = get_message('warning', 6)

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': p_pages,
                            'onsubmit': onsubmit,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 88)
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
                return redirect("moderator:categories")

        except ObjectDoesNotExist:
            message = get_message('error', 89)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")


class SpecificProductsView(View):
    def get(self, *args, **kwargs):
        message = get_message('error', 90)
        messages.warning(
            self.request, message)
        return redirect("moderator:products")

    def post(self, *args, **kwargs):
        if 'lookAtProduct' in self.request.POST.keys():
            try:
                product_id = int(self.request.POST['lookAtProduct'])

                # get the form
                form = editOrCreateProduct()
                form.populate(product_id)
                img_form = editProductImage()

                old = product_id

                # we need all possible categories

                category = 0
                categories = Category.objects.all()

                context = {
                    'form': form,
                    'img_form': img_form,
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
            img_form = editProductImage()

            old = 'new'

            # we need all possible categories
            category = 0
            categories = Category.objects.all()

            context = {
                'form': form,
                'old': old,
                'img_form': img_form,
                'category': category,
                'categories': categories,
            }

            return render(self.request, "moderator/mod_single_product.html", context)

        elif 'saveProduct' in self.request.POST.keys():

            form = editOrCreateProduct(self.request.POST)
            img_form = editProductImage(self.request.POST)

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
                    if img_form.is_valid():
                        product.image = img_form.cleaned_data.get('image')
                    if 'category' in self.request.POST.keys():
                        category_id = int(self.request.POST['category'])
                        category = Category.objects.get(id=category_id)
                        product.category = category

                    # save

                    product.save()

                    product.slug = product.title + str(product.id)

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
                    if img_form.is_valid():
                        product.image = img_form.cleaned_data.get('image')
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
                    'form': form,
                    'img_form': img_form,
                    'old': old,
                    'category': category,
                    'categories': categories,
                }

                return render(self.request, "moderator/mod_single_product.html", context)


class CategoriesView(View):
    def get(self, *args, **kwargs):
        try:
            # get the first 20 categories and a count of all products
            categories = Category.objects.all()[:20]
            number_categories = Category.objects.all().count()
            # figure out how many pages of 20 there are
            # if there are only 20 or fewer pages will be 1

            c_pages = 1

            if number_categories > 20:
                # if there are more we divide by ten
                c_pages = number_categories / 20
                # see if there is a decimal
                testC = int(c_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if testC != c_pages:
                    c_pages = int(c_pages)
                    c_pages += 1

            # create a list for a ul to work through

            more_categories = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(c_pages):
                i += 1
                more_categories.append({'number': i})

            # make search for specific category

            form = searchCategoryForm()

            # set current page to 1
            current_page = 1

            # set a bool to check if we are showing one or multiple categories

            multiple = True

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = "None"

            # delete warning
            onsubmit = get_message('warning', 4)

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'categories': categories,
                'more_categories': more_categories,
                'form': form,
                'current_page': current_page,
                'max_pages': c_pages,
                'onsubmit': onsubmit,
            }

            return render(self.request, "moderator/mod_categories.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 96)
            messages.warning(
                self.request, message)
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
                    # we only have one type of search for this we can only get one page.
                    category_id = int(self.request.POST['search_value'])

                    if category_id != 0:
                        # next page on a single user is the same as the search for single user
                        # get the user

                        try:
                            the_category = Category.objects.get(id=category_id)

                            # there is only one
                            c_pages = 1
                            more_categories = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "categoryID"

                            # form

                            form = searchCategoryForm()
                            form.populate(category_id)
                            onsubmit = get_message('warning', 4)

                            context = {
                                'search_type': search_type,
                                'search_value': category_id,
                                'multiple': multiple,
                                'category': the_category,
                                'more_categories': more_categories,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': c_pages,
                                'onsubmit': onsubmit,
                            }

                            return render(self.request, "moderator/mod_categories.html", context)

                        except ObjectDoesNotExist:
                            info_message = get_message('info', 44)
                            messages.info(
                                self.request, info_message)
                            return redirect("moderator:categories")
                    else:
                        # if the product id is 0 we are probably trying to reset the form
                        return redirect("moderator:categories")

                else:
                    # make a form and populate so we can clean the data
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
                            more_categories = [{'number': 1}]
                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "categoryID"
                            onsubmit = get_message('warning', 4)

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'category': category,
                                'more_categories': more_categories,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': c_pages,
                                'onsubmit': onsubmit,
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
                        # rerender page with error message
                        # get the first 20 categories and a count of all categories
                        categories = Category.objects.all()[:20]
                        number_categories = Category.objects.all().count()
                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        c_pages = 1

                        if number_categories > 20:
                            # if there are more we divide by ten
                            c_pages = number_categories / 20
                            # see if there is a decimal
                            testC = int(c_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testC != c_pages:
                                c_pages = int(c_pages)
                                c_pages += 1

                        # create a list for a ul to work through

                        more_categories = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(c_pages):
                            i += 1
                            more_categories.append({'number': i})

                        # we already have the form

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        onsubmit = get_message('warning', 4)

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                            'onsubmit': onsubmit,
                        }

                        if self.request.POST['category_id'] != "":
                            message = get_message('error', 97)
                            messages.warning(
                                self.request, message)
                        return render(self.request, "moderator/mod_categories.html", context)

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                try:
                    number_categories = Category.objects.all(
                    ).count()
                    number_pages = number_categories / 20
                    if current_page < number_pages:
                        current_page += 1
                    offset = current_page * 20
                    categories = Category.objects.all()[20:offset]
                except ObjectDoesNotExist:
                    categories = {}
                    number_categories = 0

                # figure out how many pages of 20 there are
                # if there are only 20 or fewer pages will be 1

                c_pages = 1

                if number_categories > 20:
                    # if there are more we divide by ten
                    c_pages = number_categories / 20
                    # see if there is a decimal
                    testC = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testC != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1

                # create a list for a ul to work through

                more_categories = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(c_pages):
                    i += 1
                    more_categories.append({'number': i})

                # make search for specific order or customer

                form = searchCategoryForm()

                # set a bool to check if we are showing one or multiple orders

                multiple = True

                # set the hidden value for wether or not we have done a search

                search_type = "None"
                search_value = "None"

                onsubmit = get_message('warning', 4)

                context = {
                    'search_type': search_type,
                    'search_value': search_value,
                    'multiple': multiple,
                    'categories': categories,
                    'more_categories': more_categories,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': c_pages,
                    'onsubmit': onsubmit,
                }

                return render(self.request, "moderator/mod_categories.html", context)

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what page
                if current_page > 2:

                    try:
                        if current_page > 1:
                            current_page -= 1
                        offset = current_page * 20
                        categories = Category.objects.all()[20:offset]
                        number_categories = Category.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        c_pages = 1

                        if number_categories > 20:
                            # if there are more we divide by ten
                            c_pages = number_categories / 20
                            # see if there is a decimal
                            testC = int(c_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testC != c_pages:
                                c_pages = int(c_pages)
                                c_pages += 1

                        # create a list for a ul to work through

                        more_categories = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(c_pages):
                            i += 1
                            more_categories.append({'number': i})

                        # make search for specific order or customer

                        form = searchCategoryForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"
                        onsubmit = get_message('warning', 4)

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                            'onsubmit': onsubmit,
                        }

                        return render(self.request, "moderator/mod_categories.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 98)
                        messages.warning(
                            self.request, message)
                        return redirect("moderator:categories")

                else:

                    try:
                        if current_page > 1:
                            current_page -= 1
                        categories = Category.objects.all()[:20]
                        number_categories = Category.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        c_pages = 1

                        if number_categories > 20:
                            # if there are more we divide by ten
                            p_pages = number_categories / 20
                            # see if there is a decimal
                            testC = int(c_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testC != c_pages:
                                c_pages = int(c_pages)
                                c_pages += 1

                        # create a list for a ul to work through

                        more_categories = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(c_pages):
                            i += 1
                            more_categories.append({'number': i})

                        # make search for specific order or customer

                        form = searchCategoryForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"
                        onsubmit = get_message('warning', 4)

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                            'onsubmit': onsubmit,
                        }

                        return render(self.request, "moderator/mod_categories.html", context)

                    except ObjectDoesNotExist:
                        message = get_message('error', 99)
                        messages.warning(
                            self.request, message)
                        return redirect("moderator:categories")

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
            else:
                return redirect("moderator:categories")

        except ObjectDoesNotExist:
            message = get_message('error', 100)
            messages.warning(
                self.request, message)
            return redirect("moderator:overview")


class SpecificCategoryView(View):
    def get(self, *args, **kwargs):
        message = get_message('error', 104)
        messages.warning(
            self.request, message)
        return redirect("moderator:categories")

    def post(self, *args, **kwargs):
        if 'lookAtCategory' in self.request.POST.keys():
            category_id = int(self.request.POST['lookAtCategory'])

            # get the form

            form = editOrCreateCategory()
            form.populate(category_id)

            old = category_id

            context = {
                'form': form,
                'old': old,
            }

            return render(self.request, "moderator/mod_single_category.html", context)

        elif 'new' in self.request.POST.keys():

            form = editOrCreateCategory()

            old = 'new'

            context = {
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


class OrderHandlingView(View):
    def get(self, *args, **kwargs):
        # display all unsent orders, oldest first
        # first get the constants
        # get max pages regular orders
        r_pages = 1
        reg_orders = Order.objects.filter(
            ordered=True, being_delivered=False, subscription_order=False).order_by('id')
        number_reg_orders = reg_orders.count()

        if number_reg_orders > 10:
            # if there are more we divide by ten
            r_pages = number_reg_orders / 10
            # see if there is a decimal
            testR = int(r_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testR != r_pages:
                r_pages = int(r_pages)
                r_pages += 1
        # get max pages subscription orders
        s_pages = 1
        sub_orders = Order.objects.filter(
            being_delivered=False, subscription_order=True)
        number_sub_orders = sub_orders.count()

        if number_sub_orders > 10:
            # if there are more we divide by ten
            s_pages = number_sub_orders / 10
            # see if there is a decimal
            testS = int(s_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testS != s_pages:
                s_pages = int(s_pages)
                s_pages += 1
        try:
            reg_orders = Order.objects.filter(
                ordered=True, being_delivered=False, subscription_order=False).order_by('id')[:10]
            info1 = ""
        except ObjectDoesNotExist:
            reg_orders = {}
            info1 = get_message('info', 49)

        # create a list for a ul to work through

        more_reg_orders = []

        i = 0
        # populate the list with the amount of pages there are
        for i in range(r_pages):
            i += 1
            more_reg_orders.append({'number': i})

        # current page for regular

        r_current_page = 1

        try:
            sub_orders = Order.objects.filter(
                being_delivered=False, subscription_order=True).order_by('sub_out_date')[:10]
            info2 = ""
        except ObjectDoesNotExist:
            sub_orders = {}
            info2 = get_message('info', 50)

        # create a list for a ul to work through

        more_sub_orders = []

        i = 0
        # populate the list with the amount of pages there are
        for i in range(s_pages):
            i += 1
            more_sub_orders.append({'number': i})

        # sub current page

        s_current_page = 1

        # make search form for specific order or customer

        form = searchOrderForm()

        # set the hidden value for wether or not we have done a search

        search_type = "None"
        search_value = "None"

        context = {
            'form': form,
            'search_type': search_type,
            'search_value': search_value,
            'reg_orders': reg_orders,
            'sub_orders': sub_orders,
            'rmax': r_pages,
            'r_current_page': r_current_page,
            'more_reg_orders': more_reg_orders,
            's_current_page': s_current_page,
            'more_sub_orders': more_sub_orders,
            'smax': s_pages,
        }

        if info1 != "":
            messages.info(self.request, info1)
        if info2 != "":
            messages.info(self.request, info2)

        return render(self.request, "moderator/mod_orderhandling.html", context)

    def post(self, *args, **kwargs):
        # set the search type and value here before we go into the rest
        search_type = "None"
        search_value = "None"
        if 'search_type' in self.request.POST.keys():
            search_type = int(self.request.POST['search_type'])
        if 'search_value' in self.request.POST.keys():
            search_value = int(self.request.POST['search_value'])
        # handle status change and pagination
        r_current_page = int(self.request.POST['r_current_page'])
        s_current_page = int(self.request.POST['s_current_page'])
        # get max pages regurlar orders
        r_pages = 1
        number_reg_orders = Order.objects.filter(
            ordered=True, being_delivered=False, subscription_order=False).count()

        if number_reg_orders > 10:
            # if there are more we divide by ten
            r_pages = number_reg_orders / 10
            # see if there is a decimal
            testR = int(r_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testR != r_pages:
                r_pages = int(r_pages)
                r_pages += 1

        # get max pages subscription orders
        s_pages = 1
        number_sub_orders = Order.objects.filter(
            being_delivered=False, subscription_order=True).count()

        if number_sub_orders > 10:
            # if there are more we divide by ten
            s_pages = number_sub_orders / 10
            # see if there is a decimal
            testS = int(s_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testS != s_pages:
                s_pages = int(s_pages)
                s_pages += 1
        if 'search' in self.request.POST.keys() and self.request.POST['search'] != "None":
            if not 'previousPageRegOrder' in self.request.POST.keys() or not 'nextPageRegOrder' in self.request.POST.keys() or not 'r_page' in self.request.POST.keys() or not 'previousPageSubOrder' in self.request.POST.keys() or not 'nextPageSubOrder' in self.request.POST.keys() or not 's_page' in self.request.POST.keys():
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
                        r_pages = 1
                        reg_orders = Order.objects.filter(
                            ref_code=search_value, subscription_order=False).order_by('id')
                        number_reg_orders = 1
                        r_pages = 1

                        # create a list for a ul to work through

                        more_reg_orders = [{'number': 1}]

                        # current page for regular

                        r_current_page = 1

                        # get max pages subscription orders
                        s_pages = 1
                        sub_orders = Order.objects.filter(
                            ref_code=search_value, subscription_order=True).order_by('id')
                        number_sub_orders = 1

                        # create a list for a ul to work through

                        more_sub_orders = [{'number': 1}]

                        # current page for regular

                        s_current_page = 1

                        # set the search type

                        search_type = "Reference"

                        context = {
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'reg_orders': reg_orders,
                            'sub_orders': sub_orders,
                            'rmax': r_pages,
                            'r_current_page': r_current_page,
                            'more_reg_orders': more_reg_orders,
                            's_current_page': s_current_page,
                            'more_sub_orders': more_sub_orders,
                            'smax': s_pages,
                        }

                        return render(self.request, "moderator/mod_orderhandling.html", context)

                    elif order_id != None:
                        # search done on order reference
                        search_value = order_id
                        # display all unsent orders, oldest first
                        # first get the constants
                        # get max pages regular orders
                        r_pages = 1
                        reg_orders = Order.objects.filter(
                            id=search_value, subscription_order=False).order_by('id')
                        number_reg_orders = 1
                        r_pages = 1

                        # create a list for a ul to work through

                        more_reg_orders = [{'number': 1}]

                        # current page for regular

                        r_current_page = 1

                        # get max pages subscription orders
                        s_pages = 1
                        sub_orders = Order.objects.filter(
                            id=search_value, subscription_order=True).order_by('id')
                        number_sub_orders = 1

                        # create a list for a ul to work through

                        more_sub_orders = [{'number': 1}]

                        # current page for regular

                        s_current_page = 1

                        # set the search type

                        search_type = "Reference"

                        context = {
                            'form': form,
                            'search_type': search_type,
                            'search_value': search_value,
                            'reg_orders': reg_orders,
                            'sub_orders': sub_orders,
                            'rmax': r_pages,
                            'r_current_page': r_current_page,
                            'more_reg_orders': more_reg_orders,
                            's_current_page': s_current_page,
                            'more_sub_orders': more_sub_orders,
                            'smax': s_pages,
                        }

                        return render(self.request, "moderator/mod_orderhandling.html", context)
                    else:
                        message = get_message('error', 117)
                        messages.warning(
                            self.request, message)
                        return redirect("moderator:orderhandling")
            else:
                # this should never happen
                return redirect("moderator:orderhandling")
        elif 'previousPageRegOrder' in self.request.POST.keys():
            if r_current_page >= 2:
                r_current_page -= 1
        elif 'nextPageRegOrder' in self.request.POST.keys():
            if r_current_page < r_pages:
                r_current_page += 1
        elif 'r_page' in self.request.POST.keys():
            page = int(self.request.POST['r_page'])
            if page <= r_pages:
                r_current_page = page
        elif 'previousPageSubOrder' in self.request.POST.keys():
            if s_current_page >= 2:
                s_current_page -= 1
        elif 'nextPageSubOrder' in self.request.POST.keys():
            if s_current_page < s_pages:
                s_current_page += 1
        elif 's_page' in self.request.POST.keys():
            page = int(self.request.POST['s_page'])
            if page <= s_pages:
                s_current_page = page
        else:
            # bugg handle this
            test = ""

        # after all these we need display the page again but with the current pages set correctly this will differ if we or have paged.

        reg_orders = {}
        info1 = ""
        if r_current_page > 1:
            try:
                offset = r_current_page * 10
                reg_orders = Order.objects.filter(
                    ordered=True, being_delivered=False, subscription_order=False).order_by('id')[10:offset]
            except ObjectDoesNotExist:
                # no orders left to complete
                info1 = get_message('info', 49)
        else:
            try:
                reg_orders = Order.objects.filter(
                    ordered=True, being_delivered=False, subscription_order=False).order_by('id')[:10]
            except ObjectDoesNotExist:
                # no orders left to complete
                info1 = get_message('info', 49)

        # create a list for a ul to work through

        more_reg_orders = []

        i = 0
        # populate the list with the amount of pages there are
        for i in range(r_pages):
            i += 1
            more_reg_orders.append({'number': i})

        date = datetime.now()
        sub_orders = {}
        info2 = ""
        if s_current_page > 1:
            try:
                offset = s_current_page * 10
                sub_orders = Order.objects.filter(
                    being_delivered=False, subscription_order=True).order_by('sub_out_date')[10:offset]
            except ObjectDoesNotExist:
                # no orders left to complete
                info2 = get_message('info', 50)
        else:
            try:
                # get todays date
                sub_orders = Order.objects.filter(
                    being_delivered=False, subscription_order=True).order_by('sub_out_date')[:10]
            except ObjectDoesNotExist:
                # no orders left to complete
                info2 = get_message('info', 50)

        # create a list for a ul to work through

        more_sub_orders = []

        i = 0
        # populate the list with the amount of pages there are
        for i in range(s_pages):
            i += 1
            more_sub_orders.append({'number': i})
        # make search form for specific order or customer

        form = searchOrderForm()

        context = {
            'form': form,
            'search_type': search_type,
            'search_value': search_value,
            'reg_orders': reg_orders,
            'sub_orders': sub_orders,
            'rmax': r_pages,
            'r_current_page': r_current_page,
            'more_reg_orders': more_reg_orders,
            's_current_page': s_current_page,
            'more_sub_orders': more_sub_orders,
            'smax': s_pages,
        }

        if info1 != "":
            messages.info(self.request, info1)
        if info2 != "":
            messages.info(self.request, info2)

        return render(self.request, "moderator/mod_orderhandling.html", context)


class SpecificOrderHandlingView(View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 105)
        messages.warning(
            self.request, message)
        return redirect("moderator:orderhandling")

    def post(self, *args, **kwargs):
        if 'lookAtOrder' in self.request.POST.keys():
            order_id = int(self.request.POST['lookAtOrder'])
            try:
                order = Order.objects.get(id=order_id)
                order.being_read = True
                order.updated_date = make_aware(datetime.now())
                order.save()
                orderItems = order.items.all()
                path = self.request.get_full_path()
            except ObjectDoesNotExist:
                message = get_message('error', 106)
                messages.warning(
                    self.request, message)
                return redirect("moderator:orderhandling")
            context = {
                'path': path,
                'order': order,
                'orderItems': orderItems,
            }

            return render(self.request, "moderator/specificOrder.html", context)
        if 'send' in self.request.POST.keys():
            order_id = int(self.request.POST['send'])

            try:
                order = Order.objects.get(id=order_id)
                order.being_delivered = True
                order.being_read = False
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

                if order.subscription_order and order.comment != 'Partial' and order.comment != 'Nothing':
                    sub = Subscription.objects.get(next_order=order.id)
                    sub.next_order_date = get_next_order_date(
                        make_aware(datetime.now()), sub.intervall)
                    sub.updated_date = make_aware(datetime.now())

                    # create a new order for this sub
                    new_order = Order()
                    new_order.user = sub.user

                    # create a reference code and check that there isnt already one before setting the orders ref code to the code
                    refcode = create_ref_code()
                    ref_test = True

                    while ref_test:
                        try:
                            testOrder = Order.objects.get(ref_code=refcode)
                            refcode = create_ref_code()
                        except ObjectDoesNotExist:
                            ref_test = False
                    total_order_price = 0
                    new_order.ref_code = refcode
                    new_order.total_price = order.total_price
                    new_order.freight = order.freight
                    new_order.sub_out_date = sub.next_order_date
                    new_order.ordered_date = make_aware(datetime.now())
                    new_order.updated_date = make_aware(datetime.now())
                    new_order.ordered = True
                    new_order.subscription_order = True
                    new_order.being_read = False
                    new_order.shipping_address = order.shipping_address
                    new_order.billing_address = order.billing_address
                    new_order.payment_type = order.payment_type
                    new_order.coupon = order.coupon
                    new_order.save()
                    sub.next_order = new_order.id

                    # get the subitems
                    subItems = SubscriptionItem.objects.filter(
                        subscription=sub)

                    # create order items from sub items
                    for subItem in subItems:
                        # saving subscription and order items
                        orderItem = save_orderItem(subItem)
                        new_order.items.add(orderItem)
                        total_order_price = total_order_price + orderItem.total_price
                    new_order.total_price = total_order_price + new_order.freight
                    new_order.save()
                order.comment = ""
                order.save()

                if order.being_delivered:
                    info_message = get_message('info', 51)
                    messages.info(
                        self.request, info_message)
                else:
                    message = get_message('error', 108)
                    messages.warning(
                        self.request, message)

                return redirect("moderator:orderhandling")
            except ObjectDoesNotExist:
                message = get_message('error', 106)
                messages.warning(
                    self.request, message)
                return redirect("moderator:orderhandling")
        elif 'back' in self.request.POST.keys():
            order = Order.objects.get(id=int(self.request.POST['back']))
            order.being_read = False
            order.save()
            return redirect("moderator:orderhandling")
        else:
            # something wrong redirect
            message = get_message('error', 107)
            messages.warning(
                self.request, message)
            return redirect("moderator:orderhandling")


class FreightView(View):
    def get(self, *args, **kwargs):
        # get the 20 first current freights
        freights = Freight.objects.all().order_by('title')[:20]
        number_of_freights = Freight.objects.all().count()

        f_pages = 1

        if number_of_freights > 20:
            # if there are more we divide by 20
            f_pages = number_of_freights / 20
            # see if there is a decimal
            testO = int(f_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testO != f_pages:
                f_pages = int(f_pages)
                f_pages += 1

        # create a list for a ul to work through

        more_freights = []

        i = 0
        # populate the list with the amount of pages there are
        for i in range(f_pages):
            i += 1
            more_freights.append({'number': i})

        # make an empty freight for the new form
        freight = Freight()
        # search form
        form = searchFreightForm()

        # set current page, search type and search_value to start values
        current_page = 1
        search_type = "None"
        search_value = "None"

        onSubmit = get_message('warning', 5)

        context = {
            'freights': freights,
            'freight': freight,
            'form': form,
            'current_page': current_page,
            'search_type': search_type,
            'search_value': search_value,
            'more_freights': more_freights,
            'max_pages': f_pages,
            'onSubmit': onSubmit,
        }

        return render(self.request, "moderator/mod_freights.html", context)

    def post(self, *args, **kwargs):
        if 'delete' in self.request.POST.keys():
            # delete freight
            # get id
            freight_id = int(self.request.POST['delete'])
            freight = Freight.objects.get(id=freight_id)
            freight.delete()
            info_message = get_message('info', 76)
            messages.info(self.request, info_message)
            return redirect("moderator:freights")
        elif 'previousPage' in self.request.POST.keys():
            if 'search_type' in self.request.POST.keys() and 'search_value' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = int(self.request.POST['search_type'])
                search_value = int(self.request.POST['search_value'])
                current_page = int(self.request.POST['current_page'])

                if current_page >= 2:
                    # get the right 20 freights
                    current_page -= 1
                    offset = current_page
                    freights = Freight.objects.all().order_by('title')[
                        20:offset]
                    number_of_freights = Freight.objects.all().count()

                    f_pages = 1

                    if number_of_freights > 20:
                        # if there are more we divide by 20
                        f_pages = number_of_freights / 20
                        # see if there is a decimal
                        testO = int(f_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testO != f_pages:
                            f_pages = int(f_pages)
                            f_pages += 1

                    # create a list for a ul to work through

                    more_freights = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(f_pages):
                        i += 1
                        more_freights.append({'number': i})

                    # make an empty freight for the new form
                    freight = Freight()
                    # search form
                    form = searchFreightForm()
                    onSubmit = get_message('warning', 5)

                    context = {
                        'freights': freights,
                        'freight': freight,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_freights': more_freights,
                        'max_pages': f_pages,
                        'onSubmit': onSubmit,
                    }

                    return render(self.request, "moderator/mod_freights.html", context)
                if current_page == 1:
                    # this shouldnt happen but to make sure
                    # get the right 20 freights
                    freights = Freight.objects.all().order_by('title')[:20]
                    number_of_freights = Freight.objects.all().count()

                    f_pages = 1

                    if number_of_freights > 20:
                        # if there are more we divide by 20
                        f_pages = number_of_freights / 20
                        # see if there is a decimal
                        testO = int(f_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testO != f_pages:
                            f_pages = int(f_pages)
                            f_pages += 1

                    # create a list for a ul to work through

                    more_freights = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(f_pages):
                        i += 1
                        more_freights.append({'number': i})

                    # make an empty freight for the new form
                    freight = Freight()
                    # search form
                    form = searchFreightForm()
                    onSubmit = get_message('warning', 5)

                    context = {
                        'freights': freights,
                        'freight': freight,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_freights': more_freights,
                        'max_pages': f_pages,
                        'onSubmit': onSubmit,
                    }

                    return render(self.request, "moderator/mod_freights.html", context)
        elif 'page' in self.request.POST.keys():
            if 'search_type' in self.request.POST.keys() and 'search_value' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = int(self.request.POST['search_type'])
                search_value = int(self.request.POST['search_value'])
                current_page = int(self.request.POST['current_page'])
                page = int(self.request.POST['page'])

                # we need the max pages first

                number_of_freights = Freight.objects.all().count()

                f_pages = 1

                if number_of_freights > 20:
                    # if there are more we divide by 20
                    f_pages = number_of_freights / 20
                    # see if there is a decimal
                    testO = int(f_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testO != f_pages:
                        f_pages = int(f_pages)
                        f_pages += 1

                if page == 1:
                    freights = Freight.objects.all().order_by('title')[
                        :20]
                    # create a list for a ul to work through

                    more_freights = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(f_pages):
                        i += 1
                        more_freights.append({'number': i})

                    # make an empty freight for the new form
                    freight = Freight()
                    # search form
                    form = searchFreightForm()
                    onSubmit = get_message('warning', 5)

                    context = {
                        'freights': freights,
                        'freight': freight,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_freights': more_freights,
                        'max_pages': f_pages,
                        'onSubmit': onSubmit,
                    }

                    return render(self.request, "moderator/mod_freights.html", context)
                elif page > f_pages:
                    page = f_pages

                # get the right 20 freights
                offset = page
                freights = Freight.objects.all().order_by('title')[
                    20:offset]

                # create a list for a ul to work through

                more_freights = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(f_pages):
                    i += 1
                    more_freights.append({'number': i})

                # make an empty freight for the new form
                freight = Freight()
                # search form
                form = searchFreightForm()

                current_page = page
                onSubmit = get_message('warning', 5)

                context = {
                    'freights': freights,
                    'freight': freight,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_freights': more_freights,
                    'max_pages': f_pages,
                    'onSubmit': onSubmit,
                }

                return render(self.request, "moderator/mod_freights.html", context)

        elif 'nextPage' in self.request.POST.keys():
            if 'search_type' in self.request.POST.keys() and 'search_value' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = int(self.request.POST['search_type'])
                search_value = int(self.request.POST['search_value'])
                current_page = int(self.request.POST['current_page'])

                # first we need the max amount of pages

                number_of_freights = Freight.objects.all().count()

                f_pages = 1

                if number_of_freights > 20:
                    # if there are more we divide by 20
                    f_pages = number_of_freights / 20
                    # see if there is a decimal
                    testO = int(f_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testO != f_pages:
                        f_pages = int(f_pages)
                        f_pages += 1

                if current_page < f_pages:
                    current_page += 1

                offset = current_page
                freights = Freight.objects.all().order_by('title')[
                    20:offset]

                # create a list for a ul to work through

                more_freights = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(f_pages):
                    i += 1
                    more_freights.append({'number': i})

                # make an empty freight for the new form
                freight = Freight()
                # search form
                form = searchFreightForm()
                onSubmit = get_message('warning', 5)

                context = {
                    'freights': freights,
                    'freight': freight,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_freights': more_freights,
                    'max_pages': f_pages,
                    'onSubmit': onSubmit,
                }

                return render(self.request, "moderator/mod_freights.html", context)
        elif 'search' in self.request.POST.keys():
            # get the 20 first current freights
            if 'freight_id' in self.request.POST.keys():
                freight_id = int(self.request.POST['freight_id'])
                freights = Freight.objects.filter(id=freight_id)
                f_pages = 1
                more_freights = [{'number': 1}]

                # make an empty freight for the new form
                freight = Freight()
                # search form
                form = searchFreightForm()
                form.populate(freight_id)
                current_page = 1
                search_type = "freight_id"
                search_value = freight_id
                onSubmit = get_message('warning', 5)

                context = {
                    'freights': freights,
                    'freight': freight,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_freights': more_freights,
                    'max_pages': f_pages,
                    'onSubmit': onSubmit,
                }

            return render(self.request, "moderator/mod_freights.html", context)


class SpecificFreightView(View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 8)
        messages.warning(
            self.request, message)
        return redirect("moderator:freights")

    def post(self, *args, **kwargs):
        if 'see' in self.request.POST.keys():
            # get the id
            freight_id = int(self.request.POST['see'])
            # get freight form
            form = freightForm()
            form.populate(freight_id)
            context = {
                'form': form,
                'new': False,
                'freight': freight_id,
            }

            return render(self.request, "moderator/mod_single_freight.html", context)
        elif 'new' in self.request.POST.keys():
            # get freight form
            form = freightForm()

            context = {
                'form': form,
                'new': True,
                'freight': '',
            }

            return render(self.request, "moderator/mod_single_freight.html", context)
        elif 'saveOld' in self.request.POST.keys():
            # get the id
            freight_id = int(self.request.POST['saveOld'])
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
                freight.save()
                info_message = get_message('info', 74)
                messages.info(self.request, info_message)
                return redirect("moderator:freights")
            else:
                context = {
                    'form': form,
                    'new': False,
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
                    'form': form,
                    'new': True,
                    'freight': '',
                }
                message = get_message('error', 116)
                messages.warning(
                    self.request, message)
                return render(self.request, "moderator/mod_single_freight.html", context)
        else:
            return redirect("moderator:freights")


class CouponsView(View):
    def get(self, *args, **kwargs):
        # get the 20 first current freights
        coupons = Coupon.objects.all().order_by('code')[:20]
        number_of_coupons = Coupon.objects.all().count()

        c_pages = 1

        if number_of_coupons > 20:
            # if there are more we divide by 20
            c_pages = number_of_coupons / 20
            # see if there is a decimal
            testC = int(c_pages)
            # if there isn't an even number of ten make an extra page for the last group
            if testC != c_pages:
                c_pages = int(c_pages)
                c_pages += 1

        # create a list for a ul to work through

        more_coupons = []

        i = 0
        # populate the list with the amount of pages there are
        for i in range(c_pages):
            i += 1
            more_coupons.append({'number': i})

        # make an empty coupon for the new form
        coupon = Coupon()
        # search form
        form = searchCouponForm()

        # set current page, search type and search_value to start values
        current_page = 1
        search_type = "None"
        search_value = "None"

        onSubmit = get_message('warning', 7)

        context = {
            'coupons': coupons,
            'coupon': coupon,
            'form': form,
            'current_page': current_page,
            'search_type': search_type,
            'search_value': search_value,
            'more_coupons': more_coupons,
            'max_pages': c_pages,
            'onSubmit': onSubmit,
        }

        return render(self.request, "moderator/mod_coupons.html", context)

    def post(self, *args, **kwargs):
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
            if 'search_type' in self.request.POST.keys() and 'search_value' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = int(self.request.POST['search_type'])
                search_value = int(self.request.POST['search_value'])
                current_page = int(self.request.POST['current_page'])

                if current_page >= 2:
                    # get the right 20 coupons
                    current_page -= 1
                    offset = current_page
                    coupons = Coupon.objects.all().order_by('code')[
                        20:offset]
                    number_of_coupons = Coupon.objects.all().count()

                    c_pages = 1

                    if number_of_coupons > 20:
                        # if there are more we divide by 20
                        c_pages = number_of_coupons / 20
                        # see if there is a decimal
                        testO = int(c_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testO != c_pages:
                            c_pages = int(c_pages)
                            c_pages += 1

                    # create a list for a ul to work through

                    more_coupons = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(c_pages):
                        i += 1
                        more_coupons.append({'number': i})

                    # make an empty coupon for the new form
                    coupon = Coupon()
                    # search form
                    form = searchCouponForm()
                    onSubmit = get_message('warning', 7)

                    context = {
                        'coupons': coupons,
                        'coupon': coupon,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_coupons': more_coupons,
                        'max_pages': c_pages,
                        'onSubmit': onSubmit,
                    }

                    return render(self.request, "moderator/mod_coupons.html", context)
                if current_page == 1:
                    # this shouldnt happen but to make sure
                    # get the right 20 coupons
                    coupons = Coupon.objects.all().order_by('code')[:20]
                    number_of_coupons = Coupon.objects.all().count()

                    c_pages = 1

                    if number_of_coupons > 20:
                        # if there are more we divide by 20
                        c_pages = number_of_coupons / 20
                        # see if there is a decimal
                        testO = int(c_pages)
                        # if there isn't an even number of ten make an extra page for the last group
                        if testO != c_pages:
                            c_pages = int(c_pages)
                            c_pages += 1

                    # create a list for a ul to work through

                    more_coupons = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(c_pages):
                        i += 1
                        more_coupons.append({'number': i})

                    # make an empty coupon for the new form
                    coupon = Coupon()
                    # search form
                    form = searchCouponForm()
                    onSubmit = get_message('warning', 7)

                    context = {
                        'coupons': coupons,
                        'coupon': coupon,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_coupons': more_coupons,
                        'max_pages': c_pages,
                        'onSubmit': onSubmit,
                    }

                    return render(self.request, "moderator/mod_coupons.html", context)
        elif 'page' in self.request.POST.keys():
            if 'search_type' in self.request.POST.keys() and 'search_value' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = int(self.request.POST['search_type'])
                search_value = int(self.request.POST['search_value'])
                current_page = int(self.request.POST['current_page'])
                page = int(self.request.POST['page'])

                # we need the max pages first

                number_of_coupons = Coupon.objects.all().count()

                c_pages = 1

                if number_of_coupons > 20:
                    # if there are more we divide by 20
                    c_pages = number_of_coupons / 20
                    # see if there is a decimal
                    testO = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testO != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1

                if page == 1:
                    coupons = Coupon.objects.all().order_by('code')[
                        :20]
                    # create a list for a ul to work through

                    more_coupons = []

                    i = 0
                    # populate the list with the amount of pages there are
                    for i in range(c_pages):
                        i += 1
                        more_coupons.append({'number': i})

                    # make an empty coupon for the new form
                    coupon = Coupon()
                    # search form
                    form = searchCouponForm()
                    onSubmit = get_message('warning', 7)

                    context = {
                        'coupons': coupons,
                        'coupon': coupon,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'search_value': search_value,
                        'more_coupons': more_coupons,
                        'max_pages': c_pages,
                        'onSubmit': onSubmit,
                    }

                    return render(self.request, "moderator/mod_coupons.html", context)
                elif page > c_pages:
                    page = c_pages

                # get the right 20 coupons
                offset = page
                coupons = Coupon.objects.all().order_by('code')[
                    20:offset]

                # create a list for a ul to work through

                more_coupons = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(c_pages):
                    i += 1
                    more_coupons.append({'number': i})

                # make an empty coupon for the new form
                coupon = Coupon()
                # search form
                form = searchCouponForm()

                current_page = page
                onSubmit = get_message('warning', 7)

                context = {
                    'coupons': coupons,
                    'coupon': coupon,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_coupons': more_coupons,
                    'max_pages': c_pages,
                    'onSubmit': onSubmit,
                }

                return render(self.request, "moderator/mod_coupons.html", context)

        elif 'nextPage' in self.request.POST.keys():
            if 'search_type' in self.request.POST.keys() and 'search_value' in self.request.POST.keys() and 'current_page' in self.request.POST.keys():
                search_type = int(self.request.POST['search_type'])
                search_value = int(self.request.POST['search_value'])
                current_page = int(self.request.POST['current_page'])

                # first we need the max amount of pages

                number_of_coupons = Coupon.objects.all().count()

                c_pages = 1

                if number_of_coupons > 20:
                    # if there are more we divide by 20
                    c_pages = number_of_coupons / 20
                    # see if there is a decimal
                    testO = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testO != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1

                if current_page < c_pages:
                    current_page += 1

                offset = current_page
                coupons = Coupon.objects.all().order_by('code')[
                    20:offset]

                # create a list for a ul to work through

                more_coupons = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(c_pages):
                    i += 1
                    more_coupons.append({'number': i})

                # make an empty coupon for the new form
                coupon = Coupon()
                # search form
                form = searchCouponForm()
                if search_type == "code":
                    form.populate(code=search_value)
                onSubmit = get_message('warning', 7)

                context = {
                    'coupons': coupons,
                    'coupon': coupon,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_coupons': more_coupons,
                    'max_pages': c_pages,
                    'onSubmit': onSubmit,
                }

                return render(self.request, "moderator/mod_coupons.html", context)
        elif 'search' in self.request.POST.keys():
            # get the 20 first current coupons
            if 'code' in self.request.POST.keys():
                code = int(self.request.POST['code'])
                coupons = Coupon.objects.filter(code=code)
                C_pages = 1
                more_coupons = [{'number': 1}]

                # make an empty coupon for the new form
                coupon = Coupon()
                # search form
                form = searchCouponForm()
                form.populate(code)
                current_page = 1
                search_type = "code"
                search_value = code
                onSubmit = get_message('warning', 7)

                context = {
                    'coupons': coupons,
                    'coupon': coupon,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'search_value': search_value,
                    'more_coupons': more_coupons,
                    'max_pages': c_pages,
                    'onSubmit': onSubmit,
                }

            return render(self.request, "moderator/mod_coupons.html", context)


class SpecificCouponView(View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 9)
        messages.warning(
            self.request, message)
        return redirect("moderator:coupons")

    def post(self, *args, **kwargs):
        if 'see' in self.request.POST.keys():
            # get the id
            coupon_id = int(self.request.POST['see'])
            # get freight form
            form = couponForm()
            form.populate(coupon_id)
            context = {
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
            return redirect("moderator:coupons")

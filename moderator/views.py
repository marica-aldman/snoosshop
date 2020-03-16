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
            messages.warning(
                self.request, error_message_35)
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
            messages.warning(
                self.request, error_message_42)
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
            messages.info(
                self.request, error_message_83)
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
                self.request, error_message_84)
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
                        self.request, info_message_38)
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
                        self.request, info_message_39)
                    return redirect("moderator:my_profile")
            else:

                context = {
                    'form': form,
                }

                messages.info(
                    self.request, info_message_40)

                return render(self.request, "moderator/my_info.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, error_message_85)
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

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'products': products,
                'more_products': more_products,
                'form': form,
                'current_page': current_page,
                'max_pages': p_pages,
            }

            return render(self.request, "moderator/mod_products.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, error_message_86)
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

                            context = {
                                'search_type': search_type,
                                'search_value': product_id,
                                'multiple': multiple,
                                'product': the_product,
                                'more_products': more_products,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': p_pages,
                            }

                            return render(self.request, "moderator/mod_products.html", context)

                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, info_message_41)
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

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'product': product,
                                'more_products': more_products,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': p_pages,
                            }

                            return render(self.request, "moderator/mod_products.html", context)

                        except ObjectDoesNotExist:
                            if product_id is not None:
                                messages.info(
                                    self.request, info_message_42)
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

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': p_pages,
                        }
                        if self.request.POST['product_id'] is not None:
                            messages.warning(
                                self.request, error_message_103)
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

                context = {
                    'search_type': search_type,
                    'search_value': search_value,
                    'multiple': multiple,
                    'products': products,
                    'more_products': more_products,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': p_pages,
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

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': p_pages,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        messages.info(
                            self.request, error_message_87)
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

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'products': products,
                            'more_products': more_products,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': p_pages,
                        }

                        return render(self.request, "moderator/mod_products.html", context)

                    except ObjectDoesNotExist:
                        messages.warning(
                            self.request, error_message_88)
                        return redirect("moderator:products")

            elif 'delete' in self.request.POST.keys():
                if 'id' in self.request.POST.keys():

                    product_id = int(self.request.POST['id'])
                    product = Item.objects.get(id=product_id)
                    product.delete()

                    messages.info(
                        self.request, info_message_48)
                    return redirect("moderator:products")
                else:
                    return redirect("moderator:products")
            else:
                return redirect("moderator:categories")

        except ObjectDoesNotExist:
            messages.warning(
                self.request, error_message_89)
            return redirect("moderator:overview")


class SpecificProductsView(View):
    def get(self, *args, **kwargs):
        messages.info(
            self.request, error_message_90)
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
                messages.warning(
                    self.request, error_message_91)
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
                        self.request, info_message_43)
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
                        self.request, info_message_43)
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

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'categories': categories,
                'more_categories': more_categories,
                'form': form,
                'current_page': current_page,
                'max_pages': c_pages,
            }

            return render(self.request, "moderator/mod_categories.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, error_message_96)
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

                            context = {
                                'search_type': search_type,
                                'search_value': category_id,
                                'multiple': multiple,
                                'category': the_category,
                                'more_categories': more_categories,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': c_pages,
                            }

                            return render(self.request, "moderator/mod_categories.html", context)

                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, info_message_44)
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

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'category': category,
                                'more_categories': more_categories,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': c_pages,
                            }

                            return render(self.request, "moderator/mod_categories.html", context)

                        except ObjectDoesNotExist:
                            # most likely trying to reset the form
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

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                        }

                        if self.request.POST['category_id'] != "":
                            messages.warning(
                                self.request, error_message_97)
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

                context = {
                    'search_type': search_type,
                    'search_value': search_value,
                    'multiple': multiple,
                    'categories': categories,
                    'more_categories': more_categories,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': c_pages,
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

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                        }

                        return render(self.request, "moderator/mod_categories.html", context)

                    except ObjectDoesNotExist:
                        messages.warning(
                            self.request, error_message_98)
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

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                        }

                        return render(self.request, "moderator/mod_categories.html", context)

                    except ObjectDoesNotExist:
                        messages.warning(
                            self.request, error_message_99)
                        return redirect("moderator:categories")

            elif 'delete' in self.request.POST.keys():
                if 'id' in self.request.POST.keys():

                    category_id = int(self.request.POST['id'])
                    category = Category.objects.get(id=category_id)
                    category.delete()

                    messages.info(
                        self.request, info_message_47)
                    return redirect("moderator:categories")

                    # might want to change this to rerender the page where we left off
                else:
                    return redirect("moderator:categories")
            else:
                return redirect("moderator:categories")

        except ObjectDoesNotExist:
            messages.warning(
                self.request, error_message_100)
            return redirect("moderator:overview")


class SpecificCategoryView(View):
    def get(self, *args, **kwargs):
        messages.warning(
            self.request, error_message_104)
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
                        self.request, info_message_46)
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
                        self.request, info_message_46)
                    return redirect("moderator:categories")

            else:
                category_id = int(self.request.POST['old'])
                old = category_id

                context = {
                    'form': form,
                    'old': old,
                }
                messages.warning(self.request, error_message_101)
                return render(self.request, "moderator/mod_single_category.html", context)
        else:
            # post with not correct varaibles
            messages.info(
                self.request, error_message_102)
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
            info1 = info_message_49

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
            info2 = info_message_50

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
        # a list of any errors
        errors = []
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
                        messages.warning(self.request, error_message_117)
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
                info1 = info_message_49
        else:
            try:
                reg_orders = Order.objects.filter(
                    ordered=True, being_delivered=False, subscription_order=False).order_by('id')[:10]
            except ObjectDoesNotExist:
                # no orders left to complete
                info1 = info_message_49

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
                info2 = info_message_50
        else:
            try:
                # get todays date
                sub_orders = Order.objects.filter(
                    being_delivered=False, subscription_order=True).order_by('sub_out_date')[:10]
            except ObjectDoesNotExist:
                # no orders left to complete
                info2 = info_message_50

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

        # check for error messages
        for error in errors:
            messages.warning(self.request, error)

        return render(self.request, "moderator/mod_orderhandling.html", context)


class SpecificOrderHandlingView(View):
    def get(self, *args, **kwargs):
        # reroute
        messages.warning(
            self.request, error_message_105)
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
                messages.warning(
                    self.request, error_message_106)
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
                        print('here')
                        item.sent = True
                        some_sent = True
                        item.save()
                    else:
                        print('here2')
                        not_filled = True

                if not_filled:
                    if some_sent:
                        # we are sending part of the order not the entire thing
                        order.comment = "Part of the order has been sent."
                        order.being_delivered = False
                        order.comment = 'Partial'
                    else:
                        # we havent packed anything, abort
                        order.comment = 'Nothing'
                        order.being_delivered = False

                if order.subscription_order and order.comment != 'Partial' and order.comment != 'Nothing':
                    print('oh no')
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
                    if sub.comment == 0:
                        if order.being_delivered is False:
                            sub.comment = order.id
                            sub.save()
                        else:
                            sub.comment = 0
                            sub.save()
                    else:
                        # this person already has orders backed up. Abort and alert
                        messages.warning(
                            self.request, error_message_108 + str(order.user.id))
                        return redirect("moderator:orderhandling")
                order.comment = ""
                order.save()

                if order.being_delivered:
                    messages.info(
                        self.request, info_message_51)
                else:
                    messages.warning(
                        self.request, error_message_108)

                return redirect("moderator:orderhandling")
            except ObjectDoesNotExist:
                messages.warning(
                    self.request, error_message_106)
                return redirect("moderator:orderhandling")
        elif 'back' in self.request.POST.keys():
            order = Order.objects.get(id=int(self.request.POST['back']))
            order.being_read = False
            order.save()
            return redirect("moderator:orderhandling")
        else:
            # something wrong redirect
            messages.warning(
                self.request, error_message_107)
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

        context = {
            'freights': freights,
            'freight': freight,
            'form': form,
            'current_page': current_page,
            'search_type': search_type,
            'more_freights': more_freights,
            'max_pages': f_pages,
        }

        return render(self.request, "moderator/mod_freights.html", context)

    def post(self, *args, **kwargs):
        if 'delete' in self.request.POST.keys():
            # delete freight
            # get id
            freight_id = int(self.request.POST['delete'])
            freight = Freight.objects.get(id=freight_id)
            freight.delete()
            messages.info(self.request, info_message_76)
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

                    context = {
                        'freights': freights,
                        'freight': freight,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'more_freights': more_freights,
                        'max_pages': f_pages,
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

                    context = {
                        'freights': freights,
                        'freight': freight,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'more_freights': more_freights,
                        'max_pages': f_pages,
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

                    context = {
                        'freights': freights,
                        'freight': freight,
                        'form': form,
                        'current_page': current_page,
                        'search_type': search_type,
                        'more_freights': more_freights,
                        'max_pages': f_pages,
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

                context = {
                    'freights': freights,
                    'freight': freight,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'more_freights': more_freights,
                    'max_pages': f_pages,
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

                context = {
                    'freights': freights,
                    'freight': freight,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'more_freights': more_freights,
                    'max_pages': f_pages,
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

                context = {
                    'freights': freights,
                    'freight': freight,
                    'form': form,
                    'current_page': current_page,
                    'search_type': search_type,
                    'more_freights': more_freights,
                    'max_pages': f_pages,
                }

            return render(self.request, "moderator/mod_freights.html", context)


class SpecificFreightView(View):
    def get(self, *args, **kwargs):
        test = 1

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
                messages.info(self.request, info_message_74)
                return redirect("moderator:freights")
            else:
                context = {
                    'form': form,
                    'new': False,
                    'freight': freight_id,
                }
                messages.warning(self.request, error_message_115)
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
                messages.info(self.request, info_message_75)
                return redirect("moderator:freights")
            else:
                context = {
                    'form': form,
                    'new': True,
                    'freight': '',
                }
                messages.warning(self.request, error_message_116)
                return render(self.request, "moderator/mod_single_freight.html", context)
        else:
            return redirect("moderator:freights")

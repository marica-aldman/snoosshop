from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View, FormView
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from core.models import *
from .forms import UserInformationForm, CompanyInfoForm, InitialSupportForm, addressForm, NewSubscriptionForm, NewAddressForm, EditSubscriptionForm, GenericSupportForm, CookieSettingsForm, SetupAddressForm
from django.utils.dateparse import parse_datetime
from core.views import create_ref_code
from slugify import slugify

import random
import string


def test_slug_address(slug):
    test = False
    addressQuery = Address.objects.filter(slug=slug)
    if len(addressQuery) > 0:
        test = True
    return test


def test_slug_company(slug):
    test = False
    companyQuery = CompanyInfo.objects.filter(slug=slug)
    if len(companyQuery) > 0:
        test = True
    return test


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def where_am_i(self):
    path = self.request.get_full_path()
    split_path = path.split("/")
    page = split_path[-1]
    if page == "":
        page = split_path[-2]
    return page


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


def save_subItems_and_orderItems(sub, amount, product):
    # create a subscription item object
    subscription_item = SubscriptionItem()
    # set basic values
    subscription_item.user = sub.user
    subscription_item.subscription = sub
    subscription_item.quantity = amount
    # set product values
    subscription_item.item_title = product.title
    subscription_item.price = product.price
    subscription_item.item = product

    # new orderItem object
    orderItem = OrderItem()
    # set basic valeus
    orderItem.user = sub.user
    orderItem.ordered = True
    orderItem.item = product
    orderItem.title = product.title
    orderItem.quantity = subscription_item.quantity
    orderItem.price = product.price
    if product.discount_price is not None:
        orderItem.discount_price = product.discount_price
        subscription_item.discount_price = product.discount_price
        # set calculated values
        orderItem.total_price = orderItem.get_final_price
        subscription_item.total_price = orderItem.total_price
    else:
        orderItem.discount_price = 1
        subscription_item.discount_price = 1
        orderItem.total_price = orderItem.price
        subscription_item.total_price = orderItem.price
    # save orderitem
    orderItem.save()
    # save subitems
    subscription_item.save()
    return orderItem


class Setup(View):
    def get(self, *args, **kwargs):
        try:
            form_user = UserInformationForm()
            form_company = CompanyInfoForm()
            form_address = SetupAddressForm()

            context = {
                'userForm': form_user,
                'companyForm': form_company,
                'addressForm': form_address,
            }

            return render(self.request, "member/setup.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Något gick fel när vi försökte ladda formuläret för din information. Var vänlig kontakta supporten för hjälp.")
            return redirect("core:home")

    def post(self, *args, **kwargs):
        try:

            # Sort out all the save functions and what kind of adress etc

            theUser = self.request.user
            form_user = UserInformationForm(self.request.POST)
            form_company = CompanyInfoForm(self.request.POST)
            form_address = SetupAddressForm(self.request.POST)
            hasCompany = False

            if 'hasCompany' in self.request.POST.keys():
                if self.request.POST['hasCompany'] == 'on':
                    hasCompany = True

            if form_user.is_valid():
                # set this users group to client
                try:
                    theUser.groups.add(Group.objects.get(name="client"))
                except ObjectDoesNotExist:
                    # skip this
                    groups = 0
                # check that we dont already have info on this user
                try:
                    userInfo = UserInfo.objects.get(user=theUser)
                except ObjectDoesNotExist:
                    userInfo = UserInfo()

                # set values in user info AND user model

                userInfo.user = theUser
                userInfo.first_name = form_user.cleaned_data.get('first_name')
                theUser.first_name = form_user.cleaned_data.get('first_name')
                userInfo.last_name = form_user.cleaned_data.get('last_name')
                theUser.last_name = form_user.cleaned_data.get('last_name')
                userInfo.email = form_user.cleaned_data.get('email')
                userInfo.telephone = form_user.cleaned_data.get('telephone')
                if hasCompany:
                    # check that we dont already have company info on this user
                    try:
                        companyInfo = CompanyInfo.objects.get(user=theUser)
                    except ObjectDoesNotExist:
                        companyInfo = CompanyInfo()
                    try:
                        address = Address.objects.get(user=theUser)
                    except ObjectDoesNotExist:
                        address = Address()
                    if form_address.is_valid() and form_company.is_valid():
                        userInfo.company = True

                        address.user = theUser
                        address.street_address = form_address.cleaned_data.get(
                            'street_address')
                        address.apartment_address = form_address.cleaned_data.get(
                            'apartment_address')
                        address.post_town = form_address.cleaned_data.get(
                            'post_town')
                        address.zip = form_address.cleaned_data.get('zip')
                        address.country = "Sverige"
                        address.address_type = "B"
                        address.default = True

                        # create a slug

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

                        address.slug = testSlug
                        address.save()

                        companyInfo.user = theUser
                        companyInfo.company = form_company.cleaned_data.get(
                            'company')
                        companyInfo.organisation_number = form_company.cleaned_data.get(
                            'organisation_number')
                        companyInfo.addressID = address
                        slug = companyInfo.company + str(companyInfo.user.id)
                        makeSlug = slugify(slug)
                        test = test_slug_company(makeSlug)
                        i = 1
                        while test:
                            slug = companyInfo.company + \
                                str(companyInfo.user.id) + str(i)
                            makeSlug = slugify(slug)
                            test = test_slug_company(makeSlug)
                            i += 1
                        companyInfo.slug = makeSlug
                        companyInfo.save()

                        userInfo.companyID = companyInfo
                        userInfo.save()

                        # save user too
                        theUser.save()

                        messages.info(
                            self.request, "Uppgifter sparade. Du kan uppdatera och lägga till information under din profil")
                        return redirect("member:my_overview")
                    else:

                        context = {
                            'userForm': form_user,
                            'companyForm': form_company,
                            'addressForm': form_address,
                        }
                        messages.info(
                            self.request, "2 Det saknas information i något av de obligatoriska fälten.")
                        return render(self.request, "member/setup.html", context)
                else:
                    userInfo.company = False
                    userInfo.save()

                    messages.info(
                        self.request, "Uppgifter sparade. Du kan uppdatera och lägga till information under din profil")
                    return redirect("member:my_overview")
            else:

                context = {
                    'userForm': form_user,
                    'companyForm': form_company,
                    'addressForm': form_address,
                }

                messages.info(
                    self.request, "1 Det saknas information i något av de obligatoriska fälten.")
                return render(self.request, "member/setup.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Något gick fel när vi försökte ställa in ditt konto. Kontakta supporten för hjälp.")
            return redirect("core:home")


class CompanyView(View):
    def get(self, *args, **kwargs):

        # get form
        theUser = self.request.user
        form = CompanyInfoForm()
        form.populate(theUser)

        # get the users adresses incase they have moved the company

        addresses = Address.objects.filter(user=theUser, address_type="B")

        # check which one is the current one

        compInfo = CompanyInfo.objects.get(user=theUser)

        context = {
            'form': form,
            'addresses': addresses,
            'addressID': compInfo.id,
        }

        return render(self.request, "member/company.html", context)

    def post(self, *args, **kwargs):

        theUser = self.request.user
        form = CompanyInfoForm(self.request.POST)

        if form.is_valid():
            compInfo = CompanyInfo.objects.get(user=theUser)

            compInfo.company = form.cleaned_data.get('company')
            compInfo.organisation_number = form.cleaned_data.get(
                'organisation_number')

            # check for an address change

            addressID = self.request.POST['address']
            try:
                addressTest = Address.objects.get(id=addressID)

                if addressTest.id == compInfo.addressID.id:
                    # no change in adress just save and redirect
                    compInfo.save()
                    messages.info(
                        self.request, "Informationen sparad.")
                    return redirect("member:my_profile")
                else:
                    compInfo.addressID = addressTest
                    compInfo.save()
                    messages.info(
                        self.request, "Informationen sparad.")
                    return redirect("member:my_profile")
            except ObjectDoesNotExist:
                # something is wrong here rerender the form, with message

                messages.info(
                    self.request, "Någonting gick fel. Kontakta support för assistans.")

                addresses = Address.objects.filter(user=theUser)

                context = {
                    'form': form,
                    'addresses': addresses
                }

                return render(self.request, "member/company.html", context)

        else:
            # form not valid rerender

            messages.info(
                self.request, "Något i formuläret saknas Var god fyll i hela formuläret.")

            addresses = Address.objects.filter(user=theUser)

            context = {
                'form': form,
                'addresses': addresses
            }

            return render(self.request, "member/company.html", context)


class Overview(View):
    def get(self, *args, **kwargs):
        try:

            # get the active support errands and the resently ended support errands

            try:
                errands = SupportThread.objects.filter(user=self.request.user,)
            except ObjectDoesNotExist:
                errands = {}

            errands1 = []
            errands2 = []
            today = make_aware(datetime.now())

            for errand in errands:
                if errand.done:
                    time_diff = errand.doneDate - today
                    if time_diff.days < 8:
                        errands2.append(errand)
                else:
                    errands1.append(errand)

            # get the responces of open errand and see who last responded, user or support

            responces_a = []

            for errand in errands1:
                responces = errand.responce
                # get the last responce
                maxIndex = len(responces) - 1
                responce = responces[maxIndex]

                lastUser = responce.user
                if lastUser.status == 1:
                    responces_a.append({'lastReply': 'customer'})
                else:
                    responces_a.append({'lastReply': 'support'})

            responces_r = []

            for errand in errands2:
                responces = errand.responce
                # get the last responce
                maxIndex = len(responces) - 1
                responce = responces[maxIndex]

                lastUser = responce.user
                if lastUser.status == 1:
                    responces_r.append({'lastReply': 'customer'})
                else:
                    responces_r.append({'lastReply': 'support'})

            # get the active orders and the resently sent orders

            try:
                orders = Order.objects.filter(
                    user=self.request.user, ordered=True)
            except ObjectDoesNotExist:
                orders = {}

            order1 = []
            order2 = []
            today = make_aware(datetime.now())

            for order in orders:
                if order.received:
                    time_diff = order.updated_date - today
                    if time_diff.days < 8:
                        order2.append(order)
                else:
                    order1.append(order)

            context = {
                'support_a': errands1,
                'support_r': errands2,
                'order_a': order1,
                'order_r': order2,
                'responces_a': {'lastReply': 'none'},
                'responces_r': {'lastReply': 'none'},
            }

            if len(responces_a) < 0:
                context.update({'responces_a': responces_a})

            if len(responces_r) < 0:
                context.update({'responces_r': responces_r})

            return render(self.request, "member/my_overview.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your overview. Contact the support for assistance.")
            return redirect("core:home")


class Orders(View):
    def get(self, *args, **kwargs):
        try:

            # get the orders and sort out active ones
            subscription = False
            try:
                orders_a = Order.objects.filter(
                    user=self.request.user, ordered=True, received=False, subscription_order=False)
                orders_r = Order.objects.filter(
                    user=self.request.user, ordered=True, received=True, subscription_order=False)
                orders_s = Order.objects.filter(
                    user=self.request.user, subscription_order=True)
                if orders_s is not None:
                    subscription = True
            except ObjectDoesNotExist:
                orders_a = {}
                orders_r = {}
                orders_s = {}

            # get all the items and their discounts

            context = {
                'orders_r': orders_r,
                'orders_a': orders_a,
                'orders_s': orders_s,
                'subscription': subscription,
            }

            return render(self.request, "member/my_orders.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your orderlistspage. Contact the support for assistance.")
            return redirect("member:my_overview")


class OrderView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        try:
            orderQuery = Order.objects.filter(
                user=self.request.user, id=int(self.request.POST['lookAtOrder']))

            for order in orderQuery:
                # get all the addresses

                shipping_address = Address()
                billing_address = Address()

                if order.shipping_address is not None:
                    shipping_address_id = order.shipping_address.id
                    billing_address_id = order.billing_address.id

                    shipping_addressQuery = Address.objects.filter(
                        id=shipping_address_id)

                    billing_addressQuery = Address.objects.filter(
                        id=billing_address_id)

                    for address in shipping_addressQuery:
                        shipping_address = address

                    for address in billing_addressQuery:
                        billing_address = address

                # get the cupon used
                coupon_id = 0
                coupons = Coupon()

                if order.coupon is not None:
                    coupon_id = order.coupon.id

                    couponsQuery = Coupon.objects.filter(id=coupon_id)

                    for coupon in couponsQuery:
                        coupons = coupon

                # get the payment info
                payment_id = 1
                payments = Payment()
                if order.payment is not None:
                    payment_id = order.payment.id

                    paymentQuery = Payment.objects.filter(id=payment_id)

                    for payment in paymentQuery:
                        payments = payment

                theOrder = Order()
                theOrderItems = {}

                # get all the items and their discounts
                for order in orderQuery:
                    theOrderItems = order.items.all()
                    theOrder = order

                context = {
                    'order': theOrder,
                    'all_order_items': theOrderItems,
                    'shipping_address': shipping_address,
                    'billing_address': billing_address,
                    'coupons': coupons,
                    'payment': payments,
                }

                return render(self.request, "member/my_order.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Can't find this order. Contact the support for assistance.")
            return redirect("member:my_orders")


class SupportView(View):
    def get(self, *args, **kwargs):
        try:
            # get all errands, sort out the active ones

            try:
                errands = SupportThread.objects.filter(user=self.request.user,)
            except ObjectDoesNotExist:
                errands = {}

            errands_a = []
            today = make_aware(datetime.now())

            for errand in errands:
                if not errand.done:
                    errands_a.append(errand)

            context = {
                'support': errands,
                'errands_a': errands_a,
            }

            return render(self.request, "member/my_support.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing this page. Contact the support for assistance.")
            return redirect("member:my_overview")


class NewErrandView(View):
    def get(self, *args, **kwargs):
        try:
            # new errand

            form = InitialSupportForm()

            context = {
                'form': form
            }

            return render(self.request, "member/new_errand.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong. Contact the support for assistance.")
            return redirect("member:my_overview")


class ErrandView(View):
    def get(self, *args, **kwargs):
        try:
            # id check here
            slug = where_am_i(self)
            try:
                errand = SupportThread.objects.filter(
                    user=self.request.user, slug=slug)
            except ObjectDoesNotExist:
                errand = {}

            try:
                responces = SupportResponces.objects.filter(
                    user=self.request.user, slug=slug)
            except ObjectDoesNotExist:
                responces = {}

            # add form for further contact on this issue

            context = {
                'errand': errand,
                'responces': responces,
            }

            return render(self.request, "member/my_errand.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Can't find this errand. Contact the support for assistance.")
            return redirect("member:my_overview")


class Profile(View):
    def get(self, *args, **kwargs):
        try:
            # get user info
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()
                info.company = False

            # company info
            try:
                company = CompanyInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                company = {}

            # get user addresses

            try:
                addresses = Address.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                addresses = {}

            # place info in context and render page

            context = {
                'info': info,
                'company': company,
                'addresses': addresses,
            }

            return render(self.request, "member/my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")


class InfoView(View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id

            form = UserInformationForm(the_User=self.request.user)

            # check if there is a company connected
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()

            context = {
                'form': form,
                'info': info,
            }

            return render(self.request, "member/my_info.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your information. Contact the support for assistance.")
            return redirect("member:my_profile")

    def post(self, *args, **kwargs):
        try:
            form = UserInformationForm(self.request.POST)

            if 'edit' in self.request.POST.keys():

                # check if there is a company connected
                try:
                    info = UserInfo.objects.get(user=self.request.user)
                except ObjectDoesNotExist:
                    info = UserInfo()

                context = {
                    'form': form,
                    'info': info,
                }

                return render(self.request, "member/my_info.html", context)

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
                    return redirect("member:my_profile")
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
                return redirect("member:my_profile")
            else:
                try:
                    info = UserInfo.objects.get(user=self.request.user)
                except ObjectDoesNotExist:
                    info = UserInfo()

                context = {
                    'form': form,
                    'info': info,
                }

                messages.info(
                    self.request, "Missing certain information.")

                return render(self.request, "member/my_info.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when saving your information. Contact the support for assistance.")
            return redirect("member:my_profile")


class Editaddress(View):
    def get(self, *args, **kwargs):
        try:
            # which adress
            page = where_am_i(self)
            # get the address
            addressQuery = Address.objects.filter(
                user=self.request.user, slug=page)
            for address in addressQuery:
                # get form

                form = addressForm(address)

                ADDRESS_CHOICES_EXTENDED = [
                    {'key': 'B', 'name': 'Billing'},
                    {'key': 'S', 'name': 'Shipping'},
                    {'key': 'A', 'name': 'BOTH'},
                ]

                context = {
                    'form': form,
                    'address': address,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }

                return render(self.request, "member/edit_address.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        try:
            # which adress
            slug = where_am_i(self)
            # get the address
            address = Address.objects.get(slug=slug)
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
                if address.address_type == self.request.POST['address_type']:
                    if address.default is True:
                        if 'default_address' in self.request.POST.keys():
                            if self.request.POST['default_address'] == 'on':
                                address.default = True
                            else:
                                address.default = False
                        else:
                            address.default = False
                    else:
                        address.default = False
                else:
                    if 'default_address' in self.request.POST.keys():
                        if self.request.POST['default_address'] == 'on':
                            changeAdressTypeQuery = Address.objects.filter(
                                address_type=form.cleaned_data('address_type'))
                            for addressOfType in changeAdressTypeQuery:
                                addressOfType = False
                            address.default = True
                            address.address_type = form.cleaned_data(
                                'address_type')
                        else:
                            address.default = False
                            address.address_type = form.cleaned_data(
                                'address_type')
                    else:
                        address.default = False
                        address.address_type = form.cleaned_data(
                            'address_type')

                testString = address.street_address + \
                    address.address_type + str(address.user.id)
                toSlug = slugify(testString)
                if toSlug != address.slug:
                    testVariable = test_slug_address(toSlug)
                    if testVariable:
                        messages.info(
                            self.request, "You already have this address saved.")
                        return redirect("member:my_profile")
                    else:
                        address.slug = toSlug

                # save the address and return to list
                address.save()

                messages.info(self.request, "Address have been saved.")
                return redirect("member:my_profile")
            else:
                messages.info(
                    self.request, "Something is wrong, contact support.")
                return redirect("member:my_profile")
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")


class Newaddress(View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id
            form = NewAddressForm()

            context = {
                'form': form,
            }

            return render(self.request, "member/new_address.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        try:
            form = NewAddressForm(self.request.POST or None)

            if form.is_valid():

                # get values
                address = Address()

                address.user = self.request.user
                address.street_address = form.cleaned_data.get(
                    'street_address')
                address.apartment_address = form.cleaned_data.get(
                    'apartment_address')
                address.post_town = form.cleaned_data.get('post_town')
                address.zip = form.cleaned_data.get('zip')
                address.country = "Sverige"
                if 'default_address' in self.request.POST.keys():
                    if self.request.POST['default_address'] == 'on':
                        address.default = True
                    else:
                        address.default = False
                else:
                    address.default = False

                # check that if we want the address to be both shipping and billing
                address_type = form.cleaned_data.get('address_type')

                if address_type == "A":
                    # we want two copies of this address
                    address2 = Address()
                    address2.user = self.request.user
                    address2.street_address = form.cleaned_data.get(
                        'street_address')
                    address2.apartment_address = form.cleaned_data.get(
                        'apartment_address')
                    address2.post_town = form.cleaned_data.get('post_town')
                    address2.zip = form.cleaned_data.get('zip')
                    address2.country = "Sverige"
                    if 'default_address' in self.request.POST.keys():
                        if self.request.POST['default_address'] == 'on':
                            address2.default = True
                        else:
                            address2.default = False
                    else:
                        address2.default = False
                    address2.address_type = "S"
                    # check if this is set as the default address if it is remove default from all of this users addresses in the database

                    if address.default:
                        addresses = Address.objects.filter(
                            user=self.request.user, default=True)
                        for address1 in addresses:
                            address1.default = False
                            address1.save()

                    # save the second copy of the address

                    toSlug = address2.street_address + \
                        address2.address_type + str(address2.user.id)
                    testSlug = slugify(toSlug)
                    existingSlug = test_slug_address(testSlug)
                    if existingSlug:
                        messages.info(self.request, "Address already exists.")
                        return redirect("member:my_profile")
                    else:
                        address2.slug = testSlug
                    address2.save()
                    address.address_type = "B"
                else:
                    address.address_type = address_type

                    # if this is the default remove default of the same address type from the users addresses
                    if address.default:
                        addresses = Address.objects.filter(
                            user=self.request.user, default=True, address_type=address_type)
                        for address1 in addresses:
                            address1.default = False
                            address1.save()
                # create a slug

                toSlug = address.street_address + \
                    address.address_type + str(address.user.id)
                testSlug = slugify(toSlug)
                existingSlug = test_slug_address(testSlug)
                if existingSlug:
                    messages.info(self.request, "Address already exists.")
                    return redirect("member:my_profile")
                else:
                    address.slug = testSlug
                # save the address and return to list
                address.save()

                messages.info(self.request, "Address have been saved.")
                return redirect("member:my_profile")
            else:
                context = {
                    'form': form,
                }

                return render(self.request, "member/new_address.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")


class Settings(View):
    def get(self, *args, **kwargs):
        try:
            # obs make a form view for editing info and adding info

            try:
                cookieSettings = Cookies.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                cookieSettings = {}

            context = {
                'cookies': cookieSettings,
            }

            return render(self.request, "member/my_settings.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your settings. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionsView(View):
    def get(self, *args, **kwargs):

        try:
            # get all subscriptions
            try:
                subscriptions = Subscription.objects.filter(
                    user=self.request.user)
            except ObjectDoesNotExist:
                subscriptions = {}

            # make a subscription object and give it new as slog for the new button
            newSub = Subscription()
            newSub.slug = 'new'

            context = {
                'subscriptions': subscriptions,
                'newSub': newSub,
            }

            return render(self.request, "member/my_subscriptions.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        try:
            # if we pressed a delete button preform the delete
            message = ''
            if 'delete' in self.request.POST.keys():
                # get the subscription
                subscription = Subscription.objects.filter(
                    user=self.request.user, id=int(self.request.POST['id']),)
                # enter the query
                for sub in subscription:
                    # check that there is an order connected
                    if sub.next_order > 0:
                        # get the order
                        orderQuery = Order.objects.filter(id=sub.next_order)
                        # enter the query
                        for order in orderQuery:
                            # get the orderItem
                            orderItemQuery = order.items.all()
                            # enter the query
                            for orderItem in orderItemQuery:
                                # delete order item
                                orderItem.delete()
                            # delete order
                            order.delete()
                            # delete subscription
                            sub.delete()
                            message = 'subscription and corresponding order deleted'
                    else:
                        # delete subscription
                        sub.delete()
                        message = 'subscription deleted'
            # get all subscriptions
            try:
                subscriptions = Subscription.objects.filter(
                    user=self.request.user,)
            except ObjectDoesNotExist:
                subscriptions = {}

            # make a subscription object and give it new as slog for the new button
            newSub = Subscription()
            newSub.slug = 'new'

            context = {
                'subscriptions': subscriptions,
                'newSub': newSub,
            }

            messages.info(self.request, message)

            return render(self.request, "member/my_subscriptions.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionView(View):
    def post(self, *args, **kwargs):
        try:
            # if we are editing get the specific Subscription otherwise set values for new
            slug = where_am_i(self)
            if slug == 'new':

                # set additional values
                sub_date = datetime.now().strftime("%Y-%m-%d")
                number_of_products = 1
                old = False
                subscription = Subscription()

                # get the form
                form = EditSubscriptionForm(
                    self.request.user, slug=slug)

                context = {
                    'form': form,
                    'sub_date': sub_date,
                    'number_of_products': number_of_products,
                    'old': old,
                    'subscription': subscription,
                }

                return render(self.request, "member/my_subscription.html", context)
            else:
                try:
                    subscription = Subscription.objects.filter(
                        user=self.request.user, slug=slug)
                    sub_date = ""
                    number_of_products = 0

                    if subscription is not None:
                        for sub in subscription:
                            if sub.active:
                                old = True
                            else:
                                old = False
                            sub_date = sub.start_date.strftime("%Y-%m-%d")
                            number_of_products = sub.number_of_items

                            # get the form
                            form = EditSubscriptionForm(
                                self.request.user, slug=slug, n_o_p=number_of_products)

                            context = {
                                'form': form,
                                'sub_date': sub_date,
                                'subscription': sub,
                                'number_of_products': number_of_products,
                                'old': old,
                            }

                            return render(self.request, "member/my_subscription.html", context)
                    else:
                        messages.info(
                            self.request, "Something went wrong when accessing your subscription. Contact the support for assistance.")
                        return redirect("member:my_subscriptions")

                except ObjectDoesNotExist:
                    messages.info(
                        self.request, "Something went wrong when accessing your subscription. Contact the support for assistance.")
                    return redirect("member:my_subscriptions")

        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")


class SaveSubscriptionView(View):
    def post(self, *args, **kwargs):
        if 'saveSubscription' in self.request.POST.keys():
            # saving subscription
            # check if new or old
            if self.request.POST['new_or_old'] == 'old':

                # get the old subscription
                subscription = Subscription.objects.filter(
                    user=self.request.user, id=int(self.request.POST['id']),)
                message = ''
                # access query set
                for sub in subscription:
                    # take in the data
                    # user
                    sub.user = self.request.user

                    # start date
                    # make sure the date is in the correct format
                    sub.start_date = make_aware(datetime.strptime(
                        self.request.POST['start_date'], '%Y-%m-%d'))
                    # intervall
                    sub.intervall = self.request.POST['intervall']
                    # all user addresses
                    addresses = Address.objects.filter(user=self.request.user)
                    # shipping_address
                    shipping_address = self.request.POST['shipping_address']
                    # billing_address
                    billing_address = self.request.POST['billing_address']
                    for address in addresses:
                        if address.id == int(shipping_address):
                            sub.shipping_address = address
                        elif address.id == int(billing_address):
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

                    if sub.next_order > 0:
                        theOrderQuery = Order.objects.filter(
                            id=sub.next_order)
                        for theOrder in theOrderQuery:
                            theOrder.subscription_order = True
                            theOrder.subscription_date = sub.next_order_date
                            theOrder.updated_date = make_aware(datetime.now())
                            theOrder.ordered_date = make_aware(datetime.now())
                            theOrder.sub_out_date = sub.start_date
                            theOrder.ordered = True
                            theOrder.received = False
                            theOrder.being_delivered = False
                            for address in addresses:
                                if address.id == int(shipping_address):
                                    theOrder.shipping_address = address
                                elif address.id == int(billing_address):
                                    theOrder.billing_address = address
                            theOrder.save()
                            sub.next_order = theOrder.id
                            sub.save()

                            # remove old order items and subitems
                            orderItems = theOrder.items.all()
                            for item in orderItems:
                                item.delete()

                            sub_items = SubscriptionItem.objects.filter(
                                subscription=sub)
                            for item in sub_items:
                                item.delete()

                            # and then make new the order items, and subItems

                            i = 1

                            for i in range(sub.number_of_items):
                                i += 1
                                p_string = 'product%s' % (i,)
                                a_string = 'amount%s' % (i,)
                                product_id = int(self.request.POST[p_string])
                                amount = int(self.request.POST[a_string])
                                products = Item.objects.filter(id=product_id)
                                # enter the product query set for easy handling when saving subscription and order items
                                for product in products:
                                    orderItem = save_subItems_and_orderItems(
                                        sub, amount, product)
                                    theOrder.items.add(orderItem)
                                    message = "Subscription saved and activated."

                    else:
                        # it isn't so we make a new one
                        theOrder = Order()

                        theOrder.user = sub.user

                        # create a reference code and check that there isnt already one before setting the orders ref code to the code
                        ref_code = create_ref_code()
                        ref_test = True

                        while ref_test:
                            testOrder = Order.objects.filter(ref_code=ref_code)
                            if testOrder is None:
                                refcode = create_ref_code()
                            else:
                                ref_test = False

                        theOrder.ref_code = ref_code
                        theOrder.subscription_order = True
                        theOrder.subscription_date = sub.next_order_date
                        theOrder.updated_date = make_aware(datetime.now())
                        theOrder.ordered_date = make_aware(datetime.now())
                        theOrder.sub_out_date = sub.start_date
                        theOrder.ordered = True
                        theOrder.received = False
                        theOrder.being_delivered = False
                        for address in addresses:
                            if address.id == int(shipping_address):
                                theOrder.shipping_address = address
                            elif address.id == int(billing_address):
                                theOrder.billing_address = address
                        theOrder.save()
                        sub.next_order = theOrder.id
                        sub.save()

                        i = 1

                        for i in range(sub.number_of_items):
                            i += 1
                            p_string = 'product%s' % (i,)
                            a_string = 'amount%s' % (i,)
                            product_id = int(self.request.POST[p_string])
                            amount = int(self.request.POST[a_string])
                            products = Item.objects.filter(id=product_id)
                            # enter the product query set for easy handling when saving subscription and order items
                            for product in products:
                                orderItem = save_subItems_and_orderItems(
                                    sub, amount, product)
                                theOrder.items.add(orderItem)
                                message = "Subscription saved and activated."
                    messages.info(self.request, message)
                    return redirect("member:my_subscriptions")

            else:
                message = ''

                # make a subscription object
                sub = Subscription()
                # take in the data
                # user
                sub.user = self.request.user

                # start date
                # make sure the date is in the correct format
                sub.start_date = make_aware(datetime.strptime(
                    self.request.POST['start_date'], '%Y-%m-%d'))
                # intervall
                sub.intervall = self.request.POST['intervall']
                # all user addresses
                addresses = Address.objects.filter(user=self.request.user)
                # shipping_address
                shipping_address = self.request.POST['shipping_address']
                # billing_address
                billing_address = self.request.POST['billing_address']
                for address in addresses:
                    if address.id == int(shipping_address):
                        sub.shipping_address = address
                    elif address.id == int(billing_address):
                        sub.billing_address = address
                # number of products
                sub.number_of_items = int(
                    self.request.POST['number_of_products'])

                # calcuate the rest of the data
                sub.updated_date = make_aware(datetime.now())
                sub.active = True

                # get_next_order_date
                sub.next_order_date = get_next_order_date(
                    sub.start_date, sub.intervall)

                # temp slug
                sub.slug = "temp2"

                # save subscription
                sub.save()

                # set unique slug
                sub.slug = "s" + str(sub.id) + "u" + str(self.request.user.id)

                # resave
                sub.save()

                # save the order
                # first create the order

                theOrder = Order()

                theOrder.user = sub.user
                # create a reference code and check that there isnt already one before setting the orders ref code to the code
                ref_code = create_ref_code()
                ref_test = True

                while ref_test:
                    testOrder = Order.objects.filter(ref_code=ref_code)
                    if testOrder is None:
                        refcode = create_ref_code()
                    else:
                        ref_test = False

                theOrder.ref_code = ref_code
                theOrder.subscription_order = True
                theOrder.updated_date = make_aware(datetime.now())
                theOrder.ordered_date = make_aware(datetime.now())
                theOrder.sub_out_date = sub.start_date
                theOrder.ordered = True
                theOrder.received = False
                theOrder.being_delivered = False
                theOrder.shipping_address = sub.shipping_address
                theOrder.billing_address = sub.billing_address
                theOrder.save()

                sub.next_order = theOrder.id
                sub.save()

                # create subscription items and corresponding orderItems

                i = 1

                for i in range(sub.number_of_items):
                    i += 1
                    p_string = 'product%s' % (i,)
                    a_string = 'amount%s' % (i,)
                    product_id = int(self.request.POST[p_string])
                    amount = int(self.request.POST[a_string])
                    products = Item.objects.filter(id=product_id)
                    # enter the product query set for easy handling when saving subscription and order items
                    for product in products:
                        orderItem = save_subItems_and_orderItems(
                            sub, amount, product)
                        theOrder.items.add(orderItem)
                        message = "Subscription saved and activated."
                messages.info(self.request, message)
                return redirect("member:my_subscriptions")


class DeactivateSubscriptionView(View):
    def post(self, *args, **kwargs):
        if 'deactivateSubscription' in self.request.POST.keys():
            subscription = Subscription.objects.filter(
                user=self.request.user, id=int(self.request.POST['id']))

            for sub in subscription:
                # deactivate subscription
                if sub.active is False:
                    messages.info(
                        self.request, "Subscription already deactivated")
                    return redirect("member:my_subscriptions")
                else:
                    sub.active = False

                    # delete the order connected to the sub
                    theOrder = Order.objects.filter(id=sub.next_order)
                    # lets handle the query
                    message = "Subscription deactivated no order detected."
                    for order in theOrder:
                        # first get the list of items
                        theOrderItems = order.items.all()
                        # then go through the items one by one
                        message = "Subscription deactivated no order items detected."
                        for item in theOrderItems:
                            # delete the items
                            item.delete()
                            # delete order
                            order.delete()
                            message = "Subscription deactivated."
                    sub.next_order = 0
                    sub.save()

                    messages.info(
                        self.request, message)
                    return redirect("member:my_subscriptions")
        else:
            messages.info(self.request, "Fix buttons")
            return redirect("member:my_subscriptions")


class DeleteOrder(View):
    def post(self, *args, **kwargs):
        postID = self.request.POST['id']
        orderId = int(self.request.POST['id'])
        orderQuery = Order.objects.filter(id=orderId)
        for order in orderQuery:
            oIs = order.items.all()
            for item in oIs:
                item.delete()
            order.delete()
            message = "Order deleted"

        messages.info(self.request, message)
        return redirect("member:my_orders")


class CookieSettingsView(View):
    def get(self, *args, **kwargs):
        try:
            # get cookie model, fill in with previous info if there is any
            print("start")
            user = self.request.user
            print(self.request.user)
            form = CookieSettingsForm()
            print("form")
            if str(user) != 'AnonymousUser':
                form.populate(user)
            print("populate")

            try:
                if str(user) == 'AnonymousUser':
                    cookie_settings = Cookies()
                else:
                    cookie_settings = Cookies.objects.get(user=user)
            except ObjectDoesNotExist:
                cookie_settings = Cookies()
            print("anonymous")

            context = {
                'cookie_settings': cookie_settings,
                'form': form,
            }

            print("context")
            return render(self.request, "cookie_settings.html", context)
        except ObjectDoesNotExist:
            message = "Något gick fel vid laddningen av sidan. Kontakta support för hjälp."
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
            message = "Något gick fel vid sparandet av dina inställningar. Kontakta support för hjälp."
            messages.warning(self.request, message)
            return redirect("core:home")


class GenericSupportFormView(View):
    def get(self, *args, **kwargs):
        try:
            # get a form
            form = GenericSupportForm()

            context = {
                'form': form,
            }

            return render(self.request, "member/support.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing the cookie settings page. Contact the support for assistance.")
            return redirect("core:home")

    def post(self, *args, **kwargs):
        try:
            # get a form
            form = GenericSupportForm(self.request.POST)

            if form.is_valid():
                # take in data

                support = GenericSupport()
                support.email = form.cleaned_data.get('email')
                support.subject = form.cleaned_data.get('subject')
                support.message = form.cleaned_data.get('message')
                support.sent_date = datetime.now()

                makingSlug = str(support.email) + str(support.sent_date)
                testMakingSlug = makingSlug
                slug_test = True
                i = 1

                while slug_test:
                    try:
                        test = GenericSupport.objects.filter(
                            slug=testMakingSlug).count()
                    except ObjectDoesNotExist:
                        test = 10

                    if test > 0:
                        testMakingSlug = makingSlug + "_" + str(i)
                        i += 1
                    else:
                        slug_test = False
                        makingSlug = testMakingSlug

                support.slug = makingSlug

                # send email to support and copy to customer
                # support
                # dont forget to check for bad header etc

                try:
                    send_mail(
                        support.subject,
                        support.message,
                        'marica.aldman@gmail.com',
                        ['marica.aldman@gmail.com'],
                        fail_silently=False,
                    )

                except BadHeaderError:
                    messages.warning(
                        'Ämnet innehåller icke tillåtna karaktärer.')

                    context = {
                        'form': form,
                    }

                    return render(self.request, "member/support.html", context)

                # customer
                # make a can not reply message
                # take this from language database later
                canNotReply = '\n\nPs. Do not reply to this message. This is just a copy of the message you placed in the form. Support will respond to you within X buisness days. Ds.'

                send_mail(
                    "Copy: " + support.subject,
                    support.message + canNotReply,
                    'contact@snoosshop.com',
                    [support.email],
                    fail_silently=False,
                )
                # if you got this far save to database

                support.save()

                messages.info(
                    self.request, 'Ärendet skickat. En kopia har skickats till din angivna emailadress.')
                return redirect("core:home")

            # form isn't valid rerender

            context = {
                'form': form,
            }

            return render(self.request, "member/support.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Something went wrong when accessing the cookie settings page. Contact the support for assistance.")
            return redirect("core:home")

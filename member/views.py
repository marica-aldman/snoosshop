from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View, FormView
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from core.models import *
from .forms import *
from django.utils.dateparse import parse_datetime
from core.functions import *
from django.core.files import File
from django.core.files.base import ContentFile
import json


class Setup(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        theUser = self.request.user
        theUser = self.request.user
        if(theUser.is_authenticated):
            group1 = Group.objects.get(name="client")
            group2 = Group.objects.get(name="moderator")
            group3 = Group.objects.get(name="support")
            groups = theUser.groups.all()

            for group in groups:
                if group == group1:
                    return redirect("member:my_overview")
                elif group == group2:
                    return redirect("moderator:overview")
                elif group == group3:
                    return redirect("support:overview")
        group = Group.objects.get(name="client")
        group.user_set.add(theUser)

        form_user = UserInformationForm()
        form_company = CompanyInfoForm()
        form_address = SetupAddressForm()

        context = {
            'gdpr_check': gdpr_check,
            'userForm': form_user,
            'companyForm': form_company,
            'addressForm': form_address,
        }

        return render(self.request, "member/setup.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                theUser.email = form_user.cleaned_data.get('email')
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
                        address.slug = create_slug_address(address)
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
                        info_message = get_message('info', 1)
                        messages.info(
                            self.request, info_message)
                        return redirect("member:my_overview")
                    else:

                        context = {
                            'userForm': form_user,
                            'companyForm': form_company,
                            'addressForm': form_address,
                        }
                        message = get_message('error', 1)
                        messages.warning(
                            self.request, message)
                        return render(self.request, "member/setup.html", context)
                else:
                    userInfo.company = False
                    userInfo.slug = slugify(theUser.username)
                    userInfo.save()
                    settings = Cookies()
                    settings.user = theUser
                    # if we add settings it needs to be sorted here for now we only have functional so we dont need to do anything else
                    settings.save()
                    info_message = get_message('info', 1)
                    messages.info(
                        self.request, info_message)
                    return redirect("member:my_overview")
            else:

                context = {
                    'gdpr_check': gdpr_check,
                    'userForm': form_user,
                    'companyForm': form_company,
                    'addressForm': form_address,
                }
                message = get_message('error', 1)
                messages.warning(
                    self.request, message)
                return render(self.request, "member/setup.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 2)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class CompanyView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        # get form
        theUser = self.request.user
        form = CompanyInfoForm()
        form.populate(theUser)

        # get the users adresses incase they have moved the company

        addresses = Address.objects.filter(user=theUser, address_type="B")

        # check which one is the current one

        compInfo = CompanyInfo.objects.get(user=theUser)

        context = {
            'gdpr_check': gdpr_check,
            'form': form,
            'addresses': addresses,
            'addressID': compInfo.id,
        }

        return render(self.request, "member/company.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

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
                info_message = get_message('info', 2)
                if addressTest.id == compInfo.addressID.id:
                    # no change in adress just save and redirect
                    compInfo.save()
                    messages.info(
                        self.request, info_message)
                    return redirect("member:my_profile")
                else:
                    compInfo.addressID = addressTest
                    compInfo.save()
                    messages.info(
                        self.request, info_message)
                    return redirect("member:my_profile")
            except ObjectDoesNotExist:
                # something is wrong here rerender the form, with message
                message = get_message('error', 3)
                messages.warning(
                    self.request, message)

                addresses = Address.objects.filter(user=theUser)

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'addresses': addresses
                }

                return render(self.request, "member/company.html", context)

        else:
            # form not valid rerender
            message = get_message('error', 4)
            messages.warning(
                self.request, message)

            addresses = Address.objects.filter(user=theUser)

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'addresses': addresses
            }

            return render(self.request, "member/company.html", context)


class Overview(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:

            # get the orders

            try:
                orders = Order.objects.filter(
                    user=self.request.user, ordered=True, being_delivered=False)

            except ObjectDoesNotExist:
                orders = {}

            context = {
                'gdpr_check': gdpr_check,
                'order_a': orders,
            }

            return render(self.request, "member/my_overview.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 5)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class Orders(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:

            # get the orders and sort out active ones
            try:
                orders_a = Order.objects.filter(
                    user=self.request.user, ordered=True)
            except ObjectDoesNotExist:
                orders_a = {}

            # get all the items and their discounts

            context = {
                'gdpr_check': gdpr_check,
                'orders_a': orders_a,
            }

            return render(self.request, "member/my_orders.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 6)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class OrderView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        message = get_message('error', 7)
        messages.warning(
            self.request, message)
        return redirect("member:my_orders")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                noCoupons = False

                if order.coupon is not None:
                    coupon_id = order.coupon.id

                    couponsQuery = Coupon.objects.filter(id=coupon_id)

                    for coupon in couponsQuery:
                        coupons = coupon
                else:
                    noCoupons = True

                theOrder = Order()
                theOrderItems = {}

                # get all the items and their discounts
                for order in orderQuery:
                    theOrderItems = order.items.all()
                    theOrder = order

                context = {
                    'gdpr_check': gdpr_check,
                    'order': theOrder,
                    'all_order_items': theOrderItems,
                    'shipping_address': shipping_address,
                    'billing_address': billing_address,
                    'coupons': coupons,
                    'noCoupons': noCoupons,
                }

                return render(self.request, "member/my_order.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 7)
            messages.warning(
                self.request, message)
            return redirect("member:my_orders")


class SupportView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                'gdpr_check': gdpr_check,
                'support': errands,
                'errands_a': errands_a,
            }

            return render(self.request, "member/my_support.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 8)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class NewErrandView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # new errand

            form = InitialSupportForm()

            context = {
                'gdpr_check': gdpr_check,
                'form': form
            }

            return render(self.request, "member/new_errand.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 9)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class ErrandView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                'gdpr_check': gdpr_check,
                'errand': errand,
                'responces': responces,
            }

            return render(self.request, "member/my_errand.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 10)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class Profile(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get user info
            try:
                info = UserInfo.objects.get(user=self.request.user)
                print(info.company)
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
                'gdpr_check': gdpr_check,
                'user': self.request.user,
                'info': info,
                'company': company,
                'addresses': addresses,
            }

            return render(self.request, "member/my_profile.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 11)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        if 'delete' in self.request.POST.keys():
            # deleting adress
            if 'id' in self.request.POST.keys():
                a_id = int(self.request.POST['id'])
                theAddress = Address.objects.get(id=a_id)
                # check that this address isn't connected to a company
                addressUnconnected = False
                try:
                    numberOfCompanies = CompanyInfo.objects.filter(
                        addressID=theAddress).count()
                    if numberOfCompanies >= 1:
                        # a company with that address exists
                        message = get_message('error', 12)
                        messages.warning(
                            self.request, message)
                        return redirect("member:my_profile")
                    else:
                        # no companies with that address
                        addressUnconnected = True
                except ObjectDoesNotExist:
                    # no companies with that address
                    addressUnconnected = True

                info_message = get_message('info', 3)
                theAddress.delete()
                messages.info(
                    self.request, info_message)
                return redirect("member:my_profile")
        else:
            messages.info(
                self.request, "Något gick fel. Om detta återupprepas kontakta supporten för hjälp.")
            return redirect("member:my_profile")


class changePassword(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        message = get_message('error', 131)
        messages.warning(
            self.request, message)
        return redirect("member:my_profile")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if 'change' in self.request.POST.keys():
            userID = int(self.request.POST['change'])
            theUser = User.objects.get(id=userID)

            # we use this view for all accounts so test for group

            groupTest = theUser.groups.all()

            print(groupTest)
            if len(groupTest) > 1:
                message = "Något gick fel. Om detta fortsätter inträffa kontakta supporten."
                messages.warning(
                    self.request, message)
                return redirect("core:home")
            else:
                theGroup = str(groupTest[0])
            # get form for this
            print(theGroup)

            form = changePasswordForm()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'theGroup': theGroup,
                'theUser': theUser,
            }

            return render(self.request, "member/change_password.html", context)
        if 'save' in self.request.POST.keys():
            userID = int(self.request.POST['save'])
            theUser = User.objects.get(id=userID)
            form = changePasswordForm(self.request.POST)
            if form.is_valid():
                old_password = form.cleaned_data.get('old_password')
                new_password = form.cleaned_data.get('new_password')
                a_user = authenticate(
                    username=theUser.username, password=old_password)
                if a_user is not None:
                    theUser.set_password(new_password)
                    update_session_auth_hash(self.request, theUser)
                    theUser.save()
                    groups = theUser.groups.all()
                    group = "none"
                    for g in groups:
                        group = g
                    group1 = Group.objects.get(name="client")
                    group2 = Group.objects.get(name="moderator")
                    group3 = Group.objects.get(name="support")
                    if group == group1:
                        message = get_message('info', 81)
                        messages.info(
                            self.request, 83)
                        return redirect("member:my_profile")
                    elif group == group2:
                        message = get_message('info', 84)
                        messages.info(
                            self.request, message)
                        return redirect("moderator:my_profile")
                    elif group == group3:
                        message = get_message('error', 134)
                        messages.info(
                            self.request, message)
                        return redirect("support:my_profile")
                    else:
                        # we have a user without a group despite being able to change password. Place it in client for now and notify IT
                        return redirect("member:my_profile")
                else:

                    context = {
                        'gdpr_check': gdpr_check,
                        'form': form,
                        'theUser': theUser,
                    }

                    message = get_message('info', 82)
                    messages.info(
                        self.request, message)
                    return redirect("member:my_profile")

                    return render(self.request, "member/change_password.html", context)
            else:

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'theUser': theUser,
                }

                return render(self.request, "member/change_password.html", context)
        else:
            # catch fail
            message = get_message('error', 132)
            messages.warning(
                self.request, message)
            return redirect("member:my_profile")


class InfoView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get form for this using the user id

            form = UserInformationForm(the_User=self.request.user)

            # check if there is a company connected
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'info': info,
            }

            return render(self.request, "member/my_info.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 14)
            messages.warning(
                self.request, message)
            return redirect("member:my_profile")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        form = UserInformationForm(self.request.POST)
        theUser = self.request.user

        if 'edit' in self.request.POST.keys():

            # check if there is a company connected
            try:
                info = UserInfo.objects.get(user=theUser)
            except ObjectDoesNotExist:
                info = UserInfo()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'info': info,
            }

            return render(self.request, "member/my_info.html", context)

        if form.is_valid():
            info_message = get_message('info', 4)
            try:
                info = UserInfo.objects.get(user=self.request.user)
                info.first_name = form.cleaned_data.get('first_name')
                theUser.first_name = form.cleaned_data.get('first_name')
                info.last_name = form.cleaned_data.get('last_name')
                theUser.last_name = form.cleaned_data.get('last_name')
                info.email = form.cleaned_data.get('email')
                theUser.email = form.cleaned_data.get('email')
                info.telephone = form.cleaned_data.get('telephone')
                theUser.save()
                info.save()
                messages.info(
                    self.request, info_message)
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
                self.request, info_message)
            return redirect("member:my_profile")
        else:
            try:
                info = UserInfo.objects.get(user=self.request.user)
            except ObjectDoesNotExist:
                info = UserInfo()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'info': info,
            }

            message = get_message('error', 15)
            messages.warning(
                self.request, message)

            return render(self.request, "member/my_info.html", context)

# switch this to SetupAddressForm


class Editaddress(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # which adress
            page = where_am_i(self)
            # get the address
            address = Address.objects.get(
                user=self.request.user, slug=page)

            # get form

            form = addressForm(address)

            ADDRESS_CHOICES_EXTENDED = [
                {'key': 'B', 'name': 'Fakturaaddress'},
                {'key': 'S', 'name': 'Leveransaddress'},
            ]

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'address': address,
                'address_choices': ADDRESS_CHOICES_EXTENDED
            }

            return render(self.request, "member/edit_address.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 16)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:

            # which adress
            slug = where_am_i(self)
            # get the address
            address = Address.objects.get(slug=slug)
            print("original")
            print(address.street_address)
            print(address.apartment_address)
            print(address.post_town)
            print(address.zip)
            print(address.country)
            print(address.address_type)
            print(address.default)
            # get the user
            theUser = self.request.user
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
                print("new")
                print(address.street_address)
                print(address.apartment_address)
                print(address.post_town)
                print(address.zip)

                if 'address_type' in self.request.POST.keys():
                    address_type = self.request.POST['address_type']
                    print(address_type)
                    if address_type == "B":
                        # check that we dont already have one
                        addresses = Address.objects.filter(
                            user=theUser, address_type="B")
                        same = False
                        for a in addresses:
                            if a.street_address == address.street_address and a.post_town == address.post_town:
                                same = True
                        if same:
                            # abort
                            message = "Addressen finns redan som Faktureringsaddress"
                            messages.warning(self.request, message)

                            ADDRESS_CHOICES_EXTENDED = [
                                {'key': 'B', 'name': 'Fakturaaddress'},
                                {'key': 'S', 'name': 'Leveransaddress'},
                            ]

                            context = {
                                'gdpr_check': gdpr_check,
                                'form': form,
                                'address': address,
                                'address_choices': ADDRESS_CHOICES_EXTENDED
                            }

                            return render(self.request, "member/edit_address.html", context)
                        else:
                            address.address_type = "B"

                    elif address_type == "S":
                        # check that we dont already have one
                        addresses = Address.objects.filter(
                            user=theUser, address_type="S")
                        same = False
                        for a in addresses:
                            if a.street_address == address.street_address and a.post_town == address.post_town:
                                same = True
                        if same:
                            # abort
                            message = "Addressen finns redan som Leveransaddress"
                            messages.warning(self.request, message)

                            ADDRESS_CHOICES_EXTENDED = [
                                {'key': 'B', 'name': 'Fakturaaddress'},
                                {'key': 'S', 'name': 'Leveransaddress'},
                            ]

                            context = {
                                'gdpr_check': gdpr_check,
                                'form': form,
                                'address': address,
                                'address_choices': ADDRESS_CHOICES_EXTENDED
                            }

                            return render(self.request, "member/edit_address.html", context)
                        else:
                            address.address_type = "S"
                    else:
                        # someone is manipulating the code
                        message = get_message('error', 17)
                        messages.warning(
                            self.request, message)
                        return redirect("member:my_profile")
                else:
                    # rerender form
                    ADDRESS_CHOICES_EXTENDED = [
                        {'key': 'B', 'name': 'Fakturaaddress'},
                        {'key': 'S', 'name': 'Leveransaddress'},
                    ]

                    context = {
                        'gdpr_check': gdpr_check,
                        'form': form,
                        'address': address,
                        'address_choices': ADDRESS_CHOICES_EXTENDED
                    }

                    return render(self.request, "member/edit_address.html", context)

                if 'default_address' in self.request.POST.keys():
                    new_address_default(address)
                else:
                    if address.default:
                        address.default = False

                print(address.address_type)
                print(address.default)
                newSlug = create_slug_address(address)
                address.slug = newSlug

                # save the address and return to list
                address.save()
                print("end")
                info_message = get_message('info', 5)
                messages.info(self.request, info_message)
                ADDRESS_CHOICES_EXTENDED = [
                    {'key': 'B', 'name': 'Fakturaaddress'},
                    {'key': 'S', 'name': 'Leveransaddress'},
                    {'key': 'BOTH', 'name': 'Båda'},
                ]

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'address': address,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }

                return render(self.request, "member/edit_address.html", context)
            else:
                # rerender form

                ADDRESS_CHOICES_EXTENDED = [
                    {'key': 'B', 'name': 'Fakturaaddress'},
                    {'key': 'S', 'name': 'Leveransaddress'},
                    {'key': 'BOTH', 'name': 'Båda'},
                ]

                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                    'address': address,
                    'address_choices': ADDRESS_CHOICES_EXTENDED
                }

                return render(self.request, "member/edit_address.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 18)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class Newaddress(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        # get form for this using the user id
        form = NewAddressForm()

        context = {
            'gdpr_check': gdpr_check,
            'form': form,
        }

        return render(self.request, "member/new_address.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            form = NewAddressForm(self.request.POST or None)
            theUser = self.request.user

            if form.is_valid():
                # start by checking that we dont already have this address
                addresses = Address.objects.filter(user=theUser)
                # check each address to compare to the new one
                for anAddress in addresses:
                    # check the street
                    if form.cleaned_data.get(
                            'street_address') == anAddress.street_address:
                        # as streets can occur in more than one town check town
                        if form.cleaned_data.get(
                                'post_town') == anAddress.post_town:
                            # if we are here we have the address already but it might be that we also want it as the other type, so check for that
                            if form.cleaned_data.get('address_type') == "A":
                                # we want this address to occur as both types, check that it doesnt already occur as the other though
                                if anAddress.address_type == "S":
                                    check_same = False
                                    secondary_check_addresses = Address.objects.filter(
                                        user=theUser, address_type="B")
                                    for s_c_address in secondary_check_addresses:
                                        if form.cleaned_data.get('street_address') == anAddress.street_address:
                                            if form.cleaned_data.get(
                                                    'post_town') == anAddress.post_town:
                                                # we already have both types of this address
                                                check_same = True
                                                check_same_object = s_c_address
                                    # check if the address was default but is/isnt now
                                    if 'default_address' in self.request.POST.keys() and not anAddress.default:
                                        new_address_default(anAddress)
                                    # check if we found a second address
                                    if check_same:
                                        # we already have the address check if we asked for default
                                        if 'default_address' in self.request.POST.keys() and not check_same_object.default:
                                            new_address_default(
                                                check_same_object)
                                        messages.info(
                                            self.request, "Addressinformation uppdaterad")
                                        return redirect("member:my_profile")
                                    else:
                                        # we want both but only have one, create a new address
                                        new_address = Address()
                                        new_address.user = anAddress.user
                                        new_address.street_address = anAddress.user
                                        new_address.apartment_address = anAddress.user
                                        new_address.post_town = anAddress.user
                                        new_address.country = anAddress.user
                                        new_address.zip = anAddress.user
                                        new_address.address_type = anAddress.user
                                        new_address.save()
                                        new_slug = create_slug_address(
                                            new_address)
                                        new_address.slug = new_slug
                                        new_address.save()
                                        # correct for default
                                        if 'default_address' in self.request.POST.keys():
                                            new_address_default(new_address)
                                        messages.info(
                                            self.request, "Addressinformation uppdaterad")
                                        return redirect("member:my_profile")
                                elif anAddress.address_type == "B":
                                    check_same = False
                                    secondary_check_addresses = Address.objects.filter(
                                        user=theUser, address_type="S")
                                    for s_c_address in secondary_check_addresses:
                                        if form.cleaned_data.get('street_address') == anAddress.street_address:
                                            if form.cleaned_data.get(
                                                    'post_town') == anAddress.post_town:
                                                # we already have both types of this address
                                                check_same = True
                                                check_same_object = s_c_address
                                    # check if the address was default but is/isnt now
                                    if 'default_address' in self.request.POST.keys() and not anAddress.default:
                                        new_address_default(anAddress)
                                    # check if we found a second address
                                    if check_same:
                                        # we already have the address check if we asked for default
                                        if 'default_address' in self.request.POST.keys() and not check_same_object.default:
                                            new_address_default(
                                                check_same_object)
                                        messages.info(
                                            self.request, "Addressinformation uppdaterad")
                                        return redirect("member:my_profile")
                                    else:
                                        # we want both but only have one, create a new address
                                        new_address = Address()
                                        new_address.user = anAddress.user
                                        new_address.street_address = anAddress.user
                                        new_address.apartment_address = anAddress.user
                                        new_address.post_town = anAddress.user
                                        new_address.country = anAddress.user
                                        new_address.zip = anAddress.user
                                        new_address.address_type = anAddress.user
                                        new_address.save()
                                        new_slug = create_slug_address(
                                            new_address)
                                        new_address.slug = new_slug
                                        new_address.save()
                                        # correct for default
                                        if 'default_address' in self.request.POST.keys():
                                            new_address_default(new_address)
                                        messages.info(
                                            self.request, "Addressinformation uppdaterad")
                                        return redirect("member:my_profile")
                            elif anAddress.address_type == form.cleaned_data.get('address_type'):
                                info_message = get_message('info', 6)
                                if 'default_address' in self.request.POST.keys() and not anAddress.default:
                                    # remove default from other addresses of same type
                                    new_address_default(anAddress)
                                    info_message = get_message(
                                        'info', 7)
                                messages.info(
                                    self.request, info_message)
                                return redirect("member:my_profile")
                # we dont have an address else we would have already been rerouted
                address = Address()

                address.user = theUser
                address.street_address = form.cleaned_data.get(
                    'street_address')
                address.apartment_address = form.cleaned_data.get(
                    'apartment_address')
                address.post_town = form.cleaned_data.get('post_town')
                address.zip = form.cleaned_data.get('zip')
                address.country = "Sverige"

                # check what kind of address we have
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

                    address2.address_type = "S"

                    # save the second copy of the address
                    address2.save()
                    # create a unique slug
                    address2.slug = create_slug_address(address2)
                    address2.save()
                    if 'default_address' in self.request.POST.keys():
                        new_address_default(address2)
                    address.address_type = "B"
                else:
                    address.address_type = address_type
                # save the address and return to list
                address.save()
                # create a unique slug
                address.slug = create_slug_address(address)
                print(address.slug)
                address.save()

                if 'default_address' in self.request.POST.keys():
                    new_address_default(address)
                info_message = get_message('info', 10)
                messages.info(self.request, info_message)
                return redirect("member:my_profile")
            else:
                context = {
                    'gdpr_check': gdpr_check,
                    'form': form,
                }

                return render(self.request, "member/new_address.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 19)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class Settings(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # obs make a form view for editing info and adding info

            try:
                cookieSettings = Cookies.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                cookieSettings = {}

            context = {
                'gdpr_check': gdpr_check,
                'cookies': cookieSettings,
            }

            return render(self.request, "member/my_settings.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 20)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class CookieSettingsView(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get cookie model, fill in with previous info if there is any
            user = self.request.user
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
                'gdpr_check': gdpr_check,
                'cookie_settings': cookie_settings,
                'form': form,
            }

            return render(self.request, "cookie_settings.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 30)
            messages.warning(
                self.request, message)
            return redirect("core:home")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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

                    info_message = get_message('info', 17)
                    messages.info(
                        self.request, info_message)
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
                    'gdpr_check': gdpr_check,
                    'cookie_settings': cookie_settings,
                    'form': form,
                }

                return render(self.request, "cookie_settings.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 31)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class GenericSupportFormView(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # get a form
            form = GenericSupportForm()

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
            }

            return render(self.request, "member/support.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 32)
            messages.warning(
                self.request, message)
            return redirect("core:home")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
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
                    message = get_message('error', 33)
                    messages.warning(
                        self.request, message)

                    context = {
                        'gdpr_check': gdpr_check,
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
                info_message = get_message('info', 18)
                messages.info(
                    self.request, info_message)
                return redirect("core:home")

            # form isn't valid rerender

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
            }

            return render(self.request, "member/support.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 34)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class GDPRInformationRequest(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        context = {
            'gdpr_check': gdpr_check,
        }

        the_user_lazy = self.request.user
        # get user info
        the_user = UserInfo.objects.get(user=the_user_lazy)
        # get company info if company
        if the_user.company:
            company = CompanyInfo.objects.get(user=the_user_lazy)
        else:
            company = []
        # get addresses
        addresses = Address.objects.filter(user=the_user_lazy)
        # get orders
        orders = Order.objects.filter(user=the_user_lazy)

        all_orders = []

        for order in orders:
            orderItems = order.items.all()
            all_orders.append({
                'order': order,
                'orderitems': orderItems,
            })

        # get orderitems
        orderItems = OrderItem.objects.filter(user=the_user_lazy)
        # get settings
        cookie_settings = Cookies.objects.filter(user=the_user_lazy)
        # get support the internal system isnt set up yet notify the user and add a request all support errand info button

        # add all info to all_of_it

        all_of_it = {
            "User_information": the_user,
            "Has_company": the_user.company,
            "Company": company,
            "Addresses": addresses,
            "Orders": all_orders,
            "Items_ordered": orderItems,
            "Settings": cookie_settings,
        }

        context.update(
            {'user_info': all_of_it})

        return render(self.request, "member/information_request.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        context = {
            'gdpr_check': gdpr_check,
        }

        if 'back' in self.request.POST.keys():
            return redirect("member:my_profile")

        if "download" in self.request.POST.keys():

            the_user_lazy = self.request.user
            # get user info
            UI = UserInfo.objects.get(user=the_user_lazy)
            if UI != None:
                if UI.company:
                    CID = UI.companyID.id
                else:
                    CID = ""
                the_user = {
                    'user': UI.user.username,
                    'first_name': UI.first_name,
                    'last_name': UI.last_name,
                    'email': UI.email,
                    'telephone': UI.telephone,
                    'company': UI.company,
                    'companyID': CID,
                }
                # get company info if company
                if UI.company:
                    CI = CompanyInfo.objects.get(user=the_user_lazy)
                    company = {
                        'user': UI.user.username,
                        'company': CI.company,
                        'organisation_number': CI.organisation_number,
                        'addressID': CI.addressID.id,
                    }
                else:
                    company = []
            else:
                the_user = []
                company = []
            # get addresses
            A = Address.objects.filter(user=the_user_lazy)
            addresses = []
            for a in A:
                the_type = ""
                if a.address_type == "B":
                    the_type = 'Faktureringsaddress'
                else:
                    the_type = 'Leveransaddress'

                address = {
                    'id': a.id,
                    'user': a.user.username,
                    'street_address': a.street_address,
                    'apartment_address': a.apartment_address,
                    'post_town': a.post_town,
                    'country': str(a.country),
                    'zip': a.zip,
                    'address_type': the_type,
                    'default': a.default,
                }
                addresses.append(address)
            # get orders
            O = Order.objects.filter(user=the_user_lazy)

            all_orders = []

            for o in O:

                o_I = o.items.all()
                if o.freight != None:
                    OFreight = o.freight.title
                else:
                    OFreight = ""

                if o.coupon != None:
                    Ocoupon = o.coupon.id
                else:
                    Ocoupon = ""

                if o.shipping_address != None:
                    shipping_address_id = o.shipping_address.id
                else:
                    shipping_address_id = "Borttagen"

                if o.billing_address != None:
                    billing_address_id = o.billing_address.id
                else:
                    billing_address_id = "Borttagen"
                order = {
                    'id': o.id,
                    'user': o.user.username,
                    'ref_code': o.ref_code,
                    'total_price': o.total_price,
                    'freight': OFreight,
                    'freight_price': o.freight_price,
                    'ordered_date': str(o.ordered_date),
                    'ordered': o.ordered,
                    'shipping_address_id': shipping_address_id,
                    'billing_address_id': billing_address_id,
                    'coupon': Ocoupon,
                    'sent': o.being_delivered,
                    'order_canceled': o.canceled,
                    'returned': o.returned,
                    'refund_requested': o.refund_requested,
                    'refund_granted': o.refund_granted,
                }

                orderItems = []

                for oI in o_I:
                    orderItem = {
                        'id': oI.id,
                        'user': oI.user.username,
                        'ordered': o.ordered,
                        'item_id': oI.item.id,
                        'title': oI.title,
                        'quantity': oI.quantity,
                        'price': oI.price,
                        'discount_price': oI.discount_price,
                        'total_price': oI.total_price,
                        'sent': oI.sent,
                        'returned': oI.returned,
                        'canceled': oI.canceled,
                        'refund_requested': oI.refund_flag,
                        'refund_granted': oI.refund,
                    }
                    orderItems.append(orderItem)

                all_orders.append({
                    'order': order,
                    'orderitems': orderItems,
                })

            # get settings
            CS = Cookies.objects.get(user=the_user_lazy)
            if CS != None:
                cookie_settings = {
                    'user': CS.user.username,
                    'functional': CS.functional,
                }
            else:
                cookie_settings = []
            # get support the internal system isnt set up yet notify the user and add a request all support errand info button

            # add all info to all_of_it

            all_of_it = {
                "User_information": the_user,
                "Company": company,
                "Addresses": addresses,
                "Orders": all_orders,
                "Settings": cookie_settings,
            }

            # create the file with the all_of_it in it and then  send download request, display page as normal or redirect here

            # make all of it JSON
            content = json.dumps(all_of_it)
            response = HttpResponse(content, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=myinfo.json'
            return response

        return render(self.request, "member/information_request.html", context)


class GDPRErraseRequest(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        return render(self.request, "member/deletion_request.html")

    def post(self, *args, **kwargs):
        # test for delete or back

        # back
        if 'back' in self.request.POST.keys():

            return redirect("member:my_profile")

        # delete and anonymize data of the user
        elif 'delete' in self.request.POST.keys():
            # get all information that is connected to the user
            # user object
            the_user_lazy = self.request.user
            # get user info
            the_user = UserInfo.objects.get(user=the_user_lazy)
            # get company info if company
            if the_user.company:
                company = CompanyInfo.objects.get(user=the_user_lazy)
            else:
                company = []
            # get addresses
            addresses = Address.objects.filter(user=the_user_lazy)

            # get settings
            cookie_settings = Cookies.objects.filter(user=the_user_lazy)

            # anonymise where necessary
            # user object

            the_user_lazy.username = get_anonymous_user()
            the_user_lazy.email = ""
            the_user_lazy.is_active = False

            groups = the_user_lazy.groups.all()
            for group in groups:
                the_user_lazy.groups.remove(group)

            the_user_lazy.save()
            the_user_lazy.groups

            # user addresses

            for address in addresses:
                address.delete()

            # user company

            if the_user.company:
                company.delete()

            # user info

            the_user.delete()

            # orders anonymous due to user anonymous and addresses being deleted
            # cookies

            cookie_settings.delete()

            return redirect("core:home")
        else:

            return render(self.request, "member/deletion_request.html")

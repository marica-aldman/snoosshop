from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth import authenticate, login, update_session_auth_hash
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
from core.info_error_msg import *


class Setup(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
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
            'userForm': form_user,
            'companyForm': form_company,
            'addressForm': form_address,
        }

        return render(self.request, "member/setup.html", context)

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
        except ObjectDoesNotExist:
            message = get_message('error', 2)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class CompanyView(LoginRequiredMixin, View):
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
                'form': form,
                'addresses': addresses
            }

            return render(self.request, "member/company.html", context)


class Overview(LoginRequiredMixin, View):
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
            message = get_message('error', 5)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class Orders(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:

            # get the orders and sort out active ones
            try:
                orders_a = Order.objects.filter(
                    user=self.request.user, ordered=True, received=False, subscription_order=False)
                orders_r = Order.objects.filter(
                    user=self.request.user, ordered=True, received=True)
            except ObjectDoesNotExist:
                orders_a = {}
                orders_r = {}

            # get all the items and their discounts

            context = {
                'orders_r': orders_r,
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
                    'noCoupons': noCoupons,
                    'payment': payments,
                }

                return render(self.request, "member/my_order.html", context)

        except ObjectDoesNotExist:
            message = get_message('error', 7)
            messages.warning(
                self.request, message)
            return redirect("member:my_orders")


class SupportView(LoginRequiredMixin, View):
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
            message = get_message('error', 8)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class NewErrandView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            # new errand

            form = InitialSupportForm()

            context = {
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
            message = get_message('error', 10)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class Profile(LoginRequiredMixin, View):
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
                # check that this address isn't connected to a subscription
                try:
                    numberOfSubscriptionsShipping = Subscription.objects.filter(
                        shipping_address=theAddress).count()
                    numberOfSubscriptionsBilling = Subscription.objects.filter(
                        billing_address=theAddress).count()
                    if numberOfSubscriptionsBilling >= 1 or numberOfSubscriptionsShipping >= 1:
                        # a subscription is tied to this address
                        message = get_message('error', 13)
                        messages.warning(
                            self.request, message)
                        return redirect("member:my_profile")
                    else:
                        # no subsriptions with that address set conenction to true
                        addressUnconnected = True

                except ObjectDoesNotExist:
                    # no subscriptions with that address
                    addressUnconnected = True
                info_message = get_message('info', 3)
                theAddress.delete()
                messages.info(
                    self.request, info_message)
                return redirect("member:my_profile")


class changePassword(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        message = get_message('error', 131)
        messages.warning(
            self.request, message)
        return redirect("member:my_profile")

    def post(self, *args, **kwargs):
        if 'change' in self.request.POST.keys():
            userID = int(self.request.POST['change'])
            theUser = User.objects.get(id=userID)
            # get form for this

            form = changePasswordForm()

            context = {
                'form': form,
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
                        print("herec")
                        return redirect("member:my_profile")
                    elif group == group2:
                        message = get_message('info', 84)
                        messages.info(
                            self.request, message)
                        print("herem")
                        return redirect("moderator:my_profile")
                    elif group == group3:
                        message = get_message('error', 134)
                        messages.info(
                            self.request, message)
                        print("heres")
                        return redirect("support:my_profile")
                    else:
                        # we have a user without a group despite being able to change password. Place it in client for now and notify IT
                        print("herer")
                        return redirect("member:my_profile")
                else:

                    context = {
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
            message = get_message('error', 14)
            messages.warning(
                self.request, message)
            return redirect("member:my_profile")

    def post(self, *args, **kwargs):
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
            info_message = get_message('info', 4)
            try:
                info = UserInfo.objects.get(user=self.request.user)
                info.first_name = form.cleaned_data.get('first_name')
                info.last_name = form.cleaned_data.get('last_name')
                info.email = form.cleaned_data.get('email')
                info.telephone = form.cleaned_data.get('telephone')

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
                ]

                context = {
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
        try:
            # which adress
            slug = where_am_i(self)
            # get the address
            address = Address.objects.get(slug=slug)
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
                address.country = "Sverige"
                if 'address_type' in self.request.POST.keys():
                    address_type = self.request.POST['address_type']
                    if address_type == "B":
                        address.address_type = "B"
                    elif address_type == "S":
                        address.address_type = "B"
                    else:
                        # someone is manipulating the code
                        message = get_message('error', 17)
                        messages.warning(
                            self.request, message)
                        return redirect("member:my_profile")
                else:
                    # rerender form
                    ADDRESS_CHOICES_EXTENDED = [
                        {'key': 'B', 'name': 'Billing'},
                        {'key': 'S', 'name': 'Shipping'},
                    ]

                    context = {
                        'form': form,
                        'address': address,
                        'address_choices': ADDRESS_CHOICES_EXTENDED
                    }

                    return render(self.request, "member/edit_address.html", context)
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
                info_message = get_message('info', 5)
                messages.info(self.request, info_message)
                return redirect("member:my_profile")
            else:
                # rerender form
                ADDRESS_CHOICES_EXTENDED = [
                    {'key': 'B', 'name': 'Billing'},
                    {'key': 'S', 'name': 'Shipping'},
                ]

                context = {
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
        # get form for this using the user id
        form = NewAddressForm()

        context = {
            'form': form,
        }

        return render(self.request, "member/new_address.html", context)

    def post(self, *args, **kwargs):
        try:
            form = NewAddressForm(self.request.POST or None)
            theUser = self.request.user

            if form.is_valid():
                # start by checking that we dont already have this address
                sameBilling = 0
                sameShipping = 0
                addresses = Address.objects.filter(user=theUser)
                for anAddress in addresses:
                    if form.cleaned_data.get(
                            'street_address') == anAddress.street_address:
                        if form.cleaned_data.get(
                                'post_town') == anAddress.post_town:
                            if form.cleaned_data.get('address_type') == "A":
                                if anAddress.address_type == "S":
                                    sameShipping = anAddress.id
                                elif anAddress.address_type == "B":
                                    sameBilling = anAddress.id
                            elif anAddress.address_type == form.cleaned_data.get('address_type'):
                                message = get_message('info', 6)
                                if 'default_address' in self.request.POST.keys() and not anAddress.default:
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
                                    info_message = get_message(
                                        'info', 7)
                                messages.info(
                                    self.request, info_message)
                                return redirect("member:my_profile")
                # get values
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

                # confirm that it isn't the same type as we already have (this only happens when we save both) set the values to the one we don't already have unless we have both saved
                if sameBilling > 0 and sameShipping > 0:
                    # test for defaulting
                    testShipping = Address.objects.get(id=sameShipping)
                    testBilling = Address.objects.get(id=sameBilling)
                    message = get_message('info', 8)
                    if 'default_address' in self.request.POST.keys():
                        addresses = Address.objects.filter(user=theUser)
                        if not testShipping.default:
                            # remove default from other addresses of same type
                            for sameAddress in addresses:
                                if sameAddress.address_type == 'S':
                                    if sameAddress.default:
                                        sameAddress.default = False
                                        sameAddress.save()
                            # change the test one to true here
                            testShipping.default = True
                            testShipping.save()
                        if not testBilling.default:
                            testBilling.default = True
                            testBilling.save()
                            # remove default from other addresses of same type
                            for sameAddress in addresses:
                                if sameAddress.address_type == 'B':
                                    if sameAddress.default:
                                        sameAddress.default = False
                                        sameAddress.save()
                            # change the thest one to true here
                            testBilling.default = True
                            testBilling.save()
                        message = get_message('info', 9)

                    messages.info(
                        self.request, message)
                    return redirect("member:my_profile")
                elif sameBilling > 0:
                    address_type = "S"
                elif sameShipping > 0:
                    address_type = "B"

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
                        address2.default = True
                        new_address_default(address2)

                    address2.address_type = "S"
                    address2.slug = create_slug_address(address2)

                    # save the second copy of the address
                    address2.save()
                    address.address_type = "B"
                else:
                    address.address_type = address_type

                if 'default_address' in self.request.POST.keys():
                    address.default = True
                    new_address_default(address)
                # create a slug
                address.slug = create_slug_address(address)
                # save the address and return to list
                address.save()
                info_message = get_message('info', 10)
                messages.info(self.request, info_message)
                return redirect("member:my_profile")
            else:
                context = {
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
            message = get_message('error', 20)
            messages.warning(
                self.request, message)
            return redirect("member:my_overview")


class CookieSettingsView(View):
    def get(self, *args, **kwargs):
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
        try:
            # get a form
            form = GenericSupportForm()

            context = {
                'form': form,
            }

            return render(self.request, "member/support.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 32)
            messages.warning(
                self.request, message)
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
                    message = get_message('error', 33)
                    messages.warning(
                        self.request, message)

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
                info_message = get_message('info', 18)
                messages.info(
                    self.request, info_message)
                return redirect("core:home")

            # form isn't valid rerender

            context = {
                'form': form,
            }

            return render(self.request, "member/support.html", context)
        except ObjectDoesNotExist:
            message = get_message('error', 34)
            messages.warning(
                self.request, message)
            return redirect("core:home")


class CancelOrder(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 133)
        messages.warning(
            self.request, message)
        return redirect("support:orders")

    def post(self, *args, **kwargs):
        try:
            test = "test"
        except ObjectDoesNotExist:
            test = "test"


class ReturnOrder(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 134)
        messages.warning(
            self.request, message)
        return redirect("support:orders")

    def post(self, *args, **kwargs):
        try:
            test = "test"
        except ObjectDoesNotExist:
            test = "test"


class ReturnItem(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 135)
        messages.warning(
            self.request, message)
        return redirect("support:orders")

    def post(self, *args, **kwargs):
        test = "test"

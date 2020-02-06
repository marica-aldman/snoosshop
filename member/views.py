from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View, FormView
from django.shortcuts import redirect
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, CompanyInfo, UserInfo, SupportThread, SupportResponces, Subscription, Cookies, SubscriptionItem
from .forms import ProfileForm, InitialSupportForm, addressForm, NewSubscriptionForm, NewAddressForm, EditSubscriptionForm
from django.utils.dateparse import parse_datetime


# add save functions and button functions as well as the actual content to the templates, also add forms for cookie settings and settings as well as further contact form for support


class Setup(View):
    def get(self, *args, **kwargs):
        try:
            form = InitialForm()

            context = {
                'form': form,
            }

            return render(self.request, "member/setup.html", form)


        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your overview. Contact the support for assistance.")
            return redirect("core:home")


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
            today = datetime.now()

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
                orders = Order.objects.filter(user=self.request.user, ordered=True)
            except ObjectDoesNotExist:
                orders = {}

            order1 = []
            order2 = []
            today = datetime.now()

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
            messages.info(self.request, "Something went wrong when accessing your overview. Contact the support for assistance.")
            return redirect("core:home")


class Orders(View):
    def get(self, *args, **kwargs):
        try:

            # get the orders and sort out active ones

            try:
                orders = Order.objects.filter(user=self.request.user, ordered=True)
            except ObjectDoesNotExist:
                orders = {}

            orders_a = []
            today = datetime.now()

            i = 0
            for order in orders:
                if not order.recieved:
                    del orders[i]
                    orders_a.append(order)
                i +=1

            # get all the items and their discounts
            
            context = {
                'orders': orders,
                'orders_a': orders_a,
            }

            return render(self.request, "member/my_orders.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your orderlistspage. Contact the support for assistance.")
            return redirect("member:my_overview")


class OrderView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            if self.request.POST['id']:
                # get the right order

                try:
                    order = Order.objects.filter(user=self.request.user, ref_code=self.request.POST['id'])
                except ObjectDoesNotExist:
                    order = {}

                # get all the items and their discounts

                orderItems = order.items
                all_items = []
                all_order_items = []
                
                for orderItem in orderItems:
                    item = orderItem.item
                    title = item.title
                    price = item.price
                    discount = item.discount_price
                    image = item.image
                    quantity = orderItem.quantity
                    total_price = orderItem.get_final_price(orderItem)
                    full_item = {
                        'title': title,
                        'price': price,
                        'discount': discount,
                        'image': image,
                        'total_price': total_price,
                        'quantity': quantity
                        }
                    all_items.append(full_item)

                # get all the addresses

                shipping_address_id = order.shipping_address
                billing_address_id = order.billing_address

                shipping_address = Address()
                shipping_address = shipping_address.objects.get(id=shipping_address_id)

                billing_address = Address()
                billing_address = billing_address.objects.get(id=billing_address_id)

                # get the cupon used

                coupon_id = order.coupon

                coupons = Coupon()
                coupons = coupons.objects.get(id=coupon_id)

                # get the payment info
                payment_id = order.payment

                payment = Payment()
                payment = payment.object.get(id=payment_id)

                context = {
                    'order': order,
                    'all_order_items': all_order_items,
                    'all_items': all_items,
                    'shipping_address': shipping_address,
                    'billing_address': billing_address,
                    'coupons': coupons,
                    'payment': payment,
                }

                return render(self.request, "member/order.html", context)
            else:
                return redirect("member:my_orders")

        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this order. Contact the support for assistance.")
            return redirect("member:my_overview")


class SupportView(View):
    def get(self, *args, **kwargs):
        try:
            # get all errands, sort out the active ones

            try:
                errands = SupportThread.objects.filter(user=self.request.user,)
            except ObjectDoesNotExist:
                errands = {}

            errands_a = []
            today = datetime.now()

            for errand in errands:
                if not errand.done:
                    errands_a.append(errand)

            context = {
                'support': errands,
                'errands_a': errands_a,
            }

            return render(self.request, "member/my_support.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing this page. Contact the support for assistance.")
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
            messages.info(self.request, "Can't find this errand. Contact the support for assistance.")
            return redirect("member:my_overview")


class ErrandView(View):
    def get(self, *args, **kwargs):
        try:
            # id check here
            if self.request.POST['lookAt']:
                try:
                    errand = SupportThread.objects.filter(user=self.request.user, ref=self.request.POST['lookAt'])
                except ObjectDoesNotExist:
                    errand = {}

                try:
                    responces = SupportResponces.objects.filter(user=self.request.user, ref=self.request.POST['lookAt'])
                except ObjectDoesNotExist:
                    responces = {}

                # add form for further contact on this issue

                context = {
                    'errand': errand,
                    'responces': responces,
                }

                return render(self.request, "member/my_errand.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this errand. Contact the support for assistance.")
            return redirect("member:my_overview")


class Profile(View):
    def get(self, *args, **kwargs):
        try:
            # get user info
            try:
                info = UserInfo.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                info = {'company': False}
            
            # company info
            try:
                company = CompanyInfo.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                company = {}

            # get company address
            company_address = ""
            """ 
            if info.company:
                try:
                    address = Address.objects.filter(id = company.addressID)
                except ObjectDoesNotExist:
                    address = {'street_address': ''}
                
                company_address = address.street_address """

            # get user addresses

            try:
                addresses = Address.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                addresses = {}

            # place info in context and render page

            context = {
                'info': info,
                'company': company,
                'company_address': company_address,
                'addresses': addresses,
            }

            return render(self.request, "member/my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")


class EditUser(View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id

            form = ProfileForm()
            form = form.__init__(form, user=self.request.user)

            context = {
                'form': form,
            }

            return render(self.request, "member/edit_my_user_info.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")


class Editaddress(View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id
            form = addressForm()
            form = form.__init__(form, user=self.request.user, id=self.request.POST['id'])

            context = {
                'form': form,
            }

            return render(self.request, "member/edit_address.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
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
            messages.info(self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")

    def post(self, *args, **kwargs):
        try:
            form = NewAddressForm(self.request.POST or None)

            if form.is_valid():

                # get values
                address = Address()

                address.user = self.request.user
                address.street_address = form.cleaned_data.get('street_address')
                address.apartment_address = form.cleaned_data.get('apartment_address')
                address.post_town = form.cleaned_data.get('post_town')
                address.post_code = form.cleaned_data.get('post_code')
                address.country = "Sverige"
                address.default_address = form.cleaned_data.get('default_address')
                
                # check that if we want the adress to be both shipping and billing
                address_type = form.cleaned_data.get('address_type')

                if address_type == "A":
                    # we want two copies of this address
                    address2 = Address()
                    address2.user = self.request.user
                    address2.street_address = form.cleaned_data.get('street_address')
                    address2.apartment_address = form.cleaned_data.get('apartment_address')
                    address2.post_town = form.cleaned_data.get('post_town')
                    address2.post_code = form.cleaned_data.get('post_code')
                    address2.country = "Sverige"
                    address2.default_address = form.cleaned_data.get('default')
                    address2.address_type = "S"
                    # check if this is set as the default address if it is remove default from all of this users addresses in the database

                    if address.default_address:
                        addresses = Address.objects.filter(user=self.request.user, default=True)
                        for address1 in addresses:
                            address1.default = False
                            address1.save()

                    # save the second copy of the adress
                    address2.save()
                    address.address_type = "B"
                else:
                    address.address_type = address_type

                    #if this is the default remove default of the same address type from the users adresses
                    if address.default_address:
                        addresses = Address.objects.filter(user=self.request.user, default=True, address_type=address_type)
                        for address1 in addresses:
                            address1.default = False
                            address1.save()

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
            messages.info(self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
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
            messages.info(self.request, "Something went wrong when accessing your settings. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionsView(View):
    def get(self, *args, **kwargs):
        try:
            # get all subscriptions
            try:
                subscriptions = Subscription.objects.filter(user=self.request.user)
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
            messages.info(self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionView(View):
    def post(self, *args, **kwargs):
        if 'saveSubscription' in self.request.POST.keys():
            # saving subscription
            # make a subscription object if new otherwise get the old one
            test = 'hi'

                # handle saving and creating of orders here
                
            # save all products and amounts
            """sub.products_set.all().delete()
            for product in self.cleaned_data['products']:
                for amount in self.cleaned_data['amounts']:
                    SubscriptionItem.objects.create(
                        user=self.request.user,
                        subscription=sub,
                        item=product,
                        quantity=amount,
                    )"""
            
        else:
            try:

                # get the form

                form = EditSubscriptionForm(self.request.user, slug=self.request.POST['slug'])

                # if we are editing get the specific Subscription
                if self.request.POST['slug'] != 'new':
                    try:
                        subscription = Subscription.objects.filter(user=self.request.user, slug=self.request.POST['slug'])
                    except ObjectDoesNotExist:
                        subscription = {}

                    sub_date = ""
                    number_of_products = 0
                
                    for sub in subscription:
                        sub_date = sub.start_date.strftime("%Y-%m-%d")
                        number_of_products = sub.number_of_items
                    
                else:
                    sub_date = datetime.now().strftime("%Y-%m-%d")
                    number_of_products = 1

                context = {
                    'form': form,
                    'sub_date': sub_date,
                    'number_of_products': number_of_products,
                }

                return render(self.request, "member/my_subscription.html", context)

            except ObjectDoesNotExist:
                messages.info(self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
                return redirect("member:my_overview")


class NewSubscriptionView(View):
    def get(self, *args, **kwargs):
        try:
            # get the users saved shipping addresses
            shipping_addresses = Address.objects.filter(
                user=self.request.user, address_type='S')

            # get the users saved billing addresses
            billing_addresses = Address.objects.filter(
                user=self.request.user, address_type='B')

            # get the form
            aform = NewSubscriptionForm()

            # get all products and place them in a json for using js to get multiple instances of products for the same subscription
            all_products = Item.objects.all()
            products = []
            products_html = "["

            for product in all_products:
                products.append({'id': product.id, 'title': product.title})
                id = str(product.id)
                title = str(product.title)
                products_html = products_html + "{&quot;id&quot;: &quot" + id + "&quot, &quot;title&quot;: &quot" + title + "&quot},"

            products_html = products_html + "]"

            # place form and product json in context
            context = {
                'form': aform,
                'products_html': products_html,
                'shipping_adress': shipping_addresses,
                'billing_addresses': billing_addresses,
            }

            return render(self.request, "member/new_subscription.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing the new subscription form. Contact the support for assistance.")
            return redirect("member:overview")

    def post(self, *args, **kwargs):
        try:

            form = NewSubscriptionForm(self.request.POST or None)

            if form.is_valid():

                # new subscription instance

                sub = Subscription()
                # take in the data

                sub.user = self.request.user
                # make sure the date is in the correct format
                sub.start_date = form.cleaned_data.get('start_date')

                sub.intervall = form.cleaned_data.get('intervall')
                sub.shipping_address = form.cleaned_data.get('shipping_address')
                sub.billing_address = form.cleaned_data.get('billing_address')
                sub.number_of_products = int(self.request.POST['number_of_products'])

                # calcuate the rest of the data

                sub.updated_date = datetime.now()
                sub.active = True

                if sub.intervall == '001':
                    # add a week
                    d = timedelta(days=7)
                    next_date = sub.start_date + d

                    sub.next_order_date = next_date

                elif sub.intervall == '002':
                    # add two weeks
                    d = timedelta(days=14)
                    next_date = sub.start_date + d

                    sub.next_order_date = next_date

                elif sub.intervall == '010':
                    # add a month
                    d = timedelta(days=30)
                    next_date = sub.start_date + d

                    sub.next_order_date = next_date
                elif sub.intervall == '020':
                    # add two months
                    d = timedelta(days=60)
                    next_date = sub.start_date + d

                    sub.next_order_date = next_date
                elif sub.intervall == '100':
                    # add six months
                    d = timedelta(days=182)
                    next_date = sub.start_date + d

                    sub.next_order_date = next_date
                elif sub.intervall == '200':
                    # add a year
                    d = timedelta(days=365)
                    next_date = sub.start_date + d

                    sub.next_order_date = next_date
                else:
                    # this shouldnt be able to happen. Add nothing
                    sub.next_order_date = sub.start_date

                # slug
                # create a slug using user id and number of subsciption the user has
                try:
                    subscriptions = Subscription.objects.filter(user=self.request.user)
                except ObjectDoesNotExist:
                    subscriptions = {}
                sub_amount = str(len(subscriptions))
                user_id = str(self.request.user.id)
                slug = "s" + sub_amount + "u" + user_id
                sub.slug = slug

                # save subscription to aquire id
                sub.save()

                # create subscription items

                i = 1

                for i in range(sub.number_of_products + 1):
                    subscription_item = SubscriptionItem()
                    subscription_item.user = self.request.user
                    p_string = "product" + str(i)
                    a_string = "amount" + str(i)
                    product_id = form.cleaned_data.get(p_string)
                    amount = form.cleaned_data.get(a_string)
                    products = Item.objects.filter(id=product_id)
                    for product in products:
                        subscription_item.item = product
                    subscription_item.amount = amount
                    subscription_item.save()
                    sub.items.add(subscription_item)

                # save the final instance of subscription
                sub.save()

                messages.info(self.request, "Subscription saved and activated")
                return redirect("member:my_subscriptions")
            # if the form is not valid
            else:
                # get the users saved shipping addresses
                shipping_addresses = Address.objects.filter(
                    user=self.request.user, address_type='S')

                # get the users saved billing addresses
                billing_addresses = Address.objects.filter(
                    user=self.request.user, address_type='B')

                # get all products and place them in a json for using js to get multiple instances of products for the same subscription
                all_products = Item.objects.all()
                products = []
                products_html = "["

                for product in all_products:
                    products.append({'id': product.id, 'title': product.title})
                    id = str(product.id)
                    title = str(product.title)
                    products_html = products_html + "{&quot;id&quot;: &quot" + id + "&quot, &quot;title&quot;: &quot" + title + "&quot},"

                products_html = products_html + "]"

                # place form and product json in context
                context = {
                    'form': form,
                    'products_html': products_html,
                    'shipping_adress': shipping_addresses,
                    'billing_addresses': billing_addresses,
                }

                return render(self.request, "member/new_subscription.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your subscription. Contact the support for assistance.")
            return redirect("member:my_overview")


class CookieSettingsView(View):
    def get(self, *args, **kwargs):
        try:
            # turn into form
            # get cookie model, fill in with previous info if there is any

            try:
                cookie_settings = Cookies.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                cookie_settings = {}

            context = {
                'cookie_settings': cookie_settings,
            }

            return render(self.request, "cookie_settings.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing the cookie settings page. Contact the support for assistance.")
            return redirect("core:home")

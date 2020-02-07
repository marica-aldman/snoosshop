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
from core.views import create_ref_code


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
                orders_a = Order.objects.filter(user=self.request.user, ordered=True, received=False)
                orders_r = Order.objects.filter(user=self.request.user, ordered=True, received=True)
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
            messages.info(self.request, "Something went wrong when accessing your orderlistspage. Contact the support for assistance.")
            return redirect("member:my_overview")


class OrderView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        try:
            try:
                orderQuery = Order.objects.filter(user=self.request.user, id=int(self.request.POST['lookAtOrder']))
                test = 'first try'

                for order in orderQuery:
                    # get all the addresses

                    shipping_address_id = order.shipping_address.id
                    billing_address_id = order.billing_address.id

                    shipping_addressQuery = Address.objects.filter(id=shipping_address_id)

                    billing_addressQuery = Address.objects.filter(id=billing_address_id)

                    shipping_address = Address()
                    billing_address = Address()

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

                    test = 'not in yet'
                    theOrder = Order()
                    theOrderItems = {}
                    theItems = {}
                    i = 1
                    j = 1

                    # get all the items and their discounts
                    for order in orderQuery:
                        orderItems = order.items.all()
                        theOrderItems = orderItems
                        theOrder = order
                        test = 'order'
                        for orderItem in orderItems:
                            i += 1
                            itemQuery = Item.objects.filter(id=orderItem.item.id)
                            test = 'orderItem'
                            for item in itemQuery:
                                theItems[j] = item
                                j += 1
                                test = 'all the way!'
                    
                    rangeNumber = ""
                    k = 1
                    for k in range(j-1):
                        k += 1
                        rangeNumber = rangeNumber + str(k)

                    context = {
                        'order': theOrder,
                        'j': rangeNumber,
                        'i': 1,
                        'all_items': theItems,
                        'all_order_items': theOrderItems,
                        'shipping_address': shipping_address,
                        'billing_address': billing_address,
                        'coupons': coupons,
                        'payment': payments,
                        "test": test,
                    }

                    return render(self.request, "member/my_order.html", context)

                    context = {
                        'order': '',
                        'all_items': '',
                        'all_order_items': '',
                        'shipping_address': '',
                        'billing_address': '',
                        'coupons': '',
                        'payment': '',
                        "test": 'total fail',
                    }

                    return render(self.request, "member/my_order.html", context)

            except ObjectDoesNotExist:
                orderQuery = {}
                test = 'first except'

                # get all the addresses

                shipping_address_id = order.shipping_address
                billing_address_id = order.billing_address

                shipping_addressQuery = Address.objects.filter(id=shipping_address_id)

                billing_addressQuery = Address.objects.filter(id=billing_address_id)

                shipping_address = Address()
                billing_address = Address()

                for address in shipping_addressQuery:
                    shipping_address = address
                    
                for address in billing_addressQuery:
                    billing_address = address
                    
                # get the cupon used

                coupon_id = order.coupon

                couponsQuery = Coupon.objects.filter(id=coupon_id)
                coupons = Coupon()

                for coupon in couponsQuery:
                    coupons = coupon

                # get the payment info
                payment_id = order.payment

                paymentQuery = Payment.objects.filter(id=payment_id)
                payments = Payment()

                for payment in paymentQuery:
                    payments = payment

                test = 'not in yet'
                # get all the items and their discounts
                for order in orderQuery:
                    orderItems = order.items.all()
                    i = 1
                    test = 'order'
                    for orderItem in orderItems:
                        itemQuery = Item.objects.filter(id=orderItem.item.id)
                        test = 'orderItem'
                        for item in itemQuery:
                            test = item.title
                            test = 'item'

                    context = {
                        'order': orderQuery,
                        'all_items': '',
                        'all_order_items': '',
                        'shipping_address': shipping_address,
                        'billing_address': billing_address,
                        'coupons': coupons,
                        'payment': payments,
                        "test": test,
                    }

                    return render(self.request, "member/my_order.html", context)

                context = {
                    'order': '',
                    'all_items': '',
                    'all_order_items': '',
                    'shipping_address': '',
                    'billing_address': '',
                    'coupons': '',
                    'payment': '',
                    "test": 'total fail',
                }

                return render(self.request, "member/my_order.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this order. Contact the support for assistance.")
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
                
                # check that if we want the address to be both shipping and billing
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

                    # save the second copy of the address
                    address2.save()
                    address.address_type = "B"
                else:
                    address.address_type = address_type

                    #if this is the default remove default of the same address type from the users addresses
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

    def post(self, *args, **kwargs):
        try:
            # if we pressed a delete button preform the delete
            message = 'start'
            if 'delete' in self.request.POST.keys():
                # get the subscription
                message = 'in delete'
                subscription = Subscription.objects.filter(user=self.request.user, id=int(self.request.POST['id']),)
                # enter the query
                for sub in subscription:
                    # check that there is an order connected
                    message = 'in sub'
                    if sub.next_order is not None:
                        message = 'in next_order'
                        # get the order
                        orderQuery = Order.objects.filter(id=sub.next_order.id)
                        test = orderQuery
                        # enter the query
                        for order in orderQuery:
                            message = 'in order'
                            # get the orderItem
                            orderItemQuery = order.items.all()
                            # enter the query
                            for orderItem in orderItemQuery:
                                message = 'in orderitem'
                                # delete order item
                                orderItem.delete()
                            # delete order
                            order.delete()
                            # delete subscription
                            sub.delete()
                            # message = 'subscription and corresponding order deleted'
                    else:
                        # delete subscription
                        sub.delete()
                        message = 'subscription deleted'
            # get all subscriptions
            try:
                subscriptions = Subscription.objects.filter(user=self.request.user,)
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
            messages.info(self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionView(View):
    def post(self, *args, **kwargs):
        try:
            # get the form

            form = EditSubscriptionForm(self.request.user, slug=self.request.POST['slug'])

            # if we are editing get the specific Subscription otherwise set values for new
            if self.request.POST['slug'] == 'new':
                sub_date = datetime.now().strftime("%Y-%m-%d")
                number_of_products = 1
                old = False
                subscription = Subscription()
            
                context = {
                    'form': form,
                    'sub_date': sub_date,
                    'number_of_products': number_of_products,
                    'old': old,
                }

                return render(self.request, "member/my_subscription.html", context)
            else:
                old = True
                try:
                    subscription = Subscription.objects.filter(user=self.request.user, slug=self.request.POST['slug'])
                    sub_date = ""
                    number_of_products = 0
                
                    for sub in subscription:
                        sub_date = sub.start_date.strftime("%Y-%m-%d")
                        number_of_products = sub.number_of_items
                    context = {
                        'form': form,
                        'sub_date': sub_date,
                        'subscription': sub,
                        'number_of_products': number_of_products,
                        'old': old,
                        'subscription': subscription,
                    }

                    return render(self.request, "member/my_subscription.html", context)
                except ObjectDoesNotExist:
                    messages.info(self.request, "Something went wrong when accessing your subscription. Contact the support for assistance.")
                    return redirect("member:my_subscriptions")

        except ObjectDoesNotExist:
                messages.info(self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
                return redirect("member:my_overview")


class SaveSubscriptionView(View):
    def post(self, *args, **kwargs):
        if 'saveSubscription' in self.request.POST.keys():
            # saving subscription
            # check if new or old
            if self.request.POST['new_or_old'] == 'old':

                # get the old subscription
                subscription = Subscription.objects.filter(user=self.request.user, id=self.request.POST['id'],)
                message = ''
                # access query set
                for sub in subscription:
                    # take in the data
                    # user
                    sub.user = self.request.user

                    # start date
                    # make sure the date is in the correct format
                    sub.start_date = self.request.POST['start_date']
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
                    sub.number_of_items = int(self.request.POST['number_of_products'])

                    # calcuate the rest of the data
                    sub.updated_date = datetime.now()
                    sub.active = True

                    if sub.intervall == '001':
                        # add a week
                        d = timedelta(days=7)
                        add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                        next_date = add_date + d

                        sub.next_order_date = next_date

                    elif sub.intervall == '002':
                        # add two weeks
                        d = timedelta(days=14)
                        add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                        next_date = add_date + d

                        sub.next_order_date = next_date

                    elif sub.intervall == '010':
                        # add a month
                        d = timedelta(days=30)
                        add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                        next_date = add_date + d

                        sub.next_order_date = next_date
                    elif sub.intervall == '020':
                        # add two months
                        d = timedelta(days=60)
                        add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                        next_date = add_date + d

                        sub.next_order_date = next_date
                    elif sub.intervall == '100':
                        # add six months
                        d = timedelta(days=182)
                        add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                        next_date = add_date + d

                        sub.next_order_date = next_date
                    elif sub.intervall == '200':
                        # add a year
                        d = timedelta(days=365)
                        add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                        next_date = add_date + d

                        sub.next_order_date = next_date
                    else:
                        # this shouldnt be able to happen. Add nothing
                        sub.next_order_date = sub.start_date

                    # save subscription
                    sub.save()

                    # delete subscription items

                    sub_items = SubscriptionItem.objects.filter(subscription=sub)
                    for item in sub_items:
                        item.delete()

                    # recreate subscription items

                    i = 1

                    for i in range(sub.number_of_items):
                        i += 1
                        subscription_item = SubscriptionItem()
                        subscription_item.user = sub.user
                        subscription_item.subscription = sub
                        p_string = 'product%s' % (i,)
                        a_string = 'amount%s' % (i,)
                        product_id = self.request.POST[p_string]
                        amount = self.request.POST[a_string]
                        products = Item.objects.filter(id=product_id)
                        for product in products:
                            subscription_item.item = product
                        subscription_item.quantity = amount
                        subscription_item.save()

                    # save the order and order items for the next order
                    # first se if an order is connected, if it is get it
                    if sub.next_order is not None:
                        theOrderQuery = Order.objects.filter(id=sub.next_order.id)
                        for theOrder in theOrderQuery:
                            theOrder.subscription_order = True
                            theOrder.subscription_date = sub.next_order_date
                            theOrder.ordered_date = datetime.now()
                            theOrder.ordered = True
                            theOrder.received = False
                            theOrder.being_delivered = False
                            for address in addresses:
                                if address.id == int(shipping_address):
                                    theOrder.shipping_address = address
                                elif address.id == int(billing_address):
                                    theOrder.billing_address = address
                            theOrder.save()
                            sub.next_order = theOrder
                            sub.save()
                            
                            # remove old order items and then make new the order items, one for each sub item and add to order
                            
                            orderItems = theOrder.items.all()
                            for item in orderItems:
                                item.delete()

                            all_sub_items = SubscriptionItem.objects.filter(subscription=sub)
                            
                            for item in all_sub_items:
                                # new orderItem object
                                orderItem = OrderItem()
                                # populate
                                orderItem.user = sub.user
                                orderItem.ordered = True
                                orderItem.item = item.item
                                orderItem.quantity = item.quantity
                                # save
                                orderItem.save()
                                # add the item to the order
                                theOrder.items.add(orderItem)

                                # message = "Subscription saved and activated."
                    else:
                        # it isn't so we make a new one
                        theOrder = Order()

                        theOrder.user = sub.user
                        theOrder.subscription_order = True
                        theOrder.subscription_date = sub.next_order_date
                        theOrder.ordered_date = datetime.now()
                        theOrder.ordered = True
                        theOrder.received = False
                        theOrder.being_delivered = False
                        for address in addresses:
                            if address.id == int(shipping_address):
                                theOrder.shipping_address = address
                            elif address.id == int(billing_address):
                                theOrder.billing_address = address
                        theOrder.save()
                        sub.next_order = theOrder
                        sub.save()
                        
                        # make the order items, one for each sub item and add to order
                    
                        all_sub_items = SubscriptionItem.objects.filter(user=sub.user, subscription=sub)
                        # message = "Oops2"
                        for item in all_sub_items:
                            # new orderItem object
                            orderItem = OrderItem()
                            # populate
                            orderItem.user = sub.user
                            orderItem.ordered = True
                            orderItem.item = item.item
                            orderItem.quantity = item.quantity
                            # save
                            orderItem.save()
                            # add the item to the order
                            theOrder.items.add(orderItem)

                            # message = "Subscription saved and activated. " + str(sub.id) + " " + str(theOrder.id) + " " + str(orderItem.id)
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
                sub.start_date = self.request.POST['start_date']
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
                sub.number_of_items = int(self.request.POST['number_of_products'])

                # calcuate the rest of the data
                sub.updated_date = datetime.now()
                sub.active = True

                if sub.intervall == '001':
                    # add a week
                    d = timedelta(days=7)
                    add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                    next_date = add_date + d

                    sub.next_order_date = next_date

                elif sub.intervall == '002':
                    # add two weeks
                    d = timedelta(days=14)
                    add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                    next_date = add_date + d

                    sub.next_order_date = next_date

                elif sub.intervall == '010':
                    # add a month
                    d = timedelta(days=30)
                    add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                    next_date = add_date + d

                    sub.next_order_date = next_date
                elif sub.intervall == '020':
                    # add two months
                    d = timedelta(days=60)
                    add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                    next_date = add_date + d

                    sub.next_order_date = next_date
                elif sub.intervall == '100':
                    # add six months
                    d = timedelta(days=182)
                    add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                    next_date = add_date + d

                    sub.next_order_date = next_date
                elif sub.intervall == '200':
                    # add a year
                    d = timedelta(days=365)
                    add_date = datetime.strptime(sub.start_date, '%Y-%m-%d')
                    next_date = add_date + d

                    sub.next_order_date = next_date
                else:
                    # this shouldnt be able to happen. Add nothing
                    sub.next_order_date = datetime.strptime(sub.start_date, '%Y-%m-%d')

                # temp slug
                sub.slug = "temp"

                # save subscription
                sub.save()

                # set unique slug
                sub.slug = "s" + str(sub.id) + "u" + str(self.request.user.id)

                # resave
                sub.save()

                # create subscription items

                i = 1

                for i in range(sub.number_of_items):
                    i += 1
                    subscription_item = SubscriptionItem()
                    subscription_item.user = sub.user
                    subscription_item.subscription = sub
                    p_string = 'product%s' % (i,)
                    a_string = 'amount%s' % (i,)
                    product_id = self.request.POST[p_string]
                    amount = int(self.request.POST[a_string])
                    products = Item.objects.filter(id=product_id)
                    for product in products:
                        subscription_item.item = product
                    subscription_item.quantity = amount
                    subscription_item.save()

                # save the order and order items for the next order
                # first create the order

                theOrder = Order()

                theOrder.user = sub.user
                theOrder.ref_code = create_ref_code()
                theOrder.subscription_order = True
                theOrder.subscription_date = sub.next_order_date
                theOrder.ordered_date = datetime.now()
                theOrder.ordered = True
                theOrder.received = False
                theOrder.being_delivered = False
                theOrder.shipping_address = sub.shipping_address
                theOrder.billing_address = sub.billing_address
                theOrder.save()

                sub.next_order = theOrder
                sub.save()

                # make the order items, one for each sub item and add to order
                all_sub_items = SubscriptionItem.objects.filter(subscription=sub)
                for item in all_sub_items:
                    # new orderItem object
                    orderItem = OrderItem()
                    # populate
                    orderItem.user = sub.user
                    orderItem.ordered = True
                    orderItem.item = item.item
                    orderItem.quantity = item.quantity
                    # save
                    orderItem.save()
                    # add the item to the order
                    theOrder.items.add(orderItem)

                    message = "Subscription saved and activated."
                messages.info(self.request, message)
                return redirect("member:my_subscriptions")

        elif 'deactivateSubscription' in self.request.POST.keys():
            subscription = Subscription.objects.filter(user=self.request.user, id=int(self.request.POST['id']))

            for sub in subscription:
                # deactivate subscription
                if sub.active is False:
                    messages.info(self.request, "Subscription already deactivated")
                    return redirect("member:my_subscriptions")
                else:
                    sub.active = False
                    sub.save()

                    # delete the order connected to the sub
                    try:
                        theOrder = Order.objects.filter(id=sub.next_order.id)
                        # lets handle the query
                        for order in theOrder:
                            # first get the list of items
                            theOrderItems = order.items.all()
                            # then go through the items one by one
                            for item in theOrderItems:
                                # get the query for each item
                                orderItem = OrderItem.objects.filter(id=item.id)
                                # handle the query
                                for theItem in orderItem:
                                    # delete the item
                                    theItem.delete()
                                    # delete order
                                    order.delete()

                        messages.info(self.request, "Subscription deactivated and connected order deleted.")
                        return redirect("member:my_subscriptions")

                    except ObjectDoesNotExist:
                        messages.info(self.request, "Subscription deactivated")
                        return redirect("member:my_subscriptions")


class DeleteOrder(View):
    def post(self, *args, **kwargs):
        message = "oh dear"
        orderId = self.request.POST['id']
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

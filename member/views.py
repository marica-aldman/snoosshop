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


class Overview(View):
    def get(self, *args, **kwargs):
        try:
            # get the active support errands and the resently ended support errands

            errands = Support()
            errands = errands.objects.get(
                user=self.request.user)
            errands1 = {}
            errands2 = {}
            today = datetime.now()

            for errand in errands:
                if errand.done:
                    time_diff = errand.doneDate - today
                    if time_diff.days < 8:
                        errands2.append(errand)
                else:
                    errands1.append(errand)

            # get the active orders and the resently sent orders

            orders = Order()
            orders = orders.objects.get(
                user=self.request.user)
            order1 = {}
            order2 = {}
            today = datetime.now()

            for order in orders:
                if order.recieved:
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
            }

            return render(self.request, "my_overview.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your overview. Contact the support for assistance.")
            return redirect("core:home")


class Orders(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:

            # get the orders and sort out active ones

            orders = Order()
            orders = orders.objects.get(
                user=self.request.user)
            orders_a = {}
            today = datetime.now()

            for order in orders:
                if not order.recieved:
                    orders_a.append(order)

            #get all the items and their discounts

            orders = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'orders': orders,
                'orders_a': orders_a,
            }

            return render(self.request, "my_orders.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your orderlistspage. Contact the support for assistance.")
            return redirect("member:my_overview")


class Order(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            if self.request.POST['id']:
                # get the right order
                order = Order()
                order = Order.objects.get(
                    user=self.request.user, id=self.request.POST['id'])

                # get all the items and their discounts
                discounts = {}
                items = order.items
                all_items = {}
                all_order_items = {}
                
                for item in items:
                    item_id = item.id
                    check_order_item = OrderItem()
                    check_order_item = check_order_item.objects.get(id=item_id)
                    check_item = Item()
                    check_item = check_item.objects.get(id=item_id)
                    item_discount = check_item.discount_price
                    new = {
                            'id': item_id,
                            'discount': item_discount
                        }
                    discounts.append(new)
                    all_order_items.append(check_order_item)
                    all_items.append(check_item)

                # get all the addresses

                shipping_adress_id = order.shipping_address
                billing_adress_id = order.billing_address

                shipping_adress = Address()
                shipping_adress = shipping_adress.objects.get(id=shipping_adress_id)

                billing_adress = Address()
                billing_adress = billing_adress.objects.get(id=billing_adress_id)

                # get the cupon used

                coupon_id = order.coupon

                coupon = Coupon()
                coupon = coupon.objects.get(id=coupon_id)

                # get the payment info
                payment_id = order.payment

                payment = Payment()
                payment = payment.object.get(id=payment_id)

                context = {
                    'order': order,
                    'all_order_items': all_order_items,
                    'all_items': all_items,
                    'discounts': discounts,
                    'shipping_adress': shipping_adress,
                    'billing_adress': billing_adress,
                    'coupon': coupon,
                    'payment': payment,
                }

                return render(self.request, "order.html", context)
            else:
                return redirect("member:my_orders")

        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this order. Contact the support for assistance.")
            return redirect("member:my_overview")


class Support(View):
    def get(self, *args, **kwargs):
        try:
            # get all errands, sort out the active ones
            errands = Support()
            errands = errands.objects.get(
                user=self.request.user)
            errands_a = {}
            today = datetime.now()

            for errand in errands:
                if not errand.done:
                    errands_a.append(errand)

            context = {
                'support': errands,
                'errands_a': errands_a,
            }

            return render(self.request, "my_support.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing this page. Contact the support for assistance.")
            return redirect("member:my_overview")


class Errand(View):
    def get(self, *args, **kwargs):
        try:
            # id check here
            if self.request.POST['id']:
                errand = Support()
                errand = errand.objects.get(user=self.request.user, id=self.request.POST['id'])
                context = {
                    'errand': errand,
                }
                return render(self.request, "my_errand.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this errand. Contact the support for assistance.")
            return redirect("member:my_overview")


class Profile(View):
    def get(self, *args, **kwargs):
        try:
            # obs make a form view for editing info and adding info

            info = UserInfo.objects.get(user=self.request.user)
            company = CompanyInfo.objects.get(user=self.request.user)
            addresses = Address.objects.get(user=self.request.user)

            context = {
                'info': info,
                'company': company,
                'addresses': addresses,
            }

            return render(self.request, "my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your profile. Contact the support for assistance.")
            return redirect("member:my_overview")


class Settings(View):
    def get(self, *args, **kwargs):
        try:
            # obs make a form view for editing info and adding info

            cookieSettings = cookieSettings.objects.get(user=self.request.user)
            userSettings = userSettings.objects.get(user=self.request.user)

            context = {
                'cookies': cookieSettings,
                'settings': userSettings,
            }
            return render(self.request, "my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your settings. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionsView(View):
    def get(self, *args, **kwargs):
        try:
            subscriptions = Subscription.objects.get(user=self.request.user)
            context = {
                'subscriptions': subscriptions,
            }
            return render(self.request, "my_subscriptions.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionView(View):
    def get(self, *args, **kwargs):
        try:
            # obs make a form view for editing info and adding info
            # add id check
            if self.request.POST['id']:
                subscription = Subscription.objects.get(user=self.request.user, id=self.request.POST['id'])

                context = {
                    'subscription': subscription,
                }
                return render(self.request, "my_subscription.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this subscription. Contact the support for assistance.")
            return redirect("member:my_overview")


class CookieSettingsView(View):
    def get(self, *args, **kwargs):
        try:
            # get cookie model, fill in with previous info if there is any
            cookie_settings = Cookies()
            cookie_settings = cookie_settings.objects.get(
                user=self.request.user)

            context = {
                'cookie_settings': cookie_settings,
            }

            return render(self.request, "cookie_settings.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing the cookie settings page. Contact the support for assistance.")
            return redirect("core:home")

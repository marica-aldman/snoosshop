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
from core.models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, CompanyInfo, UserInfo, SupportThread, SupportResponces, Subscription, Cookies
from .forms import SubscriptionForm, ProfileForm, InitialSupportForm, AdressForm

# add save functions and button functions as well as the actual content to the templates, also add forms for cookie settings and settings as well as further contact form for support


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
                #orders = Order.objects.get(user=self.request.user, ordered=True)
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
                discounts = []
                items = order.items
                all_items = []
                all_order_items = []
                
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
                    'discounts': discounts,
                    'shipping_adress': shipping_adress,
                    'billing_adress': billing_adress,
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
            # obs make a form view for editing info and adding info
            try:
                info = UserInfo.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                info = {}
            try:
                company = CompanyInfo.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                company = {}
            try:
                addresses = Address.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                addresses = {}

            context = {
                'info': info,
                'company': company,
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


class EditAdress(View):
    def get(self, *args, **kwargs):
        try:
            # get form for this using the user id

            form = AdressForm()
            form = form.__init__(form, user=self.request.user)

            context = {
                'form': form,
            }

            return render(self.request, "member/edit_my_adress.html", context)
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

            try:
                subscriptions = Subscription.objects.filter(user=self.request.user)
            except ObjectDoesNotExist:
                subscriptions = {}

            context = {
                'subscriptions': subscriptions,
            }
            return render(self.request, "member/my_subscriptions.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Something went wrong when accessing your subscriptions. Contact the support for assistance.")
            return redirect("member:my_overview")


class SubscriptionView(View):
    def get(self, *args, **kwargs):
        try:
            # check if we have an id for the subscription
            if self.request.POST['id']:
                # check that the subscription belongs to the user

                try:
                    sub = Subscription.objects.filter(user=self.request.user, id=self.request.POST['id'])
                except ObjectDoesNotExist:
                    sub = {}
            
                if len(sub) == 0:
                    # subscription does not belong to user log possible hacking attempt
                    messages.info(self.request, "This subscription is not yours.")
                    return redirect("member:my_overview")
                else:
                    form = SubscriptionForm()
                    form = form.__init__(form, self.request.POST['id'])
                    context = {
                        'form': form,
                        'subscription': sub,
                    }
                    return render(self.request, "member/my_subscription.html", context)
            elif self.request.POST['new']:
                
                # get a blank form
                subID = 0
                form = SubscriptionForm()
                form = form.__init__(form, subID)
                context = {
                    'form': form,
                    'subscription': False,
                }
                return render(self.request, "member/my_subscription.html", context)
            else:
                messages.info(self.request, "No subscription id. Contact the support for assistance.")
                return redirect("member:my_overview")
        except ObjectDoesNotExist:
            messages.info(self.request, "Can't find this subscription. Contact the support for assistance.")
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

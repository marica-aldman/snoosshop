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
from core.models import *


class Overview(View):
    def get(self, *args, **kwargs):
        try:
            # check done and done date
            support = Support()
            support = support.objects.get(user=self.request.user)

            context = {
                'support': support,
            }

            return render(self.request, "my_overview.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("core:home")


class Orders(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            orders = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'orders': orders,
            }

            return render(self.request, "my_orders.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Order(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            if self.request.POST['id']:
                order = Order()
                order = Order.objects.get(
                    user=self.request.user, id=self.request.POST['id'])
                context = {
                    'order': order,
                }

                return render(self.request, "order.html", context)
            else:
                return redirect("member:my_orders")

        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Support(View):
    def get(self, *args, **kwargs):
        try:
            support = Support()
            support = support.objects.get(user=self.request.user)
            context = {
                'support': support,
            }
            return render(self.request, "my_support.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Errand(View):
    def get(self, *args, **kwargs):
        try:
            # id check here
            support = Support()
            support = support.objects.get(user=self.request.user)
            context = {
                'support': support,
            }
            return render(self.request, "my_errand.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Profile(View):
    def get(self, *args, **kwargs):
        try:

            info = UserInfo.objects.get(user=self.request.user)
            company = CompanyInfo.objects.get(user=self.request.user)
            address = Address.objects.get(user=self.request.user)

            context = {
                'info': info,
                'company': company,
                'address': address,
            }

            return render(self.request, "my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Settings(View):
    def get(self, *args, **kwargs):
        try:
            cookieSettings = cookieSettings.objects.get(user=self.request.user)
            userSettings = userSettings.objects.get(user=self.request.user)

            context = {
                'cookies': cookieSettings,
                'settings': userSettings,
            }
            return render(self.request, "my_profile.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Subscriptions(View):
    def get(self, *args, **kwargs):
        try:
            subscriptions = subscriptions.objects.get(user=self.request.user)
            context = {
                'subscriptions': subscriptions,
            }
            return render(self.request, "my_subscriptions.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")


class Subscription(View):
    def get(self, *args, **kwargs):
        try:
            # add id check
            subscription = subscription.objects.get(user=self.request.user)
            context = {
                'subscription': subscription,
            }
            return render(self.request, "my_subscription.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "oops")
            return redirect("member:my_overview")

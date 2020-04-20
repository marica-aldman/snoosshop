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
from core.functions import *
from .error import errorFile
from .infoFile import infoFile
from .warningFile import warningFile
from .categories import categoryFile
from .coupons import couponFile
from .items import itemsFile
from .faq import faqFile
from .freights import freightFile
from .text import textFile


class recovery(View):
    # this view requires superuser, make sure
    def get(self, *args, **kwargs):
        theUser = self.request.user
        status = theUser.is_superuser
        if status:
            context = {
            }

            return render(self.request, "recovery/recovery.html", context)

    def post(self, *args, **kwargs):
        theUser = self.request.user
        status = theUser.is_superuser
        if status:

            if 'restore' in self.request.POST.keys() and self.request.POST['restore'] == 'true':
                # get the collected data from the separate files and loop over them to add to database

                errors = errorFile

                for error in errors:
                    newError = ErrorMessages()
                    newError.code = error.code
                    newError.view_section = error.view_section
                    newError.description = error.description
                    newError.swedish = error.swedish
                    newError.save()

                infos = infoFile

                for info in infos:
                    newInfo = InformationMessages()
                    newInfo.code = info.code
                    newInfo.view_section = info.view_section
                    newInfo.description = info.description
                    newInfo.swedish = info.swedish
                    newInfo.save()

                warnings = warningFile

                for warning in warnings:
                    newWarning = WarningMessages()
                    newWarning.code = warning.code
                    newWarning.view_section = warning.view_section
                    newWarning.description = warning.description
                    newWarning.swedish = warning.swedish
                    newWarning.save()

                categories = categoryFile

                for category in categories:
                    newCategory = Category()
                    newCategory.title = category.title
                    newCategory.slug = category.slug
                    newCategory.description = category.description
                    newCategory.discount_price = category.discount_price
                    newCategory.save()

                freights = freightFile

                for freight in freights:
                    newFreight = Freight()
                    newFreight.title = freight.title
                    newFreight.slug = freight.slug
                    newFreight.amount = freight.amount
                    newFreight.save()

                # to add more variables just fill in here when more things become available

                """
                coupons = couponFile

                for coupon in coupons:
                    newCoupon = Coupon()
                    newCoupon.code = coupon.code
                    newCoupon.coupon_type = coupon.coupon_type
                    newCoupon.amount = coupon.amount
                    newCoupon.slug = coupon.slug
                    newCoupon.save()

                faqs = faqFile

                for an_faq in faqs:
                    newFAQ = FAQ()
                    newFAQ.code = an_faq.code
                    newFAQ.description = an_faq.description
                    newFAQ.swedish_subject = an_faq.swedish_subject
                    newFAQ.swedish_content = an_faq.swedish_content
                    newFAQ.save()

                texts = textFile

                for a_text in texts:
                    newText = Text()
                    newText.code = a_text.code
                    newText.view_section = a_text.view_section
                    newText.description = a_text.description
                    newText.swedish = a_text.swedish
                    newText.save()

                # this doesnt work with img or foreign keys, figure it out

                items = itemsFile

                for an_item in items:
                    newItem = Item()
                    newItem.title = an_item.title
                    newItem.price = an_item.price
                    newItem.category = an_item.category
                    newItem.description = an_item.description
                    newItem.image = an_item.image
                    newItem.slug = an_item.slug
                    newItem.save()
                
                """

                context = {

                }

                return render(self.request, "recovery/recovery.html", context)
            else:

                context = {
                }

                messages.warning(self.request, 'Failed to add standard data.')
                return render(self.request, "recovery/recovery.html", context)
        else:
            return redirect("core:home")

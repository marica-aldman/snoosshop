from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Q
from itertools import combinations
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, SearchFAQForm
from .models import *
from core.functions import *

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def products(request):
    context = {
        'items': Item.objects.all(),
        'category_choices': Categories.objects.all(),
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment

                # create a reference code and check that there isnt already one before setting the orders ref code to the code
                ref_code = create_ref_code()
                ref_test = True

                while ref_test:
                    testOrder = Order.objects.filter(ref_code=ref_code)
                    if testOrder is not None:
                        refcode = create_ref_code()
                    else:
                        ref_test = False

                order.ref_code = ref_code
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['category_choices'] = categories
        return context


class NewHomeView(View):
    def get(self, *args, **kwargs):
        theUser = self.request.user

        if(theUser.is_authenticated):
            group1 = Group.objects.get(name="client")
            group2 = Group.objects.get(name="moderator")
            group3 = Group.objects.get(name="support")
            groups = theUser.groups.all()
            has_no_group = groups != group1 or groups != group2 or groups != group3
            if has_no_group:
                return redirect("member:setup")

        categories = Category.objects.all()

        products = Item.objects.all()[:20]
        number_products = Item.objects.all().count()
        print(type(number_products))
        if(number_products >= 1):
            page = which_page(self)
            pagination = {}
            is_paginated = False

        else:
            is_paginated = False
            pagination = {}

        context = {
            "category_choices": categories,
            "object_list": products,
            "is_paginated": is_paginated,
            "page_obj": pagination
        }

        return render(self.request, 'home.html', context)

    def post(self, *args, **kwargs):
        return redirect("core:home")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['category_choices'] = categories
        return context


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 136)
        messages.warning(
            self.request, message)
        return redirect("moderator:coupons")

    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


# Category views

class CategoryView(View):
    def get(self, slug, *args, **kwargs):
        try:
            categoryquery = Category.objects.filter(slug="TS")
            context = {
                'object_list': categoryquery
            }
            return render(self.request, "category.html", context)
        except ObjectDoesNotExist:
            message.info(self.request, "Something went wrong, contact support")
            return redirect("core:home")

# FAQ


class FAQView(View):
    def get(self, *args, **kwargs):

        try:
            # need to add language tests here at a later date
            theLanguage = LanguageChoices.objects.get(language_short="swe")

            try:
                faqs = FAQ.objects.filter(language=theLanguage)
            except ObjectDoesNotExist:
                message = get_message('error', 135)
                faqs = [
                    {
                        "question": "Ett fel har uppstått:",
                        "answer": message,
                    }
                ]

            try:
                searchForm = SearchFAQForm()
                searchForm.language(theLanguage)
                aButtonType = ButtonType.objects.get(buttonType="search")
                searchButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=aButtonType)
            except ObjectDoesNotExist:
                message = get_message('error', 135)
                # flag it support
                searchForm = SearchFAQForm()
                searchButton = {"buttonText": "Search"}

        except ObjectDoesNotExist:
            faqs = [
                {
                    "question": "Ett fel har uppstått:",
                    "answer": message,
                }
            ]
            searchForm = SearchFAQForm()
            searchButton = {"buttonText": "Search"}
        comment = ""

        context = {
            'search': False,
            'faqs': faqs,
            "comment": comment,
            'searchForm': searchForm,
            "searchButton": searchButton,
        }
        return render(self.request, "faq.html", context)

    def post(self, *args, **kwargs):
        if "searchTerm" in self.request.POST.keys():
            form = SearchFAQForm(self.request.POST)
            if form.is_valid():
                # need to add language tests here at a later date
                theLanguage = LanguageChoices.objects.get(
                    language_short="swe")
                search_terms = form.cleaned_data.get('searchTerm')
                search_term_split = search_terms.split()
                len_search_term = len(search_term_split)

                # make all the combinations of the search

                a = len_search_term
                searchTermList = []
                while a > 0:
                    searchCombinations = combinations(search_term_split, a)
                    for combination in searchCombinations:
                        term = ""
                        for word in combination:
                            if term == "":
                                term = word
                            else:
                                term = term + " " + word
                        searchTermList.append(term)
                    a -= 1
                search = []
                comment = ""
                for term in searchTermList:
                    try:
                        faqs = FAQ.objects.filter(subject__contains=term)
                        search.append(faqs)
                    except ObjectDoesNotExist:
                        # this is only because we want the test without an error thrown. This comment wont be used
                        comment = term + " doesn't exist in subject."
                    try:
                        faqs = FAQ.objects.filter(content__contains=term)
                        search.append(faqs)
                    except ObjectDoesNotExist:
                        # this is only because we want the test without an error thrown. This comment wont be used
                        comment = term + " doesn't exist in content."

                search_no_duplicates = []
                len_s = len(search)
                if len_s > 0:
                    comment = ""
                    for query in search:
                        for entry in query:
                            i = 0
                            if len(search_no_duplicates) == 0:
                                search_no_duplicates.append(entry)
                            same = False
                            while i < len(search_no_duplicates):
                                if search_no_duplicates[i].id == entry.id:
                                    i = len(search_no_duplicates)
                                    same = True
                                i += 1
                            if not same:
                                search_no_duplicates.append(entry)
                else:
                    comment = get_message("info", code)

                try:
                    aButtonType = ButtonType.objects.get(
                        buttonType="search")
                    searchButton = ButtonText.objects.filter(
                        language=theLanguage, theButtonType=aButtonType)
                except ObjectDoesNotExist:
                    searchButton = {"buttonText": "Search"}

                context = {
                    'search': True,
                    'faqs': search_no_duplicates,
                    "comment": comment,
                    'searchForm': form,
                    "searchButton": searchButton,
                }
                return render(self.request, "faq.html", context)
            else:
                # add error message here
                try:
                    # need to add language tests here at a later date
                    theLanguage = LanguageChoices.objects.get(
                        language_short="swe")

                    try:
                        faqs = FAQ.objects.filter(language=theLanguage)
                    except ObjectDoesNotExist:
                        message = get_message('error', 135)
                        faqs = [
                            {
                                "question": "Ett fel har uppstått:",
                                "answer": message,
                            }
                        ]

                    try:
                        searchForm = SearchFAQForm()
                        searchForm.language(theLanguage)
                        aButtonType = ButtonType.objects.get(
                            buttonType="search")
                        searchButton = ButtonText.objects.filter(
                            language=theLanguage, theButtonType=aButtonType)
                    except ObjectDoesNotExist:
                        message = get_message('error', 135)
                        # flag it support
                        searchForm = SearchFAQForm()
                        searchButton = {"buttonText": "Search"}

                except ObjectDoesNotExist:
                    faqs = [
                        {
                            "question": "Ett fel har uppstått:",
                            "answer": message,
                        }
                    ]
                    searchForm = SearchFAQForm()
                    searchButton = {"buttonText": "Search"}
                    comment = ""

                context = {
                    'search': False,
                    'faqs': faqs,
                    "comment": comment,
                    'searchForm': searchForm,
                    "searchButton": searchButton,
                }
                return render(self.request, "faq.html", context)

        else:

            try:
                # need to add language tests here at a later date
                theLanguage = LanguageChoices.objects.get(language_short="swe")

                try:
                    faqs = FAQ.objects.filter(language=theLanguage)
                except ObjectDoesNotExist:
                    message = get_message('error', 135)
                    faqs = [
                        {
                            "question": "Ett fel har uppstått:",
                            "answer": message,
                        }
                    ]

                try:
                    searchForm = SearchFAQForm()
                    searchForm.language(theLanguage)
                    aButtonType = ButtonType.objects.get(buttonType="search")
                    searchButton = ButtonText.objects.filter(
                        language=theLanguage, theButtonType=aButtonType)
                except ObjectDoesNotExist:
                    message = get_message('error', 135)
                    # flag it support
                    searchForm = SearchFAQForm()
                    searchButton = {"buttonText": "Search"}

            except ObjectDoesNotExist:
                faqs = [
                    {
                        "question": "Ett fel har uppstått:",
                        "answer": message,
                    }
                ]
                searchForm = SearchFAQForm()
                searchButton = {"buttonText": "Search"}
                comment = ""

            context = {
                'search': False,
                'faqs': faqs,
                "comment": comment,
                'searchForm': searchForm,
                "searchButton": searchButton,
            }
            return render(self.request, "faq.html", context)

# om_oss_view


class om_oss_view(View):
    def get(self, *args, **kwargs):
        test = 1

    def post(self, *args, **kwargs):
        test = 1

# teamet_view


class teamet_view(View):
    def get(self, *args, **kwargs):
        test = 1

    def post(self, *args, **kwargs):
        test = 1

# vision_view


class vision_view(View):
    def get(self, *args, **kwargs):
        test = 1

    def post(self, *args, **kwargs):
        test = 1

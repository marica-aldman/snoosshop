from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db.models import Q
from django.contrib.sites.models import Site
from itertools import combinations
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, SearchFAQForm
from .models import *
from core.functions import *
import stripe
from django.http.response import JsonResponse, HttpResponse

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            # GDPR check
            gdpr_check = check_gdpr_cookies(self)
            path = self.request.get_full_path()
            is_post = False
            # get the content of the basket
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()

            test = str(type(order.shipping_address))
            print("test")
            print(test)
            print(type(test))

            if test == "<class 'NoneType'>":
                # get the users preset adresses if there are some
                shipping_address_qs = Address.objects.get(
                    user=self.request.user,
                    address_type='S',
                    default=True
                )
            else:
                shipping_address_qs = order.shipping_address

            test2 = str(type(order.billing_address))

            if test2 == "<class 'NoneType'>":
                # get the users preset adresses if there are some
                billing_address_qs = Address.objects.get(
                    user=self.request.user,
                    address_type='B',
                    default=True
                )
            else:
                billing_address_qs = order.billing_address

            context = {
                'gdpr_check': gdpr_check,
                'form': form,
                'couponform': CouponForm(),
                'first_load': True,
                'form_not_complete': False,
                'order': order,
                'shipping_address': shipping_address_qs,
                'billing_address': billing_address_qs,
                'DISPLAY_COUPON_FORM': True
            }

            if order.freight:
                freights = Freight.objects.all()

                selectedFreights = []

                for f in freights:
                    if f.id == int(order.freight.id):
                        selectedFreights.append(
                            {"chosen": True, "choice": f})
                    else:
                        selectedFreights.append(
                            {"chosen": False, "choice": f})
                context.update({"chosen_freight": True})
                context.update({"selectedFreights": selectedFreights})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Varukorgen är tom.")
            return redirect("core:order-summary")

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form_not_complete = False
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
                            self.request, "Ingen förinställd leveransadress funnen.")
                        return redirect('core:checkout')
                else:
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    s_post_town = form.cleaned_data.get('s_post_town')
                    if shipping_address2 == "<input":
                        shipping_address2 = ""
                    if shipping_address1 == "<input":
                        shipping_address1 = ""

                    if is_valid_form([shipping_address1, shipping_zip, s_post_town]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            zip=shipping_zip,
                            post_town=s_post_town,
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
                        form_not_complete = True
                        messages.info(
                            self.request, "Vargod fyll i de obligatoriska fälten för leveransadressen.")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address and not form_not_complete:
                    billing_address = shipping_address
                    order.billing_address = billing_address
                    order.save()

                elif same_billing_address and form_not_complete:
                    billing_address1 = shipping_address1
                    billing_address2 = shipping_address2
                    billing_zip = shipping_zip
                    b_post_town = s_post_town

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
                            self.request, "Ingen förinställd faktureringsadress funnen.")
                        return redirect('core:checkout')
                else:
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    b_post_town = form.cleaned_data.get(
                        'b_post_town')
                    if billing_address1 == "<input":
                        billing_address1 = ""
                    if billing_address2 == "<input":
                        billing_address2 = ""

                    if is_valid_form([billing_address1, billing_zip, b_post_town]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            zip=billing_zip,
                            post_town=b_post_town,
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
                        form_not_complete = True
                        messages.info(
                            self.request, "Vargod fyll i de obligatoriska fälten under faktureringsadressen.")

                freight_option = form.cleaned_data.get('freight_option')
                freight = Freight.objects.filter(id=int(freight_option))
                order.freight = freight[0]
                order.freight_price = order.freight.amount

                # recalculate order total

                order.total_price = calculate_total_order(order)
                order.ordered_date = make_aware(datetime.now())
                order.save()

                payment_option = form.cleaned_data.get('payment_option')

                if(form_not_complete):

                    # get the content of the basket
                    order = Order.objects.get(
                        user=self.request.user, ordered=False)

                    # create freight choices to go through to preselect if it is selected

                    freights = Freight.objects.all()

                    selectedFreights = []

                    for f in freight:
                        if f.id == int(freight_option):
                            selectedFreights.append(
                                {"chosen": True, "choice": f})
                        else:
                            selectedFreights.append(
                                {"chosen": False, "choice": f})

                    # create payment choices to go through to preselect if it is selected

                    payments = PaymentTypes.objects.all()

                    selectedPayments = []

                    for p in payments:
                        if p.short == payment_option:
                            selectedPayments.append(
                                {"chosen": True, "choice": p})
                        else:
                            selectedPayments.append(
                                {"chosen": False, "choice": p})

                    context = {
                        'gdpr_check': gdpr_check,
                        'form': form,
                        'couponform': CouponForm(),
                        'order': order,
                        'DISPLAY_COUPON_FORM': True,
                        'first_load': False,
                        'form_not_complete': form_not_complete,
                        'shipping_address1': shipping_address1,
                        'shipping_address2': shipping_address2,
                        'shipping_zip': shipping_zip,
                        's_post_town': s_post_town,
                        'billing_address1': billing_address1,
                        'billing_address2': billing_address2,
                        'billing_zip': billing_zip,
                        'b_post_town': b_post_town,
                        'use_default_shipping': use_default_shipping,
                        'use_default_billing': use_default_billing,
                        'same_billing_address': same_billing_address,
                        'selectedPayments': selectedPayments,
                        'selectedFreights': selectedFreights,
                    }

                    # get the users preset adresses if there are some
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
                else:
                    if payment_option == 'S':
                        # change this for stripe
                        return redirect('core:confirm')
                    else:
                        messages.warning(
                            self.request, "Ogiltig betalningsalternativ valt.")
                        return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "Varukorgen är tom.")
            return redirect("core:order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'gdpr_check': gdpr_check,
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
                self.request, "Du har inte laggt till någon faktureringsadress.")
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
                payment.timestamp = make_aware(datetime.now())
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                for item in order_items:
                    item.ordered = True
                    item.save()

                order.ordered = True
                order.ordered_date = make_aware(datetime.now())
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

                messages.success(self.request, "Din order är registrerad!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(
                    self.request, "För många API förfrågningar under kort tid")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(self.request, "Ogiltiga parametrar")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Ej autentiserad")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Nätverksfel")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Något gick fel. Betalningen gick inte igenom. Vargod försök igen.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "Ett mycket allvarligt fel har inträffat.")
                return redirect("/")

        messages.warning(self.request, "Ogiltig data inkommen")
        return redirect("/payment/stripe/")


class NewHomeView(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = True  # check_gdpr_cookies(self)

        categories = Category.objects.all()
        aquire_index = default_pagination_values
        number_products = Item.objects.all().count()
        pagination = {}
        is_paginated = False
        start_extras = False
        end_extras = False
        if(number_products > aquire_index):

            page = which_page(self)

            max_page = number_products/aquire_index

            testM = int(max_page)
            if(testM != max_page):
                max_page = testM + 1
            page_list, where = get_list_of_pages(int(page), int(max_page))

            if page == 1:
                if(page_list[-1] == max_page):
                    hasNext = False
                else:
                    hasNext = True
                pagination = {
                    "has_previous": False,
                    "previous_page_number": 1,
                    "number": 1,
                    "has_next": hasNext,
                    "next_page_number": 2
                }
                is_paginated = True
                products = Item.objects.all()[:aquire_index]
                if where != "no extras":
                    end_extras = True

            else:
                page = int(page)
                # query[offset:offset + limit]
                start_point = (int(page) - 1) * aquire_index
                o_and_l = start_point + aquire_index
                products = Item.objects.all()[start_point:o_and_l]
                is_paginated = True
                if page < max_page:
                    next_page = page + 1
                    previous_page = page - 1
                    if(page == max_page):
                        hasNext = False
                    else:
                        hasNext = True

                    if(len(page_list) == max_page):
                        hasPreivous = False
                    else:
                        hasPreivous = True

                    pagination = {
                        "has_previous": hasPreivous,
                        "previous_page_number": previous_page,
                        "number": page,
                        "has_next": hasNext,
                        "next_page_number": next_page
                    }
                else:
                    previous_page = page - 1

                    if(len(page_list) == max_page):
                        hasPreivous = False
                    else:
                        hasPreivous = True

                    pagination = {
                        "has_previous": hasPreivous,
                        "previous_page_number": previous_page,
                        "number": page,
                        "has_next": False,
                        "next_page_number": page
                    }

                if where == "start":
                    end_extras = True
                elif where == "end":
                    start_extras = True
                elif where == "mid":
                    start_extras = True
                    end_extras = True
        else:
            products = Item.objects.all()[:aquire_index]

            is_paginated = False
            pagination = {
                "has_previous": False,
                "has_next": False,
            }

        GDPR = self.request.COOKIES.get("GDPR")
        gdpr_check = True
        if GDPR == "GDPR":
            gdpr_check = False

        context = {
            'gdpr_check': gdpr_check,
            "category_choices": categories,
            "object_list": products,
            "is_paginated": is_paginated,
            "page_obj": pagination,
            "page_list": page_list,
            "start_extras": start_extras,
            "end_extras": end_extras,
            "max_page": int(max_page),
        }
        response = render(self.request, 'home.html', context)

        if GDPR != "GDPR":
            response.set_cookie("GDPR", "GDPR")

        return response

    def post(self, *args, **kwargs):
        return redirect("core:home")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        login_url = '/accounts/login/'
        redirect_field_name = 'from'
        redirect_field_value = 'to'
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            # if the user has an old basket and are returning the prices may have changed. Same if there are changes coming into effect before the order has been payed for. We need to check, update and let the user know if there is a change
            order = Order.objects.get(
                user=self.request.user, ordered=False)
            orderItems = order.items.all()
            warning = ""
            info = ""
            recount = False

            for orderItem in orderItems:
                item = orderItem.item
                total_price = 0
                if item.discount_price != None:
                    total_price = item.discount_price * orderItem.quantity
                else:
                    total_price = item.price * orderItem.quantity

                if orderItem.total_price != total_price:
                    recount = True
                    # check if there is a discount
                    # set a warning to the user so they know that there are alterations to the order
                    warning = "Priser ändrade då de antingen är gamla eller inte längre giltiga."
                    if item.discount_price != None:
                        total_price = item.discount_price * orderItem.quantity
                        if orderItem.total_price != total_price:
                            # there is difference in prices this is most likely due to a change in price of the item or discount price no longer valid
                            if item.discount_price != None:
                                total = item.discount_price * orderItem.quantity
                                orderItem.price = item.price
                                orderItem.discount_price = item.discount_price
                                orderItem.total_price = total
                                orderItem.save()
                            else:
                                total = item.price * orderItem.quantity
                                orderItem.price = item.price
                                orderItem.discount_price = item.discount_price
                                orderItem.total_price = total
                                orderItem.save()
                    else:
                        # there is no discount but the price isnt right so correct the prices
                        total = item.price * orderItem.quantity
                        orderItem.price = item.price
                        orderItem.discount_price = item.discount_price
                        orderItem.total_price = total
                        orderItem.save()
                else:
                    # the price is correct towards the regular price but check that there isnt currently a discount
                    if item.discount_price != None and (item.discount_price * orderItem.quantity) != orderItem.total_price:
                        recount = True
                        # there is currently a discount recalculate the price
                        # set a warning to the user so they know that there are alterations to the order
                        info = "Priser ändrade då de för nuvarnde är på rea."
                        total = item.discount_price * orderItem.quantity
                        orderItem.total_price = total
                        orderItem.save()

            if warning != "":
                messages.warning(
                    self.request, warning)

            if info != "":
                messages.info(
                    self.request, info)

            if recount:
                print("recount")
                # prices have changed order needs to be updated
                newTotal = update_order_total(order)
                order.total_price = newTotal
                order.ordered_date = make_aware(datetime.now())
                order.updated_date = make_aware(datetime.now())
                order.save()
                freshOrder = Order.objects.get(id=order.id)
            else:
                # no update can pass order to view without anything
                freshOrder = order

            context = {
                'gdpr_check': gdpr_check,
                'object': freshOrder,
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Varukorgen är tom.")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

    def get_context_data(self, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['category_choices'] = categories
        context['gdpr_check'] = gdpr_check
        context['path'] = self.object.get_absolute_url()
        return context


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        title=item.title,
        price=item.price,
        discount_price=item.discount_price,
        quantity=1,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order.ordered_date = make_aware(datetime.now())
        order.updated_date = make_aware(datetime.now())
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            if item.discount_price != None:
                if item.discount_price > 0:
                    if order_item.discount_price != item.discount_price:
                        messages.info(request, "Varans pris har uppdaterats.")
                        order_item.discount_price = item.discount_price
                    order_item.total_price = order_item.quantity * order_item.discount_price
            else:
                order_item.total_price = order_item.quantity * order_item.price
            order_item.save()
            messages.info(request, "Varans mängd har uppdaterats.")
            return redirect("core:order-summary")
        else:
            if item.discount_price:
                order_item.total_price = order_item.discount_price * order_item.quantity
            else:
                order_item.total_price = order_item.price * order_item.quantity
            order_item.save()
            order.items.add(order_item)
            order.total_price = calculate_total_order(order)
            order.save()
            messages.info(request, "Varan lagd i varukorgen.")
            return redirect("core:order-summary")
    else:
        ordered_date = make_aware(datetime.now())
        updated_date = make_aware(datetime.now())
        refCode = create_ref_code()
        rcode = test_order_ref_code(refCode)
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, updated_date=updated_date, ref_code=rcode)
        order_item.quantity = 1
        order_item.discount_price = item.discount_price
        order_item.price = item.price
        if item.discount_price != None and item.discount_price > 0:
            order_item.total_price = order_item.discount_price * order_item.quantity
        else:
            order_item.total_price = order_item.price * order_item.quantity
        order_item.save()
        order.items.add(order_item)
        order.total_price = calculate_total_order(order)
        order.save()
        messages.info(request, "Varan lagd i varukorgen.")
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
        order.ordered_date = make_aware(datetime.now())
        order.updated_date = make_aware(datetime.now())
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order.save()
            order_item.delete()
            messages.info(request, "Varan borttagen ur varukorgen.")
            all_items = order.items.all()
            if len(all_items) == 0:
                order.delete()
            return redirect("core:order-summary")
        else:
            messages.info(request, "Denna vara fanns inte i din varukorg.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Din varukorg är tom")
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
        order.ordered_date = make_aware(datetime.now())
        order.updated_date = make_aware(datetime.now())
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get(
                item=item,
                user=request.user,
                ordered=False
            )
            if order_item.quantity > 1:
                order_item.quantity -= 1
                if item.discount_price != None:
                    if item.discount_price > 0:
                        if order_item.discount_price != item.discount_price:
                            order_item.discount_price = item.discount_price
                        order_item.total_price = order_item.quantity * order_item.discount_price
                else:
                    order_item.total_price = order_item.quantity * order_item.price
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
                if len(order.items.all()) == 0:
                    order.delete()
            messages.info(request, "Varans mängd har uppdaterats.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Denna vara fanns inte i din varukorg.")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Varukorgen är tom.")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "Denna rabattkod är inte giltig.")
        return redirect("core:checkout")


class AddCouponView(View):
    def get(self, *args, **kwargs):
        # reroute
        message = get_message('error', 136)
        messages.warning(
            self.request, message)
        return redirect("core:home")

    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.updated_date = make_aware(datetime.now())
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Rabattkod tillagd.")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "Din varukorg är tom.")
                return redirect("core:checkout")
        else:
            messages.info(self.request, "Denna rabattkod är ej giltig.")
            return redirect("core:checkout")


# Category views

class CategoryView(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        try:
            page, am_i = where_am_i_and_page(self)
            print(page)
            print(am_i)
            categoryquery = Category.objects.get(slug=am_i)

            # alter this to a set number of products and add pagination
            aquire_index = default_pagination_values
            number_products = Item.objects.filter(
                category=categoryquery).count()
            pagination = {}
            is_paginated = False
            start_extras = False
            end_extras = False

            if(number_products > aquire_index):

                max_page = number_products/aquire_index
                testM = int(max_page)
                if(testM != max_page):
                    max_page = testM + 1
                page_list, where = get_list_of_pages(int(page), int(max_page))
                if page == 1:
                    if(page == max_page):
                        hasNext = False
                    else:
                        hasNext = True
                    pagination = {
                        "has_previous": False,
                        "previous_page_number": 1,
                        "number": 1,
                        "has_next": hasNext,
                        "next_page_number": 2
                    }
                    is_paginated = True
                    products = Item.objects.filter(
                        category=categoryquery)[:aquire_index]
                    if where != "no extras":
                        end_extras = True
                else:

                    # query[offset:offset + limit]
                    start_point = (int(page) - 1) * aquire_index
                    o_and_l = start_point + aquire_index
                    products = Item.objects.filter(category=categoryquery)[
                        start_point:o_and_l]
                    is_paginated = True
                    number_of_pages = number_products / aquire_index
                    test = int(number_of_pages)
                    if number_of_pages > test:
                        number_of_pages += 1

                    if page < number_of_pages:
                        next_page = page + 1
                        previous_page = page - 1
                        hasNext = True
                    else:
                        next_page = page
                        previous_page = page - 1
                        hasNext = False
                    hasPreivous = True

                    pagination = {
                        "has_previous": hasPreivous,
                        "previous_page_number": previous_page,
                        "number": page,
                        "has_next": hasNext,
                        "next_page_number": next_page
                    }

                if where == "start":
                    end_extras = True
                elif where == "end":
                    start_extras = True
                elif where == "mid":
                    start_extras = True
                    end_extras = True

            else:
                products = Item.objects.filter(
                    category=categoryquery)[:aquire_index]

                is_paginated = False
                pagination = {
                    "has_previous": False,
                    "has_next": False,
                }

            # we need to create a list of objects to loop through to mark the apropriate category

            category_choices = Category.objects.all()

            new_list = []
            for cat in category_choices:
                if cat.title == categoryquery.title:
                    new_list.append({
                        'title': cat.title,
                        'url': cat.get_absolute_cat_url,
                        'selected': True
                    })
                else:
                    new_list.append({
                        'title': cat.title,
                        'url': cat.get_absolute_cat_url,
                        'selected': False
                    })

            context = {
                'gdpr_check': gdpr_check,
                'object_list': products,
                'category_list': new_list,
                'selected_cateogory': categoryquery,
                "is_paginated": is_paginated,
                "page_obj": pagination,                    "page_list": page_list,
                "start_extras": start_extras,
                "end_extras": end_extras,
                "max_page": max_page,
            }
            return render(self.request, "category.html", context)
        except ObjectDoesNotExist:
            messages.info(
                self.request, "Något har gått fel, vargod kontakta supporten.")
            return redirect("core:home")

# FAQ


class FAQView(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        try:
            # need to add language tests here at a later date
            theLanguage = LanguageChoices.objects.get(language_short="swe")
            aquire_index = default_pagination_values
            number_faqs = FAQ.objects.filter(language=theLanguage).count()
            pagination = {}
            page_list = []
            is_paginated = False
            start_extras = False
            end_extras = False
            max_page = 0
            if(number_faqs > aquire_index):
                # we only land here if we are on page one without a search and we have more FAQs than fit on one page
                max_page = number_faqs / aquire_index
                testM = int(max_page)
                if(testM != max_page):
                    max_page = testM + 1
                page_list, where = get_list_of_pages(1, int(max_page))

                if(1 != max_page):
                    hasNext = False
                else:
                    hasNext = True

                pagination = {
                    "has_previous": False,
                    "previous_page_number": 1,
                    "number": 1,
                    "has_next": hasNext,
                    "next_page_number": 2
                }
                is_paginated = True
                try:
                    faqs = FAQ.objects.filter(language=theLanguage)[
                        :aquire_index]
                except ObjectDoesNotExist:
                    message = get_message('error', 135)
                    faqs = [
                        {
                            "question": "Ett FAQ fel har uppstått:",
                            "answer": message,
                        }
                    ]

                if where != "no extras":
                    end_extras = True

            else:
                # we have less FAQs then we want from aquire index, so no pagination here and no need to do a specialised search
                try:
                    faqs = FAQ.objects.filter(language=theLanguage)
                except ObjectDoesNotExist:
                    message = get_message('error', 135)
                    faqs = [
                        {
                            "question": "Ett FAQ fel har uppstått:",
                            "answer": message,
                        }
                    ]

            try:
                searchForm = SearchFAQForm()
                aButtonType = ButtonType.objects.get(buttonType="search")
                searchButton = ButtonText.objects.filter(
                    language=theLanguage, theButtonType=aButtonType)
            except ObjectDoesNotExist:
                message = get_message('error', 135)
                # flag it support
                searchForm = SearchFAQForm()
                searchButton = {"buttonText": "Search"}

        except ObjectDoesNotExist:
            pagination = {}
            page_list = []
            is_paginated = False
            start_extras = False
            end_extras = False
            max_page = 0
            faqs = [
                {
                    "question": "Ett språk fel har uppstått:",
                    "answer": message,
                }
            ]
            searchForm = SearchFAQForm()
            searchButton = {"buttonText": "Search"}
        comment = ""

        context = {
            'gdpr_check': gdpr_check,
            'search': False,
            'faqs': faqs,
            "searchTerms": "",
            'searchForm': searchForm,
            "searchButton": searchButton,
            'is_paginated': is_paginated,
            'start_page': start_extras,
            'end_page': end_extras,
            'page_list': page_list,
            'max_page': max_page,
            'page_obj': pagination,
        }
        return render(self.request, "faq.html", context)

    def post(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        if "searchTerm" in self.request.POST.keys():
            # check that the search field isnt empty, if empty redirect to get section
            searchTest = self.request.POST["searchTerm"]

            if searchTest != "":
                # we just did a search, no matter what we are on page 1
                form = SearchFAQForm(self.request.POST)
                comment = ""
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
                    search_no_duplicates = []
                    aquire_index = default_pagination_values
                    pagination = {}
                    page_list = []
                    is_paginated = False
                    start_extras = False
                    end_extras = False
                    max_page = 1

                    # get all results

                    for term in searchTermList:
                        faqs = FAQ.objects.filter(
                            Q(subject__contains=term) | Q(content__contains=term))
                        search.append(faqs)

                    # place all query entries in a new array

                    for_sorting = []

                    for query in search:
                        for entry in query:
                            for_sorting.append(entry)

                    # remove all duplicates
                    for entry in for_sorting:
                        if(len(search_no_duplicates) == 0):
                            search_no_duplicates.append(entry)
                        else:
                            i = 0
                            same = False
                            while i < len(search_no_duplicates):
                                if search_no_duplicates[i].id == entry.id:
                                    i = len(search_no_duplicates)
                                    same = True
                                else:
                                    same = False
                                i += 1

                            if not same:
                                search_no_duplicates.append(entry)

                    # remove those not to be used

                    final_search_array = []

                    if len(search_no_duplicates) > aquire_index:
                        i = 0
                        while i < aquire_index:
                            final_search_array.append(search_no_duplicates[i])
                            i += 1
                    else:
                        final_search_array = search_no_duplicates

                    # create pagination

                    number_faqs = len(search_no_duplicates)
                    if(number_faqs > aquire_index):
                        max_page = number_faqs/aquire_index
                        testM = int(max_page)
                        if(testM != max_page):
                            max_page = testM + 1

                        if(max_page > 1):

                            page_list, where = get_list_of_pages(
                                1, int(max_page))

                            if(page_list[-1] == max_page):
                                hasNext = False
                            else:
                                hasNext = True
                            pagination = {
                                "has_previous": False,
                                "previous_page_number": 1,
                                "number": 1,
                                "has_next": hasNext,
                                "next_page_number": 2
                            }
                            if where != "no extras":
                                end_extras = True

                            is_paginated = True

                    try:
                        aButtonType = ButtonType.objects.get(
                            buttonType="search")
                        searchButton = ButtonText.objects.filter(
                            language=theLanguage, theButtonType=aButtonType)
                    except ObjectDoesNotExist:
                        searchButton = {"buttonText": "Search"}

                context = {
                    'gdpr_check': gdpr_check,
                    'search': True,
                    'faqs': final_search_array,
                    "searchTerms": searchTest,
                    'searchForm': form,
                    "searchButton": searchButton,
                    'is_paginated': is_paginated,
                    'start_page': start_extras,
                    'end_page': end_extras,
                    'page_list': page_list,
                    'max_page': max_page,
                    'page_obj': pagination,
                }
                return render(self.request, "faq.html", context)
            else:
                return redirect("core:faq")

        elif "SearchTerms" in self.request.POST.keys():
            # we are paginating a search this didnt start in the form
            search_terms = self.request.POST['SearchTerms']
            page = int(self.request.POST['page'])

            # need to add language tests here at a later date
            theLanguage = LanguageChoices.objects.get(
                language_short="swe")
            search_term_split1 = search_terms.split("\"")
            if len(search_term_split1) == 1:
                search_term_split = search_term_split1[0].split()
            elif len(search_term_split1) > 1:
                search_term_split = search_term_split1[1].split()
            else:
                search_term_split = search_term_split1
            len_search_term = len(search_term_split)

            # check if the search is empty

            if len_search_term > 0:

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
                search_no_duplicates = []
                aquire_index = default_pagination_values
                pagination = {}
                page_list = []
                is_paginated = False
                start_extras = False
                end_extras = False
                max_page = 1

                # get all results

                for term in searchTermList:
                    faqs = FAQ.objects.filter(
                        Q(subject__contains=term) | Q(content__contains=term))
                    search.append(faqs)

                # place all query entries in a new array

                for_sorting = []

                for query in search:
                    for entry in query:
                        for_sorting.append(entry)

                # remove all duplicates
                for entry in for_sorting:
                    if(len(search_no_duplicates) == 0):
                        search_no_duplicates.append(entry)
                    else:
                        i = 0
                        same = False
                        while i < len(search_no_duplicates):
                            if search_no_duplicates[i].id == entry.id:
                                i = len(search_no_duplicates)
                                same = True
                            else:
                                same = False
                            i += 1
                        if not same:
                            search_no_duplicates.append(entry)
                # remove those not to be used

                final_search_array = []

                finish = (int(page) * aquire_index)
                j = finish - aquire_index
                while j < finish:
                    if(j < len(search_no_duplicates)):
                        final_search_array.append(search_no_duplicates[j])
                    j += 1

                # create pagination

                number_faqs = len(search_no_duplicates)
                if(number_faqs > aquire_index):
                    max_page = number_faqs/aquire_index
                    testM = int(max_page)
                    if(testM != max_page):
                        max_page = testM + 1

                    if(max_page > 1):

                        page_list, where = get_list_of_pages(
                            int(page), int(max_page))

                        if(where == "no extras"):
                            start_extras = False
                            end_extras = False
                            hasNext = False
                            has_previous = False
                            previous_page_number = int(page)
                            next_page_number = int(page)
                        elif(where == "start"):
                            start_extras = False
                            end_extras = True
                            has_previous = False
                            hasNext = True
                            previous_page_number = int(page)
                            next_page_number = int(page) - 1
                        elif(where == "end"):
                            start_extras = True
                            end_extras = False
                            has_previous = True
                            hasNext = False
                            previous_page_number = int(page) - 1
                            next_page_number = int(page)
                        else:
                            start_extras = True
                            end_extras = True
                            has_previous = True
                            hasNext = True
                            previous_page_number = int(page) - 1
                            next_page_number = int(page) + 1

                        pagination = {
                            "has_previous": has_previous,
                            "previous_page_number": previous_page_number,
                            "number": int(page),
                            "has_next": hasNext,
                            "next_page_number": next_page_number
                        }

                        is_paginated = True

                try:
                    searchForm = SearchFAQForm()
                    aButtonType = ButtonType.objects.get(buttonType="search")
                    searchButton = ButtonText.objects.filter(
                        language=theLanguage, theButtonType=aButtonType)
                except ObjectDoesNotExist:
                    message = get_message('error', 135)
                    # flag it support
                    searchForm = SearchFAQForm()
                    searchButton = {"buttonText": "Search"}

                context = {
                    'gdpr_check': gdpr_check,
                    'search': True,
                    'faqs': final_search_array,
                    "searchTerms": search_terms,
                    'searchForm': searchForm,
                    "searchButton": searchButton,
                    'is_paginated': is_paginated,
                    'start_page': start_extras,
                    'end_page': end_extras,
                    'page_list': page_list,
                    'max_page': max_page,
                    'page_obj': pagination,
                }
                return render(self.request, "faq.html", context)
            else:
                # GDPR check
                gdpr_check = check_gdpr_cookies(self)

                try:
                    # need to add language tests here at a later date
                    theLanguage = LanguageChoices.objects.get(
                        language_short="swe")
                    aquire_index = default_pagination_values
                    number_faqs = FAQ.objects.filter(
                        language=theLanguage).count()
                    pagination = {}
                    page_list = []
                    is_paginated = False
                    start_extras = False
                    end_extras = False
                    max_page = 0
                    if(number_faqs > aquire_index):
                        # we only land here if we are on page one without a search and we have more FAQs than fit on one page
                        max_page = number_faqs / aquire_index
                        testM = int(max_page)
                        if(testM != max_page):
                            max_page = testM + 1
                        page_list, where = get_list_of_pages(1, int(max_page))

                        if(1 != max_page):
                            hasNext = False
                        else:
                            hasNext = True

                        if page - 1 >= 1:
                            previous = page - 1
                        else:
                            previous = page
                        if page > 1:
                            has_previous = True
                        else:
                            has_previous = False
                        if page + 1 <= max_page:
                            next = page + 1
                        else:
                            next = page
                        pagination = {
                            "has_previous": has_previous,
                            "previous_page_number": previous,
                            "number": page,
                            "has_next": hasNext,
                            "next_page_number": next
                        }
                        is_paginated = True
                        try:
                            if page - 1 < 1:
                                faqs = FAQ.objects.filter(language=theLanguage)[
                                    :aquire_index]
                            else:
                                offset = aquire_index * (page - 1)
                                o_l = offset + aquire_index
                                faqs = FAQ.objects.filter(language=theLanguage)[
                                    offset:o_l]
                        except ObjectDoesNotExist:
                            message = get_message('error', 135)
                            faqs = [
                                {
                                    "question": "Ett FAQ fel har uppstått:",
                                    "answer": message,
                                }
                            ]

                        if where != "no extras":
                            end_extras = True

                        if where == "start" or where == "mid":
                            start_extras = True

                        if max_page > 5 and where == "end":
                            start_extras = True

                    else:
                        # we have less FAQs then we want from aquire index, so no pagination here and no need to do a specialised search
                        try:
                            faqs = FAQ.objects.filter(language=theLanguage)
                        except ObjectDoesNotExist:
                            message = get_message('error', 135)
                            faqs = [
                                {
                                    "question": "Ett FAQ fel har uppstått:",
                                    "answer": message,
                                }
                            ]

                    try:
                        searchForm = SearchFAQForm()
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
                    pagination = {}
                    page_list = []
                    is_paginated = False
                    start_extras = False
                    end_extras = False
                    max_page = 0
                    faqs = [
                        {
                            "question": "Ett språk fel har uppstått:",
                            "answer": message,
                        }
                    ]
                    searchForm = SearchFAQForm()
                    searchButton = {"buttonText": "Search"}
                comment = ""

                context = {
                    'gdpr_check': gdpr_check,
                    'search': False,
                    'faqs': faqs,
                    "searchTerms": "",
                    'searchForm': searchForm,
                    "searchButton": searchButton,
                    'is_paginated': is_paginated,
                    'start_page': start_extras,
                    'end_page': end_extras,
                    'page_list': page_list,
                    'max_page': max_page,
                    'page_obj': pagination,
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

            context = {
                'gdpr_check': gdpr_check,
                'search': False,
                'faqs': faqs,
                'searchForm': searchForm,
                "searchButton": searchButton,
            }
            return render(self.request, "faq.html", context)

# om_oss_view


class om_oss_view(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        context = {
            'gdpr_check': gdpr_check,
        }
        return render(self.request, "omoss.html", context)

    def post(self, *args, **kwargs):
        return redirect("core:omoss")

# teamet_view


class teamet_view(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)

        try:

            team_staff = TeamStaff.objects.all()
            people = []
            for ts in team_staff:
                if ts.active:
                    people.append(ts)

        except ObjectDoesNotExist:

            team_staff = [
                {
                    'image': "http://127.0.0.1:8000/media/media-root/89-896473_-strawberry-png-strawberry-clipart-strawberry-strawberry-clipart.png",
                    'name': "Mr Strawberry",
                    'position': "CEO",
                    'discription': "Dumtidumtidum",
                }
            ]

        context = {
            'gdpr_check': gdpr_check,
            "people": team_staff,
        }

        return render(self.request, "team.html", context)

    def post(self, *args, **kwargs):
        return redirect("core:team")

# vision_view


class vision_view(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        context = {
            'gdpr_check': gdpr_check,
        }
        return render(self.request, "vision.html", context)

    def post(self, *args, **kwargs):
        return redirect("core:vision")

# freight info


class freight_view(View):
    def get(self, *args, **kwargs):
        # GDPR check
        gdpr_check = check_gdpr_cookies(self)
        context = {
            'gdpr_check': gdpr_check,
        }
        return render(self.request, "freight.html", context)

    def post(self, *args, **kwargs):
        return redirect("core:freight")


class LogOutModView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        theUser = self.request.user
        orders = Order.objects.filter(who=theUser)
        for order in orders:
            order.who = None
            order.being_read = False
            order.save()
        logout(self.request)
        return redirect("core:home")


class SuccessView(View):
    def get(self, *args, **kwargs):
        gdpr_check = check_gdpr_cookies(self)
        theUser = self.request.user

        # get the content of the basket
        order = Order.objects.get(
            user=theUser, ordered=False)

        # update the order dates and set to ordered
        order.ordered = True
        order.ordered_date = make_aware(datetime.now())
        order.updated_date = make_aware(datetime.now())
        # to find this on the confirmation page set who to user
        order.who = theUser
        order.save()
        return redirect("core:confirmation")


class ConfirmationView(View):
    def get(self, *args, **kwargs):
        gdpr_check = check_gdpr_cookies(self)
        theUser = self.request.user

        # get the order

        order = Order.objects.get(who=theUser)
        # set who to null
        order.who = None
        order.save()

        # display confirmation

        context = {
            "gdpr_check": gdpr_check,
            "order": order,
        }

        return render(self.request, "success.html", context)


class CancelledView(View):
    def get(self, *args, **kwargs):
        # payment cancelled set message and redirect to basket
        message = "Betalning avbruten."
        messages.warning(
            self.request, message)
        return redirect("core:order-summary")


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        # FIX THIS ON UPLOAD
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # get the content of the basket
        theUser = request.user
        order = Order.objects.get(
            user=theUser, ordered=False)
        theUserInfo = UserInfo.objects.get(user=theUser)
        theName = "Orderreferens: " + order.ref_code
        # sent in öre
        theAmount = int(order.total_price * 100)
        try:
            # Create new Checkout Session for the order
            checkout_session = stripe.checkout.Session.create(

                client_reference_id=theUser.id if theUser.is_authenticated else None,
                customer_email=theUserInfo.email,
                success_url=domain_url +
                'success/',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': theName,
                        'quantity': 1,
                        'currency': 'SEK',
                        'amount': theAmount,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    print("yes")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)


class ConfirmInfo(View):
    def get(self, *args, **kwargs):
        gdpr_check = check_gdpr_cookies(self)
        theUser = self.request.user

        # get the content of the basket
        order = Order.objects.get(
            user=self.request.user, ordered=False)

        context = {
            "gdpr_check": gdpr_check,
            "order": order,
        }

        return render(self.request, "confirmInfo.html", context)

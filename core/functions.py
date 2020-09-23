from slugify import slugify
from datetime import datetime, timedelta
from core.models import *
from moderator.forms import *

import random
import string


def which_page(self):
    path = self.request.get_full_path()
    split_path = path.split("/")
    page = split_path[-1]
    if page == "":
        page = 1
    else:
        page_number = page.split("=")
        page = int(page_number[1])
    return page


def where_am_i(self):
    path = self.request.get_full_path()
    split_path = path.split("/")
    page = split_path[-1]
    if page == "":
        page = split_path[-2]
    return page


def where_am_i_and_page(self):
    path = self.request.get_full_path()
    split_path = path.split("/")
    page = split_path[-1]
    am_i = "none"
    categories = Category.objects.all()
    for cat in categories:
        if (page == cat.slug):
            am_i = page
            page = 1

    if(am_i == "none"):
        am_i = split_path[-2]

        page_number = page.split("=")
        page = int(page_number[1])
        seeking_i = page_number[0].split("?")
        am_i = seeking_i[0]

    return page, am_i


def test_slug_company(slug):
    test = False
    companyQuery = CompanyInfo.objects.filter(slug=slug)
    if len(companyQuery) > 0:
        test = True
    return test


def create_slug_address(address):
    toSlug = address.street_address + \
        "B" + str(address.user.id)
    testSlug = slugify(toSlug)
    existingSlug = test_slug_address(testSlug)
    i = 1
    while existingSlug:
        toSlug = address.street_address + \
            "B" + str(address.user.id) + "_" + str(i)
        testSlug = slugify(toSlug)
        existingSlug = test_slug_address(testSlug)
        i += 1

    return testSlug


def test_slug_address(slug):
    test = False
    addressQuery = Address.objects.filter(slug=slug)
    if len(addressQuery) > 0:
        test = True
    return test


def test_slug_address_of_user(slug, theUser):
    test = False
    addressQuery = Address.objects.filter(user=theUser, slug=slug)
    if len(addressQuery) > 0:
        test = True
    return test


def new_address_default(address):
    # remove default from any other default address of the same type
    otherAddresses = Address.objects.filter(
        address_type=address.address_type, default=True)
    for otherAddress in otherAddresses:
        otherAddress.default = False
        otherAddress.save()


def get_next_order_date(subdate, intervall):
    if intervall == '001':
        # add a week
        d = timedelta(days=7)
        add_date = subdate
        next_date = add_date + d

        return next_date

    elif intervall == '002':
        # add two weeks
        d = timedelta(days=14)
        add_date = subdate
        next_date = add_date + d

        return next_date

    elif intervall == '010':
        # add a month
        d = timedelta(days=30)
        add_date = subdate
        next_date = add_date + d

        return next_date
    elif intervall == '020':
        # add two months
        d = timedelta(days=60)
        add_date = subdate
        next_date = add_date + d

        return next_date
    elif intervall == '100':
        # add six months
        d = timedelta(days=182)
        add_date = subdate
        next_date = add_date + d

        return next_date
    elif intervall == '200':
        # add a year
        d = timedelta(days=365)
        add_date = subdate
        next_date = add_date + d

        return next_date
    else:
        # this shouldnt be able to happen. do nothing
        return subdate


def save_subItems_and_orderItems(sub, amount, product):
    # create a subscription item object
    subItem = SubscriptionItem()
    subItem.user = sub.user
    subItem.subscription = sub
    subItem.item = product
    subItem.item_title = product.title
    subItem.price = product.price
    discount_price = 1
    if product.discount_price is not None:
        discount_price = product.discount_price
    subItem.discount_price = discount_price
    subItem.quantity = amount
    total_price = product.price * discount_price * amount
    subItem.total_price = total_price

    # new orderItem object
    orderItem = OrderItem()
    # set basic valeus
    orderItem.user = sub.user
    orderItem.ordered = True
    orderItem.item = product
    orderItem.title = product.title
    orderItem.quantity = subItem.quantity
    orderItem.price = product.price
    orderItem.discount_price = discount_price
    orderItem.total_price = total_price
    # save orderitem
    orderItem.save()
    # save subitems
    subItem.save()
    return orderItem


def save_orderItem(subItem):
    # new orderItem object
    orderItem = OrderItem()
    # set basic valeus
    orderItem.user = subItem.user
    orderItem.ordered = True
    orderItem.item = subItem.item
    orderItem.title = subItem.item_title
    orderItem.quantity = subItem.quantity
    orderItem.price = subItem.price
    orderItem.discount_price = subItem.discount_price
    orderItem.total_price = subItem.total_price
    orderItem.sent = False
    # save orderitem
    orderItem.save()
    return orderItem


def sameAddress_support(theUser, form_street_address, form_post_town, form_address_type, default):
    # start by checking that we dont already have this address
    sameBilling = 0
    sameShipping = 0
    message = ''
    addresses = Address.objects.filter(user=theUser)

    for anAddress in addresses:
        if form_street_address == anAddress.street_address:
            if form_post_town == anAddress.post_town:
                if form_address_type == "A":
                    if anAddress.address_type == "S":
                        sameShipping = anAddress.id
                    elif anAddress.address_type == "B":
                        sameBilling = anAddress.id
                    return sameShipping, sameBilling, message

                elif anAddress.address_type == form_address_type:
                    message = "Address already exists"
                    if default and not anAddress.default:
                        # remove default from other addresses of same type
                        compAddresses = Address.objects.filter(
                            user=theUser, address_type=form_address_type)
                        for sameAddress in compAddresses:
                            if sameAddress.default:
                                sameAddress.default = False
                                sameAddress.save()
                                testAddress = Address.objects.get(
                                    id=sameAddress.id)
                        # add default to this address
                        anAddress.default = True
                        anAddress.save()
                        message = "Address already exists. Default changed."
                    return sameShipping, sameBilling, message
                else:
                    return sameShipping, sameBilling, message
            else:
                return sameShipping, sameBilling, message
        else:
            return sameShipping, sameBilling, message


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def test_order_ref_code(rcode):
    try:
        all_orders = Order.objects.all()
        test = False
        for order in all_orders:
            if order.ref_code == rcode:
                test = True

        if test:
            rcode = create_ref_code()
            rcode = test_order_ref_code(rcode)

        return rcode
    except ObjectDoesNotExist:
        return rcode


def get_order_total(order):
    # calculate total
    total = 0
    # items total
    orderItems = order.items.all()
    i = 0
    for item in orderItems:
        if item.discount_price > 0:
            total = total + item.discount_price
        else:
            total = total + item.price
        i = i + item.quantity
    # coupons
    coupon = order.coupon
    if coupon is not None:
        if coupon.coupon_type == "Percent":
            total = total * coupon.amount
        elif coupon.coupon_type == "Amount":
            total = total - coupon.amount
        # if we do any other types this will need adding to

    # freight
    freight = order.freight
    if freight is not None:
        # need to add the amount to the database later for easier adjustment. Also check with company what the amount is
        if i < 6:
            total = total + freight.amount
    # return total
    return total


def calculate_freight(order, freight):
    # calculate freight here for any order for now just return freight static amount as we dont have the relavant numbers
    return freight.amount


def get_message(theType, theCode):
    # get this from cookie later
    language = 'swe'
    languageObject = LanguageChoices.objects.get(language_short=language)
    if theType == "info":
        messageObject = InformationMessages.objects.get(
            code=theCode, language=languageObject)
        return messageObject.text
    elif theType == "error":
        messageObject = ErrorMessages.objects.get(
            code=theCode, language=languageObject)
        return messageObject.text
    elif theType == "warning":
        messageObject = WarningMessages.objects.get(
            code=theCode, language=languageObject)
        return messageObject.text
    else:
        return "There was an error retrieving this message. Contact IT support imidiately."


def get_list_of_pages(selected_page, max_page):

    i = 1
    max_number = default_pagination_values
    page_list = []
    where = "unset"

    if(selected_page == 1):
        if (selected_page + max_number > max_page):
            max_number = max_page

        while i <= max_number:
            page_list.append(i)
            i += 1

        if (max_number <= 5):
            where = "no extras"
        else:
            where = "start"

        return page_list, where

    elif (selected_page == max_page):

        i = max_page - (max_number - 1)
        if (i >= 1):
            while i <= max_page:
                page_list.append(i)
                i += 1

            where = "no extras"
        else:
            i = 1
            while i <= max_page:
                page_list.append(i)
                i += 1
            where = "end"

        return page_list, where

    elif (selected_page - 2 <= 1):
        # here we have less than 5 pages but still pagination or we are situated close to the start (ex page 2)

        if (max_page <= max_number):
            # 5 pages or less
            max_number = max_page

            while i <= max_number:
                page_list.append(i)
                i += 1

            where = "no extras"

        else:
            # max pages more than max_number but close to the edge

            while i <= max_number:
                page_list.append(i)
                i += 1

            where = "start"

        return page_list, where

    elif (selected_page + 2 >= max_page):
        # if we have less than 5 pages we wont be here  just create and edge list

        where = "end"

        i = max_page - (max_number - 1)

        while i <= max_page:
            page_list.append(i)
            i += 1

        return page_list, where
    else:
        # we're somewhere in the middle away from min and max

        i = selected_page - 2
        max_number = selected_page + 2

        while i <= max_number:
            page_list.append(i)
            i += 1

        if i == 1:
            where = "start"
        elif max_number == max_page:
            where = "end"
        else:
            where = "mid"

        return page_list, where

#from slugify import slugify
from django.template.defaultfilters import slugify
from datetime import datetime, timedelta
from core.models import *
from moderator.forms import *
from django.http import HttpResponse

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
        address.address_type + str(address.user.id)
    preTestSlug = slugify(toSlug)
    # we dont want anything besides a-z and 1-0 as well as -
    testSlugA = preTestSlug.replace("ä", "a")
    testSlugAa = preTestSlug.replace("å", "a")
    testSlugO = preTestSlug.replace("ö", "a")
    testSlug = testSlugO
    existingSlug = test_slug_address(testSlug)
    i = 1
    while existingSlug:
        toSlug = address.street_address + \
            address.address_type + str(address.user.id) + "_" + str(i)
        preTestSlug = slugify(toSlug)
        # we dont want anything besides a-z and 1-0 as well as - slugify removes unwanted special characters but not non a-z letters
        testSlugA = preTestSlug.replace("ä", "a")
        testSlugAa = preTestSlug.replace("å", "a")
        testSlugO = preTestSlug.replace("ö", "a")
        testSlug = testSlugO
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
    address.default = True
    address.save()


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
        if item.discount_price != None:
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
        free_freight = 6
        if i < free_freight:
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
    page_list = []
    where = "unset"
    # if we are on the first page list the first 5 if there are that many and note if there are that many or more
    if(selected_page == 1):
        end = 5
        if max_page < 5:
            end = max_page
        while i <= end:
            page_list.append(i)
            i += 1

        if max_page <= end + 1:
            where = "no extras"
        else:
            where = "start"
        return page_list, where
    # if selected page is the end page make a list from 5 less up and mark it as end if 5 less isnt 1 or lower
    elif (selected_page == max_page):
        i = max_page - 5

        if i <= 1:
            i = 1

            where = "no extras"
        else:
            if i > 2:
                where = "end"

        while i <= max_page:
            page_list.append(i)
            i += 1

        return page_list, where

    # if  we are close to 1 but not far enough away to make a 1 ..  n n n n n n .. max
    elif (selected_page - 3 <= 1):
        # basically we have pagination and selected page is nr 2 3 or 4

        if (max_page <= 5):
            # 5 pages or less

            while i <= max_page:
                page_list.append(i)
                i += 1

            where = "no extras"
            # this creates maximum 1 2 3 4 5

        else:
            # more pages than 5 ( 1 2 3 4 5 or 2 3 4 5 6 )
            end = 5
            if selected_page == 4:
                i = 2
                end = 6
                where = "4"
            else:
                where = "start"

            while i <= end:
                page_list.append(i)
                i += 1

        return page_list, where

    # if max pages is more than 5 and we are close to max but not far enough away to make a 1 ..  n n n n n n .. max
    elif (selected_page + 3 >= max_page):

        where = "end"

        i = max_page - 4

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

        where = "mid"

        return page_list, where


def calculate_total_order(order):
    total = 0
    # get the items
    all_items = order.items.all()

    for i in all_items:
        total = total + i.total_price

    if(order.freight):
        freight = int(order.freight.amount)

        total = total + freight

    return total


def check_gdpr_cookies(self):
    test = self.request.COOKIES.get('GDPR')
    if test:
        return False
    else:
        response = HttpResponse()
        response.set_cookie('GDPR', "gdpr")
        return True


def get_anonymous_user():
    user_new_id = 1

    users = User.objects.all()

    same = True
    while(same):
        test_same = False
        for user in users:
            if str(user_new_id) == user.username:
                user_new_id += 1
                test_same = True
        if not test_same:
            same = False

    return user_new_id


def update_order_total(order):
    items = order.items.all()
    total = 0

    for item in items:
        total = total + item.total_price

    if order.freight_price != None:
        total = total + order.freight_price

    if order.coupon_amount != None:
        if coupon.coupon_type == "Percent":
            total = total * order.coupon_amount
        elif coupon.coupon_type == "Amount":
            total = total - order.coupon_amount
    return total

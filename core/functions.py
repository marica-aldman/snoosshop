from slugify import slugify
from datetime import datetime, timedelta
from core.models import *

import random
import string


def where_am_i(self):
    path = self.request.get_full_path()
    split_path = path.split("/")
    page = split_path[-1]
    if page == "":
        page = split_path[-2]
    return page


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


def sameAddress_moderator(theUser, form_street_address, form_post_town, form_address_type):
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
                            user=theUser, address_type=anAddress.address_type)
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


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

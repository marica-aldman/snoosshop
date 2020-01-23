from django import forms
from datetime import datetime
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from core.models import *


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

INTERVALL_CHOICES = (
    ('001', 'En gång i veckan'),
    ('002', 'Varannan vecka'),
    ('010', 'En gång i månaden'),
    ('020', 'Varannan månad'),
    ('100', 'Var sjätte månad'),
    ('200', 'En gång om året'),
)


class SubscriptionForm(forms.ModelForm):
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    next_order_date = forms.DateTimeField()
    intervall = forms.ChoiceField(choices=INTERVALL_CHOICES)

    def __init__(self, adresses, subid, *args, **kwargs):
        super(SubscriptionForm, self).__init__(*args, **kwargs)

        # add adress fields from the supplied adresses

        self.shipping_address = forms.ChoiceField(
            choices=adresses, max_length=3)
        self.billing_address = forms.ChoiceField(
            choices=adresses, max_length=3)

        # get all available products and place in an object for later

        all_products = Item()
        all_products = all_products.objects.all()

        # create a choice list from the available products

        products = {}

        for product in all_products:
            products.append({'id': product.id, 'title': product.title})

        # create a subscription object and retrive the subscription if there is one

        sub = Subscription()
        if subid != 0:
            sub = sub.objects.get(id=subid)

            all_order_items = sub.items
            i = 1

            for order_item in all_order_items:
                field_name1 = 'product_%s' % (i,)
                self.fields[field_name1] = forms.ChoiceField(
                    choices=products, max_length=3, initial=order_item.item)
                field_name2 = 'amount_%s' % (i,)
                self.fields[field_name2] = forms.IntegerField(
                    min_value=1, value=order_item.quantity)
                i += 1

        else:
            field_name1 = 'product_1'
            self.fields[field_name1] = forms.ChoiceField(
                choices=products, max_length=3)
            field_name2 = 'amount_1'
            self.fields[field_name2] = forms.IntegerField(
                min_value=1)


class ProfileForm(forms.ModelForm):
    def __init__(self, id, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # get the user info and place in object

        user = UserInfo()
        user = user.objects.get(id=id)

        # get all adresses

        all_adresses = Address()
        all_adresses = all_adresses.objects.get(user=user.user)

        # make a choice variable from the adresses

        adresses = {}

        for adress in all_adresses:
            adresses.append({'id': adress.id, 'street': adress.street_address})

        self.first_name = forms.CharField(
            max_length=50, blank=True, null=True, initial=user.first_name)
        self.last_name = forms.CharField(
            max_length=50, blank=True, null=True, initial=user.last_name)
        self.email = forms.EmailField(initial=user.email)
        self.telephone = forms.CharField(
            max_length=50, blank=True, null=True, initial=user.telephone)

        # check if there is a company

        is_company = False
        if user.companyID:
            is_company = True

        if is_company:
            company = CompanyInfo()
            company = CompanyInfo(id=user.companyID)
            self.company_name = forms.CharField(
                max_length=50, blank=True, null=True, initial=company.company)
            self.company_org = forms.CharField(
                max_length=50, blank=True, null=True, initial=company.organisation_number)

            self.company_adress = forms.ChoiceField(
                choices=adresses, max_length=3, initial=company.adressID)


class InitialSupportForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=50)
    message = forms.CharField(widget=forms.Textarea)


class AdressForm(forms.ModelForm):
    def __init__(self, id, *args, **kwargs):
        super(AdressForm, self).__init__(*args, **kwargs)

        # check if there is an adress, get the adress and place in object then create the fields from the object if there is one

        adress = Address()
        adress = adress.objects.get(id=id)

        if len(adress) == 0:
            self.street_address = forms.CharField(max_length=100)
            self.apartment_address = forms.CharField(max_length=100)
            self.country = CountryField(multiple=False)
            self.zip = forms.CharField(max_length=100)
            self.address_type = forms.CharField(
                max_length=1, choices=ADDRESS_CHOICES)
            self.default = forms.BooleanField(default=False)
        else:
            self.street_address = forms.CharField(
                max_length=100, initial=adress.street_address)
            self.apartment_address = forms.CharField(
                max_length=100, initial=adress.apartment_address)
            self.country = CountryField(multiple=False, initial=adress.country)
            self.zip = forms.CharField(max_length=100, initial=adress.zip)
            self.address_type = forms.CharField(
                max_length=1, choices=ADDRESS_CHOICES, initial=adress.address_type)
            self.default = forms.BooleanField(default=adress.default)


# add cookie settings and settings as well as further contact form for support

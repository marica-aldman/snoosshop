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

ADDRESS_CHOICES_EXTENDED = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
    ('A', 'BOTH'),
)

INTERVALL_CHOICES = (
    ('001', 'En gång i veckan'),
    ('002', 'Varannan vecka'),
    ('010', 'En gång i månaden'),
    ('020', 'Varannan månad'),
    ('100', 'Var sjätte månad'),
    ('200', 'En gång om året'),
)


class EditSubscriptionForm(forms.Form):
    start_date = forms.DateTimeField(required=True)
    intervall = forms.ChoiceField(choices=INTERVALL_CHOICES, required=True)

    def __init__(self, theUser, slug='save', *args, **kwargs):
        super(EditSubscriptionForm, self).__init__(*args, **kwargs)
        # check if the slug is for a new or editing an old sub and if it is an old one get the old one
        initialornot = True
        if slug == "new":
            initialornot = False
            subcription = Subscription()
            subcription.id = -1
        elif slug == "newSave":
            initialornot = True
            subscription = Subscription()
            subcription.id = -2
        else:
            initialornot = True
            subcription = Subscription.objects.filter(user=theUser, slug=slug)
        # remove labels for the current fields
        self.fields['start_date'].label = ''
        self.fields['intervall'].label = ""

        # get the users shipping and billing adresses
        addresses_s = Address.objects.filter(user=theUser, address_type="S")
        addresses_b = Address.objects.filter(user=theUser, address_type="B")
        # create a list for each adress type
        the_s_adresses = []
        for adress in addresses_s:
            the_s_adresses.append((adress.id, 'test'))
        the_b_adresses = []
        for adress in addresses_b:
            the_b_adresses.append((adress.id, 'test'))
        # make the lists to tuples for use with choicefield
        addresses_s_tuple = tuple(the_s_adresses)
        addresses_b_tuple = tuple(the_b_adresses)
        
        # get all available products
        all_products = Item.objects.all()
        # create a list for the products
        products = []
        for product in all_products:
            products.append((product.id, product.title))
        # make the list a touple for use with the product ChoiceField
        product_tuple = tuple(products)

        i = 1
        for sub in subcription:
            # first name a hidden field for new or edit check
            if sub.slug == 'new':
                self.fields['new_or_old'] = forms.CharField(widget=forms.HiddenInput(), initial='newSave')
            subscriptionItems = SubscriptionItem.objects.filter(subscription=sub.id)

            # if we have items they will be in subItems
            for item in subscriptionItems:
                # create fields for all products in the subscription including initial value if it shouls have one
                field_name1 = 'product%s' % (i,)
                self.fields[field_name1] = forms.ChoiceField(choices=product_tuple, required=False, initial=item.item)
                # remove label
                self.fields[field_name1].label = ""

                # create fields for all amounts in the subscription including initial value
                field_name2 = 'amount%s' % (i,)
                self.fields[field_name2] = forms.IntegerField(min_value=1, required=False, initial=item.amount)
                # remove label
                self.fields[field_name2].label = ""
                # increment i
                i += 1
            # otherwise we need to add one set of these fields
            if not initialornot:
                self.fields['product1'] = forms.ChoiceField(choices=product_tuple, required=False)
                self.fields['amount1'] = forms.IntegerField(min_value=1, required=False)
            # create the adress choice fields and remove the labels
            if initialornot:
                self.fields['shipping'] = forms.ChoiceField(choices=addresses_s_tuple, required=False, initial=sub.shipping_address)
            else:
                self.fields['shipping'] = forms.ChoiceField(choices=addresses_s_tuple, required=False)
            self.fields['shipping'].label = ""
            if initialornot:
                self.fields['billing'] = forms.ChoiceField(choices=addresses_b_tuple, required=False, initial=sub.billing_address)
            else:
                self.fields['billing'] = forms.ChoiceField(choices=addresses_b_tuple, required=False)
            self.fields['shipping'].label = ""
            # set initials for the other fields if needed
            if initialornot:
                self.fields['intervall'].initial = sub.intervall
                self.fields['start_date'].initial = sub.start_date

    def get_product_fields(self):
        for field_name in self.fields:
            if field_name.startswith('product'):
                yield self[field_name]
    
    def get_amount_fields(self):
        for field_name in self.fields:
            if field_name.startswith('amount'):
                yield self[field_name]

    def clean(self):
        products = set()
        i = 1
        field_name = 'product%s' % (i,)
        while self.cleaned_data.get(field.name):
            products = self.cleaned_data[field_name]
            if product in products:
                self.add_error(field_name, 'Duplicate')
            else:
                products.add(product)
            i += 1
            field_name = 'product%s' % (i,)
        self.cleaned_data['products'] = products

        amounts = set()
        i = 1
        field_name = 'amount%s' % (i,)
        while self.cleaned_data.get(field.name):
            amounts = self.cleaned_data[field_name]
            if amount in amounts:
                self.add_error(field_name, 'Duplicate')
            else:
                amounts.add(amount)
            i += 1
            field_name = 'amount%s' % (i,)
        self.cleaned_data['amounts'] = amounts

class NewSubscriptionForm(forms.Form):
    start_date = forms.DateTimeField(required=True)
    intervall = forms.ChoiceField(choices=INTERVALL_CHOICES, required=True)
    amount1 = forms.IntegerField(min_value=1, required=True)

    # get all available products and place in an object for later

    all_products = Item.objects.all()

    # create a choice list from the available products

    products = []

    for product in all_products:
        products.append((product.id, product.title))

    product_tuple = tuple(products)

    product1 = forms.ChoiceField(choices=product_tuple, required=True)

    def __init__(self, *args, **kwargs):
        super(NewSubscriptionForm, self).__init__(*args, **kwargs)

        self.fields['start_date'].label = ""
        self.fields['intervall'].label = ""
        self.fields['amount1'].label = ""
        self.fields['product1'].label = ""


class NewAddressForm(forms.Form):
    street_address = forms.CharField(max_length=100, required=True)
    apartment_address = forms.CharField(max_length=100, required=False)
    post_town = forms.CharField(max_length=100, required=True)
    post_code = forms.CharField(max_length=100, required=True)
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    address_type = forms.ChoiceField(choices=ADDRESS_CHOICES_EXTENDED)

    def __init__(self, *args, **kwargs):
        super(NewAddressForm, self).__init__(*args, **kwargs)

        self.fields['street_address'].label = ""
        self.fields['apartment_address'].label = ""
        self.fields['post_town'].label = ""
        self.fields['post_code'].label = ""
        self.fields['country'].label = ""
        self.fields['address_type'].label = ""


class ProfileForm(forms.ModelForm):
    def __init__(self, id, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # get the user info and place in object

        user = UserInfo()
        user = user.objects.get(id=id)

        # get all addresses

        all_addresses = Address()
        all_addresses = all_addresses.objects.get(user=user.user)

        # make a choice variable from the addresses

        addresses = {}

        for address in all_addresses:
            addresses.append({'id': address.id, 'street': address.street_address})

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

            self.company_address = forms.ChoiceField(
                choices=addresses, max_length=3, initial=company. addressID)


class InitialSupportForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=50)
    message = forms.CharField(widget=forms.Textarea)


class addressForm(forms.ModelForm):
    def __init__(self, id, *args, **kwargs):
        super( addressForm, self).__init__(*args, **kwargs)

        # check if there is an address, get the address and place in object then create the fields from the object if there is one

        try:
            address = Address.objects.filter(
                user=self.request.user, id=self.id)
        except ObjectDoesNotExist:
            address = {}

        self.street_address = forms.CharField(
            max_length=100, initial= address.street_address)
        self.apartment_address = forms.CharField(
            max_length=100, initial= address.apartment_address)
        self.country = CountryField(multiple=False, initial= address.country)
        self.zip = forms.CharField(max_length=100, initial= address.zip)
        self.address_type = forms.CharField(
            max_length=1, choices=ADDRESS_CHOICES, initial= address.address_type)
        self.default = forms.BooleanField(default= address.default)


class InitialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InitialForm, self).__init__(*args, **kwargs)

        self.firstName = forms.CharField(
            max_length=50)
        self.last_name = forms.CharField(
            max_length=50)
        self.email = forms.EmailField()
        self.telephone = forms.CharField(
            max_length=50)

        self.is_company = forms.BooleanField(default=False)
        self.company = forms.CharField(max_length=50)
        self.organisation_number = forms.CharField(max_length=50)

        self.street_address1 = forms.CharField(max_length=100)
        self.apartment_address1 = forms.CharField(max_length=100)
        self.country1 = CountryField(multiple=False)
        self.zip1 = forms.CharField(max_length=100)
        self.default1 = forms.BooleanField(default=False)

        self.same = forms.BooleanField(default=False)

        self.street_address2 = forms.CharField(max_length=100)
        self.apartment_address2 = forms.CharField(max_length=100)
        self.country2 = CountryField(multiple=False)
        self.zip2 = forms.CharField(max_length=100)
        self.default2 = forms.BooleanField(default=False)


# add cookie settings and settings as well as further contact form for support

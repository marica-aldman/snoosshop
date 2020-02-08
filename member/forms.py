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
    start_date = forms.DateTimeField()
    intervall = forms.ChoiceField(choices=INTERVALL_CHOICES)

    def __init__(self, theUser, slug='save', n_o_p="1", *args, **kwargs):
        super(EditSubscriptionForm, self).__init__(*args, **kwargs)
        # do everything that should be done regardless if it is a new or old subscription

        # remove labels for the current fields
        self.fields['start_date'].label = ''
        self.fields['intervall'].label = ''

        # get the users shipping and billing adresses
        addresses_s = Address.objects.filter(user=theUser, address_type="S")
        addresses_b = Address.objects.filter(user=theUser, address_type="B")
        # create a list for each adress type
        the_s_adresses = []
        for adress in addresses_s:
            the_s_adresses.append((adress.id, adress.street_address))
        the_b_adresses = []
        for adress in addresses_b:
            the_b_adresses.append((adress.id, adress.street_address))
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

        # make a JSON with all the products
        products_html = "["

        for product in all_products:
            id = str(product.id)
            title = str(product.title)
            products_html = products_html + \
                "{&quot;id&quot;: &quot" + id + \
                "&quot, &quot;title&quot;: &quot" + title + "&quot},"

        products_html = products_html + "]"

        # add a hidden field with the json for use with JS

        self.fields['list_of_products'] = forms.CharField(
            widget=forms.HiddenInput(), initial='products_html')

        # check if the slug is for a new or editing an old sub
        if slug == "new":
            # add all the neccessary fields that are left no initial value
            i = 1
            for i in range(int(n_o_p)):
                i += 1
                field_name1 = 'product%s' % (i,)
                self.fields[field_name1] = forms.ChoiceField(
                    choices=product_tuple, required=False)
                self.fields[field_name1].label = ""
                field_name2 = 'amount%s' % (i,)
                self.fields[field_name2] = forms.IntegerField(
                    min_value=1, required=False)
                self.fields[field_name2].label = ""
            self.fields['shipping_address'] = forms.ChoiceField(
                choices=addresses_s_tuple, required=False)
            self.fields['shipping_address'].label = ""
            self.fields['billing_address'] = forms.ChoiceField(
                choices=addresses_b_tuple, required=False)
            self.fields['billing_address'].label = ""
            # add hidden fields for checking if it is a new or old save
            self.fields['new_or_old'] = forms.CharField(
                widget=forms.HiddenInput(), initial='new')
            # add a hidden field for number of products
            self.fields['number_of_products'] = forms.CharField(
                widget=forms.HiddenInput(), initial=n_o_p)
        else:
            subcription = Subscription.objects.filter(user=theUser, slug=slug)

            i = 1
            test = "WTF"
            for sub in subcription:
                subscriptionItems = SubscriptionItem.objects.filter(
                    subscription=sub)
                test = "we have a sub"

                # if we have items they will be in subItems
                for item in subscriptionItems:
                    # create fields for all products in the subscription including initial value if it shouls have one
                    field_name1 = 'product%s' % (i,)
                    self.fields[field_name1] = forms.ChoiceField(
                        choices=product_tuple, required=False, initial=item.item)
                    # remove label
                    self.fields[field_name1].label = ""

                    # create fields for all amounts in the subscription including initial value
                    field_name2 = 'amount%s' % (i,)
                    self.fields[field_name2] = forms.IntegerField(
                        min_value=1, required=False, initial=item.quantity)
                    # remove label
                    self.fields[field_name2].label = ""
                    # increment i
                    i += 1
                    test = "we have items"

                # add hidden fields for checking if it is a new or old save
                self.fields['new_or_old'] = forms.CharField(
                    widget=forms.HiddenInput(), initial='old')

                # add a hidden field for number of products
                i = i - 1
                self.fields['number_of_products'] = forms.CharField(
                    widget=forms.HiddenInput(), initial=i)
                # add a hidden field for the subscription id
                self.fields['id'] = forms.CharField(
                    widget=forms.HiddenInput(), initial=sub.id)

                # create the adress choice fields and remove the labels
                self.fields['shipping_address'] = forms.ChoiceField(
                    choices=addresses_s_tuple, required=False, initial=sub.shipping_address)
                self.fields['shipping_address'].label = ""
                self.fields['billing_address'] = forms.ChoiceField(
                    choices=addresses_b_tuple, required=False, initial=sub.billing_address)
                self.fields['billing_address'].label = ""

                # set initials for the other fields
                self.fields['intervall'].initial = sub.intervall
                self.fields['start_date'].initial = sub.start_date

                # forloop test
                self.fields['test'] = forms.CharField(initial=test)

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

    """all_products = Item.objects.all()"""

    # create a choice list from the available products

    products = []

    """for product in all_products:
        products.append((product.id, product.title))"""

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
            addresses.append(
                {'id': address.id, 'street': address.street_address})

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
        super(addressForm, self).__init__(*args, **kwargs)

        # check if there is an address, get the address and place in object then create the fields from the object if there is one

        try:
            address = Address.objects.filter(
                user=self.request.user, id=self.id)
        except ObjectDoesNotExist:
            address = {}

        self.street_address = forms.CharField(
            max_length=100, initial=address.street_address)
        self.apartment_address = forms.CharField(
            max_length=100, initial=address.apartment_address)
        self.country = CountryField(multiple=False, initial=address.country)
        self.zip = forms.CharField(max_length=100, initial=address.zip)
        self.address_type = forms.CharField(
            max_length=1, choices=ADDRESS_CHOICES, initial=address.address_type)
        self.default = forms.BooleanField(default=address.default)


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

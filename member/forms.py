from django import forms
from datetime import datetime
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ObjectDoesNotExist
from core.models import *


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('I', 'Invoice'),
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
    payment = forms.ChoiceField(choices=PAYMENT_CHOICES)
    intervall = forms.ChoiceField(choices=INTERVALL_CHOICES)

    def __init__(self, *args, **kwargs):
        super(EditSubscriptionForm, self).__init__(*args, **kwargs)
        # do everything that should be done regardless if it is a new or old subscription

        # remove labels for the current fields
        self.fields['start_date'].label = ''
        self.fields['intervall'].label = ''

        # get all available products
        all_products = Item.objects.all()

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

        # create freight option
        freights = Freight.objects.all()
        the_freights = []
        for f in freights:
            the_freights.append((f.id, f.title))
        # make the lists to tuples for use with choicefield
        the_freights_tuple = tuple(the_freights)

        self.fields['freight'] = forms.ChoiceField(choices=the_freights_tuple)
        self.fields['freight'].label = ""
        print(freights)
        print(the_freights)
        print(the_freights_tuple)

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
        while self.cleaned_data.get(field_name):
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
        while self.cleaned_data.get(field_name):
            amounts = self.cleaned_data[field_name]
            if amount in amounts:
                self.add_error(field_name, 'Duplicate')
            else:
                amounts.add(amount)
            i += 1
            field_name = 'amount%s' % (i,)
        self.cleaned_data['amounts'] = amounts

    def populate(self, theUser, sub, old):
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

        if old:
            subscriptionItems = SubscriptionItem.objects.filter(
                subscription=sub)
            i = 1
            # if we have items they will be in subItems
            for subItem in subscriptionItems:
                item = subItem.item
                # create fields for all products in the subscription including initial value
                field_name1 = 'product%s' % (i,)
                self.fields[field_name1] = forms.ChoiceField(
                    choices=product_tuple, required=False, initial=item.id)
                # remove label
                self.fields[field_name1].label = ""

                # create fields for all amounts in the subscription including initial value
                field_name2 = 'amount%s' % (i,)
                self.fields[field_name2] = forms.IntegerField(
                    min_value=1, required=False, initial=subItem.quantity)
                # remove label
                self.fields[field_name2].label = ""
                # increment i
                i += 1
            # check the freight
            if sub.freight is not None:
                self.fields['freight'].widget.attrs.update(
                    {'initial': sub.freight})
            # add hidden fields for checking if it is a new or old save
            self.fields['new_or_old'] = forms.CharField(
                widget=forms.HiddenInput(), initial='old')

            # add a hidden field for number of products
            i = i - 1
            self.fields['number_of_products'] = forms.CharField(
                widget=forms.HiddenInput(), initial=i)
            # add a hidden field for the subscription id
            self.fields['sub_id'] = forms.CharField(
                widget=forms.HiddenInput(), initial=sub.id)
            # add a hidden field for the user id
            self.fields['u_id'] = forms.CharField(
                widget=forms.HiddenInput(), initial=theUser.id)

            # create the adress choice fields and remove the labels
            self.fields['shipping_address'] = forms.ChoiceField(
                choices=addresses_s_tuple, required=False, initial=sub.shipping_address.id)
            self.fields['shipping_address'].label = ""
            self.fields['billing_address'] = forms.ChoiceField(
                choices=addresses_b_tuple, required=False, initial=sub.billing_address.id)
            self.fields['billing_address'].label = ""

            # set initials for the other fields
            self.fields['intervall'].initial = sub.intervall
            self.fields['start_date'].initial = sub.start_date
        else:
            # add all the neccessary fields that are left no initial value
            i = 1
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
            # add a hidden field for the sub id
            self.fields['sub_id'] = forms.CharField(
                widget=forms.HiddenInput(), initial=0)
            # add a hidden field for the user id
            self.fields['u_id'] = forms.CharField(
                widget=forms.HiddenInput(), initial=theUser.id)
            # add a hidden field for number of products
            self.fields['number_of_products'] = forms.CharField(
                widget=forms.HiddenInput(), initial="1")

    def populate_from_submit(self):
        self.fields[field_name2] = forms.IntegerField(
            min_value=1, required=False, initial=self.request.POST[field_name2])
        self.fields['start_date'].widget.attrs.update(
            {'value': self.request.POST['start_date']})
        self.fields['intervall'].widget.attrs.update(
            {'value': self.request.POST['intervall']})
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
        # Freight
        self.fields['freight'].widget.attrs.update(
            {'initial': self.request.POST['freight']})
        # get all available products
        all_products = Item.objects.all()
        # create a list for the products
        products = []
        for product in all_products:
            products.append((product.id, product.title))
        # make the list a touple for use with the product ChoiceField
        product_tuple = tuple(products)

        # add all the neccessary fields that are left with initial value
        number_of_items = int(
            self.request.POST['number_of_products'])
        i = 1
        for i in range(number_of_items):
            field_name1 = 'product%s' % (i,)
            self.fields[field_name1] = forms.ChoiceField(
                choices=product_tuple, required=False, initial=self.request.POST[field_name1])
            self.fields[field_name1].label = ""
            field_name2 = 'amount%s' % (i,)
            self.fields[field_name2] = forms.IntegerField(
                min_value=1, required=False, initial=self.request.POST[field_name2])
            self.fields[field_name2].label = ""
        self.fields['shipping_address'] = forms.ChoiceField(
            choices=addresses_s_tuple, required=False, initial=self.request.POST['shipping_address'])
        self.fields['shipping_address'].label = ""
        self.fields['billing_address'] = forms.ChoiceField(
            choices=addresses_b_tuple, required=False, initial=self.request.POST['billing_address'])
        self.fields['billing_address'].label = ""
        # add hidden fields for checking if it is a new or old save
        self.fields['new_or_old'] = forms.CharField(
            widget=forms.HiddenInput(), initial=self.request.POST['new_or_old'])
        # add a hidden field for the user id
        self.fields['user_id'] = forms.CharField(
            widget=forms.HiddenInput(), initial=self.request.POST['user_id'])
        # add a hidden field for number of products
        self.fields['number_of_products'] = forms.CharField(
            widget=forms.HiddenInput(), initial=self.request.POST['number_of_products'])


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
    zip = forms.CharField(max_length=100, required=True)
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    address_type = forms.ChoiceField(
        choices=ADDRESS_CHOICES_EXTENDED, required=False)

    def __init__(self, *args, **kwargs):
        super(NewAddressForm, self).__init__(*args, **kwargs)

        self.fields['street_address'].label = ""
        self.fields['apartment_address'].label = ""
        self.fields['post_town'].label = ""
        self.fields['zip'].label = ""
        self.fields['country'].label = ""
        self.fields['address_type'].label = ""


class SetupAddressForm(forms.Form):
    street_address = forms.CharField(max_length=100, required=False)
    apartment_address = forms.CharField(max_length=100, required=False)
    post_town = forms.CharField(max_length=100, required=False)
    zip = forms.CharField(max_length=100, required=False)
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    address_type = forms.ChoiceField(
        choices=ADDRESS_CHOICES_EXTENDED, required=False)

    def __init__(self, *args, **kwargs):
        super(SetupAddressForm, self).__init__(*args, **kwargs)

        self.fields['street_address'].label = ""
        self.fields['apartment_address'].label = ""
        self.fields['post_town'].label = ""
        self.fields['zip'].label = ""
        self.fields['country'].label = ""
        self.fields['address_type'].label = ""

    def populate(self, theCompany, *args, **kwargs):
        address = theCompany.addressID
        self.fields['street_address'].widget.attrs.update(
            {'value': address.street_address})
        self.fields['apartment_address'].widget.attrs.update(
            {'value': address.apartment_address})
        self.fields['post_town'].widget.attrs.update(
            {'value': address.post_town})
        self.fields['zip'].widget.attrs.update(
            {'value': address.zip})
        self.fields['country'].widget.attrs.update(
            {'value': address.country})
        self.fields['address_type'].widget.attrs.update(
            {'value': address.address_type})

    def populate_from_slug(self, theSlug, *args, **kwargs):
        try:
            address = Address.objects.get(slug=theSlug)
        except ObjectDoesNotExist:
            address = Address()
        self.fields['street_address'].widget.attrs.update(
            {'value': address.street_address})
        self.fields['apartment_address'].widget.attrs.update(
            {'value': address.apartment_address})
        self.fields['post_town'].widget.attrs.update(
            {'value': address.post_town})
        self.fields['zip'].widget.attrs.update(
            {'value': address.zip})
        self.fields['country'].widget.attrs.update(
            {'value': address.country})
        self.fields['address_type'].widget.attrs.update(
            {'value': address.address_type})


class UserInformationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50, label="", required=True)
    last_name = forms.CharField(
        max_length=50, label="", required=True)
    email = forms.EmailField(
        label="", required=True)
    telephone = forms.CharField(
        max_length=50, label="", required=False)

    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'email',
                  'telephone']

    def __init__(self, *args, **kwargs):
        super(UserInformationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update(
            {'class': 'form-control textinput textInput mt-2 mb-2'})
        self.fields['last_name'].widget.attrs.update(
            {'class': 'form-control emailinput mt-2 mb-2'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control textinput textInput mt-2 mb-2'})
        self.fields['telephone'].widget.attrs.update(
            {'class': 'form-control textinput textInput mt-2 mb-2'})

    def populate(self, the_user, *args, **kwargs):
        userInfo = UserInfo.objects.get(user=the_user)
        # get the user info and place in object
        self.fields['first_name'].widget.attrs.update(
            {'value': userInfo.first_name})
        self.fields['last_name'].widget.attrs.update(
            {'value': userInfo.last_name})
        self.fields['email'].widget.attrs.update(
            {'value': userInfo.email})
        self.fields['telephone'].widget.attrs.update(
            {'value': userInfo.telephone})


class InitialSupportForm(forms.ModelForm):
    subject = forms.CharField(
        max_length=50)
    message = forms.CharField(widget=forms.Textarea)


class addressForm(forms.Form):

    def __init__(self, address, *args, **kwargs):
        super(addressForm, self).__init__(*args, **kwargs)

        try:
            self.fields['street_address'] = forms.CharField(
                max_length=100, required=True, label='', initial=address.street_address)
            self.fields['apartment_address'] = forms.CharField(
                max_length=100, required=False, label='', initial=address.apartment_address)
            self.fields['post_town'] = forms.CharField(
                max_length=100, required=True, label='', initial=address.post_town)
            self.fields['zip'] = forms.CharField(
                max_length=100, required=True, label='', initial=address.zip)
            # self.country = CountryField(blank_label='(select country)').formfield(required = False,widget = CountrySelectWidget(attrs={   'class': 'custom-select d-block w-100',}))
        except AttributeError(address):
            self.fields['street_address'] = forms.CharField(
                max_length=100, required=True, label='')
            self.fields['apartment_address'] = forms.CharField(
                max_length=100, required=False, label='')
            self.fields['post_town'] = forms.CharField(
                max_length=100, required=True, label='')
            self.fields['zip'] = forms.CharField(
                max_length=100, required=True, label='')
            # self.country = CountryField(blank_label='(select country)').formfield(required = False,widget = CountrySelectWidget(attrs={   'class': 'custom-select d-block w-100',}))


class CompanyInfoForm(forms.ModelForm):
    class Meta:
        model = CompanyInfo
        fields = ['company', 'organisation_number']

    def __init__(self, *args, **kwargs):
        super(CompanyInfoForm, self).__init__(*args, **kwargs)
        self.fields['company'].label = ''
        self.fields['company'].widget.attrs.update(
            {"class": "form-control textinput textInput mt-2 mb-2"})
        self.fields['organisation_number'].label = ''
        self.fields['organisation_number'].widget.attrs.update(
            {"class": "form-control textinput textInput mt-2 mb-2"})

    def populate(self, theUser, *args, **kwargs):
        companyInfo = CompanyInfo.objects.get(user=theUser)
        self.fields['company'].widget.attrs.update(
            {'value': companyInfo.company})
        self.fields['organisation_number'].widget.attrs.update(
            {'value': companyInfo.organisation_number})


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


# generic support form

class GenericSupportForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="")
    subject = forms.CharField(max_length=200, required=True, label="")
    message = forms.CharField(widget=forms.Textarea, label="")
    sent_date = forms.DateTimeField(required=False)
    slug = forms.SlugField(required=False)

    # sort this meta class out for generic model
    class Meta:
        model = GenericSupport
        fields = ['email', 'subject', 'message', 'sent_date', 'slug']

    def __init__(self, *args, **kwargs):
        super(GenericSupportForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control emailinput mt-2 mb-2'})
        self.fields['subject'].widget.attrs.update(
            {'class': 'form-control textinput textInput mt-2 mb-2'})

# add cookie settings and settings as well as further contact form for support


class CookieSettingsForm(forms.ModelForm):

    class Meta:
        model = Cookies
        fields = ['addapted_adds']

    def __init__(self, *args, **kwargs):
        super(CookieSettingsForm, self).__init__(*args, **kwargs)
        self.fields['addapted_adds'].label = ''
        self.fields['addapted_adds'].widget.attrs.update(
            {"style": "width: 20px; height: 20px; margin-top: 2px;"})

    def populate(self, theUser, *args, **kwargs):
        try:
            cookie_settings = Cookies.objects.get(user=theUser)
        except ObjectDoesNotExist:
            cookie_settings = Cookies()
            cookie_settings.user = theUser
            cookie_settings.save()
        if cookie_settings.addapted_adds:
            self.fields['addapted_adds'].widget.attrs.update(
                {'checked': ""})

from django import forms
from .models import FormFields, FormText, Freight


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
)


def freightChoices():

    freights = Freight.objects.all()

    freightList = []

    for f in freights:
        title = f.title
        id = f.id
        freightList.append((str(f.id), f.title))

    FreightsChoices = tuple(freightList)

    return FreightsChoices


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_zip = forms.CharField(required=False)
    s_post_town = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_zip = forms.CharField(required=False)
    b_post_town = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    freight_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=freightChoices)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Rabattkod',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class SearchFAQForm(forms.Form):
    searchTerm = forms.CharField(required=True)

    def language(self, theLanguage, *args, **kwargs):

        theFormField = FormFields.objects.get(formFieldType="search")
        searchField = FormText.objects.filter(
            language=theLanguage, theformFieldType=theFormField)
        for field in searchField:
            self.fields['searchTerm'].label = field.formTextLabel
            self.fields['searchTerm'].widget.attrs.update(
                {'placeholder': field.formTextPlaceholder})
            self.fields['searchTerm'].widget.attrs.update(
                {'class': 'p-2'})

        self.fields['searchID'].widget.attrs.update(
            {'style': 'hidden'})

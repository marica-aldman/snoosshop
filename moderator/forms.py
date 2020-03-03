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


class searchOrderForm(forms.Form):
    order_ref = forms.CharField(max_length=20, required=False, label="")
    order_id = forms.IntegerField(required=False, label="")
    user_id = forms.IntegerField(required=False, label="")


class searchUserForm(forms.Form):
    user_id = forms.IntegerField(required=False, label="")


class searchProductForm(forms.Form):
    product_id = forms.IntegerField(required=True, label="")

    def populate(self, product_id, *args, **kwargs):
        self.fields['product_id'].widget.attrs.update(
            {'value': product_id})


class editOrCreateProduct(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Item
        fields = ['title', 'price', 'discount_price', 'description']

    def __init__(self, *args, **kwargs):
        super(editOrCreateProduct, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['price'].label = ""
        self.fields['discount_price'].label = ""
        self.fields['description'].label = ""

    def populate(self, product_id, *args, **kwargs):
        product = Item.objects.get(id=product_id)
        self.fields['title'].widget.attrs.update(
            {'value': product.title})
        self.fields['price'].widget.attrs.update(
            {'value': product.price})
        self.fields['discount_price'].widget.attrs.update(
            {'value': product.discount_price})
        self.fields['description'].widget.attrs.update(
            {'value': product.description})

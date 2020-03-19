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
    product_id = forms.IntegerField(required=False, label="")

    def populate(self, product_id, *args, **kwargs):
        self.fields['product_id'].widget.attrs.update(
            {'value': product_id})


class searchCategoryForm(forms.Form):
    category_id = forms.IntegerField(required=False, label="")

    def populate(self, category_id, *args, **kwargs):
        self.fields['category_id'].widget.attrs.update(
            {'value': category_id})


class searchCouponForm(forms.Form):
    code = forms.CharField(required=False, label="")

    def populate(self, code, *args, **kwargs):
        self.fields['code'].widget.attrs.update(
            {'value': code})


class searchFreightForm(forms.Form):
    freight_id = forms.IntegerField(required=False, label="")

    def populate(self, freight_id, *args, **kwargs):
        self.fields['freight_id'].widget.attrs.update(
            {'value': freight_id})


class freightForm(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Freight
        fields = ['title', 'amount']

    def __init__(self, *args, **kwargs):
        super(freightForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['amount'].label = ""
        self.fields['title'].required = True
        self.fields['amount'].required = True

    def populate(self, freight_id, *args, **kwargs):
        freight = Freight.objects.get(id=freight_id)
        self.fields['title'].widget.attrs.update(
            {'value': freight.title})
        self.fields['amount'].widget.attrs.update(
            {'value': freight.amount})


class couponForm(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Coupon
        fields = ['code', 'amount']

    def __init__(self, *args, **kwargs):
        super(couponForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = ""
        self.fields['amount'].label = ""
        self.fields['code'].required = True
        self.fields['amount'].required = True

    def populate(self, coupon_id, *args, **kwargs):
        coupon = Coupon.objects.get(id=coupon_id)
        self.fields['code'].widget.attrs.update(
            {'value': coupon.code})
        self.fields['amount'].widget.attrs.update(
            {'value': coupon.amount})


class editOrCreateProduct(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Item
        fields = ['title', 'price', 'discount_price', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super(editOrCreateProduct, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['price'].label = ""
        self.fields['discount_price'].label = ""
        self.fields['description'].label = ""
        self.fields['image'].label = ""
        self.fields['image'].required = False

    def populate(self, product_id, *args, **kwargs):
        product = Item.objects.get(id=product_id)
        self.fields['title'].widget.attrs.update(
            {'value': product.title})
        self.fields['price'].widget.attrs.update(
            {'value': product.price})
        self.fields['discount_price'].widget.attrs.update(
            {'value': product.discount_price})
        self.fields['description'].initial = product.description


class editProductImage(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Item
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(editProductImage, self).__init__(*args, **kwargs)
        self.fields['image'].label = ""
        self.fields['image'].required = False


class editOrCreateCategory(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Category
        fields = ['title', 'discount_price', 'description']

    def __init__(self, *args, **kwargs):
        super(editOrCreateCategory, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['discount_price'].label = ""
        self.fields['description'].label = ""

    def populate(self, category_id, *args, **kwargs):
        category = Category.objects.get(id=category_id)
        self.fields['title'].widget.attrs.update(
            {'value': category.title})
        self.fields['discount_price'].widget.attrs.update(
            {'value': category.discount_price})
        self.fields['description'].initial = category.description

from django import forms
from datetime import datetime
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from core.models import *


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


class theAddressForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(theAddressForm, self).__init__(*args, **kwargs)

        self.fields['street_address'] = forms.CharField(
            max_length=100, required=True, label='')
        self.fields['apartment_address'] = forms.CharField(
            max_length=100, required=False, label='')
        self.fields['post_town'] = forms.CharField(
            max_length=100, required=True, label='')
        self.fields['zip'] = forms.CharField(
            max_length=100, required=True, label='')

    def populate(self, address, *args, **kwargs):

        self.fields['street_address'].initial = address.street_address
        self.fields['apartment_address'].initial = address.apartment_address
        self.fields['post_town'].initial = address.post_town
        self.fields['zip'].initial = address.zip

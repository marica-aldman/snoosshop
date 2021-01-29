from django import forms
from datetime import datetime
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
    freight_type = forms.ChoiceField(
        choices=(("1", "Nuvarande"), ("2", "Gamla")))

    def startup(self, *args, **kwargs):
        self.fields['freight_id'].widget.attrs.update(
            {'class': 'p-2'})
        self.fields['freight_type'].widget.attrs.update(
            {'class': 'p-2'})
        self.fields['freight_id'].label = "Id:"
        self.fields['freight_type'].label = "Status:"


class freightForm(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = Freight
        fields = ['title', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        super(freightForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['title'].required = True
        self.fields['amount'].label = ""
        self.fields['amount'].required = True
        self.fields['description'].label = ""
        self.fields['description'].required = True


class oldFreightForm(forms.ModelForm):
    # sort this meta class out

    class Meta:
        model = OldFreight
        fields = ['title', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        super(oldFreightForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = ""
        self.fields['title'].required = True
        self.fields['amount'].label = ""
        self.fields['amount'].required = True
        self.fields['description'].label = ""
        self.fields['description'].required = True


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
        self.fields['description'].widget.attrs.update(
            {'style': "width: 70%"})
        self.fields['image'].initial = product.image


class editOrCreateCategory(forms.ModelForm):

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


class SearchFAQForm(forms.Form):
    searchID = forms.IntegerField(required=False)
    searchTerm = forms.CharField(required=False)

    def language(self, theLanguage, *args, **kwargs):

        theFormField1 = FormFields.objects.get(formFieldType="FAQid")
        searchField1 = FormText.objects.filter(
            language=theLanguage, theformFieldType=theFormField1)
        for field in searchField1:
            self.fields['searchID'].label = field.formTextLabel
            self.fields['searchID'].widget.attrs.update(
                {'placeholder': field.formTextPlaceholder})
            self.fields['searchID'].widget.attrs.update(
                {'class': 'p-2'})

        theFormField2 = FormFields.objects.get(formFieldType="search")
        searchField2 = FormText.objects.filter(
            language=theLanguage, theformFieldType=theFormField2)
        for field in searchField2:
            self.fields['searchTerm'].label = field.formTextLabel
            self.fields['searchTerm'].widget.attrs.update(
                {'placeholder': field.formTextPlaceholder})
            self.fields['searchTerm'].widget.attrs.update(
                {'class': 'p-2'})

        # we need to be able to sort by language, so make a choice field with all languages

        languages = LanguageChoices.objects.all()
        # temporarily make this impossible to choose anything but the only language in the list, when more langugages are implemented add ("---", "---") to the original list
        lang_list = []
        for lang in languages:
            lang_list.append((lang.language_short, lang.language))
        lang_tuple = tuple(lang_list)

        theFormField3 = FormFields.objects.get(formFieldType="LanguageChoice")
        searchField3 = FormText.objects.filter(
            language=theLanguage, theformFieldType=theFormField3)
        for field in searchField3:

            self.fields['languages'] = forms.ChoiceField(
                choices=lang_tuple, required=False)
            self.fields['languages'].label = field.formTextLabel
            self.fields['languages'].widget.attrs.update(
                {'class': 'p-2'})


class NewFAQForm(forms.ModelForm):

    class Meta:
        model = FAQ
        fields = ['description', 'subject', 'content']

    def __init__(self, *args, **kwargs):
        super(NewFAQForm, self).__init__(*args, **kwargs)
        self.fields['description'].label = "Description"
        self.fields['subject'].label = "subject"
        self.fields['content'].label = "content"

    def language(self, aLanguage, *args, **kwargs):

        theFormField1 = FormFields.objects.get(
            formFieldType="NewFAQDescription")
        searchField1 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField1)
        for field in searchField1:
            self.fields['description'].label = field.formTextLabel
            self.fields['description'].widget.attrs.update(
                {'placeholder': field.formTextPlaceholder})
            self.fields['description'].widget.attrs.update(
                {'class': 'p-2'})


class UpdateFAQ(forms.ModelForm):

    class Meta:
        model = FAQ
        fields = ['description', 'subject', 'content']

    def _init_(self, *args, **kwargs):
        super(UpdateFAQ, self).__init__(*args, **kwargs)
        # OBS aLanguage is the users language settings and separate from the text addition
        self.fields['subject'].label = ""
        self.fields['subject'].widget.attrs.update(
            {'class': 'p-2'})
        self.fields['content'].label = ""
        self.fields['content'].widget.attrs.update(
            {'class': 'p-2'})

    def language(self, aLanguage, faq, *arg):
        # correct description label and add fields for subject and content labels so we can get the right language)
        self.fields['check'] = forms.IntegerField(widget=forms.HiddenInput())
        self.fields['check'].initial = faq.id
        theFormField0 = FormFields.objects.get(
            formFieldType="NewFAQDescription")
        searchField0 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField0)
        for field in searchField0:
            self.fields['description'].label = field.formTextLabel
        theFormField1 = FormFields.objects.get(
            formFieldType="NewFAQSubject")
        searchField1 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField1)
        for field in searchField1:
            fieldSubjectTitle = "LanguageSubjectTitle"
            self.fields[fieldSubjectTitle] = forms.CharField(
                required=False)
            self.fields[fieldSubjectTitle].label = field.formTextLabel
            self.fields[fieldSubjectTitle].widget.attrs.update(
                {'style': 'display: none;'})
        theFormField2 = FormFields.objects.get(
            formFieldType="NewFAQContent")
        searchField2 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField2)
        for afield in searchField2:
            fieldContentTitle = "LanguageContentTitle"
            self.fields[fieldContentTitle] = forms.CharField(
                required=False)
            self.fields[fieldContentTitle].label = afield.formTextLabel
            self.fields[fieldContentTitle].widget.attrs.update(
                {'style': 'display: none;'})

        self.fields['subject'].initial = faq.subject
        self.fields['content'].initial = faq.content
        self.fields['description'].widget.attrs.update(
            {'value': faq.description})
        self.fields['description'].widget.attrs.update(
            {'class': 'p-2', "readonly": 'readonly'})
        self.fields['subject'].widget.attrs.update(
            {'style': 'max-width: 85%'})
        self.fields['content'].widget.attrs.update(
            {'style': 'max-width: 85%'})

    def updateFromPost(self, aLanguage, faq, *arg):
        # correct description label and add fields for subject and content labels so we can get the right language)
        theFormField0 = FormFields.objects.get(
            formFieldType="NewFAQDescription")
        searchField0 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField0)
        for field in searchField0:
            self.fields['description'].label = field.formTextLabel
        theFormField1 = FormFields.objects.get(
            formFieldType="NewFAQSubject")
        searchField1 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField1)
        for field in searchField1:
            fieldSubjectTitle = "LanguageSubjectTitle"
            self.fields[fieldSubjectTitle] = forms.CharField(
                required=False)
            self.fields[fieldSubjectTitle].label = field.formTextLabel
            self.fields[fieldSubjectTitle].widget.attrs.update(
                {'style': 'display: none;'})
        theFormField2 = FormFields.objects.get(
            formFieldType="NewFAQContent")
        searchField2 = FormText.objects.filter(
            language=aLanguage, theformFieldType=theFormField2)
        for afield in searchField2:
            fieldContentTitle = "LanguageContentTitle"
            self.fields[fieldContentTitle] = forms.CharField(
                required=False)
            self.fields[fieldContentTitle].label = afield.formTextLabel
            self.fields[fieldContentTitle].widget.attrs.update(
                {'style': 'display: none;'})

        self.fields['description'].widget.attrs.update(
            {'class': 'p-2', "readonly": 'readonly'})


class NewFAQPerLanguage(forms.Form):

    def language(self, aLanguage, *args, **kwargs):
        # OBS aLanguage is the users language settings and separate from the text addition
        theLanguages = LanguageChoices.objects.all()
        for Language in theLanguages:
            labelTitle = Language.language
            self.fields[labelTitle] = forms.CharField(required=False)
            self.fields[labelTitle].value = Language.id
            self.fields[labelTitle].widget.attrs.update(
                {'style': 'display: none;'})
            theFormField1 = FormFields.objects.get(
                formFieldType="NewFAQSubject")
            searchField1 = FormText.objects.filter(
                language=aLanguage, theformFieldType=theFormField1)
            for field in searchField1:
                fieldSubjectTitle = Language.language + "SubjectTitle"
                self.fields[fieldSubjectTitle] = forms.CharField(
                    required=False)
                self.fields[fieldSubjectTitle].label = field.formTextLabel
                self.fields[fieldSubjectTitle].widget.attrs.update(
                    {'style': 'display: none;'})
            labelSubject = Language.language + "subject"
            self.fields[labelSubject] = forms.CharField(
                widget=forms.Textarea)
            self.fields[labelSubject].label = ""
            self.fields[labelSubject].widget.attrs.update(
                {'class': 'p-2'})
            theFormField2 = FormFields.objects.get(
                formFieldType="NewFAQContent")
            searchField2 = FormText.objects.filter(
                language=aLanguage, theformFieldType=theFormField2)
            for afield in searchField2:
                fieldContentTitle = Language.language + "ContentTitle"
                self.fields[fieldContentTitle] = forms.CharField(
                    required=False)
                self.fields[fieldContentTitle].label = field.formTextLabel
                self.fields[fieldContentTitle].widget.attrs.update(
                    {'style': 'display: none;'})
            labelContent = Language.language + "content"
            self.fields[labelContent] = forms.CharField(
                widget=forms.Textarea)
            self.fields[labelContent].label = ""
            self.fields[labelContent].widget.attrs.update(
                {'class': 'p-2'})

    def saveForm(self, post, description, *args, **kwargs):
        theLanguages = LanguageChoices.objects.all()
        for Language in theLanguages:
            # make an faq per language
            # language fields
            labelSubject = Language.language + "subject"
            labelContent = Language.language + "content"
            # new FAQ
            faq = FAQ()
            # populate faq
            faq.description = description
            faq.language = Language
            faq.subject = str(post.get(labelSubject))
            faq.content = str(post.get(labelContent))
            # save faq
            faq.save()

from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# standardised variables

ADDRESS_CHOICES = [
    {'key': 'B', 'name': 'Fakturaaddress'},
    {'key': 'S', 'name': 'Leveransaddress'},
]

ADDRESS_CHOICES_EXTENDED = [
    {'key': 'B', 'name': 'Fakturaaddress'},
    {'key': 'S', 'name': 'Leveransaddress'},
    {'key': 'BOTH', 'name': 'Båda'},
]

LANGUAGE_CHOICES = (
    ('swe', 'Svenska'),
    ('eng', 'English'),
    ('deu', 'Deutch'),
    ('rus', 'Russian'),
)

BUTTON_TYPES = (
    ('001', 'Search'),
    ('002', 'Save'),
    ('003', 'Login'),
    ('004', 'Logout'),
    ('005', 'Support'),
    ('006', 'Send'),
    ('007', 'Support'),
    ('008', 'Add to cart'),
    ('009', 'Cancel'),
    ('010', 'deactvate'),
    ('011', 'remove from cart'),
    ('012', 'continue shopping'),
    ('013', 'proceed to checkout'),
    ('014', 'redeem'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
    ('015', 'continue to checkout'),
)

default_pagination_values = 8


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    post_town = models.CharField(max_length=100, null=True)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    slug = models.SlugField(default='address')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("member:edit_address", kwargs={
            'slug': self.id
        })

    # for the support

    def support_get_absolute_url(self):
        return reverse("support:edit_address", kwargs={
            'slug': self.slug
        })

    class Meta:
        verbose_name_plural = 'Addresses'


class CompanyInfo(models.Model):
    # name, orgnr, addressid
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    company = models.CharField(max_length=50, blank=True, null=True)
    organisation_number = models.CharField(
        max_length=50, blank=True, null=True)
    addressID = models.ForeignKey(
        Address, on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(default='company')

    def __str__(self):
        return self.company

    def get_absolute_url(self):
        return reverse("member:edit_companyInfo", kwargs={
            'slug': self.slug
        })

    # for the moderator

    def moderator_get_absolute_url(self):
        return reverse("moderator:edit_company", kwargs={
            'slug': self.slug
        })


class UserInfo(models.Model):
    # user, first name, last name, company, email, phone
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField()
    telephone = models.CharField(max_length=50, blank=True, null=True)
    company = models.BooleanField(default=False)
    companyID = models.ForeignKey(CompanyInfo,
                                  on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(default='userinfo')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("member:edit_userInfo", kwargs={
            'slug': self.slug
        })

    # for the moderator

    def moderator_get_absolute_url(self):
        return reverse("moderator:edit_user", kwargs={
            'slug': self.slug
        })


class Freight(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=False)
    description = models.CharField(max_length=256, null=True)
    amount = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url_moderator(self):
        return reverse("moderator:freight", kwargs={
            'slug': self.slug
        })

    def get_absolute_url_moderator_new(self):
        return reverse("moderator:freight", kwargs={
            'slug': 'new'
        })


class OldFreight(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=False)
    description = models.CharField(max_length=256, null=True)
    amount = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url_moderator(self):
        return reverse("moderator:freight", kwargs={
            'slug': self.slug
        })


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=False)
    description = models.TextField()
    discount_price = models.IntegerField()

    def __str__(self):
        return self.title

    def get_absolute_cat_url(self):
        return reverse("core:category", kwargs={
            'slug': self.slug
        })


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()

    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    description = models.TextField()
    image = models.ImageField(upload_to="media_root/")
    slug = models.SlugField(default='item', unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(
        Item, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    total_price = models.FloatField(blank=True, null=True)
    sent = models.BooleanField(default=False)
    returned_flag = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    return_handled = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    cancel_handled = models.BooleanField(default=False)
    refund_flag = models.BooleanField(default=False)
    refund = models.BooleanField(default=False)
    removed_from_order = models.BooleanField(default=False)
    refund_handled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_absolute_url_support(self):
        return reverse("support:orderItem", kwargs={
            'slug': self.id
        })


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner",
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    total_price = models.FloatField(blank=True, null=True)
    freight = models.ForeignKey('Freight',
                                on_delete=models.SET_NULL, blank=True, null=True)
    freight_price = models.FloatField(blank=True, null=True)
    ordered_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now, blank=True)
    ordered = models.BooleanField(default=False)
    who = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="packer",
                            on_delete=models.SET_NULL, blank=True, null=True)
    being_read = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    coupon_amount = models.FloatField(blank=True, null=True)
    coupon_type = models.CharField(max_length=20, blank=True, null=True)
    coupon_code = models.CharField(max_length=15, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    return_handled = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    cancel_handled = models.BooleanField(default=False)
    returned_flag = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    comment = models.CharField(max_length=500, blank=True, null=True)
    refund_handled = models.BooleanField(default=False)
    removed_order = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total_basket(self):
        total = self.total_price
        if self.freight:
            total -= self.freight_price
        return total

    def get_total(self):
        total = self.total_price
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_absolute_url_member(self):
        return reverse("member:my_order", kwargs={
            'slug': self.ref_code
        })

    def get_absolute_url_support(self):
        return reverse("support:vieworder", kwargs={
            'slug': self.ref_code
        })

    def get_absolute_url_moderator(self):
        return reverse("moderator:specific_order", kwargs={
            'slug': self.ref_code
        })

    def red_flag(self):
        date = make_aware(datetime.now())
        if date >= self.sub_out_date:
            return True
        else:
            return False

    def warning(self):
        date1 = make_aware(datetime.now() + timedelta(days=1))
        date2 = make_aware(datetime.now() + timedelta(days=3))
        if date1 <= self.sub_out_date and date2 >= self.sub_out_date:
            return True
        else:
            return False


class PaymentTypes(models.Model):
    name = models.CharField(max_length=50)
    short = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    coupon_type = models.CharField(max_length=20, default='Percent')
    amount = models.FloatField()
    slug = models.SlugField(default='coupon')

    def __str__(self):
        return self.code

    def get_absolute_url_moderator(self):
        return reverse("moderator:coupon", kwargs={
            'slug': self.slug
        })

    def get_absolute_url_moderator_new(self):
        return reverse("moderator:coupon", kwargs={
            'slug': 'new'
        })


class Refund(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, blank=True, null=True)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class SupportThread(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    last_responce = models.PositiveIntegerField(default=1)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=50)
    firstSent = models.DateTimeField(default=datetime.now, blank=True)
    done = models.BooleanField(default=False)
    doneDate = models.DateTimeField(default=datetime.now, blank=True)
    slug = models.SlugField(default='support')

    objects = models.Manager()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("member:my_errand", kwargs={
            'slug': self.slug
        })

    # for the moderator

    def moderator_get_absolute_url(self):
        return reverse("moderator:errand", kwargs={
            'slug': self.slug
        })


class SupportResponces(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref = models.ForeignKey(SupportThread, on_delete=models.CASCADE)
    message = models.TextField()
    responceSent = models.DateTimeField(default=datetime.now, blank=True)


class GenericSupport(models.Model):
    email = models.EmailField(default="test@test.se", blank=False, null=False)
    subject = models.CharField(
        max_length=200, default="subject", null=False, blank=False)
    message = models.TextField(default="Text", null=False, blank=False)
    sent_date = models.DateTimeField(default=datetime.now, blank=True)
    slug = models.SlugField(default="support")

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse("member:support", kwargs={
            'slug': self.slug
        })


class Cookies(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    functional = models.BooleanField(default=True)
    addapted_adds = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    # for the moderator

    def moderator_get_absolute_url(self):
        return reverse("moderator:user_settings", kwargs={
            'slug': self.id
        })


class LanguageChoices(models.Model):
    language = models.CharField(max_length=150)
    language_short = models.CharField(max_length=3)

    def __str__(self):
        return self.language


class TextTypeChoices(models.Model):
    textType = models.CharField(max_length=150)

    def __str__(self):
        return self.textType


class InformationMessages(models.Model):
    code = models.CharField(max_length=1024, null=True)
    view_section = models.CharField(max_length=20, null=True)
    description = models.TextField(null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(null=True)
    # additional languages can be added here

    def __str__(self):
        return self.code


class ErrorMessages(models.Model):
    code = models.CharField(max_length=1024, null=True)
    view_section = models.CharField(max_length=20, null=True)
    description = models.TextField(null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(null=True)
    # additional languages can be added here

    def __str__(self):
        return self.code


class WarningMessages(models.Model):
    code = models.CharField(max_length=1024, null=True)
    view_section = models.CharField(max_length=20, null=True)
    description = models.TextField(null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(null=True)

    def __str__(self):
        return self.code


class TextField(models.Model):
    view_section = models.CharField(max_length=20, null=True)
    short_hand = models.CharField(max_length=20, default="fixthis")
    description = models.CharField(max_length=200)
    textType = models.ForeignKey(
        TextTypeChoices, on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.TextField(null=True)

    def __str__(self):
        return self.description


class ButtonType(models.Model):
    buttonType = models.CharField(max_length=250)

    def __str__(self):
        return self.buttonType


class FormFields(models.Model):
    formFieldType = models.CharField(max_length=250)

    def __str__(self):
        return self.formFieldType


class ButtonText(models.Model):
    theButtonType = models.ForeignKey(
        ButtonType, on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    buttonText = models.TextField(null=True)

    def __str__(self):
        return self.buttonText


class FormText(models.Model):
    theformFieldType = models.ForeignKey(
        FormFields, on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    formTextLabel = models.TextField(null=True)
    formTextPlaceholder = models.TextField(null=True)

    def __str__(self):
        return self.formTextLabel


class FAQ(models.Model):
    description = models.CharField(max_length=200, null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.TextField(null=True)
    content = models.TextField(null=True)
    # additional languages can be added here

    def __str__(self):
        return str(self.id)

    def get_absolute_url_moderator(self):
        return reverse("moderator:faq", kwargs={
            'slug': self.id
        })

    def get_absolute_url_moderator_delete(self):
        return reverse("moderator:delete")

    def get_absolute_url_moderator_new(self):
        return reverse("moderator:new_faq")


class PaymentType(models.Model):
    code = models.CharField(max_length=3, blank=True, null=True)
    language = models.ForeignKey(
        LanguageChoices, on_delete=models.SET_NULL, blank=True, null=True)
    text = models.CharField(max_length=20, blank=True, null=True)
    # additional languages can be added here

    def __str__(self):
        return self.code


class TeamStaff(models.Model):
    name = models.CharField(max_length=256)
    position = models.CharField(max_length=256)
    active = models.BooleanField(null=True)
    description = models.TextField()
    image = models.ImageField(upload_to="media_root/")

    def __str__(self):
        return self.name


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)

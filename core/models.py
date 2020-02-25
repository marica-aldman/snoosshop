from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from datetime import datetime
from django_countries.fields import CountryField


CATEGORY_CHOICES = (
    ('TS', 'Tobaksfritt Snus'),
    ('KS', 'Klassikt Snus'),
    ('TB', 'Tillbehör')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

LANGUAGE_CHOICES = (
    ('SWE', 'Svenska'),
    ('ENG', 'English'),
    ('DEU', 'Deutch'),
    ('RUS', 'Russian'),
)

INTERVALL_CHOICES = (
    ('001', 'En gång i veckan'),
    ('002', 'Varannan vecka'),
    ('010', 'En gång i månaden'),
    ('020', 'Varannan månad'),
    ('100', 'Var sjätte månad'),
    ('200', 'En gång om året'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    post_town = models.CharField(max_length=100, null=True)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    slug = models.SlugField(default='address')

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("member:edit_address", kwargs={
            'slug': self.slug
        })

    # for the moderator

    def moderator_get_absolute_url(self):
        return reverse("moderator:edit_address", kwargs={
            'slug': self.id
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
        return self.user.username

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


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    discount_price = models.IntegerField()

    def get_absolute_cat_url(self):
        return reverse("core:category", kwargs={
            'slug': self.slug
        })


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    description = models.TextField()
    image = models.ImageField()
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


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    total_price = models.FloatField(blank=True, null=True)
    freight = models.FloatField(blank=True, null=True)
    sub_out_date = models.DateTimeField(default=datetime.now, blank=True)
    ordered_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now, blank=True)
    ordered = models.BooleanField(default=False)
    subscription_order = models.BooleanField(default=False)
    being_read = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    slug = models.SlugField(default='order')

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

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_absolute_url_member(self):
        return reverse("member:my_order", kwargs={
            'slug': self.slug
        })


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return self.stripe_charge_id


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


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


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=datetime.now, blank=True)
    next_order_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now, blank=True)
    next_order = models.IntegerField(default=1)
    intervall = models.CharField(choices=INTERVALL_CHOICES, max_length=3)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        Address, related_name='billing', on_delete=models.SET_NULL, blank=True, null=True)
    active = models.BooleanField(default=True)
    number_of_items = models.PositiveIntegerField()
    slug = models.SlugField(max_length=20, null=False, unique=True)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse("member:my_subscription", kwargs={
            'slug': self.slug
        })

    # for the moderator

    def moderator_get_absolute_url(self):
        return reverse("moderator:edit_subscription", kwargs={
            'slug': self.slug
        })


class SubscriptionItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, related_name='subscription', on_delete=models.CASCADE, blank=True, null=True)
    item = models.ForeignKey(
        Item, on_delete=models.SET_NULL, blank=True, null=True)
    item_title = models.CharField(
        max_length=100, default="Somethings wrong, contact support")
    quantity = models.PositiveIntegerField()
    price = models.FloatField(blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    total_price = models.FloatField(blank=True, null=True)


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


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)

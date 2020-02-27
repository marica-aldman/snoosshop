from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import *


class TestUrls(SimpleTestCase):

    def test_homepage_is_resolved(self):
        url = reverse('core:home')
        self.assertEquals(resolve(url).func.view_class, HomeView)


    def test_checkout_is_resolved(self):
        url = reverse('core:checkout')
        self.assertEquals(resolve(url).func.view_class, CheckoutView)


    def test_odersum_is_resolved(self):
        url = reverse('core:order-summary')
        self.assertEquals(resolve(url).func.view_class, OrderSummaryView)

    def test_product_is_resolved(self):
        url = reverse('core:product', args=['some-slug'])
        self.assertEquals(resolve(url).func.view_class, ItemDetailView)

    def test_addToCart_is_resolved(self):
        url = reverse('core:add-to-cart', args=['some-slug'])
        self.assertEquals(resolve(url).func, add_to_cart)

    def test_addCoupon_is_resolved(self):
        url = reverse('core:add-coupon')
        self.assertEquals(resolve(url).func.view_class, AddCouponView)

    def test_removeFromCart_is_resolved(self):
        url = reverse('core:remove-from-cart', args=['some-slug'])
        self.assertEquals(resolve(url).func, remove_from_cart)

    def test_removeSingleFromCart_is_resolved(self):
        url = reverse('core:remove-single-item-from-cart', args=['some-slug'])
        self.assertEquals(resolve(url).func, remove_single_item_from_cart)

    def test_payement_is_resolved(self):
        url = reverse('core:payment', args=['some-slug'])
        self.assertEquals(resolve(url).func.view_class, PaymentView)

    def test_refund_is_resolved(self):
        url = reverse('core:request-refund')
        self.assertEquals(resolve(url).func.view_class, RequestRefundView)

    def test_category_is_resolved(self):
        url = reverse('core:category', args=['some-slug'])
        self.assertEquals(resolve(url).func.view_class, CategoryView)

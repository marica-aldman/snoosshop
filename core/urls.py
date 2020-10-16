from django.urls import path
from .views import (
    ItemDetailView,
    CheckoutView,
    NewHomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    CategoryView,
    FAQView,
    om_oss_view,
    teamet_view,
    vision_view,
    freight_view,
)

app_name = 'core'

urlpatterns = [
    path('', NewHomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('category/<slug>', CategoryView.as_view(), name='category'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('omoss', om_oss_view.as_view(), name='om-oss'),
    path('team', teamet_view.as_view(), name='teamet'),
    path('vision', vision_view.as_view(), name='vision'),
    path('freight', freight_view.as_view(), name='freight'),
]

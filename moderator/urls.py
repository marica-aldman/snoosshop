from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Overview,
    ProfileView,
    InfoView,
    ProductsView,
    SpecificProductsView,
    CategoriesView,
    SpecificCategoryView,
    OrderHandlingView,
    SpecificOrderHandlingView,
    FreightView,
    SpecificFreightView,
    CouponsView,
    SpecificCouponView,
    FAQsView,
    SpecificFAQView,
    DeleteSpecificFAQView,
    NewSpecificFAQView,
)

from member.views import CookieSettingsView, changePassword

app_name = 'moderator'

urlpatterns = [
    path('overview/', Overview.as_view(), name='overview'),
    path('my_profile/', ProfileView.as_view(), name='my_profile'),
    path('my_info/', InfoView.as_view(), name='my_info'),
    path('settings/', CookieSettingsView.as_view(), name='settings'),
    path('products/', ProductsView.as_view(), name='products'),
    path('product/', SpecificProductsView.as_view(), name='product'),
    path('new_product/', SpecificProductsView.as_view(), name='new_product'),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('category/', SpecificCategoryView.as_view(), name='category'),
    path('new_category/', SpecificCategoryView.as_view(), name='new_category'),
    path('orderhandling/', OrderHandlingView.as_view(), name='orderhandling'),
    path('specific_order/<slug>',
         SpecificOrderHandlingView.as_view(), name='specific_order'),
    path('freights/', FreightView.as_view(), name='freights'),
    path('freight/<slug>',
         SpecificFreightView.as_view(), name='freight'),
    path('faqs/', FAQsView.as_view(), name='faqs'),
    path('faq/<slug>',
         SpecificFAQView.as_view(), name='faq'),
    path('delete/',
         DeleteSpecificFAQView.as_view(), name='delete'),
    path('new_faq/',
         NewSpecificFAQView.as_view(), name='new_faq'),
    path('coupons/', CouponsView.as_view(), name='coupons'),
    path('coupon/<slug>',
         SpecificCouponView.as_view(), name='coupon'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
# move cookies for general use to base

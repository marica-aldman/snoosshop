from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Overview,
    Orders,
    Order,
    Support,
    Errand,
    Profile,
    Settings,
    SubscriptionsView,
    SubscriptionView,
    CookieSettingsView,
)

app_name = 'member'

urlpatterns = [
    path('my_overview/', Overview.as_view(), name='my_overview'),
    path('my_orders/', Orders.as_view(), name='my_orders'),
    path('my_order/<slug>', Order.as_view(), name='my_order'),
    path('my_support/', Support.as_view(), name='my_support'),
    path('my_errand/<slug>', Errand.as_view(), name='my_errand'),
    path('my_profile/', Profile.as_view(), name='my_profile'),
    path('my_settings/', Settings.as_view(), name='my_settings'),
    path('settings/', CookieSettingsView.as_view(), name='cookie_settings'),
    path('my_subscriptions/', SubscriptionsView.as_view(), name='my_subscriptions'),
    path('my_subscription/<slug>',
         SubscriptionView.as_view(), name='my_subscription'),
]

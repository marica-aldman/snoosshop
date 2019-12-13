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
    Subscriptions,
    Subscription,
)

app_name = 'member'

urlpatterns = [
    path('overview/', Overview.as_view(), name='my_overview'),
    path('orders/', Orders.as_view(), name='my_orders'),
    path('order/<slug>', Order.as_view(), name='my_order'),
    path('support/', Support.as_view(), name='my_support'),
    path('errand/<slug>', Errand.as_view(), name='my_errand'),
    path('profile/', Profile.as_view(), name='my_profile'),
    path('settings/', Settings.as_view(), name='my_settings'),
    path('subscriptions/', Subscriptions.as_view(), name='my_subscriptions'),
    path('subscription/<slug>', Subscription.as_view(), name='my_subscription'),
]

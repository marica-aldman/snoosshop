from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Overview,
    MultipleOrdersView,
    OrderView,
    SupportView,
    Errand,
    Profile,
    Users,
    EditUser,
    NewAddress,
    EditAdress,
    EditAdresses,
    SettingsView,
    EditCompany,
    Subscriptions,
)

from member.views import CookieSettingsView

app_name = 'moderator'

urlpatterns = [
    path('overview/', Overview.as_view(), name='overview'),
    path('orders/', MultipleOrdersView.as_view(), name='orders'),
    path('vieworder/<slug>', OrderView.as_view(), name='vieworder'),
    path('support/', SupportView.as_view(), name='support'),
    path('errand/<slug>', Errand.as_view(), name='errand'),
    path('search_users/', Users.as_view(), name='search_users'),
    path('profile/', Profile.as_view(), name='profile'),
    path('edit_user/', EditUser.as_view(), name='edit_user'),
    path('edit_company/', EditCompany.as_view(), name='edit_company'),
    path('edit_address/<slug>', EditAdress.as_view(), name='edit_address'),
    path('edit_addresses/', EditAdresses.as_view(), name='edit_addresses'),
    path('new_address/', NewAddress.as_view(), name='new_address'),
    path('settings/', CookieSettingsView.as_view(), name='settings'),
    path('user_settings/', SettingsView.as_view(), name='user_settings'),
    path('subscriptions/', Subscriptions.as_view(), name='subscriptions'),

]

# move cookies for general use to base

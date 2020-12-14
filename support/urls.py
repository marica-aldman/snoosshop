from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Overview,
    MultipleOrdersView,
    OrderView,
    OrderItemView,
    SupportView,
    Errand,
    ProfileView,
    InfoView,
    Users,
    SpecificUser,
    EditUser,
    NewAddress,
    EditAdress,
    EditAdresses,
    SettingsView,
    EditCompany,
)

from member.views import CookieSettingsView, changePassword

app_name = 'support'

urlpatterns = [
    path('overview/', Overview.as_view(), name='overview'),
    path('orders/', MultipleOrdersView.as_view(), name='orders'),
    path('vieworder/<slug>', OrderView.as_view(), name='vieworder'),
    path('orderItem/<slug>', OrderItemView.as_view(), name='orderItem'),
    path('support/', SupportView.as_view(), name='support'),
    path('errand/<slug>', Errand.as_view(), name='errand'),
    path('search_users/', Users.as_view(), name='search_users'),
    path('specific_user/', SpecificUser.as_view(), name='specific_user'),
    path('my_profile/', ProfileView.as_view(), name='my_profile'),
    path('my_info/', InfoView.as_view(), name='my_info'),
    path('edit_user/', EditUser.as_view(), name='edit_user'),
    path('edit_company/', EditCompany.as_view(), name='edit_company'),
    path('edit_address/', EditAdress.as_view(), name='edit_address'),
    path('edit_addresses/', EditAdresses.as_view(), name='edit_addresses'),
    path('new_address/', NewAddress.as_view(), name='new_address'),
    path('settings/', CookieSettingsView.as_view(), name='settings'),
    path('user_settings/', SettingsView.as_view(), name='user_settings'),

]

# move cookies for general use to base

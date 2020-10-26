from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Setup,
    Overview,
    Orders,
    OrderView,
    GenericSupportFormView,
    SupportView,
    NewErrandView,
    ErrandView,
    Profile,
    InfoView,
    CompanyView,
    Editaddress,
    Newaddress,
    Settings,
    CookieSettingsView,
    changePassword,
    GDPRInformationRequest,
    GDPRErraseRequest,
)

app_name = 'member'

urlpatterns = [
    path('setup/', Setup.as_view(), name='setup'),
    path('my_overview/', Overview.as_view(), name='my_overview'),
    path('my_orders/', Orders.as_view(), name='my_orders'),
    path('my_order/<slug>', OrderView.as_view(), name='my_order'),
    path('my_support/', SupportView.as_view(), name='my_support'),
    path('support/', GenericSupportFormView.as_view(), name='support'),
    path('new_errand/', NewErrandView.as_view(), name='new_errand'),
    path('my_errand/<slug>', ErrandView.as_view(), name='my_errand'),
    path('my_profile/', Profile.as_view(), name='my_profile'),
    path('my_info/', InfoView.as_view(), name='my_info'),
    path('company_info/', CompanyView.as_view(), name='company'),
    path('edit_address/<slug>', Editaddress.as_view(), name='edit_address'),
    path('new_address/', Newaddress.as_view(), name='new_address'),
    path('my_settings/', CookieSettingsView.as_view(), name='my_settings'),
    path('cookie_settings/', CookieSettingsView.as_view(), name='cookie_settings'),
    path('changePassword',
         changePassword.as_view(), name='changePassword'),
    path('request_info',
         GDPRInformationRequest.as_view(), name='request_info'),
    path('delete',
         GDPRErraseRequest.as_view(), name='delete'),
]

# move cookies for general use to base

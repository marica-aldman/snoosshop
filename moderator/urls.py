from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Overview,
    OrderView,
    SupportView,
    Errand,
    Profile,
    EditUser,
    EditAdress,
    Settings,
    CookieSettingsView,
)

app_name = 'moderator'

urlpatterns = [
    path('mod_overview/', Overview.as_view(), name='mod_overview'),
    path('mod_vieworder/<slug>', OrderView.as_view(), name='mod_vieworder'),
    path('mod_support/', SupportView.as_view(), name='mod_support'),
    path('mod_errand/<slug>', Errand.as_view(), name='mod_errand'),
    path('mod_profile/', Profile.as_view(), name='mod_profile'),
]

# move cookies for general use to base

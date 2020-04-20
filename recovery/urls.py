from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    recovery,
)

from member.views import CookieSettingsView

app_name = 'recovery'

urlpatterns = [
    path('recovery/', recovery.as_view(), name='recovery'),
]

# move cookies for general use to base

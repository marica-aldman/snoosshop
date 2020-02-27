from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    Overview,
    MultipleOrdersView,
    OrderView,
    SupportView,
    Errand,
    ProfileView,
    InfoView,
    Users,
    EditUser,
    NewAddress,
    EditAdress,
    EditAdresses,
    SettingsView,
    EditCompany,
    Subscriptions,
    SpecificSubscription,
    ProductsView,
    SpecificProductsView,
    CategoriesView,
    SpecificCategoryView,
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
    path('my_profile/', ProfileView.as_view(), name='my_profile'),
    path('my_info/', InfoView.as_view(), name='my_info'),
    path('edit_user/', EditUser.as_view(), name='edit_user'),
    path('edit_company/', EditCompany.as_view(), name='edit_company'),
    path('edit_address/<slug>', EditAdress.as_view(), name='edit_address'),
    path('edit_addresses/', EditAdresses.as_view(), name='edit_addresses'),
    path('new_address/', NewAddress.as_view(), name='new_address'),
    path('settings/', CookieSettingsView.as_view(), name='settings'),
    path('user_settings/', SettingsView.as_view(), name='user_settings'),
    path('subscriptions/', Subscriptions.as_view(), name='subscriptions'),
    path('subscription/<slug>', SpecificSubscription.as_view(), name='subscription'),
    path('products/', ProductsView.as_view(), name='products'),
    path('product/', SpecificProductsView.as_view(), name='product'),
    path('new_product/', SpecificProductsView.as_view(), name='new_product'),
    path('categories/', CategoriesView.as_view(), name='categories'),
    path('category/', SpecificCategoryView.as_view(), name='category'),
    path('new_category/', SpecificCategoryView.as_view(), name='new_category'),

]

# move cookies for general use to base

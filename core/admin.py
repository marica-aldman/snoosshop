from django.contrib import admin

from .models import *


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'coupon',
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'post_town',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(Category)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserInfo)
admin.site.register(CompanyInfo)
admin.site.register(Cookies)
admin.site.register(PaymentType)
admin.site.register(PaymentTypes)
admin.site.register(Freight)
admin.site.register(LanguageChoices)
admin.site.register(TextTypeChoices)
admin.site.register(InformationMessages)
admin.site.register(ErrorMessages)
admin.site.register(WarningMessages)
admin.site.register(TextField)
admin.site.register(ButtonType)
admin.site.register(ButtonText)
admin.site.register(FormFields)
admin.site.register(FormText)
admin.site.register(FAQ)
admin.site.register(SupportThread)
admin.site.register(SupportResponces)
admin.site.register(GenericSupport)
admin.site.register(TeamStaff)

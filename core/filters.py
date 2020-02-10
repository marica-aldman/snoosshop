import django_filters
from .models import Item

class ItemFilter(django_filters.FilterSet):

    class Meta:
        model = Item
        fields = ('title', 'price', 'discount_price', 'category')

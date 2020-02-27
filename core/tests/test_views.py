from django.test import TestCase, Client
from django.urls import reverse
from core.models import *
import json


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')
        self.prod_url = reverse('core:product', args=['p1'])
        self.add2cart_url = reverse('core:add-to-cart', args=['p1'])
        self.cat = Category.objects.create(
        title='Cat1',
        slug='C1',
        description="cfvbhjnl",
        discount_price= '0'
        )
        Item.objects.create(
        id=0,
        title='product1',
        price='60',
        discount_price='0',
        category=self.cat,
        description="xgcfhjbkn",
        image = 'placeholder',
        slug='p1'
        )
        Item.objects.create(
        id=1,
        title='product2',
        price='65',
        discount_price='0',
        category=self.cat,
        description="xgcfhjbkn",
        image = 'placeholder',
        slug='p2'
        )


    # def test_HomeView_GET(self):
    #     response = self.client.get(self.home_url)
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'home.html')

    def test_products_GET(self):
        response = self.client.get(self.prod_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'product.html')

    def test_addToCart_GET(self):
        response= self.client.get(self.add2cart_url)
        self.assertEquals(response.status_code, 302)

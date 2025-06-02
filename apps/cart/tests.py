from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from decimal import Decimal

User = get_user_model()

# Create your tests here.

class CartModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.product2 = Product.objects.create(name='Mouse', price=Decimal('25.00'), category=self.category)

    def test_cart_creation(self):
        self.assertIsInstance(self.cart, Cart)
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.items.count(), 0)
        self.assertEqual(self.cart.total_price, Decimal('0.00'))

    def test_add_item(self):
        cart_item1 = self.cart.add_item(self.product1, 2)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(cart_item1.product, self.product1)
        self.assertEqual(cart_item1.quantity, 2)
        self.assertEqual(cart_item1.subtotal, Decimal('2400.00'))
        self.assertEqual(self.cart.total_price, Decimal('2400.00'))

        # Add the same product again
        cart_item1_again = self.cart.add_item(self.product1, 1)
        self.assertEqual(self.cart.items.count(), 1) 
        self.assertEqual(cart_item1_again.quantity, 3)
        self.assertEqual(cart_item1_again.subtotal, Decimal('3600.00'))
        self.assertEqual(self.cart.total_price, Decimal('3600.00'))

        # Add a different product
        cart_item2 = self.cart.add_item(self.product2, 5)
        self.assertEqual(self.cart.items.count(), 2)
        self.assertEqual(cart_item2.product, self.product2)
        self.assertEqual(cart_item2.quantity, 5)
        self.assertEqual(cart_item2.subtotal, Decimal('125.00'))
        self.assertEqual(self.cart.total_price, Decimal('3725.00'))

    def test_remove_item(self):
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 5)
        self.assertEqual(self.cart.items.count(), 2)

        self.cart.remove_item(self.product1)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.total_price, Decimal('125.00'))
        self.assertFalse(self.cart.items.filter(product=self.product1).exists())

        self.cart.remove_item(self.product2)
        self.assertEqual(self.cart.items.count(), 0)
        self.assertEqual(self.cart.total_price, Decimal('0.00'))
        self.assertFalse(self.cart.items.filter(product=self.product2).exists())

    def test_clear_cart(self):
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 5)
        self.assertEqual(self.cart.items.count(), 2)

        self.cart.clear()
        self.assertEqual(self.cart.items.count(), 0)
        self.assertEqual(self.cart.total_price, Decimal('0.00'))

class CartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.cart, created = Cart.objects.get_or_create(user=self.user)

    def test_cart_detail_view(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/detail.html')
        self.assertIn('cart_items', response.context)
        self.assertIn('cart_total', response.context)

    def test_cart_count_view(self):
        response = self.client.get(reverse('cart:cart_count'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        self.cart.add_item(self.product, 3)
        response = self.client.get(reverse('cart:cart_count'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)

    def test_add_to_cart_view(self):
        response = self.client.post(reverse('cart:add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart_detail'))
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 2)

    def test_update_cart_item_view(self):
        cart_item = self.cart.add_item(self.product, 2)
        response = self.client.post(reverse('cart:update_cart_item', args=[cart_item.id]), {'quantity': 5})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart_detail'))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_from_cart_view(self):
        cart_item = self.cart.add_item(self.product, 2)
        self.assertEqual(self.cart.items.count(), 1)
        response = self.client.post(reverse('cart:remove_from_cart', args=[cart_item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart_detail'))
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_view_empty_cart(self):
        response = self.client.get(reverse('cart:checkout'))
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('cart:cart_detail'))
        messages_list = list(response.wsgi_request._messages)
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), 'Your cart is empty')

class CartSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)

    def test_cart_serializer(self):
        cart_item = self.cart.add_item(self.product, 2)
        serializer = CartSerializer(instance=self.cart)
        data = serializer.data
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['product'], self.product.id)
        self.assertEqual(data['items'][0]['quantity'], 2)
        self.assertEqual(Decimal(data['items'][0]['subtotal']), Decimal('2400.00'))
        self.assertEqual(Decimal(data['total_price']), Decimal('2400.00'))

from rest_framework import status
from unittest.mock import patch
from apps.orders.models import Order
from django.urls import reverse as rest_reverse

class CartViewSetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.cart, created = Cart.objects.get_or_create(user=self.user)

    def test_list_cart(self):
        response = self.client.get(rest_reverse('cart-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Since get_queryset filters by user, we expect one cart in the list for the logged-in user
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.id)

    def test_retrieve_cart(self):
        response = self.client.get(rest_reverse('cart-detail', args=[self.cart.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

    def test_add_item_to_cart(self):
        url = rest_reverse('cart-add-item', args=[self.cart.pk])
        data = {'product_id': self.product.id, 'quantity': 3}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 3)
        self.assertEqual(Decimal(response.data['subtotal']), Decimal('3600.00'))

    def test_update_cart_item_quantity(self):
        cart_item = self.cart.add_item(self.product, 2)
        url = rest_reverse('cart-update-item', args=[self.cart.pk])
        data = {'product_id': self.product.id, 'quantity': 5}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
        self.assertEqual(Decimal(response.data['subtotal']), Decimal('6000.00'))

    def test_remove_item_from_cart(self):
        self.cart.add_item(self.product, 2)
        self.assertEqual(self.cart.items.count(), 1)
        url = rest_reverse('cart-remove-item', args=[self.cart.pk])
        data = {'product_id': self.product.id}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.cart.items.count(), 0)

    def test_clear_cart(self):
        self.cart.add_item(self.product, 2)
        self.assertEqual(self.cart.items.count(), 1)
        url = rest_reverse('cart-clear', args=[self.cart.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_from_cart(self):
        self.cart.add_item(self.product, 2)
        self.assertEqual(self.cart.items.count(), 1)
        url = rest_reverse('cart-checkout', args=[self.cart.pk])
        # Mocking send_order_notifications to prevent external calls during testing
        with patch('apps.cart.views.send_order_notifications') as mock_send_notification:
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(self.cart.items.count(), 0) # Cart should be empty after checkout
            self.assertEqual(Order.objects.count(), 1) # An order should be created
            created_order = Order.objects.first()
            self.assertEqual(created_order.user, self.user)
            self.assertEqual(created_order.total_price, Decimal('2400.00'))
            self.assertEqual(created_order.items.count(), 1) # Order should have one item
            mock_send_notification.assert_called_once_with(created_order)

    def test_checkout_empty_cart(self):
        url = rest_reverse('cart-checkout', args=[self.cart.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Your cart is empty')
        self.assertEqual(Order.objects.count(), 0) # No order should be created

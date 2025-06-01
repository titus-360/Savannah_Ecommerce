from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from decimal import Decimal
from apps.orders.serializers import OrderSerializer

from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

# Create your tests here.

class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.product2 = Product.objects.create(name='Mouse', price=Decimal('25.00'), category=self.category)
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item1 = self.cart.add_item(self.product1, 2)
        self.cart_item2 = self.cart.add_item(self.product2, 5)
        self.cart.save()  # Ensure cart is saved

    def test_order_creation_from_cart(self):
        cart_total = self.cart.total_price
        cart_items_count = self.cart.items.count()
        order = Order.create_order_from_cart(self.cart)
        self.assertIsInstance(order, Order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, cart_total)
        self.assertEqual(order.items.count(), cart_items_count)

        # Verify OrderItems were created correctly
        order_item1 = order.items.get(product=self.product1)
        self.assertEqual(order_item1.quantity, 2)
        self.assertEqual(order_item1.price, self.product1.price)

        order_item2 = order.items.get(product=self.product2)
        self.assertEqual(order_item2.quantity, 5)
        self.assertEqual(order_item2.price, self.product2.price)

        # Verify cart is cleared after order creation
        self.assertEqual(self.cart.items.count(), 0)
        self.assertEqual(self.cart.total_price, Decimal('0.00'))

    def test_order_item_subtotal(self):
        order = Order.create_order_from_cart(self.cart)
        order_item1 = order.items.get(product=self.product1)
        order_item2 = order.items.get(product=self.product2)

        self.assertEqual(order_item1.subtotal, Decimal('2400.00'))
        self.assertEqual(order_item2.subtotal, Decimal('125.00'))

    def test_order_total_price(self):
        order = Order.create_order_from_cart(self.cart)
        self.assertEqual(order.total_price, Decimal('2525.00'))

class OrderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.product2 = Product.objects.create(name='Mouse', price=Decimal('25.00'), category=self.category)
        self.cart, created = Cart.objects.get_or_create(user=self.user)
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 5)
        self.order = Order.create_order_from_cart(self.cart)

    def test_order_list_view(self):
        response = self.client.get(reverse('orders:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/list.html')
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0], self.order)

    def test_order_detail_view(self):
        response = self.client.get(reverse('orders:order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/detail.html')
        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'], self.order)

    def test_order_detail_view_other_user(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        other_client = Client()
        other_client.login(username='otheruser', password='password')
        response = other_client.get(reverse('orders:order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 404) # Should not find order belonging to another user

    # Note: Testing the checkout process with successful order creation is done in the OrderModelTests.
    # Additional tests for views related to checkout might involve testing form submissions, redirects, and error handling.

class OrderSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.product2 = Product.objects.create(name='Mouse', price=Decimal('25.00'), category=self.category)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 5)
        self.order = Order.create_order_from_cart(self.cart)

    def test_order_serializer(self):
        serializer = OrderSerializer(instance=self.order)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'user', 'order_number', 'status', 'total_price', 'shipping_address', 'phone_number', 'created_at', 'updated_at', 'items']))
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['order_number'], self.order.order_number)
        self.assertEqual(data['status'], 'pending')
        self.assertEqual(Decimal(data['total_price']), Decimal('2525.00'))
        self.assertEqual(len(data['items']), 2)

class OrderAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.category)
        self.product2 = Product.objects.create(name='Mouse', price=Decimal('25.00'), category=self.category)
        self.cart = Cart.objects.create(user=self.user)
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 5)
        self.order = Order.create_order_from_cart(self.cart)

    def test_list_orders(self):
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1) # Check results because of pagination
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_retrieve_order(self):
        url = reverse('order-detail', args=[self.order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(Decimal(response.data['total_price']), self.order.total_price)

    def test_retrieve_order_other_user(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('order-detail', args=[self.order.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

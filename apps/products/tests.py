from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product, Category
from decimal import Decimal
from django.utils.text import slugify

# Create your tests here.

class CategoryModelTests(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Electronics')
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.slug, 'electronics')
        self.assertIsNone(category.parent)

    def test_category_with_parent(self):
        parent_category = Category.objects.create(name='Electronics')
        child_category = Category.objects.create(name='Phones', parent=parent_category)
        self.assertEqual(child_category.name, 'Phones')
        self.assertEqual(child_category.slug, 'phones')
        self.assertEqual(child_category.parent, parent_category)

    def test_category_slugification(self):
        category = Category.objects.create(name='Books & Movies')
        self.assertEqual(category.slug, 'books-movies')

    # Add tests for custom methods if any on the Category model, e.g., get_average_price
    # Note: get_average_price is currently an action on the ViewSet, but if it were a model method, test it here.

    def test_get_ancestors_path(self):
        electronics = Category.objects.create(name='Electronics')
        phones = Category.objects.create(name='Phones', parent=electronics)
        smartphones = Category.objects.create(name='Smartphones', parent=phones)
        self.assertEqual(electronics.get_ancestors_path(), 'Electronics')
        self.assertEqual(phones.get_ancestors_path(), 'Electronics > Phones')
        self.assertEqual(smartphones.get_ancestors_path(), 'Electronics > Phones > Smartphones')

    def test_get_all_products(self):
        electronics = Category.objects.create(name='Electronics')
        phones = Category.objects.create(name='Phones', parent=electronics)
        laptops = Category.objects.create(name='Laptops', parent=electronics)
        product1 = Product.objects.create(name='Smartphone X', price=Decimal('999.99'), category=phones)
        product2 = Product.objects.create(name='Laptop Y', price=Decimal('1499.99'), category=laptops)
        product3 = Product.objects.create(name='Basic Phone', price=Decimal('99.99'), category=phones)

        electronics_products = electronics.get_all_products()
        self.assertEqual(electronics_products.count(), 3)
        self.assertIn(product1, electronics_products)
        self.assertIn(product2, electronics_products)
        self.assertIn(product3, electronics_products)

        phones_products = phones.get_all_products()
        self.assertEqual(phones_products.count(), 2)
        self.assertIn(product1, phones_products)
        self.assertIn(product3, phones_products)
        self.assertNotIn(product2, phones_products)

        laptops_products = laptops.get_all_products()
        self.assertEqual(laptops_products.count(), 1)
        self.assertIn(product2, laptops_products)
        self.assertNotIn(product1, laptops_products)
        self.assertNotIn(product3, laptops_products)

    def test_get_average_price(self):
        electronics = Category.objects.create(name='Electronics')
        phones = Category.objects.create(name='Phones', parent=electronics)
        laptops = Category.objects.create(name='Laptops', parent=electronics)
        product1 = Product.objects.create(name='Smartphone X', price=Decimal('1000.00'), category=phones)
        product2 = Product.objects.create(name='Laptop Y', price=Decimal('2000.00'), category=laptops)
        product3 = Product.objects.create(name='Basic Phone', price=Decimal('300.00'), category=phones)

        self.assertEqual(electronics.get_average_price(), Decimal('1100.00')) # (1000 + 2000 + 300) / 3
        self.assertEqual(phones.get_average_price(), Decimal('650.00')) # (1000 + 300) / 2
        self.assertEqual(laptops.get_average_price(), Decimal('2000.00')) # 2000 / 1
        self.assertEqual(Category.objects.create(name='Empty Category').get_average_price(), Decimal('0.00')) # Empty category

class ProductModelTests(TestCase):
    def test_product_creation(self):
        category = Category.objects.create(name='Test Category')
        product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price=Decimal('19.99'),
            stock=10,
            category=category,
            rating=Decimal('4.5'),
            review_count=20
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, Decimal('19.99'))
        self.assertEqual(product.stock, 10)
        self.assertEqual(product.category.name, 'Test Category')
        self.assertEqual(product.rating, Decimal('4.5'))
        self.assertEqual(product.review_count, 20)

    def test_product_defaults(self):
        category = Category.objects.create(name='Another Category')
        product = Product.objects.create(
            name='Default Product',
            price=Decimal('5.00'),
            category=category
        )
        self.assertEqual(product.description, '') # Assuming default is empty string
        self.assertEqual(product.stock, 0) # Assuming default is 0
        self.assertEqual(product.rating, Decimal('0.00')) # Assuming default is 0.00
        self.assertEqual(product.review_count, 0) # Assuming default is 0

class CategoryViewSetTests(TestCase):
    def setUp(self):
        # Clear existing data
        Category.objects.all().delete()
        Product.objects.all().delete()

        self.client = APIClient()
        self.parent_category = Category.objects.create(name='Electronics', slug='electronics')
        self.child_category = Category.objects.create(name='Phones', slug='phones', parent=self.parent_category)
        self.product1 = Product.objects.create(name='Laptop', price=Decimal('1200.00'), category=self.parent_category)
        self.product2 = Product.objects.create(name='Smartphone', price=Decimal('800.00'), category=self.child_category)

    def test_list_categories(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return both parent and child categories
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['name'], 'Electronics')
        self.assertEqual(response.data['results'][1]['name'], 'Phones')

    def test_retrieve_category_by_slug(self):
        response = self.client.get(f'/api/categories/{self.parent_category.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

    def test_get_category_average_price(self):
        response = self.client.get(f'/api/categories/{self.parent_category.slug}/average_price/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Average price for Electronics should include products in descendants
        self.assertEqual(response.data['average_price'], Decimal('1000.00')) # Average of 1200 and 800

    def test_get_category_products(self):
        response = self.client.get(f'/api/categories/{self.parent_category.slug}/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return products in this category and its descendants
        self.assertEqual(len(response.data), 2)
        # Check for expected products
        product_names = [product['name'] for product in response.data]
        self.assertIn('Laptop', product_names)
        self.assertIn('Smartphone', product_names)

class ProductViewSetTests(TestCase):
    def setUp(self):
        # Clear existing data to ensure a clean state for tests
        Product.objects.all().delete()
        Category.objects.all().delete()

        print(f"DEBUG: Products after cleanup: {Product.objects.count()}") # Debug print

        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=Decimal('10.00'), category=self.category)

        print(f"DEBUG: Products after creating test product: {Product.objects.count()}") # Debug print

    def test_get_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f"DEBUG: Products returned by API: {response.data}") # Debug print to see response data
        # The API response is paginated, so check the length of the 'results' list
        self.assertEqual(len(response.data['results']), 1)

    def test_get_average_price(self):
        response = self.client.get(f'/api/categories/{self.category.slug}/average_price/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert against a Decimal value, matching the expected return type
        self.assertEqual(response.data['average_price'], Decimal('10.00'))

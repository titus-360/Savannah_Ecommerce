from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.products.models import Category, Product
from django.contrib.auth.models import User
from apps.orders.models import Order, OrderItem
from decimal import Decimal

class Command(BaseCommand):
    help = 'Loads sample data into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create Categories
        self.stdout.write('Creating categories...')

        # Main categories
        all_products = Category.objects.create(name='All Products')

        # Electronics
        electronics = Category.objects.create(name='Electronics', parent=all_products)
        phones = Category.objects.create(name='Phones', parent=electronics)
        laptops = Category.objects.create(name='Laptops', parent=electronics)
        accessories = Category.objects.create(name='Accessories', parent=electronics)

        # Phone subcategories
        Category.objects.create(name='Smartphones', parent=phones)
        Category.objects.create(name='Feature Phones', parent=phones)

        # Laptop subcategories
        Category.objects.create(name='Gaming Laptops', parent=laptops)
        Category.objects.create(name='Business Laptops', parent=laptops)
        Category.objects.create(name='Student Laptops', parent=laptops)

        # Accessories subcategories
        Category.objects.create(name='Phone Cases', parent=accessories)
        Category.objects.create(name='Chargers', parent=accessories)
        Category.objects.create(name='Headphones', parent=accessories)

        # Fashion
        fashion = Category.objects.create(name='Fashion', parent=all_products)
        clothing = Category.objects.create(name='Clothing', parent=fashion)
        shoes = Category.objects.create(name='Shoes', parent=fashion)

        # Clothing subcategories
        Category.objects.create(name='Men\'s Clothing', parent=clothing)
        Category.objects.create(name='Women\'s Clothing', parent=clothing)
        Category.objects.create(name='Kids\' Clothing', parent=clothing)

        # Shoes subcategories
        Category.objects.create(name='Men\'s Shoes', parent=shoes)
        Category.objects.create(name='Women\'s Shoes', parent=shoes)
        Category.objects.create(name='Sports Shoes', parent=shoes)

        # Create Products
        self.stdout.write('Creating products...')

        # Electronics products
        smartphone = Product.objects.create(
            name='iPhone 13 Pro',
            description='Latest iPhone with pro camera system',
            price=Decimal('999.99'),
            category=phones,
            stock=50
        )

        laptop = Product.objects.create(
            name='MacBook Pro M2',
            description='Powerful laptop for professionals',
            price=Decimal('1299.99'),
            category=laptops,
            stock=30
        )

        headphones = Product.objects.create(
            name='AirPods Pro',
            description='Wireless noise-cancelling earbuds',
            price=Decimal('249.99'),
            category=accessories,
            stock=100
        )

        # Fashion products
        tshirt = Product.objects.create(
            name='Classic White T-Shirt',
            description='100% cotton t-shirt',
            price=Decimal('19.99'),
            category=clothing,
            stock=200
        )

        sneakers = Product.objects.create(
            name='Nike Air Max',
            description='Comfortable running shoes',
            price=Decimal('89.99'),
            category=shoes,
            stock=75
        )

        # Create Users
        self.stdout.write('Creating users...')

        user1 = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )

        # Create Orders
        self.stdout.write('Creating orders...')

        order1 = Order.objects.create(
            customer=user1,
            total_amount=Decimal('1049.98'),
            shipping_address='123 Main St, City, Country',
            phone_number='+1234567890'
        )

        OrderItem.objects.create(
            order=order1,
            product=smartphone,
            quantity=1,
            price=smartphone.price,
            subtotal=smartphone.price
        )

        OrderItem.objects.create(
            order=order1,
            product=headphones,
            quantity=1,
            price=headphones.price,
            subtotal=headphones.price
        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

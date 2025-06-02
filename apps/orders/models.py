from django.db import models
from django.conf import settings
from apps.products.models import Product
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from apps.cart.models import Cart

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('0.00'))
    shipping_address = models.TextField(default='')
    phone_number = models.CharField(max_length=15, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number based on timestamp
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD-{timestamp}"
        super().save(*args, **kwargs)

    @classmethod
    def create_order_from_cart(cls, cart):
        """
        Create a new order from a cart.
        """
        # Create the order
        order = cls.objects.create(
            user=cart.user,
            total_price=cart.total_price,
            shipping_address='',
            phone_number=cart.user.customer.phone if hasattr(cart.user, 'customer') and cart.user.customer.phone else ''
        )

        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                subtotal=cart_item.subtotal
            )

        # Clear the cart
        cart.clear()

        return order

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

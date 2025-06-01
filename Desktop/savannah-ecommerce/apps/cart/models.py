from django.db import models
from django.conf import settings
from apps.products.models import Product
from decimal import Decimal

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        """Returns the total number of items in the cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Returns the total price of all items in the cart"""
        return sum(item.subtotal for item in self.items.all())

    def add_item(self, product, quantity=1):
        """Add a product to the cart or update its quantity if it already exists"""
        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def remove_item(self, product):
        """Remove a product from the cart"""
        self.items.filter(product=product).delete()

    def clear(self):
        """Remove all items from the cart"""
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        """Returns the total price for this item"""
        return self.product.price * self.quantity

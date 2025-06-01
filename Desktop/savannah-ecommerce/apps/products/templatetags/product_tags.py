from django import template
from apps.products.models import Product
from decimal import Decimal

register = template.Library()

@register.filter
def get_product(product_id):
    """Get product object from product ID"""
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

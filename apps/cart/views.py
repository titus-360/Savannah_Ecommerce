from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.products.models import Product
from apps.orders.models import Order, OrderItem
import logging

logger = logging.getLogger(__name__)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the cart for the current user"""
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create a cart for the current user"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the cart"""
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item = cart.add_item(product, quantity)
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def update_item(self, request, pk=None):
        """Update the quantity of an item in the cart"""
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            cart_item = cart.items.get(product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity <= 0:
            cart.remove_item(cart_item.product)
            return Response(status=status.HTTP_204_NO_CONTENT)

        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        """Remove an item from the cart"""
        cart = self.get_object()
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart.remove_item(product)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear all items from the cart"""
        cart = self.get_object()
        cart.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """Create an order from the cart"""
        cart = self.get_object()
        
        if not cart.items.exists():
            return Response(
                {'error': 'Your cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Create order using the create_order_from_cart method
            order = Order.create_order_from_cart(cart)
            
            # Optionally send notifications (consider moving to a background task in production)
            try:
                from apps.orders.views import send_order_notifications
                send_order_notifications(order)
                logger.info(f"Successfully sent notifications for order {order.order_number}")
            except Exception as e:
                logger.error(f"Failed to send notifications for order {order.order_number}: {str(e)}")
                logger.exception("Full traceback:")
                
            # Return the created order details
            from apps.orders.serializers import OrderSerializer
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error during checkout: {str(e)}")
            logger.exception("Full traceback:")
            return Response(
                {'error': 'An error occurred during checkout.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart_items': cart.items.all(),
        'cart_total': cart.total_price
    }
    return render(request, 'cart/detail.html', context)

@login_required
def cart_count(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    count = sum(item.quantity for item in cart.items.all())
    return JsonResponse({'count': count})

@login_required
def update_cart_item(request, item_id):
    """Update the quantity of a cart item"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart:cart_detail')

@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        messages.error(request, 'Quantity must be greater than 0')
        return redirect('products:detail', pk=product_id)
    
    cart_item = cart.add_item(product, quantity)
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart:cart_detail')

@login_required
def checkout(request):
    """Handle the checkout process"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart_detail')
    
    # Create order using the create_order_from_cart method
    order = Order.create_order_from_cart(cart)
    
    # Send notifications
    try:
        from apps.orders.views import send_order_notifications
        send_order_notifications(order)
        logger.info(f"Successfully sent notifications for order {order.order_number}")
    except Exception as e:
        logger.error(f"Failed to send notifications for order {order.order_number}: {str(e)}")
        logger.exception("Full traceback:")
    
    messages.success(request, 'Order placed successfully!')
    return redirect('orders:order_detail', pk=order.pk) 
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import africastalking
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import OrderForm, OrderItemForm
from apps.products.models import Product
from decimal import Decimal
import logging
# from twilio.rest import Client # Import Twilio Client

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Africa's Talking
try:
    username = settings.AFRICAS_TALKING_USERNAME
    api_key = settings.AFRICAS_TALKING_API_KEY
    
    # Log initialization attempt
    logger.info("Attempting to initialize Africa's Talking...")
    logger.info(f"Username: {username}")
    logger.info(f"API Key length: {len(api_key) if api_key else 0} characters")
    
    # Initialize with sandbox credentials
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
    logger.info("Successfully initialized Africa's Talking")
    
    # No need to test sending here, let's rely on the actual send later
    # try:
    #     # Try to get account info to verify credentials
    #     response = sms.send("Test message", ["+254700000000"])
    #     logger.info("Successfully initialized Africa's Talking and verified credentials")
    # except Exception as test_error:
    #     logger.error(f"Failed to verify Africa's Talking credentials: {str(test_error)}")
    #     sms = None
    #     raise
        
except Exception as e:
    logger.error(f"Failed to initialize Africa's Talking: {str(e)}")
    logger.error("Please check your AT_USERNAME and AT_API_KEY in .env file")
    sms = None

# Initialize Twilio
# try:
#     twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     logger.info("Successfully initialized Twilio client")
# except Exception as e:
#     logger.error(f"Failed to initialize Twilio client: {str(e)}")
#     twilio_client = None

def send_order_notifications(order):
    """Send notifications for a new order"""
    logger.info(f"Starting to send notifications for order {order.order_number}")
    try:
        # Send email to customer
        customer_context = {
            'order': order,
            'items': order.items.all(),
            'site_url': settings.SITE_URL,
            'site_name': settings.SITE_NAME
        }
        logger.info(f"Preparing customer email for {order.user.email}")
        customer_html_message = render_to_string('orders/email/order_confirmation.html', customer_context)
        customer_plain_message = f"Thank you for your order #{order.order_number}. Total amount: ${order.total_price}"
        
        try:
            logger.info(f"Sending customer email to {order.user.email}")
            send_mail(
                subject=f'Order Confirmation - #{order.order_number}',
                message=customer_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                html_message=customer_html_message,
                fail_silently=False
            )
            logger.info(f"Successfully sent confirmation email to {order.user.email}")
        except Exception as e:
            logger.error(f"Failed to send customer email: {str(e)}")
            # Don't raise the exception for email failures as they're not critical

        # Send email to admin
        admin_context = {
            'order': order,
            'items': order.items.all(),
            'site_url': settings.SITE_URL,
            'site_name': settings.SITE_NAME
        }
        logger.info(f"Preparing admin email for {settings.ADMIN_EMAIL}")
        admin_html_message = render_to_string('orders/email/admin_order_notification.html', admin_context)
        admin_plain_message = f"New order #{order.order_number} received from {order.user.email}. Total amount: ${order.total_price}"
        
        try:
            logger.info(f"Sending admin email to {settings.ADMIN_EMAIL}")
            send_mail(
                subject=f'New Order Received - #{order.order_number}',
                message=admin_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                html_message=admin_html_message,
                fail_silently=False
            )
            logger.info(f"Successfully sent admin notification email to {settings.ADMIN_EMAIL}")
        except Exception as e:
            logger.error(f"Failed to send admin email: {str(e)}")
            # Don't raise the exception for email failures as they're not critical

        # Send SMS to customer if Africa's Talking is configured
        if sms and order.phone_number:
            try:
                # Format phone number to international format if not already
                phone = order.phone_number.strip()
                if not phone.startswith('+'):
                    # Remove any leading zeros and add country code
                    phone = phone.lstrip('0')
                    if not phone.startswith('254'):
                        phone = f'254{phone}'
                    phone = f'+{phone}'
                
                # In sandbox mode, we need to use a specific format
                if settings.AFRICAS_TALKING_USERNAME == 'sandbox':
                    # For sandbox, we can only send to specific numbers
                    # Using a test number for sandbox
                    phone = '+254700000000'
                    logger.info("Using sandbox test number for SMS")
                
                message = f"Thank you for your order #{order.order_number}. Total amount: ${order.total_price}. We'll notify you when it ships."
                logger.info(f"Sending SMS to {phone}")
                response = sms.send(message, [phone])
                logger.info(f"SMS sent successfully. Response: {response}")
            except Exception as e:
                logger.error(f"Failed to send SMS: {str(e)}")
                # Don't raise the exception for SMS failures as they're not critical
        else:
            logger.warning("SMS not sent: Africa's Talking not configured or no phone number provided")

    except Exception as e:
        logger.error(f"Failed to send notifications for order {order.order_number}: {str(e)}")
        logger.exception("Full traceback in send_order_notifications:")
        # Don't re-raise the exception here, as we handle email and SMS failures individually

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all orders
        for the currently authenticated user.
        """
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        send_order_notifications(order)

@login_required
def order_create(request):
    logger.info(f"Starting order creation process for user {request.user.username}")
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = form.save(commit=False)
                order.user = request.user
                
                # Use customer's phone number if not provided in the form
                if not order.phone_number and hasattr(request.user, 'customer') and request.user.customer.phone:
                    order.phone_number = request.user.customer.phone
                    logger.info(f"Using customer's phone number: {order.phone_number}")
                
                order.save()
                logger.info(f"Created order {order.order_number} for user {request.user.username}")

                # Process order items
                cart = request.session.get('cart', {})
                total_price = Decimal('0.00')
                logger.info(f"Processing {len(cart)} items from cart")

                for product_id, quantity in cart.items():
                    product = get_object_or_404(Product, id=product_id)
                    price = product.price
                    subtotal = price * quantity
                    total_price += subtotal

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price,
                        subtotal=subtotal
                    )
                    logger.info(f"Added item {product.name} (quantity: {quantity}) to order {order.order_number}")

                order.total_price = total_price
                order.save()
                logger.info(f"Updated order {order.order_number} total price to ${total_price}")

                # Clear cart
                request.session['cart'] = {}
                logger.info("Cart cleared after successful order")

                # Send notifications
                logger.info("About to send notifications...")
                try:
                    send_order_notifications(order)
                    logger.info(f"Successfully sent notifications for order {order.order_number}")
                except Exception as e:
                    logger.error(f"Failed to send notifications for order {order.order_number}: {str(e)}")
                    logger.exception("Full traceback:")

                messages.success(request, 'Order placed successfully!')
                logger.info(f"Order {order.order_number} completed successfully")
                return redirect('orders:order_detail', pk=order.pk)
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                logger.exception("Full traceback:")
                messages.error(request, 'There was an error processing your order. Please try again.')
        else:
            logger.warning(f"Invalid order form submission: {form.errors}")
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = OrderForm()
        logger.info("Displaying order creation form")

    return render(request, 'orders/create.html', {
        'form': form,
        'cart': request.session.get('cart', {})
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/list.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})
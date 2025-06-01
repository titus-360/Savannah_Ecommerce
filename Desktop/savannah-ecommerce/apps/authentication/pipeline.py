from django.contrib.auth import get_user_model
from apps.customers.models import Customer

def create_customer_profile(backend, user, response, *args, **kwargs):
    """
    Create a customer profile for users who sign in with Google.
    """
    if backend.name == 'google-oauth2':
        # Check if user already has a customer profile
        if not hasattr(user, 'customer'):
            # Create customer profile with Google data
            Customer.objects.create(
                user=user,
                email=user.email,
                name=f"{response.get('given_name', '')} {response.get('family_name', '')}".strip(),
                phone=response.get('phone_number', ''),
            ) 
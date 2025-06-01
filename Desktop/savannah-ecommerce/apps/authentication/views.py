from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from social_core.exceptions import AuthAlreadyAssociated, AuthForbidden, AuthTokenError, AuthStateMissing
from django.contrib.auth import get_user_model, login
from social_django.models import UserSocialAuth
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# Create your views here.
class AuthAPIView:
    @classmethod
    def as_view(cls):
        pass

@login_required
def customer_dashboard(request):
    return render(request, 'authentication/customer_dashboard.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def profile_view(request):
    """View for user profile page"""
    return render(request, 'authentication/profile.html', {
        'user': request.user
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Handle form submission
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Update user email if changed
        if email and email != request.user.email:
            request.user.email = email
            request.user.save()

        # Update customer phone number
        if hasattr(request.user, 'customer'):
            request.user.customer.phone = phone
            request.user.customer.save()
        else:
            # Create customer profile if it doesn't exist
            from apps.customers.models import Customer
            Customer.objects.create(
                user=request.user,
                email=request.user.email,
                phone=phone
            )

        messages.success(request, 'Profile updated successfully')
        return redirect('authentication:profile')

    return render(request, 'authentication/edit_profile.html', {
        'user': request.user
    })

def social_auth_error(request):
    """Handle social auth errors"""
    error = request.GET.get('error', '')
    message = request.GET.get('message', 'An error occurred during authentication.')
    email = request.GET.get('email', '')

    if error == 'AuthAlreadyAssociated':
        # Try to find the user by email
        try:
            user = User.objects.get(email=email)
            # If user exists, log them in
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        except User.DoesNotExist:
            # Try to find the user through social auth
            try:
                social_auth = UserSocialAuth.objects.get(uid=email)
                user = social_auth.user
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            except UserSocialAuth.DoesNotExist:
                message = 'This Google account is already associated with another user. Please use a different Google account or contact support if you believe this is an error.'
    elif error == 'AuthForbidden':
        message = 'Access was denied. Please try again or contact support if the problem persists.'
    elif error == 'AuthTokenError':
        message = 'There was a problem with the authentication token. Please try again.'
    elif error == 'AuthStateMissing':
        message = 'The authentication state is missing. Please try again.'

    return render(request, 'authentication/social_auth_error.html', {
        'message': message,
        'error': error,
        'email': email
    })

def register(request):
    """View for user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Savannah E-commerce.')
            return redirect('core:home')
    else:
        form = UserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})

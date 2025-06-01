from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.customers.models import Customer

User = get_user_model()

class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password', email='test@example.com')

    def test_login_view(self):
        response = self.client.get(reverse('authentication:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

        # Test successful login
        response = self.client.post(reverse('authentication:login'), {'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302) # Should redirect after successful login
        # Check if user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_view_invalid_credentials(self):
        response = self.client.post(reverse('authentication:login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200) # Should render login page again on failure
        self.assertTemplateUsed(response, 'registration/login.html')
        # Check if user is NOT logged in
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_view(self):
        self.client.login(username='testuser', password='password')
        self.assertTrue('_auth_user_id' in self.client.session) # Ensure user is logged in initially

        response = self.client.get(reverse('authentication:logout'))
        self.assertEqual(response.status_code, 302) # Should redirect after logout
        # Check if user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('authentication:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('authentication:profile'))
        # Should redirect to login page for unauthenticated users
        self.assertEqual(response.status_code, 302)

class AuthenticationPipelineTests(TestCase):
    def test_create_customer_profile_google(self):
        # Create a test user
        user = User.objects.create_user(username='socialuser', email='social@example.com')

        # Simulate backend and response from Google OAuth2
        class MockBackend:
            name = 'google-oauth2'

        mock_backend = MockBackend()
        mock_response = {
            'given_name': 'Social',
            'family_name': 'User',
            'email': 'social@example.com',
            'phone_number': '+1234567890',
        }

        # Call the pipeline function
        from apps.authentication.pipeline import create_customer_profile
        create_customer_profile(backend=mock_backend, user=user, response=mock_response)

        # Assert that a customer profile was created
        self.assertTrue(hasattr(user, 'customer'))

        # Assert customer profile details
        customer = user.customer
        self.assertEqual(customer.email, 'social@example.com')
        self.assertEqual(customer.name, 'Social User')
        self.assertEqual(customer.phone, '+1234567890')

    def test_create_customer_profile_existing_customer(self):
        # Create a test user and an existing customer profile
        user = User.objects.create_user(username='existinguser', email='existing@example.com')
        Customer.objects.create(user=user, name='Existing User', email='existing@example.com', phone='0987654321')

        # Simulate backend and response (should not create a new profile)
        class MockBackend:
            name = 'google-oauth2'

        mock_backend = MockBackend()
        mock_response = {
            'given_name': 'Existing',
            'family_name': 'User',
            'email': 'existing@example.com',
            'phone_number': '+1122334455',
        }

        # Call the pipeline function
        from apps.authentication.pipeline import create_customer_profile
        create_customer_profile(backend=mock_backend, user=user, response=mock_response)

        # Assert that only one customer profile exists for the user
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)

        # Assert that the existing customer profile was NOT overwritten (assuming pipeline doesn't update existing)
        customer = user.customer
        self.assertEqual(customer.name, 'Existing User')
        self.assertEqual(customer.phone, '0987654321') # Phone should be the original one

    def test_create_customer_profile_other_backend(self):
        # Create a test user
        user = User.objects.create_user(username='otheruser', email='other@example.com')

        # Simulate a backend that is not google-oauth2
        class MockBackend:
            name = 'facebook'

        mock_backend = MockBackend()
        mock_response = {
            'name': 'Other User',
            'email': 'other@example.com',
        }

        # Call the pipeline function
        from apps.authentication.pipeline import create_customer_profile
        create_customer_profile(backend=mock_backend, user=user, response=mock_response)

        # Assert that no customer profile was created
        self.assertFalse(hasattr(user, 'customer'))

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.reverse import reverse
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer

User = get_user_model()

class CustomerModelTests(TestCase):
    # (Keep your existing CustomerModelTests here if any)
    pass # Placeholder if the class is empty or doesn't exist yet

class CustomerAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', email='test@example.com')
        self.customer = Customer.objects.create(user=self.user, name='Test Customer', email='test@example.com', phone='1234567890')
        self.client.force_authenticate(user=self.user)
        self.customer_list_url = reverse('customer-list')

    def test_list_customers_authenticated(self):
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.customer.id)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_list_customers_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # Should require authentication to list

    def test_retrieve_customer_authenticated_own(self):
        url = reverse('customer-detail', args=[self.customer.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.customer.id)
        self.assertEqual(response.data['user'], self.user.id)

    def test_retrieve_customer_authenticated_other_user(self):
        other_user = User.objects.create_user(username='otheruser', password='password', email='other@example.com')
        other_customer = Customer.objects.create(user=other_user, name='Other Customer', email='other@example.com')
        url = reverse('customer-detail', args=[other_customer.pk])
        response = self.client.get(url)
        # Should return 404 as the queryset is filtered by the authenticated user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_customer_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('customer-detail', args=[self.customer.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_customer_not_allowed(self):
        # Creating a customer for the same user should not be allowed (OneToOne)
        data = {
            'name': 'Duplicate Customer',
            'email': 'duplicate@example.com',
            'phone': '0987654321'
        }
        response = self.client.post(self.customer_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'A customer profile already exists for this user.')

    def test_update_customer_authenticated_own(self):
        url = reverse('customer-detail', args=[self.customer.pk])
        data = {'name': 'Updated Name', 'phone': '9876543210'}
        response = self.client.patch(url, data) # Use patch for partial update
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Name')
        self.assertEqual(self.customer.phone, '9876543210')

    def test_update_customer_authenticated_other_user_forbidden(self):
        other_user = User.objects.create_user(username='otheruser', password='password', email='other2@example.com')
        other_customer = Customer.objects.create(user=other_user, name='Other Customer 2', email='other2@example.com')
        url = reverse('customer-detail', args=[other_customer.pk])
        data = {'name': 'Attempted Update'}
        response = self.client.patch(url, data)
        # Should return 404 as the user cannot access another user's profile via the filtered queryset
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_customer_not_allowed(self):
        url = reverse('customer-detail', args=[self.customer.pk])
        response = self.client.delete(url)
        # DELETE is generally not enabled by default for ModelViewSet with IsAuthenticatedOrReadOnly for regular users
        # We expect 405 Method Not Allowed or 403 Forbidden
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN])
        self.assertTrue(Customer.objects.filter(pk=self.customer.pk).exists()) # Ensure customer was not deleted

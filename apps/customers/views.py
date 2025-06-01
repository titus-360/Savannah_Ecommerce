from django.shortcuts import render
from .models import Customer
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomerSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

# Create your views here.

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customers/customer_list.html', {'customers': customers})

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put']  # Disable DELETE

    def get_queryset(self):
        """
        This view should return a list of all customers
        for the currently authenticated user.
        """
        return Customer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if Customer.objects.filter(user=self.request.user).exists():
            raise ValidationError({'detail': 'A customer profile already exists for this user.'})
        serializer.save(user=self.request.user)

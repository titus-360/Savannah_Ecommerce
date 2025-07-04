# Generated by Django 4.2.7 on 2025-06-01 10:20

from django.db import migrations
from django.contrib.auth import get_user_model

def link_customers_to_users(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    User = get_user_model()

    # Get all customers without a user
    customers = Customer.objects.filter(user__isnull=True)

    for customer in customers:
        try:
            # Try to find a user with matching email
            user = User.objects.get(email=customer.email)
            customer.user = user
            customer.save()
        except User.DoesNotExist:
            # If no user found, we'll leave the customer unlinked
            pass

def reverse_link_customers_to_users(apps, schema_editor):
    # No need to reverse this migration
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0002_customer_created_at_customer_updated_at_and_more"),
    ]

    operations = [
        migrations.RunPython(link_customers_to_users, reverse_link_customers_to_users),
    ]

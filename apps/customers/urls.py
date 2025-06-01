"""
Customers app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)

app_name = 'customers'

urlpatterns = [
    path('', include(router.urls)),
]

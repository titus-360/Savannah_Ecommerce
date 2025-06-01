"""
Orders app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

app_name = 'orders'

urlpatterns = [
    path('', include(router.urls)),
    path('list/', views.order_list, name='order_list'),
    path('create/', views.order_create, name='create'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
]

"""
Products app URLs
"""
from django.urls import path, include
from . import views


app_name = 'products'

urlpatterns = [

    # Template-based views
    path('list/', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/update/', views.product_update, name='update'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
]

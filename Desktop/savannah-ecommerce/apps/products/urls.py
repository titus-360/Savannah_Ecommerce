"""
Products app URLs
"""
from django.urls import path, include
# from rest_framework.routers import DefaultRouter # Router moved to main urls.py
from . import views

# router = DefaultRouter()
# router.register(r'products', views.ProductViewSet, basename='product')
# router.register(r'categories', views.CategoryViewSet, basename='category')

app_name = 'products'

urlpatterns = [
    # Removed router include as it's now in main urls.py
    # path('', include(router.urls)),

    # Template-based views
    path('list/', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/update/', views.product_update, name='update'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
]

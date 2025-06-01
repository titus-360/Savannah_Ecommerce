"""
URL configuration for savannah_ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from apps.products.views import ProductViewSet, CategoryViewSet
from apps.customers.views import CustomerViewSet
from apps.orders.views import OrderViewSet
from apps.cart.views import CartViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Savannah E-commerce API",
        default_version='v1',
        description="API documentation for Savannah E-commerce",
        terms_of_service="https://www.savannah.com/terms/",
        contact=openapi.Contact(email="contact@savannah.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('products/', include('apps.products.urls')),
    path('api/', include(router.urls)),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('api/schema/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    path('auth/', include('apps.authentication.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Development Guide

## Getting Started

### 1. Environment Setup

1. **Python Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=savannah_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5433
   ```

### 2. Database Setup

1. **PostgreSQL**:
   ```bash
   # Using Docker
   docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5433:5432 -d postgres:15
   ```

2. **Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

## Code Structure

### 1. Apps Organization

```
apps/
├── authentication/    # User authentication
├── customers/        # Customer management
├── products/         # Product catalog
├── orders/          # Order processing
└── cart/            # Shopping cart
```

### 2. Key Components

#### Authentication
```python
# apps/authentication/views.py
class AuthAPIView:
    @classmethod
    def as_view(cls):
        # OAuth2 implementation
        pass
```

#### Product Management
```python
# apps/products/models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

#### Order Processing
```python
# apps/orders/views.py
def send_order_notifications(order):
    # Notification system
    pass
```

## Development Workflow

### 1. Code Style

1. **PEP 8 Compliance**:
   ```bash
   # Run flake8
   flake8 .
   ```

2. **Code Formatting**:
   ```bash
   # Run black
   black .
   ```

### 2. Testing

1. **Unit Tests**:
   ```bash
   # Run tests
   pytest
   
   # With coverage
   pytest --cov=.
   ```

2. **Test Structure**:
   ```python
   # Example test
   class ProductTests(TestCase):
       def setUp(self):
           self.product = Product.objects.create(
               name="Test Product",
               price=10.00
           )
       
       def test_product_creation(self):
           self.assertEqual(self.product.name, "Test Product")
   ```

### 3. API Development

1. **Endpoint Creation**:
   ```python
   # apps/products/views.py
   class ProductViewSet(viewsets.ModelViewSet):
       queryset = Product.objects.all()
       serializer_class = ProductSerializer
   ```

2. **Serializer Definition**:
   ```python
   # apps/products/serializers.py
   class ProductSerializer(serializers.ModelSerializer):
       class Meta:
           model = Product
           fields = ['id', 'name', 'price', 'description']
   ```

### 4. Database Operations

1. **Model Creation**:
   ```python
   # Example model
   class Category(models.Model):
       name = models.CharField(max_length=100)
       parent = models.ForeignKey('self', null=True, blank=True)
   ```

2. **Migrations**:
   ```bash
   # Create migration
   python manage.py makemigrations
   
   # Apply migration
   python manage.py migrate
   ```

## Best Practices

### 1. Code Organization

1. **DRY Principle**:
   - Use mixins for common functionality
   - Create utility functions for repeated code
   - Implement base classes for shared behavior

2. **KISS Principle**:
   - Keep functions small and focused
   - Use clear, descriptive names
   - Avoid unnecessary complexity

### 2. Security

1. **Authentication**:
   ```python
   # Example permission class
   class IsOwnerOrReadOnly(permissions.BasePermission):
       def has_object_permission(self, request, view, obj):
           return obj.user == request.user
   ```

2. **Data Protection**:
   - Use environment variables
   - Implement proper validation
   - Sanitize user input

### 3. Performance

1. **Database Optimization**:
   - Use select_related() and prefetch_related()
   - Implement proper indexing
   - Optimize queries

2. **Caching**:
   ```python
   # Example cache usage
   from django.core.cache import cache
   
   def get_product(product_id):
       return cache.get_or_set(
           f'product_{product_id}',
           lambda: Product.objects.get(id=product_id),
           3600
       )
   ```

## Deployment

### 1. Docker

1. **Build Image**:
   ```bash
   docker build -t savannah-ecommerce .
   ```

2. **Run Container**:
   ```bash
   docker run -p 8000:8000 savannah-ecommerce
   ```

### 2. Kubernetes

1. **Deploy**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

2. **Monitor**:
   ```bash
   kubectl get pods
   kubectl logs <pod-name>
   ```

## Troubleshooting

### 1. Common Issues

1. **Database Connection**:
   - Check PostgreSQL service
   - Verify credentials
   - Check port availability

2. **Authentication**:
   - Verify OAuth2 configuration
   - Check token validity
   - Review permission settings

### 2. Debugging

1. **Logging**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   def some_function():
       logger.debug("Debug message")
       logger.error("Error message")
   ```

2. **Error Handling**:
   ```python
   try:
       # Operation
   except Exception as e:
       logger.error(f"Error occurred: {str(e)}")
       # Handle error
   ```

## Contributing

1. **Branch Strategy**:
   - main: production code
   - develop: development code
   - feature/*: new features
   - bugfix/*: bug fixes

2. **Pull Request Process**:
   - Create feature branch
   - Write tests
   - Update documentation
   - Submit PR

## Resources

1. **Documentation**:
   - Django Documentation
   - DRF Documentation
   - Kubernetes Documentation

2. **Tools**:
   - Postman for API testing
   - pgAdmin for database management
   - Docker Desktop for containerization 
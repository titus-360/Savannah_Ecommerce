# Development Guide

This guide covers the development workflow for the Savannah E-commerce platform.

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/savannah-ecommerce.git
cd savannah-ecommerce
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Development Environment Variables

Create a `.env` file:

```env
DEBUG=True
SECRET_KEY=your-development-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=savannah_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5433
REDIS_URL=redis://localhost:6379/0
```

### 5. Start Development Services

```bash
docker-compose up -d
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

## Project Structure

```
savannah-ecommerce/
├── apps/
│   ├── cart/           # Shopping cart functionality
│   ├── core/           # Core functionality and views
│   ├── customers/      # Customer management
│   ├── orders/         # Order processing
│   └── products/       # Product management
├── docs/              # Documentation
├── k8s/               # Kubernetes configurations
├── media/             # User-uploaded files
├── static/            # Static files
├── templates/         # HTML templates
└── tests/             # Test suite
```

## Development Workflow

### 1. Create a New Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the coding standards:
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Follow PEP 8 style guide
- Write tests for new features

### 3. Run Tests

```bash
pytest
```

### 4. Check Code Style

```bash
flake8
black .
isort .
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: your feature description"
```

### 6. Push Changes

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Use the PR template
- Include tests
- Update documentation
- Request review

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_views.py

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_views.py::TestCartView::test_add_to_cart
```

### Writing Tests

1. Create test file in `tests/` directory
2. Use pytest fixtures
3. Follow AAA pattern (Arrange, Act, Assert)
4. Mock external services
5. Use factories for test data

Example:

```python
import pytest
from django.urls import reverse

def test_add_to_cart(client, product):
    url = reverse('cart:add_to_cart', args=[product.id])
    response = client.post(url, {'quantity': 1})
    assert response.status_code == 200
    assert 'cart' in response.json()
```

## API Development

### Adding New Endpoints

1. Create serializer in `apps/your_app/serializers.py`
2. Create viewset in `apps/your_app/views.py`
3. Add URL patterns in `apps/your_app/urls.py`
4. Update API documentation

Example:

```python
# serializers.py
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# views.py
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# urls.py
router.register(r'products', ProductViewSet)
```

## Frontend Development

### Templates

- Use base template (`templates/base.html`)
- Follow BEM naming convention
- Use Bootstrap components
- Include Font Awesome icons

### Static Files

- Place CSS in `static/css/`
- Place JavaScript in `static/js/`
- Place images in `static/images/`
- Use Django's static template tag

## Database Management

### Creating Migrations

```bash
python manage.py makemigrations
```

### Applying Migrations

```bash
python manage.py migrate
```

### Database Shell

```bash
python manage.py dbshell
```

## Debugging

### Django Debug Toolbar

Enabled in development:
- SQL queries
- Templates
- Cache
- Signals
- Logging

### Logging

Configure in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## Performance Optimization

### Caching

- Use Redis for caching
- Cache expensive queries
- Use template fragment caching
- Cache API responses

### Database Optimization

- Use select_related() and prefetch_related()
- Add appropriate indexes
- Use database transactions
- Monitor slow queries

## Security Best Practices

1. Use Django's security middleware
2. Implement CSRF protection
3. Use secure password hashing
4. Validate user input
5. Use parameterized queries
6. Implement rate limiting
7. Use secure headers

## Documentation

### Code Documentation

- Use docstrings
- Follow Google style
- Document complex logic
- Include examples

### API Documentation

- Use drf-spectacular
- Document all endpoints
- Include request/response examples
- Document authentication

## Code Review Guidelines

1. Check code style
2. Verify tests
3. Review security
4. Check performance
5. Verify documentation
6. Test edge cases
7. Review error handling

## Common Issues and Solutions

### Database Connection Issues

1. Check database settings
2. Verify PostgreSQL is running
3. Check port configuration
4. Verify credentials

### Static Files Not Loading

1. Run collectstatic
2. Check STATIC_URL setting
3. Verify file permissions
4. Check template tags

### API Authentication Issues

1. Check token validity
2. Verify permissions
3. Check request headers
4. Review OAuth2 configuration

## Support

For development support:
- Email: dev@savannah.com
- GitHub Issues: https://github.com/yourusername/savannah-ecommerce/issues
- Documentation: https://docs.savannah.com 
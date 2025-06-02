# Savannah E-commerce Platform

A modern, scalable e-commerce platform built with Django and Django REST Framework, featuring a robust API, social authentication, and comprehensive product management.

## Documentation

- [Technical Architecture](docs/technical_architecture.md) - System design and components
- [Development Guide](docs/development_guide.md) - How to work with the codebase
- [API Documentation](docs/api_documentation.md) - API endpoints and usage
- [Deployment Guide](docs/deployment_guide.md) - Deployment and operations

## Features

- **User Management**
  - Social authentication (Google OAuth2)
  - User profiles and preferences
  - Role-based access control

- **Product Management**
  - Hierarchical categories (using MPTT)
  - Product variants and attributes
  - Inventory management
  - Image handling

- **Shopping Experience**
  - Shopping cart functionality
  - Wishlist management
  - Order processing
  - Payment integration

- **API Features**
  - RESTful API with DRF
  - OAuth2 authentication
  - Swagger/OpenAPI documentation
  - Comprehensive API endpoints

- **Additional Features**
  - SMS notifications (Africa's Talking)
  - Email notifications
  - Health checks
  - CORS support
  - Redis caching

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Authentication**: OAuth2, Social Auth
- **Documentation**: DRF Spectacular
- **Containerization**: Docker, Kubernetes
- **Testing**: pytest, coverage

## Prerequisites

- Python 3.12+
- PostgreSQL 15
- Redis 7
- Docker and Docker Compose
- Kubernetes (for production deployment)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/titus-360/Savannah_Ecommerce.git
   cd savannah-ecommerce
   ```

2. **Set up environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=savannah_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5433
   AT_USERNAME=sandbox
   AT_API_KEY=your-api-key
   ```

4. **Start services**
   ```bash
   docker-compose up -d
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Development

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Run flake8 for linting

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=.
```

### API Documentation

- Swagger UI: `/api/docs/`
- ReDoc: `/api/schema/redoc/`

## Deployment

### Docker

```bash
# Build image
docker build -t ghcr.io/yourusername/savannah-ecommerce:latest .

# Push to registry
docker push ghcr.io/yourusername/savannah-ecommerce:latest
```

### Kubernetes

```bash
# Create namespace
kubectl create namespace savannah

# Apply configurations
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@savannah.com or create an issue in the repository.

## Acknowledgments

- Django and Django REST Framework teams
- Africa's Talking for SMS integration
- All contributors to the project

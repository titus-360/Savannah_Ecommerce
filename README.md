# Savannah E-commerce Platform

A modern, scalable e-commerce platform built with Django and Django REST Framework, featuring a robust API, social authentication, and comprehensive product management.

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

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/savannah-ecommerce.git
   cd savannah-ecommerce
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
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

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t ghcr.io/yourusername/savannah-ecommerce:latest .
   ```

2. **Push to container registry**
   ```bash
   docker push ghcr.io/yourusername/savannah-ecommerce:latest
   ```

## Kubernetes Deployment

1. **Create namespace**
   ```bash
   kubectl create namespace savannah
   ```

2. **Apply configurations**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

## API Documentation

The API documentation is available at:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/schema/redoc/`

### Authentication

The API uses OAuth2 for authentication. To obtain a token:

```bash
curl -X POST http://localhost:8000/o/token/ \
     -d "grant_type=password" \
     -d "username=your_username" \
     -d "password=your_password" \
     -d "client_id=your_client_id" \
     -d "client_secret=your_client_secret"
```

### Main API Endpoints

- Products: `/api/products/`
- Categories: `/api/categories/`
- Orders: `/api/orders/`
- Cart: `/api/cart/`
- Customers: `/api/customers/`

## Testing

Run tests with pytest:
```bash
pytest
```

Generate coverage report:
```bash
pytest --cov=.
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

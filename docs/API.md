# Savannah E-commerce API Documentation

## Overview

The Savannah E-commerce API provides a comprehensive set of endpoints for managing products, categories, orders, customers, and shopping carts. The API follows RESTful principles and uses OAuth2 for authentication.

## Authentication

### Google OAuth2 Authentication

The API supports Google OAuth2 authentication for web applications. To authenticate:

1. Redirect users to the Google OAuth2 endpoint:
```
GET /accounts/google/login/
```

2. After successful authentication, users will be redirected to:
```
/complete/google-oauth2/
```

3. The application will create or update the user's account and provide an OAuth2 token.

### OAuth2 Token Authentication

For API access, you need to obtain an OAuth2 token. There are two ways to get a token:

#### 1. Using Google OAuth2 (Web Application)

After Google authentication, you can obtain a token using the OAuth2 endpoint:

```bash
curl -X POST http://localhost:8000/o/token/ \
     -d "grant_type=authorization_code" \
     -d "code=your_auth_code" \
     -d "client_id=your_client_id" \
     -d "client_secret=your_client_secret" \
     -d "redirect_uri=your_redirect_uri"
```

#### 2. Using Password Grant (Mobile/Desktop Applications)

```bash
curl -X POST http://localhost:8000/o/token/ \
     -d "grant_type=password" \
     -d "username=your_username" \
     -d "password=your_password" \
     -d "client_id=your_client_id" \
     -d "client_secret=your_client_secret"
```

Response:
```json
{
    "access_token": "your_access_token",
    "token_type": "Bearer",
    "expires_in": 36000,
    "refresh_token": "your_refresh_token",
    "scope": "read write"
}
```

#### Using the Access Token

Include the access token in the Authorization header:
```
Authorization: Bearer your_access_token
```

### Token Refresh

To refresh an expired token:

```bash
curl -X POST http://localhost:8000/o/token/ \
     -d "grant_type=refresh_token" \
     -d "refresh_token=your_refresh_token" \
     -d "client_id=your_client_id" \
     -d "client_secret=your_client_secret"
```

## API Endpoints

### Products

#### List Products
```http
GET /api/products/
```

Query Parameters:
- `category`: Filter by category ID
- `search`: Search in product name and description
- `min_price`: Minimum price
- `max_price`: Maximum price
- `in_stock`: Filter by stock availability (true/false)

Response:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Product Name",
            "description": "Product Description",
            "price": "99.99",
            "stock": 10,
            "category": 1,
            "images": [
                {
                    "id": 1,
                    "image": "http://localhost:8000/media/products/image.jpg"
                }
            ]
        }
    ]
}
```

#### Get Product Details
```http
GET /api/products/{id}/
```

#### Create Product
```http
POST /api/products/
```

Request Body:
```json
{
    "name": "New Product",
    "description": "Product Description",
    "price": "99.99",
    "stock": 10,
    "category": 1
}
```

### Categories

#### List Categories
```http
GET /api/categories/
```

Response:
```json
[
    {
        "id": 1,
        "name": "Electronics",
        "parent": null,
        "children": [
            {
                "id": 2,
                "name": "Smartphones",
                "parent": 1,
                "children": []
            }
        ]
    }
]
```

### Cart

#### Get Cart
```http
GET /api/cart/
```

#### Add Item to Cart
```http
POST /api/cart/add_item/
```

Request Body:
```json
{
    "product_id": 1,
    "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/cart/update_item/
```

Request Body:
```json
{
    "product_id": 1,
    "quantity": 3
}
```

#### Remove Item from Cart
```http
DELETE /api/cart/remove_item/
```

Request Body:
```json
{
    "product_id": 1
}
```

### Orders

#### List Orders
```http
GET /api/orders/
```

#### Create Order
```http
POST /api/orders/
```

Request Body:
```json
{
    "shipping_address": {
        "street": "123 Main St",
        "city": "Nairobi",
        "state": "Nairobi",
        "country": "Kenya",
        "postal_code": "00100"
    },
    "payment_method": "credit_card"
}
```

#### Get Order Details
```http
GET /api/orders/{id}/
```

### Customers

#### Get Customer Profile
```http
GET /api/customers/profile/
```

#### Update Customer Profile
```http
PUT /api/customers/profile/
```

Request Body:
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+254712345678"
}
```

## Error Handling

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
    "error": "Error message",
    "detail": "Detailed error description"
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse. The current limits are:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated users

Rate limit headers are included in the response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097600
```

## Pagination

List endpoints support pagination with the following query parameters:
- `page`: Page number
- `page_size`: Number of items per page (default: 20, max: 100)

Response includes pagination metadata:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [...]
}
```
## Versioning

The API is versioned through the URL path. The current version is v1:
```
http://localhost:8000/api/v1/products/
```

## Support

For API support or to report issues:
- Email: api-support@savannah.com
- GitHub Issues: https://github.com/yourusername/savannah-ecommerce/issues 

# API Documentation

## Overview

The Savannah E-commerce API is built using Django REST Framework and follows REST principles. All endpoints are versioned and require authentication unless specified otherwise.

## Authentication

### OAuth2 Authentication

```bash
# Get access token
curl -X POST http://localhost:8000/o/token/ \
     -d "grant_type=password" \
     -d "username=your_username" \
     -d "password=your_password" \
     -d "client_id=your_client_id" \
     -d "client_secret=your_client_secret"
```

### Social Authentication (Google)

```bash
# Google OAuth2 login
GET /auth/google/login/
```

## API Endpoints

### Products

#### List Products
```http
GET /api/products/
```

**Query Parameters:**
- `category`: Filter by category ID
- `search`: Search in name and description
- `min_price`: Minimum price
- `max_price`: Maximum price
- `ordering`: Sort by field (-field for descending)

**Response:**
```json
{
    "count": 100,
    "next": "http://api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Product Name",
            "description": "Product Description",
            "price": "99.99",
            "category": {
                "id": 1,
                "name": "Category Name"
            }
        }
    ]
}
```

#### Create Product
```http
POST /api/products/
```

**Request Body:**
```json
{
    "name": "New Product",
    "description": "Product Description",
    "price": "99.99",
    "category": 1,
    "stock": 100
}
```

### Categories

#### List Categories
```http
GET /api/categories/
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Parent Category",
        "children": [
            {
                "id": 2,
                "name": "Child Category"
            }
        ]
    }
]
```

#### Get Category Average Price
```http
GET /api/categories/{id}/average_price/
```

**Response:**
```json
{
    "average_price": "89.99"
}
```

### Orders

#### Create Order
```http
POST /api/orders/
```

**Request Body:**
```json
{
    "shipping_address": "123 Main St",
    "phone_number": "+1234567890",
    "items": [
        {
            "product": 1,
            "quantity": 2
        }
    ]
}
```

#### List Orders
```http
GET /api/orders/
```

**Response:**
```json
[
    {
        "id": 1,
        "order_number": "ORD-20240101-001",
        "total_price": "199.98",
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z",
        "items": [
            {
                "product": {
                    "id": 1,
                    "name": "Product Name"
                },
                "quantity": 2,
                "price": "99.99"
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

**Response:**
```json
{
    "id": 1,
    "items": [
        {
            "product": {
                "id": 1,
                "name": "Product Name",
                "price": "99.99"
            },
            "quantity": 2,
            "subtotal": "199.98"
        }
    ],
    "total_price": "199.98"
}
```

#### Add Item to Cart
```http
POST /api/cart/add_item/
```

**Request Body:**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

### Customers

#### Get Customer Profile
```http
GET /api/customers/me/
```

**Response:**
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
}
```

#### Update Customer Profile
```http
PATCH /api/customers/me/
```

**Request Body:**
```json
{
    "name": "John Doe",
    "phone": "+1234567890"
}
```

## Error Handling

### Error Response Format
```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### Common Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

## Rate Limiting

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number
- `page_size`: Items per page (default: 10, max: 100)

## Filtering

Most endpoints support filtering using query parameters:
- `ordering`: Sort by field (-field for descending)
- `search`: Search in relevant fields
- `min_price`/`max_price`: Price range
- `category`: Filter by category

## Examples

### Creating an Order

```python
import requests

# Get access token
token_response = requests.post('http://localhost:8000/o/token/', data={
    'grant_type': 'password',
    'username': 'user@example.com',
    'password': 'password',
    'client_id': 'client_id',
    'client_secret': 'client_secret'
})
token = token_response.json()['access_token']

# Create order
headers = {'Authorization': f'Bearer {token}'}
order_data = {
    'shipping_address': '123 Main St',
    'phone_number': '+1234567890',
    'items': [
        {'product': 1, 'quantity': 2}
    ]
}
response = requests.post('http://localhost:8000/api/orders/', 
                        json=order_data, 
                        headers=headers)
```

### Uploading a Product

```python
import requests

# Get access token
token_response = requests.post('http://localhost:8000/o/token/', data={
    'grant_type': 'password',
    'username': 'user@example.com',
    'password': 'password',
    'client_id': 'client_id',
    'client_secret': 'client_secret'
})
token = token_response.json()['access_token']

# Upload product
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'multipart/form-data'
}
product_data = {
    'name': 'New Product',
    'description': 'Product Description',
    'price': '99.99',
    'category': 1,
    'stock': 100,
    'image': open('product.jpg', 'rb')
}
response = requests.post('http://localhost:8000/api/products/', 
                        data=product_data, 
                        headers=headers)
```

## Webhooks

### Order Created
```http
POST /webhooks/order-created/
```

**Payload:**
```json
{
    "event": "order.created",
    "data": {
        "order_id": 1,
        "order_number": "ORD-20240101-001",
        "total_price": "199.98",
        "customer": {
            "id": 1,
            "email": "customer@example.com"
        }
    }
}
```

### Order Status Updated
```http
POST /webhooks/order-status-updated/
```

**Payload:**
```json
{
    "event": "order.status_updated",
    "data": {
        "order_id": 1,
        "order_number": "ORD-20240101-001",
        "old_status": "pending",
        "new_status": "processing"
    }
}
```

## SDK Examples

### Python SDK
```python
from savannah_ecommerce import SavannahClient

client = SavannahClient(
    api_key='your_api_key',
    base_url='http://localhost:8000'
)

# Create order
order = client.orders.create(
    shipping_address='123 Main St',
    phone_number='+1234567890',
    items=[{'product': 1, 'quantity': 2}]
)

# Get products
products = client.products.list(
    category=1,
    min_price=10,
    max_price=100
)
```

### JavaScript SDK
```javascript
const SavannahClient = require('savannah-ecommerce');

const client = new SavannahClient({
    apiKey: 'your_api_key',
    baseUrl: 'http://localhost:8000'
});

// Create order
client.orders.create({
    shipping_address: '123 Main St',
    phone_number: '+1234567890',
    items: [{ product: 1, quantity: 2 }]
}).then(order => {
    console.log('Order created:', order);
});

// Get products
client.products.list({
    category: 1,
    min_price: 10,
    max_price: 100
}).then(products => {
    console.log('Products:', products);
});
``` 
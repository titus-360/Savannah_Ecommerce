# UI Access Guide

This document provides information about accessing different user interfaces in the Savannah E-commerce application.

## Available UI Portals

### 1. Main E-commerce Portal
- **URL**: `http://localhost:8000/`
- **Description**: The main customer-facing e-commerce portal where users can:
  - Browse products
  - Add items to cart
  - Place orders
  - View order history
  - Manage their profile
- **Access**: Public access, requires login for personalized features

### 2. Django Administration Portal
- **URL**: `http://localhost:8000/admin/`
- **Description**: The Django admin interface for managing:
  - Products and categories
  - Orders and customers
  - User accounts
  - System settings
- **Access**: Requires admin credentials
- **Default Admin Account**:
  - Username: `admin`
  - Password: Set during initial setup

### 3. API Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
  - Interactive API documentation
  - Test API endpoints directly
  - View request/response schemas
- **ReDoc**: `http://localhost:8000/api/redoc/`
  - Alternative API documentation view
  - More readable format
  - Better for printing

### 4. REST Framework Browsable API
- **URL**: `http://localhost:8000/api/`
- **Description**: Built-in browsable API interface
- **Features**:
  - Browse API endpoints
  - Test API calls
  - View response data
- **Access**: Requires authentication for protected endpoints

## Authentication

### Customer Login
1. Visit `http://localhost:8000/auth/login/`
2. Enter your credentials
3. Or use social login (Google)

### Admin Login
1. Visit `http://localhost:8000/admin/`
2. Enter admin credentials
3. Access the admin dashboard

### API Authentication
1. Get OAuth2 token from `http://localhost:8000/o/token/`
2. Use token in API requests
3. Or use session authentication for browser-based access

## Security Notes

1. Always use HTTPS in production
2. Keep admin credentials secure
3. Regularly rotate API tokens
4. Monitor login attempts
5. Use strong passwords

## Troubleshooting

If you cannot access any of the portals:

1. Check if the server is running
2. Verify the correct port (8000)
3. Check your network connection
4. Clear browser cache
5. Try incognito mode
6. Check server logs for errors

## Support

For access issues:
- Email: support@savannah.com
- Documentation: https://docs.savannah.com
- GitHub Issues: https://github.com/yourusername/savannah-ecommerce/issues 
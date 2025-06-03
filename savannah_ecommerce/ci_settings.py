import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = 'dummy-secret-key-for-ci'

DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Include your apps that require migrations or are tested
    'apps.authentication',
    'apps.customers',
    'apps.products',
    'apps.orders',
    'apps.cart',
    'rest_framework',
    'django_coverage_plugin',
    'mptt',
    'social_django',
    'oauth2_provider',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

ROOT_URLCONF = 'savannah_ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'savannah_ecommerce.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600)
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Coverage configuration
COVERAGE_RCFILE = '.coveragerc'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}

# Minimal Social Auth settings for CI
SOCIAL_AUTH_TRAILING_SLASH = False
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'dummy_key'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'dummy_secret'
SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'apps.authentication.pipeline.create_customer_profile',
]

# Minimal OAuth2 Toolkit settings for CI
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 60 * 10,
    'ROTATE_REFRESH_TOKEN': False,
    'AUTHORIZATION_CODE_EXPIRE_SECONDS': 60,
}

# Dummy Email backend for CI
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Dummy Africa's Talking settings (if needed by code logic, though we added a check)
AFRICAS_TALKING_USERNAME = 'dummy_user'
AFRICAS_TALKING_API_KEY = 'dummy_key'

# Dummy Twilio settings (if needed by code logic)
TWILIO_ACCOUNT_SID = 'dummy_sid'
TWILIO_AUTH_TOKEN = 'dummy_token'
TWILIO_PHONE_NUMBER = 'dummy_phone'

# Dummy Site settings
SITE_NAME = 'CI Test Site'
SITE_URL = 'http://localhost/'
ADMIN_EMAIL = 'ci_admin@example.com'

# Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Savannah E-commerce API (CI)',
    'DESCRIPTION': 'API for managing customers, products, categories, and orders',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SECURITY': [{'Bearer': []}],
    'TAGS': [
        {'name': 'categories', 'description': 'Category operations'},
        {'name': 'products', 'description': 'Product operations'},
        {'name': 'customers', 'description': 'Customer operations'},
        {'name': 'orders', 'description': 'Order operations'},
    ],
}

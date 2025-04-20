import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import socket

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

def get_ngrok_url():
    """Get the ngrok URL from environment or try to detect it"""
    ngrok_url = os.getenv('NGROK_URL')
    if ngrok_url:
        return ngrok_url.replace('https://', '').replace('http://', '')
    return None

# Add ngrok URL to allowed hosts if available
NGROK_URL = get_ngrok_url()
ALLOWED_HOSTS = [
    'linkly-production.up.railway.app',
    'c175-102-217-65-14.ngrok-free.app',
    'localhost',
    '127.0.0.1',
    '.ngrok-free.app',  # Allow all ngrok subdomains
]

if NGROK_URL:
    ALLOWED_HOSTS.append(NGROK_URL)

# Security Settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development
CORS_ALLOW_CREDENTIALS = True

# If not in debug mode, specify allowed origins
if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "https://godigitalafrica-admin.web.app",
        "https://linkly-production.up.railway.app",
        "https://c175-102-217-65-14.ngrok-free.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5174",
    ]

    if NGROK_URL:
        CORS_ALLOWED_ORIGINS.append(f"https://{NGROK_URL}")

# CORS Headers Configuration
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_EXPOSE_HEADERS = ["content-type", "x-csrftoken"]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    "https://linkly-production.up.railway.app",
    "https://c175-102-217-65-14.ngrok-free.app",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5174",
]

if NGROK_URL:
    CSRF_TRUSTED_ORIGINS.append(f"https://{NGROK_URL}")

# Cookie Settings
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax' if DEBUG else 'None'
SESSION_COOKIE_SAMESITE = 'Lax' if DEBUG else 'None'

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_rest_passwordreset',
    'drf_yasg',
    # Local apps
    'users.apps.UsersConfig',
    'socials.apps.SocialsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'socials.middleware.APIUsageMiddleware',
]

ROOT_URLCONF = 'linkly.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'linkly.wsgi.application'

# Database
DATABASE_URL = "postgresql://postgres:hiTrOJnkqeRbIFiIGcynBHzvWBExIbkQ@metro.proxy.rlwy.net:30172/railway"
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATICFILES_STORAGE = 'linkly.storage.CustomWhiteNoiseStorage'


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}




# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Social Authentication Settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_CLIENT_ID', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('FACEBOOK_APP_ID', '')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email,picture'
}

SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = os.environ.get('LINKEDIN_CLIENT_ID', '')
SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_liteprofile', 'r_emailaddress']
SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ['emailAddress', 'formatted-name', 'public-profile-url', 'picture-url']

# Instagram Settings
INSTAGRAM_CLIENT_ID = os.environ.get('INSTAGRAM_CLIENT_ID', '')
INSTAGRAM_CLIENT_SECRET = os.environ.get('INSTAGRAM_CLIENT_SECRET', '')
INSTAGRAM_SCOPE = ['basic', 'public_content']

# Twitter/X Settings
TWITTER_CLIENT_ID = os.environ.get('TWITTER_API_KEY', '')  # Using API Key as Client ID
TWITTER_CLIENT_SECRET = os.environ.get('TWITTER_API_SECRET', '')  # Using API Secret as Client Secret
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN', '')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '')

# TikTok Settings
TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY', '')
TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET', '')

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_USERNAME = os.environ.get('TELEGRAM_BOT_USERNAME', '')
TELEGRAM_WEBHOOK_URL = os.environ.get('TELEGRAM_WEBHOOK_URL', '')  # For production

# =========================================
# STRIPE CONFIGURATION
# =========================================
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

# Webhook and Redirect URLs
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STRIPE_SUCCESS_URL = os.environ.get('STRIPE_SUCCESS_URL', 'https://godigitalafrica-admin.web.app/billing/success')
STRIPE_CANCEL_URL = os.environ.get('STRIPE_CANCEL_URL', 'https://godigitalafrica-admin.web.app/billing/cancel')



# OAuth2 Redirect URIs
OAUTH2_REDIRECT_URI = os.environ.get('FRONTEND_URL', 'https://godigitalafrica-admin.web.app')

# Jazzmin Settings
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Linkly Admin",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Linkly",
    # Logo to use for your site, must be present in static files
    "site_logo": None,
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Linkly Admin",
    # Copyright on the footer
    "copyright": "Linkly Ltd",
    # The model admin to search from the search bar
    "search_model": "users.User",
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": "avatar",
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Custom icons for side menu apps/models
    "icons": {
        "users.user": "fas fa-users",
        "auth.Group": "fas fa-users-cog",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    # Use a custom sidebar menu
    "custom_links": {
        "users": [{
            "name": "User Metrics", 
            "url": "admin:users_user_changelist", 
            "icon": "fas fa-chart-line"
        }]
    },
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "users.user": "collapsible",
    }
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# Swagger Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT token format: Bearer <token>'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEFAULT_MODEL_RENDERING': 'model',
    'DEFAULT_MODEL_DEPTH': 3,
    'SHOW_REQUEST_HEADERS': True,
    'DEEP_LINKING': True,
    'DISPLAY_OPERATION_ID': False,
    'PERSIST_AUTH': True,
    'VALIDATOR_URL': None,
    'APIS_SORTER': 'alpha',
    'DEFAULT_API_URL': None,
    'ENABLE_OAUTH2_BUTTON': False,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,
    'API_KEYS_ENABLED': True,
    'API_KEY_NAME': 'Authorization',
    'API_KEY_TYPE': 'header',
    'API_KEY_PREFIX': 'Bearer',
    'SHOW_EXTENSIONS': True,
    'SERVERS': [
        {
            'url': 'https://api.linkly.com/v1',
            'description': 'Production server'
        },
        {
            'url': 'https://staging-api.linkly.com/v1',
            'description': 'Staging server'
        },
        {
            'url': 'http://localhost:8000',
            'description': 'Local development server'
        }
    ],
    'SPEC_URL': 'swagger.json',
    'FILTER': True,
    'DEFAULT_INFO': {
        'description': """
# API Overview

This API provides access to Linkly's social media management platform.

## Authentication
All authenticated endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Rate Limiting
Rate limits are based on your subscription plan:
- Free Trial: 100 requests/hour
- Basic: 1,000 requests/hour
- Pro: 5,000 requests/hour
- Enterprise: Unlimited

## Common Response Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Versioning
The API version is included in the URL path:
```
https://api.linkly.com/v1/
```

## Support
For API support:
- Email: api-support@linkly.com
- Documentation: https://docs.linkly.com
- Status: https://status.linkly.com
""",
        'terms_of_service': 'https://www.linkly.com/terms/',
        'contact': {
            'name': 'API Support',
            'url': 'https://www.linkly.com/support',
            'email': 'api-support@linkly.com'
        },
        'license': {
            'name': 'MIT License',
            'url': 'https://opensource.org/licenses/MIT'
        },
        'x-logo': {
            'url': 'https://www.linkly.com/logo.png',
            'backgroundColor': '#FFFFFF',
            'altText': 'Linkly Logo'
        }
    }
}

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://default:GWrrpZmbktNIrwHMJiRRmuVJhBastQWM@shinkansen.proxy.rlwy.net:44916',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 50,
        }
    }
}

# Cache time to live is 15 minutes
CACHE_TTL = 60 * 15

# Redis as session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default' 
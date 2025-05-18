"""
Django settings for socialbu project.
"""

from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-key-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG=True

# Parse allowed hosts from environment variable
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,railway.app').split(',')

FRONTEND_URL = 'http://localhost:3000'  # Adjust based on your frontend URL

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    
    # Django AllAuth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Social providers
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.instagram',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.linkedin_oauth2',
    'allauth.socialaccount.providers.pinterest',
    # Custom providers (will be implemented)
    'social_platforms.providers.tiktok',
    'social_platforms.providers.youtube',
    'social_platforms.providers.threads',
    'social_platforms.providers.googleads',  # Renamed to avoid conflict with the local app
    
    # Local apps
    'users',
    'subscriptions',
    'content',
    'platforms',
    'posts',
    'analytics',
    'google_ads',
    'social_platforms',  # Social platforms with AllAuth integration
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'socialbu.urls'

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

WSGI_APPLICATION = 'socialbu.wsgi.application'

# Database configuration
# Use DATABASE_URL environment variable if available (Railway provides this)
# Otherwise use the hardcoded Railway PostgreSQL connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:mmejgrkDAGJFBxRmDJkszJkkbhtGUPVv@shuttle.proxy.rlwy.net:21529/railway')

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
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

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Django AllAuth Configuration
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Django backend
    'django.contrib.auth.backends.ModelBackend',
    # AllAuth backend
    'allauth.account.auth_backends.AuthenticationBackend',
]

# AllAuth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# Social Account settings
SOCIALACCOUNT_AUTO_SIGNUP = False  # We'll handle user creation in our adapter
SOCIALACCOUNT_ADAPTER = 'social_platforms.adapters.CustomSocialAccountAdapter'

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile', 'pages_show_list'],
        'FIELDS': ['id', 'email', 'name', 'picture'],
    },
    'instagram': {
        'SCOPE': ['user_profile', 'user_media'],
    },
    'twitter': {
        'SCOPE': ['tweet.read', 'users.read', 'offline.access'],
    },
    'linkedin_oauth2': {
        'SCOPE': ['r_liteprofile', 'r_emailaddress', 'w_member_social'],
        'PROFILE_FIELDS': ['id', 'first-name', 'last-name', 'email-address', 'picture-url'],
    },
    'google': {
        'SCOPE': ['profile', 'email', 'https://www.googleapis.com/auth/youtube.readonly'],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    },
    'pinterest': {
        'SCOPE': ['boards:read', 'pins:read', 'user_accounts:read'],
    },
    # Custom providers require additional configuration in their respective provider classes
    'tiktok': {
        'METHOD': 'oauth2',
        'SCOPE': ['user.info.basic', 'video.list'],
    },
    'youtube': {
        'METHOD': 'oauth2',
        'SCOPE': ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/youtube'],
    },
    'threads': {
        'METHOD': 'oauth2',
        # Uses Instagram's permissions since Threads uses the Instagram API
        'SCOPE': ['user_profile', 'user_media'],
    },
    'googleads': {
        'METHOD': 'oauth2',
        'SCOPE': ['https://www.googleapis.com/auth/adwords'],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    },
}

REDIS_URL = os.getenv('REDIS_URL', 'redis://default:GWrrpZmbktNIrwHMJiRRmuVJhBastQWM@shinkansen.proxy.rlwy.net:44916')
REDIS_HOST = os.getenv('REDIS_HOST', 'shinkansen.proxy.rlwy.net')
REDIS_PORT = int(os.getenv('REDIS_PORT', 44916))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'GWrrpZmbktNIrwHMJiRRmuVJhBastQWM')

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings - in production, we should be more specific, but for demo we can allow all
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'
CORS_ALLOWED_ORIGINS = [origin for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001,http://localhost:3002,https://linkly-frontend.up.railway.app,https://linkly-production.up.railway.app,https://linkly-gd.web.app,https://linkly-gd.firebaseapp.com').split(',') if origin]

# CSRF_TRUSTED_ORIGINS = [
#     "https://linkly-production.up.railway.app",
#     "https://linkly-gd.web.app",
#     "https://linkly-gd.firebaseapp.com"
# ]


CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
]



# If you're making API calls using cookies (session auth)
CORS_ALLOW_CREDENTIALS = True

# Additional CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Celery settings
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Social Media API Keys
# Twitter API v1.1 keys (older API)
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')

# Twitter/X OAuth 2.0 credentials (newer API)
TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID', 'WFZUOThVQmpjS1E4ZldpRTNkQm86MTpjaQ')
TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET', '')
TWITTER_REDIRECT_URI = os.getenv('TWITTER_REDIRECT_URI', 'http://localhost:8000/api/social_platforms/oauth/callback/twitter/')

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', '')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', '')

INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

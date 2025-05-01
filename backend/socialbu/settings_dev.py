"""
Django development settings for socialbu project.
Imports from the base settings and overrides certain values.
"""

from .settings import *

# Turn on debug mode
DEBUG = True

# Use simple static files storage that doesn't require collectstatic
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Add OpenAI API key - using a placeholder for development
# In production, this should be set via environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-placeholder-for-dev-environment')

# For development, enable CORS for all origins
CORS_ALLOW_ALL_ORIGINS = True 
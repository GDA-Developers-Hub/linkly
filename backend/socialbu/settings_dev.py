"""
Django development settings for socialbu project.
Imports from the base settings and overrides certain values.
"""

from .settings import *

# Turn on debug mode
DEBUG = True

# Use simple static files storage that doesn't require collectstatic
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage' 
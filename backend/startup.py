#!/usr/bin/env python
"""
Django Startup Helper Script

This script configures the Python path correctly for Django to run
regardless of what directory structure it's deployed in.
"""

import os
import sys
from pathlib import Path

# Get the current directory (the backend directory)
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socialbu.settings")

# Import and run the Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 
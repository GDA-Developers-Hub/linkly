"""
WSGI config for project.
This is a convenience file for Railway and other deployment platforms that may look for a wsgi.py in the root directory.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialbu.settings')

# Import the WSGI application directly
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 
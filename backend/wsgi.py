"""
WSGI config for project.
This is a convenience file for Railway and other deployment platforms that may look for a wsgi.py in the root directory.
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialbu.settings')

# Import the application from the actual wsgi file
from socialbu.wsgi import application  # noqa 
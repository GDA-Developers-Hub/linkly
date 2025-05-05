#!/usr/bin/env python
"""
Django Startup Helper Script

This script configures the Python path correctly for Django to run
regardless of what directory structure it's deployed in.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting Django application...")
    
    # Get the current directory (the backend directory)
    BASE_DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(BASE_DIR))
    logger.info(f"Added {BASE_DIR} to Python path")
    
    # Display the full Python path for debugging
    logger.info(f"Python path: {sys.path}")
    
    # Set the Django settings module to use our standalone settings
    os.environ["DJANGO_SETTINGS_MODULE"] = "standalone_settings"
    logger.info(f"Using settings module: {os.environ['DJANGO_SETTINGS_MODULE']}")
    
    # List available modules in the directory
    logger.info(f"Files in directory: {os.listdir(BASE_DIR)}")
    
    # Import and run the Django WSGI application
    logger.info("Initializing Django WSGI application...")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logger.info("Django WSGI application initialized successfully")
    
except Exception as e:
    logger.error(f"Error initializing Django application: {e}", exc_info=True)
    
    # Fall back to a simple WSGI app that displays the error
    def simple_error_app(environ, start_response):
        status = '500 Internal Server Error'
        output = f"Error initializing Django application: {str(e)}".encode('utf-8')
        response_headers = [('Content-type', 'text/plain'),
                           ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
    
    application = simple_error_app 
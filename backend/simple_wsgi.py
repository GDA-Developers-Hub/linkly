"""
Simple WSGI application for diagnostics.

This is a minimal WSGI application that can be used to diagnose deployment issues.
"""

import os
import sys
import json
from pathlib import Path

def simple_app(environ, start_response):
    """A simple WSGI application that returns diagnostic information."""
    # Get the current directory
    current_dir = os.getcwd()
    
    # Get Python path
    python_path = sys.path
    
    # Get environment variables
    env_vars = {key: value for key, value in os.environ.items() if not key.startswith('_')}
    
    # List directory contents
    try:
        dir_contents = os.listdir(current_dir)
    except Exception as e:
        dir_contents = f"Error listing directory: {str(e)}"
    
    # Check for Django settings module
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')
    django_settings_exists = False
    try:
        if settings_module:
            __import__(settings_module)
            django_settings_exists = True
    except ImportError as e:
        django_settings_exists = f"Error importing settings: {str(e)}"
    
    # Prepare the response data
    data = {
        'status': 'Running diagnostic WSGI app',
        'current_directory': current_dir,
        'python_path': python_path,
        'directory_contents': dir_contents,
        'environment_variables': env_vars,
        'django_settings_module': settings_module,
        'django_settings_exists': django_settings_exists,
    }
    
    # Convert the data to a JSON string and encode as bytes
    output = json.dumps(data, indent=2, default=str).encode('utf-8')
    
    # Set response headers
    status = '200 OK'
    headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(output)))
    ]
    
    # Send response headers
    start_response(status, headers)
    
    # Return response body
    return [output]

# The WSGI application
application = simple_app 
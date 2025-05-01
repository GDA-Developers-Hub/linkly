"""
Simple Flask application for diagnostics.
This is a fallback app that can help diagnose deployment issues.
"""

import os
import sys
import json
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Display diagnostic information."""
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
    
    # Check for our custom files
    try:
        app_dir_contents = os.listdir('/app')
    except Exception as e:
        app_dir_contents = f"Error listing /app directory: {str(e)}"
    
    # Prepare the response data
    data = {
        'status': 'Running diagnostic Flask app',
        'current_directory': current_dir,
        'python_path': python_path,
        'directory_contents': dir_contents,
        'app_directory_contents': app_dir_contents,
        'environment_variables': env_vars,
    }
    
    return jsonify(data)

if __name__ == '__main__':
    # Get port from environment variable or use 8000 as default
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port) 
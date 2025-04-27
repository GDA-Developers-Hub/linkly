#!/usr/bin/env python
"""
Django Settings Fix Script

This script will modify your Django settings.py file to set APPEND_SLASH = False.
This resolves issues with API requests that don't include trailing slashes.

Usage:
    python fix_django_settings.py

The script will automatically locate and modify your settings.py file.
"""

import os
import re
import sys
from pathlib import Path

def find_settings_file():
    """Find the Django settings.py file in the current directory tree"""
    for root, dirs, files in os.walk('.'):
        if 'settings.py' in files:
            return os.path.join(root, 'settings.py')
    return None

def update_settings(settings_path):
    """Update the settings.py file to set APPEND_SLASH = False"""
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Check if APPEND_SLASH is already defined
    if re.search(r'APPEND_SLASH\s*=', content):
        # Replace existing setting
        modified = re.sub(
            r'APPEND_SLASH\s*=\s*True',
            'APPEND_SLASH = False  # Modified by fix_django_settings.py',
            content
        )
        if modified == content:  # If no replacement was made, it might already be False
            print(f"APPEND_SLASH already appears to be set to False in {settings_path}")
            return False
    else:
        # Add the setting if it doesn't exist
        comment = '\n# Disable automatic trailing slash redirects for API endpoints\n'
        setting = 'APPEND_SLASH = False  # Added by fix_django_settings.py\n'
        
        # Find a good place to insert - after the last setting
        match = re.search(r'^[A-Z_]+=.+$', content, re.MULTILINE)
        if match:
            last_pos = content.rindex(match.group(0)) + len(match.group(0))
            modified = content[:last_pos] + '\n' + comment + setting + content[last_pos:]
        else:
            # If we can't find a good position, just append to the end
            modified = content + '\n' + comment + setting
    
    # Write the modified content back
    with open(settings_path, 'w') as f:
        f.write(modified)
    
    return True

def main():
    """Main function to find and update settings.py"""
    settings_path = find_settings_file()
    
    if not settings_path:
        print("Error: Could not find settings.py in the current directory tree.")
        print("Make sure you run this script from your Django project root.")
        sys.exit(1)
    
    print(f"Found Django settings file at: {settings_path}")
    
    if update_settings(settings_path):
        print("Successfully updated settings.py: APPEND_SLASH = False")
        print("Please restart your Django server for changes to take effect.")
    
    print("\nThis change will allow API endpoints to work without trailing slashes.")
    print("Your frontend code can now make requests to /api/users/login without the trailing slash.")

if __name__ == "__main__":
    main() 
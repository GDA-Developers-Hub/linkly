# Django Settings Fix
# Add this to your Django settings.py file if you prefer to disable APPEND_SLASH

"""
# APPEND_SLASH Setting
# -------------------
# When set to False, Django will not automatically append a slash to URLs that don't have one
# This can be useful when dealing with frontend frameworks that strip trailing slashes
# in API requests.

# Uncomment the line below to disable automatic slash appending:
"""

APPEND_SLASH = False

"""
# After making this change, restart your Django server for the setting to take effect.
# This will allow POST requests to endpoints like /api/users/login without requiring a trailing slash.
""" 
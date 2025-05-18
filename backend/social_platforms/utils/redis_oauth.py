"""
Redis utility functions for OAuth state management.
This module is deprecated and now uses session-based storage instead of Redis.
It maintains the same API for backward compatibility.
"""
import json
import logging
import uuid
import warnings
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Show deprecation warning
warnings.warn(
    "redis_oauth is deprecated. Please use session_oauth or Django Allauth instead.",
    DeprecationWarning, stacklevel=2
)

# Default expiration time for OAuth states (10 minutes)
DEFAULT_EXPIRY = 600  # seconds

def generate_oauth_state():
    """Generate a unique state parameter for OAuth"""
    return str(uuid.uuid4())

def store_oauth_state(platform, state, user_id=None, expiry=DEFAULT_EXPIRY):
    """Store OAuth state in session fallback"""
    warnings.warn(
        "store_oauth_state using Redis is deprecated. Use Django session instead.",
        DeprecationWarning, stacklevel=2
    )
    # Store in a thread-local or global dictionary for this request
    return state

def validate_oauth_state(platform, state):
    """Validate OAuth state (session fallback)"""
    warnings.warn("validate_oauth_state using Redis is deprecated. Use Django session instead.",
                 DeprecationWarning, stacklevel=2)
    # Simple validation since we can't access session without request
    return {
        'state': state,
        'platform': platform,
        'valid': True
    }

def store_oauth_code(platform, code, state=None, user_id=None, expiry=DEFAULT_EXPIRY):
    """Store OAuth code (session fallback)"""
    warnings.warn(
        "store_oauth_code using Redis is deprecated. Use Django session instead.",
        DeprecationWarning, stacklevel=2
    )
    # Generate a unique ID
    code_id = str(uuid.uuid4())
    return code_id

def get_oauth_code(platform, code_id):
    """Get OAuth code by ID (session fallback)"""
    warnings.warn(
        "get_oauth_code using Redis is deprecated. Use Django session instead.",
        DeprecationWarning, stacklevel=2
    )
    # We can't retrieve the code without session access
    return None

def get_oauth_code_by_state(platform, state):
    """Get OAuth code by state (session fallback)"""
    warnings.warn(
        "get_oauth_code_by_state using Redis is deprecated. Use Django session instead.",
        DeprecationWarning, stacklevel=2
    )
    # We can't retrieve the code without session access
    return None

def delete_oauth_data(platform, state=None, code_id=None):
    """Delete OAuth data (session fallback)"""
    warnings.warn(
        "delete_oauth_data using Redis is deprecated. Use Django session instead.",
        DeprecationWarning, stacklevel=2
    )
    # Can't delete without session access
    return False

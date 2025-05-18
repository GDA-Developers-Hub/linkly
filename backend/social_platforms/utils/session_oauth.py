"""
Session-based utility functions for OAuth state management.
This replaces the Redis-based implementation with a Django session-based approach.
"""
import json
import logging
import uuid
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

# Default expiration time for OAuth states (10 minutes)
DEFAULT_EXPIRY = 600  # seconds

def generate_oauth_state():
    """Generate a unique state parameter for OAuth"""
    return str(uuid.uuid4())

def store_oauth_state(request, platform, state, user_id=None, expiry=DEFAULT_EXPIRY):
    """
    Store OAuth state in the Django session
    
    Args:
        request: Django request object with session
        platform: The platform name (e.g., 'linkedin', 'youtube')
        state: The state parameter to store
        user_id: Optional user ID to associate with this state
        expiry: Time in seconds until the state expires
        
    Returns:
        The state that was stored
    """
    if not hasattr(request, 'session'):
        logger.warning("Cannot store OAuth state - no session available")
        return state
        
    # Create a state object with expiry time
    expires_at = (timezone.now() + timedelta(seconds=expiry)).timestamp()
    state_data = {
        'state': state,
        'platform': platform,
        'created_at': timezone.now().timestamp(),
        'expires_at': expires_at
    }
    
    if user_id:
        state_data['user_id'] = user_id
        
    # Store in session
    key = f'oauth_state_{platform}_{state}'
    request.session[key] = state_data
    
    # Also store in platform-specific key for lookup by platform
    request.session[f'oauth_state_{platform}'] = state
    
    logger.debug(f"Stored OAuth state in session: {key}")
    
    return state

def validate_oauth_state(request, platform, state):
    """
    Validate an OAuth state parameter from session
    
    Args:
        request: Django request object with session
        platform: The platform name
        state: The state to validate
        
    Returns:
        dict: The stored data if valid, None otherwise
    """
    if not hasattr(request, 'session'):
        logger.warning("Cannot validate OAuth state - no session available")
        return None
        
    # Get the state data from session
    key = f'oauth_state_{platform}_{state}'
    state_data = request.session.get(key)
    
    if not state_data:
        logger.warning(f"OAuth state not found in session: {key}")
        return None
        
    # Check if expired
    expires_at = state_data.get('expires_at')
    if expires_at and expires_at < timezone.now().timestamp():
        logger.warning(f"OAuth state expired: {key}")
        del request.session[key]
        return None
        
    # State is valid
    return state_data

def store_oauth_code(request, platform, code, state=None, user_id=None, expiry=DEFAULT_EXPIRY):
    """
    Store OAuth code in session for later retrieval
    
    Args:
        request: Django request object with session
        platform: The platform name
        code: The OAuth code to store
        state: Associated state parameter
        user_id: Optional user ID to associate with this code
        expiry: Time in seconds until the code expires
        
    Returns:
        str: ID for retrieving the code later
    """
    if not hasattr(request, 'session'):
        logger.warning("Cannot store OAuth code - no session available")
        return None
        
    # Generate a unique ID for this code
    code_id = str(uuid.uuid4())
    
    # Create a code object with expiry time
    expires_at = (timezone.now() + timedelta(seconds=expiry)).timestamp()
    code_data = {
        'id': code_id,
        'code': code,
        'platform': platform,
        'created_at': timezone.now().timestamp(),
        'expires_at': expires_at
    }
    
    if state:
        code_data['state'] = state
        
    if user_id:
        code_data['user_id'] = user_id
        
    # Store in session
    key = f'oauth_code_{platform}_{code_id}'
    request.session[key] = code_data
    
    # If we have a state, also store a reference for lookup by state
    if state:
        state_key = f'oauth_code_by_state_{platform}_{state}'
        request.session[state_key] = code_id
    
    logger.debug(f"Stored OAuth code in session: {key}")
    
    return code_id

def get_oauth_code(request, platform, code_id):
    """
    Retrieve OAuth code by its ID from session
    
    Args:
        request: Django request object with session
        platform: The platform name
        code_id: The ID of the stored code
        
    Returns:
        dict: The stored data if found, None otherwise
    """
    if not hasattr(request, 'session'):
        logger.warning("Cannot get OAuth code - no session available")
        return None
        
    # Get the code data from session
    key = f'oauth_code_{platform}_{code_id}'
    code_data = request.session.get(key)
    
    if not code_data:
        logger.warning(f"OAuth code not found in session: {key}")
        return None
        
    # Check if expired
    expires_at = code_data.get('expires_at')
    if expires_at and expires_at < timezone.now().timestamp():
        logger.warning(f"OAuth code expired: {key}")
        del request.session[key]
        return None
        
    # Code is valid
    return code_data

def get_oauth_code_by_state(request, platform, state):
    """
    Retrieve OAuth code by the associated state parameter from session
    
    Args:
        request: Django request object with session
        platform: The platform name
        state: The state parameter associated with the code
        
    Returns:
        dict: The stored code data if found, None otherwise
    """
    if not hasattr(request, 'session'):
        logger.warning("Cannot get OAuth code by state - no session available")
        return None
        
    # Get the code ID by state
    state_key = f'oauth_code_by_state_{platform}_{state}'
    code_id = request.session.get(state_key)
    
    if not code_id:
        logger.warning(f"OAuth code ID not found for state: {state_key}")
        return None
        
    # Get the code data by ID
    return get_oauth_code(request, platform, code_id)

def delete_oauth_data(request, platform, state=None, code_id=None):
    """
    Delete OAuth data from session
    
    Args:
        request: Django request object with session
        platform: The platform name
        state: Optional state to delete
        code_id: Optional code ID to delete
        
    Returns:
        bool: True if data was deleted, False otherwise
    """
    if not hasattr(request, 'session'):
        logger.warning("Cannot delete OAuth data - no session available")
        return False
        
    deleted = False
    
    # Delete state if provided
    if state:
        key = f'oauth_state_{platform}_{state}'
        if key in request.session:
            del request.session[key]
            deleted = True
            
        # Also delete code reference by state
        state_key = f'oauth_code_by_state_{platform}_{state}'
        if state_key in request.session:
            del request.session[state_key]
            deleted = True
    
    # Delete code if provided
    if code_id:
        key = f'oauth_code_{platform}_{code_id}'
        if key in request.session:
            del request.session[key]
            deleted = True
    
    return deleted

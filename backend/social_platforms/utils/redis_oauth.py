"""
Redis utility functions for OAuth state management.
This provides better cross-session storage than cookies or Django sessions.
"""
import json
import logging
import uuid
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import Redis, but don't fail if it's not installed yet
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis library not available. OAuth state will use session fallback.")
    REDIS_AVAILABLE = False

# Default expiration time for OAuth states (10 minutes)
DEFAULT_EXPIRY = 600  # seconds

# Redis connection - will be created on first use
_redis_client = None

def get_redis_client():
    """Get or create Redis client instance"""
    global _redis_client
    
    if not REDIS_AVAILABLE:
        return None
        
    if _redis_client is None:
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            _redis_client = redis.from_url(redis_url)
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return None
            
    return _redis_client

def generate_oauth_state():
    """Generate a unique state parameter for OAuth"""
    return str(uuid.uuid4())

def store_oauth_state(platform, state, user_id=None, expiry=DEFAULT_EXPIRY):
    """
    Store OAuth state in Redis or session
    
    Args:
        platform: The platform name (e.g., 'linkedin', 'youtube')
        state: The state parameter to store
        user_id: Optional user ID to associate with this state
        expiry: Time in seconds until the state expires
        
    Returns:
        The state that was stored
    """
    key = f"oauth:state:{platform}:{state}"
    data = {
        'platform': platform,
        'state': state,
        'user_id': user_id
    }
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.setex(key, expiry, json.dumps(data))
            logger.info(f"Stored OAuth state in Redis: {platform}:{state[:8]}...")
            return state
        except Exception as e:
            logger.error(f"Failed to store OAuth state in Redis: {e}")
    
    # Fallback to returning the state without storing if Redis is unavailable
    logger.warning(f"Redis unavailable, returning OAuth state without persistent storage: {state[:8]}...")
    return state

def validate_oauth_state(platform, state):
    """
    Validate an OAuth state parameter
    
    Args:
        platform: The platform name
        state: The state to validate
        
    Returns:
        dict: The stored data if valid, None otherwise
    """
    if not state:
        return None
        
    key = f"oauth:state:{platform}:{state}"
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
            logger.warning(f"OAuth state not found in Redis: {platform}:{state[:8]}...")
        except Exception as e:
            logger.error(f"Failed to validate OAuth state from Redis: {e}")
    
    # If we get here, state validation failed or Redis is unavailable
    return None

def store_oauth_code(platform, code, state=None, user_id=None, expiry=DEFAULT_EXPIRY):
    """
    Store OAuth code in Redis for later retrieval
    
    Args:
        platform: The platform name
        code: The OAuth code to store
        state: Associated state parameter
        user_id: Optional user ID to associate with this code
        expiry: Time in seconds until the code expires
    """
    # Create a unique key for this code
    code_id = str(uuid.uuid4())
    key = f"oauth:code:{platform}:{code_id}"
    
    data = {
        'platform': platform,
        'code': code,
        'state': state,
        'user_id': user_id,
        'code_id': code_id
    }
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.setex(key, expiry, json.dumps(data))
            
            # Also store a lookup by state if available
            if state:
                state_key = f"oauth:state_to_code:{platform}:{state}"
                redis_client.setex(state_key, expiry, code_id)
                
            logger.info(f"Stored OAuth code in Redis: {platform}:{code_id}")
            return code_id
        except Exception as e:
            logger.error(f"Failed to store OAuth code in Redis: {e}")
    
    logger.warning("Redis unavailable, OAuth code not stored persistently")
    return code_id

def get_oauth_code(platform, code_id):
    """
    Retrieve OAuth code by its ID
    
    Args:
        platform: The platform name
        code_id: The ID of the stored code
        
    Returns:
        dict: The stored data if found, None otherwise
    """
    key = f"oauth:code:{platform}:{code_id}"
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
            logger.warning(f"OAuth code not found in Redis: {platform}:{code_id}")
        except Exception as e:
            logger.error(f"Failed to retrieve OAuth code from Redis: {e}")
    
    return None

def get_oauth_code_by_state(platform, state):
    """
    Retrieve OAuth code by the associated state parameter
    
    Args:
        platform: The platform name
        state: The state parameter associated with the code
        
    Returns:
        dict: The stored code data if found, None otherwise
    """
    if not state:
        return None
        
    state_key = f"oauth:state_to_code:{platform}:{state}"
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            code_id = redis_client.get(state_key)
            if code_id:
                return get_oauth_code(platform, code_id.decode('utf-8'))
            logger.warning(f"No OAuth code found for state: {platform}:{state[:8]}...")
        except Exception as e:
            logger.error(f"Failed to retrieve OAuth code by state from Redis: {e}")
    
    return None

def delete_oauth_data(platform, state=None, code_id=None):
    """Delete OAuth data from Redis"""
    redis_client = get_redis_client()
    if not redis_client:
        return
        
    try:
        if state:
            redis_client.delete(f"oauth:state:{platform}:{state}")
            redis_client.delete(f"oauth:state_to_code:{platform}:{state}")
            
        if code_id:
            redis_client.delete(f"oauth:code:{platform}:{code_id}")
            
        logger.info(f"Deleted OAuth data for {platform}")
    except Exception as e:
        logger.error(f"Failed to delete OAuth data from Redis: {e}")

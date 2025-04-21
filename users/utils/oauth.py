import os
import secrets
import hashlib
import base64
from typing import Tuple, Dict, Optional
from urllib.parse import urlencode
import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string

def generate_pkce() -> Tuple[str, str]:
    """Generate PKCE code verifier and challenge."""
    code_verifier = secrets.token_urlsafe(96)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return code_verifier, code_challenge

def store_oauth_state(platform: str, user_id: Optional[int] = None) -> str:
    """Generate and store OAuth state parameter."""
    state = get_random_string(32)
    cache_key = f'oauth_state_{state}'
    cache_data = {'platform': platform}
    if user_id:
        cache_data['user_id'] = user_id
    cache.set(cache_key, cache_data, timeout=3600)  # 1 hour expiry
    return state

def verify_oauth_state(state: str) -> Dict:
    """Verify OAuth state parameter and return stored data."""
    cache_key = f'oauth_state_{state}'
    data = cache.get(cache_key)
    if not data:
        raise ValueError('Invalid or expired OAuth state')
    cache.delete(cache_key)
    return data

def get_platform_config(platform: str, user=None) -> Dict:
    """Get OAuth configuration for a specific platform."""
    # Check if user-specific credentials exist
    if user:
        from ..models import PlatformCredentials
        try:
            credentials = PlatformCredentials.objects.get(user=user, platform=platform)
            return {
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'redirect_uri': credentials.redirect_uri,
                'auth_url': get_default_auth_url(platform),
                'token_url': get_default_token_url(platform),
                'scopes': get_default_scopes(platform),
                'uses_pkce': platform in ['google', 'youtube', 'twitter']
            }
        except PlatformCredentials.DoesNotExist:
            # Fall back to default credentials
            pass
            
    # Default configurations
    configs = {
        'google': {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'scopes': ['openid', 'email', 'profile'],
            'uses_pkce': True
        },
        'youtube': {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
            'token_url': 'https://oauth2.googleapis.com/token',
            'scopes': ['https://www.googleapis.com/auth/youtube.readonly'],
            'uses_pkce': True
        },
        'facebook': {
            'client_id': settings.FACEBOOK_CLIENT_ID,
            'client_secret': settings.FACEBOOK_CLIENT_SECRET,
            'auth_url': 'https://www.facebook.com/v12.0/dialog/oauth',
            'token_url': 'https://graph.facebook.com/v12.0/oauth/access_token',
            'scopes': ['email', 'public_profile'],
            'uses_pkce': False
        },
        'twitter': {
            'client_id': settings.TWITTER_CLIENT_ID,
            'client_secret': settings.TWITTER_CLIENT_SECRET,
            'auth_url': 'https://twitter.com/i/oauth2/authorize',
            'token_url': 'https://api.twitter.com/2/oauth2/token',
            'scopes': ['tweet.read', 'users.read'],
            'uses_pkce': True
        },
        'linkedin': {
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET,
            'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
            'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
            'scopes': ['r_liteprofile', 'r_emailaddress'],
            'uses_pkce': False
        },
        'instagram': {
            'client_id': settings.INSTAGRAM_CLIENT_ID,
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'auth_url': 'https://api.instagram.com/oauth/authorize',
            'token_url': 'https://api.instagram.com/oauth/access_token',
            'scopes': ['basic'],
            'uses_pkce': False
        },
        'tiktok': {
            'client_id': settings.TIKTOK_CLIENT_ID,
            'client_secret': settings.TIKTOK_CLIENT_SECRET,
            'auth_url': 'https://www.tiktok.com/auth/authorize/',
            'token_url': 'https://open-api.tiktok.com/oauth/access_token/',
            'scopes': ['user.info.basic'],
            'uses_pkce': False
        },
        'telegram': {
            'client_id': settings.TELEGRAM_BOT_TOKEN.split(':')[0] if settings.TELEGRAM_BOT_TOKEN else None,
            'client_secret': settings.TELEGRAM_BOT_TOKEN.split(':')[1] if settings.TELEGRAM_BOT_TOKEN else None,
            'auth_url': 'https://oauth.telegram.org/auth',
            'token_url': None,  # Telegram uses a different auth flow
            'scopes': [],  # Telegram doesn't use OAuth scopes
            'uses_pkce': False
        }
    }
    
    if platform not in configs:
        raise ValueError(f'Unsupported platform: {platform}')
    return configs[platform]

def get_default_auth_url(platform: str) -> str:
    """Get the default authorization URL for a platform."""
    urls = {
        'google': 'https://accounts.google.com/o/oauth2/v2/auth',
        'youtube': 'https://accounts.google.com/o/oauth2/v2/auth',
        'facebook': 'https://www.facebook.com/v12.0/dialog/oauth',
        'twitter': 'https://twitter.com/i/oauth2/authorize',
        'linkedin': 'https://www.linkedin.com/oauth/v2/authorization',
        'instagram': 'https://api.instagram.com/oauth/authorize',
        'tiktok': 'https://www.tiktok.com/auth/authorize/',
        'telegram': 'https://oauth.telegram.org/auth'
    }
    return urls.get(platform)

def get_default_token_url(platform: str) -> str:
    """Get the default token URL for a platform."""
    urls = {
        'google': 'https://oauth2.googleapis.com/token',
        'youtube': 'https://oauth2.googleapis.com/token',
        'facebook': 'https://graph.facebook.com/v12.0/oauth/access_token',
        'twitter': 'https://api.twitter.com/2/oauth2/token',
        'linkedin': 'https://www.linkedin.com/oauth/v2/accessToken',
        'instagram': 'https://api.instagram.com/oauth/access_token',
        'tiktok': 'https://open-api.tiktok.com/oauth/access_token/',
        'telegram': None  # Telegram uses a different auth flow
    }
    return urls.get(platform)

def get_default_scopes(platform: str) -> list:
    """Get the default scopes for a platform."""
    scopes = {
        'google': ['openid', 'email', 'profile'],
        'youtube': ['https://www.googleapis.com/auth/youtube.readonly'],
        'facebook': ['email', 'public_profile'],
        'twitter': ['tweet.read', 'users.read'],
        'linkedin': ['r_liteprofile', 'r_emailaddress'],
        'instagram': ['basic'],
        'tiktok': ['user.info.basic'],
        'telegram': []
    }
    return scopes.get(platform, [])

def build_authorization_url(platform: str, redirect_uri: str, state: str, client_id: str = None, user=None) -> Tuple[str, Optional[str]]:
    """Build OAuth authorization URL for a specific platform."""
    config = get_platform_config(platform, user)
    
    params = {
        'client_id': client_id or config['client_id'],
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(config['scopes']),
        'state': state
    }
    
    code_verifier = None
    if config['uses_pkce']:
        code_verifier, code_challenge = generate_pkce()
        params['code_challenge'] = code_challenge
        params['code_challenge_method'] = 'S256'
        
        # Store code verifier in cache
        cache_key = f'pkce_{state}'
        cache.set(cache_key, code_verifier, timeout=3600)  # 1 hour expiry
    
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    return auth_url, code_verifier

def get_stored_code_verifier(state: str) -> Optional[str]:
    """Retrieve stored PKCE code verifier."""
    cache_key = f'pkce_{state}'
    code_verifier = cache.get(cache_key)
    if code_verifier:
        cache.delete(cache_key)
    return code_verifier

def get_stored_pkce_verifier(state: str) -> Optional[str]:
    """
    Retrieve stored PKCE code verifier for the given state.
    This is an alias for get_stored_code_verifier for consistency in naming.
    """
    return get_stored_code_verifier(state)

def validate_pkce_code_verifier(code_verifier: str, code_challenge: str) -> bool:
    """
    Validate that the code_verifier matches the previously generated code_challenge.
    
    Args:
        code_verifier: The original code verifier string
        code_challenge: The code challenge that was sent to the authorization server
        
    Returns:
        bool: True if the verification passes, False otherwise
    """
    if not code_verifier or not code_challenge:
        return False
        
    # Generate the challenge from the verifier
    generated_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()
    
    # Compare the generated challenge with the provided challenge
    return generated_challenge == code_challenge

def store_pkce_code_verifier(state: str, code_verifier: str, timeout: int = 3600) -> None:
    """
    Store PKCE code verifier in cache with the given state as key.
    
    Args:
        state: The OAuth state parameter
        code_verifier: The PKCE code verifier to store
        timeout: Cache timeout in seconds (default 1 hour)
    """
    cache_key = f'pkce_{state}'
    cache.set(cache_key, code_verifier, timeout=timeout)
    
def log_oauth_parameters(request, platform: str) -> Dict:
    """
    Log OAuth callback parameters for debugging purposes.
    
    Args:
        request: The Django request object
        platform: The platform name
        
    Returns:
        Dict: Dictionary with the logged parameters
    """
    logger = logging.getLogger('social')
    
    # Get common OAuth parameters
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    error = request.query_params.get('error')
    error_description = request.query_params.get('error_description')
    
    # Log parameters
    params = {
        'platform': platform,
        'code_exists': bool(code),
        'state': state[:10] + '...' if state and len(state) > 10 else state,
        'error': error,
        'error_description': error_description
    }
    
    logger.info(f"OAuth callback for {platform}: {params}")
    
    # Check for errors
    if error or error_description:
        logger.error(f"OAuth error for {platform}: {error} - {error_description}")
    
    return params 
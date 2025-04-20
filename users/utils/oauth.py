import os
import secrets
import hashlib
import base64
from typing import Tuple, Dict, Optional
from urllib.parse import urlencode

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

def get_platform_config(platform: str) -> Dict:
    """Get OAuth configuration for a specific platform."""
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

def build_authorization_url(platform: str, redirect_uri: str, state: str) -> Tuple[str, Optional[str]]:
    """Build OAuth authorization URL for a specific platform."""
    config = get_platform_config(platform)
    
    params = {
        'client_id': config['client_id'],
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
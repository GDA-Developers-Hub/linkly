from django.conf import settings
import urllib.parse
import requests
from typing import Dict
import logging
import base64
import hashlib
import secrets
from ..utils.oauth import (
    store_oauth_state,
    build_authorization_url,
    get_platform_config
)

logger = logging.getLogger('oauth')

def generate_code_verifier():
    """Generate a code verifier for PKCE"""
    return secrets.token_urlsafe(32)

def generate_code_challenge(verifier):
    """Generate a code challenge for PKCE"""
    sha256 = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(sha256).decode('utf-8').rstrip('=')

def generate_state():
    """Generate a secure state parameter"""
    return secrets.token_urlsafe(16)

def get_google_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get Google OAuth URL."""
    platform = 'google'
    state = store_oauth_state(platform)
    auth_url, code_verifier = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def get_facebook_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get Facebook OAuth URL."""
    platform = 'facebook'
    state = store_oauth_state(platform)
    auth_url, _ = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def get_linkedin_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get LinkedIn OAuth URL."""
    platform = 'linkedin'
    state = store_oauth_state(platform)
    auth_url, _ = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def get_twitter_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get Twitter OAuth URL."""
    platform = 'twitter'
    state = store_oauth_state(platform)
    auth_url, code_verifier = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def get_instagram_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get Instagram OAuth URL."""
    platform = 'instagram'
    state = store_oauth_state(platform)
    auth_url, _ = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def get_tiktok_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get TikTok OAuth URL."""
    platform = 'tiktok'
    state = store_oauth_state(platform)
    auth_url, code_verifier = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def get_telegram_oauth_url(business: bool = False, redirect_uri: str = None) -> Dict:
    """Get Telegram OAuth URL."""
    platform = 'telegram'
    state = store_oauth_state(platform)
    auth_url, _ = build_authorization_url(platform, redirect_uri, state)
    return {
        'auth_url': auth_url,
        'session_key': state
    }

def refresh_google_token(refresh_token: str) -> Dict[str, str]:
    """Refresh Google OAuth token."""
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        response.raise_for_status()
        data = response.json()
        return {
            'access_token': data['access_token'],
            'refresh_token': refresh_token,  # Keep existing refresh token
            'expires_in': data.get('expires_in', 3600)
        }
    except Exception as e:
        logger.error(f"Google token refresh failed: {str(e)}")
        raise TokenRefreshError(f"Google token refresh failed: {str(e)}")

def refresh_facebook_token(refresh_token: str) -> Dict[str, str]:
    """Refresh Facebook OAuth token."""
    try:
        # Facebook uses long-lived tokens instead of refresh tokens
        response = requests.get(
            'https://graph.facebook.com/oauth/access_token',
            params={
                'client_id': settings.FACEBOOK_CLIENT_ID,
                'client_secret': settings.FACEBOOK_CLIENT_SECRET,
                'grant_type': 'fb_exchange_token',
                'fb_exchange_token': refresh_token
            }
        )
        response.raise_for_status()
        data = response.json()
        return {
            'access_token': data['access_token'],
            'refresh_token': data['access_token'],  # Facebook uses same token
            'expires_in': data.get('expires_in', 5184000)  # 60 days default
        }
    except Exception as e:
        logger.error(f"Facebook token refresh failed: {str(e)}")
        raise TokenRefreshError(f"Facebook token refresh failed: {str(e)}")

def refresh_linkedin_token(refresh_token: str) -> Dict[str, str]:
    """Refresh LinkedIn OAuth token."""
    try:
        response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': settings.LINKEDIN_CLIENT_ID,
                'client_secret': settings.LINKEDIN_CLIENT_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()
        return {
            'access_token': data['access_token'],
            'refresh_token': data.get('refresh_token', refresh_token),
            'expires_in': data.get('expires_in', 3600)
        }
    except Exception as e:
        logger.error(f"LinkedIn token refresh failed: {str(e)}")
        raise TokenRefreshError(f"LinkedIn token refresh failed: {str(e)}")

def refresh_twitter_token(refresh_token: str) -> Dict[str, str]:
    """Refresh Twitter OAuth2 token."""
    try:
        response = requests.post(
            'https://api.twitter.com/2/oauth2/token',
            data={
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'client_id': settings.TWITTER_CLIENT_ID,
                'client_secret': settings.TWITTER_CLIENT_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()
        return {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expires_in': data.get('expires_in', 7200)
        }
    except Exception as e:
        logger.error(f"Twitter token refresh failed: {str(e)}")
        raise TokenRefreshError(f"Twitter token refresh failed: {str(e)}")

def refresh_instagram_token(refresh_token: str) -> Dict[str, str]:
    """Refresh Instagram OAuth token."""
    try:
        # Instagram uses long-lived tokens similar to Facebook
        response = requests.get(
            'https://graph.instagram.com/refresh_access_token',
            params={
                'grant_type': 'ig_refresh_token',
                'access_token': refresh_token
            }
        )
        response.raise_for_status()
        data = response.json()
        return {
            'access_token': data['access_token'],
            'refresh_token': data['access_token'],  # Instagram uses same token
            'expires_in': data.get('expires_in', 5184000)  # 60 days default
        }
    except Exception as e:
        logger.error(f"Instagram token refresh failed: {str(e)}")
        raise TokenRefreshError(f"Instagram token refresh failed: {str(e)}")

def refresh_tiktok_token(refresh_token: str) -> Dict[str, str]:
    """Refresh TikTok OAuth token."""
    try:
        response = requests.post(
            'https://open-api.tiktok.com/oauth/refresh_token/',
            params={
                'client_key': settings.TIKTOK_CLIENT_ID,
                'client_secret': settings.TIKTOK_CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )
        response.raise_for_status()
        data = response.json()['data']
        return {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expires_in': data.get('expires_in', 86400)  # 24 hours default
        }
    except Exception as e:
        logger.error(f"TikTok token refresh failed: {str(e)}")
        raise TokenRefreshError(f"TikTok token refresh failed: {str(e)}")

# Import at the top of the file
from .token_manager import TokenError, TokenRefreshError 
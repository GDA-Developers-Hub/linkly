from django.conf import settings
import urllib.parse
import requests
from typing import Dict
import logging
import base64
import hashlib
import secrets

logger = logging.getLogger('oauth')

def get_google_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for Google"""
    scope = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
    if business:
        scope += ' https://www.googleapis.com/auth/youtube.readonly'
    
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri or settings.GOOGLE_REDIRECT_URI,
        'scope': scope,
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f'https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}'

def get_facebook_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for Facebook"""
    scope = 'email,public_profile'
    if business:
        scope += ',pages_show_list,pages_read_engagement,instagram_basic'
    
    params = {
        'client_id': settings.FACEBOOK_CLIENT_ID,
        'redirect_uri': redirect_uri or settings.FACEBOOK_REDIRECT_URI,
        'scope': scope,
        'response_type': 'code'
    }
    return f'https://www.facebook.com/v18.0/dialog/oauth?{urllib.parse.urlencode(params)}'

def get_linkedin_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for LinkedIn"""
    scope = 'r_liteprofile r_emailaddress'
    if business:
        scope += ' r_organization_social w_organization_social rw_organization_admin'
    
    params = {
        'client_id': settings.LINKEDIN_CLIENT_ID,
        'redirect_uri': redirect_uri or settings.LINKEDIN_REDIRECT_URI,
        'scope': scope,
        'response_type': 'code',
        'state': 'random_state_string'
    }
    return f'https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}'

def generate_code_verifier():
    """Generate a code verifier for PKCE"""
    return secrets.token_urlsafe(32)

def generate_code_challenge(verifier):
    """Generate a code challenge for PKCE"""
    sha256 = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(sha256).decode('utf-8').rstrip('=')

def get_twitter_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for Twitter"""
    # Generate PKCE values
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    # Generate state
    state = secrets.token_urlsafe(16)
    
    params = {
        'client_id': settings.TWITTER_CLIENT_ID,
        'redirect_uri': redirect_uri or f"{settings.OAUTH2_REDIRECT_URI}/oauth-callback/twitter",
        'response_type': 'code',
        'scope': 'tweet.read users.read follows.read offline.access',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    if business:
        params['scope'] += ' tweet.write follows.write'
    
    # Store these values in session or cache for later verification
    # You'll need to implement this part based on your session/cache setup
    
    return {
        'auth_url': f'https://twitter.com/i/oauth2/authorize?{urllib.parse.urlencode(params)}',
        'code_verifier': code_verifier,
        'state': state
    }

def get_instagram_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for Instagram"""
    scope = 'basic'
    if business:
        # Instagram Business requires Facebook authentication
        return get_facebook_oauth_url(business=True, redirect_uri=redirect_uri)
    
    params = {
        'client_id': settings.INSTAGRAM_CLIENT_ID,
        'redirect_uri': redirect_uri or settings.INSTAGRAM_REDIRECT_URI,
        'scope': scope,
        'response_type': 'code'
    }
    return f'https://api.instagram.com/oauth/authorize?{urllib.parse.urlencode(params)}'

def get_tiktok_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for TikTok"""
    scope = 'user.info.basic'
    if business:
        scope += ' video.list user.info.stats'
    
    params = {
        'client_key': settings.TIKTOK_CLIENT_KEY,
        'redirect_uri': redirect_uri or settings.TIKTOK_REDIRECT_URI,
        'scope': scope,
        'response_type': 'code',
        'state': 'random_state_string'
    }
    return f'https://www.tiktok.com/auth/authorize/?{urllib.parse.urlencode(params)}'

def get_telegram_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for Telegram"""
    # Telegram uses a different authentication flow through their Bot API
    params = {
        'bot_id': settings.TELEGRAM_BOT_USERNAME,
        'origin': redirect_uri or settings.TELEGRAM_REDIRECT_URI,
        'request_access': 'write' if business else 'read'
    }
    return f'https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={urllib.parse.urlencode(params)}'

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
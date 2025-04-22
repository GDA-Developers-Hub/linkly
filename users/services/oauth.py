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
import time

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

def get_facebook_oauth_url(redirect_uri=None, business: bool = False):
    """
    Generate Facebook OAuth2 URL with PKCE
    """
    from django.conf import settings
    from urllib.parse import urlencode
    import secrets
    
    logger = logging.getLogger('social')
    
    try:
        # Use provided redirect URI or default
        oauth_redirect_uri = redirect_uri or settings.OAUTH2_REDIRECT_URI
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Required parameters
        params = {
            'client_id': settings.FACEBOOK_CLIENT_ID,
            'redirect_uri': oauth_redirect_uri,
            'state': state,
            'scope': 'email,public_profile,pages_show_list' if business else 'email,public_profile',
            'response_type': 'code',
        }
        
        # Build authorization URL
        auth_url = f"https://www.facebook.com/v12.0/dialog/oauth?{urlencode(params)}"
        
        logger.info("Generated Facebook OAuth URL successfully")
        
        return {
            'auth_url': auth_url,
            'state': state
        }
        
    except Exception as e:
        logger.error(f"Error generating Facebook OAuth URL: {str(e)}")
        raise ValueError(f"Failed to generate Facebook OAuth URL: {str(e)}")

def get_linkedin_oauth_url(redirect_uri=None):
    """
    Generate LinkedIn OAuth2 URL with state parameter
    """
    from django.conf import settings
    from urllib.parse import urlencode
    import secrets
    
    try:
        # Use provided redirect URI or default
        oauth_redirect_uri = redirect_uri or settings.LINKEDIN_CALLBACK_URL
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        
        # Required parameters
        params = {
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'redirect_uri': oauth_redirect_uri,
            'state': state,
            'scope': ' '.join([
                'openid',
                'profile',
                'w_member_social',
                'email'
            ]),
            'response_type': 'code'
        }
        
        # Build authorization URL
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state
        }
        
    except Exception as e:
        logger.error(f"Error generating LinkedIn OAuth URL: {str(e)}")
        raise ValueError(f"Failed to generate LinkedIn OAuth URL: {str(e)}")

def get_twitter_oauth_url(redirect_uri=None, business: bool = False):
    """
    Get Twitter OAuth authorization URL using OAuth 2.0 with PKCE
    """
    import secrets
    import hashlib
    import base64
    from urllib.parse import urlencode
    from django.conf import settings
    
    try:
        # Use provided redirect URI or default
        oauth_redirect_uri = redirect_uri or settings.OAUTH2_REDIRECT_URI
        
        # Ensure we have client credentials
        if not settings.TWITTER_CLIENT_ID or not settings.TWITTER_CLIENT_SECRET:
            raise ValueError("Twitter client credentials are not configured")
        
        # Generate PKCE code verifier and challenge
        code_verifier = secrets.token_urlsafe(96)[:128]  # Ensure it's not too long for Twitter
        
        # Generate code challenge using SHA256
        code_challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8')
        code_challenge = code_challenge.replace('=', '')  # Remove padding
        
        # Generate state parameter with platform prefix for identification
        state = f"twitter_{secrets.token_urlsafe(24)}"
        
        # Required parameters
        params = {
            'client_id': settings.TWITTER_CLIENT_ID,
            'redirect_uri': oauth_redirect_uri,
            'state': state,
            'scope': 'tweet.read users.read offline.access tweet.write' if business else 'tweet.read users.read offline.access',
            'response_type': 'code',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Build authorization URL
        auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
            'code_verifier': code_verifier
        }
        
    except Exception as e:
        print(f"Error generating Twitter OAuth URL: {str(e)}")
        return None


def connect_twitter_account(user, code: str, state: str, code_verifier: str) -> Dict:
    """
    Connect Twitter account using OAuth 2.0 token
    """
    import logging
    import tweepy
    from django.conf import settings
    from ..models import SocialAccount
    from datetime import datetime, timezone
    
    logger = logging.getLogger('social')
    
    try:
        logger.info(f"Starting Twitter connection for user {user.id} with code_verifier length: {len(code_verifier) if code_verifier else 'None'}")
        
        # Initialize OAuth 2.0 client
        client = tweepy.Client(
            consumer_key=settings.TWITTER_CLIENT_ID,
            consumer_secret=settings.TWITTER_CLIENT_SECRET,
            return_type=dict
        )
        
        # Define the redirect URI - must match what was used in the initial auth request
        redirect_uri = settings.OAUTH2_REDIRECT_URI
        logger.info(f"Using Twitter redirect URI: {redirect_uri}")
        
        # Exchange code for access token
        logger.info("Exchanging code for Twitter access token")
        token_response = client.fetch_token(
            "https://api.twitter.com/2/oauth2/token",
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier
        )
        
        # Get access token and refresh token
        logger.info("Successfully obtained Twitter tokens")
        access_token = token_response['access_token']
        refresh_token = token_response.get('refresh_token')
        
        # Initialize client with access token
        client = tweepy.Client(bearer_token=access_token)
        
        # Get user profile information
        logger.info("Fetching Twitter user profile")
        me = client.get_me(user_fields=['profile_image_url', 'description', 'public_metrics'])
        twitter_id = me['data']['id']
        twitter_username = me['data']['username']
        
        # Update or create social account
        logger.info(f"Updating Twitter account for user: {twitter_username}")
        social_account, created = SocialAccount.objects.update_or_create(
            user=user,
            platform='twitter',
            defaults={
                'platform_id': twitter_id,
                'username': twitter_username,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'profile_data': me['data'],
                'last_sync': datetime.now(timezone.utc)
            }
        )
        
        logger.info(f"Successfully connected Twitter account for user {user.id}")
        
        return {
            'success': True,
            'account_id': social_account.id,
            'platform': 'twitter',
            'username': twitter_username,
            'profile_data': me['data']
        }
        
    except Exception as e:
        logger.error(f"Error connecting Twitter account: {str(e)}")
        raise ValueError(f"Failed to connect Twitter account: {str(e)}")

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

def get_youtube_oauth_url(redirect_uri=None, business: bool = False):
    """Get YouTube OAuth URL (uses Google OAuth)."""
    platform = 'youtube'
    state = store_oauth_state(platform)
    
    try:
        # Use provided redirect URI or default
        oauth_redirect_uri = redirect_uri or settings.OAUTH2_REDIRECT_URI
        
        # Generate PKCE code verifier and challenge
        code_verifier = secrets.token_urlsafe(96)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        # Required parameters
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': oauth_redirect_uri,
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl' if business else 'https://www.googleapis.com/auth/youtube.readonly',
            'access_type': 'offline',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'include_granted_scopes': 'true'
        }
        
        # Build authorization URL
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state,
            'code_verifier': code_verifier
        }
        
    except Exception as e:
        logger.error(f"Error generating YouTube OAuth URL: {str(e)}")
        raise ValueError(f"Failed to generate YouTube OAuth URL: {str(e)}")

def get_telegram_oauth_url(redirect_uri=None, business: bool = False):
    """Get Telegram OAuth URL."""
    platform = 'telegram'
    state = store_oauth_state(platform)
    
    try:
        # Use provided redirect URI or default
        oauth_redirect_uri = redirect_uri or settings.OAUTH2_REDIRECT_URI
        
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token is not configured")
        
        # Generate secure hash
        bot_token = settings.TELEGRAM_BOT_TOKEN
        auth_date = str(int(time.time()))
        
        # Required parameters
        params = {
            'bot_id': bot_token.split(':')[0],
            'origin': oauth_redirect_uri,
            'embed': '1',
            'return_to': oauth_redirect_uri,
            'auth_date': auth_date,
            'state': state
        }
        
        # Build authorization URL
        auth_url = f"https://oauth.telegram.org/auth?{urllib.parse.urlencode(params)}"
        
        return {
            'auth_url': auth_url,
            'state': state
        }
        
    except Exception as e:
        logger.error(f"Error generating Telegram OAuth URL: {str(e)}")
        raise ValueError(f"Failed to generate Telegram OAuth URL: {str(e)}")

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
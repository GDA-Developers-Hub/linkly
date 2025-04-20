from django.conf import settings
import requests
import tweepy
import hashlib
import hmac
from urllib.parse import urlencode
import secrets

def get_google_auth_url():
    """Get Google OAuth2 authorization URL"""
    params = {
        'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}/users/auth/google/callback/",
        'scope': ' '.join([
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/youtube'
        ]),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def get_facebook_auth_url(redirect_uri=None):
    """Get Facebook OAuth2 authorization URL"""
    params = {
        'client_id': settings.SOCIAL_AUTH_FACEBOOK_KEY,
        'redirect_uri': redirect_uri or f"{settings.OAUTH2_REDIRECT_URI}/users/auth/facebook/callback/",
        'scope': 'email,public_profile,pages_show_list,pages_read_engagement,pages_manage_posts',
        'response_type': 'code',
        'state': secrets.token_urlsafe(32)  # Generate secure state parameter
    }
    return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"

def get_linkedin_auth_url():
    """Get LinkedIn OAuth2 authorization URL"""
    params = {
        'client_id': settings.SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY,
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}/users/auth/linkedin/callback/",
        'scope': 'r_liteprofile r_emailaddress w_member_social rw_organization_admin',
        'response_type': 'code',
        'state': hashlib.sha256(settings.SECRET_KEY.encode()).hexdigest()
    }
    return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

def get_twitter_auth_url():
    """Get Twitter OAuth authorization URL"""
    try:
        # Initialize OAuth 1.0a authentication
        auth = tweepy.OAuthHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            callback=f"{settings.OAUTH2_REDIRECT_URI}/users/auth/twitter/callback/"
        )

        # Set access token for API v1.1 compatibility
        auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )

        try:
            # Get authorization URL
            redirect_url = auth.get_authorization_url(
                signin_with_twitter=True,
                include_email=True
            )
            request_token = auth.request_token
            print(f"Twitter OAuth Debug - Auth URL: {redirect_url}")  # Debug log
            print(f"Twitter OAuth Debug - Request Token: {request_token}")  # Debug log
            return redirect_url, request_token
        except (tweepy.errors.TweepyException, Exception) as e:
            print(f"Twitter auth error: {str(e)}")  # Debug log
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Twitter API Response: {e.response.text}")  # Debug log
            return None, None
    except Exception as e:
        print(f"Twitter setup error: {str(e)}")  # Debug log
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Twitter API Response: {e.response.text}")  # Debug log
        return None, None

def get_instagram_auth_url():
    """Get Instagram OAuth2 authorization URL"""
    params = {
        'client_id': settings.INSTAGRAM_CLIENT_ID,
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}/users/auth/instagram/callback/",
        'scope': 'basic public_content',
        'response_type': 'code'
    }
    return f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"

def get_tiktok_auth_url():
    """Get TikTok OAuth authorization URL"""
    params = {
        'client_key': settings.TIKTOK_CLIENT_KEY,
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}/users/auth/tiktok/callback/",
        'scope': 'user.info.basic,video.list',
        'response_type': 'code'
    }
    return f"https://open-api.tiktok.com/platform/oauth/connect/?{urlencode(params)}"

def get_telegram_auth_url():
    """Get Telegram login widget URL"""
    params = {
        'origin': settings.OAUTH2_REDIRECT_URI,
        'bot_id': settings.TELEGRAM_BOT_TOKEN.split(':')[0],
        'request_access': 'write',
        'return_to': f"{settings.OAUTH2_REDIRECT_URI}/users/auth/telegram/callback/"
    }
    return f"https://oauth.telegram.org/auth?{urlencode(params)}"

def verify_telegram_hash(auth_data):
    """Verify Telegram authentication hash"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    auth_string = []
    
    for key in sorted(auth_data.keys()):
        if key != 'hash':
            auth_string.append(f'{key}={auth_data[key]}')
    
    auth_string = '\n'.join(auth_string)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash = hmac.new(secret_key, auth_string.encode(), hashlib.sha256).hexdigest()
    
    return hash == auth_data['hash'] 
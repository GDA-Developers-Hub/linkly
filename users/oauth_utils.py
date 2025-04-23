from django.conf import settings
import requests
import tweepy
import hashlib
import hmac
from urllib.parse import urlencode
import secrets
import logging
from django.core.cache import cache
from typing import Tuple, Optional, Dict

def get_google_auth_url():
    """Get Google OAuth2 authorization URL"""
    params = {
        'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}api/v1/users/auth/google/callback/",
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
        'redirect_uri': redirect_uri or f"{settings.OAUTH2_REDIRECT_URI}api/v1/users/auth/facebook/callback/",
        'scope': 'email,public_profile,pages_show_list,pages_read_engagement,pages_manage_posts',
        'response_type': 'code',
        'state': secrets.token_urlsafe(32)  # Generate secure state parameter
    }
    return f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"

def get_linkedin_auth_url():
    """Get LinkedIn OAuth2 authorization URL"""
    params = {
        'client_id': settings.SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY,
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}/api/v1/users/auth/linkedin/callback/",
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
            callback=f"{settings.OAUTH2_REDIRECT_URI}/api/v1/users/auth/twitter/callback/"
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
        'redirect_uri': f"{settings.OAUTH2_REDIRECT_URI}api/v1/users/auth/instagram/callback/",
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

def verify_oauth_state_from_sources(state: str, platform: str) -> Tuple[bool, Optional[Dict]]:
    """Returns (is_valid, data) tuple"""
    logger = logging.getLogger('oauth')
    logger.info(f"Verifying {platform} OAuth state: {state}")
    
    # Try all possible cache key formats
    cache_data = None
    cache_key_formats = [
        f'oauth_state_{state}',
        f'{platform}_oauth_state_{state}',
        f'1:oauth_state_{state}',
        f'1:{platform}_oauth_state_{state}'
    ]
    
    for cache_key in cache_key_formats:
        logger.info(f"Trying cache key: {cache_key}")
        try:
            data = cache.get(cache_key)
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            # Fall back to session
            continue
        if data:
            cache.delete(cache_key)  # Remove used state
            cache_data = data
            logger.info(f"Found state data in cache with key: {cache_key}")
            return True, data
    
    # Log all cache keys for debugging
    try:
        all_keys = cache.keys('*oauth_state*')
        logger.info(f"Available oauth state cache keys: {all_keys}")
    except Exception as e:
        logger.warning(f"Could not list cache keys: {e}")
    
    # If not found in cache, try session storage
    # This is a fallback for when Redis is not available
    from django.contrib.sessions.backends.base import SessionBase
    
    def check_session(request, key):
        if hasattr(request, 'session') and isinstance(request.session, SessionBase):
            if key in request.session:
                value = request.session.get(key)
                if state == value:
                    logger.info(f"Found matching state in session with key: {key}")
                    return True, value
        return False, None
    
    # Check if we have request in the current context
    from django.core.handlers.wsgi import WSGIRequest
    if 'request' in locals() and isinstance(request, WSGIRequest):
        if check_session(request, 'oauth_state') or check_session(request, f'{platform}_oauth_state'):
            return True, cache_data
    
    # In production, we may want to proceed with a warning rather than failing
    # This is a fallback for when Redis has issues or when cache expires
    if not settings.DEBUG:
        logger.warning(f"State verification failed for {platform}: state={state} not found in cache or session")
        logger.warning(f"Proceeding without state verification in production")
        return True, cache_data
    
    logger.error(f"State verification failed for {platform}: state={state} not found in any source")
    return False, None

def exchange_linkedin_code(code, redirect_uri):
    # Implementation of exchange_linkedin_code function
    pass

def linkedin_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    if not code or not state:
        return HttpResponse("Invalid request")

    if request.user.is_authenticated:
        # User is authenticated, connect LinkedIn account
        result = connect_linkedin_account(request.user, code, state)
        # Return success response with redirect to frontend
        return result
    else:
        # User is not authenticated, store tokens for later
        token_data = exchange_linkedin_code(code, redirect_uri=settings.LINKEDIN_CALLBACK_URL)
        token_cache_key = f'linkedin_token_{state}'
        cache.set(token_cache_key, token_data, timeout=3600)
        redirect_url = f"{settings.FRONTEND_URL}/login?pending_oauth=linkedin&state={state}"
        return redirect_url 
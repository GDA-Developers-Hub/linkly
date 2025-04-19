from django.conf import settings
import urllib.parse

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

def get_twitter_oauth_url(business=False, redirect_uri=None):
    """Generate OAuth URL for Twitter"""
    scope = 'tweet.read users.read'
    if business:
        scope += ' account.follow.read account.follows.read'
    
    params = {
        'client_id': settings.TWITTER_CLIENT_ID,
        'redirect_uri': redirect_uri or settings.TWITTER_REDIRECT_URI,
        'scope': scope,
        'response_type': 'code',
        'state': 'random_state_string'
    }
    return f'https://twitter.com/i/oauth2/authorize?{urllib.parse.urlencode(params)}'

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
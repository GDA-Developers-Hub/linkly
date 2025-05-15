"""
Twitter OAuth compatibility module for backward compatibility.
This provides the functions that were previously in the oauth/twitter.py module.
"""
import logging
import warnings
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter

logger = logging.getLogger(__name__)

def get_twitter_auth_url(request, oauth_callback, session=None):
    """
    Generate Twitter OAuth URL using Allauth.
    This is a compatibility function for backward compatibility.
    """
    warnings.warn(
        "get_twitter_auth_url is deprecated. Please use Django Allauth integration instead.",
        DeprecationWarning, stacklevel=2
    )
    
    try:
        # Get Twitter app
        app = SocialApp.objects.get(provider='twitter')
        
        # Create adapter
        adapter = TwitterOAuthAdapter()
        
        # Get a request token
        request_token = adapter.get_request_token(oauth_callback)
        
        # Store the request token in the session
        if session:
            session['twitter_request_token'] = request_token
        elif hasattr(request, 'session'):
            request.session['twitter_request_token'] = request_token
            
        # Construct the authorize URL
        authorize_url = f"https://api.twitter.com/oauth/authenticate?oauth_token={request_token['oauth_token']}"
        
        return {
            'url': authorize_url,
            'request_token': request_token
        }
    except Exception as e:
        logger.exception(f"Error getting Twitter auth URL: {str(e)}")
        return {'error': str(e)}

def handle_twitter_callback(request, oauth_token, oauth_verifier, request_token=None):
    """
    Handle Twitter OAuth callback.
    This is a compatibility function for backward compatibility.
    """
    warnings.warn(
        "handle_twitter_callback is deprecated. Please use Django Allauth integration instead.",
        DeprecationWarning, stacklevel=2
    )
    
    try:
        # Get Twitter app
        app = SocialApp.objects.get(provider='twitter')
        
        # Create adapter
        adapter = TwitterOAuthAdapter()
        
        # Get the request token from the session if not provided
        if not request_token and hasattr(request, 'session'):
            request_token = request.session.get('twitter_request_token')
            
        if not request_token:
            return {'error': 'Missing request token'}
            
        # Get access token
        access_token = adapter.get_access_token(request_token, oauth_verifier)
        
        # Get user info
        user_info = adapter.get_user_info(access_token)
        
        return {
            'user_id': user_info.get('id'),
            'screen_name': user_info.get('screen_name'),
            'name': user_info.get('name'),
            'access_token': access_token.get('oauth_token'),
            'access_token_secret': access_token.get('oauth_token_secret')
        }
    except Exception as e:
        logger.exception(f"Error handling Twitter callback: {str(e)}")
        return {'error': str(e)}

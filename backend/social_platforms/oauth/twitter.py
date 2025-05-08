import base64
import hashlib
import logging
import secrets
import requests
from django.utils import timezone
from datetime import timedelta
import urllib.parse
from ..models import SocialPlatform, UserSocialAccount

logger = logging.getLogger(__name__)

def generate_code_verifier():
    """Generate a random code verifier for PKCE"""
    return secrets.token_urlsafe(64)[:128]

def generate_code_challenge(code_verifier):
    """Generate code challenge using S256 method"""
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')

def get_twitter_auth_url(request, user):
    """Generate Twitter OAuth authorization URL with secure PKCE"""
    try:
        # Get Twitter platform configuration
        try:
            twitter_platform = SocialPlatform.objects.get(name='twitter', is_active=True)
            logger.info(f"Found Twitter platform: {twitter_platform.name}, client_id: {twitter_platform.client_id[:5]}...")
        except SocialPlatform.DoesNotExist:
            logger.error("Twitter platform not found in database")
            raise Exception("Twitter platform not configured in system")
        
        # Generate a cryptographically secure random code verifier
        code_verifier = generate_code_verifier()
        logger.info(f"Generated code_verifier: {code_verifier[:10]}... (length: {len(code_verifier)})")
        
        # Generate proper S256 code challenge
        code_challenge = generate_code_challenge(code_verifier)
        logger.info(f"Generated code_challenge: {code_challenge[:10]}... (length: {len(code_challenge)})")
        
        # Store verifier securely in session for the callback
        request.session['twitter_code_verifier'] = code_verifier
        
        # Generate a secure state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session['oauth_state_twitter'] = state
        
        # Build the parameters 
        params = {
            'client_id': twitter_platform.client_id,
            'redirect_uri': twitter_platform.redirect_uri,
            'response_type': 'code',
            'scope': twitter_platform.scope,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Detailed logging of each parameter
        logger.info("OAuth parameters being used:")
        for key, value in params.items():
            if key in ['client_id', 'code_challenge']:
                logger.info(f"  {key}: {value[:10]}...")
            else:
                logger.info(f"  {key}: {value}")
        
        # Use urllib.parse.urlencode for proper parameter encoding
        query_string = urllib.parse.urlencode(params)
        logger.info(f"Generated query string: {query_string[:50]}...")
        
        auth_url = f"{twitter_platform.auth_url}?{query_string}"
        
        # Log the full URL for debugging
        logger.info(f"Complete auth URL: {auth_url}")
        
        # Check if PKCE parameters are in the URL
        if 'code_challenge' not in auth_url:
            logger.error("CRITICAL: code_challenge not found in final URL!")
        if 'code_challenge_method' not in auth_url:
            logger.error("CRITICAL: code_challenge_method not found in final URL!")
        
        return auth_url
        
    except Exception as e:
        logger.error(f"Error generating Twitter auth URL: {str(e)}")
        raise

def handle_twitter_callback(request, user, code, state):
    """Process Twitter OAuth callback and create account with secure PKCE"""
    try:
        # Log the start of callback processing
        logger.info(f"Twitter OAuth callback handler started")
        logger.info(f"Authorization code received, length: {len(code)}")
        logger.info(f"State parameter received: {state[:10]}...")
        
        # Get Twitter platform configuration
        try:
            twitter_platform = SocialPlatform.objects.get(name='twitter', is_active=True)
            logger.info(f"Using Twitter platform configuration: {twitter_platform.name}")
        except SocialPlatform.DoesNotExist:
            logger.error("Twitter platform not found in database")
            raise Exception("Twitter platform not configured in system")
        
        # Retrieve values from session
        expected_state = request.session.get('oauth_state_twitter')
        code_verifier = request.session.get('twitter_code_verifier')
        
        # Validate state parameter (CSRF protection)
        if not expected_state:
            logger.error("No state parameter found in session - session may have expired")
            raise Exception("Session expired or invalid. Please try again.")
            
        if expected_state != state:
            logger.error(f"State parameter mismatch. Session may have been tampered with.")
            raise Exception("Security validation failed. Please try again.")
            
        # Validate code verifier
        if not code_verifier:
            logger.error("No code verifier found in session - session may have expired")
            raise Exception("Session expired or invalid. Please try again.")
            
        logger.info("Security validation passed successfully")
        
        # Clean up session
        if 'oauth_state_twitter' in request.session:
            del request.session['oauth_state_twitter']
        if 'twitter_code_verifier' in request.session:
            del request.session['twitter_code_verifier']
            
        # Now exchange the code for an access token using secure code_verifier
        token_url = twitter_platform.token_url
        token_data = {
            'client_id': twitter_platform.client_id,
            'client_secret': twitter_platform.client_secret,
            'code': code,
            'redirect_uri': twitter_platform.redirect_uri,
            'grant_type': 'authorization_code',
            'code_verifier': code_verifier  # Important: Using the secure code_verifier from session
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        # Log what we're sending for debugging
        logger.info(f"Token request to {token_url}")
        logger.info(f"Code: {code[:5]}...")
        logger.info(f"Redirect URI: {twitter_platform.redirect_uri}")
        
        # Exchange code for token
        token_response = requests.post(
            token_url,
            data=token_data,
            headers=headers,
        )
        
        if token_response.status_code != 200:
            logger.error(f"Token error: {token_response.status_code} {token_response.text}")
            raise Exception(f"Failed to exchange code for token: {token_response.text}")
            
        token_data = token_response.json()
        
        # Get user info with the token
        user_info_url = "https://api.twitter.com/2/users/me"
        user_info_headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        user_info_params = {
            "user.fields": "profile_image_url,username"
        }
        
        user_info_response = requests.get(
            user_info_url,
            headers=user_info_headers,
            params=user_info_params
        )
        
        if user_info_response.status_code != 200:
            logger.error(f"User info error: {user_info_response.text}")
            raise Exception(f"Failed to get user info: {user_info_response.text}")
            
        user_data = user_info_response.json().get('data', {})
        
        # Get the Twitter platform instance
        twitter_platform = SocialPlatform.objects.get(name='twitter')
        
        # Create or update social media account
        account, created = UserSocialAccount.objects.update_or_create(
            user=user,
            platform=twitter_platform,
            account_id=user_data['id'],
            defaults={
                'account_name': user_data.get('username', ''),
                'profile_picture_url': user_data.get('profile_image_url', ''),
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'token_expiry': timezone.now() + timedelta(seconds=token_data.get('expires_in', 7200)),
                'status': 'active',
                'raw_data': user_data
            }
        )
        
        return account
        
    except Exception as e:
        logger.error(f"Error in Twitter callback: {str(e)}")
        raise

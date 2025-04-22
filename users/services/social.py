from django.conf import settings
import requests
import hashlib
import hmac
import time
from rest_framework import status
from rest_framework.exceptions import ValidationError
import tweepy
from django.utils import timezone
from django.core.cache import cache
import logging
from typing import Dict, Any
from .exceptions import (
    OAuthError,
    TokenExchangeError,
    ProfileFetchError,
    StateVerificationError,
    PKCEVerificationError
)
from ..utils.oauth import get_platform_config, verify_oauth_state, get_stored_code_verifier
import base64
import json

logger = logging.getLogger('social')

class SocialConnectionError(Exception):
    pass

def exchange_google_code(code, redirect_uri=None):
    """Exchange Google auth code for tokens"""
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'code': code,
                'redirect_uri': redirect_uri or settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange Google auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Google OAuth error: {str(e)}')

def exchange_facebook_code(code, redirect_uri=None):
    """Exchange Facebook auth code for tokens"""
    try:
        response = requests.get(
            'https://graph.facebook.com/v18.0/oauth/access_token',
            params={
                'client_id': settings.FACEBOOK_CLIENT_ID,
                'client_secret': settings.FACEBOOK_CLIENT_SECRET,
                'code': code,
                'redirect_uri': redirect_uri or settings.FACEBOOK_REDIRECT_URI
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange Facebook auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Facebook OAuth error: {str(e)}')

def exchange_linkedin_code(code, redirect_uri=None):
    """Exchange LinkedIn auth code for tokens"""
    try:
        # Build the request data
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET,
            'redirect_uri': redirect_uri or settings.LINKEDIN_REDIRECT_URI
        }
        
        # Log the request data (without sensitive info)
        logger = logging.getLogger('oauth')
        logger.info(f"Exchanging LinkedIn code. Redirect URI: {redirect_uri or settings.LINKEDIN_REDIRECT_URI}")
        logger.info(f"LinkedIn client ID: {settings.LINKEDIN_CLIENT_ID[:5]}... (truncated)")
        logger.info(f"Code length: {len(code) if code else 'None'}")
        
        # Make the token request
        response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data=data
        )
        
        # Check for errors and log response
        if response.status_code != 200:
            error_msg = f'Failed to exchange LinkedIn auth code: Status {response.status_code}, Response: {response.text}'
            logger.error(error_msg)
            
            # Try to parse the error response
            try:
                error_data = response.json()
                logger.error(f"LinkedIn API error details: {error_data}")
            except:
                logger.error("Could not parse LinkedIn error response as JSON")
                
            raise SocialConnectionError(error_msg)
            
        # Parse and return the token response
        token_data = response.json()
        logger.info(f"Successfully exchanged LinkedIn code for token. Token type: {token_data.get('token_type')}")
        logger.info(f"Access token length: {len(token_data.get('access_token', ''))}")
        
        # If the response includes a refresh token, log that too
        if 'refresh_token' in token_data:
            logger.info("Refresh token received from LinkedIn")
        
        return token_data
    except requests.RequestException as e:
        logger.error(f'LinkedIn OAuth network error: {str(e)}')
        if hasattr(e, 'response') and e.response:
            logger.error(f'LinkedIn response status: {e.response.status_code}')
            logger.error(f'LinkedIn response content: {e.response.text}')
        raise SocialConnectionError(f'LinkedIn OAuth request error: {str(e)}')
    except Exception as e:
        logger.error(f'LinkedIn OAuth error: {str(e)}')
        raise SocialConnectionError(f'LinkedIn OAuth error: {str(e)}')

def exchange_twitter_code(
    code: str, redirect_uri: str, code_verifier: str
) -> Dict[str, Any]:
    """
    Exchange the Twitter auth code for an access token.
    
    Args:
        code: Authorization code
        redirect_uri: Redirect URI used during authorization
        code_verifier: PKCE code verifier
        
    Returns:
        Dict containing the access token and profile information
        
    Raises:
        SocialConnectionError: If the token exchange fails
    """
    logger = logging.getLogger('social')
    logger.info(f"Exchanging Twitter code for token with redirect URI: {redirect_uri}")
    logger.info(f"Code length: {len(code) if code else 0}, Code verifier length: {len(code_verifier) if code_verifier else 0}")
    
    # Prepare the token request data
    token_url = 'https://api.twitter.com/2/oauth2/token'
    data = {
        'client_id': settings.TWITTER_CLIENT_ID,
        'client_secret': settings.TWITTER_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
    }
    
    # Log request data without exposing sensitive information
    logger.info(
        f"Twitter token request data: client_id={settings.TWITTER_CLIENT_ID[:5]}..., "
        f"redirect_uri={redirect_uri}, code_length={len(code)}"
    )
    
    try:
        # Execute the token request
        token_response = requests.post(token_url, data=data)
        
        # Check if the request was successful
        if token_response.status_code != 200:
            logger.error(
                f"Twitter token exchange failed with status {token_response.status_code}: {token_response.text}"
            )
            
            # Try to parse the error response as JSON
            try:
                error_data = token_response.json()
                logger.error(f"Twitter error details: {error_data}")
                error_message = error_data.get('error_description', 'Unknown error')
            except (ValueError, json.JSONDecodeError):
                logger.error("Could not parse Twitter error response as JSON")
                error_message = token_response.text if token_response.text else f"HTTP {token_response.status_code}"
            
            raise SocialConnectionError(f"Twitter API error: {error_message}")
        
        # Parse the token response
        token_data = token_response.json()
        
        # Log successful token exchange
        logger.info(
            f"Successfully exchanged Twitter code for token. "
            f"Token type: {token_data.get('token_type')}, "
            f"Access token length: {len(token_data.get('access_token', ''))},"
        )
        
        if 'refresh_token' in token_data:
            logger.info("Refresh token included in Twitter response")
        
        # Twitter requires a separate call to get the user profile
        me_url = 'https://api.twitter.com/2/users/me'
        me_params = {
            'user.fields': 'name,username,profile_image_url,description,verified'
        }
        me_headers = {
            'Authorization': f"Bearer {token_data['access_token']}"
        }
        
        logger.info("Fetching Twitter user profile")
        profile_response = requests.get(me_url, params=me_params, headers=me_headers)
        
        if profile_response.status_code != 200:
            logger.error(
                f"Twitter profile fetch failed with status {profile_response.status_code}: {profile_response.text}"
            )
            
            # Try to parse the error response as JSON
            try:
                error_data = profile_response.json()
                logger.error(f"Twitter profile error details: {error_data}")
                error_message = error_data.get('error_description', 'Unknown error')
            except (ValueError, json.JSONDecodeError):
                logger.error("Could not parse Twitter profile error response as JSON")
                error_message = profile_response.text if profile_response.text else f"HTTP {profile_response.status_code}"
                
            raise SocialConnectionError(f"Twitter profile API error: {error_message}")
        
        profile_data = profile_response.json()
        logger.info(f"Successfully fetched Twitter profile for user: {profile_data.get('data', {}).get('username')}")
        
        # Combine token and profile data
        result = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data.get('refresh_token'),
            'expires_in': token_data.get('expires_in'),
            'profile': profile_data.get('data', {})
        }
        
        # Add profile data for convenience and consistency across platforms
        twitter_user = profile_data.get('data', {})
        name = twitter_user.get('name', '')
        username = twitter_user.get('username', '')
        
        result['name'] = name
        result['email'] = f"{username}@twitter.com"  # Twitter doesn't provide email
        result['picture'] = twitter_user.get('profile_image_url', '')
        result['user_id'] = twitter_user.get('id', '')
        
        return result
    
    except requests.RequestException as e:
        # Network-related error
        logger.exception(f"Network error during Twitter code exchange: {str(e)}")
        raise SocialConnectionError(f"Failed to connect to Twitter API: {str(e)}")
    
    except Exception as e:
        # Any other unexpected error
        logger.exception(f"Unexpected error during Twitter code exchange: {str(e)}")
        raise SocialConnectionError(f"Twitter authentication error: {str(e)}")

def exchange_instagram_code(code: str, redirect_uri: str = None) -> Dict[str, Any]:
    """
    Exchange the Instagram auth code for an access token.
    
    Args:
        code: Authorization code from Instagram
        redirect_uri: Redirect URI used during authorization
        
    Returns:
        Dict containing the access token and profile information
        
    Raises:
        SocialConnectionError: If the token exchange fails
    """
    logger = logging.getLogger('social')
    
    if not redirect_uri:
        redirect_uri = settings.INSTAGRAM_REDIRECT_URI
    
    logger.info(f"Exchanging Instagram code for token with redirect URI: {redirect_uri}")
    logger.info(f"Code length: {len(code) if code else 0}")
    
    # Prepare the token request data
    token_url = 'https://api.instagram.com/oauth/access_token'
    data = {
        'client_id': settings.INSTAGRAM_CLIENT_ID,
        'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    # Log request data without exposing sensitive information
    logger.info(
        f"Instagram token request data: client_id={settings.INSTAGRAM_CLIENT_ID[:5]}..., "
        f"redirect_uri={redirect_uri}, code_length={len(code)}"
    )
    
    try:
        # Execute the token request
        token_response = requests.post(token_url, data=data)
        
        # Check if the request was successful
        if token_response.status_code != 200:
            logger.error(
                f"Instagram token exchange failed with status {token_response.status_code}: {token_response.text}"
            )
            
            # Try to parse the error response as JSON
            try:
                error_data = token_response.json()
                logger.error(f"Instagram error details: {error_data}")
                error_message = error_data.get('error_message', 'Unknown error')
            except (ValueError, json.JSONDecodeError):
                logger.error("Could not parse Instagram error response as JSON")
                error_message = token_response.text if token_response.text else f"HTTP {token_response.status_code}"
            
            raise SocialConnectionError(f"Instagram API error: {error_message}")
        
        # Parse the token response
        token_data = token_response.json()
        
        # Log successful token exchange
        logger.info(
            f"Successfully exchanged Instagram code for token. "
            f"Access token length: {len(token_data.get('access_token', ''))}, "
            f"User ID: {token_data.get('user_id', 'N/A')}"
        )
        
        # Instagram returns a short-lived access token and user_id in the first request
        # We need to make additional calls to get the user's profile and a long-lived token
        access_token = token_data.get('access_token')
        user_id = token_data.get('user_id')
        
        if not access_token:
            logger.error("Instagram returned no access token")
            raise SocialConnectionError("Instagram authentication failed: No access token returned")
        
        # Get a long-lived token
        logger.info("Exchanging for long-lived Instagram token")
        long_lived_url = 'https://graph.instagram.com/access_token'
        params = {
            'grant_type': 'ig_exchange_token',
            'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
            'access_token': access_token
        }
        
        try:
            long_lived_response = requests.get(long_lived_url, params=params)
            
            if long_lived_response.status_code != 200:
                logger.error(
                    f"Instagram long-lived token exchange failed with status {long_lived_response.status_code}: {long_lived_response.text}"
                )
                # Continue with the short-lived token
                logger.warning("Continuing with short-lived Instagram token")
            else:
                long_lived_data = long_lived_response.json()
                access_token = long_lived_data.get('access_token', access_token)
                logger.info(
                    f"Successfully exchanged for long-lived Instagram token. "
                    f"Expires in: {long_lived_data.get('expires_in', 'N/A')} seconds"
                )
        except Exception as e:
            logger.warning(f"Error exchanging for long-lived Instagram token: {str(e)}")
            # Continue with the short-lived token
            logger.warning("Continuing with short-lived Instagram token")
        
        # Get user profile information
        logger.info(f"Fetching Instagram user profile for user ID: {user_id}")
        profile_url = 'https://graph.instagram.com/me'
        params = {
            'fields': 'id,username,account_type,media_count',
            'access_token': access_token
        }
        
        profile_response = requests.get(profile_url, params=params)
        
        if profile_response.status_code != 200:
            logger.error(
                f"Instagram profile fetch failed with status {profile_response.status_code}: {profile_response.text}"
            )
            
            # Try to parse the error response as JSON
            try:
                error_data = profile_response.json()
                logger.error(f"Instagram profile error details: {error_data}")
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
            except (ValueError, json.JSONDecodeError):
                logger.error("Could not parse Instagram profile error response as JSON")
                error_message = profile_response.text if profile_response.text else f"HTTP {profile_response.status_code}"
                
            # We have the token but couldn't get profile, return what we have
            logger.warning("Using limited profile information due to profile fetch error")
            return {
                'access_token': access_token,
                'user_id': user_id,
                'profile': {'id': user_id},
                'error_fetching_profile': error_message
            }
        
        profile_data = profile_response.json()
        logger.info(f"Successfully fetched Instagram profile for username: {profile_data.get('username')}")
        
        # Build the result object
        result = {
            'access_token': access_token,
            'user_id': user_id,
            'profile': profile_data,
            'name': profile_data.get('username', ''),
            'username': profile_data.get('username', ''),
            'picture': '',  # Instagram Graph API doesn't provide profile picture in basic display API
            'email': f"{profile_data.get('username', '')}@instagram.com"  # Instagram doesn't provide email
        }
        
        return result
    
    except requests.RequestException as e:
        # Network-related error
        logger.exception(f"Network error during Instagram code exchange: {str(e)}")
        raise SocialConnectionError(f"Failed to connect to Instagram API: {str(e)}")
    
    except Exception as e:
        # Any other unexpected error
        logger.exception(f"Unexpected error during Instagram code exchange: {str(e)}")
        raise SocialConnectionError(f"Instagram authentication error: {str(e)}")

def exchange_tiktok_code(code: str, redirect_uri: str = None) -> Dict[str, Any]:
    """
    Exchange the TikTok auth code for an access token.
    
    Args:
        code: Authorization code from TikTok
        redirect_uri: Redirect URI used during authorization
        
    Returns:
        Dict containing the access token and profile information
        
    Raises:
        SocialConnectionError: If the token exchange fails
    """
    logger = logging.getLogger('social')
    
    if not redirect_uri:
        redirect_uri = settings.TIKTOK_REDIRECT_URI
    
    logger.info(f"Exchanging TikTok code for token with redirect URI: {redirect_uri}")
    logger.info(f"Code length: {len(code) if code else 0}")
    
    # Prepare the token request data
    token_url = 'https://open-api.tiktok.com/oauth/access_token/'
    params = {
        'client_key': settings.TIKTOK_CLIENT_KEY,
        'client_secret': settings.TIKTOK_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    
    # Log request data without exposing sensitive information
    logger.info(
        f"TikTok token request data: client_key={settings.TIKTOK_CLIENT_KEY[:5]}..., "
        f"redirect_uri={redirect_uri}, code_length={len(code)}"
    )
    
    try:
        # Execute the token request
        token_response = requests.post(token_url, params=params)
        
        # Check if the request was successful
        if token_response.status_code != 200:
            logger.error(
                f"TikTok token exchange failed with status {token_response.status_code}: {token_response.text}"
            )
            
            # Try to parse the error response as JSON
            try:
                error_data = token_response.json()
                logger.error(f"TikTok error details: {error_data}")
                error_message = (
                    error_data.get('error', {}).get('message', '') or 
                    error_data.get('message', '') or 
                    'Unknown error'
                )
            except (ValueError, json.JSONDecodeError):
                logger.error("Could not parse TikTok error response as JSON")
                error_message = token_response.text if token_response.text else f"HTTP {token_response.status_code}"
            
            raise SocialConnectionError(f"TikTok API error: {error_message}")
        
        # Parse the token response
        token_data = token_response.json()
        
        # TikTok API nests the data in a 'data' key
        data = token_data.get('data', {})
        if not data or token_data.get('message') != 'success':
            logger.error(f"TikTok returned error response: {token_data}")
            error_message = token_data.get('message', 'Unknown error')
            raise SocialConnectionError(f"TikTok API error: {error_message}")
        
        # Extract access token and other data
        access_token = data.get('access_token')
        open_id = data.get('open_id')
        
        if not access_token or not open_id:
            logger.error("TikTok returned no access token or open_id")
            raise SocialConnectionError("TikTok authentication failed: Missing token or open_id")
        
        # Log successful token exchange
        logger.info(
            f"Successfully exchanged TikTok code for token. "
            f"Access token length: {len(access_token)}, "
            f"Open ID: {open_id}"
        )
        
        # Get user profile information
        logger.info(f"Fetching TikTok user profile for open_id: {open_id}")
        
        profile_url = 'https://open-api.tiktok.com/user/info/'
        profile_params = {
            'access_token': access_token,
            'open_id': open_id,
            'fields': 'open_id,union_id,avatar_url,display_name'
        }
        
        try:
            profile_response = requests.get(profile_url, params=profile_params)
            
            if profile_response.status_code != 200:
                logger.error(
                    f"TikTok profile fetch failed with status {profile_response.status_code}: {profile_response.text}"
                )
                
                # Try to parse the error response as JSON
                try:
                    error_data = profile_response.json()
                    logger.error(f"TikTok profile error details: {error_data}")
                    error_message = (
                        error_data.get('error', {}).get('message', '') or 
                        error_data.get('message', '') or 
                        'Unknown error'
                    )
                except (ValueError, json.JSONDecodeError):
                    logger.error("Could not parse TikTok profile error response as JSON")
                    error_message = profile_response.text if profile_response.text else f"HTTP {profile_response.status_code}"
                
                # We have the token but couldn't get profile, return what we have
                logger.warning("Using limited profile information due to profile fetch error")
                return {
                    'access_token': access_token,
                    'open_id': open_id,
                    'profile': {'open_id': open_id},
                    'error_fetching_profile': error_message
                }
            
            profile_data = profile_response.json()
            profile_data = profile_data.get('data', {})
            
            if not profile_data or profile_response.json().get('message') != 'success':
                logger.error(f"TikTok profile API returned error: {profile_response.json()}")
                # Continue with limited information
                profile_data = {'open_id': open_id}
            
            logger.info(f"Successfully fetched TikTok profile for user: {profile_data.get('display_name', 'unknown')}")
            
            # Build the result object
            result = {
                'access_token': access_token,
                'open_id': open_id,
                'profile': profile_data,
                'name': profile_data.get('display_name', ''),
                'username': profile_data.get('display_name', ''),
                'picture': profile_data.get('avatar_url', ''),
                'email': f"{open_id}@tiktok.com"  # TikTok doesn't provide email
            }
            
            return result
            
        except requests.RequestException as e:
            logger.exception(f"Network error during TikTok profile fetch: {str(e)}")
            # Return at least the token information
            return {
                'access_token': access_token,
                'open_id': open_id,
                'profile': {'open_id': open_id},
                'error_fetching_profile': str(e)
            }
    
    except requests.RequestException as e:
        # Network-related error
        logger.exception(f"Network error during TikTok code exchange: {str(e)}")
        raise SocialConnectionError(f"Failed to connect to TikTok API: {str(e)}")
    
    except Exception as e:
        # Any other unexpected error
        logger.exception(f"Unexpected error during TikTok code exchange: {str(e)}")
        raise SocialConnectionError(f"TikTok authentication error: {str(e)}")

def verify_telegram_data(auth_data):
    """
    Verify Telegram login widget data
    https://core.telegram.org/widgets/login#checking-authorization
    """
    try:
        # Get the hash and remove it from the data
        received_hash = auth_data.pop('hash', '')
        auth_string = []
        
        # Sort the remaining fields alphabetically
        for key in sorted(auth_data.keys()):
            if auth_data[key] is not None:
                auth_string.append(f'{key}={auth_data[key]}')
        
        # Join the sorted fields
        auth_string = '\n'.join(auth_string)
        
        # Create a secret key using SHA256
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        
        # Calculate the hash using HMAC-SHA256
        computed_hash = hmac.new(
            secret_key,
            auth_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify the hash
        if computed_hash != received_hash:
            raise SocialConnectionError('Invalid Telegram authentication data')
        
        # Check if the auth data is not expired (default 1 day)
        auth_date = int(auth_data.get('auth_date', 0))
        if time.time() - auth_date > 86400:
            raise SocialConnectionError('Telegram authentication data has expired')
            
        return True
        
    except Exception as e:
        raise SocialConnectionError(f'Telegram verification error: {str(e)}')

def connect_social_account(user, platform, auth_data, business=False):
    """Connect a social media account to a user"""
    platform = platform.lower()
    
    try:
        if platform == 'google':
            tokens = exchange_google_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.google_access_token = tokens.get('access_token')
            user.google_refresh_token = tokens.get('refresh_token')
            if business:
                user.google_business_connected = True
        
        elif platform == 'facebook':
            tokens = exchange_facebook_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.facebook_access_token = tokens.get('access_token')
            if business:
                user.facebook_business_connected = True
        
        elif platform == 'linkedin':
            tokens = exchange_linkedin_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.linkedin_access_token = tokens.get('access_token')
            if business:
                user.linkedin_business_connected = True
        
        elif platform == 'twitter':
            tokens = exchange_twitter_code(
                auth_data.get('code'), 
                auth_data.get('redirect_uri'),
                auth_data.get('code_verifier')
            )
            user.twitter_access_token = tokens.get('access_token')
            if business:
                user.twitter_business_connected = True
        
        elif platform == 'instagram':
            if business:
                # Instagram Business uses Facebook authentication
                tokens = exchange_facebook_code(auth_data.get('code'), auth_data.get('redirect_uri'))
                user.instagram_business_access_token = tokens.get('access_token')
                user.instagram_business_connected = True
            else:
                tokens = exchange_instagram_code(auth_data.get('code'), auth_data.get('redirect_uri'))
                user.instagram_access_token = tokens.get('access_token')
        
        elif platform == 'tiktok':
            tokens = exchange_tiktok_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.tiktok_access_token = tokens.get('access_token')
            if business:
                user.tiktok_business_connected = True
        
        elif platform == 'telegram':
            if verify_telegram_data(auth_data):
                user.telegram_id = auth_data.get('id')
                if business:
                    user.telegram_business_connected = True
        
        else:
            raise ValidationError({'platform': ['Invalid platform specified.']})
        
        user.save()
        return user
        
    except SocialConnectionError as e:
        raise ValidationError({'detail': str(e)})
    except Exception as e:
        raise ValidationError({'detail': f'Failed to connect {platform} account: {str(e)}'})

def fetch_google_user_data(access_token):
    """Fetch Google user profile data"""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to fetch Google user data')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Google API error: {str(e)}')

def fetch_facebook_user_data(access_token):
    """Fetch Facebook user profile and page data"""
    try:
        # Get user profile
        profile = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,name,email,picture',
                'access_token': access_token
            }
        ).json()
        
        # Get user's pages
        pages = requests.get(
            'https://graph.facebook.com/me/accounts',
            params={'access_token': access_token}
        ).json()
        
        return {
            'profile': profile,
            'pages': pages.get('data', [])
        }
    except Exception as e:
        raise SocialConnectionError(f'Facebook API error: {str(e)}')

def fetch_linkedin_user_data(access_token):
    """Fetch LinkedIn user profile and company data"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get basic profile
        profile = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        ).json()
        
        # Get email address
        email = requests.get(
            'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
            headers=headers
        ).json()
        
        # Get company data if available
        companies = requests.get(
            'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee',
            headers=headers
        ).json()
        
        return {
            'profile': profile,
            'email': email.get('elements', [{}])[0].get('handle~', {}).get('emailAddress'),
            'companies': companies.get('elements', [])
        }
    except Exception as e:
        raise SocialConnectionError(f'LinkedIn API error: {str(e)}')

def fetch_twitter_user_data(access_token, access_token_secret):
    """Fetch Twitter user profile data"""
    try:
        auth = tweepy.OAuthHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET
        )
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        # Get user profile
        user = api.verify_credentials()
        
        return {
            'id': user.id_str,
            'username': user.screen_name,
            'name': user.name,
            'profile_image': user.profile_image_url_https,
            'followers_count': user.followers_count,
            'friends_count': user.friends_count,
            'statuses_count': user.statuses_count
        }
    except Exception as e:
        raise SocialConnectionError(f'Twitter API error: {str(e)}')

def fetch_instagram_user_data(access_token):
    """Fetch Instagram user profile data"""
    try:
        # Get user profile
        profile = requests.get(
            'https://graph.instagram.com/me',
            params={
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }
        ).json()
        
        # Get user media
        media = requests.get(
            'https://graph.instagram.com/me/media',
            params={
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink',
                'access_token': access_token
            }
        ).json()
        
        return {
            'profile': profile,
            'recent_media': media.get('data', [])
        }
    except Exception as e:
        raise SocialConnectionError(f'Instagram API error: {str(e)}')

def fetch_tiktok_user_data(access_token, open_id):
    """Fetch TikTok user profile data"""
    try:
        # Get user info
        response = requests.get(
            'https://open-api.tiktok.com/user/info/',
            params={
                'access_token': access_token,
                'open_id': open_id,
                'fields': ['open_id', 'union_id', 'avatar_url', 'display_name', 
                          'bio_description', 'profile_deep_link', 'follower_count', 
                          'following_count', 'likes_count', 'video_count']
            }
        )
        
        if response.status_code != 200:
            raise SocialConnectionError('Failed to fetch TikTok user data')
            
        return response.json().get('data', {})
    except Exception as e:
        raise SocialConnectionError(f'TikTok API error: {str(e)}')

def fetch_telegram_channel_data(chat_id):
    """Fetch Telegram channel data"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Get chat info
        chat_info = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChat',
            params={'chat_id': chat_id}
        ).json()
        
        if not chat_info.get('ok'):
            raise SocialConnectionError('Failed to fetch Telegram channel info')
        
        # Get member count
        member_count = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChatMemberCount',
            params={'chat_id': chat_id}
        ).json()
        
        return {
            'chat': chat_info.get('result', {}),
            'member_count': member_count.get('result', 0)
        }
    except Exception as e:
        raise SocialConnectionError(f'Telegram API error: {str(e)}')

def fetch_youtube_channel_data(access_token, channel_id):
    """Fetch YouTube channel data"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get channel details
        channel_response = requests.get(
            'https://youtube.googleapis.com/youtube/v3/channels',
            params={
                'part': 'snippet,statistics,brandingSettings',
                'id': channel_id
            },
            headers=headers
        ).json()
        
        if 'error' in channel_response:
            raise SocialConnectionError('Failed to fetch YouTube channel data')
            
        channel = channel_response.get('items', [{}])[0]
        
        return {
            'snippet': channel.get('snippet', {}),
            'statistics': channel.get('statistics', {}),
            'branding': channel.get('brandingSettings', {})
        }
    except Exception as e:
        raise SocialConnectionError(f'YouTube API error: {str(e)}')

def update_user_social_data(user, platform, data):
    """Update user's social media data"""
    try:
        if platform == 'google':
            user.email = data.get('email')
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
            user.profile_picture = data.get('picture')
            
        elif platform == 'facebook':
            profile = data.get('profile', {})
            user.facebook_page = f"https://facebook.com/{profile.get('id')}"
            if data.get('pages'):
                page = data['pages'][0]  # Get first page
                user.facebook_page_id = page.get('id')
                user.facebook_page_name = page.get('name')
                user.facebook_page_token = page.get('access_token')
                
        elif platform == 'linkedin':
            profile = data.get('profile', {})
            user.linkedin_profile = f"https://linkedin.com/in/{profile.get('vanityName', '')}"
            if data.get('companies'):
                company = data['companies'][0]  # Get first company
                user.linkedin_company_id = company.get('organizationalTarget')
                user.has_linkedin_company = True
                
        elif platform == 'twitter':
            user.twitter_handle = data.get('username')
            user.twitter_profile_url = f"https://twitter.com/{data.get('username')}"
            user.twitter_followers = data.get('followers_count', 0)
            
        elif platform == 'instagram':
            profile = data.get('profile', {})
            user.instagram_handle = profile.get('username')
            user.instagram_profile_url = f"https://instagram.com/{profile.get('username')}"
            if profile.get('account_type') == 'BUSINESS':
                user.has_instagram_business = True
                
        elif platform == 'tiktok':
            user.tiktok_handle = data.get('display_name')
            user.tiktok_profile_url = data.get('profile_deep_link')
            user.tiktok_followers = data.get('follower_count', 0)
            
        elif platform == 'telegram':
            chat = data.get('chat', {})
            user.telegram_channel_name = chat.get('title')
            user.telegram_subscribers = data.get('member_count', 0)
            
        elif platform == 'youtube':
            snippet = data.get('snippet', {})
            stats = data.get('statistics', {})
            user.youtube_channel_title = snippet.get('title')
            user.youtube_channel = f"https://youtube.com/channel/{snippet.get('channelId')}"
            user.youtube_subscribers = int(stats.get('subscriberCount', 0))
            
        user.metrics_last_updated = timezone.now()
        user.update_last_sync(platform)
        user.save()
        
    except Exception as e:
        raise SocialConnectionError(f'Failed to update user data: {str(e)}')

def exchange_code_for_token(platform: str, code: str, redirect_uri: str, code_verifier: str = None) -> Dict:
    """Exchange authorization code for access token."""
    config = get_platform_config(platform)
    
    data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    if code_verifier:
        data['code_verifier'] = code_verifier
    
    response = requests.post(config['token_url'], data=data)
    if not response.ok:
        raise TokenExchangeError(f"Failed to exchange code for {platform}: {response.text}")
    
    return response.json()

def connect_google_account(user, code: str, session_key: str, state: str) -> Dict:
    """Connect Google account."""
    verify_oauth_state(state)
    code_verifier = get_stored_code_verifier(state)
    
    token_data = exchange_code_for_token('google', code, settings.GOOGLE_REDIRECT_URI, code_verifier)
    
    # Get user profile
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
    if not response.ok:
        raise ProfileFetchError("Failed to fetch Google profile")
    
    profile = response.json()
    
    # Update user
    user.google_id = profile['id']
    user.google_access_token = token_data['access_token']
    if 'refresh_token' in token_data:
        user.google_refresh_token = token_data['refresh_token']
    user.save()
    
    return {
        'success': True,
        'platform': 'google',
        'profile': profile
    }

def connect_facebook_account(user, code: str, session_key: str, state: str) -> Dict:
    """Connect Facebook account."""
    verify_oauth_state(state)
    
    token_data = exchange_code_for_token('facebook', code, settings.FACEBOOK_REDIRECT_URI)
    
    # Get user profile
    params = {
        'fields': 'id,name,email',
        'access_token': token_data['access_token']
    }
    response = requests.get('https://graph.facebook.com/v12.0/me', params=params)
    if not response.ok:
        raise ProfileFetchError("Failed to fetch Facebook profile")
    
    profile = response.json()
    
    # Update user
    user.facebook_id = profile['id']
    user.facebook_access_token = token_data['access_token']
    user.save()
    
    return {
        'success': True,
        'platform': 'facebook',
        'profile': profile
    }

def connect_linkedin_account(user, code: str, session_key: str = None, state: str = None) -> Dict:
    """Connect LinkedIn account."""
    if state:
        verify_oauth_state(state)
    
    token_data = exchange_code_for_token('linkedin', code, settings.LINKEDIN_REDIRECT_URI)
    
    # Get profile data from userinfo endpoint (OpenID Connect)
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    profile_response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
    
    if not profile_response.ok:
        # Fallback to standard API
        profile_response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
        if not profile_response.ok:
            raise ProfileFetchError(f"Failed to fetch LinkedIn profile: {profile_response.text}")
    
    profile = profile_response.json()
    
    # Update user
    user.linkedin_id = profile.get('id') or profile.get('sub')  # Handle both API and OpenID responses
    user.linkedin_access_token = token_data['access_token']
    if 'refresh_token' in token_data:
        user.linkedin_refresh_token = token_data['refresh_token']
    user.save()
    
    return {
        'success': True,
        'platform': 'linkedin',
        'profile': profile
    }

def connect_twitter_account(user, code: str, state: str, session_key: str = None, code_verifier: str = None) -> Dict:
    """Connect Twitter account."""
    verify_oauth_state(state)
    
    # Use provided code_verifier or get it from storage
    if not code_verifier:
        code_verifier = get_stored_code_verifier(state)
        
    if not code_verifier:
        raise PKCEVerificationError("Missing PKCE code_verifier for Twitter OAuth")
    
    token_data = exchange_code_for_token('twitter', code, settings.TWITTER_REDIRECT_URI, code_verifier)
    
    # Get user profile
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    response = requests.get('https://api.twitter.com/2/users/me', headers=headers)
    if not response.ok:
        raise ProfileFetchError("Failed to fetch Twitter profile")
    
    profile = response.json()
    
    # Update user
    user.twitter_id = profile['data']['id']
    user.twitter_access_token = token_data['access_token']
    if 'refresh_token' in token_data:
        user.twitter_refresh_token = token_data['refresh_token']
    user.save()
    
    return {
        'success': True,
        'platform': 'twitter',
        'profile': profile['data']
    }

def connect_instagram_account(user, code: str, session_key: str, state: str) -> Dict:
    """Connect Instagram account."""
    verify_oauth_state(state)
    
    token_data = exchange_code_for_token('instagram', code, settings.INSTAGRAM_REDIRECT_URI)
    
    # Get user profile
    params = {
        'fields': 'id,username',
        'access_token': token_data['access_token']
    }
    response = requests.get('https://graph.instagram.com/me', params=params)
    if not response.ok:
        raise ProfileFetchError("Failed to fetch Instagram profile")
    
    profile = response.json()
    
    # Update user
    user.instagram_id = profile['id']
    user.instagram_access_token = token_data['access_token']
    user.save()
    
    return {
        'success': True,
        'platform': 'instagram',
        'profile': profile
    }

def connect_tiktok_account(user, code: str, session_key: str, state: str) -> Dict:
    """Connect TikTok account."""
    verify_oauth_state(state)
    code_verifier = get_stored_code_verifier(state)
    
    token_data = exchange_code_for_token('tiktok', code, settings.TIKTOK_REDIRECT_URI, code_verifier)
    
    # Get user profile
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    response = requests.get('https://open.tiktokapis.com/v2/user/info/', headers=headers)
    if not response.ok:
        raise ProfileFetchError("Failed to fetch TikTok profile")
    
    profile = response.json()
    
    # Update user
    user.tiktok_id = profile['data']['user']['id']
    user.tiktok_access_token = token_data['access_token']
    user.save()
    
    return {
        'success': True,
        'platform': 'tiktok',
        'profile': profile['data']['user']
    }

def connect_telegram_account(user, code: str, session_key: str, state: str) -> Dict:
    """Connect Telegram account."""
    verify_oauth_state(state)
    
    # Telegram uses a different authentication flow through their Bot API
    # The code parameter here is actually the user's Telegram ID
    user.telegram_id = code
    user.save()
    
    return {
        'success': True,
        'platform': 'telegram',
        'profile': {'id': code}
    } 
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
import datetime
from datetime import timedelta
import os

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

def exchange_facebook_code(code: str, redirect_uri: str = None) -> Dict[str, Any]:
    """
    Exchange Facebook authorization code for an access token.
    
    Args:
        code: The authorization code received from Facebook
        redirect_uri: The redirect URI used during authorization
        
    Returns:
        Dictionary containing access token and other token data
        
    Raises:
        SocialConnectionError: If there's an error exchanging the code for a token
    """
    logger = logging.getLogger('social')
    logger.info("===== Exchanging Facebook code for token =====")
    
    # Use configured redirect URI if none provided
    if not redirect_uri:
        redirect_uri = settings.FACEBOOK_REDIRECT_URI
    
    logger.info(f"Using redirect URI: {redirect_uri}")
    logger.info(f"Code length: {len(code) if code else 'None'}")
    
    # Validate inputs
    if not code:
        logger.error("Missing code parameter for Facebook OAuth")
        raise SocialConnectionError("Missing authorization code")
        
    if not settings.FACEBOOK_CLIENT_ID or not settings.FACEBOOK_CLIENT_SECRET:
        logger.error("Missing Facebook client credentials in settings")
        raise SocialConnectionError("Facebook API credentials not configured")
    
    # Build request data
    request_data = {
        'client_id': settings.FACEBOOK_CLIENT_ID,
        'client_secret': settings.FACEBOOK_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    # Log request details (without exposing sensitive data)
    logger.info(f"Token request data (client_id and redirect_uri): {settings.FACEBOOK_CLIENT_ID}, {redirect_uri}")
    
    try:
        # Exchange code for token
        token_url = 'https://graph.facebook.com/v17.0/oauth/access_token'
        logger.info(f"Making token request to: {token_url}")
        
        response = requests.get(
            token_url,
            params=request_data,
            timeout=10
        )
        
        # Check if response is successful
        if response.status_code != 200:
            logger.error(f"Token request failed: Status {response.status_code}, Response: {response.text}")
            
            # Try to parse the error response as JSON
            try:
                error_data = response.json()
                logger.error(f"Facebook error details: {error_data}")
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                error_type = error_data.get('error', {}).get('type', 'unknown_error')
                error_code = error_data.get('error', {}).get('code', 0)
                logger.error(f"Facebook error type: {error_type}, code: {error_code}, message: {error_message}")
            except (ValueError, json.JSONDecodeError, AttributeError):
                logger.error("Could not parse Facebook error response as JSON")
                error_message = response.text if response.text else f"HTTP {response.status_code}"
            
            raise SocialConnectionError(f"Facebook API error: {error_message}")
        
        # Parse response
        token_data = response.json()
        
        # Verify token data
        if 'access_token' not in token_data:
            logger.error(f"Token response missing access_token: {token_data}")
            raise SocialConnectionError("Facebook token response missing access_token")
        
        logger.info(
            f"Successfully exchanged code for Facebook token. "
            f"Token type: {token_data.get('token_type', 'unknown')}, "
            f"Access token length: {len(token_data.get('access_token', ''))}"
        )
        
        if 'expires_in' in token_data:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=int(token_data['expires_in']))
            logger.info(f"Token expires in {token_data['expires_in']} seconds (at {expiry_time.isoformat()})")
        
        # Get user profile with the token
        try:
            logger.info("Fetching Facebook user profile with the access token")
            profile_data = get_facebook_profile(token_data['access_token'])
            
            # Add profile data to the result
            result = {
                'access_token': token_data['access_token'],
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type'),
                'id': profile_data.get('id'),
                'name': profile_data.get('name'),
                'email': profile_data.get('email'),
                'picture': profile_data.get('picture'),
                'profile': profile_data
            }
            
            logger.info(f"Successfully retrieved Facebook profile for user: {profile_data.get('name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Facebook profile, returning token only: {e}")
            # Return token data even if profile fetch fails
            return {
                'access_token': token_data['access_token'],
                'expires_in': token_data.get('expires_in'),
                'token_type': token_data.get('token_type')
            }
            
    except requests.RequestException as e:
        logger.exception(f"Request error during Facebook token exchange: {e}")
        raise SocialConnectionError(f"Network error during Facebook token exchange: {str(e)}")
    except ValueError as e:
        logger.exception(f"JSON parsing error during Facebook token exchange: {e}")
        raise SocialConnectionError(f"Failed to parse Facebook token response: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error during Facebook token exchange: {e}")
        raise SocialConnectionError(f"Unexpected error during Facebook token exchange: {str(e)}")

def get_facebook_profile(access_token: str) -> Dict[str, Any]:
    """
    Fetch the user's Facebook profile data using the access token.
    
    Args:
        access_token: Facebook access token
        
    Returns:
        Dictionary containing user profile data
        
    Raises:
        SocialConnectionError: If there's an error fetching the profile
    """
    logger = logging.getLogger('social')
    logger.info("===== Fetching Facebook profile =====")
    
    try:
        # Request user profile data with fields we want
        fields = "id,name,email,picture.type(large),first_name,last_name,link"
        profile_url = f"https://graph.facebook.com/v17.0/me?fields={fields}&access_token={access_token}"
        
        logger.info(f"Making profile request to Facebook Graph API")
        
        response = requests.get(profile_url, timeout=10)
        
        # Check if response is successful
        if response.status_code != 200:
            logger.error(f"Profile request failed: Status {response.status_code}, Response: {response.text}")
            
            # Try to parse the error response as JSON
            try:
                error_data = response.json()
                logger.error(f"Facebook profile error details: {error_data}")
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                error_type = error_data.get('error', {}).get('type', 'unknown_error')
                error_code = error_data.get('error', {}).get('code', 0)
                logger.error(f"Facebook profile error type: {error_type}, code: {error_code}, message: {error_message}")
            except (ValueError, json.JSONDecodeError, AttributeError):
                logger.error("Could not parse Facebook profile error response as JSON")
                error_message = response.text if response.text else f"HTTP {response.status_code}"
            
            raise SocialConnectionError(f"Facebook profile API error: {error_message}")
        
        # Parse response
        profile_data = response.json()
        
        # Check for required profile fields
        if 'id' not in profile_data:
            logger.error(f"Profile response missing user ID: {profile_data}")
            raise SocialConnectionError("Facebook profile response missing user ID")
        
        # Extract picture URL if available
        if 'picture' in profile_data and 'data' in profile_data['picture'] and 'url' in profile_data['picture']['data']:
            profile_data['picture'] = profile_data['picture']['data']['url']
            logger.info(f"Extracted profile picture URL from response")
        else:
            logger.warning("No profile picture found in Facebook response")
        
        # Log profile data (excluding sensitive information)
        safe_profile_data = {
            'id': profile_data.get('id'),
            'name': profile_data.get('name'),
            'has_email': 'email' in profile_data,
            'has_picture': 'picture' in profile_data and isinstance(profile_data['picture'], str)
        }
        logger.info(f"Facebook profile data received: {safe_profile_data}")
        
        return profile_data
        
    except requests.RequestException as e:
        logger.exception(f"Request error during Facebook profile fetch: {e}")
        raise SocialConnectionError(f"Network error fetching Facebook profile: {str(e)}")
    except ValueError as e:
        logger.exception(f"JSON parsing error during Facebook profile fetch: {e}")
        raise SocialConnectionError(f"Failed to parse Facebook profile response: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error during Facebook profile fetch: {e}")
        raise SocialConnectionError(f"Unexpected error during Facebook profile fetch: {str(e)}")

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
        logger.info("===== Exchanging LinkedIn code =====")
        logger.info(f"Exchanging LinkedIn code. Redirect URI: {redirect_uri or settings.LINKEDIN_REDIRECT_URI}")
        logger.info(f"LinkedIn client ID: {settings.LINKEDIN_CLIENT_ID[:5]}... (truncated)")
        logger.info(f"Code length: {len(code) if code else 'None'}")
        
        # Ensure we have proper values
        if not code:
            logger.error("Missing code parameter for LinkedIn OAuth")
            raise SocialConnectionError("Missing authorization code")
            
        if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
            logger.error("Missing LinkedIn client credentials in settings")
            raise SocialConnectionError("LinkedIn API credentials not configured")
        
        # Log all settings to help debug production issues
        logger.info(f"LinkedIn settings: REDIRECT_URI={settings.LINKEDIN_REDIRECT_URI}")
        # If there's a separate callback URL setting, log that too
        if hasattr(settings, 'LINKEDIN_CALLBACK_URL'):
            logger.info(f"LinkedIn callback URL from settings: {settings.LINKEDIN_CALLBACK_URL}")
        
        # Make the token request
        logger.info("Making request to LinkedIn token endpoint")
        try:
            response = requests.post(
                'https://www.linkedin.com/oauth/v2/accessToken',
                data=data,
                timeout=10  # Add a timeout to prevent hanging requests
            )
            logger.info(f"LinkedIn token response received. Status: {response.status_code}")
        except requests.RequestException as req_err:
            logger.error(f"Network error during LinkedIn token request: {str(req_err)}")
            raise SocialConnectionError(f"Network error during LinkedIn token request: {str(req_err)}")
        
        # Check for errors and log response
        if response.status_code != 200:
            error_msg = f'Failed to exchange LinkedIn auth code: Status {response.status_code}, Response: {response.text}'
            logger.error(error_msg)
            
            # Try to parse the error response
            try:
                error_data = response.json()
                logger.error(f"LinkedIn API error details: {error_data}")
                # Extract specific error info if available
                error_description = error_data.get('error_description', 'Unknown error')
                error_type = error_data.get('error', 'unknown_error')
                detailed_error = f"{error_type}: {error_description}"
                raise SocialConnectionError(detailed_error)
            except (ValueError, json.JSONDecodeError):
                logger.error("Could not parse LinkedIn error response as JSON")
                raise SocialConnectionError(error_msg)
            except Exception as json_err:
                logger.error(f"Error parsing LinkedIn error response: {str(json_err)}")
                raise SocialConnectionError(error_msg)
                
            raise SocialConnectionError(error_msg)
            
        # Parse and return the token response
        try:
            token_data = response.json()
            
            # Validate token data
            if 'access_token' not in token_data:
                logger.error("LinkedIn response did not contain access_token")
                raise SocialConnectionError("LinkedIn did not return an access token")
                
            logger.info(f"Successfully exchanged LinkedIn code for token. Token type: {token_data.get('token_type')}")
            logger.info(f"Access token length: {len(token_data.get('access_token', ''))}")
            
            # If the response includes a refresh token, log that too
            if 'refresh_token' in token_data:
                logger.info("Refresh token received from LinkedIn")
            
            # Optionally fetch profile data to ensure token works
            try:
                headers = {'Authorization': f"Bearer {token_data['access_token']}"}
                profile_response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers, timeout=10)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    logger.info(f"Successfully fetched LinkedIn profile. User ID: {profile_data.get('sub', 'N/A')}")
                    token_data['profile'] = profile_data
                else:
                    logger.warning(f"Could not fetch LinkedIn profile: Status {profile_response.status_code}")
                    # We'll return what we have even without profile data
            except Exception as profile_err:
                logger.warning(f"Error fetching LinkedIn profile: {str(profile_err)}")
                # Continue without profile data
            
            return token_data
            
        except (ValueError, json.JSONDecodeError) as json_err:
            logger.error(f"Failed to parse LinkedIn token response as JSON: {str(json_err)}")
            logger.error(f"Response text: {response.text[:500]}")
            raise SocialConnectionError("Invalid response format from LinkedIn")
            
    except requests.RequestException as e:
        logger.error(f'LinkedIn OAuth network error: {str(e)}')
        if hasattr(e, 'response') and e.response:
            logger.error(f'LinkedIn response status: {e.response.status_code}')
            logger.error(f'LinkedIn response content: {e.response.text}')
        raise SocialConnectionError(f'LinkedIn OAuth request error: {str(e)}')
    except SocialConnectionError:
        # Re-raise SocialConnectionError to preserve the message
        raise
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

def get_instagram_profile(access_token: str) -> Dict[str, Any]:
    """
    Fetch the user's Instagram profile data using the access token.
    
    Args:
        access_token: Instagram access token
        
    Returns:
        Dictionary containing user profile data
        
    Raises:
        SocialConnectionError: If there's an error fetching the profile
    """
    logger = logging.getLogger('social')
    logger.info("===== Fetching Instagram profile =====")
    
    try:
        # Request user profile data with fields we want
        fields = "id,username,account_type,media_count"
        profile_url = f"https://graph.instagram.com/me?fields={fields}&access_token={access_token}"
        
        logger.info(f"Making profile request to Instagram Graph API")
        
        response = requests.get(profile_url, timeout=10)
        
        # Check if response is successful
        if response.status_code != 200:
            logger.error(f"Profile request failed: Status {response.status_code}, Response: {response.text}")
            
            # Try to parse the error response as JSON
            try:
                error_data = response.json()
                logger.error(f"Instagram profile error details: {error_data}")
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                error_type = error_data.get('error', {}).get('type', 'unknown_error')
                error_code = error_data.get('error', {}).get('code', 0)
                logger.error(f"Instagram profile error type: {error_type}, code: {error_code}, message: {error_message}")
            except (ValueError, json.JSONDecodeError, AttributeError):
                logger.error("Could not parse Instagram profile error response as JSON")
                error_message = response.text if response.text else f"HTTP {response.status_code}"
            
            raise SocialConnectionError(f"Instagram profile API error: {error_message}")
        
        # Parse response
        profile_data = response.json()
        
        # Check for required profile fields
        if 'id' not in profile_data:
            logger.error(f"Profile response missing user ID: {profile_data}")
            raise SocialConnectionError("Instagram profile response missing user ID")
        
        # Log profile data (excluding sensitive information)
        safe_profile_data = {
            'id': profile_data.get('id'),
            'username': profile_data.get('username'),
            'account_type': profile_data.get('account_type'),
            'media_count': profile_data.get('media_count')
        }
        logger.info(f"Instagram profile data received: {safe_profile_data}")
        
        return profile_data
        
    except requests.RequestException as e:
        logger.exception(f"Request error during Instagram profile fetch: {e}")
        raise SocialConnectionError(f"Network error fetching Instagram profile: {str(e)}")
    except ValueError as e:
        logger.exception(f"JSON parsing error during Instagram profile fetch: {e}")
        raise SocialConnectionError(f"Failed to parse Instagram profile response: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error during Instagram profile fetch: {e}")
        raise SocialConnectionError(f"Unexpected error during Instagram profile fetch: {str(e)}")

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
        
        profile_url = 'https://open-api.tiktokapis.com/v2/user/info/'
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

def verify_telegram_data(auth_data: Dict) -> bool:
    """
    Verify the data received from the Telegram Login Widget.
    
    Checks that:
    1. The auth_date is recent (prevent replay attacks)
    2. The data hash is valid (verify authenticity)
    
    Args:
        auth_data: Dictionary containing Telegram login widget data
            - id: User's Telegram ID
            - first_name: User's first name
            - last_name: User's last name (optional)
            - username: User's username (optional)
            - photo_url: URL of user's profile photo (optional)
            - auth_date: Authentication date as Unix time
            - hash: HMAC-SHA-256 signature of the data
            
    Returns:
        bool: True if verification passes
        
    Raises:
        SocialConnectionError: If verification fails
    """
    logger = logging.getLogger('social')
    
    # Check for required fields
    required_fields = ['id', 'auth_date', 'hash']
    for field in required_fields:
        if field not in auth_data:
            logger.error(f"Missing required field '{field}' in Telegram auth data")
            raise SocialConnectionError(f"Missing required field '{field}' in Telegram auth data")
    
    # Get Telegram Bot token from settings or environment
    from django.conf import settings
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', os.environ.get('TELEGRAM_BOT_TOKEN'))
    
    if not bot_token:
        logger.error("Telegram Bot token is not configured")
        raise SocialConnectionError("Telegram Bot token is not configured")
    
    # Check auth_date is recent (within last 24 hours)
    auth_date = int(auth_data['auth_date'])
    now = int(time.time())
    if now - auth_date > 86400:  # 24 hours in seconds
        logger.error(f"Telegram auth_date is too old: {auth_date} (current time: {now})")
        raise SocialConnectionError("Telegram authentication has expired")
    
    # Verify data hash
    received_hash = auth_data['hash']
    
    # Remove hash from data_check_string
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        if key != 'hash':
            data_check_arr.append(f"{key}={value}")
    data_check_string = '\n'.join(data_check_arr)
    
    # Create secret key from bot token
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Compute signature
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Compare received hash with computed hash
    if received_hash != computed_hash:
        logger.error("Telegram data signature verification failed")
        raise SocialConnectionError("Invalid Telegram authentication data")
    
    logger.info(f"Telegram auth data successfully verified for user {auth_data['id']}")
    return True

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

def connect_facebook_account(user: 'User', code: str, state: str = None, session_key: str = None) -> Dict[str, Any]:
    """
    Connect a Facebook account to a user's profile.
    
    Args:
        user: The User object to connect the Facebook account to
        code: The authorization code received from Facebook
        state: The state parameter used during authorization
        session_key: The user's session key for storing session-specific data
        
    Returns:
        Dictionary containing token and profile data
        
    Raises:
        StateVerificationError: If state verification fails
        TokenExchangeError: If token exchange fails
        ProfileFetchError: If profile fetching fails
        SocialConnectionError: For other Facebook connection errors
    """
    logger = logging.getLogger('social')
    logger.info(f"===== Connecting Facebook account for user {user.username} =====")
    
    try:
        # Exchange code for token
        redirect_uri = settings.FACEBOOK_REDIRECT_URI
        token_data = exchange_facebook_code(code, redirect_uri)
        
        if not token_data or 'access_token' not in token_data:
            logger.error("Failed to exchange Facebook code for token")
            raise TokenExchangeError("Failed to exchange Facebook code for token")
        
        # Extract profile data
        facebook_id = token_data.get('id')
        name = token_data.get('name')
        email = token_data.get('email')
        picture_url = token_data.get('picture')
        
        # If we don't have an ID, try to get the profile again
        if not facebook_id:
            logger.warning("Facebook ID not found in token data, fetching profile separately")
            try:
                profile_data = get_facebook_profile(token_data['access_token'])
                facebook_id = profile_data.get('id')
                name = profile_data.get('name')
                email = profile_data.get('email')
                picture_url = profile_data.get('picture')
                
                # Update token_data with profile data
                token_data.update(profile_data)
            except Exception as e:
                logger.error(f"Error fetching Facebook profile: {e}")
                raise ProfileFetchError(f"Failed to fetch Facebook profile: {e}")
        
        if not facebook_id:
            logger.error("Facebook ID not found in profile data")
            raise ProfileFetchError("Could not retrieve Facebook user ID")
        
        # Check if this Facebook account is already connected to another user
        try:
            existing_connection = SocialAccount.objects.filter(
                provider='facebook',
                provider_id=facebook_id
            ).exclude(user=user).first()
            
            if existing_connection:
                logger.error(f"Facebook account already connected to another user: {existing_connection.user.username}")
                raise SocialConnectionError("This Facebook account is already connected to another user")
        except Exception as e:
            logger.warning(f"Error checking existing Facebook connections: {e}")
        
        # Get or create social account
        try:
            social_account, created = SocialAccount.objects.get_or_create(
                user=user,
                provider='facebook',
                provider_id=facebook_id,
                defaults={
                    'extra_data': {
                        'access_token': token_data['access_token'],
                        'token_type': token_data.get('token_type'),
                        'expires_in': token_data.get('expires_in'),
                        'name': name,
                        'email': email,
                        'picture': picture_url
                    }
                }
            )
            
            if not created:
                # Update existing account
                social_account.extra_data = {
                    'access_token': token_data['access_token'],
                    'token_type': token_data.get('token_type'),
                    'expires_in': token_data.get('expires_in'),
                    'name': name,
                    'email': email,
                    'picture': picture_url
                }
                social_account.save()
                logger.info(f"Updated existing Facebook account for user {user.username}")
            else:
                logger.info(f"Created new Facebook account for user {user.username}")
                
            # Update user profile if email is provided and user doesn't have one
            if email and not user.email:
                user.email = email
                user.save(update_fields=['email'])
                logger.info(f"Updated user email to {email}")
            
            # Return account data
            result = {
                'provider': 'facebook',
                'provider_id': facebook_id,
                'name': name,
                'email': email,
                'picture': picture_url,
                'access_token': token_data['access_token'],
                'token_type': token_data.get('token_type'),
                'expires_in': token_data.get('expires_in'),
            }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error saving Facebook account: {e}")
            raise SocialConnectionError(f"Failed to save Facebook account: {e}")
            
    except StateVerificationError as e:
        # Re-raise state verification errors
        raise
    except TokenExchangeError as e:
        # Re-raise token exchange errors
        raise
    except ProfileFetchError as e:
        # Re-raise profile fetch errors
        raise
    except SocialConnectionError as e:
        # Re-raise social connection errors
        raise
    except Exception as e:
        logger.exception(f"Unexpected error connecting Facebook account: {e}")
        raise SocialConnectionError(f"Unexpected error connecting Facebook account: {e}")

def connect_linkedin_account(user, code: str, state: str = None, session_key: str = None) -> Dict:
    """
    Connect a LinkedIn account to a user's profile.
    
    Args:
        user: The User object to connect the LinkedIn account to
        code: The authorization code received from LinkedIn
        state: The state parameter used during authorization
        session_key: The user's session key for storing session-specific data
        
    Returns:
        Dictionary containing token and profile data
        
    Raises:
        StateVerificationError: If state verification fails
        TokenExchangeError: If token exchange fails
        ProfileFetchError: If profile fetching fails
        SocialConnectionError: For other LinkedIn connection errors
    """
    logger = logging.getLogger('social')
    logger.info(f"===== Connecting LinkedIn account for user {user.username} =====")
    
    try:
        # Verify state if provided
        if state:
            from ..utils.oauth import verify_oauth_state
            try:
                verify_oauth_state(state)
                logger.info("LinkedIn state verification successful")
            except ValueError as e:
                logger.error(f"LinkedIn state verification failed: {str(e)}")
                raise StateVerificationError(f"LinkedIn state verification failed: {str(e)}")
        
        # Exchange code for token
        redirect_uri = settings.LINKEDIN_REDIRECT_URI
        token_data = exchange_linkedin_code(code, redirect_uri)
        
        if not token_data or 'access_token' not in token_data:
            logger.error("Failed to exchange LinkedIn code for token")
            raise TokenExchangeError("Failed to exchange LinkedIn code for token")
        
        # Get the user profile
        profile_data = {}
        if 'profile' in token_data:
            profile_data = token_data['profile']
        else:
            try:
                headers = {'Authorization': f"Bearer {token_data['access_token']}"}
                profile_response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
                
                if not profile_response.ok:
                    logger.error(f"Failed to fetch LinkedIn profile: Status {profile_response.status_code}, {profile_response.text}")
                    raise ProfileFetchError(f"Failed to fetch LinkedIn profile: {profile_response.text}")
                
                profile_data = profile_response.json()
                logger.info(f"Successfully fetched LinkedIn profile with ID: {profile_data.get('sub')}")
            except requests.RequestException as e:
                logger.error(f"Network error fetching LinkedIn profile: {str(e)}")
                raise ProfileFetchError(f"Network error fetching LinkedIn profile: {str(e)}")
            except ValueError as e:
                logger.error(f"JSON parsing error fetching LinkedIn profile: {str(e)}")
                raise ProfileFetchError(f"Failed to parse LinkedIn profile response: {str(e)}")
        
        # Extract profile information
        linkedin_id = profile_data.get('sub')
        name = profile_data.get('name', '')
        email = profile_data.get('email', '')
        picture_url = profile_data.get('picture', '')
        
        if not linkedin_id:
            logger.error("LinkedIn ID (sub) not found in profile data")
            raise ProfileFetchError("Could not retrieve LinkedIn user ID")
        
        # Check if this LinkedIn account is already connected to another user
        try:
            from ..models import SocialAccount
            existing_connection = SocialAccount.objects.filter(
                provider='linkedin',
                provider_id=linkedin_id
            ).exclude(user=user).first()
            
            if existing_connection:
                logger.error(f"LinkedIn account already connected to another user: {existing_connection.user.username}")
                raise SocialConnectionError("This LinkedIn account is already connected to another user")
        except Exception as e:
            logger.warning(f"Error checking existing LinkedIn connections: {e}")
        
        # Get or create social account
        try:
            social_account, created = SocialAccount.objects.get_or_create(
                user=user,
                provider='linkedin',
                provider_id=linkedin_id,
                defaults={
                    'extra_data': {
                        'access_token': token_data['access_token'],
                        'token_type': token_data.get('token_type'),
                        'expires_in': token_data.get('expires_in'),
                        'name': name,
                        'email': email,
                        'picture': picture_url
                    }
                }
            )
            
            if not created:
                # Update existing account
                social_account.extra_data = {
                    'access_token': token_data['access_token'],
                    'token_type': token_data.get('token_type'),
                    'expires_in': token_data.get('expires_in'),
                    'name': name,
                    'email': email,
                    'picture': picture_url
                }
                social_account.save()
                logger.info(f"Updated existing LinkedIn account for user {user.username}")
            else:
                logger.info(f"Created new LinkedIn account for user {user.username}")
            
            # Update user model fields
            user.linkedin_id = linkedin_id
            user.linkedin_access_token = token_data['access_token']
            if 'expires_in' in token_data:
                expires_at = timezone.now() + timedelta(seconds=int(token_data['expires_in']))
                user.linkedin_token_expires_at = expires_at
            
            # Update user email if provided and user doesn't have one
            if email and not user.email:
                user.email = email
            
            user.save()
            logger.info(f"Updated user with LinkedIn data: ID={linkedin_id}")
            
            # Return account data
            result = {
                'success': True,
                'platform': 'linkedin',
                'profile': {
                    'id': linkedin_id,
                    'name': name,
                    'email': email,
                    'picture': picture_url
                }
            }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error saving LinkedIn account: {e}")
            raise SocialConnectionError(f"Failed to save LinkedIn account: {e}")
    
    except StateVerificationError:
        # Re-raise state verification errors
        raise
    except TokenExchangeError:
        # Re-raise token exchange errors
        raise
    except ProfileFetchError:
        # Re-raise profile fetch errors
        raise
    except SocialConnectionError:
        # Re-raise social connection errors
        raise
    except Exception as e:
        logger.exception(f"Unexpected error connecting LinkedIn account: {e}")
        raise SocialConnectionError(f"Unexpected error connecting LinkedIn account: {e}")

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

def connect_instagram_account(user: 'User', code: str, state: str = None, session_key: str = None) -> Dict[str, Any]:
    """
    Connect an Instagram account to a user's profile.
    
    Args:
        user: The User object to connect the Instagram account to
        code: The authorization code received from Instagram
        state: The state parameter used during authorization
        session_key: The user's session key for storing session-specific data
        
    Returns:
        Dictionary containing token and profile data
        
    Raises:
        StateVerificationError: If state verification fails
        TokenExchangeError: If token exchange fails
        ProfileFetchError: If profile fetching fails
        SocialConnectionError: For other Instagram connection errors
    """
    logger = logging.getLogger('social')
    logger.info(f"===== Connecting Instagram account for user {user.username} =====")
    
    try:
        # Exchange code for token
        redirect_uri = settings.INSTAGRAM_REDIRECT_URI
        token_data = exchange_instagram_code(code, redirect_uri)
        
        if not token_data or 'access_token' not in token_data:
            logger.error("Failed to exchange Instagram code for token")
            raise TokenExchangeError("Failed to exchange Instagram code for token")
        
        # Extract profile data
        instagram_id = token_data.get('id')
        username = token_data.get('username')
        picture_url = token_data.get('picture')
        
        # If we don't have an ID, try to get the profile again
        if not instagram_id:
            logger.warning("Instagram ID not found in token data, fetching profile separately")
            try:
                profile_data = get_instagram_profile(token_data['access_token'])
                instagram_id = profile_data.get('id')
                username = profile_data.get('username')
                picture_url = profile_data.get('profile_pic_url') or profile_data.get('picture')
                
                # Update token_data with profile data
                token_data.update(profile_data)
            except Exception as e:
                logger.error(f"Error fetching Instagram profile: {e}")
                raise ProfileFetchError(f"Failed to fetch Instagram profile: {e}")
        
        if not instagram_id:
            logger.error("Instagram ID not found in profile data")
            raise ProfileFetchError("Could not retrieve Instagram user ID")
        
        # Check if this Instagram account is already connected to another user
        try:
            existing_connection = SocialAccount.objects.filter(
                provider='instagram',
                provider_id=instagram_id
            ).exclude(user=user).first()
            
            if existing_connection:
                logger.error(f"Instagram account already connected to another user: {existing_connection.user.username}")
                raise SocialConnectionError("This Instagram account is already connected to another user")
        except Exception as e:
            logger.warning(f"Error checking existing Instagram connections: {e}")
        
        # Get or create social account
        try:
            social_account, created = SocialAccount.objects.get_or_create(
                user=user,
                provider='instagram',
                provider_id=instagram_id,
                defaults={
                    'extra_data': {
                        'access_token': token_data['access_token'],
                        'token_type': token_data.get('token_type'),
                        'expires_in': token_data.get('expires_in'),
                        'username': username,
                        'picture': picture_url
                    }
                }
            )
            
            if not created:
                # Update existing account
                social_account.extra_data = {
                    'access_token': token_data['access_token'],
                    'token_type': token_data.get('token_type'),
                    'expires_in': token_data.get('expires_in'),
                    'username': username,
                    'picture': picture_url
                }
                social_account.save()
                logger.info(f"Updated existing Instagram account for user {user.username}")
            else:
                logger.info(f"Created new Instagram account for user {user.username}")
            
            # Update user model fields
            user.instagram_id = instagram_id
            user.instagram_handle = username
            user.instagram_access_token = token_data['access_token']
            user.instagram_profile_url = f"https://instagram.com/{username}" if username else None
            
            # Set token expiry if available
            if 'expires_in' in token_data:
                expiry = timezone.now() + timedelta(seconds=int(token_data['expires_in']))
                user.instagram_token_expiry = expiry
                
            user.save()
            logger.info(f"Updated user model with Instagram account details")
            
            # Return account data
            result = {
                'provider': 'instagram',
                'provider_id': instagram_id,
                'username': username,
                'name': token_data.get('full_name', ''),
                'picture': picture_url,
                'access_token': token_data['access_token'],
                'token_type': token_data.get('token_type'),
                'expires_in': token_data.get('expires_in'),
            }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error saving Instagram account: {e}")
            raise SocialConnectionError(f"Failed to save Instagram account: {e}")
            
    except StateVerificationError as e:
        # Re-raise state verification errors
        raise
    except TokenExchangeError as e:
        # Re-raise token exchange errors
        raise
    except ProfileFetchError as e:
        # Re-raise profile fetch errors
        raise
    except SocialConnectionError as e:
        # Re-raise social connection errors
        raise
    except Exception as e:
        logger.exception(f"Unexpected error connecting Instagram account: {e}")
        raise SocialConnectionError(f"Unexpected error connecting Instagram account: {e}")

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

def connect_telegram_account(auth_data: Dict[str, Any] = None, code: str = None, session_key: str = None, state: str = None) -> Dict[str, Any]:
    """
    Connect a user's Telegram account to their profile using data from Telegram Login Widget.
    
    This function now supports both:
    1. Direct data from Telegram Login Widget (preferred method)
    2. Legacy flow with code, session_key and state (for backward compatibility)
    
    Args:
        auth_data: Dictionary containing Telegram login widget data
        code: Legacy parameter - Authorization code from Telegram
        session_key: Legacy parameter - Session key for state verification
        state: Legacy parameter - OAuth state for verification
    
    Returns:
        Dict containing token data and user profile information
    
    Raises:
        SocialConnectionError: If connection fails due to authentication issues
    """
    logger = logging.getLogger('social')
    
    # Log the beginning of the connection attempt
    logger.info(f"Starting Telegram account connection process")
    
    if auth_data:
        logger.info(f"Using Telegram Login Widget data")
        
        # Verify the Telegram data
        try:
            verify_telegram_data(auth_data)
        except SocialConnectionError as e:
            logger.error(f"Telegram data verification failed: {str(e)}")
            raise
            
        # Extract user data
        user_id = auth_data.get('id')
        first_name = auth_data.get('first_name', '')
        last_name = auth_data.get('last_name', '')
        username = auth_data.get('username', '')
        photo_url = auth_data.get('photo_url', '')
        
        # Create profile data
        profile_data = {
            'id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'photo_url': photo_url,
            'auth_date': auth_data.get('auth_date')
        }
        
        # For Telegram, we don't have a traditional OAuth token
        # Instead, we'll use the auth_date as a reference
        token_data = {
            'auth_date': auth_data.get('auth_date'),
            'user_id': user_id
        }
        
        # Get the user from the request context
        from django.contrib.auth import get_user_model
        from django.core.cache import cache
        
        User = get_user_model()
        user = None
        
        # Try to get the current user from the thread local storage
        from threading import local
        _thread_locals = local()
        if hasattr(_thread_locals, 'user') and _thread_locals.user and _thread_locals.user.is_authenticated:
            user = _thread_locals.user
        
        if user:
            # Update the user's profile
            logger.info(f"Updating Telegram details for user {user.id}")
            user.telegram_id = user_id
            user.telegram_username = username
            
            # Store the full profile data
            if not hasattr(user, 'social_profiles') or user.social_profiles is None:
                user.social_profiles = {}
            
            user.social_profiles['telegram'] = profile_data
            user.save(update_fields=['telegram_id', 'telegram_username', 'social_profiles'])
            
            logger.info(f"Successfully connected Telegram account for user {user.id}")
            return {
                'token_data': token_data,
                'profile': profile_data
            }
        else:
            # If no user is found, cache the data for later use
            cache_key = f"telegram_data_{user_id}"
            cache.set(cache_key, {
                'token_data': token_data,
                'profile': profile_data
            }, timeout=3600)  # Cache for 1 hour
            
            logger.info(f"Cached Telegram data for user_id {user_id} - no authenticated user found")
            return {
                'token_data': token_data,
                'profile': profile_data
            }
    
    # Legacy flow
    elif code and state:
        logger.info(f"Using legacy Telegram flow with code and state")
        # Verify the session state
        if not verify_oauth_state(state):
            logger.error(f"OAuth state verification failed")
            raise SocialConnectionError("State verification failed")
            
        # Process the code to get the user data
        # This is a placeholder since Telegram doesn't use traditional OAuth
        # In a real implementation, you would process the code to get user data
        
        logger.warning("Legacy Telegram flow is deprecated - use Telegram Login Widget instead")
        raise SocialConnectionError("Legacy Telegram flow is not supported. Please use Telegram Login Widget.")
    
    else:
        logger.error("No valid Telegram authentication data provided")
        raise SocialConnectionError("No valid Telegram authentication data provided")
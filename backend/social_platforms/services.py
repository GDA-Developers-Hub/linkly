import os
import json
import requests
import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone
from .models import SocialPlatform, UserSocialAccount

logger = logging.getLogger(__name__)

class OAuthManager:
    """Base class for OAuth authentication flows"""
    
    def __init__(self, platform_name):
        try:
            self.platform = SocialPlatform.objects.get(name=platform_name, is_active=True)
        except SocialPlatform.DoesNotExist:
            raise ValueError(f"Platform {platform_name} is not configured or not active")
            
        self.client_id = self.platform.client_id
        self.client_secret = self.platform.client_secret
        self.redirect_uri = self.platform.redirect_uri
        self.auth_url = self.platform.auth_url
        self.token_url = self.platform.token_url
        self.scopes = self.platform.get_scopes_list()
        
    def get_authorization_url(self, state=None):
        """Generate the authorization URL to begin OAuth flow"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes)
        }
        
        if state:
            params['state'] = state
            
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
            
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process token response and standardize format"""
        expires_in = token_data.get('expires_in')
        token_expiry = None
        
        if expires_in:
            token_expiry = timezone.now() + timedelta(seconds=int(expires_in))
            
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'token_expiry': token_expiry,
            'scope': token_data.get('scope', ' '.join(self.scopes))
        }
    
    def get_user_profile(self, access_token):
        """Fetch user profile with access token - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_user_profile")


class FacebookOAuthManager(OAuthManager):
    """Facebook-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('facebook')
        self.api_base_url = "https://graph.facebook.com/v17.0"
        
    def get_user_profile(self, access_token):
        """Get Facebook user profile and pages"""
        # Get user profile
        user_url = f"{self.api_base_url}/me?fields=id,name,email,picture&access_token={access_token}"
        user_response = requests.get(user_url)
        
        if user_response.status_code != 200:
            raise Exception(f"Failed to get user profile: {user_response.text}")
            
        user_data = user_response.json()
        
        # Get user pages (if permission was granted)
        pages_url = f"{self.api_base_url}/me/accounts?access_token={access_token}"
        pages_response = requests.get(pages_url)
        pages = []
        
        if pages_response.status_code == 200:
            pages_data = pages_response.json()
            pages = pages_data.get('data', [])
        
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'picture': user_data.get('picture', {}).get('data', {}).get('url'),
            'pages': pages
        }


class InstagramOAuthManager(OAuthManager):
    """Instagram-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('instagram')
        self.api_base_url = "https://graph.instagram.com"
        
    def get_user_profile(self, access_token):
        """Get Instagram user profile"""
        profile_url = f"{self.api_base_url}/me?fields=id,username,account_type,media_count&access_token={access_token}"
        response = requests.get(profile_url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
            
        profile_data = response.json()
        
        return {
            'id': profile_data.get('id'),
            'name': profile_data.get('username'),
            'account_type': profile_data.get('account_type'),
            'media_count': profile_data.get('media_count')
        }


class TwitterOAuthManager(OAuthManager):
    """Twitter-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('twitter')
        self.api_base_url = "https://api.twitter.com/2"
        
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - Twitter specific implementation"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'code_verifier': 'challenge'  # This is required for PKCE flow but we're using a simplified approach
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Log the request to help with debugging
        logger.info(f"Exchanging code for token with Twitter. Redirect URI: {self.redirect_uri}")
        
        response = requests.post(self.token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Twitter token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token with Twitter: {response.text}")
            
        token_data = response.json()
        logger.info(f"Successfully obtained token from Twitter: access_token present: {bool(token_data.get('access_token'))}, refresh_token present: {bool(token_data.get('refresh_token'))}")
        
        return token_data
    
    def get_user_profile(self, access_token):
        """Get Twitter user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # For Twitter API v2, we need to use the /users/me endpoint
        profile_url = f"{self.api_base_url}/users/me?user.fields=id,name,username,profile_image_url,public_metrics,description,verified"
        
        logger.info(f"Fetching Twitter user profile from: {profile_url}")
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to get Twitter user profile: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get Twitter user profile: {response.text}")
            
        data = response.json()
        user_data = data.get('data', {})
        
        logger.info(f"Successfully fetched Twitter profile for user: {user_data.get('username')}")
        
        # Return enhanced user data
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'username': user_data.get('username'),
            'profile_image_url': user_data.get('profile_image_url'),
            'verified': user_data.get('verified', False),
            'description': user_data.get('description'),
            'public_metrics': user_data.get('public_metrics', {}),
            'account_type': 'twitter_profile',
            'raw_response': data
        }
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired Twitter access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        logger.info(f"Refreshing Twitter access token")
        response = requests.post(self.token_url, data=data, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Twitter token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh Twitter token: {response.text}")
            
        token_data = response.json()
        logger.info(f"Successfully refreshed Twitter token: access_token present: {bool(token_data.get('access_token'))}")
        
        return token_data


class LinkedInOAuthManager(OAuthManager):
    """LinkedIn-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('linkedin')
        self.api_base_url = "https://api.linkedin.com/v2"
        
    def get_user_profile(self, access_token):
        """Get LinkedIn user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Get basic profile
        profile_url = f"{self.api_base_url}/me"
        profile_response = requests.get(profile_url, headers=headers)
        
        if profile_response.status_code != 200:
            raise Exception(f"Failed to get user profile: {profile_response.text}")
            
        profile_data = profile_response.json()
        
        # Get profile picture
        picture_url = f"{self.api_base_url}/me?projection=(profilePicture(displayImage~:playableStreams))"
        picture_response = requests.get(picture_url, headers=headers)
        picture_data = {}
        
        if picture_response.status_code == 200:
            picture_data = picture_response.json()
            
        # Get email address
        email_url = f"{self.api_base_url}/clientAwareMemberHandles?q=members&projection=(elements*(primary,type,handle~))"
        email_response = requests.get(email_url, headers=headers)
        email = None
        
        if email_response.status_code == 200:
            email_data = email_response.json()
            # Extract email from the response
            elements = email_data.get('elements', [])
            for element in elements:
                if element.get('type') == 'EMAIL':
                    email = element.get('handle~', {}).get('emailAddress')
        
        # Extract profile picture URL if available
        profile_picture_url = None
        if picture_data:
            picture_elements = picture_data.get('profilePicture', {}).get('displayImage~', {}).get('elements', [])
            if picture_elements:
                # Get the highest quality image
                largest_picture = max(picture_elements, key=lambda x: x.get('data', {}).get('width', 0))
                identifiers = largest_picture.get('identifiers', [])
                if identifiers:
                    profile_picture_url = identifiers[0].get('identifier')
        
        return {
            'id': profile_data.get('id'),
            'localizedFirstName': profile_data.get('localizedFirstName'),
            'localizedLastName': profile_data.get('localizedLastName'),
            'profile_picture_url': profile_picture_url,
            'email': email
        }


class YouTubeOAuthManager(OAuthManager):
    """YouTube (Google)-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('youtube')  # Using 'youtube' platform record
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        
    def get_user_profile(self, access_token):
        """Get YouTube channel information"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # First get user info
        user_response = requests.get(self.user_info_url, headers=headers)
        
        if user_response.status_code != 200:
            raise Exception(f"Failed to get user info: {user_response.text}")
            
        user_data = user_response.json()
        
        # Get YouTube channels
        channels_url = f"{self.api_base_url}/channels?part=snippet,statistics&mine=true"
        channels_response = requests.get(channels_url, headers=headers)
        
        if channels_response.status_code != 200:
            raise Exception(f"Failed to get channel info: {channels_response.text}")
            
        channels_data = channels_response.json()
        channels = channels_data.get('items', [])
        
        channel_data = {}
        if channels:
            # Use the first channel if user has multiple
            channel = channels[0]
            channel_data = {
                'channel_id': channel.get('id'),
                'title': channel.get('snippet', {}).get('title'),
                'description': channel.get('snippet', {}).get('description'),
                'thumbnail': channel.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url'),
                'subscriber_count': channel.get('statistics', {}).get('subscriberCount'),
                'video_count': channel.get('statistics', {}).get('videoCount')
            }
        
        return {
            'id': user_data.get('sub'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'picture': user_data.get('picture'),
            'channel': channel_data
        }
        

class TikTokOAuthManager(OAuthManager):
    """TikTok-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('tiktok')
        self.api_base_url = "https://open.tiktokapis.com/v2"
        
    def get_user_profile(self, access_token):
        """Get TikTok user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        profile_url = f"{self.api_base_url}/user/info/"
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
            
        data = response.json()
        user_data = data.get('data', {}).get('user', {})
        
        return {
            'id': user_data.get('open_id'),
            'name': user_data.get('display_name'),
            'avatar_url': user_data.get('avatar_url'),
            'profile_deep_link': user_data.get('profile_deep_link'),
            'is_verified': user_data.get('is_verified')
        }
        

class PinterestOAuthManager(OAuthManager):
    """Pinterest-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('pinterest')
        self.api_base_url = "https://api.pinterest.com/v5"
        
    def get_user_profile(self, access_token):
        """Get Pinterest user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Get user account information
        profile_url = f"{self.api_base_url}/user_account"
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
            
        user_data = response.json()
        
        # Get user boards
        boards_url = f"{self.api_base_url}/boards"
        boards_response = requests.get(boards_url, headers=headers)
        
        boards = []
        if boards_response.status_code == 200:
            boards_data = boards_response.json()
            boards = boards_data.get('items', [])
        
        return {
            'id': user_data.get('id'),
            'username': user_data.get('username'),
            'full_name': user_data.get('full_name') or user_data.get('username'),
            'profile_image': user_data.get('profile_image'),
            'account_type': user_data.get('account_type'),
            'boards': boards
        }


class GoogleAdsOAuthManager(OAuthManager):
    """Google Ads-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('google')
        self.api_base_url = "https://googleads.googleapis.com"
        self.user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.management_api_url = "https://www.googleapis.com/analytics/v3/management"
        
    def get_user_profile(self, access_token):
        """Get Google user profile and Ads accounts"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # First get basic user info
        user_response = requests.get(self.user_info_url, headers=headers)
        
        if user_response.status_code != 200:
            raise Exception(f"Failed to get user info: {user_response.text}")
            
        user_data = user_response.json()
        
        # Try to get Google Ads customer accounts if available
        # This is a simplified implementation as the actual Google Ads API requires:
        # 1. A Google Ads developer token
        # 2. A login customer ID
        # 3. Additional setup in the Google Ads API
        
        # For MVP, we'll store the user info and access token, then handle the actual API calls separately
        ads_accounts = []
        
        try:
            # Try to get Analytics accounts as a fallback
            analytics_url = f"{self.management_api_url}/accounts"
            analytics_response = requests.get(analytics_url, headers=headers)
            
            if analytics_response.status_code == 200:
                accounts_data = analytics_response.json()
                if 'items' in accounts_data:
                    ads_accounts = [
                        {
                            'id': account.get('id'),
                            'name': account.get('name'),
                            'type': 'analytics'
                        }
                        for account in accounts_data.get('items', [])
                    ]
        except Exception as e:
            logger.warning(f"Could not fetch Analytics accounts: {str(e)}")
        
        return {
            'id': user_data.get('sub'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'picture': user_data.get('picture'),
            'ads_accounts': ads_accounts
        }


# Factory to get the right OAuth manager based on platform
def get_oauth_manager(platform_name):
    """Factory function to get appropriate OAuth manager for a platform"""
    managers = {
        'facebook': FacebookOAuthManager,
        'instagram': InstagramOAuthManager,
        'twitter': TwitterOAuthManager,
        'linkedin': LinkedInOAuthManager,
        'youtube': YouTubeOAuthManager,
        'tiktok': TikTokOAuthManager,
        'pinterest': PinterestOAuthManager,
        'google': GoogleAdsOAuthManager,
    }
    
    manager_class = managers.get(platform_name)
    if not manager_class:
        raise ValueError(f"No OAuth manager implemented for platform: {platform_name}")
        
    return manager_class()


def connect_social_account(user, platform_name, auth_code):
    """Connect a user to a social media platform"""
    try:
        oauth_manager = get_oauth_manager(platform_name)
        
        # Exchange code for token
        token_data = oauth_manager.exchange_code_for_token(auth_code)
        processed_token = oauth_manager.process_token_response(token_data)
        
        # Get user profile from the platform
        profile_data = oauth_manager.get_user_profile(processed_token['access_token'])
        
        # Get or create platform instance
        platform = SocialPlatform.objects.get(name=platform_name)
        
        # Create or update user account
        account, created = UserSocialAccount.objects.update_or_create(
            user=user,
            platform=platform,
            account_id=profile_data.get('id'),
            defaults={
                'account_name': profile_data.get('name') or profile_data.get('username') or f"{platform_name} Account",
                'account_type': profile_data.get('account_type', 'profile'),
                'profile_picture_url': profile_data.get('picture') or profile_data.get('profile_image_url') or profile_data.get('avatar_url'),
                'access_token': processed_token['access_token'],
                'refresh_token': processed_token.get('refresh_token'),
                'token_expiry': processed_token.get('token_expiry'),
                'token_type': processed_token.get('token_type', 'Bearer'),
                'scope': processed_token.get('scope'),
                'raw_data': profile_data,
                'status': 'active',
                'last_used_at': timezone.now()
            }
        )
        
        # If this is the first account for this platform, make it primary
        if created:
            if not UserSocialAccount.objects.filter(
                user=user, 
                platform=platform, 
                is_primary=True
            ).exclude(id=account.id).exists():
                account.is_primary = True
                account.save()
        
        return account
    except Exception as e:
        logger.error(f"Error connecting social account: {str(e)}")
        raise
    
def refresh_token_if_needed(social_account):
    """Refresh token if it's expired and account has refresh token"""
    if social_account.is_expired and social_account.can_refresh:
        try:
            oauth_manager = get_oauth_manager(social_account.platform.name)
            token_data = oauth_manager.refresh_access_token(social_account.refresh_token)
            processed_token = oauth_manager.process_token_response(token_data)
            
            # Update account with new token info
            social_account.access_token = processed_token['access_token']
            
            # Some platforms might issue a new refresh token
            if processed_token.get('refresh_token'):
                social_account.refresh_token = processed_token['refresh_token']
                
            social_account.token_expiry = processed_token.get('token_expiry')
            social_account.status = 'active'
            social_account.save()
            
            return True
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            social_account.status = 'token_expired'
            social_account.save()
            return False
    
    return social_account.status == 'active'

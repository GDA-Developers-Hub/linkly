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
        
    def get_user_profile(self, access_token):
        """Get Twitter user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        profile_url = f"{self.api_base_url}/users/me?user.fields=id,name,username,profile_image_url"
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
            
        data = response.json()
        user_data = data.get('data', {})
        
        return {
            'id': user_data.get('id'),
            'name': user_data.get('name'),
            'username': user_data.get('username'),
            'profile_image_url': user_data.get('profile_image_url')
        }


class LinkedInOAuthManager(OAuthManager):
    """LinkedIn-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('linkedin')
        self.api_base_url = "https://api.linkedin.com/v2"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - LinkedIn implementation"""
        logger.info(f"Exchanging code for LinkedIn access token")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        logger.debug(f"LinkedIn token exchange request data (without secret): {dict(data, client_secret='***')}")
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"LinkedIn token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
            
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token - LinkedIn implementation"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"LinkedIn token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process LinkedIn token response"""
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
        """Get LinkedIn user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Initialize profile data with default values
        # This will be returned if we only have w_member_social scope
        default_profile_data = {
            'id': f"linkedin_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'first_name': 'LinkedIn',
            'last_name': 'User',
            'profile_picture_url': None,
            'email': None,
            'company_pages': [],
            'headline': 'LinkedIn Professional',
            'limited_access': True  # Flag to indicate limited scope access
        }
        
        try:
            # Get basic profile
            profile_url = f"{self.api_base_url}/me"
            profile_response = requests.get(profile_url, headers=headers)
            
            if profile_response.status_code != 200:
                # Check if this is a permissions error
                if profile_response.status_code == 403 and 'ACCESS_DENIED' in profile_response.text:
                    logger.warning("Limited LinkedIn permissions (w_member_social only). Using default profile data.")
                    return default_profile_data
                else:
                    logger.error(f"Failed to get LinkedIn profile: {profile_response.status_code} - {profile_response.text}")
                    raise Exception(f"Failed to get user profile: {profile_response.text}")
                
            profile_data = profile_response.json()
            
            # Attempt to get profile picture if we have access
            picture_data = {}
            try:
                picture_url = f"{self.api_base_url}/me?projection=(profilePicture(displayImage~:playableStreams))"
                picture_response = requests.get(picture_url, headers=headers)
                
                if picture_response.status_code == 200:
                    picture_data = picture_response.json()
                else:
                    logger.warning(f"Could not fetch LinkedIn profile picture: {picture_response.status_code} - {picture_response.text}")
            except Exception as e:
                logger.warning(f"Error fetching LinkedIn profile picture: {str(e)}")
                
            # Attempt to get email address if we have access
            email = None
            try:
                email_url = f"{self.api_base_url}/clientAwareMemberHandles?q=members&projection=(elements*(primary,type,handle~))"
                email_response = requests.get(email_url, headers=headers)
                
                if email_response.status_code == 200:
                    email_data = email_response.json()
                    # Extract email from the response
                    elements = email_data.get('elements', [])
                    for element in elements:
                        if element.get('type') == 'EMAIL':
                            email = element.get('handle~', {}).get('emailAddress')
                else:
                    logger.warning(f"Could not fetch LinkedIn email: {email_response.status_code} - {email_response.text}")
            except Exception as e:
                logger.warning(f"Error fetching LinkedIn email: {str(e)}")
            
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
            
            # Try to get company pages
            company_pages = []
            try:
                # Get company pages (organization access requires Admin APIs)
                # This is a placeholder for future expansion
                pass
            except Exception as e:
                logger.warning(f"Error fetching LinkedIn company pages: {str(e)}")
            
            # Build complete profile data
            return {
                'id': profile_data.get('id'),
                'first_name': profile_data.get('localizedFirstName'),
                'last_name': profile_data.get('localizedLastName'),
                'full_name': f"{profile_data.get('localizedFirstName')} {profile_data.get('localizedLastName')}",
                'profile_picture_url': profile_picture_url,
                'email': email,
                'company_pages': company_pages,
                'limited_access': False  # We have proper access
            }
        except Exception as e:
            logger.error(f"Error getting LinkedIn profile: {str(e)}")
            # Return default profile instead of raising exception
            logger.warning("Using default LinkedIn profile data due to error")
            return default_profile_data


class YouTubeOAuthManager(OAuthManager):
    """YouTube (Google)-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('youtube')  # Using 'youtube' platform record
        self.api_base_url = "https://www.googleapis.com/youtube/v3"
        self.user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.token_url = "https://oauth2.googleapis.com/token"  # Google's token endpoint
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - YouTube/Google implementation"""
        logger.info(f"Exchanging code for YouTube/Google access token")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        logger.debug(f"Google token exchange request data (without secret): {dict(data, client_secret='***')}")
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Google token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
            
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token - YouTube/Google implementation"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Google token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process Google token response"""
        expires_in = token_data.get('expires_in')
        token_expiry = None
        
        if expires_in:
            token_expiry = timezone.now() + timedelta(seconds=int(expires_in))
            
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'token_expiry': token_expiry,
            'scope': token_data.get('scope', ' '.join(self.scopes)),
            'id_token': token_data.get('id_token')  # Google specific, contains user info
        }
        
    def get_user_profile(self, access_token):
        """Get YouTube channel information"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            # First get user info
            user_response = requests.get(self.user_info_url, headers=headers)
            
            if user_response.status_code != 200:
                logger.error(f"Failed to get YouTube user info: {user_response.status_code} - {user_response.text}")
                raise Exception(f"Failed to get user info: {user_response.text}")
                
            user_data = user_response.json()
            
            # Get YouTube channels
            channels_url = f"{self.api_base_url}/channels?part=snippet,statistics,brandingSettings,contentDetails&mine=true"
            channels_response = requests.get(channels_url, headers=headers)
            
            if channels_response.status_code != 200:
                logger.error(f"Failed to get YouTube channel info: {channels_response.status_code} - {channels_response.text}")
                raise Exception(f"Failed to get channel info: {channels_response.text}")
                
            channels_data = channels_response.json()
            channels = channels_data.get('items', [])
            
            channel_data = {}
            recent_videos = []
            analytics_data = {}
            
            if channels:
                # Use the first channel if user has multiple
                channel = channels[0]
                channel_id = channel.get('id')
                
                # Basic channel data
                channel_data = {
                    'channel_id': channel_id,
                    'title': channel.get('snippet', {}).get('title'),
                    'description': channel.get('snippet', {}).get('description'),
                    'custom_url': channel.get('snippet', {}).get('customUrl'),
                    'published_at': channel.get('snippet', {}).get('publishedAt'),
                    'thumbnail': channel.get('snippet', {}).get('thumbnails', {}).get('high', {}).get('url'),
                    'subscriber_count': channel.get('statistics', {}).get('subscriberCount'),
                    'video_count': channel.get('statistics', {}).get('videoCount'),
                    'view_count': channel.get('statistics', {}).get('viewCount'),
                    'country': channel.get('snippet', {}).get('country'),
                    'banner_url': channel.get('brandingSettings', {}).get('image', {}).get('bannerExternalUrl'),
                    'upload_playlist_id': channel.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
                }
                
                # Get recent videos if available
                upload_playlist_id = channel_data.get('upload_playlist_id')
                if upload_playlist_id:
                    try:
                        videos_url = f"{self.api_base_url}/playlistItems?part=snippet,contentDetails&maxResults=10&playlistId={upload_playlist_id}"
                        videos_response = requests.get(videos_url, headers=headers)
                        
                        if videos_response.status_code == 200:
                            videos_data = videos_response.json()
                            videos_items = videos_data.get('items', [])
                            
                            for item in videos_items:
                                video_id = item.get('contentDetails', {}).get('videoId')
                                if video_id:
                                    recent_videos.append({
                                        'video_id': video_id,
                                        'title': item.get('snippet', {}).get('title'),
                                        'description': item.get('snippet', {}).get('description'),
                                        'published_at': item.get('snippet', {}).get('publishedAt'),
                                        'thumbnail': item.get('snippet', {}).get('thumbnails', {}).get('high', {}).get('url'),
                                    })
                    except Exception as e:
                        logger.warning(f"Error fetching YouTube videos: {str(e)}")
                
                # Try to get some basic analytics if possible
                try:
                    analytics_url = f"{self.api_base_url}/channels?part=statistics&id={channel_id}"
                    analytics_response = requests.get(analytics_url, headers=headers)
                    
                    if analytics_response.status_code == 200:
                        analytics_items = analytics_response.json().get('items', [])
                        if analytics_items:
                            analytics_data = analytics_items[0].get('statistics', {})
                except Exception as e:
                    logger.warning(f"Error fetching YouTube analytics: {str(e)}")
            
            # Combine all data
            return {
                'id': user_data.get('sub'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture'),
                'channel': channel_data,
                'recent_videos': recent_videos,
                'analytics': analytics_data
            }
        except Exception as e:
            logger.error(f"Error getting YouTube profile: {str(e)}")
            raise Exception(f"Failed to get YouTube profile: {str(e)}")
        

class TikTokOAuthManager(OAuthManager):
    """TikTok-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('tiktok')
        self.api_base_url = "https://open.tiktokapis.com/v2"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - TikTok implementation"""
        logger.info(f"Exchanging code for TikTok access token")
        
        data = {
            'client_key': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        logger.debug(f"TikTok token exchange request data: {data}")
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"TikTok token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token - TikTok implementation"""
        data = {
            'client_key': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"TikTok token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process TikTok token response"""
        expires_in = token_data.get('expires_in') or token_data.get('refresh_expires_in')
        token_expiry = None
        
        if expires_in:
            token_expiry = timezone.now() + timedelta(seconds=int(expires_in))
            
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'token_expiry': token_expiry,
            'scope': token_data.get('scope', ' '.join(self.scopes)),
            'open_id': token_data.get('open_id'),  # TikTok-specific
            'user_id': token_data.get('open_id')   # Store open_id as user_id for consistency
        }
        
    def get_user_profile(self, access_token):
        """Get TikTok user profile"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get basic user info
        profile_url = f"{self.api_base_url}/user/info/"
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to get TikTok user profile: {response.status_code} - {response.text}")
            raise Exception(f"Failed to get user profile: {response.text}")
            
        data = response.json()
        user_data = data.get('data', {}).get('user', {})
        
        # Get video statistics if possible
        video_stats = {}
        try:
            stats_url = f"{self.api_base_url}/video/list/"
            stats_response = requests.get(stats_url, headers=headers, params={'fields': 'id,like_count,comment_count,share_count,view_count'})
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                videos = stats_data.get('data', {}).get('videos', [])
                if videos:
                    # Calculate average engagement
                    total_likes = sum(v.get('like_count', 0) for v in videos)
                    total_comments = sum(v.get('comment_count', 0) for v in videos)
                    total_shares = sum(v.get('share_count', 0) for v in videos)
                    total_views = sum(v.get('view_count', 0) for v in videos)
                    
                    video_stats = {
                        'video_count': len(videos),
                        'total_likes': total_likes,
                        'total_comments': total_comments,
                        'total_shares': total_shares,
                        'total_views': total_views
                    }
        except Exception as e:
            logger.warning(f"Error fetching TikTok video stats: {str(e)}")
        
        return {
            'id': user_data.get('open_id'),
            'name': user_data.get('display_name'),
            'avatar_url': user_data.get('avatar_url'),
            'profile_deep_link': user_data.get('profile_deep_link'),
            'is_verified': user_data.get('is_verified'),
            'follower_count': user_data.get('follower_count'),
            'following_count': user_data.get('following_count'),
            'video_stats': video_stats
        }
        

class ThreadsOAuthManager(OAuthManager):
    """Threads (via Instagram) OAuth implementation"""
    
    def __init__(self):
        super().__init__('threads')
        self.api_base_url = "https://graph.instagram.com"
        self.api_version = "v18.0"  # Using same version as Instagram/Meta
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - Threads implementation"""
        logger.info(f"Exchanging code for Threads access token")
        
        # Threads uses the Meta/Facebook token endpoint
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        logger.debug(f"Threads token exchange request data (without secret): {dict(data, client_secret='***')}")
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Threads token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
            
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token - Threads implementation"""
        # Meta long-lived tokens don't typically need refreshing in the same way
        # but we'll implement this for completeness
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Threads token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process Threads token response"""
        expires_in = token_data.get('expires_in')
        token_expiry = None
        
        if expires_in:
            token_expiry = timezone.now() + timedelta(seconds=int(expires_in))
            
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'token_expiry': token_expiry,
            'scope': token_data.get('scope', ' '.join(self.scopes)),
            'user_id': token_data.get('user_id')
        }
    
    def get_user_profile(self, access_token):
        """Get Threads user profile"""
        # Threads API is based on Instagram Graph API
        # We'll get basic user info and then any Threads-specific info if available
        
        try:
            # Get basic user profile from Instagram Graph API
            fields = "id,username,account_type,media_count,profile_picture_url"
            profile_url = f"{self.api_base_url}/me?fields={fields}&access_token={access_token}"
            
            profile_response = requests.get(profile_url)
            
            if profile_response.status_code != 200:
                logger.error(f"Failed to get Threads profile: {profile_response.status_code} - {profile_response.text}")
                raise Exception(f"Failed to get user profile: {profile_response.text}")
                
            profile_data = profile_response.json()
            
            # Attempt to get Threads-specific info if available
            # As of implementation time, the Threads API is limited, so we may need to make educated guesses
            # or use the Instagram data as a fallback
            threads_profile = {
                'id': profile_data.get('id'),
                'username': profile_data.get('username'),
                'account_type': profile_data.get('account_type'),
                'profile_picture_url': profile_data.get('profile_picture_url'),
                'media_count': profile_data.get('media_count'),
                'platform': 'threads',
                'bio': None,  # Not available via standard Instagram API
                'follower_count': None,  # Not available via standard Instagram API
                'following_count': None  # Not available via standard Instagram API
            }
            
            # Try to get media items if available
            recent_posts = []
            try:
                media_url = f"{self.api_base_url}/me/media?fields=id,caption,media_type,permalink,thumbnail_url,timestamp,username&access_token={access_token}"
                media_response = requests.get(media_url)
                
                if media_response.status_code == 200:
                    media_data = media_response.json()
                    for item in media_data.get('data', [])[:5]:  # Get the first 5 posts
                        recent_posts.append({
                            'id': item.get('id'),
                            'caption': item.get('caption'),
                            'media_type': item.get('media_type'),
                            'permalink': item.get('permalink'),
                            'thumbnail_url': item.get('thumbnail_url'),
                            'timestamp': item.get('timestamp'),
                            'username': item.get('username')
                        })
            except Exception as e:
                logger.warning(f"Error fetching Threads media: {str(e)}")
            
            return {
                'profile': threads_profile,
                'recent_posts': recent_posts
            }
            
        except Exception as e:
            logger.error(f"Error getting Threads profile: {str(e)}")
            raise Exception(f"Failed to get Threads profile: {str(e)}")


class PinterestOAuthManager(OAuthManager):
    """Pinterest-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('pinterest')
        self.api_base_url = "https://api.pinterest.com/v5"
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - Pinterest implementation"""
        logger.info(f"Exchanging code for Pinterest access token")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        logger.debug(f"Pinterest token exchange request data (without secret): {dict(data, client_secret='***')}")
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Pinterest token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
            
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token - Pinterest implementation"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Pinterest token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process Pinterest token response"""
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
        """Get Pinterest user profile"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Get user account information
            profile_url = f"{self.api_base_url}/user_account"
            response = requests.get(profile_url, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get Pinterest profile: {response.status_code} - {response.text}")
                raise Exception(f"Failed to get user profile: {response.text}")
                
            user_data = response.json()
            
            # Get user boards
            boards = []
            try:
                boards_url = f"{self.api_base_url}/boards"
                boards_response = requests.get(boards_url, headers=headers)
                
                if boards_response.status_code == 200:
                    boards_data = boards_response.json()
                    boards = boards_data.get('items', [])
                    
                    # Get some basic stats for each board if available
                    for board in boards:
                        try:
                            board_id = board.get('id')
                            if board_id:
                                board_url = f"{self.api_base_url}/boards/{board_id}"
                                board_details_response = requests.get(board_url, headers=headers)
                                
                                if board_details_response.status_code == 200:
                                    board_details = board_details_response.json()
                                    board['pin_count'] = board_details.get('pin_count', 0)
                                    board['follower_count'] = board_details.get('follower_count', 0)
                        except Exception as e:
                            logger.warning(f"Could not fetch details for board {board_id}: {str(e)}")
            except Exception as e:
                logger.warning(f"Could not fetch Pinterest boards: {str(e)}")
            
            # Try to get some pins data
            pins = []
            try:
                pins_url = f"{self.api_base_url}/pins"
                pins_response = requests.get(pins_url, headers=headers)
                
                if pins_response.status_code == 200:
                    pins_data = pins_response.json()
                    pins = pins_data.get('items', [])[:5]  # Get the top 5 pins
            except Exception as e:
                logger.warning(f"Could not fetch Pinterest pins: {str(e)}")
            
            # Get analytics if available
            analytics = {}
            try:
                analytics_url = f"{self.api_base_url}/user_account/analytics"
                analytics_response = requests.get(analytics_url, headers=headers)
                
                if analytics_response.status_code == 200:
                    analytics = analytics_response.json()
            except Exception as e:
                logger.warning(f"Could not fetch Pinterest analytics: {str(e)}")
            
            return {
                'id': user_data.get('id'),
                'username': user_data.get('username'),
                'full_name': user_data.get('full_name') or user_data.get('username'),
                'profile_image': user_data.get('profile_image'),
                'account_type': user_data.get('account_type'),
                'boards': boards,
                'pins': pins,
                'analytics': analytics
            }
        except Exception as e:
            logger.error(f"Error getting Pinterest profile: {str(e)}")
            raise Exception(f"Failed to get Pinterest profile: {str(e)}")


class GoogleAdsOAuthManager(OAuthManager):
    """Google Ads-specific OAuth implementation"""
    
    def __init__(self):
        super().__init__('google')
        self.api_base_url = "https://googleads.googleapis.com"
        self.user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.management_api_url = "https://www.googleapis.com/analytics/v3/management"
        self.token_url = "https://oauth2.googleapis.com/token"  # Google's token endpoint
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token - Google implementation"""
        logger.info(f"Exchanging code for Google Ads access token")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        logger.debug(f"Google token exchange request data (without secret): {dict(data, client_secret='***')}")
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Google token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to exchange code for token: {response.text}")
            
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh an expired access token using refresh token - Google implementation"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Google token refresh failed: {response.status_code} - {response.text}")
            raise Exception(f"Failed to refresh token: {response.text}")
            
        return response.json()
    
    def process_token_response(self, token_data):
        """Process Google token response"""
        expires_in = token_data.get('expires_in')
        token_expiry = None
        
        if expires_in:
            token_expiry = timezone.now() + timedelta(seconds=int(expires_in))
            
        return {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_type': token_data.get('token_type', 'Bearer'),
            'token_expiry': token_expiry,
            'scope': token_data.get('scope', ' '.join(self.scopes)),
            'id_token': token_data.get('id_token')  # Google specific, contains user info
        }
        
    def get_user_profile(self, access_token):
        """Get Google user profile and Ads accounts"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # First get basic user info
            user_response = requests.get(self.user_info_url, headers=headers)
            
            if user_response.status_code != 200:
                logger.error(f"Failed to get Google user info: {user_response.status_code} - {user_response.text}")
                raise Exception(f"Failed to get user info: {user_response.text}")
                
            user_data = user_response.json()
            
            # Try to get Google Ads customer accounts if available
            # This is a simplified implementation as the actual Google Ads API requires:
            # 1. A Google Ads developer token
            # 2. A login customer ID
            # 3. Additional setup in the Google Ads API
            
            # For MVP, we'll store the user info and access token, then handle the actual API calls separately
            ads_accounts = []
            analytics_properties = []
            
            # Try to get Google Ads accounts
            try:
                # Note: This is a placeholder. The actual Google Ads API has more strict requirements
                # and may need a developer token and additional setup
                # For now, we'll create a simple placeholder
                ads_accounts.append({
                    'id': user_data.get('sub'),
                    'name': f"{user_data.get('name')}'s Ads Account",
                    'type': 'ads',
                    'status': 'pending_setup'
                })
            except Exception as e:
                logger.warning(f"Could not set up Google Ads account: {str(e)}")
            
            # Try to get Analytics accounts as a fallback
            try:
                analytics_url = f"{self.management_api_url}/accounts"
                analytics_response = requests.get(analytics_url, headers=headers)
                
                if analytics_response.status_code == 200:
                    accounts_data = analytics_response.json()
                    if 'items' in accounts_data:
                        for account in accounts_data.get('items', []):
                            account_id = account.get('id')
                            account_obj = {
                                'id': account_id,
                                'name': account.get('name'),
                                'type': 'analytics'
                            }
                            
                            # Try to get properties for this account
                            try:
                                properties_url = f"{self.management_api_url}/accounts/{account_id}/webproperties"
                                properties_response = requests.get(properties_url, headers=headers)
                                
                                if properties_response.status_code == 200:
                                    properties_data = properties_response.json()
                                    if 'items' in properties_data:
                                        account_obj['properties'] = [
                                            {
                                                'id': prop.get('id'),
                                                'name': prop.get('name'),
                                                'website': prop.get('websiteUrl'),
                                                'created': prop.get('created'),
                                                'updated': prop.get('updated')
                                            }
                                            for prop in properties_data.get('items', [])
                                        ]
                                        analytics_properties.extend(account_obj.get('properties', []))
                            except Exception as e:
                                logger.warning(f"Could not fetch Analytics properties for account {account_id}: {str(e)}")
                            
                            ads_accounts.append(account_obj)
            except Exception as e:
                logger.warning(f"Could not fetch Analytics accounts: {str(e)}")
            
            # Try to get any Tag Manager accounts
            tag_manager_accounts = []
            try:
                # Placeholder for Tag Manager API integration
                # Actual implementation would connect to the GTM API
                pass
            except Exception as e:
                logger.warning(f"Could not fetch Tag Manager accounts: {str(e)}")
            
            return {
                'id': user_data.get('sub'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture'),
                'ads_accounts': ads_accounts,
                'analytics_properties': analytics_properties,
                'tag_manager_accounts': tag_manager_accounts
            }
        except Exception as e:
            logger.error(f"Error getting Google profile: {str(e)}")
            raise Exception(f"Failed to get Google profile: {str(e)}")


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
        'threads': ThreadsOAuthManager,
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

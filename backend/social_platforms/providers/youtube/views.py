"""
YouTube OAuth2 views for Django Allauth.
"""
import requests
import logging
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import YouTubeProvider

logger = logging.getLogger(__name__)

class YouTubeOAuth2Adapter(GoogleOAuth2Adapter):
    """YouTube OAuth2 adapter extending Google OAuth2 adapter"""
    provider_id = YouTubeProvider.id
    
    def complete_login(self, request, app, token, **kwargs):
        """
        Complete the login process and fetch YouTube-specific data
        """
        # First get the Google user info using the parent adapter
        login = super().complete_login(request, app, token, **kwargs)
        
        # Now get YouTube-specific channel data
        try:
            headers = {
                'Authorization': f'Bearer {token.token}',
                'Content-Type': 'application/json'
            }
            
            # Get the user's YouTube channel info
            youtube_url = 'https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true'
            response = requests.get(youtube_url, headers=headers)
            
            if response.status_code == 200:
                youtube_data = response.json()
                
                if 'items' in youtube_data and youtube_data['items']:
                    channel = youtube_data['items'][0]
                    channel_id = channel.get('id')
                    snippet = channel.get('snippet', {})
                    statistics = channel.get('statistics', {})
                    
                    # Update the extra_data with YouTube-specific information
                    login.account.extra_data.update({
                        'channel_id': channel_id,
                        'channel_title': snippet.get('title'),
                        'channel_description': snippet.get('description'),
                        'channel_url': f'https://www.youtube.com/channel/{channel_id}',
                        'profile_image_url': snippet.get('thumbnails', {}).get('default', {}).get('url'),
                        'subscriber_count': statistics.get('subscriberCount'),
                        'video_count': statistics.get('videoCount'),
                        'view_count': statistics.get('viewCount'),
                        'hidden_subscriber_count': statistics.get('hiddenSubscriberCount', False),
                        'youtube_created_at': snippet.get('publishedAt')
                    })
                else:
                    logger.warning("No YouTube channel found for the authenticated user")
            else:
                logger.warning(f"Failed to fetch YouTube channel data: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.exception(f"Error fetching YouTube channel data: {str(e)}")
        
        return login


oauth2_login = OAuth2LoginView.adapter_view(YouTubeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(YouTubeOAuth2Adapter)

"""
TikTok OAuth2 views for Django Allauth.
"""
import requests
import logging
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import TikTokProvider

logger = logging.getLogger(__name__)

class TikTokOAuth2Adapter(OAuth2Adapter):
    """TikTok OAuth2 adapter"""
    provider_id = TikTokProvider.id
    
    # TikTok OAuth2 endpoints
    access_token_url = 'https://open-api.tiktok.com/oauth/access_token/'
    authorize_url = 'https://www.tiktok.com/auth/authorize/'
    profile_url = 'https://open-api.tiktok.com/v2/user/info/'
    
    def complete_login(self, request, app, token, **kwargs):
        """Complete the login process by fetching the user profile"""
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Get TikTok user profile
            profile_response = requests.get(
                self.profile_url,
                headers=headers,
                params={
                    'fields': 'open_id,union_id,avatar_url,display_name,username'
                }
            )
            
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            if 'data' in profile_data:
                user_data = profile_data['data']
                # Extract relevant fields
                extra_data = {
                    'id': user_data.get('open_id'),
                    'open_id': user_data.get('open_id'),
                    'union_id': user_data.get('union_id'),
                    'avatar_url': user_data.get('avatar_url'),
                    'display_name': user_data.get('display_name'),
                    'username': user_data.get('username')
                }
            else:
                # Use minimal data from token if profile unavailable
                extra_data = {
                    'id': kwargs.get('response', {}).get('open_id'),
                    'open_id': kwargs.get('response', {}).get('open_id')
                }
                
            return self.get_provider().sociallogin_from_response(
                request, extra_data
            )
        except Exception as e:
            logger.exception(f"Error fetching TikTok profile: {str(e)}")
            # Fallback to minimal user data
            minimal_data = {
                'id': kwargs.get('response', {}).get('open_id'),
                'open_id': kwargs.get('response', {}).get('open_id')
            }
            return self.get_provider().sociallogin_from_response(
                request, minimal_data
            )
            
    def parse_token(self, data):
        """Parse the token from TikTok response"""
        # TikTok response includes data inside a 'data' field
        if 'data' in data:
            data = data['data']
        return super().parse_token(data)


oauth2_login = OAuth2LoginView.adapter_view(TikTokOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TikTokOAuth2Adapter)

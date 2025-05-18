"""
Pinterest OAuth2 views for Django Allauth.
"""
import requests
import logging
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import PinterestProvider

logger = logging.getLogger(__name__)

class PinterestOAuth2Adapter(OAuth2Adapter):
    """Pinterest OAuth2 adapter"""
    provider_id = PinterestProvider.id
    
    # Pinterest OAuth2 endpoints
    access_token_url = 'https://api.pinterest.com/v5/oauth/token'
    authorize_url = 'https://www.pinterest.com/oauth/'
    profile_url = 'https://api.pinterest.com/v5/user_account'
    
    def complete_login(self, request, app, token, **kwargs):
        """Complete the login process by fetching the user profile"""
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # Get Pinterest user profile
            profile_response = requests.get(self.profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Extract basic user information
            user_data = {
                'id': profile_data.get('id'),
                'username': profile_data.get('username'),
                'full_name': f"{profile_data.get('first_name', '')} {profile_data.get('last_name', '')}".strip(),
                'first_name': profile_data.get('first_name'),
                'last_name': profile_data.get('last_name'),
                'bio': profile_data.get('about'),
                'profile_image': profile_data.get('profile_image'),
                'website_url': profile_data.get('website_url'),
                'account_type': profile_data.get('account_type')
            }
            
            # Try to get boards information
            try:
                boards_url = 'https://api.pinterest.com/v5/boards'
                boards_response = requests.get(boards_url, headers=headers)
                
                if boards_response.status_code == 200:
                    boards_data = boards_response.json()
                    # Add boards data to user info
                    if 'items' in boards_data:
                        user_data['boards'] = [
                            {
                                'id': board.get('id'),
                                'name': board.get('name'),
                                'description': board.get('description'),
                                'url': board.get('url')
                            }
                            for board in boards_data.get('items', [])
                        ]
                        user_data['board_count'] = len(boards_data.get('items', []))
            except Exception as e:
                logger.warning(f"Could not get Pinterest boards: {str(e)}")
            
            # Try to get some pins
            try:
                pins_url = 'https://api.pinterest.com/v5/pins'
                pins_response = requests.get(pins_url, headers=headers, 
                                           params={'page_size': 10})
                
                if pins_response.status_code == 200:
                    pins_data = pins_response.json()
                    # Add pins data to user info
                    if 'items' in pins_data:
                        user_data['pins'] = [
                            {
                                'id': pin.get('id'),
                                'title': pin.get('title'),
                                'description': pin.get('description'),
                                'link': pin.get('link'),
                                'media': pin.get('media', {}).get('images', {}).get('originals', {}).get('url')
                            }
                            for pin in pins_data.get('items', [])
                        ]
            except Exception as e:
                logger.warning(f"Could not get Pinterest pins: {str(e)}")
            
            return self.get_provider().sociallogin_from_response(
                request, user_data
            )
        except Exception as e:
            logger.exception(f"Error fetching Pinterest profile: {str(e)}")
            # Fallback to minimal user data
            minimal_data = {
                'id': kwargs.get('response', {}).get('user_id', 'unknown')
            }
            return self.get_provider().sociallogin_from_response(
                request, minimal_data
            )


oauth2_login = OAuth2LoginView.adapter_view(PinterestOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PinterestOAuth2Adapter)

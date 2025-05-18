"""
Threads OAuth2 views for Django Allauth (using Instagram's API).
"""
import requests
import logging
from allauth.socialaccount.providers.instagram.views import InstagramOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import ThreadsProvider

logger = logging.getLogger(__name__)

class ThreadsOAuth2Adapter(InstagramOAuth2Adapter):
    """Threads OAuth2 adapter (extends Instagram adapter)"""
    provider_id = ThreadsProvider.id
    
    def complete_login(self, request, app, token, **kwargs):
        """
        Complete the login process and fetch Threads-specific data
        """
        # First get the Instagram user info using the parent adapter
        login = super().complete_login(request, app, token, **kwargs)
        
        # Now try to get additional Threads-specific data (if any)
        try:
            # For now, we use the Instagram API to get the user's data
            # and add a Threads-specific identifier in the extra_data
            # In the future, if Threads has a specific API, we can update this
            
            login.account.extra_data.update({
                'is_threads_account': True,
                'threads_profile_url': f"https://www.threads.net/@{login.account.extra_data.get('username', '')}"
            })
            
            # Try to get additional Threads-specific data if available
            # Note: This is a placeholder as there's no official separate Threads API yet
            try:
                headers = {
                    'Authorization': f'Bearer {token.token}'
                }
                
                # This is a placeholder - in the future, if Threads has a public API, update this
                threads_url = f"https://graph.instagram.com/v12.0/{login.account.extra_data.get('id')}/threads"
                response = requests.get(threads_url, headers=headers)
                
                if response.status_code == 200:
                    threads_data = response.json()
                    # Update with Threads-specific information when available
                    login.account.extra_data.update({
                        'threads_data': threads_data
                    })
                    
            except Exception as e:
                logger.debug(f"Could not fetch Threads-specific data, using Instagram data instead: {str(e)}")
        
        except Exception as e:
            logger.exception(f"Error enriching Threads profile data: {str(e)}")
        
        return login


oauth2_login = OAuth2LoginView.adapter_view(ThreadsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ThreadsOAuth2Adapter)

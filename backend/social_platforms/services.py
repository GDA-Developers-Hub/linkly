"""
Services for social platform integration.
This file provides backward compatibility with the original services.py while using Allauth under the hood.
"""
import logging
import warnings
from django.utils import timezone
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from .models import SocialPlatform, UserSocialAccount
from .services_allauth import (
    get_allauth_provider_for_platform,
    sync_social_accounts,
    refresh_token_with_allauth
)
from .allauth_integration import get_oauth_redirect_url, initialize_social_apps

logger = logging.getLogger(__name__)

class OAuthManager:
    """Base class for OAuth authentication flows (compatibility wrapper for Allauth)"""
    
    def __init__(self, platform_name):
        self.platform_name = platform_name
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
        
        # Show deprecation warning
        warnings.warn(
            f"Direct use of OAuthManager is deprecated. Please use Django Allauth integration instead.",
            DeprecationWarning, stacklevel=2
        )
        
    def get_authorization_url(self, state=None):
        """Generate the authorization URL to begin OAuth flow (using Allauth)"""
        from django.http import HttpRequest
        # Create a dummy request to pass to get_oauth_redirect_url
        request = HttpRequest()
        provider_id = get_allauth_provider_for_platform(self.platform_name)
        
        try:
            # Get the authorization URL from Allauth
            result = get_oauth_redirect_url(request, provider_id)
            if 'error' in result:
                raise Exception(result['error'])
                
            # Store state in request session
            request.session = {}
            request.session[f'{provider_id}_oauth_state'] = result['state']
            
            return result['authorization_url']
        except Exception as e:
            logger.exception(f"Error getting authorization URL for {self.platform_name}: {str(e)}")
            # Fallback to old implementation for backward compatibility
            from urllib.parse import urlencode
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': ' '.join(self.scopes)
            }
            
            if state:
                params['state'] = state
                
            return f"{self.auth_url}?{urlencode(params)}"


# Factory for backward compatibility
def get_oauth_manager(platform_name):
    """Factory function to get appropriate OAuth manager for a platform"""
    warnings.warn(
        f"get_oauth_manager is deprecated. Please use Django Allauth integration instead.",
        DeprecationWarning, stacklevel=2
    )
    return OAuthManager(platform_name)


def connect_social_account(user, platform_name, auth_code):
    """Connect a user to a social media platform using the authorization code"""
    warnings.warn(
        f"connect_social_account is deprecated. Please use Django Allauth integration instead.",
        DeprecationWarning, stacklevel=2
    )
    
    # For backward compatibility, we'll create a minimal implementation
    # that simulates the old behavior but logs a warning
    try:
        platform = SocialPlatform.objects.get(name=platform_name)
        account_id = f"manual-{platform_name}-{user.id}"
        
        # Create a minimal account record
        account, created = UserSocialAccount.objects.update_or_create(
            user=user,
            platform=platform,
            account_id=account_id,
            defaults={
                'account_name': f"{user.username}'s {platform_name} account",
                'access_token': "placeholder-token",
                'status': 'pending',
                'last_used_at': timezone.now()
            }
        )
        
        logger.warning(
            f"connect_social_account was called without Allauth integration. "
            f"Created placeholder account {account.id} for platform {platform_name}."
        )
        
        return account
    except Exception as e:
        logger.exception(f"Error in deprecated connect_social_account: {str(e)}")
        raise


def refresh_token_if_needed(social_account):
    """Refresh token if it's expired and account has refresh token"""
    warnings.warn(
        f"refresh_token_if_needed is deprecated. Please use refresh_token_with_allauth instead.",
        DeprecationWarning, stacklevel=2
    )
    
    return refresh_token_with_allauth(social_account)


# Backward compatibility import to make migration smoother
# These imports will raise errors if directly accessed
try:
    from .deprecated.services import (
        FacebookOAuthManager,
        InstagramOAuthManager,
        TwitterOAuthManager, 
        LinkedInOAuthManager,
        YouTubeOAuthManager,
        TikTokOAuthManager,
        ThreadsOAuthManager,
        PinterestOAuthManager,
        GoogleAdsOAuthManager
    )
except ImportError:
    # Define placeholders that will raise warnings
    class DeprecatedOAuthManager(OAuthManager):
        def __init__(self, *args, **kwargs):
            warnings.warn(
                f"This OAuth manager is deprecated and should not be used. "
                f"Please use Django Allauth integration instead.",
                DeprecationWarning, stacklevel=2
            )
            super().__init__(*args, **kwargs)
    
    class FacebookOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('facebook')
    
    class InstagramOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('instagram')
    
    class TwitterOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('twitter')
    
    class LinkedInOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('linkedin')
    
    class YouTubeOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('youtube')
    
    class TikTokOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('tiktok')
    
    class ThreadsOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('threads')
    
    class PinterestOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('pinterest')
    
    class GoogleAdsOAuthManager(DeprecatedOAuthManager):
        def __init__(self):
            super().__init__('google_ads')  # Platform name stays the same, provider ID is now 'googleads'

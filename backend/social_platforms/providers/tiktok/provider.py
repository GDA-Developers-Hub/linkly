"""
TikTok OAuth2 provider for Django Allauth.
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

class TikTokAccount(ProviderAccount):
    """TikTok account model"""
    def get_profile_url(self):
        # TikTok doesn't provide a profile URL in their API response
        return None

    def get_avatar_url(self):
        # Return avatar URL if available in extra_data
        return self.account.extra_data.get('avatar_url', None)

    def to_str(self):
        # Use display name if available, fall back to default
        return self.account.extra_data.get('display_name', 
               super(TikTokAccount, self).to_str())


class TikTokProvider(OAuth2Provider):
    """TikTok OAuth2 provider"""
    id = 'tiktok'
    name = 'TikTok'
    account_class = TikTokAccount

    def extract_uid(self, data):
        """Extract unique user ID from TikTok account data"""
        return str(data.get('open_id') or data.get('id'))

    def extract_common_fields(self, data):
        """Extract common user fields from TikTok account data"""
        return {
            'username': data.get('username'),
            'name': data.get('display_name'),
            'email': data.get('email'),  # TikTok may not provide email
        }

    def get_default_scope(self):
        """Return default scope list"""
        return ['user.info.basic', 'video.list']


provider_classes = [TikTokProvider]

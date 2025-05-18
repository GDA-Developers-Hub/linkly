"""
YouTube OAuth2 provider for Django Allauth.
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider

class YouTubeAccount(ProviderAccount):
    """YouTube account model"""
    def get_profile_url(self):
        return self.account.extra_data.get('channel_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('profile_image_url')

    def to_str(self):
        return self.account.extra_data.get('channel_title', 
               super(YouTubeAccount, self).to_str())


class YouTubeProvider(GoogleProvider):
    """YouTube OAuth2 provider extending Google Provider"""
    id = 'youtube'
    name = 'YouTube'
    account_class = YouTubeAccount

    def extract_uid(self, data):
        """Extract unique user ID from YouTube account data"""
        return str(data.get('channel_id') or data.get('id'))

    def extract_common_fields(self, data):
        """Extract common user fields from YouTube account data"""
        return {
            'username': data.get('channel_title'),
            'name': data.get('channel_title'),
            'email': data.get('email'),
        }

    def get_default_scope(self):
        """Return default scope list specifically for YouTube"""
        return ['https://www.googleapis.com/auth/youtube.readonly', 
                'https://www.googleapis.com/auth/youtube']


provider_classes = [YouTubeProvider]

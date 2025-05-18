"""
Pinterest OAuth2 provider for Django Allauth.
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

class PinterestAccount(ProviderAccount):
    """Pinterest account model"""
    def get_profile_url(self):
        username = self.account.extra_data.get('username')
        if username:
            return f"https://www.pinterest.com/{username}/"
        return None

    def get_avatar_url(self):
        return self.account.extra_data.get('profile_image')

    def to_str(self):
        username = self.account.extra_data.get('username')
        name = self.account.extra_data.get('full_name')
        return name or username or super(PinterestAccount, self).to_str()


class PinterestProvider(OAuth2Provider):
    """Pinterest OAuth2 provider"""
    id = 'pinterest'
    name = 'Pinterest'
    account_class = PinterestAccount

    def extract_uid(self, data):
        """Extract unique user ID from Pinterest account data"""
        return str(data.get('id'))

    def extract_common_fields(self, data):
        """Extract common user fields from Pinterest account data"""
        return {
            'username': data.get('username'),
            'name': data.get('full_name') or data.get('first_name'),
            'email': data.get('email'),
        }

    def get_default_scope(self):
        """Return default scope list for Pinterest"""
        return ['boards:read', 'pins:read', 'user_accounts:read']


provider_classes = [PinterestProvider]

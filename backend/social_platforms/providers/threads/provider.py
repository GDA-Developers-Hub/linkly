"""
Threads OAuth2 provider for Django Allauth (using Instagram's API).
"""
from allauth.socialaccount.providers.instagram.provider import InstagramProvider
from allauth.socialaccount.providers.base import ProviderAccount

class ThreadsAccount(ProviderAccount):
    """Threads account model (based on Instagram)"""
    def get_profile_url(self):
        return f"https://www.threads.net/@{self.account.extra_data.get('username', '')}"

    def get_avatar_url(self):
        return self.account.extra_data.get('profile_picture')

    def to_str(self):
        return self.account.extra_data.get('username', 
               super(ThreadsAccount, self).to_str())


class ThreadsProvider(InstagramProvider):
    """Threads OAuth2 provider (extends Instagram provider)"""
    id = 'threads'
    name = 'Threads'
    account_class = ThreadsAccount

    def extract_uid(self, data):
        """Extract unique user ID from Threads (Instagram) account data"""
        return str(data.get('id'))

    def extract_common_fields(self, data):
        """Extract common user fields from Threads (Instagram) account data"""
        return {
            'username': data.get('username'),
            'name': data.get('full_name'),
        }

    def get_default_scope(self):
        """Return default scope list for Threads (Instagram)"""
        return ['user_profile', 'user_media']


provider_classes = [ThreadsProvider]

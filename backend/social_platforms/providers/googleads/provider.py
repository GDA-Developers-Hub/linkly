"""
Google Ads OAuth2 provider for Django Allauth.
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider

class GoogleAdsAccount(ProviderAccount):
    """Google Ads account model"""
    def get_profile_url(self):
        return "https://ads.google.com"

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        return self.account.extra_data.get('name', 
               super(GoogleAdsAccount, self).to_str())


class GoogleAdsProvider(GoogleProvider):
    """Google Ads OAuth2 provider, extending the Google provider"""
    id = 'googleads'
    name = 'Google Ads'
    account_class = GoogleAdsAccount

    def extract_uid(self, data):
        """Extract unique user ID from Google Ads account data"""
        return str(data.get('sub') or data.get('id'))

    def extract_common_fields(self, data):
        """Extract common user fields from Google Ads account data"""
        return {
            'email': data.get('email'),
            'last_name': data.get('family_name'),
            'first_name': data.get('given_name'),
            'name': data.get('name'),
        }

    def get_default_scope(self):
        """Return default scope list for Google Ads"""
        return ['https://www.googleapis.com/auth/adwords', 
                'email', 'profile']


provider_classes = [GoogleAdsProvider]

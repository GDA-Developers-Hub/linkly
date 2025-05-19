from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Called after a social account is linked to an already logged-in user.
        """
        # You can dynamically build your redirect here
        provider = socialaccount.provider  # e.g., 'twitter', 'facebook'
        
        # Example: redirect to your frontend with query param
        return f"{settings.LOGIN_REDIRECT_URL}?linked={provider}"

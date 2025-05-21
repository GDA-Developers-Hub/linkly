from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        token = request.GET.get("token")
        if token:
            try:
                validated = JWTAuthentication().get_validated_token(token)
                user = JWTAuthentication().get_user(validated)
                if user:
                    sociallogin.connect(request, user)
            except InvalidToken:
                pass
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Called after a social account is linked to an already logged-in user.
        """
        # You can dynamically build your redirect here
        provider = socialaccount.provider  # e.g., 'twitter', 'facebook'
        
        # Example: redirect to your frontend with query param
        return f"{settings.LOGIN_REDIRECT_URL}?linked={provider}"
    

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

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
                logger.error("Invalid token during pre_social_login")
                pass

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Called after a social account is linked to an already logged-in user.
        """
        try:
            # Get base redirect URL and ensure it's clean
            base_url = settings.LOGIN_REDIRECT_URL.strip()
            
            # Get the token from the request
            token = request.GET.get("token")
            
            # Remove any trailing slashes and clean any whitespace
            base_url = base_url.strip().rstrip('/')
            
            # Add the platform-connect path
            redirect_url = f"{base_url}/dashboard/platform-connect"
            
            # Add the linked parameter and token
            provider = socialaccount.provider
            if provider == "openid_connect":
                provider = "linkedin"  # Map openid_connect to linkedin for consistency
            
            # Build query parameters and properly encode them
            params = [f"linked={quote(provider.strip())}"]
            if token:
                params.append(f"token={quote(token.strip())}")
            
            # Add query parameters to URL
            redirect_url = f"{redirect_url}?{'&'.join(params)}"
            
            logger.info(f"Redirecting to: {redirect_url}")
            return redirect_url
            
        except Exception as e:
            logger.error(f"Error building redirect URL: {str(e)}")
            # Fallback to default dashboard
            return f"{settings.LOGIN_REDIRECT_URL.strip()}/dashboard"
    

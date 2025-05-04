from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import SocialMediaAccount
from .serializers import SocialMediaAccountSerializer
import requests
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class SocialAccountListView(generics.ListAPIView):
    serializer_class = SocialMediaAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SocialMediaAccount.objects.filter(user=self.request.user)

class ConnectSocialAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        platform = request.data.get('platform')
        auth_code = request.data.get('code')

        if not platform or not auth_code:
            return Response(
                {"error": "Platform and authorization code are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Handle different platform authentications
            if platform == 'instagram':
                return self.handle_instagram_auth(auth_code)
            elif platform == 'facebook':
                return self.handle_facebook_auth(auth_code)
            elif platform == 'twitter':
                return self.handle_twitter_auth(auth_code)
            elif platform == 'linkedin':
                return self.handle_linkedin_auth(auth_code)
            elif platform == 'tiktok':
                return self.handle_tiktok_auth(auth_code)
            else:
                return Response(
                    {"error": "Unsupported platform"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            logger.error(f"Error connecting {platform} account: {str(e)}")
            return Response(
                {"error": f"Failed to connect {platform} account: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def handle_instagram_auth(self, auth_code):
        # Exchange auth code for access token
        token_url = "https://api.instagram.com/oauth/access_token"
        token_data = {
            "client_id": settings.INSTAGRAM_CLIENT_ID,
            "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
            "code": auth_code
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if "access_token" not in token_json:
            raise Exception(f"Failed to get access token: {token_json.get('error_message')}")

        # Get user info
        user_info_url = "https://graph.instagram.com/me"
        user_info_params = {
            "fields": "id,username,account_type",
            "access_token": token_json["access_token"]
        }

        user_info_response = requests.get(user_info_url, params=user_info_params)
        user_info = user_info_response.json()

        # Create or update social media account
        account, created = SocialMediaAccount.objects.update_or_create(
            user=self.request.user,
            platform='instagram',
            account_id=user_info['id'],
            defaults={
                'username': user_info['username'],
                'access_token': token_json['access_token'],
                'account_type': user_info.get('account_type'),
                'token_expires_at': timezone.now() + timedelta(days=60),  # Instagram tokens typically expire in 60 days
                'status': 'active'
            }
        )

        return Response(SocialMediaAccountSerializer(account).data)

    def handle_facebook_auth(self, auth_code):
        # Similar implementation for Facebook
        pass

    def handle_twitter_auth(self, auth_code):
        # Similar implementation for Twitter
        pass

    def handle_linkedin_auth(self, auth_code):
        # Similar implementation for LinkedIn
        pass

    def handle_tiktok_auth(self, auth_code):
        # Similar implementation for TikTok
        pass

class DisconnectSocialAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        platform = request.data.get('platform')
        account_id = request.data.get('account_id')

        try:
            account = SocialMediaAccount.objects.get(
                user=request.user,
                platform=platform,
                account_id=account_id
            )

            # Revoke access token if possible
            self.revoke_platform_access(account)

            # Update account status
            account.status = 'revoked'
            account.save()

            return Response({"message": f"{platform} account disconnected successfully"})

        except SocialMediaAccount.DoesNotExist:
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error disconnecting {platform} account: {str(e)}")
            return Response(
                {"error": f"Failed to disconnect {platform} account: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def revoke_platform_access(self, account):
        if account.platform == 'instagram':
            # Revoke Instagram access token
            revoke_url = f"https://graph.instagram.com/{account.account_id}/permissions"
            requests.delete(revoke_url, params={"access_token": account.access_token})
        # Add similar revocation logic for other platforms

class RefreshSocialTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        platform = request.data.get('platform')
        account_id = request.data.get('account_id')

        try:
            account = SocialMediaAccount.objects.get(
                user=request.user,
                platform=platform,
                account_id=account_id
            )

            if account.platform == 'instagram':
                self.refresh_instagram_token(account)
            # Add similar refresh logic for other platforms

            return Response(SocialMediaAccountSerializer(account).data)

        except SocialMediaAccount.DoesNotExist:
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error refreshing {platform} token: {str(e)}")
            return Response(
                {"error": f"Failed to refresh {platform} token: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def refresh_instagram_token(self, account):
        refresh_url = "https://graph.instagram.com/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": account.access_token
        }

        response = requests.get(refresh_url, params=params)
        data = response.json()

        if "access_token" not in data:
            raise Exception(f"Failed to refresh token: {data.get('error', {}).get('message')}")

        account.access_token = data["access_token"]
        account.token_expires_at = timezone.now() + timedelta(days=60)
        account.save() 
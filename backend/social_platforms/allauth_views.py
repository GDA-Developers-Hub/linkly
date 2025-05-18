"""
Views for seamless integration of Django Allauth with Linkly's social platforms API.
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .allauth_integration import get_oauth_redirect_url
from .models import SocialPlatform, UserSocialAccount

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class SocialAuthInitView(APIView):
    """
    API view to initialize OAuth flow for any social platform 
    using Django Allauth under the hood.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        platform = request.data.get('platform')
        
        if not platform:
            return Response(
                {'error': 'Platform name is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Map our platform names to Allauth provider IDs if needed
        platform_to_provider = {
            'linkedin': 'linkedin_oauth2',
            'google': 'google',
            'facebook': 'facebook',
            'instagram': 'instagram',
            'twitter': 'twitter',
            'tiktok': 'tiktok',
            'youtube': 'youtube',
            'threads': 'threads',
            'pinterest': 'pinterest',
            'googleads': 'google_ads',
        }
        
        provider_id = platform_to_provider.get(platform, platform)
        
        # Get the OAuth redirect URL
        result = get_oauth_redirect_url(request, provider_id)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Store the state and platform in session for verification during callback
        request.session['oauth_state'] = result['state']
        request.session['oauth_platform'] = platform
        
        return Response({
            'authorization_url': result['authorization_url'],
            'state': result['state']
        })


class SocialAccountsView(APIView):
    """
    API view to get all social accounts connected to the current user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get all user social accounts
        accounts = UserSocialAccount.objects.filter(user=user)
        
        result = []
        for account in accounts:
            result.append({
                'id': account.id,
                'platform': account.platform.name,
                'account_id': account.account_id,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'profile_picture_url': account.profile_picture_url,
                'status': account.status,
                'is_primary': account.is_primary,
                'last_used_at': account.last_used_at.isoformat() if account.last_used_at else None,
                'created_at': account.created_at.isoformat(),
            })
        
        return Response(result)


class DisconnectSocialAccountView(APIView):
    """
    API view to disconnect a social account from the current user.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        account_id = request.data.get('account_id')
        
        if not account_id:
            return Response(
                {'error': 'Account ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            account = UserSocialAccount.objects.get(id=account_id, user=user)
            account.delete()
            
            # Also delete the corresponding Allauth SocialAccount if it exists
            from allauth.socialaccount.models import SocialAccount
            try:
                sa = SocialAccount.objects.get(uid=account.account_id, user=user)
                sa.delete()
            except SocialAccount.DoesNotExist:
                pass
                
            return Response({'success': True})
            
        except UserSocialAccount.DoesNotExist:
            return Response(
                {'error': 'Account not found'},
                status=status.HTTP_404_NOT_FOUND
            )

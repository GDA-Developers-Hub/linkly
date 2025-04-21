from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import PlatformCredentials
from ..serializers import PlatformCredentialsSerializer

class PlatformCredentialsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows clients to manage their OAuth credentials
    """
    serializer_class = PlatformCredentialsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only the credentials for the current user
        """
        return PlatformCredentials.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Save the current user with the credentials
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def platforms(self, request):
        """
        Return a list of supported platforms with their details
        """
        platforms = [
            {
                'id': choice[0],
                'name': choice[1],
                'scopes_required': self._get_platform_scopes(choice[0]),
                'uses_pkce': self._platform_uses_pkce(choice[0])
            }
            for choice in PlatformCredentials._meta.get_field('platform').choices
        ]
        return Response(platforms)
    
    def _get_platform_scopes(self, platform):
        """
        Return the required scopes for a platform
        """
        scopes = {
            'google': ['openid', 'email', 'profile'],
            'youtube': ['https://www.googleapis.com/auth/youtube.readonly'],
            'facebook': ['email', 'public_profile'],
            'twitter': ['tweet.read', 'users.read', 'offline.access'],
            'linkedin': ['r_liteprofile', 'r_emailaddress'],
            'instagram': ['basic'],
            'tiktok': ['user.info.basic'],
            'telegram': []
        }
        return scopes.get(platform, [])
    
    def _platform_uses_pkce(self, platform):
        """
        Return whether a platform uses PKCE
        """
        pkce_platforms = ['google', 'youtube', 'twitter']
        return platform in pkce_platforms 
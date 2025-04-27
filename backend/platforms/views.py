from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
import requests
import json
import logging

from .models import Platform, PlatformAccount
from .serializers import PlatformSerializer, PlatformAccountSerializer

logger = logging.getLogger(__name__)


class PlatformListView(generics.ListAPIView):
    queryset = Platform.objects.filter(is_active=True)
    serializer_class = PlatformSerializer
    permission_classes = [permissions.IsAuthenticated]


class PlatformAccountListView(generics.ListCreateAPIView):
    serializer_class = PlatformAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PlatformAccount.objects.filter(
            user=self.request.user
        ).select_related('platform').order_by('platform__name')


class PlatformAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlatformAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PlatformAccount.objects.filter(user=self.request.user)


class DisconnectPlatformView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk=None):
        try:
            account = PlatformAccount.objects.get(pk=pk, user=request.user)
            account.status = 'disconnected'
            account.save()
            
            return Response({"detail": "Account disconnected successfully"})
        except PlatformAccount.DoesNotExist:
            return Response(
                {"error": "Platform account not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class TwitterAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implementation would depend on the Twitter OAuth flow
        # This is a placeholder implementation
        redirect_uri = request.build_absolute_uri('/api/platforms/auth/callback/')
        return Response({
            "auth_url": f"https://twitter.com/oauth/authenticate?client_id={settings.TWITTER_API_KEY}&redirect_uri={redirect_uri}&state=twitter"
        })


class FacebookAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implementation would depend on the Facebook OAuth flow
        # This is a placeholder implementation
        redirect_uri = request.build_absolute_uri('/api/platforms/auth/callback/')
        return Response({
            "auth_url": f"https://www.facebook.com/v10.0/dialog/oauth?client_id={settings.FACEBOOK_APP_ID}&redirect_uri={redirect_uri}&state=facebook"
        })


class InstagramAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implementation would depend on the Instagram OAuth flow
        # This is a placeholder implementation
        redirect_uri = request.build_absolute_uri('/api/platforms/auth/callback/')
        return Response({
            "auth_url": f"https://api.instagram.com/oauth/authorize?client_id={settings.INSTAGRAM_CLIENT_ID}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code&state=instagram"
        })


class LinkedInAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Implementation would depend on the LinkedIn OAuth flow
        # This is a placeholder implementation
        redirect_uri = request.build_absolute_uri('/api/platforms/auth/callback/')
        return Response({
            "auth_url": f"https://www.linkedin.com/oauth/v2/authorization?client_id={settings.LINKEDIN_CLIENT_ID}&redirect_uri={redirect_uri}&state=linkedin&response_type=code&scope=r_liteprofile%20r_emailaddress%20w_member_social"
        })


class AuthCallbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # This would handle OAuth callbacks from various platforms
        # For simplicity, this is just a stub
        platform = request.GET.get('state', '')
        code = request.GET.get('code', '')
        
        if not platform or not code:
            return Response({"error": "Invalid callback parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process the OAuth response based on the platform
        # This is just a placeholder - actual implementation would depend on each platform's OAuth flow
        
        return Response({"message": f"Successfully authenticated with {platform}"})

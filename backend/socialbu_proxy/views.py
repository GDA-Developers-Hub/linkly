from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings

from .models import SocialBuToken, SocialPlatformConnection
from .serializers import (
    SocialBuTokenSerializer, 
    SocialBuAuthSerializer,
    SocialBuPostSerializer,
    SocialBuPostUpdateSerializer,
    SocialBuTeamSerializer,
    SocialBuTeamMemberSerializer,
    SocialPlatformConnectionSerializer
)
from .services import SocialBuService, SocialBuAPIError

class SocialBuProxyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_socialbu_service(self):
        """Get SocialBu service with user's token"""
        try:
            token_obj = SocialBuToken.objects.get(user=self.request.user)
            return SocialBuService(token=token_obj.access_token)
        except SocialBuToken.DoesNotExist:
            # If no token exists, try to authenticate with stored credentials
            if self.request.user.socialbu_email and self.request.user.socialbu_password:
                try:
                    service = SocialBuService()
                    result = service.authenticate(
                        self.request.user.socialbu_email,
                        self.request.user.socialbu_password
                    )
                    
                    # Store the token
                    token_obj, created = SocialBuToken.objects.update_or_create(
                        user=self.request.user,
                        defaults={
                            'access_token': result['token'],
                            'refresh_token': result.get('refresh_token', '')
                        }
                    )
                    
                    return SocialBuService(token=result['token'])
                except Exception as e:
                    # Log the error but return unauthenticated service
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to authenticate with SocialBu: {str(e)}")
            
            return SocialBuService()
    
    @action(detail=False, methods=['get'])
    def check_token(self, request):
        """Check if the user has a valid SocialBu token"""
        try:
            token_obj = SocialBuToken.objects.get(user=request.user)
            
            # Verify token with a simple API call
            service = SocialBuService(token=token_obj.access_token)
            try:
                # Try a simple API call
                service.get_accounts()
                return Response({'has_token': True})
            except SocialBuAPIError:
                # Token is invalid
                return Response({'has_token': False})
        except SocialBuToken.DoesNotExist:
            return Response({'has_token': False})
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user with SocialBu"""
        # This is a proxy to the SocialBu registration endpoint
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([name, email, password]):
            return Response({'detail': 'Name, email and password are required'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = SocialBuService()
            result = service.register(name, email, password)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def authenticate(self, request):
        """Authenticate with SocialBu API"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Authentication request received")
        logger.info(f"Request data: {request.data}")
        
        serializer = SocialBuAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        logger.info(f"Serializer valid data: {serializer.validated_data}")
        
        try:
            service = SocialBuService()
            
            # Get base_url from the request data if provided
            base_url = request.data.get('base_url')
            logger.info(f"Base URL from request: {base_url}")
            
            result = service.authenticate(
                serializer.validated_data['email'],
                serializer.validated_data['password'],
                base_url=base_url
            )
            
            # Verify that we got a token back
            if not result.get('token'):
                return Response(
                    {'detail': 'Authentication failed - no token received from SocialBu'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # If user is authenticated, store the token
            if request.user.is_authenticated:
                token_obj, created = SocialBuToken.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'access_token': result['token'],
                        'refresh_token': result.get('refresh_token', '')
                    }
                )
            
            return Response(result)
        except SocialBuAPIError as e:
            # Log the full error for debugging
            logger.error(f"SocialBu authentication error: {str(e)}")
            
            # Return a more detailed error message
            error_message = f"Authentication failed: {e.message}"
            return Response({'detail': error_message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any other exceptions
            logger.error(f"Unexpected error during SocialBu authentication: {str(e)}")
            
            return Response({'detail': f"Authentication error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def store_token(self, request):
        """Store a token obtained from direct API call"""
        token = request.data.get('token')
        
        if not token:
            return Response({'detail': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Store the token
            token_obj, created = SocialBuToken.objects.update_or_create(
                user=request.user,
                defaults={
                    'access_token': token,
                    'refresh_token': request.data.get('refresh_token', '')
                }
            )
            
            return Response({'success': True})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout from SocialBu API"""
        try:
            # Delete the token from our database
            SocialBuToken.objects.filter(user=request.user).delete()
            
            # Call SocialBu logout endpoint
            service = self.get_socialbu_service()
            result = service.logout()
            
            return Response({'detail': 'Successfully logged out'})
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def auth_redirect(self, request):
        """Redirect to SocialBu auth pages"""
        auth_type = request.query_params.get('type', 'login')
        
        if auth_type == 'register':
            return redirect('https://socialbu.com/auth/register')
        else:
            return redirect('https://socialbu.com/auth/login')
        
    @action(detail=False, methods=['post'])
    def get_connection_url(self, request):
        """Get URL for connecting a social platform"""
        provider = request.data.get('provider')
        account_id = request.data.get('account_id')
        
        if not provider:
            return Response({'detail': 'Provider is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a postback URL
        postback_url = request.build_absolute_uri(
            reverse('socialbu-connection-callback')
        )
        
        try:
            service = self.get_socialbu_service()
            result = service.get_connection_url(provider, postback_url, account_id)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def posts(self, request):
        """Get posts from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            limit = request.query_params.get('limit')
            post_status = request.query_params.get('status')
            result = service.get_posts(limit=limit, status=post_status)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def create_post(self, request):
        """Create a post in SocialBu API"""
        serializer = SocialBuPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_socialbu_service()
            result = service.create_post(serializer.validated_data)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_post(self, request, pk=None):
        """Update a post in SocialBu API"""
        serializer = SocialBuPostUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_socialbu_service()
            result = service.update_post(pk, serializer.validated_data)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_post(self, request, pk=None):
        """Delete a post in SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.delete_post(pk)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def media(self, request):
        """Get media from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.get_media()
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_media(self, request):
        """Upload media to SocialBu API"""
        if 'media' not in request.FILES:
            return Response({'detail': 'No media file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = self.get_socialbu_service()
            result = service.upload_media(request.FILES['media'])
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_media(self, request, pk=None):
        """Delete media from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.delete_media(pk)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def accounts(self, request):
        """Get accounts from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.get_accounts()
            
            # Store accounts in our database for reference
            for account in result:
                SocialPlatformConnection.objects.update_or_create(
                    user=request.user,
                    platform=account['platform'],
                    account_id=account['id'],
                    defaults={
                        'account_name': account['name'],
                        'status': account['status']
                    }
                )
            
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def disconnect_account(self, request, pk=None):
        """Disconnect an account from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.disconnect_account(pk)
            
            # Update status in our database
            try:
                connection = SocialPlatformConnection.objects.get(
                    user=request.user,
                    account_id=pk
                )
                connection.status = 'disconnected'
                connection.save()
            except SocialPlatformConnection.DoesNotExist:
                pass
            
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Get insights from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.get_insights()
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def post_insights(self, request, pk=None):
        """Get post insights from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.get_post_insights(pk)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        """Get notifications from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.get_notifications()
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def mark_notification_read(self, request, pk=None):
        """Mark a notification as read in SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.mark_notification_as_read(pk)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def create_team(self, request):
        """Create a team in SocialBu API"""
        serializer = SocialBuTeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_socialbu_service()
            result = service.create_team(serializer.validated_data['name'])
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_team_member(self, request, pk=None):
        """Add a team member in SocialBu API"""
        serializer = SocialBuTeamMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_socialbu_service()
            result = service.add_team_member(pk, serializer.validated_data['user_id'])
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def team_members(self, request, pk=None):
        """Get team members from SocialBu API"""
        try:
            service = self.get_socialbu_service()
            result = service.get_team_members(pk)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_team_member(self, request, pk=None):
        """Remove a team member from SocialBu API"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            service = self.get_socialbu_service()
            result = service.remove_team_member(pk, user_id)
            return Response(result)
        except SocialBuAPIError as e:
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)


class SocialBuConnectionCallbackView(APIView):
    """
    Handle callbacks from SocialBu OAuth flow
    """
    permission_classes = [permissions.AllowAny]  # Allow anonymous access for OAuth callbacks
    
    def get(self, request):
        # Extract parameters from the request
        platform = request.GET.get('platform')
        account_id = request.GET.get('account_id')
        account_name = request.GET.get('account_name')
        status = request.GET.get('status', 'connected')
        user_id = request.GET.get('user_id')
        
        if not all([platform, account_id, user_id]):
            return Response({'detail': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            
            # Store the connection in our database
            SocialPlatformConnection.objects.update_or_create(
                user=user,
                platform=platform,
                account_id=account_id,
                defaults={
                    'account_name': account_name or f"{platform.capitalize()} Account",
                    'status': status
                }
            )
            
            # Return success page with JavaScript to close the popup
            html_response = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Connection Successful</title>
                <style>
                    body {
                        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background-color: #f9fafb;
                        color: #111827;
                    }
                    .success-container {
                        text-align: center;
                        padding: 2rem;
                        background-color: white;
                        border-radius: 0.5rem;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        max-width: 24rem;
                    }
                    .success-icon {
                        color: #10b981;
                        font-size: 3rem;
                        margin-bottom: 1rem;
                    }
                    h1 {
                        font-size: 1.5rem;
                        font-weight: 600;
                        margin-bottom: 0.5rem;
                    }
                    p {
                        color: #6b7280;
                        margin-bottom: 1.5rem;
                    }
                </style>
            </head>
            <body>
                <div class="success-container">
                    <div class="success-icon">✓</div>
                    <h1>Connection Successful</h1>
                    <p>Your account has been connected successfully. This window will close automatically.</p>
                </div>
                <script>
                    // Close the popup window after a short delay
                    setTimeout(function() {
                        window.opener.postMessage({
                            type: 'SOCIAL_CONNECTION_SUCCESS',
                            platform: '%s',
                            accountId: '%s',
                            accountName: '%s'
                        }, '*');
                        window.close();
                    }, 2000);
                </script>
            </body>
            </html>
            """ % (platform, account_id, account_name or f"{platform.capitalize()} Account")
            
            from django.http import HttpResponse
            return HttpResponse(html_response)
            
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

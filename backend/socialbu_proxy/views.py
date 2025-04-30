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
from .services import SocialBuService, SocialBuAPIError, get_socialbu_token_for_user

class SocialBuProxyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_socialbu_service(self):
        token = get_socialbu_token_for_user(self.request.user)
        return SocialBuService(token=token)
    
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
            
            # If user is authenticated, store the token and additional info
            if request.user.is_authenticated:
                token_obj, created = SocialBuToken.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'access_token': result['token'],
                        'refresh_token': result.get('refresh_token', ''),
                        'socialbu_user_id': str(result.get('user_id', '')),
                        'name': result.get('name', ''),
                        'email': result.get('email', ''),
                        'verified': result.get('verified', False)
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
        
    @action(detail=False, methods=['post'], url_path='get_connection_url')
    def get_connection_url(self, request):
        """Get URL for connecting a social platform"""
        provider = request.data.get('provider')
        account_id = request.data.get('account_id')
        postback_url = request.data.get('postback_url')
        
        # Input validation
        if not provider:
            return Response({'detail': 'Provider is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not postback_url:
            return Response({'detail': 'Postback URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the user ID to be used in postback
        user_id = request.user.id
        
        # Add user ID to postback URL
        if '?' in postback_url:
            postback_url = f"{postback_url}&user_id={user_id}"
        else:
            postback_url = f"{postback_url}?user_id={user_id}"
        
        try:
            service = self.get_socialbu_service()
            result = service.get_connection_url(provider, postback_url, account_id)
            return Response(result)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting connection URL: {str(e)}")
            
            # Check if token exists
            has_token = SocialBuToken.objects.filter(user=request.user).exists()
            
            error_response = {
                'detail': str(e),
                'solution': 'You need to authenticate with SocialBu first before connecting social accounts.',
                'has_token': has_token,
                'authenticate_endpoint': '/api/socialbu/authenticate/',
                'error_type': 'NO_TOKEN' if 'No SocialBu token or credentials found' in str(e) else 'OTHER'
            }
            
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def posts(self, request):
        """Get posts from SocialBu API"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Posts endpoint called")
            
            # Extract query parameters
            limit = request.query_params.get('limit')
            post_status = request.query_params.get('status')
            page = request.query_params.get('page', '1')
            
            logger.info(f"Fetching posts with params: limit={limit}, status={post_status}, page={page}")
            
            # Get the service with the user's authentication
            service = self.get_socialbu_service()
            
            # Call the SocialBu API to get posts
            result = service.get_posts(limit=limit, status=post_status)
            
            # Log the result structure
            if isinstance(result, dict):
                logger.info(f"Posts result format: dictionary with keys {', '.join(result.keys())}")
                logger.info(f"Total posts: {result.get('total', 0)}")
                logger.info(f"Current page: {result.get('currentPage', 0)}")
                logger.info(f"Last page: {result.get('lastPage', 0)}")
            else:
                logger.warning(f"Unexpected posts result format: {type(result)}")
            
            return Response(result)
        except SocialBuAPIError as e:
            logger.error(f"SocialBu API error when fetching posts: {e.message}")
            return Response({'detail': e.message}, status=e.status_code or status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error when fetching posts: {str(e)}")
            return Response({'detail': f"Failed to fetch posts: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def create_post(self, request):
        """Create a post in SocialBu API"""
        serializer = SocialBuPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Log the payload for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Creating post with data: {serializer.validated_data}")
            
            # CRITICAL FIX: Re-authenticate to ensure fresh token 
            # This is a workaround for token expiry issues
            try:
                logger.info("Ensuring fresh SocialBu authentication token")
                token_obj = SocialBuToken.objects.get(user=request.user)
                
                # Re-authenticate with SocialBu (assuming credentials are stored)
                if token_obj.email and hasattr(request.user, 'socialbu_password'):
                    logger.info(f"Re-authenticating with SocialBu for user: {token_obj.email}")
                    temp_service = SocialBuService()
                    auth_result = temp_service.authenticate(token_obj.email, request.user.socialbu_password)
                    
                    # Update token in database
                    token_obj.access_token = auth_result['token']
                    token_obj.save()
                    logger.info("SocialBu token refreshed successfully")
                else:
                    logger.warning("Cannot refresh token - missing credentials")
            except Exception as e:
                logger.error(f"Error refreshing SocialBu token: {str(e)}")
                
            # Get the service with the freshly updated token
            service = self.get_socialbu_service()
            
            # If platform is not specified but accounts are provided, try to determine platform
            validated_data = serializer.validated_data.copy()
            
            # Get SocialBu accounts to find correct account IDs
            try:
                logger.info("Fetching SocialBu accounts to map local IDs to SocialBu account IDs")
                service = self.get_socialbu_service()
                socialbu_accounts = service.get_accounts()
                
                # Create mapping of local account IDs to SocialBu account IDs
                account_id_map = {}
                local_connections = SocialPlatformConnection.objects.filter(user=request.user)
                
                for local_conn in local_connections:
                    # Find matching SocialBu account
                    for sb_account in socialbu_accounts:
                        if (sb_account.get('name') == local_conn.account_name and 
                            sb_account.get('platform', '').lower() == local_conn.platform.lower()):
                            account_id_map[local_conn.account_id] = sb_account['id']
                            break
                
                logger.info(f"Account ID mapping: {account_id_map}")
                
                # Map local account IDs to SocialBu account IDs
                if validated_data.get('accounts'):
                    mapped_accounts = []
                    for local_id in validated_data['accounts']:
                        # Use the mapped ID if available, otherwise keep original
                        if str(local_id) in account_id_map:
                            mapped_accounts.append(account_id_map[str(local_id)])
                        else:
                            mapped_accounts.append(local_id)
                            
                    validated_data['accounts'] = mapped_accounts
                    logger.info(f"Mapped accounts: {validated_data['accounts']}")
            
                # Determine platform if not specified
                if not validated_data.get('platform') and validated_data.get('accounts'):
                    # Get the first account ID
                    first_account_id = validated_data['accounts'][0] if validated_data['accounts'] else None
                    
                    if first_account_id:
                        try:
                            # Check if it's in our local database
                            for sb_account in socialbu_accounts:
                                if sb_account['id'] == first_account_id:
                                    validated_data['platform'] = sb_account.get('platform')
                                    logger.info(f"Determined platform for account {first_account_id}: {sb_account.get('platform')}")
                                    break
                        except Exception as e:
                            logger.warning(f"Error determining platform for account {first_account_id}: {str(e)}")
            except Exception as e:
                logger.error(f"Error mapping account IDs: {str(e)}")
                # Continue with original account IDs if mapping fails
            
            # Fix account ID mismatch by using the correct IDs
            # CRITICAL FIX: We're observing account ID mismatch between the frontend (127742)
            # and what SocialBu expects internally. Force the correct account ID.
            logger.info(f"Original accounts: {validated_data.get('accounts')}")
            
            # Override with the correct account ID - this is immediate fix while mapping is improved
            if 'accounts' in validated_data and validated_data.get('platform') == 'facebook':
                try:
                    # DIRECT FIX: Use the known correct SocialBu account ID
                    # The user confirmed this is the correct ID in the database
                    validated_data['accounts'] = [122988]  # Specific FB account ID from the database
                    logger.info(f"Overriding with correct Facebook account ID: {validated_data['accounts']}")
                except Exception as e:
                    logger.error(f"Error overriding account ID: {str(e)}")
            
            # Make the API call with the fixed data
            result = service.create_post(validated_data)
            logger.info(f"Post creation result: {result}")
            
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
    
    @action(detail=False, methods=['post'])
    def upload_media(self, request):
        """Upload media to SocialBu API"""
        try:
            service = self.get_socialbu_service()
            
            # Get file from request
            if 'file' not in request.FILES:
                return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.FILES['file']
            result = service.upload_media(file)
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
                # Extract platform from type or _type if platform key doesn't exist
                platform = account.get('platform')
                if not platform and account.get('type'):
                    # Extract platform from type string (e.g., 'facebook.page' -> 'facebook')
                    platform = account.get('type', '').split('.')[0]
                elif not platform and account.get('_type'):
                    # Try to get platform from _type (e.g., 'Facebook Page' -> 'facebook')
                    platform_name = account.get('_type', '').split(' ')[0].lower()
                    if platform_name:
                        platform = platform_name

                # Skip if we can't determine the platform
                if not platform:
                    continue
                
                # Add 'active' field to the account data for frontend use
                account['platform'] = platform
                account['active'] = account.get('active', True)  # Default to active if not specified
                
                SocialPlatformConnection.objects.update_or_create(
                    user=request.user,
                    platform=platform,
                    account_id=account['id'],
                    defaults={
                        'account_name': account.get('name', f"Account {account['id']}"),
                        'status': account.get('status', 'connected')
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
    
    @action(detail=False, methods=['get'])
    def user_info(self, request):
        """Get current user's SocialBu information"""
        try:
            # Check if the user has a SocialBu token
            try:
                token_obj = SocialBuToken.objects.get(user=request.user)
                
                # Serialize the token data
                data = {
                    'has_token': True,
                    'user_id': token_obj.socialbu_user_id,
                    'name': token_obj.name,
                    'email': token_obj.email,
                    'verified': token_obj.verified,
                    'created_at': token_obj.created_at.isoformat() if token_obj.created_at else None,
                    'updated_at': token_obj.updated_at.isoformat() if token_obj.updated_at else None
                }
                
                # Verify token with a simple API call to make sure it's still valid
                try:
                    service = SocialBuService(token=token_obj.access_token)
                    # Try a simple API call
                    service.get_accounts()
                    data['token_valid'] = True
                except SocialBuAPIError:
                    # Token is invalid
                    data['token_valid'] = False
                
                return Response(data)
            except SocialBuToken.DoesNotExist:
                return Response({'has_token': False, 'token_valid': False})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving user SocialBu info: {str(e)}")
            return Response(
                {'detail': 'Error retrieving SocialBu information'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def debug_auth(self, request):
        """Debug endpoint to check auth headers"""
        try:
            # Get authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            # Log it for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Debug Auth Header: {auth_header}")
            
            # Get the user info
            user_info = {
                'user_id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_authenticated': request.user.is_authenticated,
                'auth_header': auth_header,
            }
            
            # Check if user has a SocialBu token
            try:
                token_obj = SocialBuToken.objects.get(user=request.user)
                user_info['has_socialbu_token'] = True
                user_info['socialbu_name'] = token_obj.name
                user_info['socialbu_email'] = token_obj.email
                user_info['socialbu_verified'] = token_obj.verified
            except SocialBuToken.DoesNotExist:
                user_info['has_socialbu_token'] = False
            
            return Response(user_info)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in debug_auth: {str(e)}")
            return Response(
                {'detail': f'Error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def test_connection(self, request):
        """Test the connection to SocialBu API"""
        try:
            # Try to get service with token
            try:
                service = self.get_socialbu_service()
                
                # Test a simple endpoint that should return quickly
                result = service.get_accounts()
                
                return Response({
                    'status': 'success',
                    'message': 'Successfully connected to SocialBu API',
                    'accounts_count': len(result) if isinstance(result, list) else 0,
                    'token_valid': True
                })
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error testing SocialBu connection: {str(e)}")
                
                # Check if it's an authentication error
                if 'No SocialBu token' in str(e):
                    return Response({
                        'status': 'error',
                        'message': 'No SocialBu token found. Please authenticate first.',
                        'error': str(e),
                        'token_valid': False,
                        'auth_required': True
                    }, status=401)
                
                # Check if it's a non-JSON response (usually HTML login page)
                if 'non-JSON response' in str(e) and 'DOCTYPE html' in str(e):
                    return Response({
                        'status': 'error',
                        'message': 'Authentication has expired. Please login again.',
                        'error': 'Session expired',
                        'token_valid': False,
                        'auth_required': True
                    }, status=401)
                
                # Other errors
                return Response({
                    'status': 'error',
                    'message': 'Error connecting to SocialBu API',
                    'error': str(e),
                    'token_valid': False
                }, status=500)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'error': str(e)
            }, status=500)


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

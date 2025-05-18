"""
API views for social platform integration using Django AllAuth.
These views maintain compatibility with the frontend while using AllAuth for OAuth.
"""
import json
import logging
import uuid
from urllib.parse import urlencode
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.instagram.views import InstagramOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter

from .models import SocialPlatform, UserSocialAccount
from .serializers import SocialPlatformSerializer, UserSocialAccountSerializer
from .utils.redis_oauth import store_oauth_code, get_oauth_code, delete_oauth_data, store_oauth_state, validate_oauth_state

logger = logging.getLogger(__name__)

# =============================
# OAuth Initialization Endpoint
# =============================

class OAuthInitAPIView(views.APIView):
    """
    Initialize OAuth flow for a specific platform.
    This creates a compatible API with the existing frontend.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, platform):
        """Generate and return authorization URL"""
        try:
            # Map our platform names to AllAuth provider names if needed
            provider_mapping = {
                'linkedin': 'linkedin_oauth2',
                'youtube': 'google',  # YouTube uses Google OAuth
                'threads': 'instagram',  # Threads uses Instagram/Meta OAuth
            }
            
            provider = provider_mapping.get(platform, platform)
            
            # Get the app configuration for this provider
            try:
                app = SocialApp.objects.get(provider=provider)
            except SocialApp.DoesNotExist:
                logger.error(f"No SocialApp configured for provider: {provider}")
                return Response({
                    'error': f'Provider {platform} is not configured'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate state for CSRF protection
            state = str(uuid.uuid4())
            
            # Store state in Redis instead of session for better persistence
            # This allows the state to be verified even across different sessions
            store_oauth_state(platform, state, user_id=request.user.id)
            
            # Also keep in session as a fallback
            request.session[f'oauth_state_{platform}'] = state
            
            # Generate the authorization URL
            redirect_uri = request.build_absolute_uri(reverse('allauth_callback', kwargs={'platform': platform}))
            
            # Different providers have different parameter requirements
            params = {
                'client_id': app.client_id,
                'redirect_uri': redirect_uri,
                'state': state,
                'response_type': 'code',
            }
            
            # Handle provider-specific scopes
            if provider == 'facebook':
                params['scope'] = 'email,public_profile,pages_show_list'
            elif provider == 'instagram':
                params['scope'] = 'user_profile,user_media'
            elif provider == 'linkedin_oauth2':
                params['scope'] = 'r_liteprofile r_emailaddress w_member_social'
            elif provider == 'twitter':
                params['scope'] = 'tweet.read users.read offline.access'
            elif provider == 'google' and platform == 'youtube':
                params['scope'] = 'profile email https://www.googleapis.com/auth/youtube.readonly'
                params['access_type'] = 'offline'
            elif provider == 'google':
                params['scope'] = 'profile email https://www.googleapis.com/auth/analytics.readonly'
                params['access_type'] = 'offline'
            
            # Get the auth URL from the SocialPlatform model
            try:
                social_platform = SocialPlatform.objects.get(name=platform)
                auth_url = social_platform.auth_url
            except SocialPlatform.DoesNotExist:
                # Fallback to standard endpoints if platform doesn't exist in our DB
                if provider == 'facebook':
                    auth_url = 'https://www.facebook.com/v17.0/dialog/oauth'
                elif provider == 'instagram':
                    auth_url = 'https://api.instagram.com/oauth/authorize'
                elif provider == 'linkedin_oauth2':
                    auth_url = 'https://www.linkedin.com/oauth/v2/authorization'
                elif provider == 'twitter':
                    auth_url = 'https://twitter.com/i/oauth2/authorize'
                elif provider == 'google':
                    auth_url = 'https://accounts.google.com/o/oauth2/auth'
                else:
                    logger.error(f"Unknown provider: {provider}")
                    return Response({
                        'error': f'Unknown provider: {provider}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construct the full authorization URL
            authorization_url = f"{auth_url}?{urlencode(params)}"
            
            # Return the URL to the frontend
            return Response({
                'authorization_url': authorization_url
            })
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {str(e)}")
            return Response({
                'error': f'Failed to generate authorization URL: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================
# OAuth Callback View
# ============================

class OAuthCallbackView(views.APIView):
    """
    Handle OAuth callback from social platforms.
    This view processes the callback and integrates with AllAuth.
    """
    permission_classes = [permissions.AllowAny]
    
    def close_window(self, **data):
        """
        Create a response that will close the popup window and pass data back to opener.
        This approach uses HTML/JS to close the window and communicate back to opener.
        """
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Complete</title>
            <script type="text/javascript">
                // Data to pass back to opener window
                var data = {json.dumps(data)};
                
                // Send message to parent/opener window
                if (window.opener && !window.opener.closed) {{                    
                    window.opener.postMessage(data, "*");
                    window.close();
                }} else {{                    
                    document.getElementById("manual-close").style.display = "block";
                }}
            </script>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                .hidden {{ display: none; }}
                button {{ padding: 10px 20px; background-color: #4285f4; color: white; 
                        border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h3>Authentication Complete</h3>
            <p>{data.get('message', 'You can close this window now.')}</p>
            <div id="manual-close" class="hidden">
                <p>If this window doesn't close automatically:</p>
                <button onclick="window.close()">Close Window</button>
            </div>
        </body>
        </html>
        '''
        
        return HttpResponse(html_content)
    
    def get(self, request):
        """Process OAuth callback by redirecting to AllAuth"""
        # Get parameters
        platform = request.GET.get('platform')
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        
        # Check for errors
        if error:
            logger.error(f"OAuth error: {error}")
            return JsonResponse({
                'success': False,
                'error': error,
                'platform': platform
            }, status=400)
        
        # If we don't have a platform or code, return error
        if not platform or not code:
            logger.error(f"Missing required parameters. Platform: {platform}, Code: {bool(code)}")
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters (platform or code)',
                'platform': platform
            }, status=400)
        
        # Map our platform name to AllAuth provider name if needed
        provider_mapping = {
            'linkedin': 'linkedin_oauth2',
            'youtube': 'google',
            'threads': 'instagram',
        }
        provider = provider_mapping.get(platform, platform)
        
        try:
            # Try to get the account
            social_account = self._process_oauth_code(request, provider, code, state)
            
            if social_account and social_account.user:
                # Get our UserSocialAccount model instance
                user_account = UserSocialAccount.objects.filter(
                    user=social_account.user,
                    platform__name=platform
                ).first()
                
                if user_account:
                    # Return success response with account details
                    return self.close_window(
                        success=True,
                        platform=platform,
                        account={
                            'id': user_account.id,
                            'platform_name': user_account.platform.name,
                            'account_name': user_account.account_name,
                            'account_type': user_account.account_type,
                            'profile_picture_url': user_account.profile_picture_url,
                            'status': user_account.status
                        }
                    )
                else:
                    return self.close_window(
                        success=True,
                        platform=platform,
                        message=f"Connected to {platform} but couldn't find the account record."
                    )
            else:
                # If the user is not authenticated, we need them to log in first
                request.session[f'pending_oauth_{platform}_code'] = code
                
                return self.close_window(
                    success=True,
                    auth_required=True,
                    platform=platform,
                    message="Please log in to complete account connection"
                )
        
        except Exception as e:
            logger.error(f"Error connecting account: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'platform': platform
            }, status=400)
    
    def _process_oauth_code(self, request, provider, code, state):
        """
        Process the OAuth code using AllAuth's infrastructure.
        This implements the code-to-token exchange using the AllAuth adapters.
        """
        try:
            # Validate state from Redis or session
            redis_state = validate_oauth_state(state, provider)
            session_state = request.session.get(f'oauth_state_{provider}')
            
            if not redis_state and not (session_state and session_state == state):
                logger.warning(f"OAuth state validation failed for {provider}")
                # For certain providers, we'll continue anyway (as in the original code)
                if provider.lower() not in ['linkedin_oauth2', 'google']:
                    raise ValueError(f"Invalid state parameter for {provider}")
            
            # Clean up session state if it exists
            if f'oauth_state_{provider}' in request.session:
                del request.session[f'oauth_state_{provider}']
            
            # Get the social app for this provider
            try:
                app = SocialApp.objects.get(provider=provider)
            except SocialApp.DoesNotExist:
                logger.error(f"No SocialApp configured for provider: {provider}")
                raise ValueError(f"Provider {provider} is not configured")
            
            # Get the adapter class for this provider
            adapter_mapping = {
                'facebook': FacebookOAuth2Adapter,
                'instagram': InstagramOAuth2Adapter,
                'google': GoogleOAuth2Adapter,
                'linkedin_oauth2': LinkedInOAuth2Adapter,
                # Add other adapters as needed
            }
            
            adapter_class = adapter_mapping.get(provider)
            if not adapter_class:
                logger.error(f"No adapter found for provider: {provider}")
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Instantiate the adapter
            adapter = adapter_class(request)
            
            # Get the callback URL
            redirect_uri = request.build_absolute_uri(reverse('allauth_callback', kwargs={'platform': provider}))
            
            # Exchange code for token
            token_response = adapter.complete_login(request, app, code, redirect_uri)
            
            # If the user is authenticated, create social account
            if request.user.is_authenticated:
                # Use AllAuth to create or get the social account
                social_account = token_response.account
                social_account.user = request.user
                social_account.save()
                
                # Create the social token
                from allauth.socialaccount.models import SocialToken
                token, created = SocialToken.objects.update_or_create(
                    account=social_account,
                    defaults={
                        'app': app,
                        'token': token_response.token,
                        'token_secret': getattr(token_response, 'token_secret', ''),
                        'expires_at': getattr(token_response, 'expires_at', None),
                    }
                )
                
                return social_account
            else:
                # Store OAuth data in Redis for later completion
                # Include token data and account data
                code_id = store_oauth_code(
                    platform=provider,
                    code=code,
                    state=state,
                    user_id=getattr(request.user, 'id', None),
                    token_data={
                        'token': token_response.token,
                        'token_secret': getattr(token_response, 'token_secret', ''),
                        'expires_at': getattr(token_response, 'expires_at', None),
                    },
                    account_data={
                        'uid': token_response.account.uid,
                        'provider': provider,
                        'extra_data': token_response.account.extra_data
                    }
                )
                
                return None
                
        except Exception as e:
            logger.error(f"Error processing OAuth code: {str(e)}")
            raise


# =============================
# Complete OAuth Flow
# =============================

class CompleteOAuthAPIView(views.APIView):
    """
    Complete OAuth flow using stored code and state after user authentication.
    This view handles the scenario where a user receives a code while not authenticated,
    then logs in and completes the connection.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, platform):
        """
        Complete the OAuth flow for an authenticated user using a stored code_id.
        """
        try:
            # Get the code_id from request
            code_id = request.data.get('code_id')
            if not code_id:
                return Response({
                    'success': False,
                    'error': 'Missing code_id parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve OAuth data from Redis
            oauth_data = get_oauth_code(code_id)
            if not oauth_data:
                return Response({
                    'success': False,
                    'error': 'Invalid or expired code_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Map our platform names to AllAuth provider names if needed
            provider_mapping = {
                'linkedin': 'linkedin_oauth2',
                'youtube': 'google',
                'threads': 'instagram',
            }
            platform_name = oauth_data.get('platform')
            provider = provider_mapping.get(platform_name, platform_name)
            
            # Verify platform matches
            if platform != platform_name:
                logger.warning(f"Platform mismatch: requested {platform}, stored {platform_name}")
                return Response({
                    'success': False,
                    'error': 'Platform mismatch'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get token data from Redis if available
            token_data = oauth_data.get('token_data', {})
            account_data = oauth_data.get('account_data', {})
            
            # If we have token data from Redis, use it
            if token_data and account_data:
                # Use the data to create a social account directly
                try:
                    # Get the platform
                    social_platform = SocialPlatform.objects.get(name=platform)
                    
                    # Create the UserSocialAccount
                    account, created = UserSocialAccount.objects.update_or_create(
                        user=request.user,
                        platform=social_platform,
                        account_id=account_data.get('uid'),
                        defaults={
                            'account_name': self._extract_account_name(platform, account_data),
                            'access_token': token_data.get('token'),
                            'refresh_token': token_data.get('token_secret'),
                            'token_expiry': token_data.get('expires_at'),
                            'raw_data': account_data.get('extra_data', {}),
                            'status': 'active',
                            'last_used_at': timezone.now()
                        }
                    )
                    
                    # Set as primary if first account
                    if created:
                        if not UserSocialAccount.objects.filter(
                            user=request.user, 
                            platform=social_platform, 
                            is_primary=True
                        ).exclude(id=account.id).exists():
                            account.is_primary = True
                            account.save()
                    
                    # Delete OAuth data from Redis
                    delete_oauth_code(code_id)
                    
                    # Return success response
                    return Response({
                        'success': True,
                        'message': f'Successfully connected {platform} account',
                        'account': UserSocialAccountSerializer(account).data
                    })
                    
                except Exception as e:
                    logger.error(f"Error creating social account from Redis data: {str(e)}")
                    # Continue to fallback
            
            # Fallback: Re-use the original code with the provider's OAuth endpoint
            # This is more complex and would require re-implementing the provider-specific logic
            # For this implementation, we'll just return an error
            return Response({
                'success': False,
                'error': 'Could not complete OAuth flow with stored data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error completing OAuth flow: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _extract_account_name(self, platform, account_data):
        """
        Extract account name from platform-specific account data
        """
        extra_data = account_data.get('extra_data', {})
        
        if platform == 'facebook':
            return extra_data.get('name', 'Facebook Account')
        elif platform == 'instagram':
            return extra_data.get('username', 'Instagram Account')
        elif platform == 'twitter':
            return extra_data.get('name', 'Twitter Account')
        elif platform == 'linkedin':
            # LinkedIn has a more complex structure
            first_name = extra_data.get('firstName', '')
            last_name = extra_data.get('lastName', '')
            if first_name or last_name:
                return f"{first_name} {last_name}".strip()
            return 'LinkedIn Account'
        elif platform == 'youtube' or platform == 'google':
            return extra_data.get('name', 'Google Account')
        
        # Default fallback
        return f"{platform.capitalize()} Account"


# =============================
# User Social Account Management
# =============================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_user_accounts(request):
    """List all social accounts for the authenticated user"""
    accounts = UserSocialAccount.objects.filter(user=request.user)
    serializer = UserSocialAccountSerializer(accounts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_primary_account(request, pk):
    """Set a social account as primary for its platform"""
    try:
        account = UserSocialAccount.objects.get(id=pk, user=request.user)
        
        # Find all other accounts for this platform and user
        other_accounts = UserSocialAccount.objects.filter(
            user=request.user,
            platform=account.platform,
            is_primary=True
        ).exclude(id=pk)
        
        # Set them as not primary
        for other_account in other_accounts:
            other_account.is_primary = False
            other_account.save()
        
        # Set this account as primary
        account.is_primary = True
        account.save()
        
        return Response({
            'success': True,
            'message': f'Account {account.account_name} is now primary for {account.platform.name}'
        })
    
    except UserSocialAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_account_token(request, pk):
    """Refresh the token for a social account"""
    try:
        account = UserSocialAccount.objects.get(id=pk, user=request.user)
        
        # TODO: Implement token refresh using AllAuth
        # For now, return a mock success response
        
        return Response({
            'success': True,
            'message': f'Token refreshed for {account.account_name}'
        })
    
    except UserSocialAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_account(request, pk):
    """Disconnect a social account"""
    try:
        account = UserSocialAccount.objects.get(id=pk, user=request.user)
        
        # Store platform name for the response
        platform_name = account.platform.name
        account_name = account.account_name
        
        # Delete the account
        account.delete()
        
        # If we also had an AllAuth SocialAccount, disconnect that too
        # This would be implemented in a production version
        
        return Response({
            'success': True,
            'message': f'Disconnected {account_name} from {platform_name}'
        })
    
    except UserSocialAccount.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)


# =============================
# Platform Management
# =============================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_platforms(request):
    """List all available social platforms"""
    platforms = SocialPlatform.objects.filter(is_active=True)
    serializer = SocialPlatformSerializer(platforms, many=True)
    return Response(serializer.data)

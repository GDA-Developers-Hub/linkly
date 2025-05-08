from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError

import json
import logging
import uuid
import urllib.parse

from .models import SocialPlatform, UserSocialAccount
from .serializers import SocialPlatformSerializer, UserSocialAccountSerializer, SocialAccountDetailSerializer
from .services import get_oauth_manager, connect_social_account, refresh_token_if_needed
from .oauth.twitter import get_twitter_auth_url, handle_twitter_callback

logger = logging.getLogger(__name__)

class SocialPlatformViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing available social platforms
    """
    queryset = SocialPlatform.objects.filter(is_active=True)
    serializer_class = SocialPlatformSerializer
    permission_classes = [IsAuthenticated]
    

class UserSocialAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing user's social media accounts
    """
    serializer_class = UserSocialAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the user's own social accounts"""
        return UserSocialAccount.objects.filter(user=self.request.user).select_related('platform')
    
    def get_serializer_class(self):
        """Return different serializers based on action"""
        if self.action == 'retrieve' or self.action == 'detail':
            return SocialAccountDetailSerializer
        return UserSocialAccountSerializer
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set an account as primary for its platform"""
        account = self.get_object()
        
        # Get all other accounts for the same platform and user
        UserSocialAccount.objects.filter(
            user=request.user,
            platform=account.platform,
            is_primary=True
        ).exclude(pk=account.pk).update(is_primary=False)
        
        # Set this account as primary
        account.is_primary = True
        account.save()
        
        return Response({'status': 'success', 'message': 'Account set as primary'})
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh the token for this account if possible"""
        account = self.get_object()
        
        if not account.can_refresh:
            return Response(
                {'status': 'error', 'message': 'This account cannot refresh its token'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        success = refresh_token_if_needed(account)
        
        if success:
            return Response({'status': 'success', 'message': 'Token refreshed successfully'})
        else:
            return Response(
                {'status': 'error', 'message': 'Failed to refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Disconnect a social media account"""
        account = self.get_object()
        was_primary = account.is_primary
        platform = account.platform
        
        # Delete the account
        account.delete()
        
        # If this was a primary account, set another account as primary if available
        if was_primary:
            other_account = UserSocialAccount.objects.filter(
                user=request.user,
                platform=platform
            ).first()
            
            if other_account:
                other_account.is_primary = True
                other_account.save()
                
        return Response(status=status.HTTP_204_NO_CONTENT)


class OAuthInitView(views.APIView):
    """
    Initialize OAuth flow for a specific platform
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, platform):
        """Generate and return authorization URL"""
        try:
            # Log the request
            logger.info(f"OAuth init request for platform: {platform} from user: {request.user.email}")
            
            # Check if platform exists
            try:
                social_platform = SocialPlatform.objects.get(name=platform, is_active=True)
            except SocialPlatform.DoesNotExist:
                logger.error(f"Platform {platform} not found or not active")
                return Response(
                    {'error': f"Platform {platform} is not available"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Special handling for Twitter using PKCE
            if platform == 'twitter':
                logger.info("Using special Twitter PKCE OAuth flow")
                auth_url = get_twitter_auth_url(request, request.user)
                
                # Verify URL contains required parameters
                if 'code_challenge=' not in auth_url or 'code_challenge_method=' not in auth_url:
                    logger.error("Twitter auth URL is missing PKCE parameters!")
                    logger.info(f"Generated URL: {auth_url}")
                    
                    # If missing, add them explicitly as a fallback
                    import secrets, hashlib, base64
                    
                    # Generate code verifier
                    code_verifier = secrets.token_urlsafe(64)[:43]  # 43 chars is Twitter's min requirement
                    request.session['twitter_code_verifier'] = code_verifier
                    
                    # Generate code challenge
                    code_challenge = base64.urlsafe_b64encode(
                        hashlib.sha256(code_verifier.encode('utf-8')).digest()
                    ).decode('utf-8').rstrip('=')
                    
                    # Append the missing parameters
                    if 'code_challenge=' not in auth_url:
                        auth_url += f"&code_challenge={urllib.parse.quote(code_challenge)}"
                    if 'code_challenge_method=' not in auth_url:
                        auth_url += "&code_challenge_method=S256"
                    
                    logger.info(f"Fixed URL: {auth_url}")
                else:
                    logger.info("Twitter auth URL contains all required PKCE parameters")
            else:
                # Generate unique state for CSRF protection
                state = str(uuid.uuid4())
                request.session[f'oauth_state_{platform}'] = state
                
                # Build the authorization URL using the platform's stored credentials
                auth_url = (
                    f"{social_platform.auth_url}"
                    f"?client_id={social_platform.client_id}"
                    f"&redirect_uri={urllib.parse.quote(social_platform.redirect_uri)}"
                    f"&response_type=code"
                    f"&scope={urllib.parse.quote(social_platform.scope)}"
                    f"&state={state}"
                )
            
            logger.info(f"Generated authorization URL for {platform}: {auth_url[:100]}...")
            
            return Response({
                'authorization_url': auth_url
            })
            
        except Exception as e:
            logger.error(f"Error initializing OAuth flow: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PublicOAuthInitView(views.APIView):
    """
    Initialize OAuth flow for a specific platform without requiring authentication
    This is a simplified version for demonstration purposes
    """
    permission_classes = [AllowAny]
    
    def get(self, request, platform):
        """Generate and return authorization URL"""
        try:
            # Log the request
            logger.info(f"Public OAuth init request for platform: {platform}")
            
            # Check if platform exists
            try:
                social_platform = SocialPlatform.objects.get(name=platform, is_active=True)
            except SocialPlatform.DoesNotExist:
                logger.error(f"Platform {platform} not found or not active")
                return Response(
                    {'error': f"Platform {platform} is not available"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Generate unique state for demo purposes
            state = "demo-state-" + str(uuid.uuid4())[:8]
            
            # Build the authorization URL using the platform's stored credentials
            auth_url = (
                f"{social_platform.auth_url}"
                f"?client_id={social_platform.client_id}"
                f"&redirect_uri={urllib.parse.quote(social_platform.redirect_uri)}"
                f"&response_type=code"
                f"&scope={urllib.parse.quote(social_platform.scope)}"
                f"&state={state}"
            )
            
            logger.info(f"Generated public authorization URL for {platform} with client ID: {social_platform.client_id[:10]}...")
            
            return Response({
                'authorization_url': auth_url
            })
            
        except Exception as e:
            logger.error(f"Error initializing public OAuth flow: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(login_required, name='dispatch')
class OAuthCallbackView(views.APIView):
    """
    Handle OAuth callback from social platforms
    """
    
    def get(self, request):
        """Process OAuth callback and create social account"""
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
            
        # Validate state for CSRF protection
        expected_state = request.session.get(f'oauth_state_{platform}')
        if not expected_state or expected_state != state:
            logger.error(f"OAuth state mismatch. Expected: {expected_state}, Got: {state}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid state parameter',
                'platform': platform
            }, status=400)
            
        # Clean up session
        if f'oauth_state_{platform}' in request.session:
            del request.session[f'oauth_state_{platform}']
            
        try:
            # Connect social account
            account = connect_social_account(request.user, platform, code)
            
            # Return success response with account details
            return JsonResponse({
                'success': True,
                'platform': platform,
                'account': {
                    'id': account.id,
                    'platform_name': account.platform.name,
                    'account_name': account.account_name,
                    'account_type': account.account_type,
                    'profile_picture_url': account.profile_picture_url,
                    'status': account.status
                }
            })
            
        except Exception as e:
            logger.error(f"Error connecting account: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'platform': platform
            }, status=400)


class SocialAccountPostView(views.APIView):
    """
    Post content to social media accounts
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        """Create a post on social media platforms"""
        # Get post data
        post_data = request.data
        
        # Validate data
        if not post_data.get('text') and not post_data.get('media_urls'):
            return Response(
                {'error': 'Post must contain text or media'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get target platforms
        platform_ids = post_data.get('platform_ids', [])
        account_ids = post_data.get('account_ids', [])
        
        if not platform_ids and not account_ids:
            return Response(
                {'error': 'Must specify at least one platform or account'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get accounts to post to
        accounts = []
        
        # If specific accounts provided
        if account_ids:
            accounts.extend(
                UserSocialAccount.objects.filter(
                    id__in=account_ids,
                    user=request.user,
                    status='active'
                )
            )
            
        # If platforms provided, use primary accounts
        if platform_ids:
            platform_accounts = UserSocialAccount.objects.filter(
                platform_id__in=platform_ids,
                user=request.user,
                is_primary=True,
                status='active'
            )
            accounts.extend(platform_accounts)
            
        if not accounts:
            return Response(
                {'error': 'No valid accounts found for the specified platforms'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Initialize results
        results = []
        
        # Post to each account
        for account in accounts:
            try:
                # Refresh token if needed
                if account.is_expired:
                    if not refresh_token_if_needed(account):
                        results.append({
                            'account_id': account.id,
                            'platform': account.platform.name,
                            'success': False,
                            'error': 'Token expired and could not be refreshed'
                        })
                        continue
                
                # Platform-specific posting logic would be implemented here
                # For now we'll just record the attempt
                
                # Update account usage timestamp
                account.last_used_at = timezone.now()
                account.save()
                
                results.append({
                    'account_id': account.id,
                    'platform': account.platform.name,
                    'success': True,
                    'post_id': 'mock_post_id',  # This would be the actual post ID from the platform
                })
                
            except Exception as e:
                logger.error(f"Error posting to {account.platform.name}: {str(e)}")
                results.append({
                    'account_id': account.id,
                    'platform': account.platform.name,
                    'success': False,
                    'error': str(e)
                })
                
        return Response({
            'results': results
        })


class TwitterOAuthCallbackView(views.APIView):
    """
    Handle OAuth callback specifically for Twitter services without requiring prior authentication
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access to this view
    
    def get(self, request):
        """Process Twitter OAuth callback and create social account"""
        # Get parameters
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        denied = request.GET.get('denied')
        
        # Log the full request and session for debugging
        logger.info(f"Twitter OAuth callback received: {request.GET}")
        logger.info(f"Session data: oauth_state_twitter={request.session.get('oauth_state_twitter')}")
        logger.info(f"Session data: twitter_code_verifier={bool(request.session.get('twitter_code_verifier'))}")
        logger.info(f"Current user authentication status: {request.user.is_authenticated}")
        
        # Check if user denied access
        if denied:
            logger.error(f"User denied Twitter authorization: {denied}")
            return self.close_window(success=False, error="Authorization was denied by user")
        
        # Check for errors
        if error:
            logger.error(f"Twitter OAuth error: {error}")
            return self.close_window(success=False, error=error)
        
        # Ensure we have the code
        if not code:
            logger.error("No authorization code received from Twitter")
            return self.close_window(success=False, error="No authorization code received")
            
        try:
            # Check authentication status
            if not request.user.is_authenticated:
                logger.warning("User not authenticated during Twitter callback - returning success with auth required flag")
                # Return a special response for frontend to handle unauthenticated state
                return self.close_window(
                    success=True,
                    platform='twitter',
                    auth_required=True,
                    auth_data={
                        'code': code,
                        'state': state
                    }
                )
            
            # User is authenticated, proceed normally
            account = handle_twitter_callback(request, request.user, code, state)
            
            # Return success response
            return self.close_window(
                success=True,
                account_name=account.account_name,  # Changed from username to account_name
                platform='twitter'
            )
            
        except Exception as e:
            logger.error(f"Error connecting Twitter account: {str(e)}")
            return self.close_window(success=False, error=str(e))
    
    def close_window(self, success=True, account_name=None, platform=None, error=None, auth_required=False, auth_data=None):
        """Return an HTML page that closes the popup window and sends a message to the opener"""
        context = {
            'success': success,
            'message': 'Twitter account connected successfully' if success and not auth_required 
                     else 'Authentication required to complete Twitter connection' if auth_required 
                     else f'Error: {error}',
            'account_name': account_name,
            'platform': platform,
            'error': error,
            'auth_required': auth_required,
            'auth_data': auth_data
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{'Success' if success else 'Error'} - Twitter Authorization</title>
            <script>
                console.log('Twitter OAuth callback window loaded');
                
                function sendMessageToParent() {{
                    try {{
                        console.log('Sending message to parent window:', {json.dumps(context)});
                        window.opener.postMessage(
                            JSON.stringify({json.dumps(context)}),
                            "*"
                        );
                        console.log('Message sent successfully');
                        
                        // Add a slight delay before closing to ensure message is processed
                        setTimeout(function() {{
                            console.log('Closing popup window');
                            window.close();
                        }}, 1000);
                    }} catch(e) {{
                        console.error('Error sending message:', e);
                        document.getElementById('error').textContent = 'Error: ' + e.message;
                        document.getElementById('error').style.display = 'block';
                    }}
                }}
                
                window.onload = function() {{
                    if (window.opener) {{
                        console.log('Found parent window, sending message');
                        sendMessageToParent();
                    }} else {{
                        console.log('No parent window found');
                        document.getElementById('message').style.display = 'block';
                    }}
                }};
            </script>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; }}
                .container {{ max-width: 500px; margin: 50px auto; padding: 20px; text-align: center; }}
                .success {{ color: #10b981; }}
                .error {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div id="message" style="display:none;">
                    <h2 class="{'success' if success else 'error'}">{'Success!' if success else 'Error'}</h2>
                    <p>{context['message']}</p>
                    <p>Status: {'Authentication required' if auth_required else 'Complete'}</p>
                    <p>Platform: {platform or 'Unknown'}</p>
                    <p>This window will close automatically. If it doesn't, you can close it manually.</p>
                </div>
                <div id="error" style="display:none; color: #ef4444;"></div>
                
                <div id="debug" style="margin-top: 30px; text-align: left; font-size: 12px; color: #666;">
                    <p>Debug info:</p>
                    <pre>{json.dumps(context, indent=2)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)

class CompleteOAuthView(views.APIView):
    """
    Complete OAuth flow using stored code and state after user authentication
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, platform):
        try:
            # Get the code and state from the request
            code = request.data.get('code')
            state = request.data.get('state')
            
            if not code or not state:
                return Response(
                    {'error': 'Missing required parameters (code, state)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Handle different platforms
            if platform == 'twitter':
                # Special handling for Twitter with code verifier
                # In this case, we'll need to generate a new code verifier and set it in the session
                # before calling handle_twitter_callback
                code_verifier = generate_code_verifier()
                request.session['twitter_code_verifier'] = code_verifier
                request.session['oauth_state_twitter'] = state
                
                # Handle the callback
                account = handle_twitter_callback(request, request.user, code, state)
                
                # Return success response
                return Response({
                    'success': True,
                    'account': UserSocialAccountSerializer(account).data
                })
            else:
                # For other platforms, implement their specific completion logic
                return Response(
                    {'error': f'Completing OAuth for {platform} is not implemented'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
                
        except Exception as e:
            logger.error(f"Error completing OAuth flow: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GoogleOAuthCallbackView(views.APIView):
    """
    Handle OAuth callback specifically for Google services
    """
    
    def get(self, request):
        """Process Google OAuth callback and create social account"""
        # Get parameters
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        
        # Default platform (since this is specific to Google)
        platform = 'google'
        
        # Check for errors
        if error:
            logger.error(f"Google OAuth error: {error}")
            return self.close_window(success=False, error=error)
            
        # Validate state for CSRF protection if available
        expected_state = request.session.get(f'oauth_state_{platform}')
        if state and expected_state and expected_state != state:
            logger.error(f"OAuth state mismatch. Expected: {expected_state}, Got: {state}")
            return self.close_window(success=False, error='Invalid state parameter')
            
        # Clean up session
        if f'oauth_state_{platform}' in request.session:
            del request.session[f'oauth_state_{platform}']
            
        try:
            # Connect social account
            account = connect_social_account(request.user, platform, code)
            
            # Return success response
            return self.close_window(
                success=True,
                account_name=account.account_name,
                platform=platform
            )
            
        except Exception as e:
            logger.error(f"Error connecting Google account: {str(e)}")
            return self.close_window(success=False, error=str(e))
    
    def close_window(self, success=True, account_name=None, platform=None, error=None):
        """Return an HTML page that closes the popup window and sends a message to the opener"""
        context = {
            'success': success,
            'message': 'Account connected successfully' if success else f'Error: {error}',
            'account_name': account_name,
            'platform': platform,
            'error': error
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{'Success' if success else 'Error'} - Google Authorization</title>
            <script>
                window.onload = function() {{
                    if (window.opener) {{
                        window.opener.postMessage(
                            JSON.stringify({json.dumps(context)}),
                            "*"
                        );
                        window.close();
                    }} else {{
                        document.getElementById('message').style.display = 'block';
                    }}
                }};
            </script>
        </head>
        <body>
            <div id="message" style="display:none; text-align:center; margin-top:50px;">
                <h3>{'Success!' if success else 'Error'}</h3>
                <p>{context['message']}</p>
                <p>You can close this window now.</p>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)

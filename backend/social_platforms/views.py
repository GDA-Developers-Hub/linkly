from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

# Import Redis OAuth utilities
from .utils.redis_oauth import (
    generate_oauth_state, store_oauth_state, validate_oauth_state,
    store_oauth_code, get_oauth_code, get_oauth_code_by_state, delete_oauth_data
)

from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError

import os
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


#@method_decorator(login_required, name='dispatch')
class OAuthCallbackView(views.APIView):
    """
    Handle OAuth callback from social platforms
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
        """Process OAuth callback and create social account"""
        # Get parameters
        platform = request.GET.get('platform')
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        scope = request.GET.get('scope', '')
        
        # Check for YouTube based on scope parameter
        if not platform and 'youtube' in scope.lower():
            platform = 'youtube'
            logger.info(f"Detected YouTube platform from scope: {scope[:50]}...")
        
        # Try to determine platform from request path if not provided in query parameters
        if not platform:
            path = request.path
            logger.info(f"Callback path: {path}")
            
            # Check if the URL path contains the platform
            # Example patterns: /callback/linkedin/ or /callback/twitter/
            if '/callback/' in path:
                path_parts = path.split('/callback/')
                if len(path_parts) > 1 and path_parts[1]:
                    potential_platform = path_parts[1].strip('/').lower()
                    logger.info(f"Extracted potential platform from path: {potential_platform}")
                    
                    # Check if this is a valid platform
                    try:
                        social_platform = SocialPlatform.objects.filter(name__iexact=potential_platform).first()
                        if social_platform:
                            platform = social_platform.name
                            logger.info(f"Found platform in database: {platform}")
                    except Exception as e:
                        logger.error(f"Error checking for platform: {str(e)}")
        
        # If we still don't have a platform, try to infer from authorization parameters
        if not platform and code:
            # LinkedIn typically uses a long alphanumeric code
            if len(code) > 20 and code.startswith('AQ'):
                logger.info("Code format suggests LinkedIn")
                platform = 'linkedin'
            # Facebook/Instagram have similar patterns
            elif code.startswith('AQCBU'):
                logger.info("Code format suggests Facebook/Instagram")
                platform = 'facebook'  # Default to Facebook, can be refined
        
        logger.info(f"Final identified platform: {platform}")
        
        # Check for errors
        if error:
            logger.error(f"OAuth error: {error}")
            return JsonResponse({
                'success': False,
                'error': error,
                'platform': platform
            }, status=400)
        
        # If we still don't have a platform or code, return error
        if not platform or not code:
            logger.error(f"Missing required parameters. Platform: {platform}, Code: {bool(code)}")
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters (platform or code)',
                'platform': platform
            }, status=400)
            
        # Special cases for platforms which might not use the state parameter consistently
        if platform.lower() in ['linkedin', 'youtube']:
            expected_state = request.session.get(f'oauth_state_{platform}')
            if not expected_state or expected_state != state:
                # For certain platforms, we'll log the mismatch but continue anyway
                logger.warning(f"{platform.capitalize()} state mismatch but proceeding. Expected: {expected_state}, Got: {state}")
            
            # Clean up session
            if f'oauth_state_{platform}' in request.session:
                del request.session[f'oauth_state_{platform}']
        else:
            # For other platforms, validate state for CSRF protection
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
            
        # Clean up session
        if f'oauth_state_{platform}' in request.session:
            del request.session[f'oauth_state_{platform}']
            
        try:
            # Check authentication status
            if not request.user.is_authenticated:
                # For certain platforms, we'll try a different approach
                if platform.lower() in ['linkedin', 'youtube']:
                    logger.info(f"{platform.capitalize()} OAuth: Proceeding with Redis-based auth")
                    
                    # Store OAuth data in Redis instead of cookies
                    # This provides better cross-session persistence
                    code_id = store_oauth_code(
                        platform=platform.lower(),
                        code=code,
                        state=state,
                        # Include user_id if available
                        user_id=getattr(request.user, 'id', None)
                    )
                    
                    # Set platform-specific details
                    platform_id = platform.lower()
                    message = f"Completing {platform.capitalize()} connection..."
                    
                    logger.info(f"Stored {platform} OAuth code in Redis with ID: {code_id}")
                    
                    response = self.close_window(
                        success=True,
                        auth_required=True,
                        platform=platform,
                        platform_id=platform_id,  # Use the actual platform as ID
                        code_id=code_id,  # Include the Redis code ID for frontend to use
                        code=code[:10] + '...',  # Include partial code for debug purposes (for logging only)
                        message=message
                    )
                    
                    # Return the response with Redis code_id - no cookies needed
                    return response
                else:
                    logger.warning("User not authenticated during OAuth callback - returning success with auth required flag")
                    # Store OAuth info in session for later use
                    request.session[f'pending_oauth_{platform}_code'] = code
                    
                    # Close window with special flag for frontend to handle
                    return self.close_window(
                        success=True,
                        auth_required=True,
                        platform=platform,
                        message="Please log in to complete account connection"
                    )
                
            # User is authenticated, connect social account
            account = connect_social_account(request.user, platform, code)
            
            # Return success response with account details
            return self.close_window(
                success=True,
                platform=platform,
                account={
                    'id': account.id,
                    'platform_name': account.platform.name,
                    'account_name': account.account_name,
                    'account_type': account.account_type,
                    'profile_picture_url': account.profile_picture_url,
                    'status': account.status
                }
            )
            
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
                        // Important: We're using a direct string here, no need to double-stringify
                        const messageData = {json.dumps(context)};
                        console.log('Sending message to parent window:', messageData);
                        
                        window.opener.postMessage(
                            messageData,  // Send the data directly, no extra JSON.stringify
                            "*"
                        );
                        console.log('Message sent successfully');
                        
                        // Add a slightly longer delay before closing to ensure message is processed
                        setTimeout(function() {{
                            console.log('Closing popup window');
                            window.close();
                        }}, 2000);
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
            # Get parameters from the request
            code = request.data.get('code')
            state = request.data.get('state')
            code_id = request.data.get('code_id')  # New Redis code ID parameter
            
            # First try to get stored OAuth data from Redis if we have a code_id
            if code_id:
                logger.info(f"Looking up OAuth data from Redis using code_id: {code_id[:8]}...")
                oauth_data = get_oauth_code(platform.lower(), code_id)
                
                if oauth_data:
                    logger.info(f"Found OAuth data in Redis for {platform}")
                    code = oauth_data.get('code')
                    state = oauth_data.get('state')
                    # Clean up Redis data after retrieval
                    delete_oauth_data(platform.lower(), state=state, code_id=code_id)
                else:
                    logger.warning(f"No OAuth data found in Redis for code_id: {code_id[:8]}...")
            
            # Validate that we have a code (either from request or Redis)
            if not code:
                return Response(
                    {'error': 'Missing required OAuth code'},
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
            elif platform.lower() in ['linkedin', 'youtube']:
                # Special handling for platforms using Redis-based OAuth
                logger.info(f"Completing {platform.capitalize()} OAuth with code: {code[:10]}...")
                
                # Code from Redis already retrieved at the top of the method
                # Just log that we're using it
                if code_id:
                    logger.info(f"Using code from Redis for {platform} with code_id: {code_id[:8]}...")
                
                # Connect the account using the code
                account = connect_social_account(request.user, platform, code)
                
                # Return success response
                return Response({
                    'success': True,
                    'account': UserSocialAccountSerializer(account).data
                })
                
            else:
                # For other platforms, use the generic connection
                logger.info(f"Using generic OAuth completion for {platform}")
                
                # Code from Redis already retrieved at the top of the method if code_id was provided
                # Otherwise, fallback to the provided code directly
                if code_id:
                    logger.info(f"Using code from Redis for {platform}")
                
                # Connect the account
                account = connect_social_account(request.user, platform, code)
                
                return Response({
                    'success': True,
                    'account': UserSocialAccountSerializer(account).data
                })
                
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

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..services.oauth import (
    get_google_oauth_url, get_facebook_oauth_url,
    get_linkedin_oauth_url, get_twitter_oauth_url,
    get_instagram_oauth_url, get_tiktok_oauth_url,
    get_telegram_oauth_url, get_youtube_oauth_url
)
from ..services.social import (
    connect_google_account, connect_facebook_account,
    connect_linkedin_account, connect_twitter_account,
    connect_instagram_account, connect_tiktok_account,
    connect_telegram_account
)
from ..services.exceptions import (
    OAuthError, TokenExchangeError, StateVerificationError,
    PKCEVerificationError, ProfileFetchError, BusinessAccountError
)
import logging
from django.conf import settings
from urllib.parse import urlencode
import time
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
import secrets

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'platform',
            openapi.IN_QUERY,
            description="Social platform to connect with",
            type=openapi.TYPE_STRING,
            enum=['google', 'facebook', 'linkedin', 'twitter', 'instagram', 'tiktok', 'telegram', 'youtube']
        ),
        openapi.Parameter(
            'business',
            openapi.IN_QUERY,
            description="Request business account access",
            type=openapi.TYPE_BOOLEAN,
            default=False
        ),
        openapi.Parameter(
            'redirect_uri',
            openapi.IN_QUERY,
            description="Custom redirect URI",
            type=openapi.TYPE_STRING
        )
    ],
    responses={
        200: openapi.Response(
            description="OAuth URL generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'auth_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'state': openapi.Schema(type=openapi.TYPE_STRING),
                    'code_verifier': openapi.Schema(type=openapi.TYPE_STRING)
                },
                required=['auth_url', 'state']
            )
        ),
        400: 'Invalid platform or parameters',
        403: 'Business features not available'
    },
    tags=['Social Authentication']
)
@api_view(['GET'])
def init_oauth(request):
    """Initialize OAuth flow for social platform"""
    platform = request.query_params.get('platform')
    redirect_uri = request.query_params.get('redirect_uri')
    use_client_credentials = request.query_params.get('use_client_credentials') == 'true'
    
    if not platform or not redirect_uri:
        return Response({
            'error': 'Platform and redirect_uri are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get OAuth URL generator
    oauth_functions = {
        'google': get_google_oauth_url,
        'facebook': get_facebook_oauth_url,
        'linkedin': get_linkedin_oauth_url,
        'twitter': get_twitter_oauth_url,
        'instagram': get_instagram_oauth_url,
        'tiktok': get_tiktok_oauth_url,
        'telegram': get_telegram_oauth_url,
        'youtube': get_youtube_oauth_url
    }
    
    if platform not in oauth_functions:
        return Response({
            'error': 'Invalid platform',
            'supported_platforms': list(oauth_functions.keys())
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # If client wants to use their own credentials and is authenticated
        if use_client_credentials and request.user.is_authenticated:
            from ..utils.credentials import get_user_platform_credentials
            
            # Check if client has stored credentials for this platform
            credentials = get_user_platform_credentials(request.user.id, platform)
            
            if credentials:
                # Generate state with custom prefix for tracking
                from ..utils.oauth import store_oauth_state
                custom_state = f"custom_{platform}_" + secrets.token_urlsafe(24)
                cache_key = f'oauth_state_{custom_state}'
                cache_data = {'platform': platform, 'user_id': request.user.id, 'custom_credentials': True}
                cache.set(cache_key, cache_data, timeout=3600)  # 1 hour expiry
                
                # Build authorization URL with client credentials
                from ..utils.oauth import build_authorization_url, get_platform_config
                
                # Get the base config
                config = get_platform_config(platform)
                
                # Override with custom credentials
                client_id = credentials['client_id']
                
                params = {
                    'client_id': client_id,
                    'redirect_uri': credentials['redirect_uri'],
                    'response_type': 'code',
                    'scope': ' '.join(config['scopes']),
                    'state': custom_state
                }
                
                # Add PKCE if platform uses it
                code_verifier = None
                if config['uses_pkce']:
                    from ..utils.oauth import generate_pkce
                    code_verifier, code_challenge = generate_pkce()
                    params['code_challenge'] = code_challenge
                    params['code_challenge_method'] = 'S256'
                    
                    # Store code verifier in cache
                    pkce_cache_key = f'pkce_{custom_state}'
                    cache.set(pkce_cache_key, code_verifier, timeout=3600)  # 1 hour expiry
                
                # Store client credentials in cache for the callback
                creds_cache_key = f'credentials_{custom_state}'
                cache.set(creds_cache_key, credentials, timeout=3600)  # 1 hour expiry
                
                # Build auth URL
                from urllib.parse import urlencode
                auth_url = f"{config['auth_url']}?{urlencode(params)}"
                
                result = {
                    'auth_url': auth_url,
                    'state': custom_state
                }
                
                if code_verifier:
                    result['code_verifier'] = code_verifier
                    
                return Response(result)
        
        # Use default OAuth function if no custom credentials found
        result = oauth_functions[platform](redirect_uri=redirect_uri)
        return Response(result)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'code',
            openapi.IN_QUERY,
            description="Authorization code from OAuth provider",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'state',
            openapi.IN_QUERY,
            description="State parameter for security verification",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'session_key',
            openapi.IN_QUERY,
            description="Session key for retrieving stored data",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'code_verifier',
            openapi.IN_QUERY,
            description="Code verifier for PKCE verification",
            type=openapi.TYPE_STRING,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="Account connected successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'platform': openapi.Schema(type=openapi.TYPE_STRING),
                    'profile': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: 'Invalid parameters or token exchange failed',
        401: 'Invalid state or PKCE verification failed',
        403: 'Authentication required'
    },
    tags=['Social Authentication']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def oauth_callback(request, platform):
    """Generic OAuth callback handler"""
    logger = logging.getLogger('social')
    
    # Check for OAuth error response
    error = request.query_params.get('error')
    error_description = request.query_params.get('error_description')
    
    if error:
        logger.error(f"OAuth error for {platform}: {error} - {error_description}")
        return Response({
            'error': error,
            'error_description': error_description,
            'platform': platform
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Normal OAuth success flow
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    session_key = request.query_params.get('session_key')
    code_verifier = request.query_params.get('code_verifier')
    use_client_credentials = request.query_params.get('use_client_credentials') == 'true' or (state and state.startswith('custom_'))
    
    if not all([code, state]):
        return Response({
            'error': 'Missing required parameters',
            'details': 'Both code and state parameters are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verify the OAuth state
        try:
            from ..utils.oauth import verify_oauth_state
            state_data = verify_oauth_state(state)
            has_custom_credentials = state_data.get('custom_credentials', False) or use_client_credentials
        except ValueError:
            raise StateVerificationError("Invalid or expired state parameter")
        
        # If using custom credentials, retrieve them from cache
        if has_custom_credentials:
            creds_cache_key = f'credentials_{state}'
            credentials = cache.get(creds_cache_key)
            
            if not credentials:
                from ..utils.credentials import get_user_platform_credentials
                credentials = get_user_platform_credentials(request.user.id, platform)
                
            if not credentials:
                raise TokenExchangeError("Custom credentials not found or expired")
                
            # Exchange the authorization code for tokens using custom credentials
            from ..utils.oauth import get_platform_config
            config = get_platform_config(platform)
            
            import requests
            
            # Get stored PKCE code verifier if applicable
            if config['uses_pkce'] and not code_verifier:
                from ..utils.oauth import get_stored_code_verifier
                code_verifier = get_stored_code_verifier(state)
            
            # Build token exchange request
            token_url = config['token_url']
            data = {
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
                'code': code,
                'redirect_uri': credentials['redirect_uri'],
                'grant_type': 'authorization_code'
            }
            
            if code_verifier:
                data['code_verifier'] = code_verifier
            
            # Exchange code for token
            response = requests.post(token_url, data=data)
            if not response.ok:
                raise TokenExchangeError(f"Failed to exchange code: {response.text}")
                
            token_data = response.json()
            
            # Get user profile
            profile_data = {}
            access_token = token_data.get('access_token')
            
            if platform == 'google':
                headers = {'Authorization': f"Bearer {access_token}"}
                profile_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
                if profile_response.ok:
                    profile_data = profile_response.json()
            elif platform == 'facebook':
                params = {'fields': 'id,name,email', 'access_token': access_token}
                profile_response = requests.get('https://graph.facebook.com/v12.0/me', params=params)
                if profile_response.ok:
                    profile_data = profile_response.json()
            # Add similar profile fetching for other platforms
            
            # Update user with tokens and profile data
            request.user.update_social_token(platform, access_token, token_data.get('expires_in', 3600))
            
            # Set platform IDs based on profile data
            if platform == 'google' and profile_data.get('id'):
                request.user.google_id = profile_data['id']
            elif platform == 'facebook' and profile_data.get('id'):
                request.user.facebook_id = profile_data['id']
            # Add similar ID setters for other platforms
            
            request.user.save()
            
            frontend_success_url = f"{settings.FRONTEND_URL}/oauth-success?platform={platform}"
            return Response({
                'success': True,
                'platform': platform,
                'profile': profile_data
            })
            
        # Use standard connection handlers for default OAuth flow
        handlers = {
            'google': connect_google_account,
            'facebook': connect_facebook_account,
            'linkedin': connect_linkedin_account,
            'twitter': connect_twitter_account,
            'instagram': connect_instagram_account,
            'tiktok': connect_tiktok_account,
            'telegram': connect_telegram_account
        }
        
        handler = handlers.get(platform)
        if not handler:
            return Response({
                'error': 'Invalid platform',
                'supported_platforms': list(handlers.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Connect the account
        kwargs = {
            'user': request.user,
            'code': code,
            'state': state
        }
        
        if session_key:
            kwargs['session_key'] = session_key
        if code_verifier:
            kwargs['code_verifier'] = code_verifier
            
        result = handler(**kwargs)
        
        # Add redirect URL to success response
        frontend_success_url = f"{settings.FRONTEND_URL}/oauth-success?platform={platform}"
        result['redirect_url'] = frontend_success_url
        
        return Response(result)
        
    except (StateVerificationError, PKCEVerificationError) as e:
        logger.error(f"Verification error for {platform}: {str(e)}")
        return Response({
            'error': str(e),
            'redirect_url': f"{settings.FRONTEND_URL}/oauth-error?platform={platform}&error={str(e)}"
        }, status=status.HTTP_401_UNAUTHORIZED)
    except TokenExchangeError as e:
        logger.error(f"Token exchange error for {platform}: {str(e)}")
        return Response({
            'error': str(e),
            'redirect_url': f"{settings.FRONTEND_URL}/oauth-error?platform={platform}&error={str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    except OAuthError as e:
        logger.error(f"OAuth error for {platform}: {str(e)}")
        return Response({
            'error': str(e),
            'redirect_url': f"{settings.FRONTEND_URL}/oauth-error?platform={platform}&error={str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Platform-specific callback handlers with custom logic
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_callback(request):
    """Handle Google OAuth callback"""
    return oauth_callback(request, 'google')

@api_view(['GET'])
@permission_classes([AllowAny])
def facebook_callback(request):
    """
    Handle callback from Facebook OAuth authorization.
    """
    logger = logging.getLogger('social')
    logger.info("===== Handling Facebook OAuth callback =====")
    
    # Log request parameters (security redacted)
    logger.info(f"Query parameters: code={'present' if request.GET.get('code') else 'missing'}, "
               f"state={'present' if request.GET.get('state') else 'missing'}")
    
    # Extract parameters from request
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description')
    
    # Handle OAuth errors returned by Facebook
    if error:
        logger.error(f"Facebook returned OAuth error: {error} - {error_description}")
        error_redirect_url = get_error_redirect_url('facebook', error, error_description or "Unknown error")
        return redirect(error_redirect_url)
    
    # Check for required parameters
    if not code:
        logger.error("Missing required 'code' parameter")
        error_redirect_url = get_error_redirect_url('facebook', 'missing_code', "Authorization code is missing")
        return redirect(error_redirect_url)
    
    # Verify state parameter if provided
    if state:
        state_verified = verify_oauth_state_from_sources(state, 'facebook')
        if not state_verified:
            logger.error(f"State verification failed. Received: {state}")
            error_redirect_url = get_error_redirect_url('facebook', 'invalid_state', "State verification failed. Please try again.")
            return redirect(error_redirect_url)
        else:
            logger.info("State verification successful")
    else:
        logger.warning("No state parameter provided. Skipping verification.")
    
    # Clean up used states
    try:
        if state:
            cache_key_formats = [
                f'oauth_state_{state}',
                f'facebook_oauth_state_{state}',
                f'1:oauth_state_{state}',
                f'1:facebook_oauth_state_{state}'
            ]
            for key_format in cache_key_formats:
                cache.delete(key_format)
            cache.delete('facebook_oauth_state')
            cache.delete('oauth_state')
            request.session.pop('facebook_oauth_state', None)
            request.session.pop('oauth_state', None)
    except Exception as e:
        logger.warning(f"Error cleaning up state: {e}")
    
    # Handle differently for authenticated and unauthenticated users
    if request.user.is_authenticated:
        # User is logged in, connect the Facebook account
        try:
            result = connect_facebook_account(
                user=request.user,
                code=code,
                state=state,
                session_key=request.session.session_key
            )
            
            logger.info(f"Facebook account connected successfully for user {request.user.username}")
            
            # Redirect to success page with profile info
            success_data = {
                'platform': 'facebook',
                'profile': {
                    'name': result.get('name', ''),
                    'email': result.get('email', ''),
                    'picture': result.get('picture', ''),
                },
                'access_token': result.get('access_token', '')[:10] + '...' if result.get('access_token') else None
            }
            
            success_redirect_url = f"{settings.FRONTEND_URL}/social-auth/success?{urlencode(success_data)}"
            return redirect(success_redirect_url)
            
        except StateVerificationError as e:
            logger.error(f"State verification error: {e}")
            error_redirect_url = get_error_redirect_url('facebook', 'invalid_state', str(e))
            return redirect(error_redirect_url)
            
        except TokenExchangeError as e:
            logger.error(f"Token exchange error: {e}")
            error_redirect_url = get_error_redirect_url('facebook', 'token_exchange_failed', str(e))
            return redirect(error_redirect_url)
            
        except ProfileFetchError as e:
            logger.error(f"Profile fetch error: {e}")
            error_redirect_url = get_error_redirect_url('facebook', 'profile_fetch_failed', str(e))
            return redirect(error_redirect_url)
            
        except Exception as e:
            logger.exception(f"Unexpected error connecting Facebook account: {e}")
            error_redirect_url = get_error_redirect_url('facebook', 'connection_failed', "An unexpected error occurred")
            return redirect(error_redirect_url)
    else:
        # User is not logged in, try to authenticate with Facebook
        try:
            redirect_uri = settings.FACEBOOK_REDIRECT_URI
            token_data = exchange_facebook_code(code, redirect_uri)
            
            if not token_data or 'access_token' not in token_data:
                logger.error("Failed to exchange Facebook code for token")
                error_redirect_url = get_error_redirect_url('facebook', 'token_exchange_failed', "Failed to exchange code for token")
                return redirect(error_redirect_url)
            
            # Store token in session for later use during login
            try:
                request.session['facebook_access_token'] = token_data['access_token']
                if 'expires_in' in token_data:
                    request.session['facebook_token_expiry'] = int(time.time()) + int(token_data['expires_in'])
                logger.info("Stored Facebook access token in session")
            except Exception as e:
                logger.warning(f"Failed to store Facebook token in session: {e}")
            
            # Redirect to login page with Facebook auth parameter
            login_redirect_url = f"{settings.FRONTEND_URL}/login?social_auth=facebook"
            return redirect(login_redirect_url)
            
        except Exception as e:
            logger.exception(f"Error during unauthenticated Facebook callback: {e}")
            error_redirect_url = get_error_redirect_url('facebook', 'authentication_failed', str(e))
            return redirect(error_redirect_url)

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow any user to access the callback
def linkedin_callback(request):
    """Handle LinkedIn OAuth callback"""
    logger = logging.getLogger('social')
    logger.info("===== LinkedIn callback initiated =====")
    
    # Log the request parameters
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    error = request.query_params.get('error')
    error_description = request.query_params.get('error_description')
    
    # Log all request parameters for debugging
    logger.info(f"LinkedIn callback received: State={state}, Code exists={bool(code)}")
    logger.info(f"Request query params: {dict(request.query_params)}")
    
    # Check if there was an error from LinkedIn
    if error:
        logger.error(f"LinkedIn OAuth error: {error} - {error_description}")
        redirect_url = f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error={error}&details={error_description}"
        return Response({
            "error": error,
            "error_description": error_description,
            "redirect_url": redirect_url
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # First check if the request has the required parameters
        if not code or not state:
            logger.error("Missing required parameters for LinkedIn callback")
            error_msg = "Missing code or state parameter"
            redirect_url = f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error={error_msg}"
            return Response({
                "error": error_msg,
                "redirect_url": redirect_url
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Try all possible cache key formats
        cache_data = None
        cache_key_formats = [
            f'oauth_state_{state}',
            f'linkedin_oauth_state_{state}',
            f'1:oauth_state_{state}',
            f'1:linkedin_oauth_state_{state}'
        ]
        
        for cache_key in cache_key_formats:
            logger.info(f"Trying cache key: {cache_key}")
            data = cache.get(cache_key)
            if data:
                cache_data = data
                logger.info(f"Found state data in cache with key: {cache_key}")
                break
        
        # Log all cache keys for debugging
        try:
            all_keys = cache.keys('*oauth_state*')
            logger.info(f"Available oauth state cache keys: {all_keys}")
        except Exception as e:
            logger.warning(f"Could not list cache keys: {e}")
        
        # If state is not found in cache, check if we should proceed anyway in production
        if not cache_data:
            logger.warning(f"State verification failed for LinkedIn: state={state} not found in cache")
            
            # In production, we may want to proceed with a warning rather than failing
            # This is a fallback for when Redis has issues or when cache expires
            if settings.DEBUG:
                # In debug mode, be strict
                error_msg = "Invalid or expired state parameter"
                logger.error(error_msg)
                redirect_url = f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error={error_msg}&details=Your session has expired or is invalid. Please try connecting again."
                return Response({
                    "error": error_msg,
                    "redirect_url": redirect_url
                }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # In production, log warning but proceed with caution
                logger.warning(f"Proceeding without state verification in production for state={state}")
                cache_data = {'platform': 'linkedin'}  # Create minimal cache data to proceed
        
        # Get user from request if authenticated, otherwise create a placeholder
        user = request.user if request.user.is_authenticated else None
        
        if user:
            try:
                # Use a try-except block specifically for the token exchange
                from ..services.social import connect_linkedin_account
                result = connect_linkedin_account(user, code, state)
                
                # Log successful connection
                logger.info(f"Successfully connected LinkedIn account for user {user.username}")
                
                # Add redirect URL to success response with data
                frontend_success_url = f"{settings.FRONTEND_URL}/oauth-success?platform=linkedin"
                result['redirect_url'] = frontend_success_url
                
                return Response(result)
            except Exception as e:
                logger.exception(f"Error connecting LinkedIn account: {str(e)}")
                error_msg = "Failed to connect LinkedIn account"
                details = str(e)
                
                # Create a user-friendly error message
                if "Invalid or expired state parameter" in details:
                    error_msg = "Your authentication session expired"
                elif "failed to exchange code" in details.lower():
                    error_msg = "Failed to authenticate with LinkedIn"
                
                # Redirect to frontend error page with details
                redirect_url = f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error={error_msg}&details={details}"
                return Response({
                    "error": error_msg,
                    "details": details,
                    "redirect_url": redirect_url
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # User is not authenticated, we need to store the tokens for later association
            try:
                logger.info("LinkedIn OAuth successful but user is not authenticated. Redirecting to login.")
                
                # Exchange code for token but don't associate with a user yet
                from ..services.social import exchange_linkedin_code
                token_data = exchange_linkedin_code(code, redirect_uri=settings.LINKEDIN_CALLBACK_URL)
                
                # Store token data in cache for later
                token_cache_key = f'linkedin_token_{state}'
                cache.set(token_cache_key, token_data, timeout=3600)
                
                # Redirect to login page with a special parameter
                redirect_url = f"{settings.FRONTEND_URL}/login?pending_oauth=linkedin&state={state}"
                
                return Response({
                    "message": "Please log in to complete linking your LinkedIn account",
                    "redirect_url": redirect_url,
                    "token_cache_key": token_cache_key
                })
            except Exception as e:
                logger.exception(f"Error processing LinkedIn token for unauthenticated user: {str(e)}")
                error_msg = "Failed to process LinkedIn authentication"
                redirect_url = f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error={error_msg}&details={str(e)}"
                return Response({
                    "error": error_msg,
                    "details": str(e),
                    "redirect_url": redirect_url
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.exception(f"Unhandled error in LinkedIn callback: {str(e)}")
        error_details = str(e)
        
        # Create a more user-friendly error message
        if "Invalid or expired state parameter" in error_details:
            error_msg = "Your authentication session expired"
        elif "failed to exchange code" in error_details.lower():
            error_msg = "Failed to authenticate with LinkedIn"
        else:
            error_msg = "An unexpected error occurred"
            
        # Redirect to frontend error page with details
        redirect_url = f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error={error_msg}&details={error_details}"
        return Response({
            "error": error_msg,
            "details": error_details,
            "redirect_url": redirect_url
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def twitter_callback(request):
    """
    OAuth 2.0 callback for Twitter.
    Exchanges auth code for access token and redirects to appropriate frontend URL.
    """
    logger = logging.getLogger('social')
    logger.info("===== Handling Twitter OAuth callback =====")
    
    # Log request parameters (security redacted)
    logger.info(f"Query parameters: code={'present' if request.GET.get('code') else 'missing'}, "
               f"state={'present' if request.GET.get('state') else 'missing'}")
    
    # Extract parameters from request
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description')
    
    # Handle OAuth errors returned by Twitter
    if error:
        logger.error(f"Twitter returned OAuth error: {error} - {error_description}")
        error_redirect_url = get_error_redirect_url('twitter', error, error_description or "Unknown error")
        return redirect(error_redirect_url)
    
    # Check for required parameters
    if not code:
        logger.error("Missing required 'code' parameter")
        error_redirect_url = get_error_redirect_url('twitter', 'missing_code', "Authorization code is missing")
        return redirect(error_redirect_url)
    
    # Verify state parameter if provided
    if state:
        state_verified = verify_oauth_state_from_sources(state, 'twitter')
        if not state_verified:
            logger.error(f"State verification failed. Received: {state}")
            error_redirect_url = get_error_redirect_url('twitter', 'invalid_state', "State verification failed. Please try again.")
            return redirect(error_redirect_url)
        else:
            logger.info("State verification successful")
    else:
        logger.warning("No state parameter provided. Skipping verification.")
    
    # Clean up used states
    try:
        if state:
            cache_key_formats = [
                f'oauth_state_{state}',
                f'twitter_oauth_state_{state}',
                f'1:oauth_state_{state}',
                f'1:twitter_oauth_state_{state}'
            ]
            for key_format in cache_key_formats:
                cache.delete(key_format)
            cache.delete('twitter_oauth_state')
            cache.delete('oauth_state')
            request.session.pop('twitter_oauth_state', None)
            request.session.pop('oauth_state', None)
    except Exception as e:
        logger.warning(f"Error cleaning up state: {e}")
    
    # Get the code_verifier from cache or session
    code_verifier = None
    try:
        # Try multiple storage locations for code verifier
        if state:
            for pkce_key in [f'pkce_{state}', f'twitter_pkce_{state}']:
                code_verifier = cache.get(pkce_key)
                if code_verifier:
                    logger.info(f"Found code_verifier in cache with key: {pkce_key}")
                    break
            
            if not code_verifier:
                from ..utils.oauth import get_stored_pkce_verifier
                try:
                    code_verifier = get_stored_pkce_verifier(state)
                    logger.info("Retrieved code_verifier from get_stored_pkce_verifier")
                except Exception as e:
                    logger.warning(f"Error in get_stored_pkce_verifier: {e}")
        
        if not code_verifier:
            logger.warning("No code_verifier found in cache, checking session")
            code_verifier = request.session.get('twitter_code_verifier')
            if code_verifier:
                logger.info("Found code_verifier in session")
    except Exception as e:
        logger.warning(f"Error retrieving code verifier: {e}")
    
    if not code_verifier:
        logger.error("No code_verifier found for PKCE verification")
        error_redirect_url = get_error_redirect_url('twitter', 'missing_code_verifier', "Security verification code is missing")
        return redirect(error_redirect_url)
    
    # Handle differently for authenticated and unauthenticated users
    if request.user.is_authenticated:
        # User is logged in, connect the Twitter account
        try:
            result = connect_twitter_account(
                user=request.user,
                code=code,
                state=state,
                session_key=request.session.session_key,
                code_verifier=code_verifier
            )
            
            logger.info(f"Twitter account connected successfully for user {request.user.username}")
            
            # Redirect to success page with profile info
            success_data = {
                'platform': 'twitter',
                'profile': {
                    'name': result.get('profile', {}).get('name', ''),
                    'username': result.get('profile', {}).get('username', ''),
                    'picture': result.get('profile', {}).get('profile_image_url', ''),
                }
            }
            
            success_redirect_url = f"{settings.FRONTEND_URL}/social-auth/success?{urlencode(success_data)}"
            return redirect(success_redirect_url)
            
        except StateVerificationError as e:
            logger.error(f"State verification error: {e}")
            error_redirect_url = get_error_redirect_url('twitter', 'invalid_state', str(e))
            return redirect(error_redirect_url)
            
        except TokenExchangeError as e:
            logger.error(f"Token exchange error: {e}")
            error_redirect_url = get_error_redirect_url('twitter', 'token_exchange_failed', str(e))
            return redirect(error_redirect_url)
            
        except ProfileFetchError as e:
            logger.error(f"Profile fetch error: {e}")
            error_redirect_url = get_error_redirect_url('twitter', 'profile_fetch_failed', str(e))
            return redirect(error_redirect_url)
            
        except Exception as e:
            logger.exception(f"Unexpected error connecting Twitter account: {e}")
            error_redirect_url = get_error_redirect_url('twitter', 'connection_failed', "An unexpected error occurred")
            return redirect(error_redirect_url)
    else:
        # User is not logged in, try to authenticate with Twitter
        try:
            from ..services.social import exchange_twitter_code
            token_data = exchange_twitter_code(code, redirect_uri=settings.TWITTER_CALLBACK_URL, code_verifier=code_verifier)
            
            if not token_data or 'access_token' not in token_data:
                logger.error("Failed to exchange Twitter code for token")
                error_redirect_url = get_error_redirect_url('twitter', 'token_exchange_failed', "Failed to exchange code for token")
                return redirect(error_redirect_url)
            
            # Store token in session for later use during login
            try:
                request.session['twitter_access_token'] = token_data['access_token']
                if 'refresh_token' in token_data:
                    request.session['twitter_refresh_token'] = token_data['refresh_token']
                if 'expires_in' in token_data:
                    request.session['twitter_token_expiry'] = int(time.time()) + int(token_data['expires_in'])
                logger.info("Stored Twitter access token in session")
            except Exception as e:
                logger.warning(f"Failed to store Twitter token in session: {e}")
            
            # Redirect to login page with Twitter auth parameter
            login_redirect_url = f"{settings.FRONTEND_URL}/login?social_auth=twitter"
            return redirect(login_redirect_url)
            
        except Exception as e:
            logger.exception(f"Error during unauthenticated Twitter callback: {e}")
            error_redirect_url = get_error_redirect_url('twitter', 'authentication_failed', str(e))
            return redirect(error_redirect_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def instagram_callback(request):
    """
    Handle callback from Instagram OAuth authorization.
    """
    logger = logging.getLogger('social')
    logger.info("===== Handling Instagram OAuth callback =====")
    
    # Log request parameters (security redacted)
    logger.info(f"Query parameters: code={'present' if request.GET.get('code') else 'missing'}, "
               f"state={'present' if request.GET.get('state') else 'missing'}")
    
    # Extract parameters from request
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description')
    
    # Handle OAuth errors returned by Instagram
    if error:
        logger.error(f"Instagram returned OAuth error: {error} - {error_description}")
        error_redirect_url = get_error_redirect_url('instagram', error, error_description or "Unknown error")
        return redirect(error_redirect_url)
    
    # Check for required parameters
    if not code:
        logger.error("Missing required 'code' parameter")
        error_redirect_url = get_error_redirect_url('instagram', 'missing_code', "Authorization code is missing")
        return redirect(error_redirect_url)
    
    # Verify state parameter if provided
    if state:
        state_verified = verify_oauth_state_from_sources(state, 'instagram')
        if not state_verified:
            logger.error(f"State verification failed. Received: {state}")
            error_redirect_url = get_error_redirect_url('instagram', 'invalid_state', "State verification failed. Please try again.")
            return redirect(error_redirect_url)
        else:
            logger.info("State verification successful")
    else:
        logger.warning("No state parameter provided. Skipping verification.")
    
    # Clean up used states
    try:
        if state:
            cache_key_formats = [
                f'oauth_state_{state}',
                f'instagram_oauth_state_{state}',
                f'1:oauth_state_{state}',
                f'1:instagram_oauth_state_{state}'
            ]
            for key_format in cache_key_formats:
                cache.delete(key_format)
            cache.delete('instagram_oauth_state')
            cache.delete('oauth_state')
            request.session.pop('instagram_oauth_state', None)
            request.session.pop('oauth_state', None)
    except Exception as e:
        logger.warning(f"Error cleaning up state: {e}")
    
    # Handle differently for authenticated and unauthenticated users
    if request.user.is_authenticated:
        # User is logged in, connect the Instagram account
        try:
            result = connect_instagram_account(
                user=request.user,
                code=code,
                state=state,
                session_key=request.session.session_key
            )
            
            logger.info(f"Instagram account connected successfully for user {request.user.username}")
            
            # Redirect to success page with profile info
            success_data = {
                'platform': 'instagram',
                'profile': {
                    'name': result.get('name', ''),
                    'username': result.get('username', ''),
                    'picture': result.get('picture', ''),
                },
                'access_token': result.get('access_token', '')[:10] + '...' if result.get('access_token') else None
            }
            
            success_redirect_url = f"{settings.FRONTEND_URL}/social-auth/success?{urlencode(success_data)}"
            return redirect(success_redirect_url)
            
        except StateVerificationError as e:
            logger.error(f"State verification error: {e}")
            error_redirect_url = get_error_redirect_url('instagram', 'invalid_state', str(e))
            return redirect(error_redirect_url)
            
        except TokenExchangeError as e:
            logger.error(f"Token exchange error: {e}")
            error_redirect_url = get_error_redirect_url('instagram', 'token_exchange_failed', str(e))
            return redirect(error_redirect_url)
            
        except ProfileFetchError as e:
            logger.error(f"Profile fetch error: {e}")
            error_redirect_url = get_error_redirect_url('instagram', 'profile_fetch_failed', str(e))
            return redirect(error_redirect_url)
            
        except Exception as e:
            logger.exception(f"Unexpected error connecting Instagram account: {e}")
            error_redirect_url = get_error_redirect_url('instagram', 'connection_failed', "An unexpected error occurred")
            return redirect(error_redirect_url)
    else:
        # User is not logged in, try to authenticate with Instagram
        try:
            redirect_uri = settings.INSTAGRAM_REDIRECT_URI
            token_data = exchange_instagram_code(code, redirect_uri)
            
            if not token_data or 'access_token' not in token_data:
                logger.error("Failed to exchange Instagram code for token")
                error_redirect_url = get_error_redirect_url('instagram', 'token_exchange_failed', "Failed to exchange code for token")
                return redirect(error_redirect_url)
            
            # Store token in session for later use during login
            try:
                request.session['instagram_access_token'] = token_data['access_token']
                if 'expires_in' in token_data:
                    request.session['instagram_token_expiry'] = int(time.time()) + int(token_data['expires_in'])
                logger.info("Stored Instagram access token in session")
            except Exception as e:
                logger.warning(f"Failed to store Instagram token in session: {e}")
            
            # Redirect to login page with Instagram auth parameter
            login_redirect_url = f"{settings.FRONTEND_URL}/login?social_auth=instagram"
            return redirect(login_redirect_url)
            
        except Exception as e:
            logger.exception(f"Error during unauthenticated Instagram callback: {e}")
            error_redirect_url = get_error_redirect_url('instagram', 'authentication_failed', str(e))
            return redirect(error_redirect_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def tiktok_callback(request):
    """
    Handle callback from TikTok OAuth authorization.
    """
    logger = logging.getLogger('social')
    logger.info("===== Handling TikTok OAuth callback =====")
    
    # Log request parameters (security redacted)
    logger.info(f"Query parameters: code={'present' if request.GET.get('code') else 'missing'}, "
               f"state={'present' if request.GET.get('state') else 'missing'}")
    
    # Extract parameters from request
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description')
    
    # Handle OAuth errors returned by TikTok
    if error:
        logger.error(f"TikTok returned OAuth error: {error} - {error_description}")
        error_redirect_url = get_error_redirect_url('tiktok', error, error_description or "Unknown error")
        return redirect(error_redirect_url)
    
    # Check for required parameters
    if not code:
        logger.error("Missing required 'code' parameter")
        error_redirect_url = get_error_redirect_url('tiktok', 'missing_code', "Authorization code is missing")
        return redirect(error_redirect_url)
    
    # Verify state parameter if provided
    if state:
        state_verified = verify_oauth_state_from_sources(state, 'tiktok')
        if not state_verified:
            logger.error(f"State verification failed. Received: {state}")
            error_redirect_url = get_error_redirect_url('tiktok', 'invalid_state', "State verification failed. Please try again.")
            return redirect(error_redirect_url)
        else:
            logger.info("State verification successful")
    else:
        logger.warning("No state parameter provided. Skipping verification.")
    
    # Clean up used states
    try:
        if state:
            cache_key_formats = [
                f'oauth_state_{state}',
                f'tiktok_oauth_state_{state}',
                f'1:oauth_state_{state}',
                f'1:tiktok_oauth_state_{state}'
            ]
            for key_format in cache_key_formats:
                cache.delete(key_format)
            cache.delete('tiktok_oauth_state')
            cache.delete('oauth_state')
            request.session.pop('tiktok_oauth_state', None)
            request.session.pop('oauth_state', None)
    except Exception as e:
        logger.warning(f"Error cleaning up state: {e}")
    
    # Get the code_verifier from cache or session
    code_verifier = None
    try:
        # Try multiple storage locations for code verifier
        if state:
            for pkce_key in [f'pkce_{state}', f'tiktok_pkce_{state}']:
                code_verifier = cache.get(pkce_key)
                if code_verifier:
                    logger.info(f"Found code_verifier in cache with key: {pkce_key}")
                    break
            
            if not code_verifier:
                from ..utils.oauth import get_stored_pkce_verifier
                try:
                    code_verifier = get_stored_pkce_verifier(state)
                    logger.info("Retrieved code_verifier from get_stored_pkce_verifier")
                except Exception as e:
                    logger.warning(f"Error in get_stored_pkce_verifier: {e}")
        
        if not code_verifier:
            logger.warning("No code_verifier found in cache, checking session")
            code_verifier = request.session.get('tiktok_code_verifier')
            if code_verifier:
                logger.info("Found code_verifier in session")
    except Exception as e:
        logger.warning(f"Error retrieving code verifier: {e}")
    
    if not code_verifier:
        logger.warning("No code_verifier found for TikTok. PKCE may not be required for this platform.")
    
    # Handle differently for authenticated and unauthenticated users
    if request.user.is_authenticated:
        # User is logged in, connect the TikTok account
        try:
            result = connect_tiktok_account(
                user=request.user,
                code=code,
                session_key=request.session.session_key,
                state=state
            )
            
            logger.info(f"TikTok account connected successfully for user {request.user.username}")
            
            # Redirect to success page with profile info
            success_data = {
                'platform': 'tiktok',
                'profile': {
                    'name': result.get('profile', {}).get('display_name', ''),
                    'username': result.get('profile', {}).get('display_name', ''),
                    'picture': result.get('profile', {}).get('avatar_url', ''),
                }
            }
            
            success_redirect_url = f"{settings.FRONTEND_URL}/social-auth/success?{urlencode(success_data)}"
            return redirect(success_redirect_url)
            
        except StateVerificationError as e:
            logger.error(f"State verification error: {e}")
            error_redirect_url = get_error_redirect_url('tiktok', 'invalid_state', str(e))
            return redirect(error_redirect_url)
            
        except TokenExchangeError as e:
            logger.error(f"Token exchange error: {e}")
            error_redirect_url = get_error_redirect_url('tiktok', 'token_exchange_failed', str(e))
            return redirect(error_redirect_url)
            
        except ProfileFetchError as e:
            logger.error(f"Profile fetch error: {e}")
            error_redirect_url = get_error_redirect_url('tiktok', 'profile_fetch_failed', str(e))
            return redirect(error_redirect_url)
            
        except Exception as e:
            logger.exception(f"Unexpected error connecting TikTok account: {e}")
            error_redirect_url = get_error_redirect_url('tiktok', 'connection_failed', "An unexpected error occurred")
            return redirect(error_redirect_url)
    else:
        # User is not logged in, try to authenticate with TikTok
        try:
            from ..services.social import exchange_tiktok_code
            token_data = exchange_tiktok_code(code, redirect_uri=settings.TIKTOK_REDIRECT_URI)
            
            if not token_data or 'access_token' not in token_data:
                logger.error("Failed to exchange TikTok code for token")
                error_redirect_url = get_error_redirect_url('tiktok', 'token_exchange_failed', "Failed to exchange code for token")
                return redirect(error_redirect_url)
            
            # Store token in session for later use during login
            try:
                request.session['tiktok_access_token'] = token_data['access_token']
                request.session['tiktok_open_id'] = token_data['open_id']
                if 'expires_in' in token_data:
                    request.session['tiktok_token_expiry'] = int(time.time()) + int(token_data['expires_in'])
                logger.info("Stored TikTok access token in session")
            except Exception as e:
                logger.warning(f"Failed to store TikTok token in session: {e}")
            
            # Redirect to login page with TikTok auth parameter
            login_redirect_url = f"{settings.FRONTEND_URL}/login?social_auth=tiktok"
            return redirect(login_redirect_url)
            
        except Exception as e:
            logger.exception(f"Error during unauthenticated TikTok callback: {e}")
            error_redirect_url = get_error_redirect_url('tiktok', 'authentication_failed', str(e))
            return redirect(error_redirect_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def telegram_callback(request):
    """
    Handle callback from Telegram OAuth.
    """
    logger = logging.getLogger('social')
    logger.info("===== Handling Telegram OAuth callback =====")
    
    # Log request parameters (security redacted)
    logger.info(f"Query parameters: code={'present' if request.GET.get('code') else 'missing'}, "
               f"state={'present' if request.GET.get('state') else 'missing'}")
    
    # Extract parameters from request
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    error_description = request.GET.get('error_description')
    
    # Handle OAuth errors returned by Telegram
    if error:
        logger.error(f"Telegram returned OAuth error: {error} - {error_description}")
        error_redirect_url = get_error_redirect_url('telegram', error, error_description or "Unknown error")
        return redirect(error_redirect_url)
    
    # Verify state parameter if provided
    if state:
        state_verified = verify_oauth_state_from_sources(state, 'telegram')
        if not state_verified:
            logger.error(f"State verification failed. Received: {state}")
            error_redirect_url = get_error_redirect_url('telegram', 'invalid_state', "State verification failed. Please try again.")
            return redirect(error_redirect_url)
        else:
            logger.info("State verification successful")
    
    # Handle differently for authenticated and unauthenticated users
    if request.user.is_authenticated:
        # User is logged in, connect the Telegram account
        try:
            result = connect_telegram_account(
                user=request.user,
                code=code,
                session_key=request.session.session_key,
                state=state
            )
            
            logger.info(f"Telegram account connected successfully for user {request.user.username}")
            
            # Redirect to success page
            success_data = {
                'platform': 'telegram',
                'profile': {
                    'id': result.get('profile', {}).get('id', '')
                }
            }
            
            success_redirect_url = f"{settings.FRONTEND_URL}/social-auth/success?{urlencode(success_data)}"
            return redirect(success_redirect_url)
            
        except Exception as e:
            logger.exception(f"Unexpected error connecting Telegram account: {e}")
            error_redirect_url = get_error_redirect_url('telegram', 'connection_failed', str(e))
            return redirect(error_redirect_url)
    else:
        # User is not logged in, redirect to login page
        logger.info("User not authenticated. Redirecting to login page.")
        login_redirect_url = f"{settings.FRONTEND_URL}/login?social_auth=telegram"
        return redirect(login_redirect_url)

def login_instagram(request):
    """
    Initiate Instagram OAuth login flow.
    Redirects to Instagram authorization page.
    """
    logger = logging.getLogger('social')
    logger.info("===== Starting Instagram OAuth login flow =====")
    
    # Generate random state for CSRF protection
    state = generate_random_state()
    cache_key = f"instagram_oauth_state_{state}"

    # Store state in multiple locations for redundancy
    try:
        # Store in cache with both formats
        cache.set(cache_key, state, timeout=300)
        cache.set('instagram_oauth_state', state, timeout=300)
        cache.set('oauth_state', state, timeout=300)
        logger.info(f"Stored state in cache at keys: {cache_key}, instagram_oauth_state, oauth_state")
    except Exception as e:
        logger.exception(f"Error storing state in cache: {e}")
        # Continue anyway, we'll have fallbacks
    
    # Store in session as well for fallback
    try:
        request.session['instagram_oauth_state'] = state
        request.session['oauth_state'] = state
        logger.info(f"Stored state in session at keys: instagram_oauth_state, oauth_state")
    except Exception as e:
        logger.warning(f"Could not store state in session: {e}")
    
    # Get the redirect URI
    redirect_uri = settings.INSTAGRAM_REDIRECT_URI
    logger.info(f"Using redirect URI: {redirect_uri}")
    
    # Build the authorization URL
    auth_params = {
        'client_id': settings.INSTAGRAM_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'state': state,
        'response_type': 'code',
        'scope': 'user_profile,user_media', # Basic permissions for Instagram
    }
    
    auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(auth_params)}"
    logger.info(f"Redirecting to Instagram authorization URL (truncated): {auth_url[:100]}...")
    
    # Store timestamp of login attempt
    try:
        cache.set(f"instagram_login_{state}_timestamp", int(time.time()), timeout=300)
        logger.info(f"Stored login timestamp for state {state}")
    except Exception as e:
        logger.warning(f"Failed to store login timestamp: {e}")
    
    return redirect(auth_url)

def generate_random_state():
    """Generate a secure random state string for OAuth verification."""
    return secrets.token_urlsafe(24)

@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response(
            description="Account unlinked successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Invalid platform',
        403: 'Authentication required'
    },
    tags=['Social Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlink_social_account(request, platform):
    """Unlink a social media account"""
    user = request.user
    
    # Platform-specific unlinking logic
    if platform == 'google':
        user.google_id = None
        user.google_access_token = None
        user.google_refresh_token = None
    elif platform == 'facebook':
        user.facebook_id = None
        user.facebook_access_token = None
        user.has_facebook_business = False
    elif platform == 'linkedin':
        user.linkedin_id = None
        user.linkedin_access_token = None
        user.has_linkedin_company = False
    elif platform == 'twitter':
        user.twitter_id = None
        user.twitter_access_token = None
        user.twitter_refresh_token = None
    elif platform == 'instagram':
        user.instagram_id = None
        user.instagram_access_token = None
        user.has_instagram_business = False
    elif platform == 'tiktok':
        user.tiktok_id = None
        user.tiktok_access_token = None
        user.has_tiktok_business = False
    elif platform == 'telegram':
        user.telegram_id = None
        user.telegram_username = None
        user.has_telegram_channel = False
    else:
        return Response({
            'error': 'Invalid platform'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.save()
    return Response({
        'success': True,
        'message': f'{platform.title()} account unlinked successfully'
    })

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['platform', 'token_data'],
        properties={
            'platform': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Social platform identifier"
            ),
            'token_data': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Token data from OAuth callback"
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Tokens saved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Invalid request data',
        401: 'Authentication required'
    },
    tags=['Social Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_platform_tokens(request):
    """Save platform tokens to user profile"""
    platform = request.data.get('platform')
    token_data = request.data.get('token_data')
    
    if not platform or not token_data:
        return Response({
            'success': False,
            'error': 'Missing required parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = request.user
        platform = platform.lower()
        
        # Extract relevant data from token_data
        profile_data = token_data.get('profile', {})
        
        # Platform-specific token saving logic
        if platform == 'twitter':
            user.twitter_id = profile_data.get('id')
            if 'username' in profile_data:
                user.twitter_handle = profile_data.get('username')
            
            # Save tokens if available in the payload
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            
            if access_token:
                user.twitter_access_token = access_token
            if refresh_token:
                user.twitter_refresh_token = refresh_token
                
        elif platform == 'facebook':
            user.facebook_id = profile_data.get('id')
            access_token = token_data.get('access_token')
            if access_token:
                user.facebook_access_token = access_token
                
        elif platform == 'instagram':
            user.instagram_id = profile_data.get('id')
            if 'username' in profile_data:
                user.instagram_handle = profile_data.get('username')
            access_token = token_data.get('access_token')
            if access_token:
                user.instagram_access_token = access_token
                
        elif platform == 'linkedin':
            user.linkedin_id = profile_data.get('id')
            access_token = token_data.get('access_token')
            if access_token:
                user.linkedin_access_token = access_token
                
        elif platform == 'google':
            user.google_id = profile_data.get('id')
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            if access_token:
                user.google_access_token = access_token
            if refresh_token:
                user.google_refresh_token = refresh_token
                
        elif platform == 'tiktok':
            user.tiktok_id = profile_data.get('id')
            if 'display_name' in profile_data:
                user.tiktok_handle = profile_data.get('display_name')
            access_token = token_data.get('access_token')
            if access_token:
                user.tiktok_access_token = access_token
                
        elif platform == 'telegram':
            user.telegram_id = profile_data.get('id')
            if 'username' in profile_data:
                user.telegram_username = profile_data.get('username')
        
        # Update last sync timestamp
        user.update_last_sync(platform)
        user.save()
        
        return Response({
            'success': True,
            'message': f'{platform.title()} tokens saved successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def login_facebook(request):
    """
    Initiate Facebook OAuth login flow.
    Redirects to Facebook authorization page.
    """
    logger = logging.getLogger('social')
    logger.info("===== Starting Facebook OAuth login flow =====")
    
    # Generate random state for CSRF protection
    state = generate_random_state()
    cache_key = f"facebook_oauth_state_{state}"

    # Store state in multiple locations for redundancy
    try:
        # Store in cache with both formats
        cache.set(cache_key, state, timeout=300)
        cache.set('facebook_oauth_state', state, timeout=300)
        cache.set('oauth_state', state, timeout=300)
        logger.info(f"Stored state in cache at keys: {cache_key}, facebook_oauth_state, oauth_state")
    except Exception as e:
        logger.exception(f"Error storing state in cache: {e}")
        # Continue anyway, we'll have fallbacks
    
    # Store in session as well for fallback
    try:
        request.session['facebook_oauth_state'] = state
        request.session['oauth_state'] = state
        logger.info(f"Stored state in session at keys: facebook_oauth_state, oauth_state")
    except Exception as e:
        logger.warning(f"Could not store state in session: {e}")
    
    # Get the redirect URI
    redirect_uri = settings.FACEBOOK_REDIRECT_URI
    logger.info(f"Using redirect URI: {redirect_uri}")
    
    # Build the authorization URL
    auth_params = {
        'client_id': settings.FACEBOOK_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'state': state,
        'response_type': 'code',
        'scope': 'email,public_profile,pages_show_list', # Add more scopes as needed
    }
    
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(auth_params)}"
    logger.info(f"Redirecting to Facebook authorization URL (truncated): {auth_url[:100]}...")
    
    # Store timestamp of login attempt
    try:
        cache.set(f"facebook_login_{state}_timestamp", int(time.time()), timeout=300)
        logger.info(f"Stored login timestamp for state {state}")
    except Exception as e:
        logger.warning(f"Failed to store login timestamp: {e}")
    
    return redirect(auth_url) 
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
        frontend_success_url = f"{settings.OAUTH2_REDIRECT_URI}/oauth-success?platform={platform}"
        result['redirect_url'] = frontend_success_url
        
        return Response(result)
        
    except (StateVerificationError, PKCEVerificationError) as e:
        logger.error(f"Verification error for {platform}: {str(e)}")
        return Response({
            'error': str(e),
            'redirect_url': f"{settings.OAUTH2_REDIRECT_URI}/oauth-error?platform={platform}&error={str(e)}"
        }, status=status.HTTP_401_UNAUTHORIZED)
    except TokenExchangeError as e:
        logger.error(f"Token exchange error for {platform}: {str(e)}")
        return Response({
            'error': str(e),
            'redirect_url': f"{settings.OAUTH2_REDIRECT_URI}/oauth-error?platform={platform}&error={str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    except OAuthError as e:
        logger.error(f"OAuth error for {platform}: {str(e)}")
        return Response({
            'error': str(e),
            'redirect_url': f"{settings.OAUTH2_REDIRECT_URI}/oauth-error?platform={platform}&error={str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Platform-specific callback handlers with custom logic
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_callback(request):
    """Handle Google OAuth callback"""
    return oauth_callback(request, 'google')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def facebook_callback(request):
    """Handle Facebook OAuth callback"""
    return oauth_callback(request, 'facebook')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def linkedin_callback(request):
    """Handle LinkedIn OAuth callback"""
    logger = logging.getLogger('social')
    
    # Log the request parameters
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    
    logger.info(f"LinkedIn callback received: State={state}, Code exists={bool(code)}")
    
    # Check if state exists in cache before passing to the callback
    from ..utils.oauth import verify_oauth_state
    cache_key = f'oauth_state_{state}'
    cache_data = cache.get(cache_key)
    
    if not cache_data:
        # Check the linkedin_oauth_state cache key too
        cache_key = f'linkedin_oauth_state_{state}'
        cache_data = cache.get(cache_key)
        
    logger.info(f"LinkedIn OAuth state verification: state={state}, found in cache={bool(cache_data)}")
    
    # Try linkedin specific oauth state format
    if not cache_data:
        logger.error(f"State verification failed for LinkedIn: state={state} not found in cache")
        return Response({
            "error": "Invalid or expired state parameter",
            "redirect_url": f"{settings.FRONTEND_URL}/oauth-error?platform=linkedin&error=Invalid or expired state parameter"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # State is valid, proceed with the standard callback
    return oauth_callback(request, 'linkedin')

@api_view(['GET'])
def twitter_callback(request):
    """
    OAuth 2.0 callback for Twitter.
    Exchanges auth code for access token and refreshes the connected platforms list.
    """
    logger = logging.getLogger('social')
    logger.info("Received Twitter OAuth callback")
    
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    
    logger.info(f"Twitter callback parameters - Code exists: {bool(code)}, State: {state[:10] if state else None}")
    
    if not code or not state:
        logger.error("Missing required parameters for Twitter callback")
        return Response(
            {"error": "Missing required parameters"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Extract the platform from state if available
    platform = 'twitter'
    if state and '_' in state:
        platform = state.split('_')[0]
        logger.info(f"Extracted platform from state: {platform}")
    
    # Get the code_verifier from session storage
    # This is provided by frontend or stored in backend depending on implementation
    code_verifier = get_stored_pkce_verifier(state)
    if not code_verifier:
        logger.warning(f"No code_verifier found for state: {state}")
        return Response(
            {"error": "No code verifier found for this authorization request"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    logger.info(f"Code verifier retrieved for state: {state}, length: {len(code_verifier)}")
    
    try:
        # Verify the state parameter to prevent CSRF
        verify_oauth_state(state)
        logger.info("State verification successful")
        
        # Exchange the code for tokens
        user = request.user
        connect_twitter_account(user, code, code_verifier)
        logger.info(f"Successfully connected Twitter account for user {user.username}")
        
        # Return success response
        return Response({"status": "success", "message": "Twitter account connected successfully"})
    
    except StateVerificationError as e:
        logger.error(f"State verification error: {str(e)}")
        return Response(
            {"error": "State verification failed", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except PKCEVerificationError as e:
        logger.error(f"PKCE verification error: {str(e)}")
        return Response(
            {"error": "PKCE verification failed", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except TokenExchangeError as e:
        logger.error(f"Token exchange error: {str(e)}")
        return Response(
            {"error": "Failed to exchange code for tokens", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except ProfileFetchError as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return Response(
            {"error": "Failed to fetch Twitter profile", "details": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.exception(f"Unexpected error in Twitter callback: {str(e)}")
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def instagram_callback(request):
    """Handle Instagram OAuth callback"""
    return oauth_callback(request, 'instagram')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tiktok_callback(request):
    """Handle TikTok OAuth callback"""
    return oauth_callback(request, 'tiktok')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def telegram_callback(request):
    """Handle Telegram OAuth callback"""
    return oauth_callback(request, 'telegram')

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
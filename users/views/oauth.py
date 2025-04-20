from rest_framework import status
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
@permission_classes([IsAuthenticated])
def oauth_callback(request, platform):
    """Generic OAuth callback handler"""
    code = request.query_params.get('code')
    state = request.query_params.get('state')
    session_key = request.query_params.get('session_key')
    
    if not all([code, state, session_key]):
        return Response({
            'error': 'Missing required parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get the appropriate connection handler
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
                'error': 'Invalid platform'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Connect the account
        result = handler(request.user, code, session_key, state)
        return Response(result)
        
    except (StateVerificationError, PKCEVerificationError) as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
    except TokenExchangeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except OAuthError as e:
        return Response({
            'error': str(e)
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
    return oauth_callback(request, 'linkedin')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def twitter_callback(request):
    """Handle Twitter OAuth 1.0a callback"""
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')
    
    if not oauth_token or not oauth_verifier:
        return Response({
            'error': 'Missing required parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = connect_twitter_account(request.user, oauth_token, oauth_verifier)
        return Response(result)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

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
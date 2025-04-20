from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import tweepy
from django.conf import settings
import logging
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Google Account",
    operation_description="Connect a Google account using OAuth token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_google(request):
    """Connect Google account"""
    try:
        result = request.user.connect_google(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Facebook Account",
    operation_description="Connect a Facebook account using OAuth token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_facebook(request):
    """Connect Facebook account"""
    try:
        result = request.user.connect_facebook(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect LinkedIn Account",
    operation_description="Connect a LinkedIn account using OAuth token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_linkedin(request):
    """Connect LinkedIn account"""
    try:
        result = request.user.connect_linkedin(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Twitter Account",
    operation_description="Connect a Twitter account using OAuth 2.0 tokens",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['code', 'state', 'code_verifier'],
        properties={
            'code': openapi.Schema(type=openapi.TYPE_STRING),
            'state': openapi.Schema(type=openapi.TYPE_STRING),
            'code_verifier': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid parameters',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_twitter(request):
    """Connect Twitter account using OAuth 2.0"""
    logger = logging.getLogger('social')
    
    code = request.data.get('code')
    state = request.data.get('state')
    code_verifier = request.data.get('code_verifier')
    
    if not all([code, state, code_verifier]):
        return Response({
            'error': 'code, state, and code_verifier are all required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from ..services.oauth import connect_twitter_account
        
        # Convert the async function to sync
        connect_twitter_sync = sync_to_async(connect_twitter_account)
        result = connect_twitter_sync(request.user, code, state, code_verifier)
        
        return Response(result)
            
    except tweepy.errors.TwitterException as e:
        logger.error(f"Twitter API error: {str(e)}")
        return Response({
            'error': f"Twitter API error: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Twitter connection error: {str(e)}")
        return Response({
            'error': f"Twitter connection failed: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Instagram Account",
    operation_description="Connect an Instagram account using OAuth token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_instagram(request):
    """Connect Instagram account"""
    try:
        result = request.user.connect_instagram(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect TikTok Account",
    operation_description="Connect a TikTok account using OAuth token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_tiktok(request):
    """Connect TikTok account"""
    try:
        result = request.user.connect_tiktok(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Telegram Account",
    operation_description="Connect a Telegram account using Bot API token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_telegram(request):
    """Connect Telegram account"""
    try:
        result = request.user.connect_telegram(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Business Account Connection Views

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Facebook Page",
    operation_description="Connect a Facebook business page",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['page_id', 'access_token'],
        properties={
            'page_id': openapi.Schema(type=openapi.TYPE_STRING),
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Page connected successfully',
        400: 'Invalid page ID or token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_facebook_page(request):
    """Connect Facebook business page"""
    try:
        result = request.user.connect_facebook_page(
            request.data.get('page_id'),
            request.data.get('access_token')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Instagram Business",
    operation_description="Connect an Instagram business account",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['account_id', 'access_token'],
        properties={
            'account_id': openapi.Schema(type=openapi.TYPE_STRING),
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid account ID or token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_instagram_business(request):
    """Connect Instagram business account"""
    try:
        result = request.user.connect_instagram_business(
            request.data.get('account_id'),
            request.data.get('access_token')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect LinkedIn Company",
    operation_description="Connect a LinkedIn company page",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['company_id', 'access_token'],
        properties={
            'company_id': openapi.Schema(type=openapi.TYPE_STRING),
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Company connected successfully',
        400: 'Invalid company ID or token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_linkedin_company(request):
    """Connect LinkedIn company page"""
    try:
        result = request.user.connect_linkedin_company(
            request.data.get('company_id'),
            request.data.get('access_token')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect TikTok Business",
    operation_description="Connect a TikTok business account",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['account_id', 'access_token'],
        properties={
            'account_id': openapi.Schema(type=openapi.TYPE_STRING),
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Account connected successfully',
        400: 'Invalid account ID or token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_tiktok_business(request):
    """Connect TikTok business account"""
    try:
        result = request.user.connect_tiktok_business(
            request.data.get('account_id'),
            request.data.get('access_token')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Telegram Channel",
    operation_description="Connect a Telegram channel",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['channel_id', 'access_token'],
        properties={
            'channel_id': openapi.Schema(type=openapi.TYPE_STRING),
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: 'Channel connected successfully',
        400: 'Invalid channel ID or token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_telegram_channel(request):
    """Connect Telegram channel"""
    try:
        result = request.user.connect_telegram_channel(
            request.data.get('channel_id'),
            request.data.get('access_token')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) 
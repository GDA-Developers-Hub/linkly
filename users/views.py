from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.urls import reverse
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import json
import hashlib
import hmac
import tweepy
import stripe
from django.db.models import Q
from datetime import datetime, timedelta
from .models import SubscriptionPlan, Subscription
from .utils import get_stripe_instance, get_stripe_public_key

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    Enable2FASerializer,
    Verify2FASerializer
)

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: UserSerializer()}
    )
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Start free trial
                user.start_free_trial()
                
                return Response({
                    'status': 'success',
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data provided',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web token pair.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Obtain JWT token pair with user credentials",
        responses={
            200: openapi.Response(
                description="JWT token pair obtained successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: openapi.Response(description="Invalid credentials")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class Enable2FAView(generics.GenericAPIView):
    """
    Enable Two-Factor Authentication for a user account.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = Enable2FASerializer

    @swagger_auto_schema(
        operation_description="Enable 2FA for user account",
        responses={
            200: openapi.Response(
                description="2FA enabled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'qr_code': openapi.Schema(type=openapi.TYPE_STRING),
                        'secret': openapi.Schema(type=openapi.TYPE_STRING),
                        'backup_codes': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            401: openapi.Response(description="Authentication credentials not provided")
        }
    )
    def post(self, request):
        user = request.user
        secret = user.enable_2fa()
        backup_codes = user.backup_codes
        serializer = self.get_serializer(user)
        
        return Response({
            'qr_code': serializer.data['qr_code'],
            'secret': secret,
            'backup_codes': backup_codes
        })

class Verify2FAView(generics.GenericAPIView):
    """
    Verify Two-Factor Authentication code.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = Verify2FASerializer

    @swagger_auto_schema(
        operation_description="Verify 2FA code and obtain tokens",
        request_body=Verify2FASerializer,
        responses={
            200: openapi.Response(
                description="2FA verification successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(description="Invalid 2FA code")
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }
        
        user.update_jwt_tokens(data['access'], data['refresh'])
        return Response(data)

class ChangePasswordView(generics.UpdateAPIView):
    """
    Change user password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(description="Invalid password data")
        }
    )
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"message": "Password updated successfully"}, 
                          status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        return self.request.user

class UpdateProfileView(generics.UpdateAPIView):
    """
    Update user profile information.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    @swagger_auto_schema(
        operation_description="Update user profile",
        request_body=UpdateUserSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=UserSerializer
            ),
            400: openapi.Response(description="Invalid profile data")
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update user profile",
        request_body=UpdateUserSerializer,
        responses={
            200: openapi.Response(
                description="Profile partially updated successfully",
                schema=UserSerializer
            ),
            400: openapi.Response(description="Invalid profile data")
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class UserProfileView(generics.RetrieveAPIView):
    """
    Retrieve user profile information.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Get user profile information",
        responses={
            200: openapi.Response(
                description="Profile retrieved successfully",
                schema=UserSerializer
            ),
            401: openapi.Response(description="Authentication credentials not provided")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class ValidateTokenView(generics.GenericAPIView):
    """
    Validate JWT token and return user information.
    """
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        operation_description="Validate JWT token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token'],
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Token is valid",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            401: openapi.Response(description="Token is invalid")
        }
    )
    def post(self, request):
        token = request.data.get('token')
        try:
            user = User.objects.get(access_token_jwt=token)
            if user.token_created_at and (datetime.now() - user.token_created_at).days < 1:
                return Response({'valid': True, 'user': UserSerializer(user).data})
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='post',
    operation_description="Handle Google OAuth2 callback",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response(
            description="Google authentication successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            'access': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    ),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: openapi.Response(description="Invalid Google token")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def google_auth_callback(request):
    """Handle Google OAuth2 callback"""
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        # Verify token with Google
        google_user_info = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        ).json()
        
        if 'error' in google_user_info:
            return JsonResponse({'error': 'Invalid Google token'}, status=400)
        
        email = google_user_info.get('email')
        google_id = google_user_info.get('sub')
        
        user, created = User.objects.get_or_create(
            google_id=google_id,
            defaults={
                'email': email,
                'username': email,
                'first_name': google_user_info.get('given_name', ''),
                'last_name': google_user_info.get('family_name', ''),
            }
        )
        
        user.update_social_token('google', access_token)
        
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return JsonResponse({
            'tokens': tokens,
            'user': {
                'id': user.id,
                'email': user.email,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="Handle Facebook OAuth2 callback",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response(
            description="Facebook authentication successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            'access': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    ),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: openapi.Response(description="Invalid Facebook token")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def facebook_auth_callback(request):
    """Handle Facebook OAuth2 callback"""
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        # Verify token with Facebook
        fb_user_info = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,email,first_name,last_name',
                'access_token': access_token
            }
        ).json()
        
        if 'error' in fb_user_info:
            return JsonResponse({'error': 'Invalid Facebook token'}, status=400)
        
        email = fb_user_info.get('email')
        facebook_id = fb_user_info.get('id')
        
        # Get or create user
        user, created = User.objects.get_or_create(
            facebook_id=facebook_id,
            defaults={
                'email': email,
                'username': email,
                'first_name': fb_user_info.get('first_name', ''),
                'last_name': fb_user_info.get('last_name', ''),
            }
        )
        
        # Update user's Facebook token
        user.update_social_token('facebook', access_token)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return JsonResponse({
            'tokens': tokens,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f'{user.first_name} {user.last_name}'.strip(),
                'is_business': user.is_business,
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="Handle LinkedIn OAuth2 callback",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response(
            description="LinkedIn authentication successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            'access': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    ),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: openapi.Response(description="Invalid LinkedIn token")
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def linkedin_auth_callback(request):
    """Handle LinkedIn OAuth2 callback"""
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        company_id = data.get('company_id')
        
        if not access_token or not company_id:
            return Response({
                'error': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get company details
        headers = {'Authorization': f'Bearer {access_token}'}
        company_info = requests.get(
            f'https://api.linkedin.com/v2/organizations/{company_id}',
            headers=headers
        ).json()
        
        if 'error' in company_info:
            return Response({
                'error': 'Invalid access token or company ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get follower statistics
        follower_stats = requests.get(
            f'https://api.linkedin.com/v2/organizations/{company_id}/followingStatistics',
            headers=headers
        ).json()
        
        user = request.user
        user.linkedin_company_id = company_id
        user.linkedin_company_token = access_token
        user.linkedin_company_name = company_info.get('localizedName')
        user.linkedin_company_page = f"https://www.linkedin.com/company/{company_id}"
        user.linkedin_company_followers = follower_stats.get('totalFollowerCount', 0)
        user.has_linkedin_company = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'company': {
                'id': company_id,
                'name': user.linkedin_company_name,
                'url': user.linkedin_company_page,
                'followers': user.linkedin_company_followers
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlink_social_account(request, platform):
    """Unlink a social media account"""
    try:
        user = request.user
        platform_id = f"{platform}_id"
        platform_token = f"{platform}_access_token"
        platform_expiry = f"{platform}_token_expiry"
        
        if hasattr(user, platform_id):
            setattr(user, platform_id, None)
            setattr(user, platform_token, None)
            setattr(user, platform_expiry, None)
            user.save()
            
            return JsonResponse({'message': f'{platform.title()} account unlinked successfully'})
        else:
            return JsonResponse({'error': 'Invalid platform'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_youtube(request):
    """Connect YouTube account to existing user"""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        
        # Exchange code for tokens
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
        ).json()
        
        if 'error' in token_response:
            return JsonResponse({'error': 'Invalid YouTube authorization code'}, status=400)
        
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        expires_in = token_response.get('expires_in', 3600)
        
        # Get YouTube channel info
        headers = {'Authorization': f'Bearer {access_token}'}
        channel_response = requests.get(
            'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true',
            headers=headers
        ).json()
        
        if 'error' in channel_response:
            return JsonResponse({'error': 'Failed to fetch YouTube channel info'}, status=400)
        
        channel = channel_response.get('items', [{}])[0]
        channel_id = channel.get('id')
        channel_title = channel.get('snippet', {}).get('title')
        
        # Update user's YouTube info
        user = request.user
        user.youtube_id = channel_id
        user.youtube_channel_id = channel_id
        user.youtube_channel_title = channel_title
        user.youtube_channel = f'https://www.youtube.com/channel/{channel_id}'
        user.youtube_access_token = access_token
        user.youtube_refresh_token = refresh_token
        user.update_social_token('youtube', access_token, expires_in)
        user.save()
        
        return JsonResponse({
            'message': 'YouTube account connected successfully',
            'channel': {
                'id': channel_id,
                'title': channel_title,
                'url': user.youtube_channel
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_facebook(request):
    """Connect Facebook account to existing user"""
    try:
        data = json.loads(request.body)
        access_token = data.get('access_token')
        
        # Verify Facebook token and get user info
        fb_user_info = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,email,name,picture',
                'access_token': access_token
            }
        ).json()
        
        if 'error' in fb_user_info:
            return JsonResponse({'error': 'Invalid Facebook token'}, status=400)
        
        facebook_id = fb_user_info.get('id')
        
        # Check if this Facebook account is already connected to another user
        if User.objects.filter(facebook_id=facebook_id).exclude(id=request.user.id).exists():
            return JsonResponse({'error': 'This Facebook account is already connected to another user'}, status=400)
        
        # Update user's Facebook info
        user = request.user
        user.facebook_id = facebook_id
        user.facebook_page = f'https://facebook.com/{facebook_id}'
        user.update_social_token('facebook', access_token)
        user.save()
        
        return JsonResponse({
            'message': 'Facebook account connected successfully',
            'facebook_id': facebook_id,
            'facebook_page': user.facebook_page
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_connected_accounts(request):
    """Get user's connected social accounts"""
    user = request.user
    
    connected_accounts = {
        'google': bool(user.google_id),
        'facebook': bool(user.facebook_id),
        'linkedin': bool(user.linkedin_id),
        'youtube': bool(user.youtube_id),
        'telegram': bool(user.telegram_id),
        'instagram': bool(user.instagram_id),
        'twitter': bool(user.twitter_id),
        'tiktok': bool(user.tiktok_id),
        'accounts': {
            'google': {
                'connected': bool(user.google_id),
                'email': user.email if user.google_id else None,
                'token_valid': user.is_social_token_valid('google')
            },
            'facebook': {
                'connected': bool(user.facebook_id),
                'page_url': user.facebook_page if user.facebook_id else None,
                'token_valid': user.is_social_token_valid('facebook')
            },
            'youtube': {
                'connected': bool(user.youtube_id),
                'channel_title': user.youtube_channel_title if user.youtube_id else None,
                'channel_url': user.youtube_channel if user.youtube_id else None,
                'token_valid': user.is_social_token_valid('youtube')
            },
            'telegram': {
                'connected': bool(user.telegram_id),
                'username': user.telegram_username if user.telegram_id else None,
                'chat_id': user.telegram_chat_id if user.telegram_id else None,
                'token_valid': user.is_social_token_valid('telegram')
            },
            'instagram': {
                'connected': bool(user.instagram_id),
                'username': user.instagram_handle if user.instagram_id else None,
                'profile_url': user.instagram_profile_url if user.instagram_id else None,
                'token_valid': user.is_social_token_valid('instagram')
            },
            'twitter': {
                'connected': bool(user.twitter_id),
                'username': user.twitter_handle if user.twitter_id else None,
                'profile_url': user.twitter_profile_url if user.twitter_id else None,
                'token_valid': user.is_social_token_valid('twitter')
            },
            'tiktok': {
                'connected': bool(user.tiktok_id),
                'username': user.tiktok_handle if user.tiktok_id else None,
                'profile_url': user.tiktok_profile_url if user.tiktok_id else None,
                'token_valid': user.is_social_token_valid('tiktok')
            }
        }
    }
    
    return JsonResponse(connected_accounts)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_telegram(request):
    """Connect Telegram account to existing user"""
    try:
        data = json.loads(request.body)
        auth_data = data.get('auth_data')  # Telegram auth data from Widget
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Verify Telegram auth data
        auth_string = []
        for key in sorted(auth_data.keys()):
            if key != 'hash':
                auth_string.append(f'{key}={auth_data[key]}')
        
        auth_string = '\n'.join(auth_string)
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        hash = hmac.new(secret_key, auth_string.encode(), hashlib.sha256).hexdigest()
        
        if hash != auth_data['hash']:
            return JsonResponse({'error': 'Invalid Telegram authentication'}, status=400)
        
        telegram_id = str(auth_data.get('id'))
        username = auth_data.get('username', '')
        first_name = auth_data.get('first_name', '')
        
        # Check if this Telegram account is already connected to another user
        if User.objects.filter(telegram_id=telegram_id).exclude(id=request.user.id).exists():
            return JsonResponse({'error': 'This Telegram account is already connected to another user'}, status=400)
        
        # Update user's Telegram info
        user = request.user
        user.telegram_id = telegram_id
        user.telegram_username = username
        user.telegram_chat_id = telegram_id  # Used for sending notifications
        user.save()
        
        # Optional: Send welcome message via Telegram bot
        try:
            bot_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            message = f'Hello {first_name}! Your Linkly account has been successfully connected.'
            requests.post(bot_url, json={
                'chat_id': telegram_id,
                'text': message
            })
        except Exception as e:
            # Log the error but don't fail the connection
            print(f"Failed to send Telegram welcome message: {str(e)}")
        
        return JsonResponse({
            'message': 'Telegram account connected successfully',
            'telegram_data': {
                'id': telegram_id,
                'username': username,
                'first_name': first_name
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_instagram(request):
    """Connect Instagram account to existing user"""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        
        # Exchange code for token
        token_response = requests.post(
            'https://api.instagram.com/oauth/access_token',
            data={
                'client_id': settings.INSTAGRAM_CLIENT_ID,
                'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
                'code': code
            }
        ).json()
        
        if 'error' in token_response:
            return JsonResponse({'error': 'Invalid Instagram authorization code'}, status=400)
        
        access_token = token_response.get('access_token')
        user_id = token_response.get('user_id')
        
        # Get user profile
        profile_response = requests.get(
            f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}'
        ).json()
        
        if 'error' in profile_response:
            return JsonResponse({'error': 'Failed to fetch Instagram profile'}, status=400)
        
        instagram_id = profile_response.get('id')
        username = profile_response.get('username')
        
        # Check if this Instagram account is already connected
        if User.objects.filter(instagram_id=instagram_id).exclude(id=request.user.id).exists():
            return JsonResponse({'error': 'This Instagram account is already connected to another user'}, status=400)
        
        # Update user's Instagram info
        user = request.user
        user.instagram_id = instagram_id
        user.instagram_handle = username
        user.instagram_profile_url = f'https://instagram.com/{username}'
        user.instagram_access_token = access_token
        user.update_social_token('instagram', access_token)
        user.save()
        
        return JsonResponse({
            'message': 'Instagram account connected successfully',
            'instagram_data': {
                'id': instagram_id,
                'username': username,
                'profile_url': user.instagram_profile_url
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_twitter(request):
    """Connect Twitter/X account to existing user"""
    try:
        data = json.loads(request.body)
        oauth_token = data.get('oauth_token')
        oauth_verifier = data.get('oauth_verifier')
        
        # Exchange OAuth tokens
        auth = tweepy.OAuthHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET
        )
        auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}
        
        try:
            auth.get_access_token(oauth_verifier)
        except tweepy.TweepError:
            return JsonResponse({'error': 'Failed to verify Twitter credentials'}, status=400)
        
        access_token = auth.access_token
        access_token_secret = auth.access_token_secret
        
        # Get user profile
        api = tweepy.API(auth)
        twitter_user = api.verify_credentials()
        
        twitter_id = str(twitter_user.id)
        username = twitter_user.screen_name
        
        # Check if this Twitter account is already connected
        if User.objects.filter(twitter_id=twitter_id).exclude(id=request.user.id).exists():
            return JsonResponse({'error': 'This Twitter account is already connected to another user'}, status=400)
        
        # Update user's Twitter info
        user = request.user
        user.twitter_id = twitter_id
        user.twitter_handle = username
        user.twitter_profile_url = f'https://twitter.com/{username}'
        user.twitter_access_token = access_token
        user.twitter_access_token_secret = access_token_secret
        user.update_social_token('twitter', access_token)
        user.save()
        
        return JsonResponse({
            'message': 'Twitter account connected successfully',
            'twitter_data': {
                'id': twitter_id,
                'username': username,
                'profile_url': user.twitter_profile_url
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_tiktok(request):
    """Connect TikTok account to existing user"""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        
        # Exchange code for token
        token_response = requests.post(
            'https://open-api.tiktok.com/oauth/access_token/',
            params={
                'client_key': settings.TIKTOK_CLIENT_KEY,
                'client_secret': settings.TIKTOK_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code'
            }
        ).json()
        
        if 'data' not in token_response or 'error' in token_response:
            return JsonResponse({'error': 'Invalid TikTok authorization code'}, status=400)
        
        data = token_response['data']
        access_token = data.get('access_token')
        open_id = data.get('open_id')
        
        # Get user info
        user_response = requests.get(
            'https://open-api.tiktok.com/user/info/',
            params={
                'access_token': access_token,
                'open_id': open_id,
                'fields': ['open_id', 'union_id', 'avatar_url', 'display_name']
            }
        ).json()
        
        if 'data' not in user_response or 'error' in user_response:
            return JsonResponse({'error': 'Failed to fetch TikTok user info'}, status=400)
        
        tiktok_data = user_response['data']
        display_name = tiktok_data.get('display_name')
        
        # Check if this TikTok account is already connected
        if User.objects.filter(tiktok_id=open_id).exclude(id=request.user.id).exists():
            return JsonResponse({'error': 'This TikTok account is already connected to another user'}, status=400)
        
        # Update user's TikTok info
        user = request.user
        user.tiktok_id = open_id
        user.tiktok_handle = display_name
        user.tiktok_profile_url = f'https://tiktok.com/@{display_name}'
        user.tiktok_access_token = access_token
        user.update_social_token('tiktok', access_token)
        user.save()
        
        return JsonResponse({
            'message': 'TikTok account connected successfully',
            'tiktok_data': {
                'id': open_id,
                'display_name': display_name,
                'profile_url': user.tiktok_profile_url
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_facebook_page(request):
    """Connect a Facebook Business Page"""
    try:
        page_id = request.data.get('page_id')
        access_token = request.data.get('access_token')
        
        if not page_id or not access_token:
            return Response({
                'error': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify page access token and get page details
        page_info = requests.get(
            f'https://graph.facebook.com/v18.0/{page_id}',
            params={
                'access_token': access_token,
                'fields': 'name,category,fan_count,link'
            }
        ).json()
        
        if 'error' in page_info:
            return Response({
                'error': 'Invalid page access token or page ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.facebook_page_id = page_id
        user.facebook_page_token = access_token
        user.facebook_page_name = page_info.get('name')
        user.facebook_page_category = page_info.get('category')
        user.facebook_page = page_info.get('link')
        user.facebook_page_followers = page_info.get('fan_count', 0)
        user.has_facebook_business = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'page': {
                'id': page_id,
                'name': user.facebook_page_name,
                'category': user.facebook_page_category,
                'followers': user.facebook_page_followers,
                'url': user.facebook_page
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    operation_description="Connect Instagram Business Account",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['code', 'redirect_uri'],
        properties={
            'code': openapi.Schema(type=openapi.TYPE_STRING),
            'redirect_uri': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response(
            description="Instagram Business Account connected successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'account_info': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: openapi.Response(description="Invalid Instagram code")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_instagram_business(request):
    """Connect Instagram Business Account"""
    try:
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        
        if not code or not redirect_uri:
            return Response({
                'error': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for token
        token_response = requests.post(
            'https://api.instagram.com/oauth/access_token',
            data={
                'client_id': settings.INSTAGRAM_CLIENT_ID,
                'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
                'code': code
            }
        ).json()
        
        if 'error' in token_response:
            return Response({
                'error': token_response['error_message']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_response['access_token']
        instagram_user_id = token_response['user_id']
        
        # Get user info
        user_info = requests.get(
            f'https://graph.instagram.com/v12.0/{instagram_user_id}',
            params={
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }
        ).json()
        
        if user_info.get('account_type') != 'BUSINESS':
            return Response({
                'error': 'This endpoint requires an Instagram Business Account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.instagram_business_id = instagram_user_id
        user.instagram_business_name = user_info['username']
        user.instagram_business_token = access_token
        user.has_instagram_business = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'account_info': {
                'id': user.instagram_business_id,
                'username': user.instagram_business_name,
                'media_count': user_info.get('media_count', 0)
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_linkedin_company(request):
    """Connect a LinkedIn Company Page"""
    try:
        access_token = request.data.get('access_token')
        company_id = request.data.get('company_id')
        
        if not access_token or not company_id:
            return Response({
                'error': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get company details
        headers = {'Authorization': f'Bearer {access_token}'}
        company_info = requests.get(
            f'https://api.linkedin.com/v2/organizations/{company_id}',
            headers=headers
        ).json()
        
        if 'error' in company_info:
            return Response({
                'error': 'Invalid access token or company ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get follower statistics
        follower_stats = requests.get(
            f'https://api.linkedin.com/v2/organizations/{company_id}/followingStatistics',
            headers=headers
        ).json()
        
        user = request.user
        user.linkedin_company_id = company_id
        user.linkedin_company_token = access_token
        user.linkedin_company_name = company_info.get('localizedName')
        user.linkedin_company_page = f"https://www.linkedin.com/company/{company_id}"
        user.linkedin_company_followers = follower_stats.get('totalFollowerCount', 0)
        user.has_linkedin_company = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'company': {
                'id': company_id,
                'name': user.linkedin_company_name,
                'url': user.linkedin_company_page,
                'followers': user.linkedin_company_followers
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_youtube_brand(request):
    """Connect a YouTube Brand Account"""
    try:
        access_token = request.data.get('access_token')
        brand_id = request.data.get('brand_id')
        
        if not access_token or not brand_id:
            return Response({
                'error': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get channel details
        headers = {'Authorization': f'Bearer {access_token}'}
        channel_info = requests.get(
            'https://youtube.googleapis.com/youtube/v3/channels',
            params={
                'part': 'snippet,statistics',
                'id': brand_id
            },
            headers=headers
        ).json()
        
        if 'error' in channel_info:
            return Response({
                'error': 'Invalid access token or brand ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        channel = channel_info.get('items', [{}])[0]
        snippet = channel.get('snippet', {})
        statistics = channel.get('statistics', {})
        
        user = request.user
        user.youtube_brand_id = brand_id
        user.youtube_brand_token = access_token
        user.youtube_brand_name = snippet.get('title')
        user.youtube_channel = f"https://youtube.com/channel/{brand_id}"
        user.youtube_subscribers = int(statistics.get('subscriberCount', 0))
        user.has_youtube_brand = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'channel': {
                'id': brand_id,
                'name': user.youtube_brand_name,
                'url': user.youtube_channel,
                'subscribers': user.youtube_subscribers
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_tiktok_business(request):
    """Connect a TikTok Business Account"""
    try:
        code = request.data.get('code')
        
        if not code:
            return Response({
                'error': 'Missing authorization code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for access token
        token_response = requests.post(
            'https://open-api.tiktok.com/oauth/access_token/',
            params={
                'client_key': settings.TIKTOK_CLIENT_KEY,
                'client_secret': settings.TIKTOK_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code'
            }
        ).json()
        
        if 'error' in token_response:
            return Response({
                'error': 'Invalid authorization code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_response.get('access_token')
        open_id = token_response.get('open_id')
        
        # Get business account info
        account_info = requests.get(
            'https://open-api.tiktok.com/business/profile/info/',
            params={
                'access_token': access_token,
                'open_id': open_id
            }
        ).json()
        
        user = request.user
        user.tiktok_business_id = open_id
        user.tiktok_business_token = access_token
        user.tiktok_business_name = account_info.get('display_name')
        user.tiktok_business_category = account_info.get('category')
        user.tiktok_profile_url = f"https://tiktok.com/@{account_info.get('username')}"
        user.tiktok_followers = account_info.get('follower_count', 0)
        user.has_tiktok_business = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'account': {
                'id': open_id,
                'name': user.tiktok_business_name,
                'category': user.tiktok_business_category,
                'url': user.tiktok_profile_url,
                'followers': user.tiktok_followers
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    operation_description="Connect Instagram Business Account",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['access_token'],
        properties={
            'access_token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response(
            description="Instagram Business Account connected successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'account_info': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: openapi.Response(description="Invalid access token")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_telegram_channel(request):
    """Connect a Telegram Channel"""
    try:
        channel_id = request.data.get('channel_id')
        channel_name = request.data.get('channel_name')
        
        if not channel_id or not channel_name:
            return Response({
                'error': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify bot ownership and get channel info
        bot_token = settings.TELEGRAM_BOT_TOKEN
        channel_info = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChat',
            params={'chat_id': channel_id}
        ).json()
        
        if not channel_info.get('ok'):
            return Response({
                'error': 'Invalid channel ID or bot is not an admin'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get member count
        member_count = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChatMemberCount',
            params={'chat_id': channel_id}
        ).json()
        
        user = request.user
        user.telegram_chat_id = channel_id
        user.telegram_channel_name = channel_name
        user.telegram_subscribers = member_count.get('result', 0)
        user.has_telegram_channel = True
        user.metrics_last_updated = datetime.now()
        user.save()
        
        return Response({
            'success': True,
            'channel': {
                'id': channel_id,
                'name': channel_name,
                'subscribers': user.telegram_subscribers
            }
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['plan_id'],
        properties={
            'plan_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the subscription plan')
        }
    ),
    responses={
        200: openapi.Response(
            description="Checkout session created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'url': openapi.Schema(type=openapi.TYPE_STRING, description='Checkout session URL'),
                    'session_id': openapi.Schema(type=openapi.TYPE_STRING, description='Stripe session ID')
                }
            )
        ),
        400: 'Invalid plan ID',
        401: 'Authentication required'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    Create a Stripe checkout session
    """
    stripe = get_stripe_instance()
    
    try:
        plan_id = request.data.get('plan_id')
        success_url = request.data.get('success_url', settings.STRIPE_SUCCESS_URL)
        cancel_url = request.data.get('cancel_url', settings.STRIPE_CANCEL_URL)

        # Get the subscription plan
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({
                'error': 'Invalid subscription plan'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Linkly {plan.name} Plan',
                        'description': f'Upgrade to {plan.name} Plan',
                    },
                    'unit_amount': int(plan.price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
            }
        )

        return Response({
            'session_id': checkout_session.id,
            'url': checkout_session.url
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    operation_description="Handle Stripe webhook events for subscription updates",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'type': openapi.Schema(type=openapi.TYPE_STRING, description='Stripe event type'),
            'data': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'object': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description='Event object data'
                    )
                }
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Webhook processed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='Success status')
                }
            )
        ),
        400: 'Invalid webhook data',
        401: 'Invalid Stripe signature'
    },
    security=[],  # No authentication required for webhook
)
@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get user and plan from metadata
        user_id = session.get('metadata', {}).get('user_id')
        plan_id = session.get('metadata', {}).get('plan_id')
        
        try:
            user = User.objects.get(id=user_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)
            
            # Create new subscription
            subscription = user.subscribe_to_plan(
                plan=plan,
                payment_method='stripe'
            )
            
            # Send confirmation email
            send_mail(
                'Subscription Upgraded Successfully',
                f'Your subscription has been upgraded to {plan.name} plan.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            
        except (User.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'success'})

@swagger_auto_schema(
    operation_description="Get current subscription status and details",
    responses={
        200: openapi.Response('Subscription details retrieved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'plan': openapi.Schema(type=openapi.TYPE_STRING),
                    'features': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING)
                    ),
                    'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                }
            )
        ),
        401: 'Authentication required'
    }
)
class SubscriptionStatusView(APIView):
    """View to check subscription status and details"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current user's subscription status",
        responses={
            200: openapi.Response(
                description="Subscription status retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether subscription is active'),
                        'plan': openapi.Schema(type=openapi.TYPE_STRING, description='Current subscription plan'),
                        'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Subscription expiry date')
                    }
                )
            ),
            401: 'Authentication required'
        }
    )
    def get(self, request):
        user = request.user
        current_subscription = user.current_subscription

        response_data = {
            'is_active': False,
            'plan': None,
            'features': {
                'social_accounts_limit': 0,
                'ai_caption_limit': 0,
                'has_analytics': False,
                'has_advanced_analytics': False,
                'has_content_calendar': False,
                'has_team_collaboration': False,
                'has_competitor_analysis': False,
                'has_api_access': False,
                'has_dedicated_support': False,
            },
            'expires_at': None
        }

        if current_subscription and current_subscription.is_active():
            plan = current_subscription.plan
            response_data.update({
                'is_active': True,
                'plan': plan.name,
                'features': {
                    'social_accounts_limit': plan.social_accounts_limit,
                    'ai_caption_limit': plan.ai_caption_limit,
                    'has_analytics': plan.has_analytics,
                    'has_advanced_analytics': plan.has_advanced_analytics,
                    'has_content_calendar': plan.has_content_calendar,
                    'has_team_collaboration': plan.has_team_collaboration,
                    'has_competitor_analysis': plan.has_competitor_analysis,
                    'has_api_access': plan.has_api_access,
                    'has_dedicated_support': plan.has_dedicated_support,
                },
                'expires_at': current_subscription.expires_at
            })

        return Response(response_data)

@swagger_auto_schema(
    method='get',
    operation_description="Get list of available subscription plans",
    responses={
        200: openapi.Response(
            description="Available plans retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Plan ID'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Plan name'),
                        'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Monthly price in USD'),
                        'features': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description='List of features included in the plan'
                        )
                    }
                )
            )
        )
    }
)
@api_view(['GET'])
def available_plans(request):
    """Get all available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).exclude(name='FREE_TRIAL')
    
    return Response([{
        'id': plan.id,
        'name': plan.name,
        'price': float(plan.price),
        'social_accounts_limit': plan.social_accounts_limit,
        'ai_caption_limit': plan.ai_caption_limit,
        'features': {
            'analytics': plan.has_analytics,
            'advanced_analytics': plan.has_advanced_analytics,
            'content_calendar': plan.has_content_calendar,
            'team_collaboration': plan.has_team_collaboration,
            'competitor_analysis': plan.has_competitor_analysis,
            'api_access': plan.has_api_access,
            'dedicated_support': plan.has_dedicated_support,
        }
    } for plan in plans])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stripe_config(request):
    """
    Safely expose the publishable key to the frontend
    """
    return Response({
        'publishableKey': get_stripe_public_key()
    }) 



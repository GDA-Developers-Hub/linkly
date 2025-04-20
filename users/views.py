from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.urls import reverse
from datetime import datetime, timedelta, timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes, action
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
from .models import SubscriptionPlan, Subscription
from .utils import get_stripe_instance, get_stripe_public_key
from .oauth_utils import (
    get_google_auth_url,
    get_facebook_auth_url,
    get_linkedin_auth_url,
    get_twitter_auth_url,
    get_instagram_auth_url,
    get_tiktok_auth_url,
    get_telegram_auth_url,
    verify_telegram_hash
)
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer,
    Enable2FASerializer,
    Verify2FASerializer,
    SocialConnectionSerializer,
    SocialAccountSerializer
)
from .services.oauth import (
    get_google_oauth_url, get_facebook_oauth_url,
    get_linkedin_oauth_url, get_twitter_oauth_url,
    get_instagram_oauth_url, get_tiktok_oauth_url,
    get_telegram_oauth_url
)
from .services.social import (
    connect_google_account, connect_facebook_account,
    connect_linkedin_account, connect_twitter_account,
    connect_instagram_account, connect_tiktok_account,
    connect_telegram_account
)
from django.core.cache import cache
import secrets

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
    Custom token view that returns JWT token pair.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Login User",
        operation_description="""
        Authenticate user and obtain JWT token pair.
        
        Features:
        - JWT token pair generation
        - 2FA verification if enabled
        - Token refresh capability
        - Access token expiry: 1 hour
        - Refresh token expiry: 24 hours
        
        Returns both access and refresh tokens for API authentication.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='email',
                    description='User email address'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='password',
                    description='User password'
                ),
                'two_factor_code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='2FA code if enabled'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='JWT access token'
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='JWT refresh token'
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='User profile information'
                        )
                    }
                )
            ),
            400: 'Invalid credentials',
            401: '2FA code required',
            403: 'Account inactive'
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class Enable2FAView(generics.GenericAPIView):
    """
    Enable Two-Factor Authentication for user account.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = Enable2FASerializer

    @swagger_auto_schema(
        operation_summary="Enable 2FA",
        operation_description="""
        Enable Two-Factor Authentication for the user account.
        
        Features:
        - TOTP-based 2FA
        - QR code generation
        - Backup codes generation
        - Compatible with Google Authenticator
        
        Returns:
        - QR code for scanning
        - Secret key for manual entry
        - One-time backup codes
        
        Store the backup codes securely - they won't be shown again.
        """,
        responses={
            200: openapi.Response(
                description="2FA enabled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'qr_code': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='QR code data URL'
                        ),
                        'secret': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='TOTP secret key'
                        ),
                        'backup_codes': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            description='One-time backup codes'
                        )
                    }
                )
            ),
            401: 'Authentication required',
            409: '2FA already enabled'
        },
        tags=['Authentication']
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
        operation_summary="Verify 2FA Code",
        operation_description="""
        Verify 2FA code and complete authentication.
        
        Accepts:
        - TOTP code from authenticator app
        - One-time backup code
        
        Returns JWT tokens upon successful verification.
        Invalid attempts are rate limited.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='6-digit TOTP code or backup code'
                ),
                'remember_device': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='Remember device for 30 days'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="2FA verification successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='JWT access token'
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='JWT refresh token'
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='User profile information'
                        )
                    }
                )
            ),
            400: 'Invalid 2FA code',
            429: 'Too many attempts'
        },
        tags=['Authentication']
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
        operation_summary="Validate Token",
        operation_description="""
        Validate JWT token and return user information.
        
        Features:
        - Token validation
        - Token expiry check
        - User status check
        - Profile information return
        
        Use this endpoint to verify token validity and get user data.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token'],
            properties={
                'token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='JWT access token to validate'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Token is valid",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valid': openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description='Token validity status'
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='User profile information'
                        )
                    }
                )
            ),
            401: 'Token is invalid or expired'
        },
        tags=['Authentication']
    )
    def post(self, request):
        token = request.data.get('token')
        try:
            user = User.objects.get(access_token_jwt=token)
            if user.token_created_at and (datetime.now() - user.token_created_at).days < 1:
                return Response({
                    'valid': True,
                    'user': UserSerializer(user).data
                })
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='post',
    operation_summary="Register New User",
    operation_description="""
    Register a new user account.
    
    Features:
    - Email verification
    - Automatic free trial activation
    - Optional business account setup
    
    A verification email will be sent to complete registration.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password', 'username'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'is_business': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'company_name': openapi.Schema(type=openapi.TYPE_STRING),
            'business_description': openapi.Schema(type=openapi.TYPE_STRING),
            'website': openapi.Schema(type=openapi.TYPE_STRING, format='uri'),
            'industry': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        201: openapi.Response(
            description="User registered successfully",
            schema=UserSerializer
        ),
        400: 'Invalid registration data',
        409: 'Email already registered'
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_summary="Initialize Social OAuth",
    operation_description="""
    Initialize OAuth flow for social media platform connection.
    
    Supported Platforms:
    - Google
    - Facebook
    - LinkedIn
    - Twitter
    - Instagram
    - TikTok
    - Telegram
    
    Returns an authorization URL for the specified platform.
    Business account connection requires additional scopes.
    """,
    manual_parameters=[
        openapi.Parameter(
            'platform',
            openapi.IN_QUERY,
            description="Social media platform",
            type=openapi.TYPE_STRING,
            enum=['google', 'facebook', 'linkedin', 'twitter', 'instagram', 'tiktok', 'telegram'],
            required=True
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
            description="OAuth redirect URI",
            type=openapi.TYPE_STRING,
            format='uri'
        )
    ],
    responses={
        200: openapi.Response(
            description="OAuth URL generated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'auth_url': openapi.Schema(type=openapi.TYPE_STRING, format='uri')
                }
            )
        ),
        400: 'Invalid platform or parameters',
        403: 'Insufficient subscription plan'
    },
    tags=['Social Integration']
)
def init_oauth(request):
    """Initialize OAuth flow for social media platforms"""
    # Debug logging
    print(f"Auth header: {request.headers.get('Authorization', 'No Auth header')}")
    print(f"User authenticated: {request.user.is_authenticated}")
    
    platform = request.GET.get('platform')
    redirect_uri = request.GET.get('redirect_uri')
    
    if not platform or not redirect_uri:
        return Response({
            'error': 'Platform and redirect_uri are required',
            'platform': platform,
            'redirect_uri': redirect_uri
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not request.user.is_authenticated:
        return Response({
            'error': 'Authentication required',
            'detail': 'Please provide a valid JWT token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get the appropriate OAuth URL based on platform
        if platform == 'facebook':
            auth_url = get_facebook_auth_url(redirect_uri)
        elif platform == 'google':
            auth_url = get_google_auth_url()
        elif platform == 'linkedin':
            auth_url = get_linkedin_auth_url()
        elif platform == 'twitter':
            auth_url, request_token = get_twitter_auth_url()
        elif platform == 'instagram':
            auth_url = get_instagram_auth_url()
        elif platform == 'tiktok':
            auth_url = get_tiktok_auth_url()
        elif platform == 'telegram':
            auth_url = get_telegram_auth_url()
        else:
            return Response({
                'error': 'Invalid platform',
                'platform': platform,
                'supported_platforms': ['facebook', 'google', 'linkedin', 'twitter', 'instagram', 'tiktok', 'telegram']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Store OAuth state in Redis with user ID
        state = auth_url.split('state=')[-1].split('&')[0] if 'state=' in auth_url else None
        if state:
            cache.set(
                f'oauth_state_{state}',
                {
                    'user_id': request.user.id,
                    'platform': platform,
                    'redirect_uri': redirect_uri
                },
                timeout=3600  # 1 hour expiry
            )
            
            # Debug logging
            print(f"Stored state in cache: {state}")
            print(f"User ID: {request.user.id}")
            print(f"Platform: {platform}")
            print(f"Redirect URI: {redirect_uri}")
        
        return Response({
            'auth_url': auth_url,
            'state': state  # Include state in response for debugging
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'detail': 'An error occurred during OAuth initialization'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Social Account",
    operation_description="""
    Connect a social media account using OAuth token.
    
    Features:
    - Automatic token refresh setup
    - Profile information sync
    - Business account detection
    - Analytics integration
    
    Token expiry and refresh schedules are handled automatically.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['platform', 'access_token'],
        properties={
            'platform': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['google', 'facebook', 'linkedin', 'twitter', 'instagram', 'tiktok', 'telegram']
            ),
            'access_token': openapi.Schema(type=openapi.TYPE_STRING),
            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
            'expires_in': openapi.Schema(type=openapi.TYPE_INTEGER),
            'business': openapi.Schema(type=openapi.TYPE_BOOLEAN)
        }
    ),
    responses={
        200: openapi.Response(
            description="Account connected successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'platform': openapi.Schema(type=openapi.TYPE_STRING),
                    'account_type': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        enum=['personal', 'business']
                    ),
                    'profile': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: 'Invalid token or platform',
        401: 'Authentication required',
        402: 'Subscription plan limit reached',
        409: 'Account already connected'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_social_account(request):
    """Connect a social media account"""
    platform = request.data.get('platform')
    access_token = request.data.get('access_token')
    refresh_token = request.data.get('refresh_token')
    expires_in = request.data.get('expires_in')
    business = request.data.get('business', False)
    
    if not platform or not access_token:
        return Response({
            'error': 'Missing required parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = request.user
        
        # Check subscription limits
        connected_accounts = user.get_connected_accounts_count()
        subscription = user.current_subscription
        
        if subscription and connected_accounts >= subscription.plan.social_accounts_limit:
            return Response({
                'error': 'Social accounts limit reached for your subscription plan'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        # Connect account based on platform
        if platform == 'facebook':
            result = user.connect_facebook(access_token, business)
        elif platform == 'instagram':
            result = user.connect_instagram(access_token, business)
        elif platform == 'twitter':
            result = user.connect_twitter(access_token, business)
        elif platform == 'linkedin':
            result = user.connect_linkedin(access_token, business)
        elif platform == 'tiktok':
            result = user.connect_tiktok(access_token, business)
        elif platform == 'telegram':
            result = user.connect_telegram(access_token)
        else:
            return Response({
                'error': 'Invalid platform'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Create Subscription Checkout",
    operation_description="""
    Create a Stripe checkout session for subscription purchase.
    
    Features:
    - Secure payment processing
    - Automatic trial conversion
    - Proration handling
    - Coupon support
    
    The session URL will redirect to Stripe's hosted checkout page.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['plan_id'],
        properties={
            'plan_id': openapi.Schema(type=openapi.TYPE_STRING),
            'coupon': openapi.Schema(type=openapi.TYPE_STRING),
            'success_url': openapi.Schema(type=openapi.TYPE_STRING, format='uri'),
            'cancel_url': openapi.Schema(type=openapi.TYPE_STRING, format='uri')
        }
    ),
    responses={
        200: openapi.Response(
            description="Checkout session created",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'session_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'url': openapi.Schema(type=openapi.TYPE_STRING, format='uri')
                }
            )
        ),
        400: 'Invalid plan or parameters',
        401: 'Authentication required',
        402: 'Payment required'
    },
    tags=['Subscriptions']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create a subscription checkout session"""
    try:
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                'error': 'Plan ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        plan = SubscriptionPlan.objects.get(id=plan_id)
        stripe = get_stripe_instance()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.data.get('success_url', 'https://linkly.com/success'),
            cancel_url=request.data.get('cancel_url', 'https://linkly.com/cancel'),
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id
            }
        )
        
        return Response({
            'session_id': session.id,
            'url': session.url
        })
        
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'Invalid plan ID'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="Get Connected Accounts",
    operation_description="""
    Get list of all connected social media accounts.
    
    Returns:
    - Connected platforms
    - Account types (personal/business)
    - Profile information
    - Analytics access status
    - Last sync timestamps
    """,
    responses={
        200: openapi.Response(
            description="Connected accounts retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'accounts': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'platform': openapi.Schema(type=openapi.TYPE_STRING),
                                'account_type': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    enum=['personal', 'business']
                                ),
                                'profile': openapi.Schema(type=openapi.TYPE_OBJECT),
                                'analytics_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'last_synced': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                            }
                        )
                    ),
                    'total_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'limit': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        ),
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_connected_accounts(request):
    """Get all connected social media accounts"""
    user = request.user
    subscription = user.current_subscription
    
    accounts = []
    
    # Facebook
    if user.facebook_id:
        accounts.append({
            'platform': 'facebook',
            'account_type': 'business' if user.has_facebook_business else 'personal',
            'profile': {
                'id': user.facebook_id,
                'name': user.facebook_page_name if user.has_facebook_business else None,
                'followers': user.facebook_page_followers if user.has_facebook_business else None
            },
            'analytics_enabled': user.has_facebook_business and subscription and subscription.plan.has_analytics,
            'last_synced': user.last_sync.get('facebook')
        })
    
    # Instagram
    if user.instagram_id:
        accounts.append({
            'platform': 'instagram',
            'account_type': 'business' if user.has_instagram_business else 'personal',
            'profile': {
                'id': user.instagram_id,
                'username': user.instagram_handle,
                'business_name': user.instagram_business_name if user.has_instagram_business else None,
                'followers': user.instagram_business_followers if user.has_instagram_business else None
            },
            'analytics_enabled': user.has_instagram_business and subscription and subscription.plan.has_analytics,
            'last_synced': user.last_sync.get('instagram')
        })
    
    # Add other platforms...
    
    return Response({
        'accounts': accounts,
        'total_count': len(accounts),
        'limit': subscription.plan.social_accounts_limit if subscription else 0
    })

class SubscriptionStatusView(APIView):
    """
    View to retrieve subscription status for the current user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Subscription Status",
        operation_description="""
        Get current user's subscription status including:
        - Current plan details
        - Trial status
        - Days remaining
        - Features access
        - Usage limits
        """,
        responses={
            200: openapi.Response(
                description="Subscription status retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=['ACTIVE', 'EXPIRED', 'CANCELLED', 'TRIAL', 'PENDING']
                        ),
                        'plan': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'features': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'analytics': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'advanced_analytics': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'content_calendar': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'team_collaboration': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'competitor_analysis': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'api_access': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'dedicated_support': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                    }
                                ),
                                'limits': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'social_accounts': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'ai_captions': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'team_members': openapi.Schema(type=openapi.TYPE_INTEGER)
                                    }
                                )
                            }
                        ),
                        'is_trial': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'days_remaining': openapi.Schema(type=openapi.TYPE_STRING),
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'auto_renew': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            401: 'Authentication credentials not provided'
        },
        tags=['Subscriptions']
    )
    def get(self, request):
        """Get subscription status for current user"""
        user = request.user
        subscription = user.current_subscription

        if not subscription:
            return Response({
                'status': 'NONE',
                'plan': None,
                'is_trial': False,
                'days_remaining': '0',
                'start_date': None,
                'end_date': None,
                'auto_renew': False
            })

        plan = subscription.plan
        return Response({
            'status': subscription.status,
            'plan': {
                'name': plan.get_name_display(),
                'price': float(plan.price),
                'features': {
                    'analytics': plan.has_analytics,
                    'advanced_analytics': plan.has_advanced_analytics,
                    'content_calendar': plan.has_content_calendar,
                    'team_collaboration': plan.has_team_collaboration,
                    'competitor_analysis': plan.has_competitor_analysis,
                    'api_access': plan.has_api_access,
                    'dedicated_support': plan.has_dedicated_support
                },
                'limits': {
                    'social_accounts': plan.social_accounts_limit,
                    'ai_captions': plan.ai_caption_limit,
                    'team_members': plan.team_member_limit
                }
            },
            'is_trial': subscription.is_trial,
            'days_remaining': subscription.days_remaining(),
            'start_date': subscription.start_date,
            'end_date': subscription.end_date,
            'auto_renew': subscription.auto_renew
        })

@swagger_auto_schema(
    method='get',
    operation_summary="Google OAuth Callback",
    operation_description="""
    Handle Google OAuth callback and connect account.
    
    Exchanges authorization code for access token and connects the Google account.
    """,
    manual_parameters=[
        openapi.Parameter(
            'code',
            openapi.IN_QUERY,
            description="Authorization code from Google",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'state',
            openapi.IN_QUERY,
            description="State parameter for security verification",
            type=openapi.TYPE_STRING,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="Account connected successfully",
            schema=SocialConnectionSerializer
        ),
        400: 'Invalid authorization code',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_auth_callback(request):
    """Handle Google OAuth callback"""
    code = request.query_params.get('code')
    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = connect_google_account(request.user, code)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@swagger_auto_schema(
    method='get',
    operation_summary="Facebook OAuth Callback",
    operation_description="""
    Handle Facebook OAuth callback and connect account.
    
    Exchanges authorization code for access token and connects the Facebook account.
    """,
    manual_parameters=[
        openapi.Parameter(
            'code',
            openapi.IN_QUERY,
            description="Authorization code from Facebook",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'state',
            openapi.IN_QUERY,
            description="State parameter for security verification",
            type=openapi.TYPE_STRING,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="Account connected successfully",
            schema=SocialConnectionSerializer
        ),
        400: 'Invalid authorization code',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def facebook_auth_callback(request):
    """Handle Facebook OAuth callback"""
    code = request.query_params.get('code')
    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = connect_facebook_account(request.user, code)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@swagger_auto_schema(
    method='get',
    operation_summary="LinkedIn OAuth Callback",
    operation_description="""
    Handle LinkedIn OAuth callback and connect account.
    
    Exchanges authorization code for access token and connects the LinkedIn account.
    """,
    manual_parameters=[
        openapi.Parameter(
            'code',
            openapi.IN_QUERY,
            description="Authorization code from LinkedIn",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'state',
            openapi.IN_QUERY,
            description="State parameter for security verification",
            type=openapi.TYPE_STRING,
            required=False
        )
    ],
    responses={
        200: openapi.Response(
            description="Account connected successfully",
            schema=SocialConnectionSerializer
        ),
        400: 'Invalid authorization code',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def linkedin_auth_callback(request):
    """Handle LinkedIn OAuth callback"""
    code = request.query_params.get('code')
    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = connect_linkedin_account(request.user, code)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@swagger_auto_schema(
    method='post',
    operation_summary="Unlink Social Account",
    operation_description="""
    Unlink a connected social media account.
    
    Removes the connection and associated tokens for the specified platform.
    """,
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
        401: 'Authentication required',
        404: 'Account not connected'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlink_social_account(request, platform):
    """Unlink a social media account"""
    user = request.user
    
    if platform == 'facebook':
        user.facebook_id = None
        user.facebook_access_token = None
        user.has_facebook_business = False
    elif platform == 'instagram':
        user.instagram_id = None
        user.instagram_access_token = None
        user.has_instagram_business = False
    elif platform == 'twitter':
        user.twitter_id = None
        user.twitter_access_token = None
        user.twitter_access_secret = None
    elif platform == 'linkedin':
        user.linkedin_id = None
        user.linkedin_access_token = None
        user.has_linkedin_company = False
    elif platform == 'tiktok':
        user.tiktok_id = None
        user.tiktok_access_token = None
        user.has_tiktok_business = False
    elif platform == 'telegram':
        user.telegram_id = None
        user.telegram_username = None
        user.has_telegram_channel = False
    else:
        return Response(
            {'error': 'Invalid platform'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.save()
    return Response({
        'success': True,
        'message': f'{platform.title()} account unlinked successfully'
    })

@swagger_auto_schema(
    method='post',
    operation_summary="Connect YouTube Account",
    operation_description="Connect a YouTube account using OAuth token",
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_youtube(request):
    """Connect YouTube account"""
    try:
        result = request.user.connect_youtube(request.data.get('access_token'))
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Facebook Account",
    operation_description="Connect a Facebook account using OAuth token",
    responses={
        200: SocialAccountSerializer,
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
    operation_summary="Connect Telegram Account",
    operation_description="Connect a Telegram account using Bot API token",
    responses={
        200: SocialAccountSerializer,
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

@swagger_auto_schema(
    method='post',
    operation_summary="Connect Instagram Account",
    operation_description="Connect an Instagram account using OAuth token",
    responses={
        200: SocialAccountSerializer,
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
    operation_summary="Connect Twitter Account",
    operation_description="Connect a Twitter account using OAuth token",
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid token',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_twitter(request):
    """Connect Twitter account"""
    try:
        result = request.user.connect_twitter(
            request.data.get('access_token'),
            request.data.get('access_token_secret')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect TikTok Account",
    operation_description="Connect a TikTok account using OAuth token",
    responses={
        200: SocialAccountSerializer,
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
    operation_summary="Connect Facebook Page",
    operation_description="Connect a Facebook business page",
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid page ID or access',
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
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid account ID or access',
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
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid company ID or access',
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
    operation_summary="Connect YouTube Brand",
    operation_description="Connect a YouTube brand account",
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid brand account or access',
        401: 'Authentication required'
    },
    tags=['Social Integration']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_youtube_brand(request):
    """Connect YouTube brand account"""
    try:
        result = request.user.connect_youtube_brand(
            request.data.get('brand_id'),
            request.data.get('access_token')
        )
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Connect TikTok Business",
    operation_description="Connect a TikTok business account",
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid account or access',
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
    responses={
        200: SocialAccountSerializer,
        400: 'Invalid channel or access',
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

@csrf_exempt
@api_view(['POST'])
@swagger_auto_schema(
    operation_summary="Stripe Webhook Handler",
    operation_description="""
    Handle Stripe webhook events for subscription management.
    
    Events handled:
    - checkout.session.completed
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.paid
    - invoice.payment_failed
    
    Updates subscription status and user access based on webhook events.
    """,
    responses={
        200: openapi.Response(
            description="Webhook processed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Invalid webhook data',
        401: 'Invalid signature'
    },
    tags=['Subscriptions']
)
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event.type == 'checkout.session.completed':
            session = event.data.object
            handle_checkout_session(session)
            
        elif event.type == 'customer.subscription.updated':
            subscription = event.data.object
            handle_subscription_updated(subscription)
            
        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            handle_subscription_deleted(subscription)
            
        elif event.type == 'invoice.paid':
            invoice = event.data.object
            handle_invoice_paid(invoice)
            
        elif event.type == 'invoice.payment_failed':
            invoice = event.data.object
            handle_invoice_failed(invoice)
            
        return JsonResponse({'status': 'success'})
        
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def handle_checkout_session(session):
    """Handle successful checkout session completion"""
    user_id = session.metadata.get('user_id')
    plan_id = session.metadata.get('plan_id')
    
    try:
        user = User.objects.get(id=user_id)
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Create or update subscription
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=session.subscription,
            status='ACTIVE',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            auto_renew=True
        )
        
        # Update user's stripe customer ID if not set
        if not user.stripe_customer_id:
            user.stripe_customer_id = session.customer
            user.save()
            
    except (User.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
        # Log error for investigation
        print(f"Error processing checkout session: {str(e)}")

def handle_subscription_updated(stripe_subscription):
    """Handle subscription update events"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_subscription.id
        )
        
        # Update subscription status
        subscription.status = stripe_subscription.status.upper()
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end
        )
        subscription.save()
        
    except Subscription.DoesNotExist:
        # Log error for investigation
        print(f"Subscription not found: {stripe_subscription.id}")

def handle_subscription_deleted(stripe_subscription):
    """Handle subscription deletion events"""
    try:
        subscription = Subscription.objects.get(
            stripe_subscription_id=stripe_subscription.id
        )
        
        # Mark subscription as cancelled
        subscription.status = 'CANCELLED'
        subscription.auto_renew = False
        subscription.save()
        
    except Subscription.DoesNotExist:
        # Log error for investigation
        print(f"Subscription not found: {stripe_subscription.id}")

def handle_invoice_paid(invoice):
    """Handle successful invoice payment"""
    subscription_id = invoice.subscription
    if subscription_id:
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            
            # Update subscription status and dates
            subscription.status = 'ACTIVE'
            subscription.start_date = datetime.fromtimestamp(
                invoice.period_start
            )
            subscription.end_date = datetime.fromtimestamp(
                invoice.period_end
            )
            subscription.save()
            
        except Subscription.DoesNotExist:
            # Log error for investigation
            print(f"Subscription not found: {subscription_id}")

def handle_invoice_failed(invoice):
    """Handle failed invoice payment"""
    subscription_id = invoice.subscription
    if subscription_id:
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            
            # Mark subscription as past due
            subscription.status = 'PAST_DUE'
            subscription.save()
            
            # Notify user of payment failure
            send_payment_failed_notification(subscription.user, invoice)
            
        except Subscription.DoesNotExist:
            # Log error for investigation
            print(f"Subscription not found: {subscription_id}")

def send_payment_failed_notification(user, invoice):
    """Send payment failure notification email"""
    try:
        send_mail(
            subject='Payment Failed - Action Required',
            message=f"""
            Dear {user.get_full_name()},
            
            Your payment for the subscription renewal has failed. Please update your payment method to avoid service interruption.
            
            Amount due: ${invoice.amount_due / 100:.2f}
            Due date: {datetime.fromtimestamp(invoice.due_date).strftime('%Y-%m-%d')}
            
            To update your payment method, please visit:
            {settings.FRONTEND_URL}/billing/update
            
            If you need assistance, please contact our support team.
            
            Best regards,
            Linkly Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
    except Exception as e:
        # Log error for investigation
        print(f"Error sending payment failed notification: {str(e)}")

@swagger_auto_schema(
    method='get',
    operation_summary="Get Available Plans",
    operation_description="""
    Get list of available subscription plans.
    
    Returns:
    - Plan details
    - Features included
    - Usage limits
    - Pricing information
    - Trial availability
    """,
    responses={
        200: openapi.Response(
            description="Plans retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'interval': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=['month', 'year']
                        ),
                        'features': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'analytics': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'advanced_analytics': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'content_calendar': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'team_collaboration': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'competitor_analysis': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'api_access': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'dedicated_support': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                            }
                        ),
                        'limits': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'social_accounts': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'ai_captions': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'team_members': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'trial_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'popular': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            )
        )
    },
    tags=['Subscriptions']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def available_plans(request):
    """Get list of available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            'id': str(plan.id),
            'name': plan.get_name_display(),
            'description': plan.description,
            'price': float(plan.price),
            'interval': plan.billing_interval,
            'features': {
                'analytics': plan.has_analytics,
                'advanced_analytics': plan.has_advanced_analytics,
                'content_calendar': plan.has_content_calendar,
                'team_collaboration': plan.has_team_collaboration,
                'competitor_analysis': plan.has_competitor_analysis,
                'api_access': plan.has_api_access,
                'dedicated_support': plan.has_dedicated_support
            },
            'limits': {
                'social_accounts': plan.social_accounts_limit,
                'ai_captions': plan.ai_caption_limit,
                'team_members': plan.team_member_limit
            },
            'trial_days': plan.trial_days,
            'popular': plan.is_popular,
            'stripe_price_id': plan.stripe_price_id
        })
    
    return Response(plans_data)



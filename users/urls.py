from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ChangePasswordView,
    UpdateProfileView,
    UserProfileView,
    Enable2FAView,
    Verify2FAView,
    ValidateTokenView,
    google_auth_callback,
    facebook_auth_callback,
    linkedin_auth_callback,
    unlink_social_account,
    connect_youtube,
    connect_facebook,
    connect_telegram,
    connect_instagram,
    connect_twitter,
    connect_tiktok,
    connect_facebook_page,
    connect_instagram_business,
    connect_linkedin_company,
    connect_youtube_brand,
    connect_tiktok_business,
    connect_telegram_channel,
    get_connected_accounts,
    create_checkout_session,
    stripe_webhook,
    SubscriptionStatusView,
    available_plans,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 2FA endpoints
    path('2fa/enable/', Enable2FAView.as_view(), name='enable_2fa'),
    path('2fa/verify/', Verify2FAView.as_view(), name='verify_2fa'),
    
    # Token validation for Node.js
    path('token/validate/', ValidateTokenView.as_view(), name='validate_token'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    
    # Social Authentication URLs
    path('auth/google/callback/', google_auth_callback, name='google-auth-callback'),
    path('auth/facebook/callback/', facebook_auth_callback, name='facebook-auth-callback'),
    path('auth/linkedin/callback/', linkedin_auth_callback, name='linkedin-auth-callback'),
    path('auth/unlink/<str:platform>/', unlink_social_account, name='unlink-social-account'),
    
    # Connect Social Accounts
    path('connect/youtube/', connect_youtube, name='connect-youtube'),
    path('connect/facebook/', connect_facebook, name='connect-facebook'),
    path('connect/telegram/', connect_telegram, name='connect-telegram'),
    path('connect/instagram/', connect_instagram, name='connect-instagram'),
    path('connect/twitter/', connect_twitter, name='connect-twitter'),
    path('connect/tiktok/', connect_tiktok, name='connect-tiktok'),
    
    # Connect Business Accounts
    path('connect/facebook-page/', connect_facebook_page, name='connect-facebook-page'),
    path('connect/instagram-business/', connect_instagram_business, name='connect-instagram-business'),
    path('connect/linkedin-company/', connect_linkedin_company, name='connect-linkedin-company'),
    path('connect/youtube-brand/', connect_youtube_brand, name='connect-youtube-brand'),
    path('connect/tiktok-business/', connect_tiktok_business, name='connect-tiktok-business'),
    path('connect/telegram-channel/', connect_telegram_channel, name='connect-telegram-channel'),
    
    path('connected-accounts/', get_connected_accounts, name='connected-accounts'),
    
    # Subscription URLs
    path('subscriptions/checkout/', create_checkout_session, name='create-checkout-session'),
    path('subscriptions/webhook/', stripe_webhook, name='stripe-webhook'),
    path('subscriptions/status/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('subscriptions/plans/', available_plans, name='available-plans'),
] 
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
    init_oauth,
    oauth_callback,
    google_callback,
    facebook_callback,
    linkedin_callback,
    twitter_callback,
    instagram_callback,
    tiktok_callback,
    telegram_callback,
    unlink_social_account,
    SubscriptionStatusView,
    available_plans,
    create_checkout_session,
    connect_google,
    connect_facebook,
    connect_linkedin,
    connect_twitter,
    connect_instagram,
    connect_tiktok,
    connect_telegram,
    connect_facebook_page,
    connect_instagram_business,
    connect_linkedin_company,
    connect_tiktok_business,
    connect_telegram_channel,
    get_connected_accounts
)

# OAuth URLs
urlpatterns = [
    # OAuth initialization
    path('auth/init/', init_oauth, name='oauth-init'),
    
    # Generic OAuth callback
    path('auth/callback/<str:platform>/', oauth_callback, name='oauth-callback'),
    
    # Platform-specific callbacks
    path('auth/callback/google/', google_callback, name='google-callback'),
    path('auth/callback/facebook/', facebook_callback, name='facebook-callback'),
    path('auth/callback/linkedin/', linkedin_callback, name='linkedin-callback'),
    path('auth/callback/twitter/', twitter_callback, name='twitter-callback'),
    path('auth/callback/instagram/', instagram_callback, name='instagram-callback'),
    path('auth/callback/tiktok/', tiktok_callback, name='tiktok-callback'),
    path('auth/callback/telegram/', telegram_callback, name='telegram-callback'),
    
    # Connected accounts endpoint
    path('accounts/', get_connected_accounts, name='connected-accounts'),
    
    # Connect endpoints for personal accounts
    path('connect/google/', connect_google, name='connect-google'),
    path('connect/facebook/', connect_facebook, name='connect-facebook'),
    path('connect/linkedin/', connect_linkedin, name='connect-linkedin'),
    path('connect/twitter/', connect_twitter, name='connect-twitter'),
    path('connect/instagram/', connect_instagram, name='connect-instagram'),
    path('connect/tiktok/', connect_tiktok, name='connect-tiktok'),
    path('connect/telegram/', connect_telegram, name='connect-telegram'),
    
    # Connect endpoints for business accounts
    path('connect/facebook/page/', connect_facebook_page, name='connect-facebook-page'),
    path('connect/instagram/business/', connect_instagram_business, name='connect-instagram-business'),
    path('connect/linkedin/company/', connect_linkedin_company, name='connect-linkedin-company'),
    path('connect/tiktok/business/', connect_tiktok_business, name='connect-tiktok-business'),
    path('connect/telegram/channel/', connect_telegram_channel, name='connect-telegram-channel'),
    
    # Unlink social account
    path('auth/unlink/<str:platform>/', unlink_social_account, name='unlink-social'),
]

# Authentication URL patterns
auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('validate/', ValidateTokenView.as_view(), name='validate-token'),
    path('2fa/enable/', Enable2FAView.as_view(), name='enable-2fa'),
    path('2fa/verify/', Verify2FAView.as_view(), name='verify-2fa'),
]

# User management URL patterns
user_urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('password/change/', ChangePasswordView.as_view(), name='change-password'),
]

# Subscription URL patterns
subscription_urlpatterns = [
    path('subscription/status/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('subscription/plans/', available_plans, name='available-plans'),
    path('subscription/checkout/', create_checkout_session, name='create-checkout-session'),
]

# Combine all URL patterns
urlpatterns = auth_urlpatterns + user_urlpatterns + urlpatterns + subscription_urlpatterns

# URL pattern documentation
"""
OAuth Flow Documentation:

1. Google OAuth2 Flow:
   - Initialize: GET /auth/init/?platform=google
   - Callback: GET /auth/callback/google/?code={code}&state={state}&session_key={session_key}
   - Scopes: email, profile, youtube (for business)
   - PKCE: Required
   - State: Required
   - Business Features: YouTube channel access

2. Facebook OAuth2 Flow:
   - Initialize: GET /auth/init/?platform=facebook
   - Callback: GET /auth/callback/facebook/?code={code}&state={state}&session_key={session_key}
   - Scopes: email, public_profile, pages (for business)
   - State: Required
   - Business Features: Page management, Instagram Business

3. LinkedIn OAuth2 Flow:
   - Initialize: GET /auth/init/?platform=linkedin
   - Callback: GET /auth/callback/linkedin/?code={code}&state={state}&session_key={session_key}
   - Scopes: r_liteprofile, r_emailaddress, w_organization_social (for business)
   - PKCE: Required
   - State: Required
   - Business Features: Company page management

4. Twitter OAuth2 Flow:
   - Initialize: GET /auth/init/?platform=twitter
   - Callback: GET /auth/callback/twitter/?code={code}&state={state}&session_key={session_key}
   - Scopes: tweet.read, users.read, offline.access, tweet.write (for business)
   - PKCE: Required
   - State: Required
   - Business Features: Tweet management

5. Instagram OAuth2 Flow:
   - Initialize: GET /auth/init/?platform=instagram
   - Callback: GET /auth/callback/instagram/?code={code}&state={state}&session_key={session_key}
   - Scopes: basic, public_content
   - State: Required
   - Business Features: Via Facebook Business integration

6. TikTok OAuth2 Flow:
   - Initialize: GET /auth/init/?platform=tiktok
   - Callback: GET /auth/callback/tiktok/?code={code}&state={state}&session_key={session_key}
   - Scopes: user.info.basic, video.list (for business)
   - PKCE: Required
   - State: Required
   - Business Features: Video management

7. Telegram Auth Flow:
   - Initialize: GET /auth/init/?platform=telegram
   - Callback: GET /auth/callback/telegram/?code={code}&state={state}&session_key={session_key}
   - Authentication: Bot API based
   - State: Required
   - Business Features: Channel management

Common Parameters:
- platform: The social platform to connect with
- business: Boolean flag for business account access
- redirect_uri: Optional custom redirect URI
- session_key: Key for retrieving stored PKCE and state data
- state: Security parameter to prevent CSRF
- code: Authorization code from OAuth provider

Security Features:
1. PKCE (Proof Key for Code Exchange):
   - Implemented for: Google, LinkedIn, Twitter, TikTok
   - Prevents authorization code interception
   - Required for public clients

2. State Parameter:
   - Required for all platforms
   - Prevents CSRF attacks
   - Validated on callback

3. Session Management:
   - PKCE and state stored in Redis cache
   - Short expiration time (5 minutes)
   - Cleaned up after successful connection

4. Business Account Verification:
   - Additional scope verification
   - Platform-specific business feature checks
   - Rate limits and quota management

Error Handling:
- TokenExchangeError: Failed to exchange authorization code
- StateVerificationError: Invalid or expired state
- PKCEVerificationError: Invalid or expired PKCE data
- ProfileFetchError: Failed to fetch user profile
- BusinessAccountError: Business account connection issues

Rate Limiting:
- OAuth initialization: 10 requests per minute
- Callbacks: 5 requests per minute
- Business features: Based on subscription plan

Cache Keys:
- OAuth session: oauth_{platform}_{random_string}
- PKCE data: pkce_{platform}_{session_id}
- State: state_{platform}_{session_id}

Subscription Requirements:
- Free: Basic social account connection
- Pro: Business account features
- Enterprise: Advanced analytics and automation
""" 
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views
from . import allauth_views

app_name = 'social_platforms'

# Create a router for API viewsets
router = DefaultRouter()
router.register(r'platforms', views.SocialPlatformViewSet)
router.register(r'accounts', views.UserSocialAccountViewSet, basename='account')

urlpatterns = [
    # API Endpoints (original views)
    path('api/', include(router.urls)),
    path('api/posts/', views.SocialAccountPostView.as_view(), name='posts'),
    
    # AllAuth integration API endpoints (existing)
    path('api/oauth/init/<str:platform>/', api_views.OAuthInitAPIView.as_view(), name='oauth_init_allauth'),
    path('api/oauth/complete/<str:platform>/', views.CompleteOAuthView.as_view(), name='complete_oauth'),
    path('api/oauth/complete-allauth/<str:platform>/', api_views.CompleteOAuthAPIView.as_view(), name='complete_oauth_allauth'),
    
    # New Allauth integration views - unified approach
    path('api/oauth/connect/', allauth_views.SocialAuthInitView.as_view(), name='oauth_connect'),
    path('api/accounts/', allauth_views.SocialAccountsView.as_view(), name='accounts_list'),
    path('api/accounts/disconnect/', allauth_views.DisconnectSocialAccountView.as_view(), name='account_disconnect'),
    
    # User account management with AllAuth (existing)
    path('api/accounts/list/', api_views.list_user_accounts, name='list_accounts'),
    path('api/accounts/<int:pk>/primary/', api_views.set_primary_account, name='set_primary_account'),
    path('api/accounts/<int:pk>/refresh/', api_views.refresh_account_token, name='refresh_account_token'),
    path('api/accounts/<int:pk>/disconnect/', api_views.disconnect_account, name='disconnect_account'),
    
    # Public OAuth endpoints (no authentication required) - compatible with existing frontend
    path('api/public/oauth/init/<str:platform>/', views.PublicOAuthInitView.as_view(), name='public_oauth_init'),
    
    # OAuth callbacks - using both original and AllAuth implementation for transition
    path('oauth/callback/', views.OAuthCallbackView.as_view(), name='oauth_callback'),  # Original callback
    path('oauth/callback/allauth/<str:platform>/', api_views.OAuthCallbackView.as_view(), name='allauth_callback'),  # New AllAuth callback
    
    # Platform-specific callbacks - maintained for compatibility
    path('oauth/callback/twitter/', views.TwitterOAuthCallbackView.as_view(), name='twitter_oauth_callback'),
    path('api/social_platforms/oauth/callback/twitter/', views.TwitterOAuthCallbackView.as_view(), name='twitter_oauth_callback_api'),
    path('auth/google/callback', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    
    # Include Django AllAuth URLs
    path('accounts/', include('allauth.urls')),
]

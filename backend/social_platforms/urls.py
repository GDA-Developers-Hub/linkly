from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'social_platforms'

# Create a router for API viewsets
router = DefaultRouter()
router.register(r'platforms', views.SocialPlatformViewSet)
router.register(r'accounts', views.UserSocialAccountViewSet, basename='account')

urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    path('api/oauth/init/<str:platform>/', views.OAuthInitView.as_view(), name='oauth_init'),
    path('api/oauth/complete/<str:platform>/', views.CompleteOAuthView.as_view(), name='complete_oauth'),
    path('api/posts/', views.SocialAccountPostView.as_view(), name='posts'),
    
    # Public OAuth endpoints (no authentication required)
    path('api/public/oauth/init/<str:platform>/', views.PublicOAuthInitView.as_view(), name='public_oauth_init'),
    
    # OAuth callbacks
    path('oauth/callback/', views.OAuthCallbackView.as_view(), name='oauth_callback'),
    path('oauth/callback/twitter/', views.TwitterOAuthCallbackView.as_view(), name='twitter_oauth_callback'),
    # This matches the redirect URI that Twitter is expecting
    path('api/social_platforms/oauth/callback/twitter/', views.TwitterOAuthCallbackView.as_view(), name='twitter_oauth_callback_api'),
    
    # Add URL at project-level (to be included in project-level urls.py)
    path('auth/google/callback', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
]

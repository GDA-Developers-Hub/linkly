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
    path('api/posts/', views.SocialAccountPostView.as_view(), name='posts'),
    
    # Twitter-specific endpoints
    path('api/twitter/post/', views.TwitterPostView.as_view(), name='twitter_post'),
    path('api/twitter/analytics/', views.TwitterAnalyticsView.as_view(), name='twitter_analytics'),
    
    # Public OAuth endpoints (no authentication required)
    path('api/public/oauth/init/<str:platform>/', views.PublicOAuthInitView.as_view(), name='public_oauth_init'),
    
    # OAuth callbacks
    path('oauth/callback/', views.OAuthCallbackView.as_view(), name='oauth_callback'),
    
    # Add URL at project-level (to be included in project-level urls.py)
    path('auth/google/callback', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
]

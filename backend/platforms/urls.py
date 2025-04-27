from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.PlatformListView.as_view(), name='platform-list'),
    path('accounts/', views.PlatformAccountListView.as_view(), name='platform-account-list'),
    path('accounts/<int:pk>/', views.PlatformAccountDetailView.as_view(), name='platform-account-detail'),
    path('accounts/<int:pk>/disconnect/', views.DisconnectPlatformView.as_view(), name='platform-disconnect'),
    
    # Auth endpoints
    path('auth/twitter/login/', views.TwitterAuthView.as_view(), name='twitter-auth'),
    path('auth/facebook/login/', views.FacebookAuthView.as_view(), name='facebook-auth'),
    path('auth/instagram/login/', views.InstagramAuthView.as_view(), name='instagram-auth'),
    path('auth/linkedin/login/', views.LinkedInAuthView.as_view(), name='linkedin-auth'),
    path('auth/callback/', views.AuthCallbackView.as_view(), name='auth-callback'),
]

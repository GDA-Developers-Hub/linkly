from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Social Media Account URLs
    path('social-accounts/', views.SocialAccountListView.as_view(), name='social-accounts-list'),
    path('social-accounts/connect/', views.ConnectSocialAccountView.as_view(), name='connect-social-account'),
    path('social-accounts/disconnect/', views.DisconnectSocialAccountView.as_view(), name='disconnect-social-account'),
    path('social-accounts/refresh-token/', views.RefreshSocialTokenView.as_view(), name='refresh-social-token'),
] 
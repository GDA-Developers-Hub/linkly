from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, UserRegisterView, CustomTokenObtainPairView, LogoutView, UserProfileView, ChangePasswordView

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path("", include("allauth.socialaccount.urls")),
    path("", include("allauth.socialaccount.providers.openid_connect.urls")),
    path("", include("allauth.socialaccount.providers.facebook.urls")),
    path("", include("allauth.socialaccount.providers.twitter.urls")),
    path("", include("allauth.socialaccount.providers.instagram.urls")),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Authentication-required endpoints
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]

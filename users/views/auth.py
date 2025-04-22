# users/auth.py - Remove the RegisterView class
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from ..serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)

User = get_user_model()

# RegisterView is removed from here - use the one in views.py instead

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain pair view."""
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordView(generics.UpdateAPIView):
    """Change password view."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ValidateTokenView(generics.RetrieveAPIView):
    """Validate JWT token view."""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
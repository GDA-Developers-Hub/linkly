from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import Group
from rest_framework.decorators import action

from .serializers import (
    UserSerializer, 
    UserRegisterSerializer, 
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set up logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting user registration process for email: {request.data.get('email')}")
        
        # Create user in our system
        user = serializer.save()
        logger.info(f"Created user in database with ID: {user.id}")
        
        # Ensure UserProfile exists (normally created by signal, but check as backup)
        from .models import UserProfile
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)
            logger.info(f"Created UserProfile for user ID: {user.id}")
        
        # Generate token for the new user
        refresh = RefreshToken.for_user(user)
        logger.info(f"Generated authentication tokens for user ID: {user.id}")
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({"message": "Password updated successfully."}, 
                           status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all().order_by('username')

    def create(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'success': False, 'message': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create user with email as username if it doesn't exist
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email}
            )

            if not created:
                return Response(
                    {'success': False, 'message': 'User already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'success': True,
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            })

        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def role(self, request, pk=None):
        user = self.get_object()
        is_manager = request.data.get('is_google_ads_manager', False)
        
        try:
            google_ads_group = Group.objects.get(name='google_ads_managers')
            
            if is_manager:
                google_ads_group.user_set.add(user)
            else:
                google_ads_group.user_set.remove(user)

            return Response({
                'success': True,
                'message': f"User role {'granted' if is_manager else 'revoked'} successfully",
                'user': UserSerializer(user).data
            })

        except Group.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Google Ads Managers group does not exist'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            user.delete()
            return Response({
                'success': True,
                'message': 'User removed successfully'
            })
        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

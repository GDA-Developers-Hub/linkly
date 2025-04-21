# /home/ismael/linkly/users/views/registration.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

# Fix the import paths - go up one directory level
from django.contrib.auth import get_user_model
from ..serializers import RegisterSerializer, UserSerializer
 # Go up one level to users/serializers.py

User = get_user_model()

class RegisterView(APIView):
    permission_classes = (AllowAny,)
    
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: UserSerializer()}
    )
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Start free trial
                user.start_free_trial()
                
                return Response({
                    'status': 'success',
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Invalid data provided',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
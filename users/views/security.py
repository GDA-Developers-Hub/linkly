from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..serializers import TwoFactorSerializer

class Enable2FAView(generics.CreateAPIView):
    """Enable 2FA view."""
    serializer_class = TwoFactorSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        user.enable_2fa()
        return Response({
            'success': True,
            'message': '2FA has been enabled'
        })

class Verify2FAView(generics.CreateAPIView):
    """Verify 2FA token view."""
    serializer_class = TwoFactorSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        token = serializer.validated_data['token']
        
        if user.verify_2fa_token(token):
            return Response({
                'success': True,
                'message': 'Token verified successfully'
            })
        
        return Response({
            'success': False,
            'message': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST) 
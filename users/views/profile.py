from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializers import UpdateUserSerializer

class UpdateProfileView(generics.UpdateAPIView):
    """Update user profile view."""
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserProfileView(generics.RetrieveAPIView):
    """Retrieve user profile view."""
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user 
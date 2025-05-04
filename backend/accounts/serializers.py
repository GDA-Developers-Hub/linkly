from rest_framework import serializers
from .models import SocialMediaAccount

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SocialMediaAccount
        fields = [
            'id', 'platform', 'platform_display', 'username', 'profile_picture',
            'account_type', 'status', 'status_display', 'connected_at', 'last_used'
        ]
        read_only_fields = [
            'id', 'platform_display', 'status_display', 'connected_at', 'last_used'
        ] 
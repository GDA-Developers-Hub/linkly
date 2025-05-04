from rest_framework import serializers
from .models import SocialPlatform, UserSocialAccount

class SocialPlatformSerializer(serializers.ModelSerializer):
    """Serializer for social platform configuration"""
    
    class Meta:
        model = SocialPlatform
        fields = ['id', 'name', 'display_name', 'is_active']
        
class UserSocialAccountSerializer(serializers.ModelSerializer):
    """Serializer for user's social media accounts"""
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    platform_display_name = serializers.CharField(source='platform.display_name', read_only=True)
    
    class Meta:
        model = UserSocialAccount
        fields = [
            'id', 'platform', 'platform_name', 'platform_display_name',
            'account_id', 'account_name', 'account_type',
            'profile_picture_url', 'status', 'is_primary',
            'created_at', 'updated_at', 'last_used_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SocialAccountDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user's social media accounts"""
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    platform_display_name = serializers.CharField(source='platform.display_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    can_refresh = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserSocialAccount
        fields = [
            'id', 'platform', 'platform_name', 'platform_display_name',
            'account_id', 'account_name', 'account_type',
            'profile_picture_url', 'status', 'is_primary',
            'token_type', 'scope', 'is_expired', 'can_refresh',
            'created_at', 'updated_at', 'last_used_at'
        ]
        read_only_fields = [
            'id', 'platform', 'platform_name', 'platform_display_name',
            'account_id', 'account_name', 'token_type', 'scope',
            'is_expired', 'can_refresh', 'created_at', 'updated_at'
        ]

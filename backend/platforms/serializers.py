from rest_framework import serializers
from .models import Platform, PlatformAccount


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name', 'api_name', 'description', 'icon', 'is_active']


class PlatformAccountSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)
    platform_id = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.filter(is_active=True),
        write_only=True,
        source='platform'
    )
    
    class Meta:
        model = PlatformAccount
        fields = [
            'id', 'user', 'platform', 'platform_id', 'account_id', 
            'account_name', 'account_username', 'account_avatar', 
            'status', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'error_message', 
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

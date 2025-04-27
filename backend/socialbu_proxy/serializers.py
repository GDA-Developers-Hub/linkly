from rest_framework import serializers
from .models import SocialBuToken, SocialPlatformConnection

class SocialBuTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialBuToken
        fields = ['access_token', 'refresh_token', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class SocialBuAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

class SocialBuPostSerializer(serializers.Serializer):
    content = serializers.CharField()
    platforms = serializers.ListField(child=serializers.CharField())
    media_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    scheduled_at = serializers.DateTimeField(required=False)
    
class SocialBuPostUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False)
    platforms = serializers.ListField(child=serializers.CharField(), required=False)
    media_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    scheduled_at = serializers.DateTimeField(required=False)

class SocialBuTeamSerializer(serializers.Serializer):
    name = serializers.CharField()

class SocialBuTeamMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class SocialPlatformConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPlatformConnection
        fields = ['id', 'platform', 'account_id', 'account_name', 'status', 'connected_at', 'updated_at']
        read_only_fields = ['id', 'connected_at', 'updated_at']

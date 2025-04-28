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

class AttachmentSerializer(serializers.Serializer):
    upload_token = serializers.CharField()

class PostOptionsSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)
    post_as_story = serializers.BooleanField(required=False, default=False)

class SocialBuPostSerializer(serializers.Serializer):
    accounts = serializers.ListField(child=serializers.IntegerField())
    team_id = serializers.IntegerField(required=False, allow_null=True)
    publish_at = serializers.DateTimeField(required=False, allow_null=True)
    content = serializers.CharField()
    draft = serializers.BooleanField(required=False, default=False)
    existing_attachments = serializers.ListField(
        child=AttachmentSerializer(), 
        required=False,
        default=list
    )
    postback_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    options = PostOptionsSerializer(required=False, allow_null=True)
    
class SocialBuPostUpdateSerializer(serializers.Serializer):
    accounts = serializers.ListField(child=serializers.IntegerField(), required=False)
    team_id = serializers.IntegerField(required=False, allow_null=True)
    publish_at = serializers.DateTimeField(required=False, allow_null=True)
    content = serializers.CharField(required=False)
    draft = serializers.BooleanField(required=False)
    existing_attachments = serializers.ListField(
        child=AttachmentSerializer(), 
        required=False
    )
    postback_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    options = PostOptionsSerializer(required=False, allow_null=True)

class SocialBuTeamSerializer(serializers.Serializer):
    name = serializers.CharField()

class SocialBuTeamMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class SocialPlatformConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPlatformConnection
        fields = ['id', 'platform', 'account_id', 'account_name', 'status', 'connected_at', 'updated_at']
        read_only_fields = ['id', 'connected_at', 'updated_at']

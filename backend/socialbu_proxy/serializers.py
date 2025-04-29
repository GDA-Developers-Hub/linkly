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

# Media metadata for thumbnails, etc.
class MediaMetadataSerializer(serializers.Serializer):
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)

# Media object for thumbnails, etc.
class MediaObjectSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    mimeType = serializers.CharField(required=False)
    extension = serializers.CharField(required=False)
    key = serializers.CharField(required=False)
    url = serializers.CharField(required=False)
    secureKey = serializers.CharField(required=False)
    temporary = serializers.BooleanField(required=False)
    _metaData = MediaMetadataSerializer(required=False)
    size = serializers.IntegerField(required=False)
    type = serializers.CharField(required=False)
    ext = serializers.CharField(required=False)
    mime = serializers.CharField(required=False)

# Platform-specific option serializers
class FacebookOptionsSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)
    post_as_story = serializers.BooleanField(required=False, default=False)

class InstagramOptionsSerializer(serializers.Serializer):
    post_as_reel = serializers.BooleanField(required=False, default=False)
    post_as_story = serializers.BooleanField(required=False, default=False)
    share_reel_to_feed = serializers.BooleanField(required=False, default=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    thumbnail = MediaObjectSerializer(required=False)

class TwitterReplySerializer(serializers.Serializer):
    tweet = serializers.CharField(required=False)
    media = serializers.ListField(child=MediaObjectSerializer(), required=False)

class TwitterOptionsSerializer(serializers.Serializer):
    media_alt_text = serializers.ListField(child=serializers.CharField(), required=False)
    threaded_replies = serializers.ListField(child=TwitterReplySerializer(), required=False)

class LinkedInOptionsSerializer(serializers.Serializer):
    link = serializers.URLField(required=False)
    trim_link_from_content = serializers.BooleanField(required=False, default=False)
    customize_link = serializers.BooleanField(required=False, default=False)
    link_description = serializers.CharField(required=False, allow_blank=True)
    link_title = serializers.CharField(required=False, allow_blank=True)
    thumbnail = MediaObjectSerializer(required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    document_title = serializers.CharField(required=False, allow_blank=True)

class YouTubeOptionsSerializer(serializers.Serializer):
    video_title = serializers.CharField(required=False, allow_blank=True)
    video_tags = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    privacy_status = serializers.CharField(required=False, allow_blank=True)
    post_as_short = serializers.BooleanField(required=False, default=False)
    made_for_kids = serializers.BooleanField(required=False, default=False)

class TikTokOptionsSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True)
    privacy_status = serializers.CharField(required=False, allow_blank=True)
    allow_stitch = serializers.BooleanField(required=False, default=True)
    allow_duet = serializers.BooleanField(required=False, default=True)
    allow_comment = serializers.BooleanField(required=False, default=True)
    disclose_content = serializers.BooleanField(required=False, default=False)
    branded_content = serializers.BooleanField(required=False, default=False)
    own_brand = serializers.BooleanField(required=False, default=False)

# Generic options serializer that can handle any platform
class PostOptionsSerializer(serializers.Serializer):
    # Common options across platforms
    comment = serializers.CharField(required=False, allow_blank=True)
    post_as_story = serializers.BooleanField(required=False, default=False)
    
    # Instagram specific
    post_as_reel = serializers.BooleanField(required=False, default=False)
    share_reel_to_feed = serializers.BooleanField(required=False, default=False)
    thumbnail = MediaObjectSerializer(required=False)
    
    # Twitter specific
    media_alt_text = serializers.ListField(child=serializers.CharField(), required=False)
    threaded_replies = serializers.ListField(child=TwitterReplySerializer(), required=False)
    
    # LinkedIn specific
    link = serializers.URLField(required=False)
    trim_link_from_content = serializers.BooleanField(required=False, default=False)
    customize_link = serializers.BooleanField(required=False, default=False)
    link_description = serializers.CharField(required=False, allow_blank=True)
    link_title = serializers.CharField(required=False, allow_blank=True)
    document_title = serializers.CharField(required=False, allow_blank=True)
    
    # YouTube specific
    video_title = serializers.CharField(required=False, allow_blank=True)
    video_tags = serializers.CharField(required=False, allow_blank=True)
    category_id = serializers.IntegerField(required=False)
    privacy_status = serializers.CharField(required=False, allow_blank=True)
    post_as_short = serializers.BooleanField(required=False, default=False)
    made_for_kids = serializers.BooleanField(required=False, default=False)
    
    # TikTok specific
    title = serializers.CharField(required=False, allow_blank=True)
    allow_stitch = serializers.BooleanField(required=False, default=True)
    allow_duet = serializers.BooleanField(required=False, default=True)
    allow_comment = serializers.BooleanField(required=False, default=True)
    disclose_content = serializers.BooleanField(required=False, default=False)
    branded_content = serializers.BooleanField(required=False, default=False)
    own_brand = serializers.BooleanField(required=False, default=False)

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
    
    # Include platform info to determine which options to use
    platform = serializers.CharField(required=False, allow_blank=True)
    
    # Generic options that work with any platform
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
    
    # Include platform info to determine which options to use
    platform = serializers.CharField(required=False, allow_blank=True)
    
    # Generic options that work with any platform
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

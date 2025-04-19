# socials/serializers.py
from rest_framework import serializers
from .models import APIUsageLog, APIQuota, ScheduledPost, PostMedia

class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'media_type', 'created_at']

class ScheduledPostSerializer(serializers.ModelSerializer):
    media = PostMediaSerializer(many=True, read_only=True)
    platforms = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledPost
        fields = [
            'id', 'content', 'hashtags', 'scheduled_time', 
            'is_draft', 'status', 'platforms', 'media',
            'created_at', 'updated_at'
        ]

    def get_platforms(self, obj):
        return {
            'instagram': obj.post_to_instagram,
            'facebook': obj.post_to_facebook,
            'twitter': obj.post_to_twitter,
            'linkedin': obj.post_to_linkedin
        }

class APIQuotaSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = APIQuota
        fields = ['platform', 'limit', 'used', 'reset_at', 'status']

    def get_status(self, obj):
        if obj.used >= obj.limit:
            return 'Rate Limited'
        elif obj.used >= obj.limit * 0.8:
            return 'Limited'
        return 'Connected'

class APIUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIUsageLog
        fields = ['platform', 'endpoint', 'timestamp', 'status', 'response_time']
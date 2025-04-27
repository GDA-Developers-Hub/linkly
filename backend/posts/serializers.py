from rest_framework import serializers
from .models import Post, PostPlatform, PostMedia, PostMetrics
from platforms.models import PlatformAccount
from platforms.serializers import PlatformAccountSerializer


class PostMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PostMedia
        fields = ['id', 'file', 'file_url', 'order', 'caption', 'alt_text', 'created_at']
        read_only_fields = ['id', 'file_url', 'created_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class PostMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetrics
        fields = [
            'id', 'impressions', 'reach', 'likes', 'comments', 
            'shares', 'saves', 'clicks', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class PostPlatformSerializer(serializers.ModelSerializer):
    platform_account = PlatformAccountSerializer(read_only=True)
    platform_account_id = serializers.PrimaryKeyRelatedField(
        queryset=PlatformAccount.objects.all(),
        write_only=True,
        source='platform_account'
    )
    metrics = PostMetricsSerializer(read_only=True, many=True)
    
    class Meta:
        model = PostPlatform
        fields = [
            'id', 'platform_account', 'platform_account_id', 'custom_content',
            'status', 'platform_post_id', 'platform_post_url', 
            'error_message', 'published_at', 'metrics'
        ]
        read_only_fields = ['id', 'status', 'platform_post_id', 'platform_post_url', 
                           'error_message', 'published_at']
    
    def validate_platform_account_id(self, value):
        request = self.context.get('request')
        if value.user != request.user:
            raise serializers.ValidationError("You don't have access to this platform account.")
        return value


class PostSerializer(serializers.ModelSerializer):
    post_platforms = PostPlatformSerializer(many=True, required=False)
    media = PostMediaSerializer(many=True, read_only=True)
    platforms = serializers.PrimaryKeyRelatedField(
        queryset=PlatformAccount.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'post_type', 'scheduled_time', 
            'status', 'platforms', 'post_platforms', 'media',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_platforms(self, value):
        request = self.context.get('request')
        for platform in value:
            if platform.user != request.user:
                raise serializers.ValidationError(f"You don't have access to the platform account {platform.id}.")
        return value
    
    def create(self, validated_data):
        platforms_data = validated_data.pop('platforms', [])
        post_platforms_data = validated_data.pop('post_platforms', [])
        
        validated_data['user'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        
        # Add platform accounts
        for platform in platforms_data:
            PostPlatform.objects.create(post=post, platform_account=platform)
        
        # Add custom platform data
        for pp_data in post_platforms_data:
            platform_account = pp_data.pop('platform_account')
            PostPlatform.objects.create(post=post, platform_account=platform_account, **pp_data)
        
        return post
    
    def update(self, instance, validated_data):
        platforms_data = validated_data.pop('platforms', None)
        post_platforms_data = validated_data.pop('post_platforms', None)
        
        # Update post fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update platform accounts if provided
        if platforms_data is not None:
            # Clear existing relationships
            instance.platforms.clear()
            # Create new relationships
            for platform in platforms_data:
                PostPlatform.objects.create(post=instance, platform_account=platform)
        
        # Update custom platform data if provided
        if post_platforms_data is not None:
            instance.post_platforms.all().delete()
            for pp_data in post_platforms_data:
                platform_account = pp_data.pop('platform_account')
                PostPlatform.objects.create(post=instance, platform_account=platform_account, **pp_data)
        
        return instance


class SchedulePostSerializer(serializers.Serializer):
    scheduled_time = serializers.DateTimeField(required=True)
    
    def validate_scheduled_time(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Scheduled time cannot be in the past.")
        return value


class PublishPostSerializer(serializers.Serializer):
    platforms = serializers.PrimaryKeyRelatedField(
        queryset=PlatformAccount.objects.all(),
        many=True,
        required=True
    )
    
    def validate_platforms(self, value):
        request = self.context.get('request')
        for platform in value:
            if platform.user != request.user:
                raise serializers.ValidationError(f"You don't have access to the platform account {platform.id}.")
        return value

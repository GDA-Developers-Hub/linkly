from rest_framework import serializers
from .models import Caption, Hashtag, HashtagGroup, Media


class CaptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caption
        fields = ['id', 'text', 'platform', 'is_saved', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'post_count', 'growth_rate', 'engagement_rate', 'is_trending', 'last_updated']
        read_only_fields = ['id', 'post_count', 'growth_rate', 'engagement_rate', 'is_trending', 'last_updated']


class HashtagGroupSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, read_only=True)
    hashtag_names = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = HashtagGroup
        fields = ['id', 'name', 'platform', 'hashtags', 'hashtag_names', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        hashtag_names = validated_data.pop('hashtag_names', [])
        validated_data['user'] = self.context['request'].user
        
        hashtag_group = HashtagGroup.objects.create(**validated_data)
        
        # Add hashtags to the group
        for name in hashtag_names:
            hashtag, created = Hashtag.objects.get_or_create(name=name.strip())
            hashtag_group.hashtags.add(hashtag)
        
        return hashtag_group
    
    def update(self, instance, validated_data):
        hashtag_names = validated_data.pop('hashtag_names', None)
        
        # Update the group
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update hashtags if provided
        if hashtag_names is not None:
            instance.hashtags.clear()
            for name in hashtag_names:
                hashtag, created = Hashtag.objects.get_or_create(name=name.strip())
                instance.hashtags.add(hashtag)
        
        return instance


class MediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = ['id', 'file', 'file_url', 'media_type', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'file_url', 'created_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CaptionGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True)
    platform = serializers.ChoiceField(
        choices=Caption.PLATFORM_CHOICES,
        default='all'
    )
    tone = serializers.CharField(required=False, default='professional')
    include_hashtags = serializers.BooleanField(required=False, default=False)
    hashtag_count = serializers.IntegerField(required=False, default=5, min_value=1, max_value=30)


class HashtagGenerateSerializer(serializers.Serializer):
    query = serializers.CharField(required=True)
    platform = serializers.CharField(required=False, default='instagram')
    count = serializers.IntegerField(required=False, default=10, min_value=1, max_value=30)

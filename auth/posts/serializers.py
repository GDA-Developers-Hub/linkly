from allauth.socialaccount.models import SocialAccount, SocialApp
from rest_framework import serializers
from .models import Post, PostPlatform, PostMedia, PostMetrics


class PostMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = [
            "id",
            "file",
            "file_url",
            "order",
            "caption",
            "alt_text",
            "created_at",
        ]
        read_only_fields = ["id", "file_url", "created_at"]

    def get_file_url(self, obj):
        if obj.file:
            # Use the Cloudinary URL directly
            return obj.get_url()
        return None


    def get_social_app_id(self, obj):
        try:
            return SocialApp.objects.get(provider=obj.provider).id
        except SocialApp.DoesNotExist:
            return None


class PostMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMetrics
        fields = [
            "id",
            "impressions",
            "reach",
            "likes",
            "comments",
            "shares",
            "saves",
            "clicks",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]


class PostPlatformSerializer(serializers.ModelSerializer):
    social_account = serializers.PrimaryKeyRelatedField(
        queryset=SocialAccount.objects.all(), write_only=True
    )
    social_app = serializers.PrimaryKeyRelatedField(
        queryset=SocialApp.objects.all(), write_only=True
    )
    metrics = PostMetricsSerializer(read_only=True, many=True)

    class Meta:
        model = PostPlatform
        fields = [
            "id",
            "social_account",
            "social_app",
            "custom_content",
            "status",
            "platform_post_id",
            "platform_post_url",
            "error_message",
            "published_at",
            "metrics",
        ]
        read_only_fields = [
            "id",
            "status",
            "platform_post_id",
            "platform_post_url",
            "error_message",
            "published_at",
        ]

    def get_social_account_info(self, obj):
        return {
            "provider": obj.social_account.provider,
            "uid": obj.social_account.uid,
            "display_name": obj.social_account.extra_data.get("name"),
        }

    def validate_social_account(self, value):
        request = self.context.get("request")
        if value.user != request.user:
            raise serializers.ValidationError(
                "You don't have access to this social account."
            )
        return value


class PostSerializer(serializers.ModelSerializer):
    platforms = PostPlatformSerializer(many=True, required=False)
    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "post_type",
            "scheduled_time",
            "status",
            "platforms",
            "media",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_social_accounts(self, value):
        request = self.context.get("request")
        for account in value:
            if account.user != request.user:
                raise serializers.ValidationError(
                    f"You don't have access to the social account {account.id}."
                )
        return value

    def create(self, validated_data):
        accounts_data = validated_data.pop("social_accounts", [])
        post_platforms_data = validated_data.pop("platforms", [])

        validated_data["user"] = self.context["request"].user
        post = Post.objects.create(**validated_data)

        for account in accounts_data:
            PostPlatform.objects.create(post=post, social_account=account)

        for pp_data in post_platforms_data:
            account = pp_data.pop("social_account")
            PostPlatform.objects.create(post=post, social_account=account, **pp_data)


        return post

    def update(self, instance, validated_data):
        accounts_data = validated_data.pop("social_accounts", None)
        post_platforms_data = validated_data.pop("post_platforms", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if accounts_data is not None:
            instance.post_platforms.all().delete()
            for account in accounts_data:
                PostPlatform.objects.create(post=instance, social_account=account)

        if post_platforms_data is not None:
            instance.post_platforms.all().delete()
            for pp_data in post_platforms_data:
                account = pp_data.pop("social_account")
                PostPlatform.objects.create(
                    post=instance, social_account=account, **pp_data
                )

        return instance





class SchedulePostSerializer(serializers.Serializer):
    scheduled_time = serializers.DateTimeField(required=True)

    def validate_scheduled_time(self, value):
        from django.utils import timezone

        if value < timezone.now():
            raise serializers.ValidationError("Scheduled time cannot be in the past.")
        return value

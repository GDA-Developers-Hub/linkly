from rest_framework import serializers
from .models import AccountMetrics, AudienceInsight, BestTimeToPost
from allauth.socialaccount.models import SocialAccount, SocialApp


class AccountMetricsSerializer(serializers.ModelSerializer):
    # social_account = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AccountMetrics
        fields = [
            "id",
            "social_account",
            "followers",
            "following",
            "impressions",
            "reach",
            "profile_views",
            "follower_growth",
            "engagement_rate",
            "date",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]


class AudienceInsightSerializer(serializers.ModelSerializer):
    # social_account = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AudienceInsight
        fields = [
            "id",
            "social_account",
            "age_range",
            "gender",
            "location",
            "value",
            "is_percentage",
            "date",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]


class BestTimeToPostSerializer(serializers.ModelSerializer):
    # social_account = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BestTimeToPost
        fields = [
            "id",
            "social_account",
            "day_of_week",
            "hour",
            "engagement_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

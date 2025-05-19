from rest_framework import serializers
from .models import Campaign, AdGroup, Ad, PerformanceReport, KeywordMetrics, GoogleAdsAccount

class GoogleAdsAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleAdsAccount
        fields = ['customer_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class AdGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdGroup
        fields = '__all__'

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = '__all__'

class PerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReport
        fields = '__all__'

class KeywordMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordMetrics
        fields = '__all__'

class CampaignDetailSerializer(serializers.ModelSerializer):
    performance_reports = PerformanceReportSerializer(many=True, read_only=True)
    ad_groups = AdGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'

class AdGroupDetailSerializer(serializers.ModelSerializer):
    ads = AdSerializer(many=True, read_only=True)
    keyword_metrics = KeywordMetricsSerializer(many=True, read_only=True)

    class Meta:
        model = AdGroup
        fields = '__all__' 
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Campaign, AdGroup, Ad, PerformanceReport, KeywordMetrics

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'budget', 'start_date', 'end_date', 'performance_metrics')
    list_filter = ('status', 'start_date')
    search_fields = ('name',)
    readonly_fields = ('id',)
    
    def performance_metrics(self, obj):
        metrics = PerformanceReport.objects.filter(campaign=obj).aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_cost=Sum('cost'),
            total_conversions=Sum('conversions')
        )
        
        return format_html(
            'Impressions: {}<br>Clicks: {}<br>Cost: ${}<br>Conversions: {}',
            metrics['total_impressions'] or 0,
            metrics['total_clicks'] or 0,
            metrics['total_cost'] or 0,
            metrics['total_conversions'] or 0
        )
    
    performance_metrics.short_description = 'Performance'

@admin.register(AdGroup)
class AdGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'status', 'type', 'ads_count', 'keywords_count')
    list_filter = ('status', 'campaign', 'type')
    search_fields = ('name', 'campaign__name')
    readonly_fields = ('id',)
    
    def ads_count(self, obj):
        return obj.ads.count()
    ads_count.short_description = 'Ads'
    
    def keywords_count(self, obj):
        return obj.keyword_metrics.count()
    keywords_count.short_description = 'Keywords'

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('headline', 'ad_group', 'status', 'final_url')
    list_filter = ('status', 'ad_group__campaign', 'ad_group')
    search_fields = ('headline', 'description', 'ad_group__name')
    readonly_fields = ('id',)

class PerformanceReportAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'date', 'impressions', 'clicks', 'cost', 'conversions', 'ctr', 'cpc')
    list_filter = ('date', 'campaign')
    date_hierarchy = 'date'
    
    def ctr(self, obj):
        if obj.impressions > 0:
            return f'{(obj.clicks / obj.impressions) * 100:.2f}%'
        return '0%'
    ctr.short_description = 'CTR'
    
    def cpc(self, obj):
        if obj.clicks > 0:
            return f'${obj.cost / obj.clicks:.2f}'
        return '$0.00'
    cpc.short_description = 'CPC'

admin.site.register(PerformanceReport, PerformanceReportAdmin)

@admin.register(KeywordMetrics)
class KeywordMetricsAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'match_type', 'ad_group', 'impressions', 'clicks', 'cost', 'conversions', 'ctr', 'cpc')
    list_filter = ('match_type', 'date', 'ad_group__campaign', 'ad_group')
    search_fields = ('keyword', 'ad_group__name')
    date_hierarchy = 'date'
    
    def ctr(self, obj):
        if obj.impressions > 0:
            return f'{(obj.clicks / obj.impressions) * 100:.2f}%'
        return '0%'
    ctr.short_description = 'CTR'
    
    def cpc(self, obj):
        if obj.clicks > 0:
            return f'${obj.cost / obj.clicks:.2f}'
        return '$0.00'
    cpc.short_description = 'CPC' 
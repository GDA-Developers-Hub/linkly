from django.contrib import admin
from .models import AccountMetrics

@admin.register(AccountMetrics)
class AccountMetricsAdmin(admin.ModelAdmin):
    list_display = ('social_account', 'date', 'followers', 'following', 'impressions', 'reach', 'engagement_rate')
    list_filter = ('date', 'social_account__provider')
    search_fields = ('social_account__account_name',)
    date_hierarchy = 'date'
    raw_id_fields = ('social_account',) 
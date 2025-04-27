from django.contrib import admin
from .models import AccountMetrics

@admin.register(AccountMetrics)
class AccountMetricsAdmin(admin.ModelAdmin):
    list_display = ('platform_account', 'date', 'followers', 'following', 'impressions', 'reach', 'engagement_rate')
    list_filter = ('date', 'platform_account__platform')
    search_fields = ('platform_account__account_name',)
    date_hierarchy = 'date'
    raw_id_fields = ('platform_account',) 
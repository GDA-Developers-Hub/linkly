from django.contrib import admin
from .models import SocialPlatform, UserSocialAccount


class SocialPlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'display_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'is_active')
        }),
        ('OAuth Configuration', {
            'fields': ('client_id', 'client_secret', 'auth_url', 'token_url', 'redirect_uri', 'scope'),
            'classes': ('collapse',),
            'description': 'OAuth 2.0 configuration for this platform'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class UserSocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'account_name', 'account_type', 'status', 'is_primary', 'created_at')
    list_filter = ('platform', 'status', 'is_primary')
    search_fields = ('user__email', 'account_name', 'account_id')
    readonly_fields = ('created_at', 'updated_at', 'last_used_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'platform', 'is_primary', 'status')
        }),
        ('Account Details', {
            'fields': ('account_id', 'account_name', 'account_type', 'profile_picture_url'),
        }),
        ('OAuth Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_type', 'token_expiry', 'scope'),
            'classes': ('collapse',),
            'description': 'Sensitive OAuth token data'
        }),
        ('Additional Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_used_at'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(SocialPlatform, SocialPlatformAdmin)
admin.site.register(UserSocialAccount, UserSocialAccountAdmin)

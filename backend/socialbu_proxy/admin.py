from django.contrib import admin
from .models import SocialBuToken, SocialPlatformConnection

@admin.register(SocialBuToken)
class SocialBuTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'socialbu_user_id', 'name', 'email', 'verified', 'created_at', 'updated_at')
    search_fields = ('user__email', 'name', 'email', 'socialbu_user_id')
    list_filter = ('verified', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'email', 'verified', 'socialbu_user_id')
        }),
        ('Authentication', {
            'fields': ('access_token', 'refresh_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(SocialPlatformConnection)
class SocialPlatformConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'account_name', 'account_id', 'status', 'connected_at')
    search_fields = ('user__email', 'platform', 'account_name')
    list_filter = ('platform', 'status', 'connected_at')
    readonly_fields = ('connected_at', 'updated_at')

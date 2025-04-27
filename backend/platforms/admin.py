from django.contrib import admin
from .models import Platform, PlatformAccount

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'api_name')

@admin.register(PlatformAccount)
class PlatformAccountAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'platform', 'user', 'status')
    list_filter = ('platform', 'status')
    search_fields = ('account_name', 'account_username', 'user__email')
    raw_id_fields = ('user', 'platform') 
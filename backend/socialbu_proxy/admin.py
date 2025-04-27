from django.contrib import admin
from .models import SocialBuToken

@admin.register(SocialBuToken)
class SocialBuTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'created_at', 'updated_at')
    search_fields = ('user__email',)

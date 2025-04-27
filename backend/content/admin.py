from django.contrib import admin
from .models import Hashtag

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'growth_rate', 'engagement_rate', 'is_trending', 'last_updated')
    list_filter = ('is_trending',)
    search_fields = ('name',)
    readonly_fields = ('last_updated',) 
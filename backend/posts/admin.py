from django.contrib import admin
from .models import Post, PostPlatform, PostMetrics

class PostPlatformInline(admin.TabularInline):
    model = PostPlatform
    extra = 1
    raw_id_fields = ('platform_account',)

class PostMetricsInline(admin.TabularInline):
    model = PostMetrics
    extra = 0
    readonly_fields = ('impressions', 'reach', 'likes', 'comments', 'shares', 'saves', 'clicks')
    can_delete = False
    max_num = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post_type', 'status', 'scheduled_time', 'created_at')
    list_filter = ('status', 'post_type')
    search_fields = ('content', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
    inlines = [PostPlatformInline, PostMetricsInline]

@admin.register(PostPlatform)
class PostPlatformAdmin(admin.ModelAdmin):
    list_display = ('post', 'platform_account', 'status', 'published_at')
    list_filter = ('status', 'platform_account__platform')
    search_fields = ('post__content', 'platform_account__account_name')
    raw_id_fields = ('post', 'platform_account')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PostMetrics)
class PostMetricsAdmin(admin.ModelAdmin):
    list_display = ('post', 'platform_post', 'impressions', 'reach', 'likes', 'comments')
    search_fields = ('post__content',)
    raw_id_fields = ('post', 'platform_post') 
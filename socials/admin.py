# socials/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import APIUsageLog, APIQuota, ScheduledPost, PostMedia

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'media_type', 'file_preview', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['post__content', 'post__user__email']
    readonly_fields = ['file_preview']

    def file_preview(self, obj):
        if obj.media_type == 'image' and obj.file:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.file.url)
        return format_html('<span class="badge badge-info">{}</span>', obj.media_type)
    file_preview.short_description = 'Preview'

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1
    readonly_fields = ['preview_image']
    
    def preview_image(self, obj):
        if obj.media_type == 'image' and obj.file:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.file.url)
        return '-'

@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'content_preview', 'platform_badges', 
        'scheduled_time', 'status_badge', 'media_count'
    ]
    list_filter = [
        'status', 'is_draft', 'post_to_instagram', 
        'post_to_facebook', 'post_to_twitter', 'post_to_linkedin',
        'scheduled_time'
    ]
    search_fields = ['content', 'hashtags', 'user__email']
    inlines = [PostMediaInline]
    actions = ['publish_now', 'convert_to_draft']
    date_hierarchy = 'scheduled_time'
    fieldsets = (
        ('Post Details', {
            'fields': ('user', 'content', 'hashtags', 'scheduled_time', 'is_draft', 'status')
        }),
        ('Platforms', {
            'fields': (
                'post_to_instagram', 'post_to_facebook', 
                'post_to_twitter', 'post_to_linkedin'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def platform_badges(self, obj):
        badges = []
        if obj.post_to_instagram:
            badges.append('<span class="badge badge-info">Instagram</span>')
        if obj.post_to_facebook:
            badges.append('<span class="badge badge-primary">Facebook</span>')
        if obj.post_to_twitter:
            badges.append('<span class="badge badge-info">Twitter</span>')
        if obj.post_to_linkedin:
            badges.append('<span class="badge badge-success">LinkedIn</span>')
        return format_html(' '.join(badges))
    platform_badges.short_description = 'Platforms'

    def status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'scheduled': 'info',
            'published': 'success',
            'failed': 'danger'
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.status.title()
        )
    status_badge.short_description = 'Status'

    def media_count(self, obj):
        count = obj.media.count()
        return format_html(
            '<span class="badge badge-dark">{} {}</span>',
            count,
            'files' if count != 1 else 'file'
        )
    media_count.short_description = 'Media'

@admin.register(APIQuota)
class APIQuotaAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'platform', 'usage_display', 
        'reset_at', 'status_badge'
    ]
    list_filter = ['platform', 'reset_at']
    search_fields = ['user__email']
    date_hierarchy = 'reset_at'
    fieldsets = (
        ('Quota Details', {
            'fields': ('user', 'platform', 'limit', 'used', 'reset_at')
        }),
    )

    def usage_display(self, obj):
        percentage = (obj.used / obj.limit) * 100 if obj.limit else 0
        color = 'success'
        if percentage >= 80:
            color = 'warning'
        if percentage >= 100:
            color = 'danger'
        return format_html(
            '<div class="progress" style="width: 100px;">'
            '<div class="progress-bar bg-{}" role="progressbar" '
            'style="width: {}%">{}/{}</div></div>',
            color, min(percentage, 100), obj.used, obj.limit
        )
    usage_display.short_description = 'Usage'

    def status_badge(self, obj):
        if obj.used >= obj.limit:
            color = 'danger'
            status = 'Rate Limited'
        elif obj.used >= obj.limit * 0.8:
            color = 'warning'
            status = 'Limited'
        else:
            color = 'success'
            status = 'Connected'
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'

@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'platform', 'endpoint', 
        'status_code', 'response_time_display', 
        'timestamp'
    ]
    list_filter = [
        'platform', 'status', 
        'timestamp'
    ]
    search_fields = [
        'user__email', 'endpoint'
    ]
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Usage Details', {
            'fields': ('user', 'platform', 'endpoint', 'status', 'response_time', 'timestamp')
        }),
    )
    readonly_fields = ['timestamp']

    def status_code(self, obj):
        colors = {
            '2': 'success',
            '3': 'info',
            '4': 'warning',
            '5': 'danger'
        }
        status_first_digit = str(obj.status)[0]
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors.get(status_first_digit, 'secondary'),
            obj.status
        )
    status_code.short_description = 'Status'

    def response_time_display(self, obj):
        if obj.response_time < 0.5:
            color = 'success'
        elif obj.response_time < 1:
            color = 'warning'
        else:
            color = 'danger'
        return format_html(
            '<span class="badge badge-{}">{:.2f}s</span>',
            color, obj.response_time
        )
    response_time_display.short_description = 'Response Time'

    class Media:
        css = {
            'all': ['admin/css/custom.css']
        }
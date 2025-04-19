from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count, F, Sum, Avg, Case, When
from django.urls import reverse
from django.utils import timezone
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from .models import SubscriptionPlan, Subscription
from decimal import Decimal
from django.db import models
from django.contrib import messages

User = get_user_model()

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('plan', 'status', 'start_date', 'end_date', 'is_trial', 'auto_renew')
    can_delete = False
    max_num = 5
    ordering = ('-created_at',)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'username', 'is_active', 'subscription_status',
        'date_joined', 'get_connected_platforms', 'get_business_accounts',
        'total_followers', 'last_login_colored', 'engagement_score'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser',
        'current_subscription__status', 'has_used_trial',
        'has_facebook_business', 'has_instagram_business',
        'has_linkedin_company', 'has_youtube_brand',
        'has_tiktok_business', 'has_telegram_channel',
        'date_joined', 'last_login',
        ('metrics_last_updated', admin.DateFieldListFilter),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name', 
                    'company_name', 'business_description', 'industry')
    ordering = ('-date_joined',)
    actions = [
        'update_metrics', 'deactivate_users', 'activate_users', 
        'start_trial', 'cancel_subscription', 'reset_2fa',
        'export_user_data', 'sync_social_metrics'
    ]
    inlines = [SubscriptionInline]
    change_list_template = 'admin/users/user/change_list.html'

    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password'),
            'classes': ('wide',)
        }),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'profile_picture', 'phone_number'),
            'classes': ('collapse',)
        }),
        (_('Business Info'), {
            'fields': (
                'is_business', 'company_name', 'business_description', 
                'website', 'industry', 'get_total_reach'
            ),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'metrics_last_updated'),
            'classes': ('collapse',)
        }),
        (_('Personal Social Accounts'), {
            'classes': ('collapse',),
            'fields': (
                ('google_id', 'google_token_expiry', 'get_google_status'),
                ('facebook_id', 'facebook_token_expiry', 'get_facebook_status'),
                ('linkedin_id', 'linkedin_token_expiry', 'get_linkedin_status'),
                ('telegram_id', 'telegram_token_expiry', 'get_telegram_status'),
                ('instagram_id', 'instagram_token_expiry', 'get_instagram_status'),
                ('twitter_id', 'twitter_token_expiry', 'get_twitter_status'),
                ('tiktok_id', 'tiktok_token_expiry', 'get_tiktok_status')
            ),
        }),
        (_('Business Accounts'), {
            'classes': ('collapse',),
            'fields': (
                ('has_facebook_business', 'facebook_page_id', 'facebook_page_name', 'facebook_page_token', 'facebook_page_token_expiry', 'get_facebook_metrics'),
                ('has_instagram_business', 'instagram_business_id', 'instagram_business_name', 'instagram_business_token', 'instagram_business_token_expiry', 'get_instagram_metrics'),
                ('has_linkedin_company', 'linkedin_company_id', 'linkedin_company_name', 'linkedin_company_token', 'linkedin_company_token_expiry', 'get_linkedin_metrics'),
                ('has_youtube_brand', 'youtube_brand_id', 'youtube_brand_name', 'youtube_brand_token', 'youtube_brand_token_expiry', 'get_youtube_metrics'),
                ('has_tiktok_business', 'tiktok_business_id', 'tiktok_business_name', 'tiktok_business_token', 'tiktok_business_token_expiry', 'get_tiktok_metrics'),
                ('has_telegram_channel', 'telegram_chat_id', 'telegram_channel_name', 'get_telegram_metrics')
            ),
        }),
        (_('Metrics & Analytics'), {
            'classes': ('collapse',),
            'fields': (
                ('facebook_page_followers', 'instagram_business_followers', 'get_social_growth'),
                ('linkedin_company_followers', 'youtube_subscribers', 'get_engagement_rate'),
                ('twitter_followers', 'tiktok_followers', 'get_platform_distribution'),
                ('telegram_subscribers', 'get_total_engagement', 'get_best_performing_platform')
            ),
        }),
        (_('2FA Settings'), {
            'classes': ('collapse',),
            'fields': ('two_factor_enabled', 'two_factor_secret', 'backup_codes', 'get_2fa_status'),
        }),
        (_('Subscription'), {
            'fields': (
                'current_subscription', 'has_used_trial',
                'subscription_updated_at', 'get_subscription_history'
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = (
        'date_joined', 'last_login', 'metrics_last_updated',
        'google_id', 'facebook_id', 'linkedin_id',
        'telegram_id', 'instagram_id', 'twitter_id',
        'tiktok_id', 'google_token_expiry', 'facebook_token_expiry',
        'linkedin_token_expiry', 'telegram_token_expiry',
        'instagram_token_expiry', 'twitter_token_expiry',
        'tiktok_token_expiry', 'facebook_page_token_expiry',
        'instagram_business_token_expiry', 'linkedin_company_token_expiry',
        'youtube_brand_token_expiry', 'tiktok_business_token_expiry',
        'subscription_updated_at', 'get_total_reach', 'get_google_status',
        'get_facebook_status', 'get_linkedin_status', 'get_telegram_status',
        'get_instagram_status', 'get_twitter_status', 'get_tiktok_status',
        'get_facebook_metrics', 'get_instagram_metrics', 'get_linkedin_metrics',
        'get_youtube_metrics', 'get_tiktok_metrics', 'get_telegram_metrics',
        'get_social_growth', 'get_engagement_rate', 'get_platform_distribution',
        'get_total_engagement', 'get_best_performing_platform', 'get_2fa_status',
        'get_subscription_history'
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            total_followers=(
                F('facebook_page_followers') +
                F('instagram_business_followers') +
                F('linkedin_company_followers') +
                F('youtube_subscribers') +
                F('tiktok_followers') +
                F('telegram_subscribers')
            ),
            engagement_score=Case(
                When(total_followers__gt=0, then=F('total_followers') * 100),
                default=0,
                output_field=models.IntegerField(),
            )
        )

    def get_connected_platforms(self, obj):
        platforms = []
        if obj.google_id:
            platforms.append('<span class="badge badge-info">Google</span>')
        if obj.facebook_id:
            platforms.append('<span class="badge badge-primary">Facebook</span>')
        if obj.linkedin_id:
            platforms.append('<span class="badge badge-success">LinkedIn</span>')
        if obj.telegram_id:
            platforms.append('<span class="badge badge-info">Telegram</span>')
        if obj.instagram_id:
            platforms.append('<span class="badge badge-warning">Instagram</span>')
        if obj.twitter_id:
            platforms.append('<span class="badge badge-primary">Twitter</span>')
        if obj.tiktok_id:
            platforms.append('<span class="badge badge-dark">TikTok</span>')
        return format_html(' '.join(platforms)) if platforms else 'None'
    get_connected_platforms.short_description = 'Connected Platforms'
    get_connected_platforms.allow_tags = True

    def get_business_accounts(self, obj):
        accounts = []
        if obj.has_facebook_business:
            accounts.append('<span class="badge badge-primary">FB Business</span>')
        if obj.has_instagram_business:
            accounts.append('<span class="badge badge-warning">IG Business</span>')
        if obj.has_linkedin_company:
            accounts.append('<span class="badge badge-success">LinkedIn Company</span>')
        if obj.has_youtube_brand:
            accounts.append('<span class="badge badge-danger">YouTube Brand</span>')
        if obj.has_tiktok_business:
            accounts.append('<span class="badge badge-dark">TikTok Business</span>')
        if obj.has_telegram_channel:
            accounts.append('<span class="badge badge-info">Telegram Channel</span>')
        return format_html(' '.join(accounts)) if accounts else 'None'
    get_business_accounts.short_description = 'Business Accounts'
    get_business_accounts.allow_tags = True

    def last_login_colored(self, obj):
        if not obj.last_login:
            return format_html('<span class="text-muted">Never</span>')
        
        days_since_login = (timezone.now() - obj.last_login).days
        if days_since_login < 7:
            color = 'success'
        elif days_since_login < 30:
            color = 'warning'
        else:
            color = 'danger'
        
        return format_html('<span class="text-{}">{}</span>', 
                         color, obj.last_login.strftime('%Y-%m-%d %H:%M'))
    last_login_colored.short_description = 'Last Login'
    last_login_colored.admin_order_field = 'last_login'

    def total_followers(self, obj):
        formatted_number = "{:,}".format(obj.total_followers)
        return format_html('<b>{}</b>', formatted_number)
    total_followers.short_description = 'Total Followers'
    total_followers.admin_order_field = 'total_followers'

    def subscription_status(self, obj):
        if not obj.current_subscription:
            return format_html('<span class="text-muted">No Subscription</span>')
        
        status = obj.current_subscription.status
        if status == 'ACTIVE':
            color = 'success'
        elif status == 'TRIAL':
            color = 'info'
        elif status == 'PENDING':
            color = 'warning'
        else:
            color = 'danger'
        
        days = obj.current_subscription.days_remaining()
        status_text = f"{status} ({days} days left)"
        
        return format_html('<span class="text-{}">{}</span>', color, status_text)
    subscription_status.short_description = 'Subscription'
    subscription_status.admin_order_field = 'current_subscription__status'

    def engagement_score(self, obj):
        score = obj.engagement_score
        if score > 10000:
            color = 'success'
        elif score > 5000:
            color = 'warning'
        else:
            color = 'danger'
        return format_html('<span class="badge badge-{}">{}</span>', color, score)
    engagement_score.short_description = 'Engagement'
    engagement_score.admin_order_field = 'engagement_score'

    def get_social_growth(self, obj):
        # Calculate social media growth rate
        try:
            current_total = obj.total_followers
            previous_total = obj.previous_total_followers
            growth_rate = ((current_total - previous_total) / previous_total * 100)
            color = 'success' if growth_rate > 0 else 'danger'
            return format_html(
                '<span class="badge badge-{}">{:+.1f}%</span>',
                color, growth_rate
            )
        except:
            return format_html('<span class="text-muted">N/A</span>')
    get_social_growth.short_description = 'Social Growth'

    def get_engagement_rate(self, obj):
        # Calculate engagement rate across platforms
        try:
            total_engagement = obj.total_engagement
            total_followers = obj.total_followers
            rate = (total_engagement / total_followers * 100)
            return format_html('{:.2f}%', rate)
        except:
            return format_html('<span class="text-muted">N/A</span>')
    get_engagement_rate.short_description = 'Engagement Rate'

    def get_platform_distribution(self, obj):
        # Show distribution of followers across platforms
        platforms = []
        total = obj.total_followers
        if total > 0:
            for platform, count in {
                'FB': obj.facebook_page_followers,
                'IG': obj.instagram_business_followers,
                'LI': obj.linkedin_company_followers,
                'YT': obj.youtube_subscribers,
                'TT': obj.tiktok_followers,
                'TG': obj.telegram_subscribers
            }.items():
                if count > 0:
                    percentage = count / total * 100
                    platforms.append(f'{platform}: {percentage:.1f}%')
            return format_html('<br>'.join(platforms))
        return 'No followers'
    get_platform_distribution.short_description = 'Platform Distribution'

    def get_best_performing_platform(self, obj):
        # Identify best performing platform
        platforms = {
            'Facebook': obj.facebook_page_followers,
            'Instagram': obj.instagram_business_followers,
            'LinkedIn': obj.linkedin_company_followers,
            'YouTube': obj.youtube_subscribers,
            'TikTok': obj.tiktok_followers,
            'Telegram': obj.telegram_subscribers
        }
        best = max(platforms.items(), key=lambda x: x[1])
        return format_html(
            '<span class="badge badge-success">{} ({:,})</span>',
            best[0], best[1]
        )
    get_best_performing_platform.short_description = 'Best Platform'

    def get_subscription_history(self, obj):
        # Show subscription history
        history = obj.subscriptions.all()[:5]
        if not history:
            return 'No subscription history'
        
        html = ['<ul style="padding-left: 15px;">']
        for sub in history:
            status_color = {
                'ACTIVE': 'success',
                'TRIAL': 'info',
                'CANCELLED': 'danger',
                'EXPIRED': 'warning',
                'PENDING': 'secondary'
            }.get(sub.status, 'secondary')
            
            html.append(
                f'<li>{sub.plan.name} - '
                f'<span class="badge badge-{status_color}">{sub.status}</span><br>'
                f'<small class="text-muted">{sub.start_date.strftime("%Y-%m-%d")} to '
                f'{sub.end_date.strftime("%Y-%m-%d")}</small></li>'
            )
        html.append('</ul>')
        return format_html(''.join(html))
    get_subscription_history.short_description = 'Subscription History'

    @admin.action(description='Update social media metrics')
    def update_metrics(self, request, queryset):
        updated = 0
        for user in queryset:
            try:
                # Add your metric update logic here
                user.metrics_last_updated = timezone.now()
                user.save()
                updated += 1
            except Exception as e:
                self.message_user(request, f"Error updating metrics for {user.email}: {str(e)}")
        
        self.message_user(request, f'Successfully updated metrics for {updated} users.')

    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {updated} users.')

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {updated} users.')

    def get_total_reach(self, obj):
        total = obj.total_followers
        return format_html('<b>{:,}</b> followers', total)
    get_total_reach.short_description = 'Total Reach'

    def get_google_status(self, obj):
        if not obj.google_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.google_token_expiry and obj.google_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_google_status.short_description = 'Status'

    def get_facebook_status(self, obj):
        if not obj.facebook_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.facebook_token_expiry and obj.facebook_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_facebook_status.short_description = 'Status'

    def get_linkedin_status(self, obj):
        if not obj.linkedin_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.linkedin_token_expiry and obj.linkedin_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_linkedin_status.short_description = 'Status'

    def get_telegram_status(self, obj):
        if not obj.telegram_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.telegram_token_expiry and obj.telegram_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_telegram_status.short_description = 'Status'

    def get_instagram_status(self, obj):
        if not obj.instagram_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.instagram_token_expiry and obj.instagram_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_instagram_status.short_description = 'Status'

    def get_twitter_status(self, obj):
        if not obj.twitter_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.twitter_token_expiry and obj.twitter_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_twitter_status.short_description = 'Status'

    def get_tiktok_status(self, obj):
        if not obj.tiktok_id:
            return format_html('<span class="text-muted">Not Connected</span>')
        if obj.tiktok_token_expiry and obj.tiktok_token_expiry < timezone.now():
            return format_html('<span class="text-danger">Token Expired</span>')
        return format_html('<span class="text-success">Connected</span>')
    get_tiktok_status.short_description = 'Status'

    def get_facebook_metrics(self, obj):
        if not obj.has_facebook_business:
            return '-'
        return format_html(
            '<div style="text-align: left;">'
            'Followers: <b>{:,}</b><br>'
            'Page: <b>{}</b>'
            '</div>',
            obj.facebook_page_followers,
            obj.facebook_page_name or 'N/A'
        )
    get_facebook_metrics.short_description = 'Metrics'

    def get_instagram_metrics(self, obj):
        if not obj.has_instagram_business:
            return '-'
        return format_html(
            '<div style="text-align: left;">'
            'Followers: <b>{:,}</b><br>'
            'Account: <b>{}</b>'
            '</div>',
            obj.instagram_business_followers,
            obj.instagram_business_name or 'N/A'
        )
    get_instagram_metrics.short_description = 'Metrics'

    def get_linkedin_metrics(self, obj):
        if not obj.has_linkedin_company:
            return '-'
        return format_html(
            '<div style="text-align: left;">'
            'Followers: <b>{:,}</b><br>'
            'Company: <b>{}</b>'
            '</div>',
            obj.linkedin_company_followers,
            obj.linkedin_company_name or 'N/A'
        )
    get_linkedin_metrics.short_description = 'Metrics'

    def get_youtube_metrics(self, obj):
        if not obj.has_youtube_brand:
            return '-'
        return format_html(
            '<div style="text-align: left;">'
            'Subscribers: <b>{:,}</b><br>'
            'Channel: <b>{}</b>'
            '</div>',
            obj.youtube_subscribers,
            obj.youtube_brand_name or 'N/A'
        )
    get_youtube_metrics.short_description = 'Metrics'

    def get_tiktok_metrics(self, obj):
        if not obj.has_tiktok_business:
            return '-'
        return format_html(
            '<div style="text-align: left;">'
            'Followers: <b>{:,}</b><br>'
            'Account: <b>{}</b>'
            '</div>',
            obj.tiktok_followers,
            obj.tiktok_business_name or 'N/A'
        )
    get_tiktok_metrics.short_description = 'Metrics'

    def get_telegram_metrics(self, obj):
        if not obj.has_telegram_channel:
            return '-'
        return format_html(
            '<div style="text-align: left;">'
            'Subscribers: <b>{:,}</b><br>'
            'Channel: <b>{}</b>'
            '</div>',
            obj.telegram_subscribers,
            obj.telegram_channel_name or 'N/A'
        )
    get_telegram_metrics.short_description = 'Metrics'

    def get_total_engagement(self, obj):
        try:
            total_followers = obj.total_followers
            if total_followers > 0:
                # Calculate engagement score based on followers and activity
                engagement_score = (total_followers * 100) / 1000  # Example calculation
                return format_html(
                    '<div>'
                    '<span style="font-size: 18px;"><b>{:.1f}</b></span><br>'
                    '<small class="text-muted">Score</small>'
                    '</div>',
                    engagement_score
                )
            return '0'
        except:
            return 'N/A'
    get_total_engagement.short_description = 'Engagement Score'

    def get_2fa_status(self, obj):
        if not obj.two_factor_enabled:
            return format_html(
                '<span class="text-danger">'
                '<i class="fas fa-unlock"></i> Disabled'
                '</span>'
            )
        return format_html(
            '<span class="text-success">'
            '<i class="fas fa-lock"></i> Enabled'
            '</span>'
        )
    get_2fa_status.short_description = '2FA Status'

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_price', 'social_accounts_limit', 'ai_caption_limit', 'is_active', 'get_features', 'active_subscriptions')
    list_filter = ('is_active', 'has_analytics', 'has_advanced_analytics', 'has_team_collaboration')
    search_fields = ('name',)
    ordering = ('price',)
    actions = ['activate_plans', 'deactivate_plans', 'duplicate_plan']

    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'is_active')
        }),
        (_('Limits'), {
            'fields': ('social_accounts_limit', 'ai_caption_limit', 'team_member_limit')
        }),
        (_('Features'), {
            'fields': (
                'has_analytics',
                'has_advanced_analytics',
                'has_content_calendar',
                'has_team_collaboration',
                'has_competitor_analysis',
                'has_api_access',
                'has_dedicated_support'
            )
        }),
    )
    

    def formatted_price(self, obj):
        formatted_price = '{:.2f}'.format(float(obj.price))
        return format_html('${} /month', formatted_price)
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'

    def active_subscriptions(self, obj):
        count = obj.subscription_set.filter(status='ACTIVE').count()
        return format_html('<span class="badge badge-success">{}</span>', count)
    active_subscriptions.short_description = 'Active Subs'

    def get_features(self, obj):
        features = []
        if obj.has_analytics:
            features.append('<span class="badge badge-info">Analytics</span>')
        if obj.has_advanced_analytics:
            features.append('<span class="badge badge-primary">Advanced Analytics</span>')
        if obj.has_content_calendar:
            features.append('<span class="badge badge-success">Calendar</span>')
        if obj.has_team_collaboration:
            features.append('<span class="badge badge-warning">Team ({} max)</span>'.format(obj.team_member_limit))
        if obj.has_competitor_analysis:
            features.append('<span class="badge badge-danger">Competitor Analysis</span>')
        if obj.has_api_access:
            features.append('<span class="badge badge-dark">API Access</span>')
        if obj.has_dedicated_support:
            features.append('<span class="badge badge-primary">Support</span>')
        return format_html(' '.join(features)) if features else 'None'
    get_features.short_description = 'Features'
    get_features.allow_tags = True

    @admin.action(description='Activate selected plans')
    def activate_plans(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Successfully activated {updated} plans.')

    @admin.action(description='Deactivate selected plans')
    def deactivate_plans(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Successfully deactivated {updated} plans.')

    @admin.action(description='Duplicate selected plans')
    def duplicate_plan(self, request, queryset):
        for plan in queryset:
            new_plan = SubscriptionPlan.objects.create(
                name=f"{plan.name}_COPY",
                price=plan.price,
                social_accounts_limit=plan.social_accounts_limit,
                ai_caption_limit=plan.ai_caption_limit,
                has_analytics=plan.has_analytics,
                has_advanced_analytics=plan.has_advanced_analytics,
                has_content_calendar=plan.has_content_calendar,
                has_team_collaboration=plan.has_team_collaboration,
                team_member_limit=plan.team_member_limit,
                has_competitor_analysis=plan.has_competitor_analysis,
                has_api_access=plan.has_api_access,
                has_dedicated_support=plan.has_dedicated_support,
                is_active=False
            )
        self.message_user(request, f'Successfully duplicated {queryset.count()} plans.')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            active_subs_count=Count('subscription', 
                filter=models.Q(subscription__status='ACTIVE'))
        )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'plan_name', 'status', 'start_date', 'end_date', 'is_trial', 'days_remaining', 'auto_renew', 'monthly_revenue')
    list_filter = ('status', 'is_trial', 'auto_renew', 'plan__name', 'created_at', 'payment_method')
    search_fields = ('user__email', 'user__username', 'plan__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ['cancel_subscriptions', 'activate_subscriptions', 'extend_trial', 'enable_auto_renew', 'disable_auto_renew']
    
    change_list_template = 'admin/users/subscription_change_list.html'

    fieldsets = (
        (None, {
            'fields': ('user', 'plan', 'status')
        }),
        (_('Dates'), {
            'fields': (
                'start_date',
                'end_date',
                'trial_end_date',
                'cancelled_at',
                'created_at',
                'updated_at'
            )
        }),
        (_('Settings'), {
            'fields': (
                'is_trial',
                'auto_renew',
                'payment_method'
            )
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def monthly_revenue(self, obj):
        if obj.status == 'ACTIVE' and not obj.is_trial:
            return format_html('${:.2f}', obj.plan.price)
        return format_html('<span class="text-muted">$0.00</span>')
    monthly_revenue.short_description = 'Monthly Revenue'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'plan')

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        
        try:
            qs = self.get_queryset(request)
            now = timezone.now()
            month_ago = now - timezone.timedelta(days=30)
            
            # Basic metrics
            active_subs = qs.filter(status='ACTIVE', is_trial=False)
            active_count = active_subs.count()
            previous_active_count = qs.filter(
                status='ACTIVE',
                is_trial=False,
                start_date__lt=month_ago
            ).count()
            
            # Calculate trends
            active_trend = (
                ((active_count - previous_active_count) / previous_active_count * 100)
                if previous_active_count > 0 else 0
            )
            
            # Trial metrics
            total_trials = qs.filter(status='TRIAL').count()
            converted_trials = qs.filter(
                status='ACTIVE',
                is_trial=False,
                start_date__gte=month_ago
            ).count()
            trial_conversion_rate = (
                (converted_trials / total_trials * 100)
                if total_trials > 0 else 0
            )
            
            # Revenue metrics
            current_mrr = active_subs.aggregate(
                total=Sum('plan__price'))['total'] or Decimal('0')
            previous_mrr = qs.filter(
                status='ACTIVE',
                is_trial=False,
                start_date__lt=month_ago
            ).aggregate(total=Sum('plan__price'))['total'] or Decimal('0')
            mrr_growth = (
                ((current_mrr - previous_mrr) / previous_mrr * 100)
                if previous_mrr > 0 else 0
            )
            
            # Churn metrics
            churned = qs.filter(
                status='CANCELLED',
                cancelled_at__gte=month_ago
            ).count()
            churn_rate = (
                (churned / active_count * 100)
                if active_count > 0 else 0
            )
            
            # Get expiring subscriptions
            expiring_soon = qs.filter(
                status='ACTIVE',
                end_date__range=[now, now + timezone.timedelta(days=7)]
            ).select_related('user', 'plan')
            
            # Historical data for charts
            months = 6
            revenue_data = []
            revenue_labels = []
            new_subs_data = []
            churned_subs_data = []
            subscription_labels = []
            
            for i in range(months-1, -1, -1):
                date = now - timezone.timedelta(days=30*i)
                month_start = date.replace(day=1)
                if i > 0:
                    month_end = (month_start + timezone.timedelta(days=32)).replace(day=1)
                else:
                    month_end = now
                
                # Revenue data
                month_revenue = qs.filter(
                    status='ACTIVE',
                    is_trial=False,
                    start_date__lt=month_end,
                    end_date__gt=month_start
                ).aggregate(total=Sum('plan__price'))['total'] or Decimal('0')
                revenue_data.append(float(month_revenue))
                revenue_labels.append(date.strftime('%B %Y'))
                
                # Subscription data
                new_subs = qs.filter(
                    start_date__range=[month_start, month_end],
                    is_trial=False
                ).count()
                churned_subs = qs.filter(
                    cancelled_at__range=[month_start, month_end]
                ).count()
                new_subs_data.append(new_subs)
                churned_subs_data.append(-churned_subs)  # Negative for the stacked chart
                subscription_labels.append(date.strftime('%b %Y'))
            
            # Plan distribution
            plan_distribution = []
            for plan in SubscriptionPlan.objects.all():
                plan_subs = active_subs.filter(plan=plan)
                plan_distribution.append({
                    'name': plan.get_name_display(),
                    'count': plan_subs.count(),
                    'revenue': plan_subs.count() * plan.price
                })
            
            extra_context = {
                'total_active': active_count,
                'total_trial': total_trials,
                'monthly_revenue': current_mrr,
                'avg_subscription_length': qs.filter(
                    status='ACTIVE'
                ).aggregate(avg=Avg(F('end_date') - F('start_date')))['avg'],
                'active_trend': round(active_trend, 1),
                'trial_conversion_rate': round(trial_conversion_rate, 1),
                'mrr_growth': round(mrr_growth, 1),
                'churn_rate': round(churn_rate, 1),
                'expiring_subscriptions': expiring_soon,
                'revenue_data': revenue_data,
                'revenue_labels': revenue_labels,
                'new_subscriptions_data': new_subs_data,
                'churned_subscriptions_data': churned_subs_data,
                'subscription_labels': subscription_labels,
                'plan_distribution': plan_distribution,
            }
            
            response.context_data.update(extra_context)
        except Exception as e:
            # Log the error but don't break the admin view
            print(f"Error generating subscription stats: {e}")
        
        return response

    @admin.action(description='Extend trial by 7 days')
    def extend_trial(self, request, queryset):
        for subscription in queryset:
            if subscription.is_trial:
                subscription.end_date = subscription.end_date + timezone.timedelta(days=7)
                subscription.trial_end_date = subscription.end_date
                subscription.save()
                
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(subscription).pk,
                    object_id=subscription.id,
                    object_repr=str(subscription),
                    action_flag=CHANGE,
                    change_message='Extended trial period by 7 days'
                )
        
        self.message_user(request, f'Extended trial period for {queryset.count()} subscriptions.')

    @admin.action(description='Enable auto-renew')
    def enable_auto_renew(self, request, queryset):
        updated = queryset.update(auto_renew=True)
        self.message_user(request, f'Enabled auto-renew for {updated} subscriptions.')

    @admin.action(description='Disable auto-renew')
    def disable_auto_renew(self, request, queryset):
        updated = queryset.update(auto_renew=False)
        self.message_user(request, f'Disabled auto-renew for {updated} subscriptions.')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def plan_name(self, obj):
        return obj.plan.get_name_display()
    plan_name.short_description = 'Plan'
    plan_name.admin_order_field = 'plan__name'

    def days_remaining(self, obj):
        days = obj.days_remaining()
        if days > 30:
            color = 'success'
        elif days > 7:
            color = 'warning'
        else:
            color = 'danger'
        return format_html('<span class="text-{}">{} days</span>', color, days)
    days_remaining.short_description = 'Days Remaining'

    @admin.action(description='Cancel selected subscriptions')
    def cancel_subscriptions(self, request, queryset):
        updated = queryset.update(
            status='CANCELLED',
            cancelled_at=timezone.now(),
            auto_renew=False
        )
        self.message_user(request, f'Successfully cancelled {updated} subscriptions.')

    @admin.action(description='Activate selected subscriptions')
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(
            status='ACTIVE',
            cancelled_at=None,
            auto_renew=True
        )
        self.message_user(request, f'Successfully activated {updated} subscriptions.') 
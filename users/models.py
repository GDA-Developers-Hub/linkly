from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import pyotp
import uuid
from datetime import datetime, timedelta
from django.utils import timezone

class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('FREE_TRIAL', 'Free Trial'),
        ('STARTER', 'Starter'),
        ('PRO', 'Pro'),
        ('ENTERPRISE', 'Enterprise')
    ]

    name = models.CharField(max_length=50, choices=PLAN_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    social_accounts_limit = models.IntegerField()
    ai_caption_limit = models.IntegerField()
    has_analytics = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_content_calendar = models.BooleanField(default=False)
    has_team_collaboration = models.BooleanField(default=False)
    team_member_limit = models.IntegerField(default=0)
    has_competitor_analysis = models.BooleanField(default=False)
    has_api_access = models.BooleanField(default=False)
    has_dedicated_support = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('TRIAL', 'Trial'),
        ('PENDING', 'Pending')
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(null=True, blank=True)
    is_trial = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    def is_active(self):
        now = timezone.now()
        return (
            self.status == 'ACTIVE' and 
            self.start_date <= now and 
            self.end_date > now
        )

    def is_trial_active(self):
        now = timezone.now()
        return (
            self.is_trial and 
            self.trial_end_date and 
            self.trial_end_date > now
        )

    def days_remaining(self):
        if self.end_date:
            now = timezone.now()
            if now < self.end_date:
                time_left = self.end_date - now
                total_seconds = time_left.total_seconds()
                
                # Calculate days, hours, and minutes
                days = int(total_seconds // (24 * 3600))
                hours = int((total_seconds % (24 * 3600)) // 3600)
                minutes = int((total_seconds % 3600) // 60)
                
                # Format the time remaining
                if days > 0:
                    return f"{days}d {hours}h {minutes}m"
                elif hours > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{minutes}m"
        return "0m"

    def cancel(self):
        self.status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        self.auto_renew = False
        self.save()

class User(AbstractUser):
    # Basic user fields
    email = models.EmailField(unique=True)
    is_business = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    business_description = models.TextField(blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    
    # Subscription fields
    has_used_trial = models.BooleanField(default=False)
    
    # JWT token fields
    access_token_jwt = models.TextField(blank=True, null=True)
    refresh_token_jwt = models.TextField(blank=True, null=True)
    token_created_at = models.DateTimeField(null=True)

    # 2FA fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.JSONField(default=list)

    # Google fields
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    google_access_token = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)
    google_token_expiry = models.DateTimeField(null=True)
    google_business_connected = models.BooleanField(default=False)
    
    # Facebook fields
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_access_token = models.TextField(blank=True, null=True)
    facebook_token_expiry = models.DateTimeField(null=True)
    facebook_page = models.URLField(max_length=500, blank=True, null=True)
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_name = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_token = models.TextField(blank=True, null=True)
    facebook_page_category = models.CharField(max_length=100, blank=True, null=True)
    facebook_page_followers = models.IntegerField(default=0)
    has_facebook_business = models.BooleanField(default=False)
    
    # LinkedIn fields
    linkedin_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    linkedin_access_token = models.TextField(blank=True, null=True)
    linkedin_token_expiry = models.DateTimeField(null=True)
    linkedin_profile = models.URLField(max_length=500, blank=True, null=True)
    linkedin_company_id = models.CharField(max_length=255, blank=True, null=True)
    linkedin_company_name = models.CharField(max_length=255, blank=True, null=True)
    linkedin_company_token = models.TextField(blank=True, null=True)
    linkedin_company_page = models.URLField(max_length=500, blank=True, null=True)
    linkedin_company_followers = models.IntegerField(default=0)
    has_linkedin_company = models.BooleanField(default=False)
    
    # Twitter fields
    twitter_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    twitter_access_token = models.TextField(blank=True, null=True)
    twitter_access_token_secret = models.TextField(blank=True, null=True)
    twitter_token_expiry = models.DateTimeField(null=True)
    twitter_handle = models.CharField(max_length=255, blank=True, null=True)
    twitter_profile_url = models.URLField(max_length=500, blank=True, null=True)
    twitter_followers = models.IntegerField(default=0)
    has_twitter_business = models.BooleanField(default=False)
    
    # Instagram fields
    instagram_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    instagram_access_token = models.TextField(blank=True, null=True)
    instagram_token_expiry = models.DateTimeField(null=True)
    instagram_handle = models.CharField(max_length=255, blank=True, null=True)
    instagram_profile_url = models.URLField(max_length=500, blank=True, null=True)
    instagram_business_id = models.CharField(max_length=255, blank=True, null=True)
    instagram_business_name = models.CharField(max_length=255, blank=True, null=True)
    instagram_business_token = models.TextField(blank=True, null=True)
    instagram_business_followers = models.IntegerField(default=0)
    has_instagram_business = models.BooleanField(default=False)
    
    # TikTok fields
    tiktok_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tiktok_access_token = models.TextField(blank=True, null=True)
    tiktok_token_expiry = models.DateTimeField(null=True)
    tiktok_handle = models.CharField(max_length=255, blank=True, null=True)
    tiktok_profile_url = models.URLField(max_length=500, blank=True, null=True)
    tiktok_business_id = models.CharField(max_length=255, blank=True, null=True)
    tiktok_business_name = models.CharField(max_length=255, blank=True, null=True)
    tiktok_business_token = models.TextField(blank=True, null=True)
    tiktok_business_category = models.CharField(max_length=100, blank=True, null=True)
    tiktok_followers = models.IntegerField(default=0)
    has_tiktok_business = models.BooleanField(default=False)
    
    # Telegram fields
    telegram_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)
    telegram_channel_name = models.CharField(max_length=255, blank=True, null=True)
    telegram_subscribers = models.IntegerField(default=0)
    has_telegram_channel = models.BooleanField(default=False)
    
    # YouTube fields
    youtube_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    youtube_access_token = models.TextField(blank=True, null=True)
    youtube_refresh_token = models.TextField(blank=True, null=True)
    youtube_token_expiry = models.DateTimeField(null=True)
    youtube_channel = models.URLField(max_length=500, blank=True, null=True)
    youtube_channel_id = models.CharField(max_length=255, blank=True, null=True)
    youtube_channel_title = models.CharField(max_length=255, blank=True, null=True)
    youtube_subscribers = models.IntegerField(default=0)
    has_youtube_brand = models.BooleanField(default=False)
    
    # Metrics and sync tracking
    metrics_last_updated = models.DateTimeField(null=True)
    last_sync = models.JSONField(default=dict)  # Stores last sync time for each platform

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def enable_2fa(self):
        """Enable 2FA for the user"""
        if not self.two_factor_secret:
            self.two_factor_secret = pyotp.random_base32()
            self.generate_backup_codes()
            self.two_factor_enabled = True
            self.save()
        return self.two_factor_secret

    def verify_2fa(self, code):
        """Verify 2FA code or backup code"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code)

    def generate_backup_codes(self, count=8):
        """Generate new backup codes"""
        self.backup_codes = [str(uuid.uuid4())[:8] for _ in range(count)]
        self.save()
        return self.backup_codes

    def get_2fa_uri(self):
        """Get the 2FA QR code URI"""
        if self.two_factor_secret:
            totp = pyotp.TOTP(self.two_factor_secret)
            return totp.provisioning_uri(self.email, issuer_name="Linkly")
        return None

    def update_jwt_tokens(self, access_token, refresh_token):
        """Update JWT tokens"""
        self.access_token_jwt = access_token
        self.refresh_token_jwt = refresh_token
        self.token_created_at = timezone.now()
        self.save()

    def update_social_token(self, platform, access_token, expires_in=3600):
        """Update social media access token and expiry"""
        setattr(self, f'{platform}_access_token', access_token)
        setattr(self, f'{platform}_token_expiry', 
                timezone.now() + timedelta(seconds=int(expires_in)))
        self.save()

    def is_social_token_valid(self, platform):
        """Check if social media token is still valid"""
        expiry = getattr(self, f'{platform}_token_expiry', None)
        if not expiry:
            return False
        return timezone.now() < expiry

    def start_free_trial(self):
        if self.has_used_trial:
            return False

        trial_plan = SubscriptionPlan.objects.get(name='FREE_TRIAL')
        now = timezone.now()
        # Set trial to end at midnight of the 10th day
        trial_end = (now + timedelta(days=10)).replace(hour=23, minute=59, second=59, microsecond=999999)

        subscription = Subscription.objects.create(
            user=self,
            plan=trial_plan,
            status='TRIAL',
            start_date=now,
            end_date=trial_end,
            trial_end_date=trial_end,
            is_trial=True
        )

        self.current_subscription = subscription
        self.has_used_trial = True
        self.save()
        return True

    def subscribe_to_plan(self, plan, payment_method=None):
        now = timezone.now()
        
        # End current subscription if exists
        if self.current_subscription and self.current_subscription.is_active():
            self.current_subscription.status = 'EXPIRED'
            self.current_subscription.save()

        # Create new subscription
        subscription = Subscription.objects.create(
            user=self,
            plan=plan,
            status='ACTIVE',
            start_date=now,
            end_date=now + timedelta(days=30),  # 30-day subscription
            payment_method=payment_method,
            is_trial=False
        )

        self.current_subscription = subscription
        self.save()
        return subscription

    def can_use_feature(self, feature_name):
        if not self.current_subscription or not self.current_subscription.is_active():
            return False

        plan = self.current_subscription.plan
        feature_map = {
            'analytics': plan.has_analytics,
            'advanced_analytics': plan.has_advanced_analytics,
            'content_calendar': plan.has_content_calendar,
            'team_collaboration': plan.has_team_collaboration,
            'competitor_analysis': plan.has_competitor_analysis,
            'api_access': plan.has_api_access,
            'dedicated_support': plan.has_dedicated_support
        }

        return feature_map.get(feature_name, False)

    def get_social_accounts_limit(self):
        if not self.current_subscription or not self.current_subscription.is_active():
            return 0
        return self.current_subscription.plan.social_accounts_limit

    def get_ai_caption_limit(self):
        if not self.current_subscription or not self.current_subscription.is_active():
            return 0
        return self.current_subscription.plan.ai_caption_limit

    def update_last_sync(self, platform):
        """Update last sync time for a platform"""
        self.last_sync[platform] = timezone.now().isoformat()
        self.save()

    def get_last_sync(self, platform):
        """Get last sync time for a platform"""
        return self.last_sync.get(platform)

    def update_last_sync(self, platform):
        """Update the last sync timestamp for a platform"""
        sync_field = f'last_sync_{platform.lower()}'
        if hasattr(self, sync_field):
            setattr(self, sync_field, timezone.now())
            self.save(update_fields=[sync_field])

    def get_last_sync(self, platform):
        """Get the last sync time for a platform in a human-readable format"""
        sync_field = f'last_sync_{platform.lower()}'
        last_sync = getattr(self, sync_field) if hasattr(self, sync_field) else None
        
        if not last_sync:
            return 'Never'
            
        now = timezone.now()
        diff = now - last_sync
        
        if diff.days > 0:
            return f'{diff.days} days ago'
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f'{hours} hours ago'
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f'{minutes} minutes ago'
        else:
            return 'Just now'

    class Meta:
        db_table = 'auth_user' 
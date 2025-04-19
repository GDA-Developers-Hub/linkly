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
                return (self.end_date - now).days
        return 0

    def cancel(self):
        self.status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        self.auto_renew = False
        self.save()

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    is_business = models.BooleanField(default=False)
    company_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    # Social auth fields
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True)
    linkedin_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    linkedin_company_id = models.CharField(max_length=255, blank=True, null=True)
    twitter_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    youtube_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    youtube_brand_id = models.CharField(max_length=255, blank=True, null=True)
    telegram_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    instagram_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    instagram_business_id = models.CharField(max_length=255, blank=True, null=True)
    tiktok_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    tiktok_business_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Social media fields
    instagram_handle = models.CharField(max_length=255, blank=True)
    instagram_profile_url = models.URLField(blank=True)
    instagram_business_name = models.CharField(max_length=255, blank=True)
    instagram_business_category = models.CharField(max_length=255, blank=True)
    
    twitter_handle = models.CharField(max_length=255, blank=True)
    twitter_profile_url = models.URLField(blank=True)
    twitter_business_type = models.CharField(max_length=255, blank=True)
    
    linkedin_profile = models.URLField(blank=True)
    linkedin_company_page = models.URLField(blank=True)
    linkedin_company_name = models.CharField(max_length=255, blank=True)
    
    youtube_channel = models.URLField(blank=True)
    youtube_channel_id = models.CharField(max_length=255, blank=True)
    youtube_channel_title = models.CharField(max_length=255, blank=True)
    youtube_brand_name = models.CharField(max_length=255, blank=True)
    
    facebook_page = models.URLField(blank=True)
    facebook_page_name = models.CharField(max_length=255, blank=True)
    facebook_page_category = models.CharField(max_length=255, blank=True)
    
    tiktok_handle = models.CharField(max_length=255, blank=True)
    tiktok_profile_url = models.URLField(blank=True)
    tiktok_business_name = models.CharField(max_length=255, blank=True)
    tiktok_business_category = models.CharField(max_length=255, blank=True)
    
    telegram_username = models.CharField(max_length=255, blank=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True)
    telegram_channel_name = models.CharField(max_length=255, blank=True)

    # Social tokens
    google_access_token = models.TextField(blank=True, null=True)
    facebook_access_token = models.TextField(blank=True, null=True)
    facebook_page_token = models.TextField(blank=True, null=True)
    linkedin_access_token = models.TextField(blank=True, null=True)
    linkedin_company_token = models.TextField(blank=True, null=True)
    twitter_access_token = models.TextField(blank=True, null=True)
    twitter_access_token_secret = models.TextField(blank=True, null=True)
    youtube_access_token = models.TextField(blank=True, null=True)
    youtube_refresh_token = models.TextField(blank=True, null=True)
    youtube_brand_token = models.TextField(blank=True, null=True)
    telegram_bot_token = models.TextField(blank=True, null=True)
    instagram_access_token = models.TextField(blank=True, null=True)
    instagram_business_token = models.TextField(blank=True, null=True)
    tiktok_access_token = models.TextField(blank=True, null=True)
    tiktok_business_token = models.TextField(blank=True, null=True)
    
    # Token refresh timestamps
    google_token_expiry = models.DateTimeField(null=True)
    facebook_token_expiry = models.DateTimeField(null=True)
    facebook_page_token_expiry = models.DateTimeField(null=True)
    linkedin_token_expiry = models.DateTimeField(null=True)
    linkedin_company_token_expiry = models.DateTimeField(null=True)
    twitter_token_expiry = models.DateTimeField(null=True)
    youtube_token_expiry = models.DateTimeField(null=True)
    youtube_brand_token_expiry = models.DateTimeField(null=True)
    telegram_token_expiry = models.DateTimeField(null=True)
    instagram_token_expiry = models.DateTimeField(null=True)
    instagram_business_token_expiry = models.DateTimeField(null=True)
    tiktok_token_expiry = models.DateTimeField(null=True)
    tiktok_business_token_expiry = models.DateTimeField(null=True)

    # Business account flags
    has_facebook_business = models.BooleanField(default=False)
    has_instagram_business = models.BooleanField(default=False)
    has_linkedin_company = models.BooleanField(default=False)
    has_youtube_brand = models.BooleanField(default=False)
    has_twitter_business = models.BooleanField(default=False)
    has_tiktok_business = models.BooleanField(default=False)
    has_telegram_channel = models.BooleanField(default=False)

    # Business metrics (for caching common metrics)
    facebook_page_followers = models.IntegerField(default=0)
    instagram_business_followers = models.IntegerField(default=0)
    linkedin_company_followers = models.IntegerField(default=0)
    youtube_subscribers = models.IntegerField(default=0)
    twitter_followers = models.IntegerField(default=0)
    tiktok_followers = models.IntegerField(default=0)
    telegram_subscribers = models.IntegerField(default=0)
    
    # Last metrics update
    metrics_last_updated = models.DateTimeField(null=True)

    # Additional business fields
    business_description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    # 2FA fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Token fields for Node.js compatibility
    access_token_jwt = models.TextField(blank=True, null=True)
    refresh_token_jwt = models.TextField(blank=True, null=True)
    token_created_at = models.DateTimeField(null=True)
    
    # Add subscription-related fields
    current_subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_user'
    )
    has_used_trial = models.BooleanField(default=False)
    subscription_updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

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
        """Update JWT tokens for Node.js compatibility"""
        self.access_token_jwt = access_token
        self.refresh_token_jwt = refresh_token
        self.token_created_at = datetime.now()
        self.save()

    def update_social_token(self, platform, access_token, expires_in=3600):
        """Update social media access token and expiry"""
        token_field = f"{platform}_access_token"
        expiry_field = f"{platform}_token_expiry"
        
        if hasattr(self, token_field) and hasattr(self, expiry_field):
            setattr(self, token_field, access_token)
            setattr(self, expiry_field, datetime.now() + timedelta(seconds=expires_in))
            self.save()

    def is_social_token_valid(self, platform):
        """Check if social media token is still valid"""
        expiry_field = f"{platform}_token_expiry"
        if hasattr(self, expiry_field):
            expiry = getattr(self, expiry_field)
            if expiry and expiry > datetime.now():
                return True
        return False

    def start_free_trial(self):
        if self.has_used_trial:
            return False

        trial_plan = SubscriptionPlan.objects.get(name='FREE_TRIAL')
        now = timezone.now()
        trial_end = now + timedelta(days=10)  # 10-day trial

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
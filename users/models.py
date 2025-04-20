from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import pyotp
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
import logging

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
    current_subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_user'
    )
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
        """Get the last sync time for a platform"""
        return self.last_sync.get(platform)

    def connect_twitter(self, access_token, access_token_secret):
        """Connect Twitter account using OAuth tokens"""
        import tweepy
        from django.conf import settings
        
        try:
            # First, create OAuth 1.0a User Handler
            auth = tweepy.OAuthHandler(
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET
            )
            auth.set_access_token(access_token, access_token_secret)
            
            # Create API v1.1 instance for compatibility
            api = tweepy.API(auth)
            
            # Verify credentials using v1.1 endpoint
            user_info = api.verify_credentials()
            
            if not user_info:
                logging.error("Failed to verify Twitter credentials")
                return {
                    'success': False,
                    'error': 'Could not verify Twitter credentials'
                }
            
            # Store Twitter account info
            self.twitter_id = str(user_info.id)
            self.twitter_handle = user_info.screen_name
            self.twitter_profile_url = f"https://twitter.com/{user_info.screen_name}"
            self.twitter_followers = user_info.followers_count
            self.twitter_access_token = access_token
            self.twitter_access_token_secret = access_token_secret
            
            # Create v2 client for additional data if needed
            client = tweepy.Client(
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            try:
                # Try to get additional user data from v2 API
                user_v2 = client.get_me()
                if user_v2.data:
                    # Update with any additional v2 data if available
                    pass
            except Exception as e:
                # Log v2 error but don't fail the whole connection
                logging.warning(f"Failed to get v2 user data: {str(e)}")
            
            self.save()
            
            return {
                'success': True,
                'profile': {
                    'id': self.twitter_id,
                    'handle': self.twitter_handle,
                    'profile_url': self.twitter_profile_url,
                    'followers': self.twitter_followers
                }
            }
            
        except Exception as e:
            logging.error(f"Twitter connection error: {str(e)}")
            return {
                'success': False,
                'error': f"Twitter API Error: {str(e)}"
            }

    def connect_facebook(self, access_token):
        """Connect Facebook account using OAuth token"""
        import facebook
        from django.conf import settings
        
        try:
            # Initialize Facebook Graph API client
            graph = facebook.GraphAPI(access_token=access_token)
            
            # Get user info
            user_info = graph.get_object('me', fields='id,name,link')
            
            # Store Facebook account info
            self.facebook_id = user_info['id']
            self.facebook_access_token = access_token
            self.facebook_token_expiry = timezone.now() + timedelta(days=60)  # Facebook tokens typically expire in 60 days
            self.save()
            
            return {
                'success': True,
                'profile': {
                    'id': self.facebook_id,
                    'name': user_info.get('name'),
                    'profile_url': user_info.get('link')
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def connect_linkedin(self, access_token):
        """Connect LinkedIn account using OAuth token"""
        from linkedin import linkedin
        from django.conf import settings
        
        try:
            # Initialize LinkedIn API client
            authentication = linkedin.LinkedInAuthentication(
                settings.LINKEDIN_CLIENT_ID,
                settings.LINKEDIN_CLIENT_SECRET,
                settings.LINKEDIN_REDIRECT_URI,
                ['r_liteprofile']
            )
            authentication.token = access_token
            application = linkedin.LinkedInApplication(authentication)
            
            # Get user profile
            profile = application.get_profile()
            
            # Store LinkedIn account info
            self.linkedin_id = profile['id']
            self.linkedin_access_token = access_token
            self.linkedin_token_expiry = timezone.now() + timedelta(days=60)
            self.linkedin_profile = profile.get('siteStandardProfileRequest', {}).get('url')
            self.save()
            
            return {
                'success': True,
                'profile': {
                    'id': self.linkedin_id,
                    'profile_url': self.linkedin_profile
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def connect_instagram(self, access_token):
        """Connect Instagram account using OAuth token"""
        import requests
        from django.conf import settings
        
        try:
            # Get user info from Instagram Graph API
            response = requests.get(
                'https://graph.instagram.com/me',
                params={
                    'fields': 'id,username',
                    'access_token': access_token
                }
            )
            user_info = response.json()
            
            # Store Instagram account info
            self.instagram_id = user_info['id']
            self.instagram_handle = user_info['username']
            self.instagram_profile_url = f"https://instagram.com/{user_info['username']}"
            self.instagram_access_token = access_token
            self.instagram_token_expiry = timezone.now() + timedelta(days=60)
            self.save()
            
            return {
                'success': True,
                'profile': {
                    'id': self.instagram_id,
                    'handle': self.instagram_handle,
                    'profile_url': self.instagram_profile_url
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def connect_tiktok(self, access_token):
        """Connect TikTok account using OAuth token"""
        import requests
        from django.conf import settings
        
        try:
            # Get user info from TikTok API
            response = requests.get(
                'https://open-api.tiktok.com/user/info/',
                params={
                    'access_token': access_token,
                    'fields': 'open_id,union_id,avatar_url,display_name'
                }
            )
            user_info = response.json()['data']
            
            # Store TikTok account info
            self.tiktok_id = user_info['open_id']
            self.tiktok_handle = user_info['display_name']
            self.tiktok_access_token = access_token
            self.tiktok_token_expiry = timezone.now() + timedelta(days=1)  # TikTok tokens expire in 24 hours
            self.save()
            
            return {
                'success': True,
                'profile': {
                    'id': self.tiktok_id,
                    'handle': self.tiktok_handle
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def connect_telegram(self, chat_id, username):
        """Connect Telegram account"""
        try:
            # Store Telegram account info
            self.telegram_id = str(chat_id)
            self.telegram_username = username
            self.telegram_chat_id = str(chat_id)
            self.save()
            
            return {
                'success': True,
                'profile': {
                    'id': self.telegram_id,
                    'username': self.telegram_username,
                    'chat_id': self.telegram_chat_id
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def disconnect_twitter(self):
        """Disconnect Twitter account"""
        self.twitter_id = None
        self.twitter_handle = None
        self.twitter_profile_url = None
        self.twitter_followers = None
        self.twitter_access_token = None
        self.twitter_access_token_secret = None
        self.twitter_token_expiry = None
        self.save()
        return {'success': True}

    def disconnect_facebook(self):
        """Disconnect Facebook account"""
        self.facebook_id = None
        self.facebook_access_token = None
        self.facebook_token_expiry = None
        self.save()
        return {'success': True}

    def disconnect_linkedin(self):
        """Disconnect LinkedIn account"""
        self.linkedin_id = None
        self.linkedin_access_token = None
        self.linkedin_token_expiry = None
        self.linkedin_profile = None
        self.save()
        return {'success': True}

    def disconnect_instagram(self):
        """Disconnect Instagram account"""
        self.instagram_id = None
        self.instagram_handle = None
        self.instagram_profile_url = None
        self.instagram_access_token = None
        self.instagram_token_expiry = None
        self.save()
        return {'success': True}

    def disconnect_tiktok(self):
        """Disconnect TikTok account"""
        self.tiktok_id = None
        self.tiktok_handle = None
        self.tiktok_access_token = None
        self.tiktok_token_expiry = None
        self.save()
        return {'success': True}

    def disconnect_telegram(self):
        """Disconnect Telegram account"""
        self.telegram_id = None
        self.telegram_username = None
        self.telegram_chat_id = None
        self.save()
        return {'success': True}

    def get_connected_platforms(self):
        """Get a list of all connected social media platforms"""
        connected = []
        
        if self.twitter_id:
            connected.append({
                'platform': 'twitter',
                'id': self.twitter_id,
                'handle': self.twitter_handle,
                'profile_url': self.twitter_profile_url,
                'followers': self.twitter_followers,
                'last_sync': self.get_last_sync('twitter')
            })
            
        if self.facebook_id:
            connected.append({
                'platform': 'facebook',
                'id': self.facebook_id,
                'last_sync': self.get_last_sync('facebook')
            })
            
        if self.linkedin_id:
            connected.append({
                'platform': 'linkedin',
                'id': self.linkedin_id,
                'profile_url': self.linkedin_profile,
                'last_sync': self.get_last_sync('linkedin')
            })
            
        if self.instagram_id:
            connected.append({
                'platform': 'instagram',
                'id': self.instagram_id,
                'handle': self.instagram_handle,
                'profile_url': self.instagram_profile_url,
                'last_sync': self.get_last_sync('instagram')
            })
            
        if self.tiktok_id:
            connected.append({
                'platform': 'tiktok',
                'id': self.tiktok_id,
                'handle': self.tiktok_handle,
                'last_sync': self.get_last_sync('tiktok')
            })
            
        if self.telegram_id:
            connected.append({
                'platform': 'telegram',
                'id': self.telegram_id,
                'username': self.telegram_username,
                'chat_id': self.telegram_chat_id,
                'last_sync': self.get_last_sync('telegram')
            })
            
        return connected

    def is_platform_connected(self, platform):
        """Check if a specific platform is connected"""
        platform = platform.lower()
        if platform == 'twitter':
            return bool(self.twitter_id)
        elif platform == 'facebook':
            return bool(self.facebook_id)
        elif platform == 'linkedin':
            return bool(self.linkedin_id)
        elif platform == 'instagram':
            return bool(self.instagram_id)
        elif platform == 'tiktok':
            return bool(self.tiktok_id)
        elif platform == 'telegram':
            return bool(self.telegram_id)
        return False

    class Meta:
        db_table = 'auth_user' 
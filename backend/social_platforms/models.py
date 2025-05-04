from django.db import models
from django.conf import settings
from datetime import datetime, timedelta
import json

class SocialPlatform(models.Model):
    """
    Model representing different social media platforms
    """
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('pinterest', 'Pinterest'),
        ('google', 'Google'),
    ]
    
    name = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    auth_url = models.URLField(max_length=255)
    token_url = models.URLField(max_length=255)
    redirect_uri = models.URLField(max_length=255)
    scope = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name
        
    def get_scopes_list(self):
        """Returns the scope string as a list of individual scopes"""
        return self.scope.split(' ')
        
    class Meta:
        verbose_name = "Social Platform"
        verbose_name_plural = "Social Platforms"

class UserSocialAccount(models.Model):
    """
    Model representing user connections to social media platforms
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('token_expired', 'Token Expired'),
        ('revoked', 'Revoked'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE, related_name='user_accounts')
    account_id = models.CharField(max_length=255)  # Platform-specific account ID
    account_name = models.CharField(max_length=255)  # User-friendly name (e.g., page name, channel name)
    account_type = models.CharField(max_length=100, blank=True, null=True)  # e.g., "page", "profile", "channel"
    profile_picture_url = models.URLField(max_length=255, blank=True, null=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)  # Optional: Some platforms don't provide refresh tokens
    token_expiry = models.DateTimeField(null=True, blank=True)
    token_type = models.CharField(max_length=50, default='Bearer')
    scope = models.TextField(blank=True, null=True)  # Actual scopes granted
    raw_data = models.JSONField(null=True, blank=True)  # Store raw platform data
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_primary = models.BooleanField(default=False)  # Mark primary account for each platform
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)  # Track when the account was last used
    
    def __str__(self):
        return f"{self.user.email} - {self.account_name} ({self.platform.name})"
    
    @property
    def is_expired(self):
        """Check if the access token has expired"""
        if not self.token_expiry:
            return False
        # Add a small buffer (5 minutes) to account for delays
        return self.token_expiry - timedelta(minutes=5) < datetime.now()
    
    @property
    def can_refresh(self):
        """Check if this account can refresh its token"""
        return bool(self.refresh_token)
    
    def set_raw_data(self, data):
        """Set raw data from API response"""
        self.raw_data = data
        
    def get_meta_value(self, key, default=None):
        """Helper to get values from the raw_data JSON"""
        if not self.raw_data:
            return default
        try:
            if isinstance(self.raw_data, str):
                data = json.loads(self.raw_data)
            else:
                data = self.raw_data
            return data.get(key, default)
        except json.JSONDecodeError:
            return default

    class Meta:
        verbose_name = "User Social Account"
        verbose_name_plural = "User Social Accounts"
        unique_together = ('user', 'platform', 'account_id')  # One connection per platform account
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['status']),
        ]

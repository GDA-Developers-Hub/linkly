from django.db import models
from django.conf import settings


class Platform(models.Model):
    """Model for social media platforms"""
    name = models.CharField(max_length=100)
    api_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class PlatformAccount(models.Model):
    """Model for user's connected platform accounts"""
    STATUS_CHOICES = (
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('pending', 'Pending'),
        ('error', 'Error'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='platform_accounts')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='accounts')
    
    account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    account_username = models.CharField(max_length=255, blank=True)
    account_avatar = models.URLField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Authentication tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'platform', 'account_id')
    
    def __str__(self):
        return f"{self.account_name} ({self.platform.name}) - {self.user.email}"

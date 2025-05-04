from django.db import models
from django.conf import settings

class SocialMediaAccount(models.Model):
    PLATFORM_CHOICES = (
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('error', 'Error'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)  # e.g., personal, business, creator
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    connected_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)  # Store platform-specific data

    class Meta:
        unique_together = ('user', 'platform', 'account_id')
        ordering = ['-connected_at']

    def __str__(self):
        return f"{self.platform} - {self.username}"

    def is_token_valid(self):
        from django.utils import timezone
        return self.status == 'active' and (
            self.token_expires_at is None or 
            self.token_expires_at > timezone.now()
        ) 
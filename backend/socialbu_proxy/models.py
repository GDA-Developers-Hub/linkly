from django.db import models
from django.conf import settings

class SocialBuToken(models.Model):
    """
    Model to store SocialBu API tokens
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='socialbu_token')
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True)
    socialbu_user_id = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"SocialBu token for {self.user.email}"

class SocialPlatformConnection(models.Model):
    """
    Model to store social platform connection details
    """
    STATUS_CHOICES = (
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('token_expired', 'Token Expired'),
        ('error', 'Error'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_connections')
    platform = models.CharField(max_length=50)  # facebook, twitter, instagram, etc.
    account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='connected')
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'platform', 'account_id')
    
    def __str__(self):
        return f"{self.platform} connection for {self.user.email}"

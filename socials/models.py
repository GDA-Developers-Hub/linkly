# socials/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class APIUsageLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50, choices=[
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube')
    ])
    endpoint = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    response_time = models.FloatField()

    class Meta:
        verbose_name = 'API Usage Log'
        verbose_name_plural = 'API Usage Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.platform} - {self.timestamp}"

class APIQuota(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    limit = models.IntegerField()
    used = models.IntegerField(default=0)
    reset_at = models.DateTimeField()

    class Meta:
        verbose_name = 'API Quota'
        verbose_name_plural = 'API Quotas'
        unique_together = ['user', 'platform']

    def __str__(self):
        return f"{self.user.email} - {self.platform} Quota"

class ScheduledPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    hashtags = models.TextField(blank=True)
    scheduled_time = models.DateTimeField()
    is_draft = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Platform flags
    post_to_instagram = models.BooleanField(default=False)
    post_to_facebook = models.BooleanField(default=False)
    post_to_twitter = models.BooleanField(default=False)
    post_to_linkedin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Scheduled Post'
        verbose_name_plural = 'Scheduled Posts'
        ordering = ['-scheduled_time']

    def __str__(self):
        return f"{self.user.email} - {self.scheduled_time}"

class PostMedia(models.Model):
    post = models.ForeignKey(ScheduledPost, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    media_type = models.CharField(max_length=10, choices=[
        ('image', 'Image'),
        ('video', 'Video')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Post Media'
        verbose_name_plural = 'Post Media'
        ordering = ['created_at']

    def __str__(self):
        return f"Media for {self.post}"
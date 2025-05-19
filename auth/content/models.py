from django.db import models
from django.conf import settings


class Caption(models.Model):
    PLATFORM_CHOICES = (
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
        ('all', 'All Platforms'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='captions')
    text = models.TextField()
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='all')
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Caption by {self.user.email} for {self.platform}"


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    post_count = models.PositiveIntegerField(default=0)
    growth_rate = models.FloatField(default=0.0)  # Growth rate in percentage
    engagement_rate = models.FloatField(default=0.0)  # Engagement rate in percentage
    is_trending = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class HashtagGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hashtag_groups')
    name = models.CharField(max_length=100)
    hashtags = models.ManyToManyField(Hashtag, related_name='groups')
    platform = models.CharField(max_length=20, default='instagram')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'name')
    
    def __str__(self):
        return f"{self.name} by {self.user.email}"


class Media(models.Model):
    TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='media/')
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.media_type} uploaded by {self.user.email}"

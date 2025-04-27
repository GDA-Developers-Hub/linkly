from django.db import models
from django.conf import settings
from platforms.models import PlatformAccount


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    )
    
    TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('link', 'Link'),
        ('carousel', 'Carousel'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    
    # Scheduling info
    scheduled_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Platform specific fields
    platforms = models.ManyToManyField(PlatformAccount, through='PostPlatform', related_name='posts')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post by {self.user.email} ({self.status})"


class PostPlatform(models.Model):
    """Junction model between Post and PlatformAccount with platform-specific data"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_platforms')
    platform_account = models.ForeignKey(PlatformAccount, on_delete=models.CASCADE, related_name='post_platforms')
    
    # Platform-specific content (can override the main content)
    custom_content = models.TextField(blank=True)
    
    # Publishing info
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    platform_post_id = models.CharField(max_length=255, blank=True)
    platform_post_url = models.URLField(blank=True)
    error_message = models.TextField(blank=True)
    
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('post', 'platform_account')
    
    def __str__(self):
        return f"{self.post} on {self.platform_account.platform.name}"


class PostMedia(models.Model):
    """Media attached to posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='post_media/')
    order = models.PositiveSmallIntegerField(default=0)
    
    # For carousel posts with text overlay
    caption = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Media {self.id} for {self.post}"


class PostMetrics(models.Model):
    """Metrics for posts across platforms"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='metrics')
    platform_post = models.ForeignKey(PostPlatform, on_delete=models.CASCADE, related_name='metrics')
    
    # Engagement metrics
    impressions = models.PositiveIntegerField(default=0)
    reach = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Metrics for {self.post} on {self.platform_post.platform_account.platform.name}"

from django.db import models
from django.conf import settings
from allauth.socialaccount.models import SocialApp, SocialAccount
from cloudinary.models import CloudinaryField


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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts'
    )
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')

    scheduled_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    platforms = models.ManyToManyField(
        SocialApp, through='PostPlatform', related_name='posts'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user} ({self.status})"


class PostPlatform(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_platforms')
    social_app = models.ForeignKey(SocialApp, on_delete=models.CASCADE, related_name='post_platforms')

    # Use SocialAccount to know which user account will publish
    social_account = models.ForeignKey(
        SocialAccount, on_delete=models.CASCADE, related_name='post_platforms',
        null=True, blank=True,
        help_text="User's linked social account to use for publishing"
    )

    custom_content = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    platform_post_id = models.CharField(max_length=255, blank=True)
    platform_post_url = models.URLField(blank=True)
    error_message = models.TextField(blank=True)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'social_app')

    def __str__(self):
        return f"{self.post} on {self.social_app.provider}"


class PostMedia(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    )
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media')
    file = CloudinaryField('media', folder='post_media', resource_type='auto')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    order = models.PositiveSmallIntegerField(default=0)

    caption = models.TextField(blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    duration = models.FloatField(null=True, blank=True, help_text='Duration in seconds for video/audio')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_media_type_display()} {self.id} for {self.post}"
        
    def get_url(self):
        """Return the Cloudinary URL for the media"""
        return self.file.url if self.file else None


class PostMetrics(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='metrics')
    platform_post = models.ForeignKey(PostPlatform, on_delete=models.CASCADE, related_name='metrics')

    impressions = models.PositiveIntegerField(default=0)
    reach = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metrics for {self.post} on {self.platform_post.social_app.provider}"

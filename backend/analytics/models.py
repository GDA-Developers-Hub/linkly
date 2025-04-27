from django.db import models
from django.conf import settings
from platforms.models import PlatformAccount


class AccountMetrics(models.Model):
    """Metrics for a platform account"""
    platform_account = models.ForeignKey(PlatformAccount, on_delete=models.CASCADE, related_name='metrics')
    
    # User metrics
    followers = models.PositiveIntegerField(default=0)
    following = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    impressions = models.PositiveIntegerField(default=0)
    reach = models.PositiveIntegerField(default=0)
    profile_views = models.PositiveIntegerField(default=0)
    
    # Growth metrics
    follower_growth = models.IntegerField(default=0)  # Can be negative
    engagement_rate = models.FloatField(default=0.0)  # Percentage
    
    # Timestamps
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('platform_account', 'date')
    
    def __str__(self):
        return f"Metrics for {self.platform_account} on {self.date}"


class AudienceInsight(models.Model):
    """Audience demographics and insights"""
    platform_account = models.ForeignKey(PlatformAccount, on_delete=models.CASCADE, related_name='audience_insights')
    
    # Demographics
    age_range = models.CharField(max_length=20)  # e.g., "18-24", "25-34"
    gender = models.CharField(max_length=20)  # e.g., "male", "female", "other"
    location = models.CharField(max_length=100)  # e.g., "United States", "New York"
    
    # Count/percentage
    value = models.FloatField()  # Percentage or count
    is_percentage = models.BooleanField(default=True)
    
    # Timestamps
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('platform_account', 'date', 'age_range', 'gender', 'location')
    
    def __str__(self):
        return f"Audience insight for {self.platform_account} on {self.date}"


class BestTimeToPost(models.Model):
    """Best time to post recommendations"""
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='best_times')
    platform_account = models.ForeignKey(PlatformAccount, on_delete=models.CASCADE, related_name='best_times')
    
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    hour = models.PositiveSmallIntegerField()  # 0-23
    engagement_score = models.FloatField()  # Higher is better
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('platform_account', 'day_of_week', 'hour')
        ordering = ['-engagement_score']
    
    def __str__(self):
        return f"Best time for {self.platform_account}: {self.day_of_week} at {self.hour}:00"

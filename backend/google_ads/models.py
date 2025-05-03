from django.db import models
from django.utils import timezone
from django.conf import settings

class GoogleAdsAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='google_ads_account')
    refresh_token = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512)
    token_expiry = models.DateTimeField()
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_token_expired(self):
        return self.token_expiry <= timezone.now()

    def __str__(self):
        return f"Google Ads Account for {self.user.email}"

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('PAUSED', 'Paused'),
        ('REMOVED', 'Removed'),
    ]

    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENABLED')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class AdGroup(models.Model):
    STATUS_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('PAUSED', 'Paused'),
        ('REMOVED', 'Removed'),
    ]

    TYPE_CHOICES = [
        ('SEARCH', 'Search'),
        ('DISPLAY', 'Display'),
        ('VIDEO', 'Video'),
        ('SHOPPING', 'Shopping'),
    ]

    id = models.CharField(max_length=255, primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='ad_groups')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENABLED')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.campaign.name})"

    class Meta:
        ordering = ['-created_at']

class Ad(models.Model):
    STATUS_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('PAUSED', 'Paused'),
        ('REMOVED', 'Removed'),
    ]

    id = models.CharField(max_length=255, primary_key=True)
    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE, related_name='ads')
    headline = models.CharField(max_length=255)
    description = models.TextField()
    final_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ENABLED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ['-created_at']

class PerformanceReport(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='performance_reports')
    date = models.DateField()
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['campaign', 'date']
        ordering = ['-date']

    @property
    def ctr(self):
        return (self.clicks / self.impressions * 100) if self.impressions > 0 else 0

    @property
    def cpc(self):
        return (self.cost / self.clicks) if self.clicks > 0 else 0

class KeywordMetrics(models.Model):
    MATCH_TYPE_CHOICES = [
        ('EXACT', 'Exact'),
        ('PHRASE', 'Phrase'),
        ('BROAD', 'Broad'),
    ]

    ad_group = models.ForeignKey(AdGroup, on_delete=models.CASCADE, related_name='keyword_metrics')
    keyword = models.CharField(max_length=255)
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES)
    date = models.DateField()
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['ad_group', 'keyword', 'match_type', 'date']
        ordering = ['-date', '-impressions']

    @property
    def ctr(self):
        return (self.clicks / self.impressions * 100) if self.impressions > 0 else 0

    @property
    def cpc(self):
        return (self.cost / self.clicks) if self.clicks > 0 else 0 
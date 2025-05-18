"""
URL patterns for all custom Django Allauth providers.
"""
from django.urls import path, include

# Import URL patterns from each provider
urlpatterns = [
    # TikTok provider URLs
    path('tiktok/', include('social_platforms.providers.tiktok.urls')),
    
    # YouTube provider URLs
    path('youtube/', include('social_platforms.providers.youtube.urls')),
    
    # Threads provider URLs
    path('threads/', include('social_platforms.providers.threads.urls')),
    
    # Pinterest provider URLs
    path('pinterest/', include('social_platforms.providers.pinterest.urls')),
    
    # Google Ads provider URLs (renamed to googleads)
    path('googleads/', include('social_platforms.providers.googleads.urls')),
]

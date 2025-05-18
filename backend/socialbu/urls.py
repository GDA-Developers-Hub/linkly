from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
import sys
import os
# Import directly from social_platforms.allauth_views instead
from social_platforms.allauth_views import SocialAuthInitView

def debug_view(request):
    """A simple view that returns debugging information."""
    data = {
        'debug': True,
        'python_version': sys.version,
        'environment': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
        'static_root': os.environ.get('STATIC_ROOT', 'Not set'),
        'database_url': os.environ.get('DATABASE_URL', 'Not set').replace('postgres:', '****:'),
        'python_path': sys.path,
    }
    return JsonResponse(data)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/content/', include('content.urls')),
    path('api/platforms/', include('platforms.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/social_platforms/', include('social_platforms.urls')),  # Social platforms within API namespace
    
    # Django Allauth URLs
    path('accounts/', include('allauth.urls')),
    
    # Custom Allauth providers
    path('accounts/socialaccount/providers/', include('social_platforms.providers.urls')),
    
    path('debug/', debug_view, name='debug'),
    
    # Use Django Allauth for OAuth callbacks instead of the custom callback view
    path('auth/init', SocialAuthInitView.as_view(), name='oauth_init'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

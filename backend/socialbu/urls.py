from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/content/', include('content.urls')),
    path('api/platforms/', include('platforms.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/', include('socialbu_proxy.urls')),  # Added the new app URLs
    
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

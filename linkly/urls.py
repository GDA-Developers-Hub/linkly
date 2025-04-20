from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

def health_check(request):
    return HttpResponse("OK", status=200)

schema_view = get_schema_view(
    openapi.Info(
        title="Linkly API",
        default_version='v1',
        description="""
# Linkly API Documentation

Linkly is a comprehensive social media integration platform that allows users to manage multiple social media accounts, schedule posts, analyze performance, and more.

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Rate Limiting
- Free Trial: 100 requests/hour
- Basic Plan: 1,000 requests/hour
- Pro Plan: 5,000 requests/hour
- Enterprise Plan: Unlimited

## Features
1. **User Management**
   - Registration and Authentication
   - Two-Factor Authentication
   - Profile Management
   - Subscription Management

2. **Social Media Integration**
   - Connect Multiple Platforms
   - OAuth2 Authentication
   - Business Account Integration
   - Account Management

3. **Content Management**
   - Post Scheduling
   - Media Upload
   - Content Calendar
   - Bulk Scheduling

4. **Analytics**
   - Performance Metrics
   - Engagement Analytics
   - Audience Insights
   - Custom Reports

5. **Team Collaboration**
   - Role-based Access
   - Team Member Management
   - Activity Logging
   - Shared Calendar

## Error Handling
Errors are returned in the following format:
```json
{
    "error": "Error type",
    "message": "Detailed error message",
    "code": "error_code"
}
```

## Support
For API support, please contact:
- Email: api-support@linkly.com
- Documentation: https://docs.linkly.com
- Status Page: https://status.linkly.com
""",
        terms_of_service="https://www.linkly.com/terms/",
        contact=openapi.Contact(
            name="API Support",
            url="https://www.linkly.com/support",
            email="api-support@linkly.com"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
        x_logo={
            "url": "https://www.linkly.com/logo.png",
            "backgroundColor": "#FFFFFF",
            "altText": "Linkly Logo"
        },
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('users/', include('users.urls')),
        path('socials/', include('socials.urls')),
    ],
)

urlpatterns = [
    path('', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('socials/', include('socials.urls')),
    
    # Swagger documentation URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = 'Linkly Administration'
admin.site.site_title = 'Linkly Admin Portal'
admin.site.index_title = 'Welcome to Linkly Admin Portal' 
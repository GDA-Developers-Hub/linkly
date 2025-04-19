# Developer Documentation

## Architecture Overview

Linkly is built with a Django backend and uses several key components:

- **Django REST Framework**: For building the REST API
- **PostgreSQL**: Primary database
- **Redis**: For caching and Celery task queue
- **Celery**: For background tasks and scheduled jobs
- **Stripe**: Payment processing
- **JWT**: Authentication
- **Swagger/OpenAPI**: API documentation

## Project Structure

```
linkly/
├── backend/             # Django project settings
├── users/              # User management and authentication
│   ├── models.py       # User and social account models
│   ├── views.py        # Authentication and user views
│   ├── serializers.py  # API serializers
│   ├── services/       # Business logic
│   │   ├── oauth.py    # OAuth URL generation
│   │   └── social.py   # Social account connection
│   └── urls.py         # API endpoints
├── social/             # Social media integration
├── subscriptions/      # Subscription and payment handling
├── analytics/          # Analytics and reporting
├── static/             # Static files
├── templates/          # HTML templates
└── tests/              # Test suite
```

## Development Setup

1. **Clone and Setup**
```bash
git clone https://github.com/GDA-Developers-Hub/linkly.git
cd linkly
python -m venv env
source env/bin/activate  # Linux/Mac
.\env\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Create PostgreSQL database
createdb linkly

# Run migrations
python manage.py migrate
```

3. **Create Test Data**
```bash
# Load subscription plans
python manage.py loaddata subscription_plans

# Create test user
python manage.py createsuperuser
```

## Social Authentication Implementation

### OAuth Flow Architecture

The social authentication system uses a unified approach for handling multiple platforms. Here's how it works:

1. **OAuth Initialization**
   ```python
   @api_view(['GET'])
   @permission_classes([IsAuthenticated])
   def init_oauth(request):
       """
       Unified OAuth initialization for all platforms.
       Query params:
       - platform: The social platform (google, facebook, etc.)
       - business: Boolean for business account access
       - redirect_uri: Optional custom redirect URI
       """
       platform = request.query_params.get('platform')
       business = request.query_params.get('business', 'false').lower() == 'true'
       redirect_uri = request.query_params.get('redirect_uri')
       # Returns platform-specific authorization URL
   ```

2. **Platform-Specific Callbacks**
   ```python
   @api_view(['GET'])
   @permission_classes([IsAuthenticated])
   def google_auth_callback(request):
       """Handle Google OAuth callback"""
       code = request.query_params.get('code')
       # Exchange code for tokens
   ```

3. **Account Connection**
   ```python
   def connect_social_account(user, platform, tokens, is_business=False):
       """
       Connect social account to user profile.
       - Stores OAuth tokens
       - Syncs profile information
       - Sets up token refresh if supported
       """
   ```

### Database Schema

```python
class User(AbstractUser):
    # Social account fields
    google_account = JSONField(null=True)
    facebook_account = JSONField(null=True)
    linkedin_account = JSONField(null=True)
    twitter_account = JSONField(null=True)
    instagram_account = JSONField(null=True)
    tiktok_account = JSONField(null=True)
    telegram_account = JSONField(null=True)
```

### OAuth URL Generation

The `oauth_utils.py` module contains platform-specific URL generators:

```python
def get_oauth_url(platform, business=False, redirect_uri=None):
    """
    Generate OAuth URL for specified platform.
    
    Args:
        platform (str): Social media platform
        business (bool): Request business account access
        redirect_uri (str): Optional custom redirect URI
    
    Returns:
        str: Authorization URL
    """
    settings = get_oauth_settings(platform)
    
    scopes = settings['scopes']
    if business:
        scopes.extend(settings['business_scopes'])
        
    params = {
        'client_id': settings['client_id'],
        'redirect_uri': redirect_uri or settings['redirect_uri'],
        'scope': ' '.join(scopes),
        'response_type': 'code',
        'state': generate_state_token()
    }
    
    return f"{settings['auth_url']}?{urlencode(params)}"
```

### Token Management

1. **Token Storage**
   - Tokens are encrypted before storage
   - Refresh tokens are handled automatically
   - Token rotation is implemented where supported

2. **Token Refresh**
   ```python
   def refresh_oauth_token(user, platform):
       """
       Refresh OAuth access token if expired.
       Implements platform-specific refresh logic.
       """
   ```

### Error Handling

Custom exceptions for OAuth-related errors:

```python
class OAuthError(Exception):
    """Base exception for OAuth errors"""
    pass

class TokenExchangeError(OAuthError):
    """Error during code-to-token exchange"""
    pass

class ProfileFetchError(OAuthError):
    """Error fetching user profile"""
    pass

class TokenRefreshError(OAuthError):
    """Error refreshing OAuth token"""
    pass
```

### Testing

1. **Unit Tests**
   ```python
   class OAuthTests(TestCase):
       def test_oauth_initialization(self):
           """Test OAuth URL generation"""
           response = self.client.get('/api/auth/init/', {'platform': 'google'})
           self.assertEqual(response.status_code, 200)
           self.assertIn('auth_url', response.data)

       def test_oauth_callback(self):
           """Test OAuth callback handling"""
           response = self.client.get('/api/auth/google/callback/', {'code': 'test_code'})
           self.assertEqual(response.status_code, 200)
   ```

2. **Integration Tests**
   ```python
   class SocialIntegrationTests(TestCase):
       def test_google_connection(self):
           """Test complete Google OAuth flow"""
           # Initialize OAuth
           init_response = self.client.get('/api/auth/init/', {'platform': 'google'})
           # Mock OAuth callback
           callback_response = self.client.get('/api/auth/google/callback/', {'code': 'test_code'})
           # Verify connection
           self.assertTrue(self.user.google_account is not None)
   ```

### Security Considerations

1. **Token Security**
   - Access tokens are encrypted at rest
   - Refresh tokens use additional encryption
   - Token rotation is implemented where supported

2. **State Validation**
   ```python
   def validate_oauth_state(request_state, stored_state):
       """
       Validate OAuth state parameter to prevent CSRF.
       Implements time-based expiration and one-time use.
       """
   ```

3. **Scope Management**
   - Minimal scope requests by default
   - Business scopes require subscription check
   - Scope elevation requires re-authentication

### Rate Limiting

```python
@method_decorator(ratelimit(key='user', rate='5/m', method=['GET']), name='get')
def init_oauth(request):
    """Rate limited to 5 requests per minute per user"""
```

### Monitoring

1. **OAuth Metrics**
   - Connection success/failure rates
   - Token refresh success/failure rates
   - API quota usage per platform

2. **Logging**
   ```python
   logger = logging.getLogger('oauth')
   logger.info('OAuth initialized', extra={
       'platform': platform,
       'user_id': user.id,
       'business': business
   })
   ```

### Webhook Handling

```python
def handle_oauth_webhook(request, platform):
    """
    Handle platform-specific OAuth webhooks.
    - Token revocation
    - Account disconnection
    - Permission changes
    """
```

## Code Style Guidelines

We follow PEP 8 with some modifications:

- Line length: 100 characters
- Use double quotes for strings
- Use trailing commas in multi-line structures

### Code Formatting

```bash
# Install development tools
pip install black isort flake8

# Format code
black .
isort .

# Check style
flake8
```

## API Development

### Adding New Endpoints

1. Create serializer in `serializers.py`:
```python
from rest_framework import serializers

class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'google_business_connected',
            'facebook_business_connected',
            'linkedin_business_connected',
            'twitter_business_connected',
            'instagram_business_connected',
            'tiktok_business_connected',
            'telegram_business_connected'
        ]
```

2. Create view in `views.py`:
```python
from rest_framework import viewsets

class SocialAccountViewSet(viewsets.ModelViewSet):
    serializer_class = SocialAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
```

3. Add URL in `urls.py`:
```python
path('social-accounts/', 
     SocialAccountViewSet.as_view({'get': 'list', 'post': 'create'}))
```

### API Documentation

Use Swagger decorators for documentation:

```python
@swagger_auto_schema(
    operation_description="Connect a social media account",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'code': openapi.Schema(type=openapi.TYPE_STRING),
            'redirect_uri': openapi.Schema(type=openapi.TYPE_STRING),
            'business': openapi.Schema(type=openapi.TYPE_BOOLEAN)
        },
        required=['code']
    ),
    responses={
        200: "{'status': 'success'}",
        400: "{'error': 'error message'}",
        401: "{'detail': 'Authentication credentials not provided'}"
    }
)
def connect_social_account(request, platform):
    # Implementation
    pass
```

## Security Best Practices

1. **Token Storage**
   - Never store tokens in plaintext
   - Use encryption for sensitive data
   - Implement token rotation

2. **OAuth Security**
   - Validate redirect URIs
   - Use state parameter
   - Implement PKCE for mobile apps

3. **API Security**
   - Rate limiting
   - Input validation
   - CORS configuration

4. **Error Handling**
   - Don't expose sensitive info in errors
   - Log security events
   - Monitor failed attempts

## Deployment

1. **Environment Setup**
```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=linkly.settings.production

# Configure SSL
python manage.py check --deploy
```

2. **Database Migration**
```bash
python manage.py migrate --noinput
```

3. **Static Files**
```bash
python manage.py collectstatic --noinput
```

4. **Security Headers**
```python
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Monitoring

1. **Error Tracking**
   - Sentry integration
   - Custom error logging

2. **Performance Monitoring**
   - New Relic
   - Django Debug Toolbar

3. **Security Monitoring**
   - Failed login attempts
   - API usage patterns
   - Token revocations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests
4. Implement changes
5. Run linters and tests
6. Submit pull request

### Pull Request Guidelines

- Follow code style
- Include tests
- Update documentation
- One feature per PR
- Clear commit messages

## Support

- Technical Documentation: [docs.linkly.com/developers](https://docs.linkly.com/developers)
- API Reference: [docs.linkly.com/api](https://docs.linkly.com/api)
- Developer Discord: [discord.gg/linkly-dev](https://discord.gg/linkly-dev) 
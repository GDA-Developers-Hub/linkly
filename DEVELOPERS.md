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

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test tests.test_subscriptions

# Run with coverage
coverage run manage.py test
coverage report
```

### Writing Tests

- Place tests in the `tests/` directory
- Follow the `test_*.py` naming convention
- Use descriptive test method names
- Include docstrings explaining test purpose

Example:
```python
from django.test import TestCase
from users.models import User

class SubscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_free_trial_creation(self):
        """Test that free trial is created when user registers"""
        self.assertTrue(self.user.has_used_trial)
        self.assertIsNotNone(self.user.current_subscription)
```

## API Development

### Adding New Endpoints

1. Create serializer in `serializers.py`:
```python
from rest_framework import serializers

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'description']
```

2. Create view in `views.py`:
```python
from rest_framework import viewsets

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated]
```

3. Add URL in `urls.py`:
```python
path('my-models/', MyModelViewSet.as_view({'get': 'list', 'post': 'create'}))
```

### API Documentation

Use Swagger decorators for documentation:

```python
@swagger_auto_schema(
    operation_description="Create a new resource",
    request_body=MyModelSerializer,
    responses={
        201: MyModelSerializer,
        400: "Bad Request",
        403: "Forbidden"
    }
)
def create(self, request):
    # Implementation
    pass
```

## Subscription System

### Adding New Plan Features

1. Update `SubscriptionPlan` model:
```python
class SubscriptionPlan(models.Model):
    # Add new feature flag
    has_new_feature = models.BooleanField(default=False)
```

2. Update middleware checks:
```python
class SubscriptionRestrictionMiddleware:
    def __call__(self, request):
        # Add feature check
        if url_name == 'new-feature' and not request.user.can_use_feature('new_feature'):
            return JsonResponse({
                'error': 'Feature not available',
                'code': 'feature_not_available'
            }, status=402)
```

### Payment Integration

1. Create Stripe product and price:
```python
stripe.Product.create(
    name="New Plan",
    description="Description"
)

stripe.Price.create(
    product="prod_xxx",
    unit_amount=2900,  # $29.00
    currency="usd",
    recurring={"interval": "month"}
)
```

2. Update subscription views:
```python
def create_checkout_session(request):
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_xxx',
            'quantity': 1,
        }],
        mode='subscription',
        success_url=domain + '/success',
        cancel_url=domain + '/cancel',
    )
    return JsonResponse({'id': checkout_session.id})
```

## Social Media Integration

### Adding New Platform

1. Add model fields:
```python
class User(AbstractUser):
    new_platform_id = models.CharField(max_length=255, blank=True)
    new_platform_token = models.TextField(blank=True)
```

2. Create OAuth views:
```python
@api_view(['POST'])
def connect_new_platform(request):
    code = request.data.get('code')
    # Implement OAuth flow
    # Save tokens
    return Response({'status': 'success'})
```

3. Update platform limits check:
```python
def check_platform_limits(user):
    connected_platforms = sum([
        bool(user.facebook_id),
        bool(user.instagram_id),
        bool(user.new_platform_id),  # Add new platform
    ])
    return connected_platforms <= user.get_platform_limit()
```

## Deployment

### Production Setup

1. Update settings:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
```

2. Configure web server (Nginx):
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

3. Set up Gunicorn:
```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables

Required production variables:
```plaintext
DATABASE_URL=postgres://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379
STRIPE_LIVE_SECRET_KEY=sk_live_xxx
STRIPE_LIVE_WEBHOOK_SECRET=whsec_xxx
```

## Contributing

1. Create feature branch:
```bash
git checkout -b feature/new-feature
```

2. Make changes and test:
```bash
python manage.py test
```

3. Update documentation:
- Add API endpoints to Swagger
- Update README if needed
- Add migration notes if needed

4. Create pull request:
- Use descriptive title
- Include testing steps
- Link related issues

## Troubleshooting

### Common Issues

1. **Migration Conflicts**
```bash
python manage.py migrate --fake
python manage.py migrate
```

2. **Stripe Webhook Errors**
- Check webhook signature
- Verify endpoint URL
- Check event types

3. **Social Auth Issues**
- Verify OAuth credentials
- Check callback URLs
- Monitor token expiration

### Debug Tools

1. Django Debug Toolbar:
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

2. Logging:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
``` 
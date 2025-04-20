# Linkly Developer Documentation

## 🏗️ Architecture Overview

### Tech Stack
- **Backend**: Django + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT + OAuth2
- **API Documentation**: Swagger/OpenAPI

### Project Structure
```
linkly/
├── users/                 # User management app
│   ├── models/           # Database models
│   ├── views/            # API views
│   ├── serializers/      # DRF serializers
│   ├── services/         # Business logic
│   └── utils/            # Helper functions
├── social/               # Social media integration
│   ├── models/          
│   ├── services/         # Platform-specific services
│   └── utils/            # OAuth utilities
├── subscriptions/        # Subscription management
│   ├── models/
│   ├── services/         # Stripe integration
│   └── webhooks/         # Payment webhooks
└── core/                 # Core functionality
    ├── middleware/
    ├── permissions/
    └── utils/
```

## 🔄 OAuth2 Implementation

### Flow Overview
1. User initiates OAuth flow via `/auth/init/`
2. Backend generates PKCE challenge and state
3. User is redirected to provider
4. Provider redirects back with code
5. Backend exchanges code for tokens
6. Tokens are stored securely

### PKCE Implementation
```python
def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge
```

### State Parameter
```python
def generate_oauth_state():
    return secrets.token_urlsafe(32)
```

### Token Storage
- Access tokens stored in Redis
- Refresh tokens in encrypted database field
- Session data with short TTL

## 🔐 Security Guidelines

### Authentication
1. JWT tokens with short expiry
2. Refresh token rotation
3. 2FA implementation
4. Rate limiting on auth endpoints

### Data Protection
1. Input validation on all endpoints
2. SQL injection prevention
3. XSS protection
4. CSRF protection

### OAuth Security
1. PKCE for all providers
2. State parameter validation
3. Secure token storage
4. Scope validation

## 📡 API Development

### Endpoint Structure
```
/api/
├── auth/                  # Authentication
│   ├── register/
│   ├── login/
│   ├── refresh/
│   └── validate/
├── social/                # Social Media
│   ├── connect/
│   ├── disconnect/
│   └── status/
└── subscription/          # Subscriptions
    ├── plans/
    ├── checkout/
    └── webhook/
```

### Response Format
```json
{
    "status": "success",
    "data": {},
    "message": "Operation successful",
    "meta": {
        "pagination": {},
        "filters": {}
    }
}
```

### Error Format
```json
{
    "status": "error",
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    }
}
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/                 # Unit tests
├── integration/          # Integration tests
└── e2e/                 # End-to-end tests
```

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test tests.unit.test_oauth

# Run with coverage
coverage run manage.py test
coverage report
```

### Mock OAuth Providers
```python
@mock.patch('social.services.oauth.GoogleOAuth')
def test_google_oauth_flow(mock_oauth):
    mock_oauth.return_value.get_authorization_url.return_value = 'http://mock-url'
    # Test implementation
```

## 🔄 Git Workflow

### Branch Naming
- `feature/`: New features
- `bugfix/`: Bug fixes
- `hotfix/`: Critical fixes
- `release/`: Release preparation

### Commit Messages
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Pull Request Process
1. Create feature branch
2. Write tests
3. Update documentation
4. Create PR with description
5. Pass CI/CD checks
6. Get code review
7. Merge to development

## 📦 Deployment

### Prerequisites
- Docker
- Docker Compose
- AWS CLI (for production)

### Local Development
```bash
# Build containers
docker-compose build

# Start services
docker-compose up

# Run migrations
docker-compose exec web python manage.py migrate
```

### Production Deployment
```bash
# Build production image
docker build -t linkly:latest .

# Push to registry
docker push registry.example.com/linkly:latest

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## 🔍 Monitoring

### Logging
- Use `logging` module
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracking

### Metrics
- Request latency
- Error rates
- OAuth success rates
- Subscription conversions
- API usage by endpoint

### Health Checks
- Database connectivity
- Redis availability
- OAuth provider status
- Stripe API status

## 🎯 Performance Optimization

### Caching Strategy
1. Redis for:
   - OAuth tokens
   - User sessions
   - API responses
   - Rate limiting

2. Cache invalidation:
   - Time-based expiry
   - Event-based invalidation
   - Soft invalidation

### Database Optimization
1. Indexing strategy
2. Query optimization
3. Connection pooling
4. Read replicas

### API Optimization
1. Pagination
2. Field filtering
3. Response compression
4. Background tasks

## 📚 Documentation Guidelines

### Code Documentation
```python
def function_name(param1: str, param2: int) -> Dict[str, Any]:
    """
    Short description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Dict containing processed data

    Raises:
        ValueError: If params are invalid
    """
```

### API Documentation
- Use OpenAPI/Swagger
- Include examples
- Document error responses
- Maintain changelog

## 🤝 Contributing Guidelines

1. Fork the repository
2. Create feature branch
3. Write tests
4. Update documentation
5. Submit pull request

### Code Style
- Follow PEP 8
- Use type hints
- Maximum line length: 88
- Use Black for formatting

### Review Process
1. Automated checks
2. Code review
3. Documentation review
4. Security review
5. Performance review

## 📞 Support

### Developer Resources
- API Documentation: `/api/docs/`
- Technical Docs: `/docs/`
- Developer Discord: [Join](https://discord.gg/yourdiscord)

### Getting Help
- GitHub Issues
- Developer Forum
- Stack Overflow Tag
- Email Support 
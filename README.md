# Linkly - Social Media Management Platform

Linkly is a comprehensive social media management platform that allows users to manage multiple social media accounts, schedule posts, analyze performance, and generate AI-powered content.

## Features

- **Multi-Platform Support**
  - Facebook (Personal & Business Pages)
  - Instagram (Personal & Business)
  - Twitter/X
  - LinkedIn (Personal & Company)
  - YouTube (Personal & Brand)
  - TikTok (Personal & Business)
  - Telegram (Personal & Channels)

- **Subscription Plans**
  - Free Trial (10 days)
  - Starter Plan
  - Pro Plan
  - Enterprise Plan

- **Core Features**
  - Social Media Account Management
  - Post Scheduling
  - Analytics Dashboard
  - AI Caption Generation
  - Team Collaboration
  - Content Calendar
  - Competitor Analysis
  - API Access

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- PostgreSQL 13+
- Redis (for Celery)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/GDA-Developers-Hub/linkly.git
cd linkly
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
.\env\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create initial subscription plans:
```bash
python manage.py loaddata subscription_plans
```

7. Run the development server:
```bash
python manage.py runserver
```

## Social Authentication Setup

### OAuth Configuration

Linkly uses a unified OAuth initialization endpoint for all social media platforms. The endpoint is:

```
GET /api/auth/init/?platform={platform}&business={boolean}&redirect_uri={uri}
```

Supported platforms:
- google
- facebook
- linkedin
- twitter
- instagram
- tiktok
- telegram

Parameters:
- `platform`: (required) The social media platform to connect with
- `business`: (optional) Set to true for business account access
- `redirect_uri`: (optional) Custom OAuth redirect URI

Example:
```bash
# Initialize Google OAuth
curl -X GET "https://api.linkly.com/api/auth/init/?platform=google"

# Initialize Facebook Business OAuth
curl -X GET "https://api.linkly.com/api/auth/init/?platform=facebook&business=true"
```

### Platform-Specific Setup

#### Google
1. Go to Google Cloud Console
2. Create a new project or select existing one
3. Enable Google+ API and YouTube Data API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `https://your-domain.com/api/auth/google/callback/`

#### Facebook
1. Go to Facebook Developers
2. Create a new app or select existing one
3. Add Facebook Login product
4. Configure OAuth settings
5. Add redirect URI: `https://your-domain.com/api/auth/facebook/callback/`

[Similar sections for other platforms...]

### Environment Variables

```env
# OAuth Client IDs
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
TIKTOK_CLIENT_ID=your_tiktok_client_id
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OAuth Redirect URIs (optional, defaults to domain-based URIs)
OAUTH_REDIRECT_BASE_URL=https://your-domain.com/api/auth
```

### Testing OAuth Integration

1. Use the Postman collection in `docs/postman/` for testing
2. Initialize OAuth flow:
   ```bash
   # Get authorization URL
   curl -X GET "https://api.linkly.com/api/auth/init/?platform=google"
   ```
3. Complete OAuth flow in browser
4. Handle callback at `/api/auth/{platform}/callback/`

## API Documentation

Our API is documented using Swagger/OpenAPI. Access the interactive documentation at:

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

### Rate Limiting

API endpoints are rate-limited based on the subscription plan:
- Free Trial: 100 requests/hour
- Starter: 1,000 requests/hour
- Pro: 5,000 requests/hour
- Enterprise: Custom limits

### Error Handling

The API returns standard HTTP status codes and JSON error responses:

```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```

Common error codes:
- `authentication_failed`: Invalid or missing authentication
- `permission_denied`: Insufficient permissions
- `subscription_required`: Feature requires subscription
- `rate_limit_exceeded`: Too many requests
- `validation_error`: Invalid input data
- `platform_error`: Social media platform API error

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

See [DEVELOPERS.md](DEVELOPERS.md) for detailed development guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [docs.linkly.com](https://docs.linkly.com)
- Email: support@linkly.com
- Discord: [Join our community](https://discord.gg/linkly) 
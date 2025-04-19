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

### Environment Variables

Required environment variables in `.env`:

```plaintext
# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=linkly
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Stripe Integration
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Social Media API Keys
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
TIKTOK_CLIENT_KEY=your_tiktok_client_key
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Environment Variable Details

#### Django Settings
- `SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Set to True for development, False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed host domains

#### Database Configuration
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: Database user with access to the database
- `DB_PASSWORD`: Database user password
- `DB_HOST`: Database host address (localhost for development)
- `DB_PORT`: Database port (default: 5432)

#### Redis Configuration
- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)

#### Email Settings
- `EMAIL_HOST`: SMTP server host (e.g., smtp.gmail.com)
- `EMAIL_PORT`: SMTP server port (usually 587 for TLS)
- `EMAIL_USE_TLS`: Whether to use TLS for email (True/False)
- `EMAIL_HOST_USER`: Email address for sending emails
- `EMAIL_HOST_PASSWORD`: App-specific password for email account

#### Stripe Integration
- `STRIPE_PUBLIC_KEY`: Stripe publishable key (starts with 'pk_')
- `STRIPE_SECRET_KEY`: Stripe secret key (starts with 'sk_')
- `STRIPE_WEBHOOK_SECRET`: Webhook signing secret (starts with 'whsec_')

#### Social Media API Keys
Each social media platform requires specific API keys:

**Facebook/Instagram**
- `FACEBOOK_APP_ID`: Facebook application ID
- `FACEBOOK_APP_SECRET`: Facebook application secret
- `INSTAGRAM_CLIENT_ID`: Instagram application client ID
- `INSTAGRAM_CLIENT_SECRET`: Instagram application client secret

**Twitter/X**
- `TWITTER_API_KEY`: Twitter API key
- `TWITTER_API_SECRET`: Twitter API secret
- `TWITTER_BEARER_TOKEN`: Twitter API bearer token

**LinkedIn**
- `LINKEDIN_CLIENT_ID`: LinkedIn application client ID
- `LINKEDIN_CLIENT_SECRET`: LinkedIn application client secret

**YouTube**
- `YOUTUBE_API_KEY`: YouTube Data API key

**TikTok**
- `TIKTOK_CLIENT_KEY`: TikTok application client key
- `TIKTOK_CLIENT_SECRET`: TikTok application client secret

**Telegram**
- `TELEGRAM_BOT_TOKEN`: Telegram bot API token

#### AI Service
- `OPENAI_API_KEY`: OpenAI API key for AI caption generation

### Development Tools
- `DJANGO_SETTINGS_MODULE`: Python path to settings module
- `PYTHONPATH`: Python path including project root
- `NODE_ENV`: Node.js environment (development/production)

### Security Considerations

1. Never commit `.env` file to version control
2. Use strong, unique passwords for all credentials
3. Rotate API keys periodically
4. Use environment-specific keys (development vs production)
5. Monitor API usage and set up alerts for unusual activity

### Obtaining API Keys

1. **Stripe**: Sign up at [stripe.com](https://stripe.com) and get API keys from dashboard
2. **Social Media Platforms**:
   - Facebook/Instagram: [Meta for Developers](https://developers.facebook.com)
   - Twitter: [Twitter Developer Portal](https://developer.twitter.com)
   - LinkedIn: [LinkedIn Developers](https://developer.linkedin.com)
   - YouTube: [Google Cloud Console](https://console.cloud.google.com)
   - TikTok: [TikTok for Developers](https://developers.tiktok.com)
   - Telegram: [Telegram Bot Father](https://t.me/botfather)
3. **OpenAI**: Sign up at [OpenAI Platform](https://platform.openai.com)

## Stripe Configuration

To enable the subscription system, you'll need to set up Stripe:

1. Create a [Stripe account](https://stripe.com) if you don't have one
2. Get your API keys from the Stripe Dashboard:
   - Find your publishable key and secret key in the [API keys section](https://dashboard.stripe.com/apikeys)
   - Create a webhook endpoint in Stripe Dashboard and note the signing secret
3. Update your `.env` file with your Stripe credentials:
   ```
   STRIPE_PUBLIC_KEY=pk_test_your_publishable_key
   STRIPE_SECRET_KEY=sk_test_your_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret
   ```
4. Configure your webhook endpoint in Stripe Dashboard to point to:
   ```
   https://your-domain.com/api/users/subscriptions/webhook/
   ```
   Subscribe to the following events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

> Note: For development, you can use [Stripe CLI](https://stripe.com/docs/stripe-cli) to test webhooks locally.

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

API requests are rate-limited based on the subscription plan:
- Free Trial: 100 requests/hour
- Starter: 1,000 requests/hour
- Pro: 5,000 requests/hour
- Enterprise: 20,000 requests/hour

## Subscription Features

### Free Trial
- 3 social accounts
- 50 AI captions/month
- Basic analytics
- 10-day trial period

### Starter Plan ($9/month)
- 5 social accounts
- 100 AI captions/month
- Basic analytics
- Content calendar

### Pro Plan ($29/month)
- 15 social accounts
- 500 AI captions/month
- Advanced analytics
- Team collaboration (up to 3 members)
- Competitor analysis
- Content calendar

### Enterprise Plan ($99/month)
- Unlimited social accounts
- 2000 AI captions/month
- Advanced analytics
- Unlimited team members
- Competitor analysis
- API access
- Dedicated support
- Custom features

## Contributing

Please read [DEVELOPERS.md](DEVELOPERS.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
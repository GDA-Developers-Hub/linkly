# Linkly - Social Media Management Platform

Linkly is a comprehensive social media management platform that allows users to connect and manage multiple social media accounts in one place. With support for major platforms including Google, Facebook, Twitter, LinkedIn, Instagram, TikTok, and Telegram.

## 🌟 Features

### Social Media Integration
- Connect multiple social media accounts
- OAuth2 authentication for secure access
- Support for business accounts and API features
- Real-time sync of social media metrics

### Account Management
- Secure user authentication with JWT
- Two-factor authentication (2FA)
- Profile management
- Password recovery

### Subscription System
- Flexible subscription plans
- Free trial period
- Stripe integration for payments
- Business features access control

### Security
- OAuth2 with PKCE support
- State parameter verification
- Secure token storage
- Rate limiting
- Input validation

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Redis
- PostgreSQL
- Node.js 14+ (for frontend)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkly.git
cd linkly
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
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

6. Start the development server:
```bash
python manage.py runserver
```

### Environment Variables

Required environment variables:

```plaintext
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# OAuth2 Credentials
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_CLIENT_ID=your-facebook-client-id
FACEBOOK_CLIENT_SECRET=your-facebook-client-secret
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret
TIKTOK_CLIENT_ID=your-tiktok-client-id
TIKTOK_CLIENT_SECRET=your-tiktok-client-secret
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Stripe
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

## 📚 API Documentation

API documentation is available at `/api/docs/` when running the server. It includes:
- Authentication endpoints
- Social media integration
- Profile management
- Subscription handling

## 🔒 Security Features

1. **OAuth2 Security**
   - PKCE for public clients
   - State parameter verification
   - Secure token storage
   - Automatic token refresh

2. **User Security**
   - JWT authentication
   - Two-factor authentication
   - Password validation
   - Rate limiting

3. **Data Security**
   - Input validation
   - HTTPS enforcement
   - CORS configuration
   - SQL injection protection

## 🤝 Contributing

Please read [DEVELOPERS.md](DEVELOPERS.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Technical Documentation: [/docs](./docs)
- API Reference: `/api/docs/`
- Developer Discord: [Join](https://discord.gg/yourdiscord)
- Email Support: support@linkly.com

## ✨ Acknowledgments

- All the amazing social platforms that provide APIs
- The open-source community
- Our contributors and users 
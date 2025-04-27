# SocialBu Backend API

This is the Django backend for SocialBu, a social media management platform.

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (for Celery)

### Installation

1. Clone the repository
\`\`\`bash
git clone https://github.com/yourusername/socialbu.git
cd socialbu/backend
\`\`\`

2. Create a virtual environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Set up environment variables
\`\`\`bash
cp .env.example .env
# Edit .env file with your configuration
\`\`\`

5. Run migrations
\`\`\`bash
python manage.py migrate
\`\`\`

6. Create a superuser
\`\`\`bash
python manage.py createsuperuser
\`\`\`

7. Start the development server
\`\`\`bash
python manage.py runserver
\`\`\`

## API Endpoints

### Authentication
- `POST /api/users/register/` - Register a new user
- `POST /api/users/login/` - Login a user
- `POST /api/users/logout/` - Logout a user
- `POST /api/users/token/refresh/` - Refresh JWT token
- `GET/PATCH /api/users/profile/` - Get and update user profile
- `POST /api/users/change-password/` - Change user password

### Subscriptions
- `GET /api/subscriptions/plans/` - Get available subscription plans
- `GET/POST /api/subscriptions/subscription/` - Get or create subscriptions
- `POST /api/subscriptions/subscription/cancel/` - Cancel subscription
- `GET /api/subscriptions/invoices/` - Get user invoices

### Content Generation
- `POST /api/content/generate-caption/` - Generate captions with AI
- `GET/POST /api/content/saved-captions/` - Save and retrieve captions
- `POST /api/content/generate-hashtags/` - Generate hashtags with AI
- `GET /api/content/hashtags/trending/` - Get trending hashtags
- `GET /api/content/hashtags/related/` - Get related hashtags
- `GET/POST /api/content/hashtag-groups/` - Save and retrieve hashtag groups
- `GET/POST /api/content/media/` - Upload and manage media files

### Platform Connections
- `GET /api/platforms/list/` - List available platforms
- `GET/POST /api/platforms/accounts/` - List and connect platform accounts
- `GET/PATCH/DELETE /api/platforms/accounts/<id>/` - Manage a platform account
- `POST /api/platforms/accounts/<id>/disconnect/` - Disconnect a platform
- `GET /api/platforms/auth/<platform>/login/` - Auth URLs for platforms
- `GET /api/platforms/auth/callback/` - OAuth callback handler

### Posts
- `GET/POST /api/posts/` - List and create posts
- `GET/PATCH/DELETE /api/posts/<id>/` - Manage a post
- `POST /api/posts/<id>/media/` - Upload media to a post
- `POST /api/posts/<id>/schedule/` - Schedule a post
- `POST /api/posts/<id>/publish/` - Publish a post
- `POST /api/posts/<id>/cancel/` - Cancel a scheduled post
- `GET /api/posts/metrics/` - Get post performance metrics

### Analytics
- `GET /api/analytics/metrics/` - Get account metrics
- `GET /api/analytics/audience/` - Get audience insights
- `GET /api/analytics/best-times/` - Get best times to post
- `GET /api/analytics/summary/` - Get account summary

## Development

### Running tests
\`\`\`bash
python manage.py test
\`\`\`

### Database Reset
\`\`\`bash
python manage.py flush
\`\`\`

### Creating database migrations
\`\`\`bash
python manage.py makemigrations

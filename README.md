# Linkly - Social Media Management Platform

![Linkly Logo](frontend/public/linkly-logo.png)

## Overview

Linkly is a comprehensive social media management platform that allows businesses and individuals to connect, manage, and post to multiple social media platforms from a single dashboard. With its custom OAuth2 integration, Linkly provides direct connections to popular social networks without relying on third-party services like SocialBu.

## Key Features

- **Custom OAuth2 Social Platform Integration**: Direct connections to Facebook, Instagram, Twitter, LinkedIn, YouTube, TikTok, Pinterest, and Google
- **Unified Dashboard**: Monitor all your social media metrics in one place
- **Cross-Platform Publishing**: Create and schedule posts for multiple platforms simultaneously
- **Analytics & Reporting**: Track engagement, followers, and performance across all connected platforms
- **Google Ads Integration**: Seamlessly manage your social media and paid advertising campaigns together
- **Modern UI/UX**: Sleek, responsive interface with an intuitive design

## Use Cases

### Digital Marketing Agency

**Scenario**: A digital marketing agency manages social media accounts for 20+ clients across different industries.

**How Linkly Helps**:
- Connect all client accounts under a single dashboard
- Schedule and manage content calendars for each client
- Generate performance reports for client meetings
- Track engagement metrics to optimize content strategy
- Manage permissions for team members working on different accounts

### E-commerce Business

**Scenario**: An online store wants to increase social media presence and drive sales through multiple channels.

**How Linkly Helps**:
- Synchronize product listings across all social platforms
- Schedule promotional posts for sales and new product launches
- Track which platforms drive the most traffic and conversions
- Integrate with Google Ads to retarget visitors
- Monitor engagement to identify the most effective content types

### Content Creator

**Scenario**: An influencer needs to maintain consistent posting across multiple platforms while tracking growth.

**How Linkly Helps**:
- Post content to multiple platforms with a single click
- Schedule content for optimal posting times
- Track follower growth and engagement across all platforms
- Identify top-performing content types for each platform
- Monitor comment sentiment and audience demographics

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- PostgreSQL
- Redis (for background tasks)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-org/linkly.git
cd linkly
```

2. **Set up the backend**

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up the database
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

3. **Set up the frontend**

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

4. **Configure OAuth credentials**

- Log in to the Django admin interface at `http://localhost:8000/admin/`
- Navigate to Social Platforms and add the necessary OAuth credentials for each platform

## Architecture

Linkly uses a modern tech stack:

- **Frontend**: Next.js with TypeScript, Tailwind CSS, and Shadcn UI components
- **Backend**: Django with Django REST Framework for the API
- **Authentication**: JWT-based authentication
- **Database**: PostgreSQL for data storage
- **Background Tasks**: Celery with Redis for task queue management

## Documentation

For detailed technical documentation and developer guidelines, see [DEV.md](DEV.md).

## License

[MIT License](LICENSE)

## Support

For support, please open an issue in the GitHub repository or contact support@linkly.com.
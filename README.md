# Linkly - Social Media Management Platform

![Linkly Logo](frontend/public/linkly-logo.png)

## Overview

Linkly is a comprehensive social media management platform that allows businesses and individuals to connect, manage, and post to multiple social media platforms from a single dashboard. With its Django Allauth-based OAuth2 integration, Linkly provides direct connections to popular social networks without relying on third-party services.

## Key Features

- **Django Allauth OAuth2 Integration**: Standardized connections to Facebook, Instagram, Twitter, LinkedIn, YouTube, TikTok, Threads, Pinterest, and Google Ads
- **Unified Dashboard**: Monitor all your social media metrics in one place
- **Cross-Platform Publishing**: Create and schedule posts for multiple platforms simultaneously
- **Analytics & Reporting**: Track engagement, followers, and performance across all connected platforms
- **Google Ads Integration**: Seamlessly manage your social media and paid advertising campaigns together
- **Modern UI/UX**: Sleek, responsive interface with an intuitive design

## Authentication Flow

Linkly uses Django Allauth for standardized OAuth2 authentication with all supported social platforms. This provides a consistent and secure authentication experience while simplifying the codebase.

### OAuth2 Flow Architecture

1. **Initialization**: User clicks "Connect" for a social platform in the frontend
2. **Authorization Request**: System generates an OAuth URL with proper scopes and state parameter
3. **Platform Authorization**: User is redirected to the platform's authorization page
4. **Callback Processing**: After user consent, the platform redirects to our callback URL with a code
5. **Token Exchange**: Backend exchanges the code for access and refresh tokens
6. **Profile Data Retrieval**: System fetches user profile and account data from the platform's API
7. **Account Creation**: A UserSocialAccount record is created/updated with the token and profile information

### API Endpoints

#### OAuth Authentication

- **POST /api/social_platforms/api/oauth/connect/**
  - Initiates OAuth flow for a specified platform
  - Request Body: `{"platform": "platform_id"}` (e.g., facebook, twitter, youtube)
  - Response: `{"authorization_url": "https://...", "state": "random_state_token"}`

- **GET /auth/init**
  - Alternative endpoint for OAuth initialization
  - Query Params: `?platform=platform_id`
  - Response: Redirect to platform's authorization page

- **GET /api/social_platforms/api/accounts/**
  - Retrieves all connected social accounts for the authenticated user
  - Response: List of social accounts with platform, profile data, and status

- **POST /api/social_platforms/api/accounts/disconnect/**
  - Disconnects a social account
  - Request Body: `{"account_id": 123}`
  - Response: Success message

#### Legacy Compatibility Endpoints

- **GET /api/social_platforms/oauth/init/{platform}/**
  - Legacy OAuth initialization endpoint (maintained for backward compatibility)

- **GET /api/social_platforms/accounts/**
  - Legacy endpoint for listing connected accounts

### Supported Platforms

Each platform has a custom implementation with specific data retrieval:

- **YouTube**: Channel data, videos, and analytics
- **Threads**: Profile information via Instagram/Meta API
- **Pinterest**: Boards, pins, and account statistics
- **Google Ads**: Ads accounts, analytics properties, and campaign data
- **Facebook**: Pages, posts, and insights
- **Instagram**: Profile, media, and engagement metrics
- **Twitter**: Profile, tweets, and follower data
- **LinkedIn**: Profile, company pages, and posts
- **TikTok**: Profile, videos, and engagement metrics

### Configuration

Platform credentials are managed through the Django admin interface:

1. Navigate to Admin > Social Account > Social applications
2. Add a new social application for each platform
3. Configure the client ID, secret, and associated site

## Technical Architecture

### Backend (Django)

- **Django Allauth**: Core authentication framework for social login
- **Custom Providers**: Extended Allauth with custom providers for platforms not supported out-of-the-box
- **Session-Based State Management**: Secure OAuth state handling using Django sessions
- **Adapter Pattern**: Custom adapters to integrate Allauth with existing UserSocialAccount model
- **Platform-Specific APIs**: Custom implementations for each platform's unique data structure

### Frontend (React/Next.js)

- **Platform-Specific Components**: Custom React components for each social platform
  - `youtube-connect.tsx`: YouTube channel display and management
  - `threads-connect.tsx`: Threads/Instagram connection flow
  - `pinterest-connect.tsx`: Pinterest boards and pins visualization
  - `google-ads-connect.tsx`: Google Ads account management
- **API Client**: Service layer with graceful fallback between new and legacy endpoints
- **State Management**: React context for managing connection state

### Implementation Details

#### YouTube Integration

The YouTube integration uses the Google OAuth2 flow with specialized scopes for YouTube data access. It retrieves detailed channel information, including subscriber count, video metrics, and engagement statistics. The frontend component displays channel thumbnails, subscriber counts, and recent video performance.

#### Threads Integration

The Threads integration leverages the Meta/Instagram API, as Threads currently shares authentication with Instagram. It manages profile connections and retrieves user data through the Instagram Graph API. The frontend component displays profile information and recent thread engagement metrics.

#### Pinterest Integration

The Pinterest integration uses OAuth2 with specialized error handling and detailed board/pin retrieval. The frontend displays boards, pins, and engagement metrics in a visually appealing grid layout that matches Pinterest's aesthetic.

#### Google Ads Integration

The Google Ads provider was renamed from `google_ads` to `googleads` to avoid application label conflicts. It features comprehensive token handling and account data retrieval, displaying Ads accounts and analytics properties in the frontend component.

### Backward Compatibility

The system maintains backward compatibility through:

1. **Parallel Endpoints**: Legacy API endpoints continue to function alongside new ones
2. **Frontend Fallback**: API client attempts new endpoints first, falls back to legacy endpoints if needed
3. **Data Structure Consistency**: Same output format maintained across both implementations

This ensures a smooth transition from the original implementation to the new Django Allauth-based system.

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
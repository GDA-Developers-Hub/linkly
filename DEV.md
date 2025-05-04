# Linkly Developer Documentation

This document provides comprehensive technical information for developers working on the Linkly platform. It covers architecture, implementation details, APIs, and development workflows.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Frontend](#frontend)
- [Backend](#backend)
- [Social Platforms Integration](#social-platforms-integration)
- [API Documentation](#api-documentation)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)
- [Extending Linkly](#extending-linkly)
- [Google Ads Integration](#google-ads-integration)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

Linkly is built with a modern, decoupled architecture:

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   Frontend    │◄────►│ Backend APIs  │◄────►│  Databases &  │
│  (Next.js)    │      │   (Django)    │      │    Services   │
└───────────────┘      └───────────────┘      └───────────────┘
                              ▲
                              │
                              ▼
                      ┌───────────────┐
                      │  Social Media │
                      │   Platforms   │
                      └───────────────┘
```

- **Frontend**: Next.js application with TypeScript and Shadcn UI components
- **Backend**: Django REST Framework APIs with JWT authentication
- **Database**: PostgreSQL for storing user data, social accounts, posts, and analytics
- **Social Integration**: Custom OAuth2 implementations for direct connections to social platforms

## Frontend

### Tech Stack

- **Next.js**: React framework with server-side rendering and routing
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS framework
- **Shadcn UI**: Accessible UI components built with Radix UI and TailwindCSS
- **SWR**: React hooks for data fetching
- **Zustand**: State management

### Directory Structure

```
frontend/
├── app/                  # Next.js app directory
│   ├── (auth)/           # Authentication pages
│   ├── dashboard/        # Dashboard pages
│   │   ├── platform-connect/  # Social platform connection page
│   │   └── ...
│   └── ...
├── components/           # Reusable React components
├── contexts/             # React context providers
├── lib/                  # Utility functions and services
├── public/               # Static assets
└── styles/               # Global styles
```

### Key Components

#### OAuth Flow Integration

The `platform-connect/page.tsx` component handles the OAuth flow for connecting social media accounts:

```typescript
// Example of OAuth initialization
const connectAccount = async (platform: string) => {
  try {
    // First try our custom OAuth
    const token = localStorage.getItem('accessToken');
    if (token) {
      // Call our custom OAuth API
      const response = await customSocialPlatformsAPI.initOAuthFlow(platform);
      if (response.authorization_url) {
        // Open popup for OAuth flow
        const width = 600;
        const height = 700;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;
        const popup = window.open(
          response.authorization_url,
          'Connect ' + platform,
          `width=${width},height=${height},top=${top},left=${left}`
        );
        
        // Listen for messages from the popup
        window.addEventListener('message', handleOAuthCallback);
        return;
      }
    }
    
    // Fallback to SocialBu if custom implementation fails
    await socialBuAPI.connectAccount(platform);
    fetchAccounts();
  } catch (error) {
    console.error("Error connecting account:", error);
    toast({
      title: "Connection Error",
      description: "Failed to connect your account. Please try again.",
      variant: "destructive",
    });
  }
};
```

#### API Client

The frontend interacts with the backend through API client classes:

```typescript
// Example API client for social platforms
class SocialPlatformsAPI {
  private apiBase: string;
  
  constructor() {
    this.apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  
  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
    };
  }
  
  async initOAuthFlow(platform: string) {
    const response = await fetch(`${this.apiBase}/api/social-platforms/api/oauth/init/${platform}/`, {
      method: 'GET',
      headers: this.getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Failed to initialize OAuth flow');
    }
    
    return await response.json();
  }
  
  async getAccounts() {
    const response = await fetch(`${this.apiBase}/api/social-platforms/api/accounts/`, {
      headers: this.getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch accounts');
    }
    
    return await response.json();
  }
  
  // Other methods for posting, disconnecting accounts, etc.
}
```

## Backend

### Tech Stack

- **Django**: Web framework
- **Django REST Framework**: API toolkit
- **SimpleJWT**: JWT authentication
- **PostgreSQL**: Relational database
- **Celery**: Task queue (for background jobs)
- **Redis**: Cache and message broker

### Directory Structure

```
backend/
├── core/               # Core settings and base configurations
├── social_platforms/   # Custom social media integration
│   ├── admin.py        # Admin interface for social platforms
│   ├── models.py       # Data models
│   ├── serializers.py  # API serializers
│   ├── services.py     # Business logic and OAuth services
│   ├── urls.py         # API routes
│   └── views.py        # API views
├── socialbu/           # Legacy SocialBu integration
└── users/              # User management
```

### Database Models

The `social_platforms` app defines the following key models:

#### SocialPlatform

```python
class SocialPlatform(models.Model):
    """Configuration for a social media platform"""
    name = models.CharField(max_length=50)
    platform_id = models.CharField(max_length=50, unique=True)
    auth_url = models.URLField()
    token_url = models.URLField()
    api_base_url = models.URLField()
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scope = models.TextField(blank=True)
    extra_params = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Other fields and methods...
```

#### UserSocialAccount

```python
class UserSocialAccount(models.Model):
    """User's connection to a social platform"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    account_name = models.CharField(max_length=255)
    account_username = models.CharField(max_length=255, blank=True)
    account_email = models.EmailField(blank=True, null=True)
    account_avatar = models.URLField(blank=True, null=True)
    account_type = models.CharField(max_length=50, blank=True)
    is_primary = models.BooleanField(default=False)
    extra_data = models.JSONField(default=dict, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)
    
    # Other fields and methods...
```

## Social Platforms Integration

### OAuth Implementation

Linkly implements a custom OAuth2 integration for all supported social platforms. The core of this implementation is in the `services.py` file:

```python
class OAuthManager:
    """Base class for OAuth authentication flow"""
    
    def __init__(self, platform):
        self.platform = platform
        self.client_id = platform.client_id
        self.client_secret = platform.client_secret
        self.auth_url = platform.auth_url
        self.token_url = platform.token_url
        self.api_base_url = platform.api_base_url
        self.scope = platform.scope
        self.extra_params = platform.extra_params
    
    def get_authorization_url(self, redirect_uri, state=None):
        """Generate authorization URL for OAuth flow"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
        }
        
        if self.scope:
            params['scope'] = self.scope
            
        if state:
            params['state'] = state
            
        # Add any platform-specific parameters
        params.update(self.extra_params)
        
        # Construct the auth URL with parameters
        url_parts = list(urllib.parse.urlparse(self.auth_url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        
        return urllib.parse.urlunparse(url_parts)
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Failed to exchange code for token: {response.text}")
        
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """Refresh the access token using the refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        return response.json()
    
    def get_user_profile(self, access_token):
        """Get user profile information - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement this method")
```

Platform-specific implementations inherit from this base class:

```python
class FacebookOAuthManager(OAuthManager):
    """Facebook-specific OAuth implementation"""
    
    def get_user_profile(self, access_token):
        """Get Facebook user profile"""
        profile_url = f"{self.api_base_url}/me?fields=id,name,email,picture&access_token={access_token}"
        response = requests.get(profile_url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
        
        profile_data = response.json()
        
        return {
            'id': profile_data.get('id'),
            'name': profile_data.get('name'),
            'email': profile_data.get('email'),
            'avatar': profile_data.get('picture', {}).get('data', {}).get('url')
        }
```

### Factory Function

A factory function is used to get the appropriate OAuth manager for each platform:

```python
def get_oauth_manager(platform_id):
    """Get the appropriate OAuth manager for the platform"""
    try:
        platform = SocialPlatform.objects.get(platform_id=platform_id, is_active=True)
    except SocialPlatform.DoesNotExist:
        raise ValueError(f"Platform {platform_id} not found or not active")
    
    manager_map = {
        'facebook': FacebookOAuthManager,
        'instagram': InstagramOAuthManager,
        'twitter': TwitterOAuthManager,
        'linkedin': LinkedInOAuthManager,
        'youtube': YouTubeOAuthManager,
        'tiktok': TikTokOAuthManager,
        'pinterest': PinterestOAuthManager,
        'google': GoogleOAuthManager,
    }
    
    manager_class = manager_map.get(platform_id)
    if not manager_class:
        raise ValueError(f"No OAuth manager implemented for {platform_id}")
    
    return manager_class(platform)
```

## API Documentation

### Social Platforms API

#### List Available Platforms

```
GET /api/social-platforms/api/platforms/
```

Response:
```json
[
  {
    "id": 1,
    "name": "Facebook",
    "platform_id": "facebook",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Twitter",
    "platform_id": "twitter",
    "is_active": true
  }
]
```

#### Initialize OAuth Flow

```
GET /api/social-platforms/api/oauth/init/{platform}/
```

Response:
```json
{
  "authorization_url": "https://facebook.com/oauth/authorize?...",
  "state": "abc123"
}
```

#### List Connected Accounts

```
GET /api/social-platforms/api/accounts/
```

Response:
```json
[
  {
    "id": 1,
    "platform": "facebook",
    "account_name": "John Doe",
    "account_username": "johndoe",
    "account_avatar": "https://example.com/avatar.jpg",
    "account_type": "personal",
    "is_primary": true,
    "connected_at": "2023-01-01T00:00:00Z"
  }
]
```

#### Disconnect Account

```
DELETE /api/social-platforms/api/accounts/{id}/
```

#### Create Post

```
POST /api/social-platforms/api/posts/
```

Request:
```json
{
  "account_ids": [1, 2],
  "content": "Hello world!",
  "media_urls": ["https://example.com/image.jpg"],
  "scheduled_at": "2023-01-01T12:00:00Z" 
}
```

Response:
```json
{
  "id": 1,
  "status": "scheduled",
  "accounts": ["Facebook", "Twitter"],
  "scheduled_at": "2023-01-01T12:00:00Z"
}
```

## Development Workflow

### Setting Up the Development Environment

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

# Create a .env file with necessary environment variables
cp .env.example .env
# Edit .env with your configuration

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

# Create a .env.local file
cp .env.example .env.local
# Edit .env.local with your configuration

# Run the development server
npm run dev
```

### Working with OAuth Platforms

To set up a new social platform in the admin:

1. Go to `http://localhost:8000/admin/`
2. Navigate to Social Platforms > Add Social Platform
3. Fill in the required details:
   - Name: Display name (e.g., "Facebook")
   - Platform ID: Unique identifier (e.g., "facebook")
   - Auth URL: The OAuth authorization endpoint
   - Token URL: The OAuth token endpoint
   - API Base URL: The base URL for API requests
   - Client ID: Your app's client ID from the platform
   - Client Secret: Your app's client secret
   - Scope: Required permissions (space-separated)
   - Extra Params: Any additional OAuth parameters in JSON format

### Code Style and Best Practices

- **Frontend**: Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **Backend**: Follow [PEP 8](https://peps.python.org/pep-0008/) and [Django's coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- Use TypeScript for type safety in the frontend
- Write tests for new features
- Document API endpoints and complex functions

## Testing

### Frontend Testing

```bash
# Run frontend tests
cd frontend
npm test
```

### Backend Testing

```bash
# Run backend tests
cd backend
python manage.py test
```

## Deployment

### Production Deployment Checklist

1. **Backend preparation**
   - Set `DEBUG=False` in settings
   - Configure secure `SECRET_KEY`
   - Set up proper database credentials
   - Configure CORS settings
   - Set up proper HTTPS with SSL certificates

2. **Frontend preparation**
   - Configure production API URLs
   - Optimize assets with `npm run build`
   - Set up proper environment variables

3. **Database migration**
   - Backup existing database
   - Apply migrations
   - Verify data integrity

4. **Server configuration**
   - Set up Nginx or Apache as a reverse proxy
   - Configure Gunicorn for Django
   - Set up proper firewall rules
   - Configure monitoring and logging

## Extending Linkly

### Adding a New Social Platform

1. **Create a platform-specific OAuth manager**

```python
# In social_platforms/services.py
class NewPlatformOAuthManager(OAuthManager):
    """New platform OAuth implementation"""
    
    def get_user_profile(self, access_token):
        """Get user profile from the new platform"""
        profile_url = f"{self.api_base_url}/users/me?access_token={access_token}"
        response = requests.get(profile_url)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
        
        profile_data = response.json()
        
        return {
            'id': profile_data.get('id'),
            'name': profile_data.get('display_name'),
            'email': profile_data.get('email'),
            'avatar': profile_data.get('avatar_url')
        }
```

2. **Update the manager map in the factory function**

```python
manager_map = {
    'facebook': FacebookOAuthManager,
    # ... existing platforms
    'new_platform': NewPlatformOAuthManager,
}
```

3. **Add the new platform in the admin interface**

4. **Update the frontend to display the new platform**

```typescript
// In platform-connect/page.tsx
const availablePlatforms = [
  // ... existing platforms
  {
    name: "New Platform",
    platform: "new_platform",
    description: "Connect your New Platform account",
    popular: false,
  },
];

// Add the platform icon in platformConfig
const platformConfig = {
  // ... existing platforms
  new_platform: { 
    icon: NewPlatformIcon, 
    color: "#FF0000",
    gradient: "from-red-600 to-red-500"
  },
};
```

### Creating a New Feature Module

1. **Plan the API endpoints**
2. **Create necessary models in the backend**
3. **Implement API views and serializers**
4. **Update URLs configuration**
5. **Create frontend components**
6. **Implement frontend state management**
7. **Write tests**
8. **Document the new feature**

## Google Ads Integration

Linkly incorporates a fully-featured Google Ads integration that allows users to manage advertising campaigns alongside their social media content. This section details the implementation and usage of the Google Ads features.

### Credentials Configuration

To set up the Google Ads integration, you need to configure the following credentials:

1. **OAuth2 Credentials**:
   - Client ID and Client Secret from the Google Cloud Console
   - Redirect URI for OAuth callbacks
   - Appropriate scopes: `https://www.googleapis.com/auth/adwords`

2. **Google Ads API Configuration**:
   - Developer Token: `_NzVJdsDLG5LTIrScLADqg` (for testing environments only)
   - Manager Account ID (if applicable)

### Backend Implementation

The Google Ads integration is implemented in two main components:

1. **Google Ads Models** (`google_ads/models.py`):
   - `GoogleAdsAccount`: Links a user to their Google Ads account credentials
   - `Campaign`: Stores campaign information and settings
   - `AdGroup`: Organizes ads into logical groups within campaigns
   - `Ad`: Represents individual advertisements
   - `PerformanceReport`: Stores campaign performance metrics
   - `KeywordMetrics`: Tracks keyword performance data

2. **Google Ads Service** (`services/google-ads/src/services/GoogleAdsService.ts`):
   - Handles communication with the Google Ads API
   - Manages authentication with refresh tokens
   - Provides methods for CRUD operations on campaigns, ad groups, and ads
   - Fetches performance metrics and reports

### Frontend Integration

The frontend interacts with the Google Ads API through several components:

1. **API Client** (`frontend/services/googleAdsService.ts`):
   - Makes HTTP requests to the backend API
   - Handles data formatting and error management
   - Provides typed responses for type safety

2. **UI Components**:
   - `GoogleAdsAuth.tsx`: Handles the OAuth connection flow
   - `GoogleAdsOverview.tsx`: Displays a dashboard with key metrics
   - `CampaignsList.tsx`: Shows active campaigns and their status
   - `PerformanceMetrics.tsx`: Visualizes important performance indicators
   - `KeywordPerformance.tsx`: Displays keyword analytics

3. **Custom Hooks**:
   - `useGoogleAdsData.ts`: Fetches and manages Google Ads data for components

### Data Flow

The complete data flow for the Google Ads integration is as follows:

1. **Authentication**:
   - User connects their Google account through OAuth2
   - Backend exchanges the authorization code for access and refresh tokens
   - Tokens are stored in the `GoogleAdsAccount` model

2. **Campaign Management**:
   - Frontend makes requests to the backend API
   - Backend uses the stored tokens to authenticate with the Google Ads API
   - The Google Ads API processes the request and returns data
   - Backend transforms and returns the formatted data to the frontend

3. **Data Visualization**:
   - Performance data is fetched periodically
   - Data is processed and transformed for visualization
   - UI components display the data in charts, tables, and summaries

### Example: Creating a Campaign

Here's how the system creates a new Google Ads campaign:

```typescript
// Frontend (Campaign creation request)
async function createCampaign(campaignData) {
  try {
    const result = await googleAdsService.post('/campaigns/', campaignData);
    return result;
  } catch (error) {
    console.error('Error creating campaign:', error);
    throw error;
  }
}

// Backend (Processing the request)
async createCampaign(campaign: Omit<Campaign, 'id'>): Promise<Campaign> {
  try {
    logger.info('Creating new campaign', { campaignName: campaign.name });
    const customer = this.client.Customer({
      customer_id: this.config.accountId,
    });

    const result = await customer.campaigns.create({
      name: campaign.name,
      status: campaign.status,
      campaign_budget: campaign.budget.toString(),
      start_date: campaign.startDate,
      end_date: campaign.endDate,
    });

    return {
      id: result.id!,
      ...campaign,
    };
  } catch (error) {
    logger.error('Error creating campaign', { error });
    throw error;
  }
}
```

### Integration with Social Media Data

The Google Ads integration connects with the social media features in the following ways:

1. **Unified Analytics**:
   - Combined dashboards show both paid and organic performance
   - Cross-channel attribution identifies the customer journey

2. **Coordinated Campaigns**:
   - Ads can be aligned with social media content
   - Consistent messaging across all channels

3. **Audience Targeting**:
   - Social media audience insights inform ad targeting
   - Custom audiences can be created based on social engagement

## Troubleshooting

### Common Issues

1. **OAuth Connection Failures**
   - Check if the platform is properly configured in the admin
   - Verify the client ID and secret
   - Ensure the redirect URI is correctly configured on the platform's developer dashboard
   - Check browser console for any CORS errors

2. **API Error Responses**
   - Verify JWT token validity
   - Check request formatting
   - Look for validation errors in the backend logs

3. **Database Migration Issues**
   - Create a backup before migrating
   - Run migrations with the `--plan` flag to preview changes
   - Check for dependency conflicts in models

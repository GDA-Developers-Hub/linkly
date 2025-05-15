# Social Platforms Integration with Django Allauth

This document provides an overview of how the social platforms integration has been restructured using Django Allauth for authentication.

## Overview

The integration uses Django Allauth as the foundation for OAuth authentication with various social platforms. All supported platforms have been integrated with Allauth's provider system, ensuring a consistent and reliable authentication flow.

## Supported Platforms

The following social platforms are now supported through Django Allauth:

- Facebook
- Instagram
- Twitter/X
- LinkedIn
- Google (General)
- YouTube
- TikTok
- Threads
- Pinterest
- Google Ads

## Architecture

The authentication flow is handled by Django Allauth, while our custom adapter bridges the gap between Allauth and our existing `UserSocialAccount` model. This ensures backward compatibility while leveraging Allauth's robust OAuth handling.

### Key Components

1. **Custom Providers**: For platforms not supported by Allauth out of the box (e.g., TikTok, Threads), we've implemented custom providers.
2. **Custom Adapter**: `CustomSocialAccountAdapter` maps Allauth's social accounts to our `UserSocialAccount` model.
3. **API Endpoints**: New API endpoints for a more streamlined OAuth flow.
4. **Initialization Utilities**: Helper functions to initialize OAuth flows for any platform.

## API Endpoints

### New Endpoints

- `POST /api/social_platforms/api/oauth/connect/`: Initialize OAuth flow for any platform
- `GET /api/social_platforms/api/accounts/`: List all connected social accounts
- `POST /api/social_platforms/api/accounts/disconnect/`: Disconnect a social account

### Legacy Endpoints (still supported)

- `/api/social_platforms/api/oauth/init/<str:platform>/`
- `/api/social_platforms/api/oauth/complete/<str:platform>/`
- `/api/social_platforms/api/accounts/list/`

## Implementation Details

### Custom Providers

Custom Allauth providers have been implemented for:
- TikTok
- YouTube
- Threads
- Pinterest
- Google Ads

Each provider includes:
1. Provider class (defines OAuth parameters)
2. OAuth2Adapter (handles the OAuth2 flow)
3. Views (login and callback)

### Token Management

Access tokens are stored in both Allauth's `SocialToken` model and our `UserSocialAccount` model, allowing for backward compatibility with existing code.

### Initialization

The system automatically initializes all social platforms and Allauth providers during application startup.

## Migration Notes

- No database migrations are needed as we maintain compatibility with existing models
- The frontend can use both the new and legacy endpoints during transition
- OAuth state is now handled by Allauth, removing the need for Redis-based state management

### File Structure Changes

- Original OAuth implementation files have been moved to the `deprecated/` directory
- A compatibility layer has been added to `services.py` to maintain backward compatibility
- New Allauth-based implementations are in `services_allauth.py` and the `providers/` directory
- Redis-based state management (`redis_store.py`) has been deprecated in favor of Django session-based state

## Configuration

Make sure the following environment variables are set for each platform:

```
FACEBOOK_CLIENT_ID
FACEBOOK_CLIENT_SECRET
INSTAGRAM_CLIENT_ID
INSTAGRAM_CLIENT_SECRET
TWITTER_CLIENT_ID
TWITTER_CLIENT_SECRET
LINKEDIN_CLIENT_ID
LINKEDIN_CLIENT_SECRET
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
TIKTOK_CLIENT_ID
TIKTOK_CLIENT_SECRET
PINTEREST_CLIENT_ID
PINTEREST_CLIENT_SECRET
```

## Testing

To test the new OAuth flow:

1. Use the `/api/social_platforms/api/oauth/connect/` endpoint with the platform name
2. Complete the OAuth flow on the provider's site
3. Check the connected accounts using `/api/social_platforms/api/accounts/`

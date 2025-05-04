# Linkly API Endpoints Documentation

This document provides comprehensive information about all API endpoints in the Linkly application, including request/response formats, required fields, authentication requirements, and expected behavior.

## Table of Contents

- [Authentication](#authentication)
- [Social Platforms API](#social-platforms-api)
- [Google Ads API](#google-ads-api)
- [Testing Guide](#testing-guide)

## Authentication

All API endpoints (except public endpoints) require authentication using JWT tokens.

### Headers

Include the following header in all authenticated requests:

```
Authorization: Bearer {access_token}
```

### Authentication Endpoints

#### Login

```
POST http://localhost:8000/api/auth/token/
```

Request:
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token

```
POST /api/auth/token/refresh/
```

Request:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Social Platforms API

### Available Platforms

#### List Available Platforms

Returns a list of available social media platforms configured in the system.

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
  },
  {
    "id": 3,
    "name": "Instagram",
    "platform_id": "instagram",
    "is_active": true
  }
]
```

### OAuth Flow

#### Initialize OAuth Flow

Initiates the OAuth flow for connecting a social media account.

```
GET /api/social-platforms/api/oauth/init/{platform}/
```

Path Parameters:
- `platform`: The platform ID (e.g., "facebook", "twitter", "instagram")

Response:
```json
{
  "authorization_url": "https://facebook.com/oauth/authorize?client_id=123456&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fsocial-platforms%2Foauth%2Fcallback%2F&response_type=code&state=abcdef123456",
  "state": "abcdef123456"
}
```

#### OAuth Callback

Handles the OAuth callback from social platforms. This endpoint is called by the social platform after user authorization.

```
GET /api/social-platforms/oauth/callback/
```

Query Parameters:
- `code`: The authorization code from the social platform
- `state`: The state parameter sent in the initial request
- `error`: (Optional) Error message if authorization failed
- `platform`: (Optional, if not included in state) The platform ID

Response:
```json
{
  "success": true,
  "message": "Successfully connected to Facebook",
  "account": {
    "id": 1,
    "platform": "facebook",
    "account_name": "John Doe",
    "account_username": "johndoe",
    "is_primary": false
  }
}
```

### User Social Accounts

#### List Connected Accounts

Returns a list of user's connected social media accounts.

```
GET /api/social-platforms/api/accounts/
```

Response:
```json
[
  {
    "id": 1,
    "platform": {
      "id": 1,
      "name": "Facebook",
      "platform_id": "facebook"
    },
    "account_id": "1234567890",
    "account_name": "John Doe",
    "account_username": "johndoe",
    "account_email": "john@example.com",
    "account_avatar": "https://example.com/avatar.jpg",
    "account_type": "personal",
    "is_primary": true,
    "connected_at": "2023-01-01T12:00:00Z",
    "last_used_at": "2023-01-02T12:00:00Z"
  }
]
```

#### Get Account Details

Returns details of a specific connected account.

```
GET /api/social-platforms/api/accounts/{id}/
```

Path Parameters:
- `id`: The ID of the connected account

Response:
```json
{
  "id": 1,
  "platform": {
    "id": 1,
    "name": "Facebook",
    "platform_id": "facebook"
  },
  "account_id": "1234567890",
  "account_name": "John Doe",
  "account_username": "johndoe",
  "account_email": "john@example.com",
  "account_avatar": "https://example.com/avatar.jpg",
  "account_type": "personal",
  "is_primary": true,
  "connected_at": "2023-01-01T12:00:00Z",
  "last_used_at": "2023-01-02T12:00:00Z",
  "token_expired": false
}
```

#### Set Primary Account

Sets a connected account as the primary account for its platform.

```
POST /api/social-platforms/api/accounts/{id}/set_primary/
```

Path Parameters:
- `id`: The ID of the connected account

Response:
```json
{
  "success": true,
  "message": "Account set as primary"
}
```

#### Refresh Token

Manually refreshes the access token for a connected account.

```
POST /api/social-platforms/api/accounts/{id}/refresh_token/
```

Path Parameters:
- `id`: The ID of the connected account

Response:
```json
{
  "success": true,
  "message": "Token refreshed successfully"
}
```

#### Disconnect Account

Disconnects a social media account.

```
DELETE /api/social-platforms/api/accounts/{id}/
```

Path Parameters:
- `id`: The ID of the connected account

Response:
```json
{
  "success": true,
  "message": "Account disconnected successfully"
}
```

### Social Media Posts

#### Create Post

Creates a new post on one or more social media platforms.

```
POST /api/social-platforms/api/posts/
```

Request:
```json
{
  "account_ids": [1, 2],
  "content": "Hello, world!",
  "media_urls": ["https://example.com/image.jpg"],
  "scheduled_at": "2023-01-01T12:00:00Z"
}
```

Response:
```json
{
  "id": 1,
  "accounts": [
    {
      "id": 1,
      "platform": "facebook",
      "status": "scheduled"
    },
    {
      "id": 2,
      "platform": "twitter",
      "status": "scheduled"
    }
  ],
  "content": "Hello, world!",
  "media_urls": ["https://example.com/image.jpg"],
  "scheduled_at": "2023-01-01T12:00:00Z",
  "created_at": "2022-12-31T12:00:00Z"
}
```

#### Get Posts

Returns a list of posts created by the user.

```
GET /api/social-platforms/api/posts/
```

Query Parameters:
- `status`: (Optional) Filter by status (scheduled, published, failed)
- `platform`: (Optional) Filter by platform ID
- `account_id`: (Optional) Filter by account ID
- `start_date`: (Optional) Filter by start date
- `end_date`: (Optional) Filter by end date

Response:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "accounts": [
        {
          "id": 1,
          "platform": "facebook",
          "status": "published",
          "post_id": "fb_post_123",
          "post_url": "https://facebook.com/posts/123"
        },
        {
          "id": 2,
          "platform": "twitter",
          "status": "published",
          "post_id": "tw_post_456",
          "post_url": "https://twitter.com/user/status/456"
        }
      ],
      "content": "Hello, world!",
      "media_urls": ["https://example.com/image.jpg"],
      "scheduled_at": "2023-01-01T12:00:00Z",
      "published_at": "2023-01-01T12:00:00Z",
      "created_at": "2022-12-31T12:00:00Z"
    }
  ]
}
```

#### Get Post Details

Returns details of a specific post.

```
GET /api/social-platforms/api/posts/{id}/
```

Path Parameters:
- `id`: The ID of the post

Response:
```json
{
  "id": 1,
  "accounts": [
    {
      "id": 1,
      "platform": "facebook",
      "status": "published",
      "post_id": "fb_post_123",
      "post_url": "https://facebook.com/posts/123",
      "metrics": {
        "likes": 10,
        "comments": 5,
        "shares": 2
      }
    },
    {
      "id": 2,
      "platform": "twitter",
      "status": "published",
      "post_id": "tw_post_456",
      "post_url": "https://twitter.com/user/status/456",
      "metrics": {
        "likes": 15,
        "retweets": 3,
        "replies": 2
      }
    }
  ],
  "content": "Hello, world!",
  "media_urls": ["https://example.com/image.jpg"],
  "scheduled_at": "2023-01-01T12:00:00Z",
  "published_at": "2023-01-01T12:00:00Z",
  "created_at": "2022-12-31T12:00:00Z"
}
```

#### Cancel Scheduled Post

Cancels a scheduled post that hasn't been published yet.

```
POST /api/social-platforms/api/posts/{id}/cancel/
```

Path Parameters:
- `id`: The ID of the post

Response:
```json
{
  "success": true,
  "message": "Post cancelled successfully"
}
```

## Google Ads API

### Authentication

#### Get Auth Status

Checks if the user has connected their Google Ads account.

```
GET /api/google-ads/account/
```

Response:
```json
{
  "connected": true,
  "account": {
    "customer_id": "123-456-7890",
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

#### Initialize OAuth Flow

Initiates the OAuth flow for connecting a Google Ads account.

```
GET /api/google-ads/auth/init/
```

Response:
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?client_id=123456&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fgoogle-ads%2Fauth%2Fcallback%2F&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fadwords&state=abcdef123456"
}
```

#### OAuth Callback

Handles the OAuth callback from Google.

```
GET /api/google-ads/auth/callback/
```

Query Parameters:
- `code`: The authorization code from Google
- `state`: The state parameter sent in the initial request
- `error`: (Optional) Error message if authorization failed

Response:
```json
{
  "success": true,
  "message": "Successfully connected to Google Ads"
}
```

#### Disconnect Account

Disconnects the Google Ads account.

```
POST /api/google-ads/account/disconnect/
```

Response:
```json
{
  "success": true,
  "message": "Google Ads account disconnected successfully"
}
```

### Campaigns

#### List Campaigns

Returns a list of campaigns from the connected Google Ads account.

```
GET /api/google-ads/campaigns/
```

Query Parameters:
- `status`: (Optional) Filter by status (ENABLED, PAUSED, REMOVED)
- `start_date`: (Optional) Filter by start date
- `end_date`: (Optional) Filter by end date

Response:
```json
[
  {
    "id": "12345678",
    "name": "Summer Sale Campaign",
    "status": "ENABLED",
    "budget": "100.00",
    "start_date": "2023-01-01",
    "end_date": "2023-01-31",
    "created_at": "2022-12-31T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

#### Get Campaign Details

Returns details of a specific campaign.

```
GET /api/google-ads/campaigns/{id}/
```

Path Parameters:
- `id`: The ID of the campaign

Response:
```json
{
  "id": "12345678",
  "name": "Summer Sale Campaign",
  "status": "ENABLED",
  "budget": "100.00",
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "created_at": "2022-12-31T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "ad_groups": [
    {
      "id": "87654321",
      "name": "Shoes Ad Group",
      "status": "ENABLED"
    }
  ],
  "performance": {
    "impressions": 1000,
    "clicks": 50,
    "cost": "25.00",
    "conversions": 5,
    "ctr": 5.0,
    "cpc": "0.50"
  }
}
```

#### Create Campaign

Creates a new campaign in the connected Google Ads account.

```
POST /api/google-ads/campaigns/
```

Request:
```json
{
  "name": "Winter Sale Campaign",
  "status": "ENABLED",
  "budget": "200.00",
  "start_date": "2023-02-01",
  "end_date": "2023-02-28"
}
```

Response:
```json
{
  "id": "87654321",
  "name": "Winter Sale Campaign",
  "status": "ENABLED",
  "budget": "200.00",
  "start_date": "2023-02-01",
  "end_date": "2023-02-28",
  "created_at": "2023-01-15T12:00:00Z",
  "updated_at": "2023-01-15T12:00:00Z"
}
```

#### Update Campaign

Updates an existing campaign.

```
PATCH /api/google-ads/campaigns/{id}/
```

Path Parameters:
- `id`: The ID of the campaign

Request:
```json
{
  "name": "Winter Super Sale Campaign",
  "status": "PAUSED",
  "budget": "300.00"
}
```

Response:
```json
{
  "id": "87654321",
  "name": "Winter Super Sale Campaign",
  "status": "PAUSED",
  "budget": "300.00",
  "start_date": "2023-02-01",
  "end_date": "2023-02-28",
  "created_at": "2023-01-15T12:00:00Z",
  "updated_at": "2023-01-16T12:00:00Z"
}
```

#### Get Campaign Performance

Returns performance metrics for a specific campaign.

```
GET /api/google-ads/campaigns/{id}/performance/
```

Path Parameters:
- `id`: The ID of the campaign

Query Parameters:
- `days`: (Optional) Number of days to include in the report (default: 30)

Response:
```json
[
  {
    "date": "2023-02-01",
    "impressions": 100,
    "clicks": 5,
    "cost": "2.50",
    "conversions": 1
  },
  {
    "date": "2023-02-02",
    "impressions": 150,
    "clicks": 7,
    "cost": "3.50",
    "conversions": 2
  }
]
```

### Ad Groups

#### List Ad Groups

Returns a list of ad groups from the connected Google Ads account.

```
GET /api/google-ads/ad-groups/
```

Query Parameters:
- `campaign_id`: (Optional) Filter by campaign ID
- `status`: (Optional) Filter by status (ENABLED, PAUSED, REMOVED)

Response:
```json
[
  {
    "id": "12345678",
    "campaign_id": "87654321",
    "name": "Shoes Ad Group",
    "status": "ENABLED",
    "type": "SEARCH",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

#### Get Ad Group Details

Returns details of a specific ad group.

```
GET /api/google-ads/ad-groups/{id}/
```

Path Parameters:
- `id`: The ID of the ad group

Response:
```json
{
  "id": "12345678",
  "campaign_id": "87654321",
  "campaign_name": "Winter Sale Campaign",
  "name": "Shoes Ad Group",
  "status": "ENABLED",
  "type": "SEARCH",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "ads": [
    {
      "id": "11223344",
      "headline": "Winter Shoes Sale",
      "status": "ENABLED"
    }
  ],
  "keywords": [
    {
      "keyword": "winter shoes",
      "match_type": "BROAD",
      "status": "ENABLED"
    }
  ],
  "performance": {
    "impressions": 500,
    "clicks": 25,
    "cost": "12.50",
    "conversions": 3,
    "ctr": 5.0,
    "cpc": "0.50"
  }
}
```

#### Create Ad Group

Creates a new ad group in a campaign.

```
POST /api/google-ads/ad-groups/
```

Request:
```json
{
  "campaign_id": "87654321",
  "name": "Jackets Ad Group",
  "status": "ENABLED",
  "type": "SEARCH"
}
```

Response:
```json
{
  "id": "12345678",
  "campaign_id": "87654321",
  "name": "Jackets Ad Group",
  "status": "ENABLED",
  "type": "SEARCH",
  "created_at": "2023-01-15T12:00:00Z",
  "updated_at": "2023-01-15T12:00:00Z"
}
```

#### Get Ad Group Keywords

Returns keyword metrics for a specific ad group.

```
GET /api/google-ads/ad-groups/{id}/keywords/
```

Path Parameters:
- `id`: The ID of the ad group

Query Parameters:
- `days`: (Optional) Number of days to include in the report (default: 30)

Response:
```json
[
  {
    "keyword": "winter jackets",
    "match_type": "EXACT",
    "impressions": 200,
    "clicks": 10,
    "cost": "5.00",
    "conversions": 1,
    "ctr": 5.0,
    "cpc": "0.50"
  },
  {
    "keyword": "winter coats",
    "match_type": "PHRASE",
    "impressions": 150,
    "clicks": 8,
    "cost": "4.00",
    "conversions": 1,
    "ctr": 5.33,
    "cpc": "0.50"
  }
]
```

### Ads

#### List Ads

Returns a list of ads from the connected Google Ads account.

```
GET /api/google-ads/ads/
```

Query Parameters:
- `ad_group_id`: (Optional) Filter by ad group ID
- `status`: (Optional) Filter by status (ENABLED, PAUSED, REMOVED)

Response:
```json
[
  {
    "id": "12345678",
    "ad_group_id": "87654321",
    "headline": "Winter Shoes Sale",
    "description": "Get 50% off on all winter shoes",
    "final_url": "https://example.com/shoes-sale",
    "status": "ENABLED",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

#### Get Ad Details

Returns details of a specific ad.

```
GET /api/google-ads/ads/{id}/
```

Path Parameters:
- `id`: The ID of the ad

Response:
```json
{
  "id": "12345678",
  "ad_group_id": "87654321",
  "ad_group_name": "Shoes Ad Group",
  "campaign_id": "11223344",
  "campaign_name": "Winter Sale Campaign",
  "headline": "Winter Shoes Sale",
  "description": "Get 50% off on all winter shoes",
  "final_url": "https://example.com/shoes-sale",
  "status": "ENABLED",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "performance": {
    "impressions": 300,
    "clicks": 15,
    "cost": "7.50",
    "conversions": 2,
    "ctr": 5.0,
    "cpc": "0.50"
  }
}
```

#### Create Ad

Creates a new ad in an ad group.

```
POST /api/google-ads/ads/
```

Request:
```json
{
  "ad_group_id": "87654321",
  "headline": "Winter Jackets Sale",
  "description": "Get 50% off on all winter jackets",
  "final_url": "https://example.com/jackets-sale",
  "status": "ENABLED"
}
```

Response:
```json
{
  "id": "12345678",
  "ad_group_id": "87654321",
  "headline": "Winter Jackets Sale",
  "description": "Get 50% off on all winter jackets",
  "final_url": "https://example.com/jackets-sale",
  "status": "ENABLED",
  "created_at": "2023-01-15T12:00:00Z",
  "updated_at": "2023-01-15T12:00:00Z"
}
```

#### Toggle Ad Status

Updates the status of an ad.

```
POST /api/google-ads/ads/{id}/toggle-status/
```

Path Parameters:
- `id`: The ID of the ad

Request:
```json
{
  "status": "PAUSED"
}
```

Response:
```json
{
  "id": "12345678",
  "status": "PAUSED",
  "updated_at": "2023-01-16T12:00:00Z"
}
```

### Performance Reports

#### Get Performance Summary

Returns a summary of performance metrics across all campaigns.

```
GET /api/google-ads/performance-reports/summary/
```

Query Parameters:
- `days`: (Optional) Number of days to include in the report (default: 30)

Response:
```json
{
  "impressions": 5000,
  "clicks": 250,
  "cost": "125.00",
  "conversions": 25,
  "ctr": 5.0,
  "cpc": "0.50",
  "conversion_rate": 10.0,
  "cost_per_conversion": "5.00"
}
```

#### Get Detailed Performance Reports

Returns detailed performance metrics for all campaigns.

```
GET /api/google-ads/performance-reports/
```

Query Parameters:
- `days`: (Optional) Number of days to include in the report (default: 30)
- `group_by`: (Optional) Group results by "day", "week", or "month" (default: "day")

Response:
```json
[
  {
    "date": "2023-02-01",
    "impressions": 1000,
    "clicks": 50,
    "cost": "25.00",
    "conversions": 5,
    "ctr": 5.0,
    "cpc": "0.50"
  },
  {
    "date": "2023-02-02",
    "impressions": 1200,
    "clicks": 60,
    "cost": "30.00",
    "conversions": 6,
    "ctr": 5.0,
    "cpc": "0.50"
  }
]
```

## Testing Guide

### Postman Collection

A Postman collection is available for testing all endpoints. You can import it using the following link:

```
https://www.postman.com/linkly/workspace/linkly-api-testing/collection/12345678
```

### Environment Variables

Set up the following environment variables in Postman:

- `BASE_URL`: Your API base URL (e.g., `http://localhost:8000`)
- `ACCESS_TOKEN`: JWT access token after authentication

### Testing Flow

1. **Authentication**:
   - Call the login endpoint to get the access token
   - Set the `ACCESS_TOKEN` environment variable with the received token

2. **Social Platforms**:
   - List available platforms
   - Initialize OAuth flow for a platform
   - After OAuth callback, list connected accounts
   - Create a post
   - List posts

3. **Google Ads**:
   - Check authentication status
   - Initialize OAuth flow
   - After OAuth callback, list campaigns
   - Create a new campaign
   - Create an ad group in the campaign
   - Create an ad in the ad group
   - Get performance reports

### Mock Data

For testing without real social accounts, you can use the following mock endpoints:

```
GET /api/mock/social-platforms/
GET /api/mock/google-ads/
```

These endpoints return sample data for testing the frontend integration.

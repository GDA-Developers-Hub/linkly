/**
 * Common constants used throughout the application
 */

// Base URL for API calls
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://linkly-production-f31e.up.railway.app';

// API endpoints
export const ENDPOINTS = {
  OAUTH_INIT: '/api/social_platforms/oauth/init/',
  OAUTH_COMPLETE: '/api/social_platforms/oauth/complete/',
  SOCIAL_ACCOUNTS: '/api/social_platforms/accounts/',
  PLATFORMS: '/api/social_platforms/platforms/',
};

// OAuth related constants
export const OAUTH = {
  STORAGE_PREFIX: 'pending_oauth_',
  POLL_ATTEMPTS: 30,
  POLL_INTERVAL: 2000, // ms
  POPUP_WIDTH: 600,
  POPUP_HEIGHT: 700,
};

// Authentication constants
export const AUTH = {
  TOKEN_KEY: 'accessToken',
  REFRESH_TOKEN_KEY: 'refreshToken',
};

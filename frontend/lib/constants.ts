/**
 * Common constants used throughout the application
 */

// Base URL for API calls, with protocol and trailing slash
export const API_BASE_URL = (() => {
  // Get the base URL from environment variables
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
  
  if (!baseUrl) {
    console.warn('API_URL not set in environment variables');
    baseUrl = ''; // This will cause an error and make it obvious that env vars need to be set
  }

  // Ensure it has protocol
  if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
    baseUrl = `https://${baseUrl}`;
  }

  // Ensure trailing slash
  if (!baseUrl.endsWith('/')) {
    baseUrl += '/';
  }

  console.log(`Using API Base URL: ${baseUrl} (${process.env.NODE_ENV} environment)`);
  return baseUrl;
})();

// Export other constants that might use the API base URL
export const AUTH_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}auth/login/`,
  REGISTER: `${API_BASE_URL}auth/register/`,
  REFRESH: `${API_BASE_URL}auth/refresh/`,
  VERIFY: `${API_BASE_URL}auth/verify/`,
  SOCIAL_AUTH: (provider: string) => `${API_BASE_URL}accounts/${provider}/login/`,
  SOCIAL_CONNECT: (provider: string, token: string) => 
    `${API_BASE_URL}accounts/${provider}/login/?process=connect&token=${token}`,
};

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
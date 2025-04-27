/**
 * Utility functions for handling OAuth workflows
 */
import { API_ENDPOINTS } from '../constants/endpoints';

// Base URL for API endpoints
const BASE_URL = 'https://linkly-production.up.railway.app';

/**
 * Opens a popup window for OAuth authorization
 * 
 * @param {string} authUrl - The authorization URL to open
 * @param {string} platform - The platform name (e.g., 'linkedin', 'twitter')
 * @param {function} onSuccess - Callback function when OAuth succeeds
 * @param {function} onError - Callback function when OAuth fails
 * @returns {Window} - The popup window object
 */
export const openOAuthPopup = (authUrl, platform, onSuccess, onError) => {
  // Calculate centered position
  const width = 600;
  const height = 700;
  const left = window.screen.width / 2 - width / 2;
  const top = window.screen.height / 2 - height / 2;
  
  // Open popup
  const popup = window.open(
    authUrl,
    `${platform}_oauth`,
    `width=${width},height=${height},left=${left},top=${top},toolbar=0,scrollbars=1,status=1,resizable=1`
  );
  
  // Set up message listener for communication back from popup
  const messageHandler = (event) => {
    // Validate origin if needed
    // if (event.origin !== window.location.origin) return;
    
    const { type, platform: responsePlatform, data, error } = event.data || {};
    
    if (type === 'OAUTH_SUCCESS' && responsePlatform === platform) {
      console.log('OAuth success message received:', data);
      if (onSuccess) onSuccess(data);
      window.removeEventListener('message', messageHandler);
    } else if (type === 'OAUTH_ERROR') {
      console.error('OAuth error message received:', error);
      if (onError) onError(error);
      window.removeEventListener('message', messageHandler);
    }
  };
  
  window.addEventListener('message', messageHandler);
  
  // Check periodically if popup was closed
  const checkClosed = setInterval(() => {
    if (!popup || popup.closed) {
      clearInterval(checkClosed);
      window.removeEventListener('message', messageHandler);
      if (onError) onError({ message: 'Authentication window was closed' });
    }
  }, 1000);
  
  return popup;
};

/**
 * Get the OAuth callback URL for a specific platform
 * 
 * @param {string} platform - The platform name (e.g., 'linkedin', 'twitter')
 * @returns {string} - The callback URL for the platform
 */
export const getOAuthCallbackURL = (platform) => {
  const platformUppercase = platform.toUpperCase();
  const callbackEndpoint = API_ENDPOINTS[`${platformUppercase}_CALLBACK`] || API_ENDPOINTS.OAUTH_CALLBACK;
  return callbackEndpoint;
};

/**
 * Get the full OAuth callback URL for a specific platform
 * 
 * @param {string} platform - The platform name (e.g., 'linkedin', 'twitter')
 * @param {boolean} includeFullDomain - Whether to include the full domain (default: true)
 * @returns {string} - The full callback URL for the platform
 */
export const getFullCallbackURL = (platform, includeFullDomain = true) => {
  const endpoint = getOAuthCallbackURL(platform);
  
  // Special case for Twitter due to known encoding issues
  if (platform === 'twitter') {
    return `${BASE_URL}${endpoint}`;
  }
  
  return includeFullDomain ? `${BASE_URL}${endpoint}` : endpoint;
};

/**
 * Get the OAuth authorization URL
 * 
 * @returns {string} - The authorization URL
 */
export const getOAuthAuthorizeURL = () => {
  return API_ENDPOINTS.OAUTH_AUTHORIZE;
};

/**
 * Create OAuth authorization URL for a platform
 * 
 * @param {string} platform - The platform name
 * @param {object} params - Additional parameters for the authorization
 * @returns {string} - The complete authorization URL
 */
export const createOAuthURL = (platform, params = {}) => {
  const baseUrl = getOAuthAuthorizeURL();
  const urlParams = new URLSearchParams({
    platform,
    ...params
  });
  
  // If redirect_uri not provided, add the default one
  if (!params.redirect_uri) {
    urlParams.append('redirect_uri', getFullCallbackURL(platform));
  }
  
  return `${baseUrl}?${urlParams.toString()}`;
};

/**
 * Handle redirects from OAuth callback
 * This is used when the OAuth flow redirects directly to the main window
 * instead of using a popup
 * 
 * @param {Location} location - The current location object
 * @returns {object} - The parsed data from the redirect
 */
export const handleOAuthRedirect = (location) => {
  const params = new URLSearchParams(location.search);
  const platform = params.get('platform');
  const error = params.get('error');
  const code = params.get('code');
  const state = params.get('state');
  
  return {
    platform,
    error,
    code,
    state,
    isSuccess: Boolean(platform && !error),
    isError: Boolean(error)
  };
};

/**
 * Process the data received from OAuth callback API
 * 
 * @param {string} platform - The platform name
 * @param {object} data - The data received from the API
 * @returns {object} - Processed data with standard format
 */
export const processOAuthData = (platform, data) => {
  // Default structure
  const processed = {
    platform,
    connected: data?.success || false,
    profile: data?.profile || {},
    username: null,
    profileUrl: null
  };
  
  // Platform-specific processing
  if (platform === 'linkedin') {
    processed.username = data?.profile?.name || data?.profile?.localizedFirstName;
    processed.profileUrl = data?.profile?.vanityName 
      ? `https://linkedin.com/in/${data.profile.vanityName}` 
      : null;
  } else if (platform === 'twitter') {
    processed.username = data?.profile?.username;
    processed.profileUrl = data?.profile?.username 
      ? `https://twitter.com/${data.profile.username}` 
      : null;
  } else if (platform === 'facebook') {
    processed.username = data?.profile?.name;
    processed.profileUrl = data?.profile?.id 
      ? `https://facebook.com/${data.profile.id}` 
      : null;
    processed.pictureUrl = data?.profile?.picture;
  } else if (platform === 'instagram') {
    processed.username = data?.profile?.username;
    processed.profileUrl = data?.profile?.username 
      ? `https://instagram.com/${data.profile.username}` 
      : null;
    processed.pictureUrl = data?.profile?.picture;
  } else if (platform === 'tiktok') {
    processed.username = data?.profile?.display_name;
    processed.profileUrl = data?.profile?.open_id 
      ? `https://tiktok.com/@${data.profile.username || ''}` 
      : null;
    processed.pictureUrl = data?.profile?.avatar_url;
  } else if (platform === 'google') {
    processed.username = data?.profile?.name;
    processed.profileUrl = null;
    processed.pictureUrl = data?.profile?.picture;
  }
  
  return processed;
};

export default {
  openOAuthPopup,
  handleOAuthRedirect,
  processOAuthData,
  getOAuthCallbackURL,
  getFullCallbackURL,
  getOAuthAuthorizeURL,
  createOAuthURL
}; 
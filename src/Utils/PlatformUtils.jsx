import axios from 'axios';
import API_BASE_URL from './BaseUrl';
import { getAccessToken, getRefreshToken } from './Auth';
import backendBaseUrl from './BaseUrl';
import { getFullCallbackURL } from './OAuthUtils';

// Supported platforms
export const SUPPORTED_PLATFORMS = [
  {
    id: 'twitter',
    name: 'Twitter',
    icon: '🐦',
    description: 'Connect your Twitter account to post tweets and track engagement.'
  },
  {
    id: 'facebook',
    name: 'Facebook',
    icon: '📘',
    description: 'Connect your Facebook account to post updates and track engagement.'
  },
  {
    id: 'instagram',
    name: 'Instagram',
    icon: '📷',
    description: 'Connect your Instagram account to post photos and track engagement.'
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: '💼',
    description: 'Connect your LinkedIn account to post updates and track engagement.'
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: '📹',
    description: 'Connect your YouTube account to manage videos and track engagement.'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: '🎵',
    description: 'Connect your TikTok account to post videos and track engagement.'
  },
  {
    id: 'telegram',
    name: 'Telegram',
    icon: '📱',
    description: 'Connect your Telegram account to send messages and track engagement.'
  }
];

// Initialize OAuth flow for a platform
export const initOAuthFlow = async (platform, redirectUri, useCustomCredentials = false) => {
  try {
    console.log(`Initializing OAuth flow for ${typeof platform === 'object' ? platform.id : platform}`);
    
    // Get token from Auth
    const token = getAccessToken();
    if (!token) {
      console.error('Authentication required for OAuth flow');
      throw new Error('Authentication required');
    }
    
    // Extract platform ID
    const platformId = typeof platform === 'object' ? platform.id : platform;
    
    // If no redirect URI is provided, use the full callback URL
    const effectiveRedirectUri = redirectUri || getFullCallbackURL(platformId);
    
    console.log(`Using redirect URI: ${effectiveRedirectUri}`);
    
    // Special case for Twitter to handle its OAuth flow with PKCE
    if (platformId === 'twitter') {
      console.log('Initializing Twitter OAuth flow with PKCE');
      
      // Generate a unique ID for personalization_id
      const personalizationId = `v1_${Math.random().toString(36).substring(2, 15)}`;
      
      // Construct Twitter-specific parameters
      const twitterParams = {
        platform: platformId,
        redirect_uri: effectiveRedirectUri,
        use_client_credentials: useCustomCredentials,
        personalization_id: personalizationId
      };
      
      // Use URL search params to ensure proper encoding
      const params = new URLSearchParams();
      Object.entries(twitterParams).forEach(([key, value]) => {
        params.append(key, value);
      });
      
      const requestUrl = `${API_BASE_URL}/users/auth/init/?${params.toString()}`;
      console.log('Twitter OAuth init URL:', requestUrl);
      
      const response = await axios.get(requestUrl, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data.auth_url) {
        // Store code_verifier in sessionStorage if available
        if (response.data.code_verifier && response.data.state) {
          const storeKey = `pkce_verifier_${response.data.state}`;
          sessionStorage.setItem(storeKey, response.data.code_verifier);
          console.log(`Stored Twitter code_verifier (length: ${response.data.code_verifier.length})`);
        }
        
        // Add personalization_id directly to the auth_url 
        const authUrl = response.data.auth_url;
        const separator = authUrl.includes('?') ? '&' : '?';
        const enhancedAuthUrl = `${authUrl}${separator}personalization_id=${personalizationId}`;
        console.log('Enhanced Twitter auth URL with personalization_id');
        
        return enhancedAuthUrl;
      }
      
      throw new Error('Failed to get Twitter authorization URL');
    }
    
    // Regular OAuth flow for other platforms
    // Make sure the redirect URI is properly encoded
    const encodedRedirectUri = encodeURIComponent(effectiveRedirectUri);
    
    // Debug: Log the full request URL for debugging
    const requestUrl = `${API_BASE_URL}/users/auth/init/?platform=${platformId}&redirect_uri=${encodedRedirectUri}&use_client_credentials=${useCustomCredentials}`;
    console.log('Full request URL:', requestUrl);
    
    // Use direct URL approach to avoid parameter encoding issues
    const response = await axios.get(requestUrl, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.data.auth_url) {
      // Store code_verifier in sessionStorage if available
      if (response.data.code_verifier && response.data.state) {
        const storeKey = `pkce_verifier_${response.data.state}`;
        console.log(`Storing code_verifier for state ${response.data.state}, storage key: ${storeKey}`);
        console.log(`Code verifier length: ${response.data.code_verifier.length}`);
        console.log(`First 10 chars: ${response.data.code_verifier.substring(0, 10)}...`);
        
        // Store in sessionStorage for later retrieval
        sessionStorage.setItem(storeKey, response.data.code_verifier);
        
        // Verify storage worked
        const stored = sessionStorage.getItem(storeKey);
        if (stored) {
          console.log(`Verified code_verifier was stored, length: ${stored.length}`);
        } else {
          console.error("Failed to store code_verifier in sessionStorage!");
        }
      }
      
      return response.data.auth_url;
    } else {
      throw new Error('Failed to get authorization URL');
    }
  } catch (error) {
    console.error(`Error initializing ${typeof platform === 'object' ? platform.id : platform} OAuth flow:`, error);
    throw error;
  }
};

// Get all connected platforms for the current user
export const getConnectedPlatforms = async () => {
  try {
    const token = getAccessToken();
    if (!token) {
      console.error('Authentication required for getting connected platforms');
      throw new Error('Authentication required');
    }
    
    console.log('Fetching connected platforms with token', token.slice(0, 10) + '...');
    
    // First try using the User profile endpoint which should include connected platforms
    try {
      const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('User profile API response:', JSON.stringify(response.data));
      
      // Check if the user object has a connected_platforms property
      if (response.data && response.data.connected_platforms) {
        return response.data.connected_platforms || [];
      }
      
      // If we don't have connected_platforms in the user profile, try to derive it from individual platform fields
      const user = response.data;
      const platforms = [];
      
      // Check for each platform's connection status
      if (user.facebook_id) {
        platforms.push({
          platform: 'facebook',
          account_type: user.has_facebook_business ? 'business' : 'personal',
          profile: {
            id: user.facebook_id,
            name: user.facebook_page_name || null
          }
        });
      }
      
      if (user.instagram_id) {
        platforms.push({
          platform: 'instagram',
          account_type: user.has_instagram_business ? 'business' : 'personal',
          profile: {
            id: user.instagram_id,
            username: user.instagram_handle || null
          }
        });
      }
      
      if (user.twitter_id) {
        platforms.push({
          platform: 'twitter',
          account_type: user.has_twitter_business ? 'business' : 'personal',
          profile: {
            id: user.twitter_id,
            username: user.twitter_handle || null
          }
        });
      }
      
      if (user.linkedin_id) {
        platforms.push({
          platform: 'linkedin',
          account_type: user.has_linkedin_company ? 'business' : 'personal',
          profile: {
            id: user.linkedin_id
          }
        });
      }
      
      if (user.tiktok_id) {
        platforms.push({
          platform: 'tiktok',
          account_type: user.has_tiktok_business ? 'business' : 'personal',
          profile: {
            id: user.tiktok_id,
            username: user.tiktok_handle || null
          }
        });
      }
      
      if (user.telegram_id) {
        platforms.push({
          platform: 'telegram',
          account_type: user.has_telegram_channel ? 'business' : 'personal',
          profile: {
            id: user.telegram_id,
            username: user.telegram_username || null
          }
        });
      }
      
      console.log('Derived platforms from user profile:', platforms);
      return platforms;
      
    } catch (profileError) {
      console.error('Error fetching user profile:', profileError);
      
      // Fall back to the accounts endpoint if available
      try {
        const accountsResponse = await axios.get(`${API_BASE_URL}/users/accounts/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('Connected platforms API response:', JSON.stringify(accountsResponse.data));
        return accountsResponse.data.accounts || [];
      } catch (accountsError) {
        console.error('Error fetching accounts:', accountsError);
        throw accountsError;
      }
    }
  } catch (error) {
    console.error('Error getting connected platforms:', error);
    console.log('Error status:', error.response?.status);
    console.log('Error data:', JSON.stringify(error.response?.data));
    
    // If we get a 404, it might be that the endpoint doesn't exist in this version
    if (error.response?.status === 404) {
      console.log('API endpoint not found, returning empty array');
      return [];
    }
    
    // Return empty array to avoid breaking the UI
    return [];
  }
};

// Disconnect a platform
export const disconnectPlatform = async (platform) => {
  try {
    const token = getAccessToken();
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.post(`${API_BASE_URL}/users/auth/unlink/${platform}/`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error(`Error disconnecting ${platform}:`, error);
    throw error;
  }
};

// Handles the OAuth callback by extracting the code and state parameters
export const handleOAuthCallback = async (platform, code, state) => {
  try {
    const token = getAccessToken();
    if (!token) {
      throw new Error('Authentication required');
    }
    
    console.log(`Processing OAuth callback for ${platform} with state: ${state}`);
    
    // Parse state parameter to determine if using custom credentials
    // Format is [custom_]platform_timestamp_randomString
    const isCustomCredentials = state && state.startsWith('custom_');
    const statePrefix = isCustomCredentials ? 'custom_' : '';
    
    console.log(`State parameter analysis: isCustomCredentials=${isCustomCredentials}, prefix=${statePrefix}`);
    
    // Get the code_verifier from sessionStorage if it exists
    const verifierKey = `pkce_verifier_${state}`;
    const codeVerifier = sessionStorage.getItem(verifierKey);
    console.log(`Retrieved code_verifier for state ${state} using key ${verifierKey}:`, 
                codeVerifier ? `Found (length: ${codeVerifier.length})` : 'Not found');
    
    if (codeVerifier) {
      console.log(`First 10 chars of code_verifier: ${codeVerifier.substring(0, 10)}...`);
    } else {
      console.warn(`No code_verifier found for state: ${state}. This might cause authentication to fail.`);
      // List all sessionStorage items to help debug
      const allKeys = [];
      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        allKeys.push(key);
      }
      console.log('All sessionStorage keys:', allKeys);
    }
    
    // Check if PKCE is required for this platform
    const pkceRequired = ['twitter', 'youtube', 'facebook', 'instagram'].includes(platform);
    if (pkceRequired && !codeVerifier) {
      throw new Error(`PKCE code_verifier is required for ${platform} OAuth and was not found in session storage.`);
    }
    
    // Include code_verifier in the request if available
    const params = { 
      code, 
      state,
      use_client_credentials: isCustomCredentials
    };
    
    if (codeVerifier) {
      params.code_verifier = codeVerifier;
      // Clean up after use
      sessionStorage.removeItem(verifierKey);
      console.log(`Removed code_verifier from sessionStorage after use: ${verifierKey}`);
    }
    
    // Log the full parameters we're sending
    console.log(`Calling ${platform} OAuth callback with params:`, JSON.stringify(params));
    
    // Use consistent backend callback URL pattern for all platforms
    const callbackEndpoint = `${API_BASE_URL}/users/auth/callback/${platform}/`;
    
    // Exchange the code for tokens
    const response = await axios.get(callbackEndpoint, {
      params,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log(`${platform} OAuth callback response:`, response.data);
    
    // If the backend callback succeeds, ensure tokens are saved
    if (response.data.success || response.data.status === 'success') {
      // Call the save-tokens endpoint to ensure tokens are stored
      await savePlatformTokens(platform, response.data);
      
      // For Twitter, add platform-specific handling
      if (platform === 'twitter') {
        console.log('Twitter account connected successfully');
        
        // Return enhanced response for Twitter
        return {
          ...response.data,
          platform: 'twitter',
          connected: true,
          message: response.data.message || 'Twitter account connected successfully'
        };
      }
      
      // For YouTube, add platform-specific handling
      if (platform === 'youtube') {
        console.log('YouTube account connected successfully');
        
        // Return enhanced response for YouTube
        return {
          ...response.data,
          platform: 'youtube',
          connected: true,
          message: response.data.message || 'YouTube account connected successfully'
        };
      }
    }
    
    return response.data;
  } catch (error) {
    console.error(`Error completing ${platform} OAuth flow:`, error);
    console.error('Error response:', error.response?.data);
    
    // Provide more detailed error information for Twitter
    if (platform === 'twitter') {
      let errorDetail = 'Unknown error';
      
      if (error.response?.data) {
        errorDetail = error.response.data.details || 
                      error.response.data.error || 
                      error.response.data.message || 
                      error.message;
      } else {
        errorDetail = error.message;
      }
      
      throw new Error(`Failed to connect Twitter account: ${errorDetail}`);
    }
    
    // Provide more detailed error information for YouTube
    if (platform === 'youtube') {
      let errorDetail = 'Unknown error';
      
      if (error.response?.data) {
        errorDetail = error.response.data.details || 
                      error.response.data.error || 
                      error.response.data.message || 
                      error.message;
      } else {
        errorDetail = error.message;
      }
      
      throw new Error(`Failed to connect YouTube account: ${errorDetail}`);
    }
    
    throw error;
  }
};

// Save platform tokens and account information to backend
export const savePlatformTokens = async (platform, tokenData) => {
  try {
    const token = getAccessToken();
    if (!token) {
      throw new Error('Authentication required');
    }
    
    // Send the token data to be saved in the user's profile
    const response = await axios.post(`${API_BASE_URL}/users/save-platform-tokens/`, {
      platform: platform,
      token_data: tokenData
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log(`Saved ${platform} tokens to user profile:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`Error saving ${platform} tokens:`, error);
    // This is a non-critical error, so we'll log it but not throw
    return { success: false, error: error.message };
  }
};

export default {
  SUPPORTED_PLATFORMS,
  initOAuthFlow,
  getConnectedPlatforms,
  disconnectPlatform,
  handleOAuthCallback
}; 
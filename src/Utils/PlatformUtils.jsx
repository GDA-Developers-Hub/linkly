import axios from 'axios';
import API_BASE_URL from './BaseUrl';
import { getAccessToken } from './Auth';

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
    const token = getAccessToken();
    if (!token) {
      throw new Error('Authentication required');
    }
    
    const response = await axios.get(`${API_BASE_URL}/users/auth/init/`, {
      params: {
        platform,
        redirect_uri: redirectUri,
        use_client_credentials: useCustomCredentials
      },
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
    console.error(`Error initializing ${platform} OAuth flow:`, error);
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
    
    // Check if this is using custom credentials
    const isCustomCredentials = state.includes('custom_');
    
    // Get the code_verifier from sessionStorage if it exists
    const codeVerifier = sessionStorage.getItem(`pkce_verifier_${state}`);
    console.log(`Retrieved code_verifier for state ${state}:`, codeVerifier ? `Found (length: ${codeVerifier.length})` : 'Not found');
    console.log(`First 10 chars of code_verifier: ${codeVerifier ? codeVerifier.substring(0, 10) : 'N/A'}`);
    
    // Include code_verifier in the request if available
    const params = { 
      code, 
      state,
      use_client_credentials: isCustomCredentials
    };
    if (codeVerifier) {
      params.code_verifier = codeVerifier;
      // Clean up after use
      sessionStorage.removeItem(`pkce_verifier_${state}`);
    }
    
    // Log the full parameters we're sending
    console.log(`Calling ${platform} OAuth callback with params:`, JSON.stringify(params));
    
    // First, exchange the code for tokens
    const response = await axios.get(`${API_BASE_URL}/users/auth/callback/${platform}/`, {
      params,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log(`${platform} OAuth callback response:`, response.data);
    
    // If the backend callback succeeds, ensure tokens are saved
    if (response.data.success) {
      // Call the save-tokens endpoint to ensure tokens are stored
      await savePlatformTokens(platform, response.data);
    }
    
    return response.data;
  } catch (error) {
    console.error(`Error completing ${platform} OAuth flow:`, error);
    console.error('Error response:', error.response?.data);
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
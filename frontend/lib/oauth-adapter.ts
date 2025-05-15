/**
 * OAuth Adapter for Django AllAuth Integration
 * This utility bridges the frontend components with the new AllAuth-based backend
 */

import { API_BASE_URL, AUTH, ENDPOINTS, OAUTH } from './constants';

export interface OAuthInitResponse {
  authorization_url: string;
}

export interface OAuthCompleteResponse {
  success: boolean;
  message?: string;
  account?: any;
  error?: string;
  auth_required?: boolean;
  platform?: string;
  code_id?: string;
}

export interface SocialAccount {
  id: number;
  platform_name: string;
  account_name: string;
  account_type: string;
  profile_picture_url: string;
  status: string;
}

/**
 * Initialize OAuth flow for a platform
 * @param platform Platform identifier (e.g., 'facebook', 'twitter')
 * @returns Authorization URL to redirect the user to
 */
export async function initializeOAuth(platform: string): Promise<string> {
  try {
    // Try the new AllAuth endpoint first
    const response = await fetch(`${API_BASE_URL}${ENDPOINTS.OAUTH_INIT}/${platform}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem(AUTH.TOKEN_KEY)}`,
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to initialize OAuth: ${response.statusText}`);
    }
    
    const data: OAuthInitResponse = await response.json();
    return data.authorization_url;
  } catch (error) {
    console.error('Error initializing OAuth flow:', error);
    throw error;
  }
}

/**
 * Complete OAuth flow for a platform with a code_id
 * Used after authentication when the user was not authenticated during the initial OAuth callback
 * @param platform Platform identifier
 * @param code_id The code ID from the Redis store
 * @returns The connected social account
 */
export async function completeOAuth(platform: string, code_id: string): Promise<SocialAccount> {
  try {
    const response = await fetch(`${API_BASE_URL}${ENDPOINTS.OAUTH_COMPLETE}/${platform}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem(AUTH.TOKEN_KEY)}`,
      },
      body: JSON.stringify({ code_id }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to complete OAuth: ${response.statusText}`);
    }
    
    const data: OAuthCompleteResponse = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to complete OAuth');
    }
    
    return data.account;
  } catch (error) {
    console.error('Error completing OAuth flow:', error);
    throw error;
  }
}

/**
 * Handle OAuth callback from popup window
 * @param event Message event from popup window
 * @returns Promise that resolves with the connected account or null if further authentication is needed
 */
export function handleOAuthCallback(event: MessageEvent): Promise<SocialAccount | null> {
  return new Promise((resolve, reject) => {
    try {
      // Parse the data from the popup window
      const data: OAuthCompleteResponse = typeof event.data === 'string' 
        ? JSON.parse(event.data) 
        : event.data;
      
      if (!data.success) {
        return reject(new Error(data.error || 'OAuth flow failed'));
      }
      
      // Check if authentication is required
      if (data.auth_required) {
        // Store code_id in localStorage to use after login
        if (data.code_id && data.platform) {
          localStorage.setItem(`${OAUTH.STORAGE_PREFIX}${data.platform}`, data.code_id);
        }
        return resolve(null); // Indicate authentication is needed
      }
      
      // If success and account is provided, return the account
      if (data.account) {
        return resolve(data.account);
      }
      
      reject(new Error('Invalid OAuth callback data'));
    } catch (error) {
      console.error('Error handling OAuth callback:', error);
      reject(error);
    }
  });
}

/**
 * Check for pending OAuth connections after login
 * This should be called after a user logs in
 * @returns Promise that resolves with an array of platforms that have pending connections
 */
export async function checkPendingOAuthConnections(): Promise<string[]> {
  const pendingPlatforms: string[] = [];
  
  // Check local storage for pending OAuth connections
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith(OAUTH.STORAGE_PREFIX)) {
      const platform = key.replace(OAUTH.STORAGE_PREFIX, '');
      pendingPlatforms.push(platform);
    }
  }
  
  return pendingPlatforms;
}

/**
 * Complete all pending OAuth connections
 * @returns Promise that resolves when all pending connections are completed
 */
export async function completePendingOAuthConnections(): Promise<SocialAccount[]> {
  const pendingPlatforms = await checkPendingOAuthConnections();
  const accounts: SocialAccount[] = [];
  
  for (const platform of pendingPlatforms) {
    try {
      const codeId = localStorage.getItem(`${OAUTH.STORAGE_PREFIX}${platform}`);
      if (codeId) {
        const account = await completeOAuth(platform, codeId);
        accounts.push(account);
        localStorage.removeItem(`${OAUTH.STORAGE_PREFIX}${platform}`);
      }
    } catch (error) {
      console.error(`Error completing pending OAuth for ${platform}:`, error);
    }
  }
  
  return accounts;
}

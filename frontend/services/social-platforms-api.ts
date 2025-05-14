/**
 * Social Platforms API Client
 * This module provides client-side access to the social platforms API endpoints.
 */

// Types
export interface SocialAccount {
  id: number;
  account_id: string;
  account_name: string;
  account_type: string;
  platform: {
    id: number;
    name: string;
    display_name: string;
  };
  profile_picture_url: string | null;
  status: string;
  is_primary: boolean;
  followers?: number;
  engagement_rate?: number;
  reach?: number;
  created_at: string;
  updated_at: string;
}

export interface SocialPost {
  id: number;
  content: string;
  status: string; // scheduled, published, draft
  publish_at: string | null;
  published_at: string | null;
  account: SocialAccount;
  engagement: {
    likes: number;
    comments: number;
    shares: number;
  };
}

export interface SocialPlatform {
  id: number;
  name: string;
  display_name: string;
  auth_url: string;
  is_active: boolean;
}

// Safe localStorage access
const safeLocalStorage = {
  getItem: (key: string): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(key);
    }
    return null;
  },
  setItem: (key: string, value: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, value);
    }
  }
};

// API Class
export class SocialPlatformsAPI {
  private baseUrl: string;

  constructor() {
    // Default to the production URL instead of local development
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://linkly-production.up.railway.app/api';
    
    console.log('SocialPlatformsAPI using backend URL:', this.baseUrl);
  }
  
  // Get headers with current token
  private getHeaders(): HeadersInit {
    // Try multiple possible token storage locations
    const token = 
      safeLocalStorage.getItem('accessToken') || 
      safeLocalStorage.getItem('linkly_access_token') ||
      safeLocalStorage.getItem('auth_token') ||
      safeLocalStorage.getItem('token');
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      // Add X-Requested-With header to help with CORS and auth
      'X-Requested-With': 'XMLHttpRequest'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log('SocialPlatformsAPI: Using token:', token.substring(0, 10) + '...');
    } else {
      console.warn('SocialPlatformsAPI: No access token available');
    }
    
    return headers;
  }

  /**
   * Get all connected social accounts for the current user
   */
  async getAccounts(): Promise<SocialAccount[]> {
    const response = await fetch(`${this.baseUrl}/api/social_platforms/accounts/`, {
      headers: this.getHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch social accounts');
    }

    return await response.json();
  }

  /**
   * Get all available social platforms
   */
  async getPlatforms(): Promise<SocialPlatform[]> {
    const response = await fetch(`${this.baseUrl}/api/social_platforms/platforms/`, {
      headers: this.getHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch social platforms');
    }

    return await response.json();
  }

  /**
   * Initialize OAuth flow for a specific platform
   */
  async initiateOAuth(platformId: string): Promise<{ authorization_url: string }> {
    const response = await fetch(`${this.baseUrl}/api/social_platforms/oauth/init/${platformId}/`, {
      headers: this.getHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to initiate OAuth flow');
    }

    return await response.json();
  }

  /**
   * Get posts for the connected social accounts
   */
  async getPosts(params: { limit?: number; offset?: number; status?: string } = {}): Promise<{
    items: SocialPost[];
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());
    if (params.status) queryParams.append('status', params.status);
    
    const url = `${this.baseUrl}/api/social_platforms/posts/?${queryParams.toString()}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch social posts');
    }

    const data = await response.json();
    return {
      items: data.results || [],
      total: data.count || 0,
    };
  }

  /**
   * Get metrics for the connected social accounts
   */
  async getMetrics(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/social_platforms/metrics/`, {
      headers: this.getHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch social metrics');
    }

    return await response.json();
  }

  /**
   * Disconnect a connected social account
   */
  async disconnectAccount(accountId: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/social_platforms/accounts/${accountId}/`, {
      method: 'DELETE',
      headers: this.getHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Failed to disconnect social account');
    }
  }
  
  /**
   * Complete OAuth flow using stored code and state after user authentication
   * @param platform The platform name (e.g. 'linkedin', 'twitter')
   * @param extraData Optional additional data to include in the request (e.g. state for LinkedIn)
   */
  async completeOAuth(platform: string, extraData: Record<string, any> = {}): Promise<any> {
    // Support both Redis code_id and state parameter approaches
    
    // If we have a Redis code_id, use that instead of the state parameter
    // This is the preferred authentication method for higher security
    if (extraData.code_id) {
      console.log(`Using Redis code_id for ${platform} authentication:`, extraData.code_id.substring(0, 8) + '...');
    }
    // Fallback to state parameter if code_id isn't available
    else if (['linkedin', 'youtube'].includes(platform.toLowerCase()) && !extraData.state) {
      const stateKey = `${platform.toLowerCase()}_oauth_state`;
      const storedState = localStorage.getItem(stateKey);
      
      if (storedState) {
        extraData.state = storedState;
        console.log(`Using ${platform} state from localStorage:`, storedState);
      } else {
        // Generate a random state if needed
        extraData.state = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        console.log(`Generated new state for ${platform}:`, extraData.state);
      }
    }
    
    // Enhanced logging to help with debugging
    console.log(`Completing OAuth for ${platform} with extra data:`, extraData)
    
    const response = await fetch(`${this.baseUrl}/api/social_platforms/oauth/complete/${platform}/`, {
      method: 'POST',
      headers: this.getHeaders(),
      credentials: 'include',
      body: JSON.stringify(extraData) // Always include body to prevent issues
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Failed to complete OAuth connection');
    }

    return await response.json();
  }
}

// Export a singleton instance for convenience
export const socialPlatformsApi = new SocialPlatformsAPI();

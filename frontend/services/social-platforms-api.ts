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
    const token = safeLocalStorage.getItem('accessToken') || safeLocalStorage.getItem('linkly_access_token');
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
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
    const response = await fetch(`${this.baseUrl}/social_platforms/api/accounts/`, {
      headers: this.getHeaders(),
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
    const response = await fetch(`${this.baseUrl}/social_platforms/api/platforms/`, {
      headers: this.getHeaders(),
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
    const response = await fetch(`${this.baseUrl}/social_platforms/api/oauth/init/${platformId}/`, {
      headers: this.getHeaders(),
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
    
    const url = `${this.baseUrl}/social_platforms/api/posts/?${queryParams.toString()}`;
    
    const response = await fetch(url, {
      headers: this.getHeaders(),
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
    const response = await fetch(`${this.baseUrl}/social_platforms/api/metrics/`, {
      headers: this.getHeaders(),
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
    const response = await fetch(`${this.baseUrl}/social_platforms/api/accounts/${accountId}/`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to disconnect social account');
    }
  }
}

// Export a singleton instance for convenience
export const socialPlatformsApi = new SocialPlatformsAPI();

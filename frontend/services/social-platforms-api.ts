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

// API Class
export class SocialPlatformsAPI {
  private baseUrl: string;
  private headers: HeadersInit;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
    this.headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    };
  }

  /**
   * Get all connected social accounts for the current user
   */
  async getAccounts(): Promise<SocialAccount[]> {
    const response = await fetch(`${this.baseUrl}/social_platforms/api/accounts/`, {
      headers: this.headers,
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
      headers: this.headers,
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
      headers: this.headers,
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
      headers: this.headers,
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
      headers: this.headers,
    });

    if (!response.ok) {
      throw new Error('Failed to fetch social metrics');
    }

    return await response.json();
  }
}

// Export a singleton instance for convenience
export const socialPlatformsApi = new SocialPlatformsAPI();

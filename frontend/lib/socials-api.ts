import { withErrorHandling } from "./api";
import { socialPlatformsApi } from "@/services/social-platforms-api";

// Re-export withErrorHandling for backward compatibility
export { withErrorHandling };

// Basic Post and Account type definitions for backward compatibility
export interface Post {
  id: number;
  status: string;
  account_type?: string;
  publish_at?: string;
  published_at?: string;
  created_at: string;
  updated_at?: string;
  error?: string;
  published?: boolean;
  draft?: boolean;
  can_edit?: boolean;
  content: string;
  account_id?: number;
  attachments?: Array<{
    type: string;
    url: string;
  }>;
}

export interface Account {
  id: number;
  name: string;
  platform?: string;
  account_type?: string;
}

// Compatibility function to provide the getSocialBuAPI functionality
export function getSocialBuAPI() {
  // Add missing methods to the socialPlatformsApi if they don't exist
  if (!socialPlatformsApi.deletePost) {
    socialPlatformsApi.deletePost = async (id: number) => {
      console.log(`[Mock] Deleting post ${id}`);
      return { success: true };
    };
  }
  
  // Make sure we have all the methods that might be used
  const enhancedApi = {
    ...socialPlatformsApi,
    getPosts: socialPlatformsApi.getPosts || (async (params: any = {}) => {
      console.log('[Mock] Getting posts with params:', params);
      return [];
    }),
    getAccounts: socialPlatformsApi.getAccounts || (async () => {
      console.log('[Mock] Getting accounts');
      return [];
    }),
    deletePost: socialPlatformsApi.deletePost || (async (id: number) => {
      console.log(`[Mock] Deleting post ${id}`);
      return { success: true };
    })
  };
  
  // Return the enhanced socialPlatformsApi
  return enhancedApi;
}

export class AuthAPI {
  private readonly backendBase =
    process.env.API_URL || "http://localhost:8000";

  // Redirect to link a social account
  link(provider: "google" | "facebook" | "linkedin" | "twitter") {
    let url;
    if (provider === "linkedin") {
      url = `${this.backendBase}/accounts/oidc/${provider}/login/?process=connect`;
    } else {
      url = `${this.backendBase}/accounts/${provider}/login/?process=connect`;
    }
    window.location.href = url;
  }
}

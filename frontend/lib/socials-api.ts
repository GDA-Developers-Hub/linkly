import { withErrorHandling as originalWithErrorHandling } from "./api";

// Re-export withErrorHandling for backward compatibility
export const withErrorHandling = originalWithErrorHandling;

// Add mock getSocialBuAPI function
export const getSocialBuAPI = () => {
  // This is a mock implementation to satisfy imports
  return {
    accounts: {
      list: async () => {
        return {
          items: [
            { id: 1, name: "Facebook Page", platform: "facebook", account_type: "page" },
            { id: 2, name: "Instagram", platform: "instagram", account_type: "profile" },
            { id: 3, name: "Twitter", platform: "twitter", account_type: "profile" }
          ]
        };
      },
      get: async (id: number) => {
        const accounts = [
          { id: 1, name: "Facebook Page", platform: "facebook", account_type: "page" },
          { id: 2, name: "Instagram", platform: "instagram", account_type: "profile" },
          { id: 3, name: "Twitter", platform: "twitter", account_type: "profile" }
        ];
        return accounts.find(account => account.id === id);
      }
    },
    posts: {
      list: async () => {
        return {
          items: [
            {
              id: 1,
              status: "published",
              account_id: 1,
              created_at: new Date().toISOString(),
              published_at: new Date().toISOString(),
              content: "Sample published post"
            },
            {
              id: 2,
              status: "scheduled",
              account_id: 2,
              created_at: new Date().toISOString(),
              publish_at: new Date(Date.now() + 86400000).toISOString(),
              content: "Sample scheduled post"
            }
          ]
        };
      }
    }
  };
};

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

// export class AuthAPI {
export class AuthAPI {
    private readonly backendBase =
      process.env.NEXT_PUBLIC_API_URL || 
      process.env.API_URL || 
      (process.env.NODE_ENV === "development" 
        ? "http://localhost:8000"
        : "https://linkly-production-f31e.up.railway.app");
  
    // Redirect to link a social account
    link(provider: "google" | "facebook" | "linkedin" | "twitter") {
      const token = localStorage.getItem("linkly_access_token");
      let url;
  
      if (provider === "linkedin") {
        url = `${this.backendBase}/accounts/oidc/${provider}/login/?process=connect&token=${token}`;
      } else {
        url = `${this.backendBase}/accounts/${provider}/login/?process=connect&token=${token}`;
      }
  
      window.location.href = url;
    }
  }

  
  
import { withErrorHandling as originalWithErrorHandling } from "./api";

// Re-export withErrorHandling for backward compatibility
export const withErrorHandling = originalWithErrorHandling;

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

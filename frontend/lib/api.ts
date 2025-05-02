// API client for our Django backend
import { toast } from "@/components/ui/use-toast"

// API Base URL with trailing slash for consistency
const API_BASE_URL = "https://linkly-production.up.railway.app/api/"

// API request helper function to ensure URLs are properly formed with trailing slashes
const buildUrl = (endpoint: string): string => {
  console.log(`Original endpoint: "${endpoint}"`);
  
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint.substring(1) : endpoint;
  console.log(`After removing leading slash: "${cleanEndpoint}"`);
  
  // Always add trailing slash
  const endpointWithSlash = cleanEndpoint.endsWith("/") ? cleanEndpoint : `${cleanEndpoint}/`;
  console.log(`After ensuring trailing slash: "${endpointWithSlash}"`);
  
  // Construct URL
  const url = `${API_BASE_URL}${endpointWithSlash}`;
  console.log(`Final URL: "${url}"`);
  
  return url;
}

// Types
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  account_type: "personal" | "business"
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginResponse {
  user: User
  tokens: AuthTokens
}

export interface RegisterData {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  account_type: "personal" | "business"
}

export interface LoginData {
  email: string
  password: string
}

export interface Plan {
  id: number
  name: string
  description: string
  price: string
  slug: string
  frequency: string
  post_limit: number
  account_limit: number
  team_members: number
  analytics_access: boolean
  ai_generation: boolean
  post_scheduling: boolean
  calendar_view: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Subscription {
  id: number
  plan: Plan
  status: string
  current_period_end: string
  cancel_at_period_end: boolean
}

export interface Caption {
  id?: number
  text: string
  platform: string
  date_created?: string
  hashtags?: string[]
}

export interface HashtagGroup {
  id?: number
  name: string
  hashtags?: string[] | Hashtag[]
  hashtag_names?: string[]
  platform?: string
}

export interface Hashtag {
  id?: number;
  name: string;
  hashtag?: string; // Keep for backward compatibility
  post_count?: number;
  growth_rate?: number;
  engagement_rate?: number;
  is_trending?: boolean;
  last_updated?: string;
  // Keep these for backward compatibility
  posts?: number;
  growth?: number;
  engagement?: number;
  difficulty?: number;
  platforms?: string[];
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface SocialMediaAccount {
  id: string
  platform: string
  username: string
  profile_picture?: string
  access_token?: string
  account_type?: string
  connected_at?: string
  last_used?: string
  status?: string
}

export interface InsightsParams {
  account_id: number
  date_from: string
  date_to: string
}

export interface InsightMetric {
  value: number
  change?: number
  trend?: 'up' | 'down' | 'stable'
}

export interface AccountInsights {
  followers: InsightMetric
  engagement_rate: InsightMetric
  reach: InsightMetric
  impressions: InsightMetric
  profile_views: InsightMetric
  post_count: InsightMetric
  period: {
    start: string
    end: string
  }
}

// Error handling wrapper
export async function withErrorHandling<T>(fn: () => Promise<T>, errorMessage = "An error occurred"): Promise<T> {
  try {
    return await fn()
  } catch (error: any) {
    console.error(error)
    toast({
      title: "Error",
      description: error.message || errorMessage,
      variant: "destructive",
    })
    throw error
  }
}

// API Client
class API {
  private accessToken: string | null = null
  private refreshToken: string | null = null

  constructor() {
    // Try to get tokens from localStorage
    if (typeof window !== "undefined") {
      this.accessToken = localStorage.getItem("linkly_access_token")
      this.refreshToken = localStorage.getItem("linkly_refresh_token")
    }
  }

  // Set tokens
  setTokens(tokens: AuthTokens) {
    this.accessToken = tokens.access
    this.refreshToken = tokens.refresh

    if (typeof window !== "undefined") {
      localStorage.setItem("linkly_access_token", tokens.access)
      localStorage.setItem("linkly_refresh_token", tokens.refresh)
    }
  }

  // Clear tokens
  clearTokens() {
    this.accessToken = null
    this.refreshToken = null

    if (typeof window !== "undefined") {
      localStorage.removeItem("linkly_access_token")
      localStorage.removeItem("linkly_refresh_token")
    }
  }

  // Check if authenticated
  isAuthenticated(): boolean {
    return !!this.accessToken
  }

  // Get access token
  getAccessToken(): string | null {
    return this.accessToken
  }

  // Get headers
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    }

    if (this.accessToken) {
      headers["Authorization"] = `Bearer ${this.accessToken}`
      console.log(`Adding Authorization header: Bearer ${this.accessToken.substring(0, 10)}...`);
    } else {
      console.warn("No access token available for request!");
      
      // Try to retrieve token again from localStorage as a fallback
      if (typeof window !== "undefined") {
        const storedToken = localStorage.getItem("linkly_access_token");
        if (storedToken) {
          console.log("Found token in localStorage, using it for this request");
          this.accessToken = storedToken;
          headers["Authorization"] = `Bearer ${storedToken}`;
        }
      }
    }

    return headers
  }

  // Refresh token
  private async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false

    try {
      const response = await fetch(buildUrl("users/token/refresh/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh: this.refreshToken }),
      })

      if (response.ok) {
        const data = await response.json()
        this.accessToken = data.access

        if (typeof window !== "undefined") {
          localStorage.setItem("linkly_access_token", data.access)
        }

        return true
      }

      return false
    } catch (error) {
      console.error("Error refreshing token:", error)
      return false
    }
  }

  // API request with token refresh
  async request<T>(endpoint: string, method = "GET", data?: any): Promise<T> {
    const url = buildUrl(endpoint);
    const options: RequestInit = {
      method,
      headers: this.getHeaders(),
    }

    if (data) {
      options.body = JSON.stringify(data)
    }

    console.log(`API Request to ${url}`, { 
      hasAccessToken: !!this.accessToken,
      hasRefreshToken: !!this.refreshToken,
      method
    });

    let response = await fetch(url, options)

    // Log response status
    console.log(`API Response from ${url}:`, { 
      status: response.status,
      ok: response.ok
    });

    // If unauthorized, try to refresh token
    if (response.status === 401 && this.refreshToken) {
      console.log("Token expired, attempting refresh");
      const refreshed = await this.refreshAccessToken()

      if (refreshed) {
        // Retry with new token
        console.log("Token refreshed successfully, retrying request");
        options.headers = this.getHeaders()
        response = await fetch(url, options)
        console.log(`API Retry Response from ${url}:`, { 
          status: response.status,
          ok: response.ok
        });
      } else {
        // Clear tokens and throw error
        console.log("Token refresh failed, clearing tokens");
        this.clearTokens()
        throw new Error("Session expired. Please log in again.")
      }
    }

    if (!response.ok) {
      // Try to parse response body as JSON
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        // If response is not JSON, use text or status
        try {
          const text = await response.text();
          errorData = { detail: text || `Request failed with status ${response.status}` };
        } catch (textError) {
          errorData = { detail: `Request failed with status ${response.status}` };
        }
      }
      
      console.error(`API Error for ${url}:`, errorData);
      
      // Create a more descriptive error message
      let errorMessage = "An error occurred while processing your request.";
      
      if (errorData.detail) {
        errorMessage = errorData.detail;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      } else if (errorData.error) {
        errorMessage = typeof errorData.error === 'string' ? errorData.error : JSON.stringify(errorData.error);
      }
      
      // Check for specific OpenAI related errors
      if (endpoint.includes('generate-caption') || endpoint.includes('generate-hashtags')) {
        if (response.status === 500) {
          errorMessage = "AI generation service is currently unavailable. This may be due to missing API keys or service disruption.";
        }
      }
      
      const error: any = new Error(errorMessage);
      
      // Attach the response data to the error for better error handling
      error.response = { 
        status: response.status,
        data: errorData 
      };
      
      throw error;
    }

    // Try to parse response as JSON
    try {
      return await response.json();
    } catch (e) {
      // Handle empty or non-JSON responses
      console.error(`Failed to parse JSON from ${url}:`, e);
      if (response.status === 204) { // No content
        return {} as T;
      }
      throw new Error("Invalid response format from server");
    }
  }

  // Authentication
  async register(data: RegisterData): Promise<LoginResponse> {
    try {
      console.log("API: Starting registration process", { email: data.email });
      
      const response = await this.request<LoginResponse>("/users/register/", "POST", data);
      console.log("API: Registration successful", { 
        userId: response.user.id,
        email: response.user.email,
        tokensReceived: !!response.tokens
      });
      
      this.setTokens(response.tokens);
      console.log("API: Auth tokens stored in local storage");
      
      // Note: SocialBu registration is handled on the backend during user creation,
      // and the tokens are stored there. We don't need to do anything additional here.
      console.log("API: SocialBu registration is handled on the backend");
      
      return response;
    } catch (error: any) {
      console.error("API: Registration error:", error);
      console.error("API: Registration error response:", error.response?.data);
      throw error;
    }
  }

  async login(data: LoginData): Promise<LoginResponse> {
    try {
      console.log("API: Starting login process", { email: data.email });
      
      // Explicitly use endpoint with trailing slash
      const response = await this.request<LoginResponse>("users/login/", "POST", data)
      console.log("API: Login successful, response:", response);
      console.log("API: Tokens received:", response.tokens);
      
      if (!response.tokens) {
        console.error("API: No tokens in login response!");
        throw new Error("No authentication tokens received from server");
      }
      
      this.setTokens(response.tokens)
      console.log("API: Auth tokens stored in local storage");
      
      // Try to auto-authenticate with SocialBu
      await this.ensureSocialBuAuthentication();
      
      return response
    } catch (error: any) {
      console.error("Login API error:", error)
      // If there's a specific authentication error, enhance the message
      if (error.response?.status === 401) {
        const enhancedError: any = new Error("Invalid email or password. Please check your credentials and try again.")
        enhancedError.response = error.response
        throw enhancedError
      }
      throw error
    }
  }

  // Helper method to ensure SocialBu authentication
  private async ensureSocialBuAuthentication(): Promise<void> {
    try {
      // This endpoint will automatically try to authenticate with SocialBu
      // using the stored credentials in the user model
      console.log("Attempting to authenticate with SocialBu accounts endpoint");
      
      // Use an empty object for the body to prevent JSON parsing errors
      await this.request("socialbu/accounts/", "GET", undefined);
      
      console.log("Successfully authenticated with SocialBu");
    } catch (error) {
      console.error("Error authenticating with SocialBu (will retry later):", error);
      // We don't throw the error since this is a non-critical operation
      // The backend will retry authentication when needed
    }
  }

  // Get SocialBu user information
  async getSocialBuUserInfo(): Promise<{
    has_token: boolean;
    user_id?: string;
    name?: string;
    email?: string;
    verified?: boolean;
    created_at?: string;
    updated_at?: string;
  }> {
    try {
      console.log("Fetching SocialBu user info from backend");
      
      // Ensure we have the access token
      const accessToken = this.getAccessToken();
      console.log(`Using access token for SocialBu request: ${accessToken ? 'Token exists' : 'No token'}`);
      
      // Make the request (the token is automatically included in headers via getHeaders method)
      const response = await this.request<any>("socialbu/user_info/", "GET");
      return response;
    } catch (error) {
      console.error("Error fetching SocialBu user info:", error);
      return { has_token: false};
    }
  }

  async logout(): Promise<void> {
    try {
      await this.request("/users/logout/", "POST", { refresh: this.refreshToken })
    } catch (error) {
      console.error("Error during logout:", error)
    } finally {
      this.clearTokens()
    }
  }

  async getProfile(): Promise<User> {
    return this.request<User>("/users/profile/")
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    return this.request<User>("/users/profile/", "PUT", data)
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.request<{ message: string }>("/users/change-password/", "POST", {
      old_password: oldPassword,
      new_password: newPassword,
    })
  }

  // Subscriptions
  async getPlans(): Promise<Plan[]> {
    const response = await this.request<PaginatedResponse<Plan>>("/subscriptions/plans/")
    return response.results || []
  }

  async getCurrentSubscription(): Promise<Subscription | null> {
    try {
      return await this.request<Subscription>("/subscriptions/subscription/")
    } catch (error) {
      if ((error as Error).message.includes("No subscription found")) {
        return null
      }
      throw error
    }
  }

  async createSubscription(planId: number, paymentMethodId: string = "dummy-payment"): Promise<Subscription> {
    return this.request<Subscription>("/subscriptions/subscription/", "POST", {
      plan_id: planId
    })
  }

  async cancelSubscription(): Promise<{ message: string }> {
    return this.request<{ message: string }>("/subscriptions/subscription/", "DELETE")
  }

  // Caption Generator
  async generateCaption(
    prompt: string,
    platform: string,
    tone: string,
    length: number,
    includeHashtags: boolean,
    mediaId?: number,
  ): Promise<{ caption: Caption; tokens_used: number }> {
    return this.request<{ caption: Caption; tokens_used: number }>("/content/generate-caption/", "POST", {
      prompt,
      platform,
      tone,
      length,
      include_hashtags: includeHashtags,
      media_id: mediaId,
    });
  }

  async getSavedCaptions(): Promise<Caption[]> {
    return this.request<Caption[]>("/content/saved-captions/")
  }

  async saveCaption(caption: Omit<Caption, "id" | "date_created">): Promise<Caption> {
    return this.request<Caption>("/content/saved-captions/", "POST", caption)
  }

  // Hashtag Generator
  async getTrendingHashtags(platform = "all", limit = 20): Promise<Hashtag[]> {
    return this.request<Hashtag[]>(`/content/hashtags/trending/?platform=${platform}&limit=${limit}`)
  }

  async getRelatedHashtags(hashtag: string, platform = "all", limit = 20): Promise<Hashtag[]> {
    return this.request<Hashtag[]>(`/content/hashtags/related/?hashtag=${hashtag}&platform=${platform}&limit=${limit}`)
  }

  async generateHashtags(
    keywords: string[],
    platform: string,
    contentType: string,
    count: number,
    popularityMix: string,
  ): Promise<Hashtag[]> {
    return this.request<{ hashtags: Hashtag[] }>("/content/generate-hashtags/", "POST", {
      query: Array.isArray(keywords) ? keywords.join(", ") : keywords,
      platform,
      content_type: contentType,
      count,
      popularity_mix: popularityMix,
    }).then(response => response.hashtags);
  }

  async getSavedHashtagGroups(): Promise<HashtagGroup[]> {
    return this.request<HashtagGroup[]>("/content/hashtag-groups/")
  }

  async saveHashtagGroup(group: Omit<HashtagGroup, "id">): Promise<HashtagGroup> {
    // Convert hashtags array to hashtag_names if it exists and is an array of strings
    const payload: any = { ...group };
    
    if (Array.isArray(payload.hashtags)) {
      // If hashtags contains objects, extract names
      if (typeof payload.hashtags[0] !== 'string') {
        payload.hashtag_names = payload.hashtags.map((tag: any) => 
          typeof tag === 'string' ? tag : (tag.name || tag.hashtag)
        );
      } else {
        payload.hashtag_names = payload.hashtags;
      }
      delete payload.hashtags;
    }
    
    return this.request<HashtagGroup>("/content/hashtag-groups/", "POST", payload);
  }

  // Media upload
  async uploadMedia(file: File): Promise<{ url: string; id: number }> {
    const formData = new FormData()
    formData.append("file", file)
    
    // Determine media type from the file's content type
    let mediaType = 'image'
    if (file.type.startsWith('video/')) {
      mediaType = 'video'
    } else if (file.type.startsWith('image/gif')) {
      mediaType = 'gif'
    }
    
    // Add the media_type field to the form data
    formData.append("media_type", mediaType)

    const response = await fetch(buildUrl("content/media/"), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
      },
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || errorData.message || `Upload failed with status ${response.status}`
      throw new Error(errorMessage)
    }

    return await response.json()
  }

  // SocialBu API methods
  async getAccounts(): Promise<SocialMediaAccount[]> {
    return this.request<SocialMediaAccount[]>("socialbu/accounts/")
  }

  async getInsights(params: InsightsParams): Promise<AccountInsights> {
    const queryParams = new URLSearchParams({
      account_id: params.account_id.toString(),
      date_from: params.date_from,
      date_to: params.date_to,
    }).toString()
    
    return this.request<AccountInsights>(`socialbu/insights/?${queryParams}`)
  }
}

// Singleton instance
let apiInstance: API | null = null

// Get API instance
export function getAPI(): API {
  if (!apiInstance) {
    apiInstance = new API()
  }
  return apiInstance
}

export function getSocialBuAPI(token: string): API {
  const api = new API()
  api.setTokens({ access: token, refresh: "" })
  return api
}

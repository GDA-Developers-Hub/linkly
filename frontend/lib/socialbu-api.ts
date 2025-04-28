import { toast } from "@/components/ui/use-toast"
import { getAPI } from "@/lib/api"

// Base URL for SocialBu
const SOCIALBU_BASE_URL = "https://socialbu.com/api/v1"

// Types
export interface Account {
  id: number
  name: string
  platform: string
  type: string
  status: string
  connected_at: string
}

export interface Post {
  id: number
  content: string
  platforms: string[]
  media: Media[]
  status: string
  scheduled_at: string | null
  published_at: string | null
  created_at: string
}

export interface Media {
  id: number
  url: string
  type: string
  created_at: string
}

export interface Insight {
  platform: string
  metric: string
  value: number
  change: number
  period: string
}

export interface Notification {
  id: number
  type: string
  message: string
  read: boolean
  created_at: string
}

export interface Team {
  id: number
  name: string
  created_at: string
}

export interface TeamMember {
  id: number
  name: string
  email: string
  role: string
  joined_at: string
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

// SocialBu API Client
class SocialBuAPI {
  private api = getAPI()
  private baseUrl = SOCIALBU_BASE_URL

  // Store SocialBu authentication state in localStorage
  storeAuthState(authState: {
    authenticated: boolean;
    userData?: {
      name?: string;
      email?: string;
      verified?: boolean;
      user_id?: string;
    }
  }): void {
    if (typeof window !== "undefined") {
      localStorage.setItem("socialbu_auth_state", JSON.stringify(authState));
      console.log("Stored SocialBu auth state in localStorage:", authState);
    }
  }

  // Load SocialBu authentication state from localStorage
  loadAuthState(): {
    authenticated: boolean;
    userData?: {
      name?: string;
      email?: string;
      verified?: boolean;
      user_id?: string;
    }
  } {
    if (typeof window !== "undefined") {
      const storedState = localStorage.getItem("socialbu_auth_state");
      if (storedState) {
        try {
          const parsedState = JSON.parse(storedState);
          console.log("Loaded SocialBu auth state from localStorage:", parsedState);
          return parsedState;
        } catch (e) {
          console.error("Error parsing stored auth state:", e);
        }
      }
    }
    return { authenticated: false };
  }

  // Check if authenticated
  isAuthenticated(): boolean {
    const authState = this.loadAuthState();
    return authState.authenticated;
  }

  // Check if user has valid token
  async checkToken(): Promise<boolean> {
    try {
      // Get user info from the backend using the central API client
      const userInfo = await this.api.getSocialBuUserInfo();
      
      // Log the response for debugging
      console.log('SocialBu user info response:', userInfo);
      
      // Store authentication state in localStorage
      const isAuthenticated = userInfo.has_token;
      this.storeAuthState({
        authenticated: isAuthenticated,
        userData: isAuthenticated ? {
          name: userInfo.name,
          email: userInfo.email,
          verified: userInfo.verified,
          user_id: userInfo.user_id
        } : undefined
      });
      
      // Check if we have a token and if it's valid
      return userInfo.has_token;
    } catch (error) {
      console.error("Error checking token:", error);
      this.storeAuthState({ authenticated: false });
      return false;
    }
  }

  // Get user's SocialBu info from the backend
  async getUserInfo(): Promise<{
    has_token: boolean;
    user_id?: string;
    name?: string;
    email?: string;
    verified?: boolean;
    created_at?: string;
    updated_at?: string;
  }> {
    try {
      // First try to get from localStorage
      const authState = this.loadAuthState();
      if (authState.authenticated && authState.userData) {
        console.log("Using cached SocialBu user info from localStorage");
        return {
          has_token: true,
          ...authState.userData,
        };
      }
      
      // If no cached data, use the central API client
      console.log("Fetching fresh SocialBu user info from API");
      return this.api.getSocialBuUserInfo();
    } catch (error) {
      console.error("Error in getUserInfo:", error);
      return { has_token: false };
    }
  }

  // Register a new account
  async register(name: string, email: string, password: string): Promise<void> {
    // Call the SocialBu registration endpoint directly
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || errorData.message || `Registration failed with status ${response.status}`
      throw new Error(errorMessage)
    }
  }

  // Authentication
  async authenticate(email: string, password: string): Promise<{ token: string }> {
    // Use our backend proxy to avoid CORS issues
    try {
      console.log("Attempting authentication with SocialBu");
      console.log("Base URL:", this.baseUrl);
      
      // IMPORTANT: Do not use leading slash to avoid incorrect URL construction
      const result = await this.api.request<{ token: string; user_id?: string; name?: string; email?: string }>(
        "socialbu/authenticate", 
        "POST", 
        { 
          email, 
          password, 
          base_url: this.baseUrl 
        }
      );
      
      if (!result.token) {
        throw new Error("Authentication failed: No token received");
      }
      
      // Store authentication state
      this.storeAuthState({
        authenticated: true,
        userData: {
          name: result.name,
          email: result.email,
          user_id: result.user_id
        }
      });
      
      return { token: result.token };
    } catch (error: any) {
      const errorMessage = error.message || "Authentication failed";
      console.error("Authentication error:", errorMessage);
      
      // Clear authentication state
      this.storeAuthState({ authenticated: false });
      
      throw error;
    }
  }

  async getConnectionUrl(provider: string, accountId?: string): Promise<{ url: string }> {
    // Get the app URL dynamically from the environment
    // const appUrl = process.env.NEXT_PUBLIC_API_URL;
    const appUrl = "https://cd7b-41-139-175-41.ngrok-free.app/api";
    // Build the proper postback URL
    const postbackUrl = `${appUrl}/socialbu/connection-callback/`;
    
    // Get account ID (user_id) from localStorage that has your user data
    let account_Id = '';  
    // Check localStorage for authentication data
    const keys = Object.keys(localStorage);
    for (const key of keys) {
      try {
        const value = JSON.parse(localStorage.getItem(key) || '');
        if (value && value.authenticated && value.userData && value.userData.user_id) {
          account_Id = value.userData.user_id;
          break;
        }
      } catch (e) {
        // Skip this key if it doesn't contain valid JSON
        console.log(`Skipping key: ${key}, not valid JSON`);
      }
    }

    
    // Prepare payload according to the SocialBu API requirements
    const payload: { 
      provider: string; 
      postback_url: string;
      account_id?: string;
    } = { 
      provider, 
      postback_url: postbackUrl,
      account_id: account_Id
    };
    
    
    // Get Linkly access token from localStorage
    let linklyAccessToken = '';
    if (typeof window !== 'undefined') {
      linklyAccessToken = localStorage.getItem('linkly_access_token') || '';
    }
    
    // Determine the base URL for the backend
    const baseApiUrl = process.env.NEXT_PUBLIC_API_URL || window.location.origin;
    const response = await fetch(`${baseApiUrl}/socialbu/get_connection_url/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(linklyAccessToken ? { 'Authorization': `Bearer ${linklyAccessToken}` } : {})
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || errorData.message || `Failed to get connection URL with status ${response.status}`;
      throw new Error(errorMessage);
    }
    
    return await response.json();
  }

  // Open a popup for social platform connection
  openConnectionPopup(provider: string): Promise<{ platform: string; accountId: string; accountName: string }> {
    return new Promise(async (resolve, reject) => {
      try {
        console.log('[SocialBu] openConnectionPopup called for provider:', provider);
        // Get connection URL
        const { url } = await this.getConnectionUrl(provider)

        // Calculate popup dimensions
        const width = 600
        const height = 700
        const left = window.innerWidth / 2 - width / 2
        const top = window.innerHeight / 2 - height / 2

        // Open popup
        const popup = window.open(
          url,
          `Connect ${provider}`,
          `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`,
        )

        if (!popup) {
          throw new Error("Popup blocked. Please allow popups for this site.")
        }

        // Listen for message from popup
        const messageHandler = (event: MessageEvent) => {
          console.log('[SocialBu] openConnectionPopup received message:', event.data);
          if (event.data && event.data.type === "SOCIAL_CONNECTION_SUCCESS") {
            window.removeEventListener("message", messageHandler)
            resolve({
              platform: event.data.platform,
              accountId: event.data.accountId,
              accountName: event.data.accountName,
            })
          }
        }

        window.addEventListener("message", messageHandler)

        // Check if popup was closed
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed)
            window.removeEventListener("message", messageHandler)
            reject(new Error("Connection was cancelled."))
          }
        }, 500)
      } catch (error) {
        reject(error)
      }
    })
  }

  // Posts
  async getPosts(limit?: number, status?: string): Promise<Post[]> {
    // Do not use leading slash
    let endpoint = "socialbu/posts"
    const params = [`base_url=${this.baseUrl}`]

    if (limit) {
      params.push(`limit=${limit}`)
    }

    if (status) {
      params.push(`status=${status}`)
    }

    endpoint += `?${params.join("&")}`

    return this.api.request<Post[]>(endpoint)
  }

  async createPost(content: string, platforms: string[], mediaIds?: number[], scheduledAt?: Date): Promise<Post> {
    const data: any = {
      content,
      platforms,
      base_url: this.baseUrl
    }

    if (mediaIds && mediaIds.length > 0) {
      data.media_ids = mediaIds
    }

    if (scheduledAt) {
      data.scheduled_at = scheduledAt.toISOString()
    }

    // Do not use leading slash
    return this.api.request<Post>("socialbu/create_post", "POST", data)
  }

  async updatePost(postId: number, data: Partial<Post>): Promise<Post> {
    // Do not use leading slash
    return this.api.request<Post>(`socialbu/update_post/${postId}`, "PUT", {
      ...data,
      base_url: this.baseUrl
    })
  }

  async deletePost(postId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/delete_post/${postId}?base_url=${this.baseUrl}`, "DELETE")
  }

  // Media
  async getMedia(): Promise<Media[]> {
    // Remove leading slash
    return this.api.request<Media[]>(`socialbu/media?base_url=${this.baseUrl}`)
  }

  async uploadMedia(file: File): Promise<Media> {
    const formData = new FormData()
    formData.append("media", file)
    formData.append("base_url", this.baseUrl)

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/socialbu/upload_media`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.api.getAccessToken()}`,
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

  async deleteMedia(mediaId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/delete_media/${mediaId}?base_url=${this.baseUrl}`, "DELETE")
  }

  // Accounts
  async getAccounts(): Promise<Account[]> {
    // Remove leading slash
    return this.api.request<Account[]>(`socialbu/accounts?base_url=${this.baseUrl}`)
  }

  async disconnectAccount(accountId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/disconnect_account/${accountId}?base_url=${this.baseUrl}`, "DELETE")
  }

  // Insights
  async getInsights(): Promise<Insight[]> {
    // Remove leading slash
    return this.api.request<Insight[]>(`socialbu/insights?base_url=${this.baseUrl}`)
  }

  async getPostInsights(postId: number): Promise<Insight[]> {
    // Remove leading slash
    return this.api.request<Insight[]>(`socialbu/post_insights/${postId}?base_url=${this.baseUrl}`)
  }

  // Notifications
  async getNotifications(): Promise<Notification[]> {
    // Remove leading slash
    return this.api.request<Notification[]>(`socialbu/notifications?base_url=${this.baseUrl}`)
  }

  async markNotificationAsRead(notificationId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/mark_notification_read/${notificationId}`, "PUT", {
      base_url: this.baseUrl
    })
  }

  // Teams
  async createTeam(name: string): Promise<Team> {
    // Remove leading slash
    return this.api.request<Team>("socialbu/create_team", "POST", { 
      name,
      base_url: this.baseUrl
    })
  }

  async addTeamMember(teamId: number, userId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/add_team_member/${teamId}`, "POST", { 
      user_id: userId,
      base_url: this.baseUrl 
    })
  }

  async getTeamMembers(teamId: number): Promise<TeamMember[]> {
    // Remove leading slash
    return this.api.request<TeamMember[]>(`socialbu/team_members/${teamId}?base_url=${this.baseUrl}`)
  }

  async removeTeamMember(teamId: number, userId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/remove_team_member/${teamId}?user_id=${userId}&base_url=${this.baseUrl}`, "DELETE")
  }
}

// Singleton instance
let socialBuAPIInstance: SocialBuAPI | null = null

// Get SocialBu API instance
export function getSocialBuAPI(): SocialBuAPI {
  if (!socialBuAPIInstance) {
    socialBuAPIInstance = new SocialBuAPI()
  }
  return socialBuAPIInstance
}
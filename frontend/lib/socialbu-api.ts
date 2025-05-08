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
  status?: string
  connected_at?: string
  _type?: string
  image?: string
  active?: boolean
  attachment_types?: string[]
  post_maxlength?: number
  max_attachments?: number
  post_media_required?: boolean
}

export interface Post {
  id: number
  content: string
  post_hash?: string
  external_id?: string | null
  account_id: number
  account_type?: string
  type?: string
  attachments?: Array<{
    ext: string
    mime: string
    name: string
    path: string
    size: number
    type: string
    url: string
  }>
  post_options?: {
    post_as_story?: boolean
    postback_url?: string
    [key: string]: any
  }
  shortened_links?: any[]
  error?: string | null
  source?: string | null
  user_id?: number
  user_name?: string
  publish_at?: string | null
  created_at: string
  updated_at: string
  published_at: string | null
  published: boolean
  permalink?: string | null
  draft: boolean
  approved: boolean
  reject_reason?: string | null
  insights?: any | null
  can_edit?: boolean
  can_approve?: boolean
  status?: string
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

export interface PaginatedPosts {
  items: Post[];
  currentPage: number;
  lastPage: number;
  nextPage: number | null;
  total: number;
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
      
      // Ensure base URL doesn't include /api/v1 twice
      const baseUrl = this.baseUrl.endsWith('/api/v1') 
        ? this.baseUrl.substring(0, this.baseUrl.length - 7) // Remove /api/v1
        : this.baseUrl;
        
      console.log("Base URL for authentication:", baseUrl);
      
      // IMPORTANT: Do not use leading slash to avoid incorrect URL construction
      const result = await this.api.request<{ token: string; user_id?: string; name?: string; email?: string }>(
        "socialbu/authenticate", 
        "POST", 
        { 
          email, 
          password, 
          base_url: baseUrl 
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

  async getConnectionUrl(provider: string, accountId?: string): Promise<{ connect_url: string }> {
    // Get the app URL dynamically from the environment
    // const appUrl = process.env.NEXT_PUBLIC_API_URL;
    const appUrl = "https://186b-41-139-175-41.ngrok-free.app/api";
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

  openConnectionPopup(provider: string): Promise<{ platform: string; accountId: string; accountName: string }> {
    return new Promise(async (resolve, reject) => {
      try {
        console.log('[SocialBu] openConnectionPopup called for provider:', provider);
        
        // Get connection URL - adjust this to match your actual API response structure
        const response = await this.getConnectionUrl(provider);
        const url = response.connect_url;
        
        if (!url) {
          throw new Error('No connection URL received from server');
        }
  
        console.log('[SocialBu] Got connection URL:', url);
  
        // Calculate popup dimensions
        const width = 600;
        const height = 700;
        const left = window.innerWidth / 2 - width / 2;
        const top = window.innerHeight / 2 - height / 2;
  
        // Try to open popup
        const popup = window.open(
          url,
          `Connect ${provider}`,
          `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`,
        );
  
        if (!popup) {
          console.warn('[SocialBu] Popup was blocked by browser');
          
          // Alert user to enable popups
          if (confirm('Popup was blocked. Please enable popups and try again, or click OK to open in a new tab.')) {
            const newTab = window.open(url, '_blank');
            
            if (!newTab) {
              throw new Error("Both popup and new tab were blocked. Please allow popups or new tabs for this site.");
            }
            
            // Since we can't control the new tab, we'll just resolve after a delay
            setTimeout(() => {
              resolve({
                platform: provider,
                accountId: 'unknown',
                accountName: `${provider.charAt(0).toUpperCase() + provider.slice(1)} Account`
              });
            }, 5000);
          } else {
            throw new Error('Connection cancelled by user');
          }
          
          return;
        }
  
        // Listen for message from popup
        const messageHandler = (event: MessageEvent) => {
          console.log('[SocialBu] Received message:', event.data);
          
          // Check if the message is from our popup and has the expected format
          if (event.data && event.data.type === "SOCIAL_CONNECTION_SUCCESS") {
            window.removeEventListener("message", messageHandler);
            
            if (popup && !popup.closed) {
              popup.close();
            }
            
            resolve({
              platform: event.data.platform || provider,
              accountId: event.data.accountId || 'unknown',
              accountName: event.data.accountName || `${provider.charAt(0).toUpperCase() + provider.slice(1)} Account`,
            });
          }
        };
  
        window.addEventListener("message", messageHandler);
  
        // Check if popup was closed
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            window.removeEventListener("message", messageHandler);
            reject(new Error("Connection was cancelled."));
          }
        }, 500);
        
        // Set a timeout in case the popup doesn't respond
        setTimeout(() => {
          if (popup && !popup.closed) {
            // Don't close the popup, user might still be authenticating
            window.removeEventListener("message", messageHandler);
            clearInterval(checkClosed);
            reject(new Error("Connection timed out. Please try again."));
          }
        }, 120000); // 2 minutes timeout
        
      } catch (error) {
        console.error('[SocialBu] Connection error:', error);
        reject(error);
      }
    });
  }

  // Posts
  async getPosts(params?: {
    limit?: number;
    status?: string;
    page?: number;
    account_id?: number;
  }): Promise<PaginatedPosts> {
    // Do not use leading slash
    let endpoint = "socialbu/posts"
    const queryParams = [`base_url=${this.baseUrl}`]

    // Handle both legacy format (separate parameters) and object format
    if (params) {
      if (params.limit) {
        queryParams.push(`limit=${params.limit}`)
      }

      if (params.status) {
        queryParams.push(`status=${params.status}`)
      }

      if (params.page) {
        queryParams.push(`page=${params.page}`)
      }

      if (params.account_id) {
        queryParams.push(`account_id=${params.account_id}`)
      }
    } else if (arguments.length > 0) {
      // Legacy support for separate arguments
      const [limit, status, page] = arguments;
      
      if (limit) {
        queryParams.push(`limit=${limit}`)
      }

      if (status) {
        queryParams.push(`status=${status}`)
      }

      if (page) {
        queryParams.push(`page=${page}`)
      }
    }

    endpoint += `?${queryParams.join("&")}`
    
    console.log(`Fetching posts with endpoint: ${endpoint}`)
    
    const result = await this.api.request<PaginatedPosts>(endpoint)
    console.log(`Received posts response with ${result.items?.length || 0} items of ${result.total} total posts`)
    
    return result
  }

  async createPost(data: {
    accounts: number[];
    team_id?: number;
    publish_at?: string;
    content: string;
    draft?: boolean;
    existing_attachments?: Array<{ upload_token: string }>;
    postback_url?: string;
    platform?: string;
    options?: Record<string, any>;
  }): Promise<Post> {
    // Log the post creation request
    console.log('[SocialBu] Creating post with data:', JSON.stringify(data, null, 2));
    
    // If platform is not provided but accounts are, try to determine platform
    if (!data.platform && data.accounts && data.accounts.length > 0) {
      try {
        // Get accounts if not already cached
        const accounts = await this.getAccounts();
        const accountId = data.accounts[0];
        const account = accounts.find(acc => acc.id === accountId);
        
        if (account && account.platform) {
          data.platform = account.platform;
          console.log(`[SocialBu] Determined platform from account: ${data.platform}`);
        }
      } catch (error) {
        console.warn('[SocialBu] Could not determine platform from account:', error);
      }
    }
    
    // If we have a platform, filter options to only include relevant ones for that platform
    if (data.platform && data.options) {
      data.options = getPlatformOptions(data.platform, data.options);
      console.log(`[SocialBu] Using platform-specific options for ${data.platform}:`, data.options);
    }
    
    // Format the data according to SocialBu API requirements
    const postData = {
      ...data,
      base_url: this.baseUrl
    };

    try {
      // Do not use leading slash
      console.log('[SocialBu] Sending post creation request to socialbu/create_post');
      const result = await this.api.request<Post>("socialbu/create_post", "POST", postData);
      console.log('[SocialBu] Post creation successful:', JSON.stringify(result, null, 2));
      return result;
    } catch (error) {
      console.error('[SocialBu] Post creation failed:', error);
      throw error;
    }
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
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/socialbu/upload_media/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.api.getAccessToken()}`,
      },
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || errorData.message || `Upload failed with status ${response.status}`
      throw new Error(errorMessage)
    }

    const data = await response.json()
    
    // Return the media info from the response
    return {
      id: data.id,
      url: data.url,
      type: data.type,
      created_at: data.created_at
    }
  }

  async deleteMedia(mediaId: number): Promise<void> {
    // Remove leading slash
    return this.api.request<void>(`socialbu/delete_media/${mediaId}?base_url=${this.baseUrl}`, "DELETE")
  }

  // Accounts
  async getAccounts(): Promise<Account[]> {
    // Make a direct request to the SocialBu API endpoint
    const endpoint = `${this.baseUrl}/accounts`;
    
    // Get the Linkly access token from localStorage to use for the request
    let linklyAccessToken = '';
    if (typeof window !== 'undefined') {
      linklyAccessToken = localStorage.getItem('linkly_access_token') || '';
    }
    
    // Make the request using fetch API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/socialbu/accounts`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(linklyAccessToken ? { 'Authorization': `Bearer ${linklyAccessToken}` } : {})
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || errorData.message || `Failed to fetch accounts with status ${response.status}`;
      throw new Error(errorMessage);
    }
    
    return await response.json();
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

// Get platform-specific default options
export function getPlatformOptions(platform: string, baseOptions: Record<string, any> = {}): Record<string, any> {
  const options = { ...baseOptions };
  
  switch(platform.toLowerCase()) {
    case 'facebook':
      // Only include Facebook-specific options
      return {
        comment: options.comment,
        post_as_story: options.post_as_story
      };
      
    case 'instagram':
      return {
        post_as_reel: options.post_as_reel || false,
        post_as_story: options.post_as_story || false,
        share_reel_to_feed: options.share_reel_to_feed || false,
        comment: options.comment,
        thumbnail: options.thumbnail
      };
      
    case 'twitter':
    case 'x':
      return {
        media_alt_text: options.media_alt_text || [],
        threaded_replies: options.threaded_replies || []
      };
      
    case 'linkedin':
      return {
        link: options.link,
        trim_link_from_content: options.trim_link_from_content || false,
        customize_link: options.customize_link || false,
        link_description: options.link_description,
        link_title: options.link_title,
        thumbnail: options.thumbnail,
        comment: options.comment,
        document_title: options.document_title
      };
      
    case 'youtube':
      return {
        video_title: options.video_title,
        video_tags: options.video_tags,
        category_id: options.category_id,
        privacy_status: options.privacy_status,
        post_as_short: options.post_as_short || false,
        made_for_kids: options.made_for_kids || false
      };
      
    case 'tiktok':
      return {
        title: options.title,
        privacy_status: options.privacy_status,
        allow_stitch: options.allow_stitch !== undefined ? options.allow_stitch : true,
        allow_duet: options.allow_duet !== undefined ? options.allow_duet : true,
        allow_comment: options.allow_comment !== undefined ? options.allow_comment : true,
        disclose_content: options.disclose_content || false,
        branded_content: options.branded_content || false,
        own_brand: options.own_brand || false
      };
      
    default:
      // Return the default options for unknown platform
      return {
        comment: options.comment,
        post_as_story: options.post_as_story
      };
  }
}


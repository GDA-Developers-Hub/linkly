import { toast } from "@/components/ui/use-toast"
import { getAPI } from "@/lib/api"

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

  // Check if authenticated
  isAuthenticated(): boolean {
    return this.api.isAuthenticated()
  }

  // Authentication
  async authenticate(email: string, password: string): Promise<{ token: string }> {
    return this.api.request<{ token: string }>("/socialbu/authenticate/", "POST", { email, password })
  }

  // Social Platform Connection
  async getConnectionUrl(provider: string, accountId?: string): Promise<{ url: string }> {
    const data: any = { provider }
    if (accountId) {
      data.account_id = accountId
    }
    return this.api.request<{ url: string }>("/socialbu/get_connection_url/", "POST", data)
  }

  // Open a popup for social platform connection
  openConnectionPopup(provider: string): Promise<{ platform: string; accountId: string; accountName: string }> {
    return new Promise(async (resolve, reject) => {
      try {
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
    let endpoint = "/socialbu/posts/"
    const params = []

    if (limit) {
      params.push(`limit=${limit}`)
    }

    if (status) {
      params.push(`status=${status}`)
    }

    if (params.length > 0) {
      endpoint += `?${params.join("&")}`
    }

    return this.api.request<Post[]>(endpoint)
  }

  async createPost(content: string, platforms: string[], mediaIds?: number[], scheduledAt?: Date): Promise<Post> {
    const data: any = {
      content,
      platforms,
    }

    if (mediaIds && mediaIds.length > 0) {
      data.media_ids = mediaIds
    }

    if (scheduledAt) {
      data.scheduled_at = scheduledAt.toISOString()
    }

    return this.api.request<Post>("/socialbu/create_post/", "POST", data)
  }

  async updatePost(postId: number, data: Partial<Post>): Promise<Post> {
    return this.api.request<Post>(`/socialbu/update_post/${postId}/`, "PUT", data)
  }

  async deletePost(postId: number): Promise<void> {
    return this.api.request<void>(`/socialbu/delete_post/${postId}/`, "DELETE")
  }

  // Media
  async getMedia(): Promise<Media[]> {
    return this.api.request<Media[]>("/socialbu/media/")
  }

  async uploadMedia(file: File): Promise<Media> {
    const formData = new FormData()
    formData.append("media", file)

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/socialbu/upload_media/`, {
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
    return this.api.request<void>(`/socialbu/delete_media/${mediaId}/`, "DELETE")
  }

  // Accounts
  async getAccounts(): Promise<Account[]> {
    return this.api.request<Account[]>("/socialbu/accounts/")
  }

  async disconnectAccount(accountId: number): Promise<void> {
    return this.api.request<void>(`/socialbu/disconnect_account/${accountId}/`, "DELETE")
  }

  // Insights
  async getInsights(): Promise<Insight[]> {
    return this.api.request<Insight[]>("/socialbu/insights/")
  }

  async getPostInsights(postId: number): Promise<Insight[]> {
    return this.api.request<Insight[]>(`/socialbu/post_insights/${postId}/`)
  }

  // Notifications
  async getNotifications(): Promise<Notification[]> {
    return this.api.request<Notification[]>("/socialbu/notifications/")
  }

  async markNotificationAsRead(notificationId: number): Promise<void> {
    return this.api.request<void>(`/socialbu/mark_notification_read/${notificationId}/`, "PUT")
  }

  // Teams
  async createTeam(name: string): Promise<Team> {
    return this.api.request<Team>("/socialbu/create_team/", "POST", { name })
  }

  async addTeamMember(teamId: number, userId: number): Promise<void> {
    return this.api.request<void>(`/socialbu/add_team_member/${teamId}/`, "POST", { user_id: userId })
  }

  async getTeamMembers(teamId: number): Promise<TeamMember[]> {
    return this.api.request<TeamMember[]>(`/socialbu/team_members/${teamId}/`)
  }

  async removeTeamMember(teamId: number, userId: number): Promise<void> {
    return this.api.request<void>(`/socialbu/remove_team_member/${teamId}/?user_id=${userId}`, "DELETE")
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

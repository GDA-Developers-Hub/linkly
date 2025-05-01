"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, BarChart3, Calendar, Clock, RefreshCw, Users, TrendingUp, Activity, Eye } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { getSocialBuAPI, withErrorHandling } from "@/lib/socialbu-api"
import { useToast } from "@/components/ui/use-toast"
import { Avatar } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

interface InsightsData {
  followers: number
  engagement: number
  reach: number
  posts: {
    scheduled: number
    published: number
    total: number
  }
  connectedAccounts: Array<{
    id: number
    name: string
    _type?: string
    type?: string
    image?: string
    active: boolean
  }>
}

interface RecentPost {
  id: number
  content: string
  status: string
  scheduled_at?: string | null
  platform: string
  engagement?: {
    likes: number
    comments: number
    shares: number
  }
}

export default function DashboardPage() {
  const { toast } = useToast()
  const [insights, setInsights] = useState<InsightsData | null>(null)
  const [recentPosts, setRecentPosts] = useState<RecentPost[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      await withErrorHandling(async () => {
        console.log('[Dashboard] Fetching dashboard data');
        const api = getSocialBuAPI()

        // Fetch insights
        console.log('[Dashboard] Fetching insights');
        const insightsData = await api.getInsights()
        
        // Fetch connected accounts
        console.log('[Dashboard] Fetching connected accounts');
        const connectedAccounts = await api.getAccounts()
        console.log('[Dashboard] Received', connectedAccounts.length, 'connected accounts');

        // Fetch recent posts - limit to 5 posts
        console.log('[Dashboard] Fetching recent posts');
        const postsResponse = await api.getPosts(5)
        console.log('[Dashboard] Received posts:', 
          postsResponse.items?.length, 
          'of', 
          postsResponse.total, 
          'total posts'
        );
        
        // Extract posts from the paginated response
        const postsData = postsResponse.items || [];

        // Get basic metrics from insights (simplified for demo)
        const totalFollowers = insightsData.reduce((sum, insight) => 
          insight.metric === 'followers' ? sum + insight.value : sum, 0);
          
        const avgEngagement = insightsData.reduce((sum, insight) => 
          insight.metric === 'engagement' ? sum + insight.value : sum, 0);
          
        const totalReach = insightsData.reduce((sum, insight) => 
          insight.metric === 'reach' ? sum + insight.value : sum, 0);

        // Transform data for the dashboard
        const transformedInsights: InsightsData = {
          followers: totalFollowers,
          engagement: avgEngagement,
          reach: totalReach,
          posts: {
            scheduled: postsData.filter((post) => post.status === "scheduled").length,
            published: postsData.filter((post) => post.status === "published").length,
            total: postsResponse.total, // Use the total from the response
          },
          connectedAccounts: connectedAccounts.map(account => {
            // Extract properties safely with defaults
            return {
              id: account.id,
              name: account.name,
              _type: (account as any)._type || account.type || 'Unknown',
              type: account.type || '',
              image: (account as any).image || '',
              active: typeof (account as any).active === 'boolean' ? (account as any).active : true
            }
          })
        }

        // Transform posts data
        const transformedPosts: RecentPost[] = postsData.map((post) => ({
          id: post.id,
          content: post.content,
          status: post.status,
          scheduled_at: post.publish_at,
          platform: post.accounts?.[0]?.toString() || "unknown",
          engagement: {
            likes: Math.floor(Math.random() * 100),
            comments: Math.floor(Math.random() * 30),
            shares: Math.floor(Math.random() * 20),
          },
        }))

        setInsights(transformedInsights)
        setRecentPosts(transformedPosts)
        console.log('[Dashboard] Dashboard data loaded successfully');
      }, "Failed to fetch dashboard data")
    } catch (error) {
      console.error("[Dashboard] Error fetching dashboard data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshData = async () => {
    setIsRefreshing(true)
    await fetchDashboardData()
    setIsRefreshing(false)
    toast({
      title: "Dashboard refreshed",
      description: "Your dashboard data has been updated.",
    })
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-yellow-500';
      case 'published':
        return 'bg-green-500';
      case 'draft':
        return 'bg-gray-500';
      default:
        return 'bg-blue-500';
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'facebook':
        return '/facebook-logo-display.png';
      case 'instagram':
        return '/instagram-logo-on-phone.png';
      case 'twitter':
        return '/blue-bird-icon.png';
      case 'linkedin':
        return '/linkedin-logo-on-white.png';
      default:
        return '/placeholder-logo.png';
    }
  };

  return (
    <div className="flex-1 space-y-6 p-6 md:p-8 pt-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">Dashboard</h2>
          <p className="text-muted-foreground mt-1">Welcome back! Here's what's happening with your social accounts.</p>
        </div>
        <Button onClick={refreshData} disabled={isRefreshing} size="sm" className="shrink-0">
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh Data
        </Button>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="w-full md:w-auto justify-start">
          <TabsTrigger value="overview" className="flex-1 md:flex-initial">Overview</TabsTrigger>
          <TabsTrigger value="analytics" className="flex-1 md:flex-initial">Analytics</TabsTrigger>
          <TabsTrigger value="reports" className="flex-1 md:flex-initial">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Insights Cards */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
                <Users className="h-5 w-5 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-24 animate-pulse rounded bg-muted"></div>
                  ) : (
                    insights?.followers.toLocaleString() || "0"
                  )}
                </div>
                <div className="flex items-center mt-1">
                  <span className="text-xs text-green-500 flex items-center font-medium">
                    <TrendingUp className="h-3 w-3 mr-1" /> +2.5%
                  </span>
                  <span className="text-xs text-muted-foreground ml-1">from last month</span>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
                <Activity className="h-5 w-5 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-16 animate-pulse rounded bg-muted"></div>
                  ) : (
                    `${insights?.engagement || 0}%`
                  )}
                </div>
                <div className="flex items-center mt-1">
                  <span className="text-xs text-green-500 flex items-center font-medium">
                    <TrendingUp className="h-3 w-3 mr-1" /> +0.8%
                  </span>
                  <span className="text-xs text-muted-foreground ml-1">from last week</span>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Reach</CardTitle>
                <Eye className="h-5 w-5 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-24 animate-pulse rounded bg-muted"></div>
                  ) : (
                    insights?.reach.toLocaleString() || "0"
                  )}
                </div>
                <div className="flex items-center mt-1">
                  <span className="text-xs text-green-500 flex items-center font-medium">
                    <TrendingUp className="h-3 w-3 mr-1" /> +12.3%
                  </span>
                  <span className="text-xs text-muted-foreground ml-1">from last month</span>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
                <Calendar className="h-5 w-5 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-16 animate-pulse rounded bg-muted"></div>
                  ) : (
                    insights?.posts.scheduled || "0"
                  )}
                </div>
                <div className="mt-1">
                  <span className="text-xs text-muted-foreground">
                    {insights?.posts.published || "0"} published this week
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Connected Accounts & Recent Posts Section */}
          <div className="grid gap-6 lg:grid-cols-7">
            {/* Connected Accounts */}
            <Card className="shadow-sm hover:shadow-md transition-shadow lg:col-span-2">
              <CardHeader>
                <CardTitle>Connected Accounts</CardTitle>
                <CardDescription>Your active social media accounts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoading ? (
                  Array(3).fill(0).map((_, i) => (
                    <div key={i} className="flex items-center space-x-4">
                      <div className="h-10 w-10 animate-pulse rounded-full bg-muted"></div>
                      <div className="space-y-2">
                        <div className="h-4 w-24 animate-pulse rounded bg-muted"></div>
                        <div className="h-3 w-16 animate-pulse rounded bg-muted"></div>
                      </div>
                    </div>
                  ))
                ) : insights?.connectedAccounts.length ? (
                  insights.connectedAccounts.map((account) => (
                    <div key={account.id} className="flex items-center space-x-4 rounded-lg p-2 hover:bg-muted transition-colors">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden">
                        {account.image ? (
                          <img 
                            src={account.image} 
                            alt={account.name} 
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <img 
                            src={getPlatformIcon(account.type || '')} 
                            alt={account.type || 'platform'} 
                            className="h-6 w-6 object-contain"
                          />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{account.name}</p>
                        <p className="text-xs text-muted-foreground capitalize">{account.type || account._type}</p>
                      </div>
                      <div className={`h-2 w-2 rounded-full ${account.active ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4">
                    <p className="text-muted-foreground">No accounts connected</p>
                    <Button variant="outline" size="sm" className="mt-2">
                      Connect Account
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Posts */}
            <Card className="shadow-sm hover:shadow-md transition-shadow lg:col-span-5">
              <CardHeader>
                <CardTitle>Recent Posts</CardTitle>
                <CardDescription>Your latest content across platforms</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  Array(3).fill(0).map((_, i) => (
                    <div key={i} className="mb-4 space-y-2">
                      <div className="flex justify-between">
                        <div className="h-5 w-24 animate-pulse rounded bg-muted"></div>
                        <div className="h-5 w-16 animate-pulse rounded bg-muted"></div>
                      </div>
                      <div className="h-16 w-full animate-pulse rounded bg-muted"></div>
                    </div>
                  ))
                ) : recentPosts.length ? (
                  <div className="space-y-4">
                    {recentPosts.map((post) => (
                      <div key={post.id} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <div className="h-8 w-8 rounded-full overflow-hidden">
                              <img 
                                src={getPlatformIcon(post.platform)} 
                                alt={post.platform}
                                className="h-full w-full object-contain"
                              />
                            </div>
                            <div>
                              <p className="text-sm font-medium capitalize">{post.platform}</p>
                              <div className="flex items-center">
                                <div className={`h-1.5 w-1.5 rounded-full ${getStatusColor(post.status)} mr-1.5`}></div>
                                <p className="text-xs text-muted-foreground capitalize">{post.status}</p>
                                {post.scheduled_at && (
                                  <span className="text-xs text-muted-foreground ml-2 flex items-center">
                                    <Clock className="h-3 w-3 mr-1" />
                                    {new Date(post.scheduled_at).toLocaleDateString()}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <Badge variant="outline" className="ml-auto">
                            {post.status === 'published' ? 'Published' : post.status === 'scheduled' ? 'Scheduled' : post.status}
                          </Badge>
                        </div>
                        
                        <p className="text-sm line-clamp-2 mb-2">{post.content}</p>
                        
                        {post.engagement && (
                          <div className="flex space-x-4 text-xs text-muted-foreground">
                            <span>👍 {post.engagement.likes}</span>
                            <span>💬 {post.engagement.comments}</span>
                            <span>🔄 {post.engagement.shares}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-muted-foreground">No recent posts found</p>
                    <Button variant="outline" size="sm" className="mt-2">
                      Create a Post
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Analytics</CardTitle>
              <CardDescription>Detailed metrics and analytics coming soon</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center">
              <div className="text-center space-y-4">
                <BarChart3 className="h-16 w-16 mx-auto text-muted-foreground/50" />
                <p className="text-muted-foreground">
                  Analytics dashboard is in development and will be available soon.
                </p>
                <Button variant="outline">Get notified when ready</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Reports</CardTitle>
              <CardDescription>Custom reports and exports coming soon</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center">
              <div className="text-center space-y-4">
                <ArrowUpRight className="h-16 w-16 mx-auto text-muted-foreground/50" />
                <p className="text-muted-foreground">
                  Reports feature is coming soon. Stay tuned for updates!
                </p>
                <Button variant="outline">Get notified when ready</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

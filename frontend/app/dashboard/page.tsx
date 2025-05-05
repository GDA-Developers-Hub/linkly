"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, BarChart3, Calendar, Clock, RefreshCw, Users, TrendingUp, Activity, Eye, Plus, Link2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { getSocialBuAPI, withErrorHandling } from "@/lib/socialbu-api"
import { useToast } from "@/components/ui/use-toast"
import { Avatar } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { SocialPlatformsAPI } from "@/services/social-platforms-api"

interface PlatformMetrics {
  followers: number
  engagement: number
  reach: number
  posts: {
    scheduled: number
    published: number
    total: number
  }
}

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
    metrics?: PlatformMetrics
  }>
  // Platform-specific metrics
  platformMetrics: Record<string, PlatformMetrics>
}

interface RecentPost {
  id: number
  content: string
  status: string
  scheduled_at: string | null
  platform: string
  engagement: {
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
  const [customIntegrationAvailable, setCustomIntegrationAvailable] = useState(false)

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      
      // Check if our direct platform integration is available
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/social_platforms/api/platforms/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          setCustomIntegrationAvailable(true);
          console.log('[Dashboard] Direct social integration API is available');
          
          // If direct integration is available, fetch data from it
          const platformsApi = new SocialPlatformsAPI();
          
          // Get connected accounts
          const accounts = await platformsApi.getAccounts().catch(() => []);
          
          // Get basic metrics (simplified since we're building this part)
          const followers = accounts.reduce((sum, account) => sum + (account.followers || 0), 0);
          const engagement = accounts.length > 0 ? 
            Math.round(accounts.reduce((sum, account) => sum + (account.engagement_rate || 0), 0) / accounts.length) : 0;
          const reach = accounts.reduce((sum, account) => sum + (account.reach || 0), 0);
          
          // Get recent posts (simplified)
          const postsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/social_platforms/api/posts/`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
              'Content-Type': 'application/json',
            },
          }).then(res => res.ok ? res.json() : {items: [], total: 0}).catch(() => ({items: [], total: 0}));
          
          const transformedInsights = {
            followers: followers || 0,
            engagement: engagement || 0,
            reach: reach || 0,
            posts: {
              scheduled: postsResponse.items?.filter(post => post.status === "scheduled").length || 0,
              published: postsResponse.items?.filter(post => post.status === "published").length || 0,
              total: postsResponse.total || 0,
            },
            connectedAccounts: accounts.map(account => ({
              id: account.id,
              name: account.account_name || account.name,
              type: account.platform?.name || account.account_type || 'Unknown',
              image: account.profile_picture_url || '',
              active: account.status === 'active'
            }))
          };
          
          setInsights(transformedInsights);
          setRecentPosts(postsResponse.items || []);
          console.log('[Dashboard] Dashboard data loaded from direct integration');
          setIsLoading(false);
          return; // Exit early since we got data from direct integration
        }
      } catch (error) {
        console.log('[Dashboard] Direct social integration API not available, falling back to SocialBu');
        setCustomIntegrationAvailable(false);
      }
      
      // Fall back to SocialBu integration if direct integration is not available
      await withErrorHandling(async () => {
        console.log('[Dashboard] Fetching dashboard data from SocialBu');
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
        const postsResponse = await api.getPosts({ limit: 5 })
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

        // Create platform-specific metrics
        const platformMetrics: Record<string, PlatformMetrics> = {};
        
        // Initialize metrics for each connected account/platform
        connectedAccounts.forEach(account => {
          const platformType = account.type || (account as any)._type || 'unknown';
          
          if (!platformMetrics[platformType]) {
            platformMetrics[platformType] = {
              followers: 0,
              engagement: 0,
              reach: 0,
              posts: {
                scheduled: 0,
                published: 0,
                total: 0
              }
            };
          }
          
          // Add metrics for this account based on available data
          // In a real implementation, you would get this data from your API
          platformMetrics[platformType].followers += (account as any).followers || 0;
          if ((account as any).engagement_rate) {
            platformMetrics[platformType].engagement = 
          Math.max(platformMetrics[platformType].engagement, (account as any).engagement_rate || 0);
          }
          platformMetrics[platformType].reach += (account as any).reach || 0;
        });
        
        // Count platform-specific posts
        postsData.forEach(post => {
          const platform = post.account_type || 'unknown';
          if (platformMetrics[platform]) {
            if (post.status === 'scheduled') {
              platformMetrics[platform].posts.scheduled++;
            } else if (post.status === 'published') {
              platformMetrics[platform].posts.published++;
            }
            platformMetrics[platform].posts.total++;
          }
        });
        
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
          platformMetrics,
          connectedAccounts: connectedAccounts.map(account => {
            const platformType = account.type || (account as any)._type || 'Unknown';
            // Extract properties safely with defaults
            return {
              id: account.id,
              name: account.name,
              _type: (account as any)._type || account.type || 'Unknown',
              type: platformType,
              image: (account as any).image || '',
              active: typeof (account as any).active === 'boolean' ? (account as any).active : true,
              metrics: platformMetrics[platformType] || null
            }
          })
        }

        // Transform posts data
        const recentPosts: RecentPost[] = postsResponse.items.map(post => {
          const status = post.status || (post.published ? 'published' : post.draft ? 'draft' : 'scheduled')
          return {
          id: post.id,
          content: post.content,
            status,
            scheduled_at: post.publish_at || null,
            platform: post.account_type || 'unknown',
          engagement: {
              likes: 0,
              comments: 0,
              shares: 0,
          },
          }
        })

        setInsights(transformedInsights)
        setRecentPosts(recentPosts)
        console.log('[Dashboard] Dashboard data loaded successfully from SocialBu');
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
    <div className="flex-1 space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-white dark:bg-gray-900 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">Dashboard</h2>
          <p className="text-muted-foreground mt-1">Welcome back! Here's what's happening with your social accounts.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={refreshData} disabled={isRefreshing} size="sm" className="h-9 shadow-sm hover:shadow transition-all duration-200">
            <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          
          {customIntegrationAvailable && (
            <Button variant="outline" size="sm" className="h-9 shadow-sm hover:shadow-md transition-all duration-200" asChild>
              <a href="/dashboard/platform-connect">
                <Link2 className="mr-2 h-4 w-4" />
                Manage Platforms
              </a>
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="bg-white dark:bg-gray-900 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="relative rounded-md px-5 py-1.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">Overview</TabsTrigger>
          <TabsTrigger value="analytics" className="relative rounded-md px-5 py-1.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">Analytics</TabsTrigger>
          <TabsTrigger value="reports" className="relative rounded-md px-5 py-1.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Stats Overview */}
          <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
            <Card className="overflow-hidden border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
                <div className="h-8 w-8 rounded-md bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center shadow-sm">
                  <Users className="h-4 w-4 text-white" />
                </div>
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
                
                {/* Platform-specific metrics popup */}
                {!isLoading && insights?.platformMetrics && Object.keys(insights.platformMetrics).length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/40">
                    <p className="text-xs font-medium mb-1">Platform Breakdown:</p>
                    <div className="space-y-1">
                      {Object.entries(insights.platformMetrics).map(([platform, metrics]) => (
                        <div key={platform} className="flex justify-between text-xs">
                          <span className="capitalize">{platform}:</span>
                          <span className="font-medium">{metrics.followers.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="overflow-hidden border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
                <div className="h-8 w-8 rounded-md bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center shadow-sm">
                  <Activity className="h-4 w-4 text-white" />
                </div>
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
                
                {/* Platform-specific metrics popup */}
                {!isLoading && insights?.platformMetrics && Object.keys(insights.platformMetrics).length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/40">
                    <p className="text-xs font-medium mb-1">Platform Breakdown:</p>
                    <div className="space-y-1">
                      {Object.entries(insights.platformMetrics).map(([platform, metrics]) => (
                        <div key={platform} className="flex justify-between text-xs">
                          <span className="capitalize">{platform}:</span>
                          <span className="font-medium">{metrics.engagement}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="overflow-hidden border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Reach</CardTitle>
                <div className="h-8 w-8 rounded-md bg-gradient-to-br from-indigo-600 to-indigo-400 flex items-center justify-center shadow-sm">
                  <Eye className="h-4 w-4 text-white" />
                </div>
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
                
                {/* Platform-specific metrics popup */}
                {!isLoading && insights?.platformMetrics && Object.keys(insights.platformMetrics).length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/40">
                    <p className="text-xs font-medium mb-1">Platform Breakdown:</p>
                    <div className="space-y-1">
                      {Object.entries(insights.platformMetrics).map(([platform, metrics]) => (
                        <div key={platform} className="flex justify-between text-xs">
                          <span className="capitalize">{platform}:</span>
                          <span className="font-medium">{metrics.reach.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="overflow-hidden border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
                <div className="h-8 w-8 rounded-md bg-gradient-to-br from-amber-600 to-amber-400 flex items-center justify-center shadow-sm">
                  <Calendar className="h-4 w-4 text-white" />
                </div>
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
                
                {/* Platform-specific metrics popup */}
                {!isLoading && insights?.platformMetrics && Object.keys(insights.platformMetrics).length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/40">
                    <p className="text-xs font-medium mb-1">Platform Breakdown:</p>
                    <div className="space-y-1">
                      {Object.entries(insights.platformMetrics).map(([platform, metrics]) => (
                        <div key={platform} className="flex justify-between text-xs">
                          <span className="capitalize">{platform}:</span>
                          <span className="font-medium">{metrics.posts.scheduled} scheduled</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Connected Accounts & Recent Posts Section */}
          <div className="grid gap-6 lg:grid-cols-7">
            {/* Connected Accounts */}
            <Card className="overflow-hidden border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm lg:col-span-2">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Connected Accounts</CardTitle>
                    <CardDescription>Your active social media accounts</CardDescription>
                  </div>
                  {customIntegrationAvailable && (
                    <Button variant="outline" size="sm" className="h-8" asChild>
                      <a href="/dashboard/platform-connect">
                        <Plus className="h-3.5 w-3.5 mr-1" />
                        Connect
                      </a>
                    </Button>
                  )}
                </div>
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
                  <div className="space-y-2">
                    {insights.connectedAccounts.map((account) => (
                      <div key={account.id} className="flex items-center space-x-4 rounded-lg p-2 hover:bg-muted transition-colors">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center overflow-hidden">
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
                          <div className="flex items-center gap-2">
                            <p className="text-xs text-muted-foreground capitalize">{account.type || account._type}</p>
                            {account.metrics && (
                              <p className="text-xs text-muted-foreground">
                                <span className="text-primary font-medium">{account.metrics.followers.toLocaleString()}</span> followers
                              </p>
                            )}
                          </div>
                        </div>
                        <Badge variant="outline" className={`px-2 ${account.active ? 'bg-green-50 text-green-700 dark:bg-green-900/20' : 'bg-gray-50 text-gray-700 dark:bg-gray-900/20'}`}>
                          {account.active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    ))}
                    <Button variant="outline" size="sm" className="w-full mt-2" asChild>
                      <a href="/dashboard/platform-connect">
                        <Plus className="mr-2 h-3.5 w-3.5" />
                        Connect Another Account
                      </a>
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-sm text-muted-foreground mb-3">No accounts connected</p>
                    <Button variant="outline" size="sm" asChild>
                      <a href="/dashboard/platform-connect">
                        <Plus className="mr-2 h-3.5 w-3.5" />
                        Connect Account
                      </a>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Recent Posts */}
            <Card className="overflow-hidden border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm lg:col-span-5">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Recent Posts</CardTitle>
                    <CardDescription>Your latest content across platforms</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="h-8" asChild>
                      <a href="/dashboard/post-create">
                        <Plus className="mr-2 h-3.5 w-3.5" />
                        Create Post
                      </a>
                    </Button>
                    <Button variant="outline" size="sm" className="h-8" asChild>
                      <a href="/dashboard/analytics">
                        <BarChart3 className="mr-2 h-3.5 w-3.5" />
                        Analytics
                      </a>
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  Array(3).fill(0).map((_, i) => (
                    <div key={i} className="mb-4 space-y-2">
                      <div className="flex justify-between">
                        <div className="h-4 w-36 animate-pulse rounded bg-muted"></div>
                        <div className="h-4 w-24 animate-pulse rounded bg-muted"></div>
                      </div>
                      <div className="h-16 w-full animate-pulse rounded bg-muted"></div>
                    </div>
                  ))
                ) : recentPosts.length > 0 ? (
                  <div className="space-y-4 divide-y">
                    {recentPosts.map((post) => (
                      <div key={post.id} className="pt-4 first:pt-0">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className={`h-2 w-2 rounded-full ${getStatusColor(post.status)}`}></div>
                            <span className="text-sm font-medium capitalize">{post.status}</span>
                          </div>
                          <div className="flex items-center">
                            <span className="text-xs text-muted-foreground">
                              {post.scheduled_at ? (
                                <>
                                  <Clock className="inline h-3 w-3 mr-1" />
                                  {new Date(post.scheduled_at).toLocaleDateString()}
                                </>
                              ) : (
                                "Posted"
                              )}
                            </span>
                            <Badge variant="outline" className="ml-2 capitalize">
                              {post.platform}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm line-clamp-2 mb-2">{post.content}</p>
                        <div className="flex items-center justify-between">
                          <div className="flex space-x-4 text-xs text-muted-foreground">
                            <span>👍 {post.engagement.likes}</span>
                            <span>💬 {post.engagement.comments}</span>
                            <span>↗️ {post.engagement.shares}</span>
                          </div>
                          <Button variant="ghost" size="sm" className="h-7 text-xs">
                            <ArrowUpRight className="h-3 w-3 mr-1" />
                            View
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No posts yet</p>
                    <Button variant="outline" size="sm" className="mt-2">
                      Create Post
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <Card className="border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm">
            <CardHeader>
              <CardTitle>Engagement Analytics</CardTitle>
              <CardDescription>Performance metrics across all your social platforms</CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="p-16 flex items-center justify-center border rounded-lg bg-muted/20">
                <p className="text-center text-muted-foreground">Analytics coming soon!</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-6">
          <Card className="border-0 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-900 shadow-sm">
            <CardHeader>
              <CardTitle>Custom Reports</CardTitle>
              <CardDescription>Generate and download reports for your campaigns</CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <div className="p-16 flex items-center justify-center border rounded-lg bg-muted/20">
                <p className="text-center text-muted-foreground">Report generation coming soon!</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

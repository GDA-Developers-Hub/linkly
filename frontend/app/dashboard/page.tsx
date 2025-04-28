"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ArrowUpRight, BarChart3, Calendar, Clock, RefreshCw, Users } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { getSocialBuAPI, withErrorHandling } from "@/lib/socialbu-api"
import { useToast } from "@/components/ui/use-toast"

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
        const api = getSocialBuAPI()

        // Fetch insights
        const insightsData = await api.getInsights()
        
        // Fetch connected accounts
        const connectedAccounts = await api.getAccounts()

        // Fetch recent posts
        const postsData = await api.getPosts()

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
            total: postsData.length,
          },
          connectedAccounts: connectedAccounts.map(account => ({
            id: account.id,
            name: account.name,
            _type: account._type || account.type || 'Unknown',
            type: account.type || '',
            image: account.image || '',
            active: typeof account.active === 'boolean' ? account.active : true
          }))
        }

        // Transform posts data
        const transformedPosts: RecentPost[] = postsData.map((post) => ({
          id: post.id,
          content: post.content,
          status: post.status,
          scheduled_at: post.scheduled_at,
          platform: post.platforms?.[0] || "unknown",
          engagement: {
            likes: Math.floor(Math.random() * 100),
            comments: Math.floor(Math.random() * 30),
            shares: Math.floor(Math.random() * 20),
          },
        }))

        setInsights(transformedInsights)
        setRecentPosts(transformedPosts)
      }, "Failed to fetch dashboard data")
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
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

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <Button variant="outline" size="sm" onClick={refreshData} disabled={isRefreshing}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-24 animate-pulse rounded bg-muted"></div>
                  ) : (
                    insights?.followers.toLocaleString() || "0"
                  )}
                </div>
                <p className="text-xs text-muted-foreground">+2.5% from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-16 animate-pulse rounded bg-muted"></div>
                  ) : (
                    `${insights?.engagement || 0}%`
                  )}
                </div>
                <p className="text-xs text-muted-foreground">+1.2% from last month</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Scheduled Posts</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-12 animate-pulse rounded bg-muted"></div>
                  ) : (
                    insights?.posts.scheduled || "0"
                  )}
                </div>
                <p className="text-xs text-muted-foreground">For the next 7 days</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Reach</CardTitle>
                <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isLoading ? (
                    <div className="h-8 w-24 animate-pulse rounded bg-muted"></div>
                  ) : (
                    insights?.reach.toLocaleString() || "0"
                  )}
                </div>
                <p className="text-xs text-muted-foreground">+19% from last month</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <Card className="col-span-4">
              <CardHeader>
                <CardTitle>Recent Posts</CardTitle>
                <CardDescription>Your latest content across platforms</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center space-x-4">
                        <div className="h-12 w-12 animate-pulse rounded bg-muted"></div>
                        <div className="space-y-2">
                          <div className="h-4 w-48 animate-pulse rounded bg-muted"></div>
                          <div className="h-3 w-24 animate-pulse rounded bg-muted"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : recentPosts.length > 0 ? (
                  <div className="space-y-4">
                    {recentPosts.map((post) => (
                      <div key={post.id} className="flex items-start space-x-4">
                        <div className="rounded-full bg-primary/10 p-2">
                          {post.status === "scheduled" ? (
                            <Clock className="h-4 w-4 text-primary" />
                          ) : (
                            <BarChart3 className="h-4 w-4 text-primary" />
                          )}
                        </div>
                        <div className="flex-1 space-y-1">
                          <p className="text-sm font-medium leading-none">
                            {post.content.length > 60 ? `${post.content.substring(0, 60)}...` : post.content}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {post.status === "scheduled"
                              ? `Scheduled for ${new Date(post.scheduled_at || "").toLocaleDateString()}`
                              : `Published on ${post.platform}`}
                          </p>
                        </div>
                        {post.engagement && (
                          <div className="text-xs text-muted-foreground">
                            <div className="flex items-center">
                              <span className="mr-1">👍</span> {post.engagement.likes}
                            </div>
                            <div className="flex items-center">
                              <span className="mr-1">💬</span> {post.engagement.comments}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex h-[200px] items-center justify-center">
                    <p className="text-sm text-muted-foreground">No recent posts found</p>
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card className="col-span-3">
              <CardHeader>
                <CardTitle>Connected Accounts</CardTitle>
                <CardDescription>Your connected social media platforms</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2].map((i) => (
                      <div key={i} className="flex items-center space-x-4">
                        <div className="h-10 w-10 animate-pulse rounded-full bg-muted"></div>
                        <div className="space-y-2">
                          <div className="h-4 w-32 animate-pulse rounded bg-muted"></div>
                          <div className="h-3 w-20 animate-pulse rounded bg-muted"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : insights && insights.connectedAccounts && insights.connectedAccounts.length > 0 ? (
                  <div className="space-y-3">
                    {insights.connectedAccounts.map((account) => (
                      <div key={account.id} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {account.image ? (
                            <img 
                              src={account.image} 
                              alt={account.name} 
                              className="h-10 w-10 rounded-full object-cover" 
                            />
                          ) : (
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                              <Users className="h-5 w-5 text-primary" />
                            </div>
                          )}
                          <div>
                            <p className="text-sm font-medium">{account.name}</p>
                            <p className="text-xs text-muted-foreground">{account._type || account.type}</p>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {account.active ? (
                            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800 dark:bg-green-800/30 dark:text-green-500">
                              <div className="mr-1 h-1.5 w-1.5 rounded-full bg-green-500"></div>
                              Active
                            </div>
                          ) : (
                            <div className="flex items-center rounded-full bg-amber-100 px-2 py-1 text-xs font-medium text-amber-800 dark:bg-amber-800/30 dark:text-amber-500">
                              <div className="mr-1 h-1.5 w-1.5 rounded-full bg-amber-500"></div>
                              Inactive
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    <Button variant="outline" className="mt-2 w-full text-xs" asChild>
                      <a href="/dashboard/platform-connect">Manage Accounts</a>
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center space-y-3 py-6">
                    <Users className="h-8 w-8 text-muted-foreground" />
                    <div className="text-center">
                      <p className="text-sm font-medium">No connected accounts</p>
                      <p className="text-xs text-muted-foreground">Connect your social media accounts to get started</p>
                    </div>
                    <Button variant="outline" size="sm" asChild>
                      <a href="/dashboard/platform-connect">Connect Accounts</a>
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
              <CardDescription>Detailed metrics and performance data</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center">
              <p className="text-muted-foreground">Analytics dashboard coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Reports</CardTitle>
              <CardDescription>Generate and view custom reports</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center">
              <p className="text-muted-foreground">Reports dashboard coming soon</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

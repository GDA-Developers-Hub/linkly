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
}

interface RecentPost {
  id: number
  content: string
  status: string
  scheduled_at?: string
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

        // Fetch recent posts
        const postsData = await api.getPosts({ limit: 5 })

        // Transform data for the dashboard
        const transformedInsights: InsightsData = {
          followers: insightsData.followers || 0,
          engagement: insightsData.engagement || 0,
          reach: insightsData.reach || 0,
          posts: {
            scheduled: postsData.filter((post) => post.status === "scheduled").length,
            published: postsData.filter((post) => post.status === "published").length,
            total: postsData.length,
          },
        }

        // Transform posts data
        const transformedPosts: RecentPost[] = postsData.map((post) => ({
          id: post.id,
          content: post.content,
          status: post.status,
          scheduled_at: post.scheduled_at,
          platform: post.account_ids?.[0]?.toString() || "unknown",
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
                <CardTitle>Content Performance</CardTitle>
                <CardDescription>Your content engagement metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-8">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="font-medium">Instagram</div>
                    <div className="text-muted-foreground">72%</div>
                  </div>
                  <Progress value={72} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="font-medium">Facebook</div>
                    <div className="text-muted-foreground">54%</div>
                  </div>
                  <Progress value={54} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="font-medium">Twitter</div>
                    <div className="text-muted-foreground">48%</div>
                  </div>
                  <Progress value={48} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="font-medium">LinkedIn</div>
                    <div className="text-muted-foreground">35%</div>
                  </div>
                  <Progress value={35} className="h-2" />
                </div>
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

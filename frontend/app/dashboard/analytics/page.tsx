"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { toast } from "@/components/ui/use-toast"
import Image from "next/image"
import {
  ArrowUpRight,
  ArrowDownRight,
  Users,
  Eye,
  Heart,
  MessageSquare,
  Share2,
  Download,
  Calendar,
  RefreshCw,
  Image as ImageIcon
} from "lucide-react"
import { ChartContainer } from "@/components/ui/chart"
import { 
  LineChart, 
  Line,
  BarChart,
  Bar, 
  PieChart, 
  Pie,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from "recharts"

// Mock data for development
const MOCK_OVERVIEW = {
  followers: {
    total: 24532,
    change: 342,
    percentage: 1.4,
    positive: true,
  },
  reach: {
    total: 45000,
    change: 1200,
    percentage: 2.7,
    positive: true,
  },
  engagement: {
    total: 3.2,
    change: 0.2,
    percentage: 6.7,
    positive: true,
  },
  impressions: {
    total: 78500,
    change: -1500,
    percentage: 1.9,
    positive: false,
  },
}

const MOCK_PLATFORMS = {
  instagram: {
    followers: 12500,
    engagement: 3.8,
    reach: 25000,
    posts: 45,
  },
  facebook: {
    followers: 8200,
    engagement: 2.1,
    reach: 15000,
    posts: 38,
  },
  twitter: {
    followers: 3200,
    engagement: 4.5,
    reach: 5000,
    posts: 120,
  },
  linkedin: {
    followers: 632,
    engagement: 1.8,
    reach: 2000,
    posts: 22,
  },
}

const MOCK_ENGAGEMENT = [
  { name: "Likes", value: 65, color: "#ec4899" },
  { name: "Comments", value: 20, color: "#8b5cf6" },
  { name: "Shares", value: 10, color: "#3b82f6" },
  { name: "Saves", value: 5, color: "#10b981" },
]

const MOCK_AUDIENCE = {
  age: [
    { name: "18-24", value: 25 },
    { name: "25-34", value: 40 },
    { name: "35-44", value: 20 },
    { name: "45-54", value: 10 },
    { name: "55+", value: 5 },
  ],
  gender: [
    { name: "Female", value: 58 },
    { name: "Male", value: 40 },
    { name: "Other", value: 2 },
  ],
  location: [
    { name: "United States", value: 45 },
    { name: "United Kingdom", value: 15 },
    { name: "Canada", value: 10 },
    { name: "Australia", value: 8 },
    { name: "Germany", value: 7 },
    { name: "Other", value: 15 },
  ],
}

const MOCK_GROWTH_DATA = {
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  datasets: [
    {
      data: [10200, 11500, 12800, 14200, 15600, 17000, 18500, 19800, 21200, 22500, 23800, 24532],
    },
  ],
}

const MOCK_ENGAGEMENT_DATA = {
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  datasets: [
    {
      data: [2.8, 2.9, 3.0, 2.7, 2.8, 3.1, 3.3, 3.2, 3.4, 3.3, 3.1, 3.2],
    },
  ],
}

const MOCK_PLATFORM_GROWTH = {
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  datasets: [
    {
      data: [5200, 5800, 6500, 7200, 8000, 8800, 9500, 10200, 10800, 11500, 12000, 12500],
    },
    {
      data: [3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 7800, 8000, 8200],
    },
    {
      data: [1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3100, 3200],
    },
    {
      data: [300, 320, 350, 380, 410, 450, 480, 510, 550, 580, 610, 632],
    },
  ],
}

// Ensure we have a default empty config for the Chart
const defaultChartConfig = {
  default: { color: "#0ea5e9" }
};

interface EngagementItem {
  name: string;
  value: number;
  color: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    tension?: number;
  }[];
}

interface AudienceData {
  age: { name: string; value: number }[];
  gender: { name: string; value: number }[];
  location: { name: string; value: number }[];
}

export default function AnalyticsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [overview, setOverview] = useState<any>(null)
  const [platforms, setPlatforms] = useState<any>(null)
  const [engagement, setEngagement] = useState<EngagementItem[]>([])
  const [audience, setAudience] = useState<AudienceData | null>(null)
  const [growthData, setGrowthData] = useState<any[]>([])
  const [engagementData, setEngagementData] = useState<any[]>([])
  const [platformGrowth, setPlatformGrowth] = useState<any[]>([])
  const [dateRange, setDateRange] = useState("30d")
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true)
        // In a real app, we would fetch from the API
        // const api = getSocialBuAPI()
        // const analyticsData = await api.getAnalytics(dateRange)

        // Using mock data for now
        setTimeout(() => {
          setOverview(MOCK_OVERVIEW)
          setPlatforms(MOCK_PLATFORMS)
          setEngagement(MOCK_ENGAGEMENT)
          setAudience(MOCK_AUDIENCE)
          // Transform the data for Recharts
          setGrowthData(MOCK_GROWTH_DATA.labels.map((label, index) => ({
            name: label,
            value: MOCK_GROWTH_DATA.datasets[0].data[index]
          })))
          setEngagementData(MOCK_ENGAGEMENT_DATA.labels.map((label, index) => ({
            name: label,
            value: MOCK_ENGAGEMENT_DATA.datasets[0].data[index]
          })))
          setPlatformGrowth(MOCK_PLATFORM_GROWTH.labels.map((label, index) => ({
            name: label,
            instagram: MOCK_PLATFORM_GROWTH.datasets[0].data[index],
            facebook: MOCK_PLATFORM_GROWTH.datasets[1].data[index],
            twitter: MOCK_PLATFORM_GROWTH.datasets[2].data[index],
            linkedin: MOCK_PLATFORM_GROWTH.datasets[3].data[index],
          })))
          setIsLoading(false)
        }, 1000)
      } catch (error) {
        console.error("Failed to load analytics", error)
        toast({
          title: "Error",
          description: "Failed to load analytics data. Please try again.",
          variant: "destructive",
        })
        setIsLoading(false)
      }
    }

    loadData()
  }, [dateRange])

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      // In a real app, we would fetch fresh data from the API
      // const api = getSocialBuAPI()
      // const analyticsData = await api.getAnalytics(dateRange, true)

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      toast({
        title: "Data Refreshed",
        description: "Analytics data has been updated with the latest information.",
      })
    } catch (error) {
      console.error("Failed to refresh data", error)
      toast({
        title: "Error",
        description: "Failed to refresh analytics data. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleExport = () => {
    toast({
      title: "Export Started",
      description: "Your analytics report is being generated and will download shortly.",
    })

    // Simulate download delay
    setTimeout(() => {
      toast({
        title: "Export Complete",
        description: "Your analytics report has been downloaded.",
      })
    }, 2000)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <Skeleton className="h-8 w-64" />
          <div className="flex items-center gap-2">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-32 mb-2" />
                <Skeleton className="h-4 w-20" />
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-[300px] w-full" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-[300px] w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">Track your social media performance across all platforms</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <div className="flex justify-between items-center">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="growth">Growth</TabsTrigger>
            <TabsTrigger value="engagement">Engagement</TabsTrigger>
            <TabsTrigger value="audience">Audience</TabsTrigger>
          </TabsList>

          <div className="flex items-center space-x-2">
            <Button variant={dateRange === "7d" ? "default" : "outline"} size="sm" onClick={() => setDateRange("7d")}>
              7D
            </Button>
            <Button variant={dateRange === "30d" ? "default" : "outline"} size="sm" onClick={() => setDateRange("30d")}>
              30D
            </Button>
            <Button variant={dateRange === "90d" ? "default" : "outline"} size="sm" onClick={() => setDateRange("90d")}>
              90D
            </Button>
            <Button variant={dateRange === "1y" ? "default" : "outline"} size="sm" onClick={() => setDateRange("1y")}>
              1Y
            </Button>
          </div>
        </div>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Followers</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview.followers.total.toLocaleString()}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  {overview.followers.positive ? (
                    <ArrowUpRight className="mr-1 h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-4 w-4 text-red-500" />
                  )}
                  <span className={overview.followers.positive ? "text-green-500" : "text-red-500"}>
                    {overview.followers.percentage}%
                  </span>
                  <span className="ml-1">from last period</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Reach</CardTitle>
                <Eye className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview.reach.total.toLocaleString()}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  {overview.reach.positive ? (
                    <ArrowUpRight className="mr-1 h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-4 w-4 text-red-500" />
                  )}
                  <span className={overview.reach.positive ? "text-green-500" : "text-red-500"}>
                    {overview.reach.percentage}%
                  </span>
                  <span className="ml-1">from last period</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
                <Heart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview.engagement.total}%</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  {overview.engagement.positive ? (
                    <ArrowUpRight className="mr-1 h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-4 w-4 text-red-500" />
                  )}
                  <span className={overview.engagement.positive ? "text-green-500" : "text-red-500"}>
                    {overview.engagement.percentage}%
                  </span>
                  <span className="ml-1">from last period</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Impressions</CardTitle>
                <Eye className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview.impressions.total.toLocaleString()}</div>
                <div className="flex items-center text-xs text-muted-foreground">
                  {overview.impressions.positive ? (
                    <ArrowUpRight className="mr-1 h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-4 w-4 text-red-500" />
                  )}
                  <span className={overview.impressions.positive ? "text-green-500" : "text-red-500"}>
                    {overview.impressions.percentage}%
                  </span>
                  <span className="ml-1">from last period</span>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Platform Breakdown</CardTitle>
                <CardDescription>Followers and engagement by platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="h-4 w-4 rounded-full bg-pink-500 mr-2" />
                          <span>Instagram</span>
                        </div>
                        <span className="font-medium">{platforms.instagram.followers.toLocaleString()}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-pink-500"
                          style={{
                            width: `${(platforms.instagram.followers / overview.followers.total) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="h-4 w-4 rounded-full bg-blue-500 mr-2" />
                          <span>Facebook</span>
                        </div>
                        <span className="font-medium">{platforms.facebook.followers.toLocaleString()}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-blue-500"
                          style={{
                            width: `${(platforms.facebook.followers / overview.followers.total) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="h-4 w-4 rounded-full bg-green-500 mr-2" />
                          <span>Twitter</span>
                        </div>
                        <span className="font-medium">{platforms.twitter.followers.toLocaleString()}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{
                            width: `${(platforms.twitter.followers / overview.followers.total) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="h-4 w-4 rounded-full bg-purple-500 mr-2" />
                          <span>LinkedIn</span>
                        </div>
                        <span className="font-medium">{platforms.linkedin.followers.toLocaleString()}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-purple-500"
                          style={{
                            width: `${(platforms.linkedin.followers / overview.followers.total) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Engagement Breakdown</CardTitle>
                <CardDescription>Types of engagement across all platforms</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ChartContainer config={defaultChartConfig}>
                    <PieChart>
                      <Pie
                        data={engagement}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                      >
                        {engagement.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ChartContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="growth" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Follower Growth</CardTitle>
              <CardDescription>Total followers over time across all platforms</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ChartContainer config={defaultChartConfig}>
                  <LineChart data={growthData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ChartContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Platform Growth</CardTitle>
              <CardDescription>Follower growth by platform</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ChartContainer config={defaultChartConfig}>
                  <LineChart data={platformGrowth}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="instagram" 
                      stroke="rgb(236, 72, 153)"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="facebook" 
                      stroke="rgb(59, 130, 246)"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="twitter" 
                      stroke="rgb(16, 185, 129)"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="linkedin" 
                      stroke="rgb(139, 92, 246)"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ChartContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="engagement" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Engagement Rate</CardTitle>
              <CardDescription>Average engagement rate over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                <ChartContainer config={defaultChartConfig}>
                  <LineChart data={engagementData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#ec4899"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ChartContainer>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Top Performing Posts</CardTitle>
                <CardDescription>Posts with the highest engagement</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-start space-x-4">
                      <div className="h-16 w-16 rounded-md bg-muted flex items-center justify-center">
                        <ImageIcon className="h-8 w-8 text-muted-foreground" />
                      </div>
                      <div className="space-y-1 flex-1">
                        <p className="text-sm font-medium leading-none">
                          {
                            [
                              "Check out our latest product launch! #excited",
                              "We're hiring! Join our amazing team.",
                              "Coming soon: Our biggest announcement of the year!",
                            ][i]
                          }
                        </p>
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Calendar className="mr-1 h-3 w-3" />
                          <span>{["2 days ago", "4 days ago", "1 week ago"][i]}</span>
                          <span className="mx-1">•</span>
                          <Heart className="mr-1 h-3 w-3 text-pink-500" />
                          <span>{[120, 85, 65][i]}</span>
                          <span className="mx-1">•</span>
                          <MessageSquare className="mr-1 h-3 w-3 text-blue-500" />
                          <span>{[32, 18, 12][i]}</span>
                          <span className="mx-1">•</span>
                          <Share2 className="mr-1 h-3 w-3 text-green-500" />
                          <span>{[15, 8, 5][i]}</span>
                        </div>
                      </div>
                      <Badge>{["Instagram", "Facebook", "Twitter"][i]}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Engagement by Platform</CardTitle>
                <CardDescription>Average engagement rate by platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="h-4 w-4 rounded-full bg-pink-500 mr-2" />
                        <span>Instagram</span>
                      </div>
                      <span className="font-medium">{platforms.instagram.engagement}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-pink-500"
                        style={{
                          width: `${(platforms.instagram.engagement / 5) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="h-4 w-4 rounded-full bg-blue-500 mr-2" />
                        <span>Facebook</span>
                      </div>
                      <span className="font-medium">{platforms.facebook.engagement}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-blue-500"
                        style={{
                          width: `${(platforms.facebook.engagement / 5) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="h-4 w-4 rounded-full bg-green-500 mr-2" />
                        <span>Twitter</span>
                      </div>
                      <span className="font-medium">{platforms.twitter.engagement}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-green-500"
                        style={{
                          width: `${(platforms.twitter.engagement / 5) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="h-4 w-4 rounded-full bg-purple-500 mr-2" />
                        <span>LinkedIn</span>
                      </div>
                      <span className="font-medium">{platforms.linkedin.engagement}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-purple-500"
                        style={{
                          width: `${(platforms.linkedin.engagement / 5) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="audience" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Age Distribution</CardTitle>
                <CardDescription>Audience breakdown by age group</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ChartContainer config={defaultChartConfig}>
                    <BarChart data={audience?.age || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="rgba(99, 102, 241, 0.8)" />
                    </BarChart>
                  </ChartContainer>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Gender Distribution</CardTitle>
                <CardDescription>Audience breakdown by gender</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ChartContainer config={defaultChartConfig}>
                    <PieChart>
                      <Pie
                        data={audience?.gender || []}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                      >
                        {(audience?.gender || []).map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={["rgba(236, 72, 153, 0.8)", "rgba(59, 130, 246, 0.8)", "rgba(16, 185, 129, 0.8)"][index]} 
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ChartContainer>
                </div>
              </CardContent>
            </Card>
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>Geographic Distribution</CardTitle>
                <CardDescription>Audience breakdown by location</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ChartContainer config={defaultChartConfig}>
                    <BarChart data={audience?.location || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="rgba(16, 185, 129, 0.8)" />
                    </BarChart>
                  </ChartContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

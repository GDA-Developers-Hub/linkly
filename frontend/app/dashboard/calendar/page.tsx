"use client"

import { useState, useEffect } from "react"
import { Calendar, momentLocalizer } from "react-big-calendar"
import moment from "moment"
import "react-big-calendar/lib/css/react-big-calendar.css"
import "./styles.css" // Import custom styles
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import {
  CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Filter,
  Plus,
  RefreshCw,
  Trash2,
  Edit,
  CalendarPlus2Icon as CalendarIcon2,
  Clock,
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
} from "lucide-react"
import { ModeToggle } from "@/components/mode-toggle"
import { format, addDays, subDays } from "date-fns"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { type Post, type Account } from "@/lib/socials-api"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"

// Initialize the localizer for react-big-calendar
const localizer = momentLocalizer(moment)

// Map platform names to icons and colors
const platformConfig: Record<string, { icon: any; color: string }> = {
  facebook: { icon: Facebook, color: "#1877F2" },
  instagram: { icon: Instagram, color: "#E1306C" },
  twitter: { icon: Twitter, color: "#1DA1F2" },
  linkedin: { icon: Linkedin, color: "#0A66C2" },
}

// Event interface for react-big-calendar
interface CalendarEvent {
  id: number
  title: string
  start: Date
  end: Date
  post: Post
  account?: Account
}

export default function CalendarPage() {
  const [view, setView] = useState<"month" | "week" | "day">("month")
  const [date, setDate] = useState(new Date())
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null)
  const [isPostDetailsOpen, setIsPostDetailsOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [selectedPlatformFilter, setSelectedPlatformFilter] = useState<string>("all")
  const [selectedStatusFilter, setSelectedStatusFilter] = useState<string>("all")
  const [accounts, setAccounts] = useState<Account[]>([])
  const { toast } = useToast()
  const router = useRouter()

  // Fetch posts and accounts
  const fetchData = async () => {
    setIsLoading(true)
    try {
      // Simulate fetching data
      const accountsData = [
        { id: 1, name: "Facebook Page", platform: "facebook", account_type: "page" },
        { id: 2, name: "Instagram", platform: "instagram", account_type: "profile" },
        { id: 3, name: "Twitter", platform: "twitter", account_type: "profile" }
      ];
      
      setAccounts(accountsData);
      
      // Mock posts data
      const postsData = {
        items: [
          {
            id: 1,
            status: "published",
            account_id: 1,
            created_at: new Date().toISOString(),
            published_at: new Date().toISOString(),
            content: "This is a sample published post for Facebook"
          },
          {
            id: 2,
            status: "scheduled",
            account_id: 2,
            created_at: new Date().toISOString(),
            publish_at: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
            content: "This is a scheduled post for Instagram"
          },
          {
            id: 3,
            status: "draft",
            account_id: 3,
            created_at: new Date().toISOString(),
            content: "This is a draft post for Twitter"
          }
        ]
      };

        // Check if postsData is the expected type with items
        if (!postsData || typeof postsData !== 'object') {
          console.error('Invalid posts data received:', postsData);
          return;
        }

        // Extract the items from PaginatedPosts response
        // Extract posts from the mock data
        const posts = postsData.items || [];
        console.log(`Processing ${posts.length} posts`);

        // Convert posts to calendar events
        const events: CalendarEvent[] = posts
          .filter((post) => post.publish_at || post.created_at)
          .map((post) => {
            // Get account for this post
            const postAccount = accountsData.find((account) => account.id === post.account_id)

            return {
              id: post.id,
              title: post.content.substring(0, 50) + (post.content.length > 50 ? "..." : ""),
              start: new Date(post.publish_at || post.created_at),
              end: new Date(post.publish_at || post.created_at),
              post,
              account: postAccount,
            }
          })

        setEvents(events)
    } catch (error) {
      console.error("Error fetching data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // Delete a post
  const deletePost = async (postId: number) => {
    try {
      // Simulate deleting a post
      console.log(`Deleting post ${postId}`);
      
      toast({
        title: "Post deleted",
        description: "The post has been successfully deleted.",
      });
      
      // Update local state to remove the deleted post
      setEvents(prev => prev.filter(event => event.post.id !== postId));
      
      // Close dialogs
      setIsPostDetailsOpen(false);
      setIsEditDialogOpen(false);
    } catch (error) {
      console.error("Error deleting post:", error);
      toast({
        title: "Error",
        description: "Failed to delete post",
        variant: "destructive"
      });
    }
  }

  // Fetch data on component mount and when filters change
  useEffect(() => {
    fetchData()
  }, [selectedPlatformFilter, selectedStatusFilter])

  // Handle event selection
  const handleSelectEvent = (event: CalendarEvent) => {
    setSelectedEvent(event)
    setIsPostDetailsOpen(true)
  }

  // Handle navigation between dates
  const handleNavigate = (action: "PREV" | "NEXT" | "TODAY") => {
    if (action === "PREV") {
      setDate((prevDate) => {
        if (view === "month") return new Date(prevDate.getFullYear(), prevDate.getMonth() - 1, 1)
        if (view === "week") return subDays(prevDate, 7)
        return subDays(prevDate, 1)
      })
    } else if (action === "NEXT") {
      setDate((prevDate) => {
        if (view === "month") return new Date(prevDate.getFullYear(), prevDate.getMonth() + 1, 1)
        if (view === "week") return addDays(prevDate, 7)
        return addDays(prevDate, 1)
      })
    } else {
      setDate(new Date())
    }
  }

  // Custom event component for the calendar
  const EventComponent = ({ event }: { event: CalendarEvent }) => {
    // Get the first account for color
    const firstAccount = event.account || { platform: "unknown" }
    const platform = firstAccount.platform && typeof firstAccount.platform === 'string' 
      ? platformConfig[firstAccount.platform] || { icon: Plus, color: "#666" } 
      : { icon: Plus, color: "#666" }

    return (
      <div
        className="rounded px-1 py-0.5 text-xs overflow-hidden cursor-pointer"
        style={{
          backgroundColor: platform.color + "20",
          borderLeft: `3px solid ${platform.color}`,
        }}
      >
        <div className="font-medium truncate">{event.title}</div>
        <div className="flex items-center gap-1 mt-0.5">
          {event.account && (
            <div className="flex items-center gap-1">
              {(() => {
                const platformIcon = event.account.platform && typeof event.account.platform === 'string'
                  ? platformConfig[event.account.platform] || { icon: Plus, color: "#666" }
                  : { icon: Plus, color: "#666" }
                const PlatformIcon = platformIcon.icon
                return <PlatformIcon className="h-3 w-3" style={{ color: platformIcon.color }} />
              })()}
            </div>
          )}
          <span className="text-[10px] ml-auto">{format(event.start, "h:mm a")}</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Content Calendar</h2>
          <p className="text-muted-foreground">Schedule and manage your social media posts</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchData} disabled={isLoading}>
            {isLoading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
            Refresh
          </Button>
          <Button asChild>
            <a href="/dashboard/posts/create">
              <Plus className="mr-2 h-4 w-4" />
              Create Post
            </a>
          </Button>
          <ModeToggle />
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <CardTitle>Content Calendar</CardTitle>
              <CardDescription>
                {view === "month"
                  ? format(date, "MMMM yyyy")
                  : view === "week"
                    ? `Week of ${format(date, "MMM d, yyyy")}`
                    : format(date, "EEEE, MMMM d, yyyy")}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => handleNavigate("PREV")}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleNavigate("TODAY")}>
                Today
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleNavigate("NEXT")}>
                <ChevronRight className="h-4 w-4" />
              </Button>
              <Tabs value={view} onValueChange={(value) => setView(value as "month" | "week" | "day")}>
                <TabsList>
                  <TabsTrigger value="month">Month</TabsTrigger>
                  <TabsTrigger value="week">Week</TabsTrigger>
                  <TabsTrigger value="day">Day</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 pt-2">
            <Select value={selectedPlatformFilter} onValueChange={setSelectedPlatformFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="All Platforms" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Platforms</SelectItem>
                {accounts.map((account) => (
                  <SelectItem key={account.id} value={account.id.toString()}>
                    {account.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedStatusFilter} onValueChange={setSelectedStatusFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="scheduled">Scheduled</SelectItem>
                <SelectItem value="published">Published</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" className="ml-auto">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-[600px] flex items-center justify-center">
              <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="h-[600px]">
              <Calendar
                localizer={localizer}
                events={events}
                startAccessor="start"
                endAccessor="end"
                view={view}
                date={date}
                onNavigate={() => {}} // We handle navigation manually
                onView={() => {}} // We handle view changes manually
                onSelectEvent={handleSelectEvent}
                components={{
                  event: EventComponent as any,
                }}
                popup
                className="rounded-md border"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Post Details Dialog */}
      <Dialog open={isPostDetailsOpen} onOpenChange={setIsPostDetailsOpen}>
        <DialogContent className="sm:max-w-[600px]">
          {selectedEvent && (
            <>
              <DialogHeader>
                <DialogTitle>Post Details</DialogTitle>
                <DialogDescription>
                  {selectedEvent.post.status === "published"
                    ? `Published on ${format(selectedEvent.start, "PPP p")}`
                    : `Scheduled for ${format(selectedEvent.start, "PPP p")}`}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="flex items-center gap-2">
                  {selectedEvent.account && (
                    <Badge
                      style={{
                        backgroundColor: (selectedEvent.account.platform && typeof selectedEvent.account.platform === 'string' 
                          ? platformConfig[selectedEvent.account.platform] || { color: "#666" }
                          : { color: "#666" }).color + "20",
                        color: (selectedEvent.account.platform && typeof selectedEvent.account.platform === 'string'
                          ? platformConfig[selectedEvent.account.platform] || { color: "#666" }
                          : { color: "#666" }).color,
                        borderColor: (selectedEvent.account.platform && typeof selectedEvent.account.platform === 'string'
                          ? platformConfig[selectedEvent.account.platform] || { color: "#666" }
                          : { color: "#666" }).color,
                      }}
                      variant="outline"
                      className="flex items-center gap-1"
                    >
                      {(() => {
                        const platformIcon = selectedEvent.account.platform && typeof selectedEvent.account.platform === 'string'
                          ? platformConfig[selectedEvent.account.platform] || { icon: Plus, color: "#666" }
                          : { icon: Plus, color: "#666" }
                        const PlatformIcon = platformIcon.icon
                        return <PlatformIcon className="h-3 w-3" />
                      })()}
                      {selectedEvent.account.name}
                    </Badge>
                  )}
                  {selectedEvent?.post?.status ? (
                    selectedEvent.post.status === "draft" ? (
                      <Badge variant="secondary">Draft</Badge>
                    ) : selectedEvent.post.status === "scheduled" ? (
                      <Badge>Scheduled</Badge>
                    ) : (
                      <Badge variant="secondary">Published</Badge>
                    )
                  ) : null}
                </div>
                <div className="rounded-md border p-4">
                  <p className="whitespace-pre-wrap">{selectedEvent.post.content}</p>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CalendarIcon2 className="h-4 w-4" />
                  <span>
                    {selectedEvent.post.status === "published"
                      ? `Published on ${format(selectedEvent.start, "PPP")}`
                      : `Scheduled for ${format(selectedEvent.start, "PPP")}`}
                  </span>
                  <Clock className="h-4 w-4 ml-2" />
                  <span>{format(selectedEvent.start, "p")}</span>
                </div>
              </div>
              <DialogFooter className="flex justify-between">
                <Button variant="destructive" size="sm" onClick={() => deletePost(selectedEvent.post.id)}>
                  <Trash2 className="mr-2 h-3.5 w-3.5" />
                  Delete
                </Button>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => setIsPostDetailsOpen(false)}>
                    Close
                  </Button>
                  <Button
                    onClick={() => {
                      setIsPostDetailsOpen(false)
                      router.push(`/dashboard/posts/edit/${selectedEvent.post.id}`)
                    }}
                  >
                    <Edit className="mr-2 h-3.5 w-3.5" />
                    Edit
                  </Button>
                </div>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Post Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          {selectedEvent && (
            <>
              <DialogHeader>
                <DialogTitle>Edit Post</DialogTitle>
                <DialogDescription>Make changes to your scheduled post</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="edit-platforms">Platforms</Label>
                  <div className="flex flex-wrap gap-2">
                    {accounts.map((account) => {
                      const platform = account.platform && typeof account.platform === 'string'
                        ? platformConfig[account.platform] || { icon: Plus, color: "#666" }
                        : { icon: Plus, color: "#666" }
                      const PlatformIcon = platform.icon
                      const isSelected = selectedEvent.post.account_id === account.id

                      return (
                        <Button
                          key={account.id}
                          variant={isSelected ? "default" : "outline"}
                          style={
                            isSelected
                              ? { backgroundColor: platform.color }
                              : { borderColor: platform.color, color: platform.color }
                          }
                        >
                          <PlatformIcon className="mr-2 h-4 w-4" />
                          {account.name}
                        </Button>
                      )
                    })}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="edit-content">Post Content</Label>
                  <Textarea id="edit-content" defaultValue={selectedEvent.post.content} className="min-h-[100px]" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Schedule Date</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full justify-start text-left font-normal">
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {format(selectedEvent.start, "PPP")}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <CalendarComponent
                          mode="single"
                          selected={selectedEvent.start}
                          onSelect={(date) => {
                            // In a real app, you would update the scheduled_at date here
                          }}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                  <div className="space-y-2">
                    <Label>Schedule Time</Label>
                    <Input type="time" defaultValue={format(selectedEvent.start, "HH:mm")} />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => {
                    // In a real app, you would save the changes here
                    setIsEditDialogOpen(false)
                    toast({
                      title: "Changes saved",
                      description: "Your post has been updated successfully.",
                    })
                  }}
                >
                  Save Changes
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Calendar,
  Facebook,
  Instagram,
  Linkedin,
  MessageSquare,
  MoreHorizontal,
  Plus,
  Search,
  Twitter,
  RefreshCw,
  Image as ImageIcon,
  Video,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getSocialBuAPI, withErrorHandling, type Post, type Account } from "@/lib/socialbu-api"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import Link from "next/link"

// Map platform names to icons and colors
const platformConfig: Record<string, { icon: any; color: string }> = {
  facebook: { icon: Facebook, color: "#1877F2" },
  instagram: { icon: Instagram, color: "#E1306C" },
  twitter: { icon: Twitter, color: "#1DA1F2" },
  linkedin: { icon: Linkedin, color: "#0A66C2" },
}

export default function PostsPage() {
  const [status, setStatus] = useState<string>("all")
  const [posts, setPosts] = useState<Post[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [platformFilter, setPlatformFilter] = useState("all")
  const [sortBy, setSortBy] = useState("newest")
  const [pagination, setPagination] = useState({
    currentPage: 1,
    lastPage: 1,
    total: 0
  })
  const { toast } = useToast()
  const router = useRouter()

  // Fetch posts and accounts
  const fetchData = async (page = 1) => {
    setIsLoading(true)
    try {
      await withErrorHandling(async () => {
        console.log('[Posts] Fetching data. Status:', status, 'Platform:', platformFilter, 'Sort:', sortBy, 'Page:', page);
        
        const api = getSocialBuAPI()

        // Fetch accounts first
        console.log('[Posts] Fetching accounts');
        const accountsData = await api.getAccounts()
        console.log('[Posts] Received accounts:', accountsData.length);
        setAccounts(accountsData)

        // Fetch posts with status filter if not "all"
        const statusParam = status !== "all" ? status : undefined
        const limit = 15; // Set desired page size
        
        console.log('[Posts] Fetching posts with params:', { 
          status: statusParam, 
          limit,
          page
        });

        // Fetch posts with pagination
        const postsResponse = await api.getPosts(limit, statusParam, page);
        console.log('[Posts] Received posts response:', JSON.stringify({
          currentPage: postsResponse.currentPage,
          lastPage: postsResponse.lastPage,
          total: postsResponse.total,
          itemsCount: postsResponse.items?.length || 0
        }, null, 2));
        
        // Store pagination data
        setPagination({
          currentPage: postsResponse.currentPage,
          lastPage: postsResponse.lastPage,
          total: postsResponse.total
        });

        // Get the posts from the items array
        const postsData = postsResponse.items || [];

        // Sort posts
        const sortedPosts = [...postsData]
        if (sortBy === "newest") {
          console.log('[Posts] Sorting by newest');
          sortedPosts.sort((a, b) => {
            const dateA = a.publish_at || a.published_at || a.created_at
            const dateB = b.publish_at || b.published_at || b.created_at
            return new Date(dateB).getTime() - new Date(dateA).getTime()
          })
        } else if (sortBy === "oldest") {
          console.log('[Posts] Sorting by oldest');
          sortedPosts.sort((a, b) => {
            const dateA = a.publish_at || a.published_at || a.created_at
            const dateB = b.publish_at || b.published_at || b.created_at
            return new Date(dateA).getTime() - new Date(dateB).getTime()
          })
        }

        setPosts(sortedPosts)
      }, "Failed to fetch posts")
    } catch (error) {
      console.error("[Posts] Error fetching data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // Change page
  const changePage = (newPage: number) => {
    console.log('[Posts] Changing to page:', newPage);
    fetchData(newPage);
  };

  // Delete a post
  const deletePost = async (postId: number) => {
    try {
      await withErrorHandling(async () => {
        console.log('[Posts] Deleting post:', postId);
        const api = getSocialBuAPI()
        await api.deletePost(postId)
        toast({
          title: "Post deleted",
          description: "The post has been successfully deleted.",
        })
        // Refresh posts list
        fetchData()
      }, "Failed to delete post")
    } catch (error) {
      console.error("[Posts] Error deleting post:", error)
    }
  }

  // Fetch data on component mount and when filters change
  useEffect(() => {
    console.log('[Posts] Filter changed, fetching new data');
    fetchData(1) // Reset to page 1 when filters change
  }, [status, platformFilter, sortBy])

  // Get account names for a post
  const getPostStatus = (post: Post): string => {
    if (post.error) return 'failed'
    if (post.published) return 'published'
    if (post.draft) return 'draft'
    if (post.publish_at) return 'scheduled'
    return 'unknown'
  }

  // Format date for display
  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return "Unknown date"

    const date = new Date(dateString)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return "Today"
    } else if (diffDays === 1) {
      return "Yesterday"
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  // Get post type icon
  const getPostTypeIcon = (post: Post) => {
    if (post.attachments && post.attachments.length > 0) {
      const type = post.attachments[0].type.toLowerCase()
      if (type.includes('image')) return <ImageIcon className="h-4 w-4" />
      if (type.includes('video')) return <Video className="h-4 w-4" />
    }
    return <MessageSquare className="h-4 w-4" />
  }

  return (
    <div className="flex flex-col h-full">
      <header className="border-b">
        <div className="container py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Posts</h1>
          <Button className="bg-[#FF8C2A] hover:bg-[#e67e25]" asChild>
            <Link href="/dashboard/posts/create">
              <Plus className="mr-2 h-4 w-4" /> Create Post
            </Link>
          </Button>
        </div>
      </header>
      <main className="flex-1 overflow-auto">
        <div className="container py-6">
          <Tabs defaultValue="all" value={status} onValueChange={setStatus}>
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <TabsList>
                <TabsTrigger value="all">All Posts</TabsTrigger>
                <TabsTrigger value="published">Published</TabsTrigger>
                <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
                <TabsTrigger value="draft">Drafts</TabsTrigger>
                <TabsTrigger value="failed">Failed</TabsTrigger>
              </TabsList>
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <div className="relative w-full sm:w-auto">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Search posts..." className="pl-8 w-full sm:w-[200px] lg:w-[300px]" />
                </div>
                <Button 
                  variant="outline" 
                  size="icon" 
                  onClick={() => {
                    void fetchData();
                  }} 
                  disabled={isLoading}
                >
                  {isLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <div className="flex flex-wrap items-center gap-2">
                <Select value={platformFilter} onValueChange={setPlatformFilter}>
                  <SelectTrigger className="w-[180px]">
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

                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="newest">Newest First</SelectItem>
                    <SelectItem value="oldest">Oldest First</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" className="h-9">
                  <Calendar className="mr-2 h-4 w-4" />
                  Date Range
                </Button>
              </div>
            </div>

            <TabsContent value="all" className="mt-0">
              {isLoading ? (
                <div className="flex justify-center p-8">
                  <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : posts.length === 0 ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                    <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium">No Posts Found</h3>
                    <p className="text-muted-foreground mt-2">
                      You don't have any posts yet. Create your first post to get started.
                    </p>
                    <Button className="mt-4" asChild>
                      <Link href="/dashboard/posts/create">
                        <Plus className="mr-2 h-4 w-4" />
                        Create Post
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {posts.map((post) => {
                    const postStatus = getPostStatus(post)
                    const statusColors: Record<string, string> = {
                      published: "bg-green-100 text-green-700",
                      scheduled: "bg-blue-100 text-blue-700",
                      draft: "bg-yellow-100 text-yellow-700",
                      failed: "bg-red-100 text-red-700",
                      unknown: "bg-gray-100 text-gray-700"
                    }

                    return (
                      <Card key={post.id} className="overflow-hidden">
                        <CardContent className="p-0">
                          <div className="p-4">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-2">
                                <div className="p-1 rounded-full bg-gray-100">
                                  {getPostTypeIcon(post)}
                                </div>
                                <span className="text-sm font-medium">{post.account_type || "Unknown Platform"}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={`text-xs px-2 py-1 rounded-full ${statusColors[postStatus]}`}>
                                  {postStatus.charAt(0).toUpperCase() + postStatus.slice(1)}
                                </span>
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-8 w-8">
                                      <MoreHorizontal className="h-4 w-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    {post.can_edit && (
                                      <DropdownMenuItem onClick={() => router.push(`/dashboard/posts/edit/${post.id}`)}>
                                        Edit
                                      </DropdownMenuItem>
                                    )}
                                    <DropdownMenuItem>Duplicate</DropdownMenuItem>
                                    {post.insights && <DropdownMenuItem>View Analytics</DropdownMenuItem>}
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem className="text-destructive" onClick={() => deletePost(post.id)}>
                                      Delete
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </div>
                            </div>

                            <div className="mb-3">
                              <p className="text-sm">{post.content}</p>
                              {post.attachments && post.attachments.length > 0 && (
                                <div className="mt-2 rounded-md overflow-hidden">
                                  <img 
                                    src={post.attachments[0].url} 
                                    alt="Post attachment" 
                                    className="w-full h-32 object-cover"
                                  />
                                </div>
                              )}
                            </div>

                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                              <div className="flex items-center">
                                <Calendar className="mr-1 h-3 w-3" />
                                <span>
                                  {postStatus === "published"
                                    ? `Posted ${formatDate(post.published_at || '')}`
                                    : postStatus === "scheduled"
                                      ? `Scheduled for ${formatDate(post.publish_at || '')}`
                                      : postStatus === "draft"
                                        ? `Draft • ${formatDate(post.updated_at)}`
                                        : postStatus === "failed"
                                          ? `Failed • ${post.error}`
                                          : formatDate(post.created_at)}
                                </span>
                              </div>
                              {post.user_name && (
                                <div className="flex items-center">
                                  <span>By {post.user_name}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}
              
              {/* Pagination Controls */}
              {!isLoading && posts.length > 0 && (
                <div className="flex justify-center mt-6">
                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => changePage(pagination.currentPage - 1)}
                      disabled={pagination.currentPage <= 1}
                    >
                      Previous
                    </Button>
                    
                    <div className="text-sm">
                      Page {pagination.currentPage} of {pagination.lastPage || 1}
                      <span className="text-muted-foreground ml-2">
                        ({pagination.total} total posts)
                      </span>
                    </div>
                    
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => changePage(pagination.currentPage + 1)}
                      disabled={pagination.currentPage >= pagination.lastPage}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="published" className="mt-0">
              {/* Similar structure as "all" tab but filtered for published posts */}
              {/* This is handled by the API call when status changes */}
            </TabsContent>

            <TabsContent value="scheduled" className="mt-0">
              {/* Similar structure as "all" tab but filtered for scheduled posts */}
              {/* This is handled by the API call when status changes */}
            </TabsContent>

            <TabsContent value="draft" className="mt-0">
              {/* Similar structure as "all" tab but filtered for draft posts */}
              {/* This is handled by the API call when status changes */}
            </TabsContent>

            <TabsContent value="failed" className="mt-0">
              {/* Similar structure as "all" tab but filtered for failed posts */}
              {/* This is handled by the API call when status changes */}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}

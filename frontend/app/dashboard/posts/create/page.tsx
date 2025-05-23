"use client"

import * as React from "react"
import { useState, useEffect } from "react"
// This fixes the React import error
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Calendar, Clock, Facebook, Hash, ImageIcon, Instagram, Linkedin, Twitter, Upload, Wand2, X, Sparkles, Video } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { format } from "date-fns"
import { useToast } from "@/components/ui/use-toast"
import { type SocialAccount, type Post, socialPlatformsApi } from "@/services/social-platforms-api"
import { getAPI } from "@/lib/api"
import { generateEnhancedContent } from "@/lib/ai-generation"

// Map platform names to icons and colors
const platformConfig: Record<string, { icon: any; color: string }> = {
  facebook: { icon: Facebook, color: "#1877F2" },
  instagram: { icon: Instagram, color: "#E1306C" },
  twitter: { icon: Twitter, color: "#1DA1F2" },
  linkedin: { icon: Linkedin, color: "#0A66C2" },
}

// Define Media type
interface Media {
  id: number
  url?: string
  type?: string
  thumbnail_url?: string
  duration?: number
  caption?: string
  alt_text?: string
  resource_type?: string
}

export default function CreatePostPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [date, setDate] = useState<Date>(new Date())
  const [time, setTime] = useState<string>(format(new Date(), "HH:mm"))
  const [selectedPlatforms, setSelectedPlatforms] = useState<number[]>([])
  const [uploadedMedia, setUploadedMedia] = useState<Media[]>([])
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [content, setContent] = useState<string>("")
  const [isDraft, setIsDraft] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [optimalTimes, setOptimalTimes] = useState<any>(null)
  const [isLoadingOptimalTimes, setIsLoadingOptimalTimes] = useState(false)

  useEffect(() => {
    fetchAccounts()
  }, [])

  // AI content generation function
  const generateContent = async (type: 'caption' | 'hashtags') => {
    setIsGenerating(true)
    try {
      // Get selected platform information
      const selectedPlatformNames = accounts
        .filter(acc => selectedPlatforms.includes(acc.id))
        .map(acc => acc.provider)

      // If no platforms selected, use default settings
      if (selectedPlatformNames.length === 0) {
        toast({
          title: "No platforms selected",
          description: "Generating general content. Select specific platforms for optimized results.",
          variant: "default",
        })
        selectedPlatformNames.push('general')
      }

      const api = getAPI();
      let generatedContent;

      // Use the ai/generate endpoint for both caption and hashtags
      const response = await api.request<{ content: string }>('api/ai/generate/', 'POST', {
        type,
        prompt: content,
        context: {
          platforms: selectedPlatformNames,
          mediaTypes: uploadedMedia.map(m => m.type),
          scheduledTime: date?.toISOString(),
          contentStructure: {
            tone: selectedPlatformNames.includes('linkedin') ? 'professional' : 'casual',
            format: uploadedMedia.length > 0 ? 'media-focused' : 'text-only',
            useEmoji: !selectedPlatformNames.includes('linkedin'),
            hashtagPlacement: selectedPlatformNames.includes('twitter') ? 'inline' : 'end'
          }
        }
      });

      generatedContent = response.content;

      // Update content based on generation type
      if (type === 'hashtags') {
        setContent(prev => `${prev}\n\n${generatedContent}`)
      } else {
        setContent(generatedContent)
      }

      toast({
        title: `${type === 'caption' ? 'Caption' : 'Hashtags'} generated`,
        description: "AI-generated content has been added to your post.",
      })
    } catch (error) {
      console.error("Error generating content:", error)
      toast({
        title: "Generation failed",
        description: "Failed to generate content. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  // Fetch connected accounts
  const fetchAccounts = async () => {
    try {
      const accountsData = await socialPlatformsApi.getAccounts()
      setAccounts(accountsData)
    } catch (error) {
      console.error("Error fetching accounts:", error)
      toast({
        title: "Failed to load accounts",
        description: "Could not load your connected social accounts.",
        variant: "destructive",
      })
    }
  }

  // Toggle platform selection
  const togglePlatform = (accountId: number) => {
    if (selectedPlatforms.includes(accountId)) {
      setSelectedPlatforms(selectedPlatforms.filter((id) => id !== accountId))
    } else {
      setSelectedPlatforms([...selectedPlatforms, accountId])
    }
  }

  // Handle media upload
  const handleMediaUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return

    setIsUploading(true)
    try {
      const file = e.target.files[0]

      // Determine media type based on file extension
      let mediaType = 'image'
      const fileName = file.name.toLowerCase()
      if (fileName.endsWith('.mp4') || fileName.endsWith('.mov') || fileName.endsWith('.webm')) {
        mediaType = 'video'
      } else if (fileName.endsWith('.mp3') || fileName.endsWith('.wav')) {
        mediaType = 'audio'
      } else if (fileName.endsWith('.pdf') || fileName.endsWith('.doc')) {
        mediaType = 'document'
      }

      // Create form data for Cloudinary upload
      const formData = new FormData()
      formData.append("file", file)
      
      // If we have a post ID, add it to associate with the post
      // This would be available if we're editing an existing post
      const postId = router.query?.id
      if (postId) {
        formData.append("post_id", postId as string)
      }

      // Directly communicate with the Django backend for Cloudinary uploads
      console.log("Attempting direct upload to Django backend...")
      
      // Define the Django backend URL
      const djangoBackendUrl = 'http://localhost:8000/';
      
      // Create a direct connection to the Django Cloudinary endpoint
      // IMPORTANT: The trailing slash is required for Django URL patterns
      const response = await fetch(`${djangoBackendUrl}api/posts/upload/cloudinary/`, {
        method: "POST",
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      })
      
      if (!response.ok) {
        console.error(`Upload failed with status: ${response.status}`, await response.text())
        throw new Error(`Failed to upload media (Status: ${response.status})`)
      }
      
      const cloudinaryData = await response.json()
      console.log("Successfully uploaded directly to Django backend", cloudinaryData)
      
      // Add the new media to state with Cloudinary URL
      const newMedia: Media = {
        id: cloudinaryData.id || Date.now(), // Use Cloudinary's ID if available or generate a temp one
        url: cloudinaryData.url,
        type: cloudinaryData.type || mediaType,
        thumbnail_url: cloudinaryData.thumbnail_url,
        duration: cloudinaryData.duration,
        resource_type: cloudinaryData.resource_type
      }
      
      setUploadedMedia([...uploadedMedia, newMedia])

      toast({
        title: "Media uploaded successfully",
        description: "Your media has been uploaded to Cloudinary.",
      })
    } catch (error) {
      console.error("Error uploading media:", error)
      toast({
        title: "Upload failed",
        description: "Failed to upload media. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
      // Reset the input
      if (e.target) e.target.value = ""
    }
  }

  // Remove media
  const removeMedia = (mediaId: number) => {
    setUploadedMedia(uploadedMedia.filter((media) => media.id !== mediaId))
  }

  // Create post
  const createPost = async () => {
    if (!content.trim()) {
      toast({
        title: "Content required",
        description: "Please add some content to your post.",
        variant: "destructive",
      })
      return
    }

    if (selectedPlatforms.length === 0) {
      toast({
        title: "Platform required",
        description: "Please select at least one platform to post to.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      // Create platforms array with selected accounts
      const platforms = selectedPlatforms.map((accountId) => {
        const account = accounts.find((a) => a.id === accountId)
        return {
          social_account: accountId,
          social_app: account?.social_app_id,
          custom_content: "",
        }
      })

      // Format date and time for scheduled posts
      const scheduledTime = isDraft
        ? null
        : new Date(`${format(date, "yyyy-MM-dd")}T${time}:00`)

      // Create post object
      const post: Post = {
        content,
        post_type: uploadedMedia.length > 0 ? (uploadedMedia[0].type || "image") : "text",
        scheduled_time: scheduledTime ? scheduledTime.toISOString() : "",
        status: isDraft ? "draft" : "scheduled",
        platforms,
      }

      // Create post
      await socialPlatformsApi.createPost(post)

      toast({
        title: isDraft ? "Draft saved" : "Post scheduled",
        description: isDraft
          ? "Your draft has been saved successfully."
          : `Your post has been scheduled for ${format(date, "MMM d, yyyy")} at ${time}.`,
      })

      // Navigate back to posts list
      router.push("/dashboard/posts")
    } catch (error) {
      console.error("Error creating post:", error)
      toast({
        title: "Post creation failed",
        description: "Failed to create post. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Get optimal posting time suggestions
  const getOptimalTimes = async (platform: string) => {
    setIsLoadingOptimalTimes(true)
    try {
      // Simulate API call for optimal times (would be replaced with actual API call)
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Sample optimal times (replace with actual API response)
      const times = {
        facebook: ["09:00", "15:00", "19:00"],
        instagram: ["12:00", "18:00", "21:00"],
        twitter: ["08:00", "12:00", "17:00"],
        linkedin: ["09:00", "13:00", "17:00"],
      }

      setOptimalTimes(times[platform as keyof typeof times] || ["12:00", "18:00"])
    } catch (error) {
      console.error("Error fetching optimal times:", error)
      toast({
        title: "Failed to load optimal times",
        description: "Could not retrieve optimal posting times.",
        variant: "destructive",
      })
    } finally {
      setIsLoadingOptimalTimes(false)
    }
  }

  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b">
        <div className="container flex items-center justify-between h-16">
          <h1 className="text-xl font-semibold">Create Post</h1>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push("/dashboard/posts")}>
              Cancel
            </Button>
            <Button variant="outline" onClick={() => setIsDraft(true)} disabled={isLoading}>
              {isLoading ? "Saving..." : "Save as Draft"}
            </Button>
            <Button onClick={() => {
              setIsDraft(false)
              createPost()
            }} disabled={isLoading}>
              {isLoading ? "Scheduling..." : "Schedule Post"}
            </Button>
          </div>
        </div>
      </header>
      <main className="flex-1 overflow-auto">
        <div className="container py-6">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            <div className="lg:col-span-3 space-y-6">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div>
                      <Textarea
                        placeholder="What's on your mind?"
                        className="min-h-[120px] resize-none"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                      />
                      <div className="flex flex-wrap gap-2 mt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-8"
                          onClick={() => generateContent('caption')}
                          disabled={isGenerating}
                        >
                          {isGenerating ? (
                            <>
                              <span className="animate-spin mr-2">◌</span> Generating...
                            </>
                          ) : (
                            <>
                              <Wand2 className="mr-2 h-3 w-3" /> Generate Caption
                            </>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-8"
                          onClick={() => generateContent('hashtags')}
                          disabled={isGenerating}
                        >
                          <Hash className="mr-2 h-3 w-3" /> Add Hashtags
                        </Button>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex flex-wrap gap-2">
                        {uploadedMedia.map((media) => (
                          <div key={media.id} className="relative rounded-md overflow-hidden w-24 h-24">
                            {media.type === 'video' ? (
                              <div className="relative w-full h-full">
                                <video
                                  src={media.url}
                                  poster={media.thumbnail_url}
                                  className="w-full h-full object-cover"
                                >
                                  Your browser does not support the video tag.
                                </video>
                                <Video className="absolute top-1 right-1 h-4 w-4 text-white drop-shadow-md" />
                              </div>
                            ) : (
                              <img src={media.url} alt={media.alt_text || ""} className="w-full h-full object-cover" />
                            )}
                            <button
                              className="absolute top-1 right-1 bg-black bg-opacity-50 rounded-full p-1"
                              onClick={() => removeMedia(media.id)}
                            >
                              <X className="h-3 w-3 text-white" />
                            </button>
                          </div>
                        ))}
                        <label className="aspect-square w-24 h-24 flex flex-col items-center justify-center border-dashed border-2 rounded-md cursor-pointer hover:bg-muted/50 transition-colors">
                          <input
                            type="file"
                            className="hidden"
                            accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                            onChange={handleMediaUpload}
                            disabled={isUploading}
                          />
                          {isUploading ? (
                            <div className="flex flex-col items-center">
                              <Upload className="h-6 w-6 mb-2 animate-pulse" />
                              <span className="text-xs">Uploading...</span>
                            </div>
                          ) : (
                            <div className="flex flex-col items-center">
                              <Upload className="h-6 w-6 mb-2" />
                              <span className="text-xs">Upload Media</span>
                              <span className="text-[10px] text-muted-foreground mt-1">Images, Videos & Docs</span>
                            </div>
                          )}
                        </label>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Supported formats: JPG, PNG, GIF, MP4, MOV (max 100MB)
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-medium mb-4">Scheduling</h3>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="date">Date</Label>
                        <Popover>
                          <PopoverTrigger asChild>
                            <Button
                              variant="outline"
                              className="w-full justify-start text-left font-normal mt-2"
                              disabled={isLoading}
                            >
                              <Calendar className="mr-2 h-4 w-4" />
                              {date ? format(date, "PPP") : "Select a date"}
                            </Button>
                          </PopoverTrigger>
                          <PopoverContent className="w-auto p-0">
                            <CalendarComponent
                              mode="single"
                              selected={date}
                              onSelect={(date) => date && setDate(date)}
                              initialFocus
                            />
                          </PopoverContent>
                        </Popover>
                      </div>
                      <div>
                        <Label htmlFor="time">Time</Label>
                        <div className="flex items-center gap-2 mt-2">
                          <Input
                            id="time"
                            type="time"
                            value={time}
                            onChange={(e) => setTime(e.target.value)}
                            className="flex-1"
                            disabled={isLoading}
                          />
                          <Popover>
                            <PopoverTrigger asChild>
                              <Button
                                variant="outline"
                                size="icon"
                                disabled={isLoadingOptimalTimes || isLoading}
                                onClick={() => {
                                  if (selectedPlatforms.length > 0) {
                                    const platform = accounts.find((a) => a.id === selectedPlatforms[0])?.provider || "facebook"
                                    getOptimalTimes(platform)
                                  } else {
                                    getOptimalTimes("facebook")
                                  }
                                }}
                              >
                                <Clock className="h-4 w-4" />
                              </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-[200px] p-4">
                              <div className="space-y-2">
                                <h4 className="font-medium text-sm">Optimal posting times</h4>
                                {isLoadingOptimalTimes ? (
                                  <div className="flex items-center justify-center py-2">
                                    <span className="animate-spin mr-2">◌</span>
                                    <span className="text-sm">Loading...</span>
                                  </div>
                                ) : (
                                  <div className="grid grid-cols-3 gap-2">
                                    {optimalTimes &&
                                      optimalTimes.map((optimalTime: string) => (
                                        <Button
                                          key={optimalTime}
                                          variant="outline"
                                          size="sm"
                                          className="w-full"
                                          onClick={() => setTime(optimalTime)}
                                        >
                                          {optimalTime}
                                        </Button>
                                      ))}
                                  </div>
                                )}
                                <p className="text-xs text-muted-foreground mt-2">
                                  Times optimized for maximum engagement
                                </p>
                              </div>
                            </PopoverContent>
                          </Popover>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-medium mb-4">Select Platforms</h3>
                  <div className="space-y-4">
                    {accounts.length > 0 ? (
                      accounts.map((account) => {
                        const platform = platformConfig[account.provider] || { icon: ImageIcon, color: "#666" }
                        const PlatformIcon = platform.icon
                        return (
                          <div
                            key={account.id}
                            className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
                              selectedPlatforms.includes(account.id)
                                ? "border-primary bg-primary/5"
                                : "border-border hover:border-primary/50"
                            }`}
                            onClick={() => togglePlatform(account.id)}
                          >
                            <div
                              className="p-2 rounded-full mr-3"
                              style={{ backgroundColor: `${platform.color}20` }}
                            >
                              <PlatformIcon className="h-5 w-5" style={{ color: platform.color }} />
                            </div>
                            <div>
                              <p className="font-medium">{account.display_name || account.provider}</p>
                              <p className="text-xs text-muted-foreground">
                                {account.provider.charAt(0).toUpperCase() + account.provider.slice(1)}
                              </p>
                            </div>
                          </div>
                        )
                      })
                    ) : (
                      <div className="text-center py-4">
                        <p className="text-muted-foreground text-sm mb-2">No social accounts connected</p>
                        <Button size="sm" variant="outline">
                          Connect Account
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-medium mb-4">Preview</h3>
                  <div className="space-y-6">
                    {selectedPlatforms.length > 0 && Array.isArray(accounts) && accounts.length > 0 ? (
                      accounts
                        .filter((account) => selectedPlatforms.includes(account.id))
                        .map((account) => {
                          const platform = platformConfig[account.provider] || { icon: ImageIcon, color: "#666" }
                          const PlatformIcon = platform.icon

                          return (
                            <div key={account.id} className="border rounded-lg p-4">
                              <div className="flex items-center gap-3 mb-3">
                                <div className="p-1 rounded-full" style={{ backgroundColor: `${platform.color}20` }}>
                                  <PlatformIcon className="h-5 w-5" style={{ color: platform.color }} />
                                </div>
                                <span className="font-medium">{account.display_name || account.provider} Preview</span>
                              </div>
                              <div className="bg-muted rounded-md h-40 flex items-center justify-center mb-3">
                                {uploadedMedia.length > 0 ? (
                                  <div className="w-full h-full flex items-center justify-center">
                                    {uploadedMedia[0].type === 'video' ? (
                                      <div className="relative w-full h-full">
                                        <video
                                          src={uploadedMedia[0].url}
                                          poster={uploadedMedia[0].thumbnail_url}
                                          controls
                                          className="h-full w-full object-contain"
                                        >
                                          Your browser does not support the video tag.
                                        </video>
                                        {uploadedMedia[0].duration && (
                                          <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs">
                                            {Math.floor(uploadedMedia[0].duration / 60)}:{(Math.floor(uploadedMedia[0].duration % 60)).toString().padStart(2, '0')}
                                          </div>
                                        )}
                                      </div>
                                    ) : (
                                      <img
                                        src={uploadedMedia[0].url || "/placeholder.svg"}
                                        alt={uploadedMedia[0].alt_text || "Preview"}
                                        className="h-full w-full object-contain"
                                      />
                                    )}
                                  </div>
                                ) : (
                                  <span className="text-xs text-muted-foreground">No media uploaded</span>
                                )}
                              </div>
                              <div className="text-sm">
                                <p className={content ? "" : "text-muted-foreground italic"}>
                                  {content || "Your post content will appear here..."}
                                </p>
                              </div>
                            </div>
                          )
                        })
                    ) : (
                      <div className="flex flex-col items-center justify-center text-center p-6">
                        <div className="bg-muted rounded-full p-3 mb-3">
                          <ImageIcon className="h-6 w-6 text-muted-foreground" />
                        </div>
                        <h4 className="font-medium mb-1">No platforms selected</h4>
                        <p className="text-sm text-muted-foreground">
                          Select at least one platform to see a preview of your post
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

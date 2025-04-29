"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Calendar, Clock, Facebook, ImageIcon, Instagram, Linkedin, Twitter, Upload, X } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { format } from "date-fns"
import { getSocialBuAPI, withErrorHandling, type Account, type Media } from "@/lib/socialbu-api"
import { useToast } from "@/components/ui/use-toast"

// Map platform names to icons and colors
const platformConfig: Record<string, { icon: any; color: string }> = {
  facebook: { icon: Facebook, color: "#1877F2" },
  instagram: { icon: Instagram, color: "#E1306C" },
  twitter: { icon: Twitter, color: "#1DA1F2" },
  linkedin: { icon: Linkedin, color: "#0A66C2" },
}

export default function CreatePostPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [date, setDate] = useState<Date>(new Date())
  const [time, setTime] = useState<string>(format(new Date(), "HH:mm"))
  const [selectedPlatforms, setSelectedPlatforms] = useState<number[]>([])
  const [uploadedMedia, setUploadedMedia] = useState<Media[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [content, setContent] = useState("")
  const [isDraft, setIsDraft] = useState(false)

  // Fetch connected accounts
  const fetchAccounts = async () => {
    try {
      await withErrorHandling(async () => {
        const api = getSocialBuAPI()
        const accountsData = await api.getAccounts()
        setAccounts(accountsData)

        // Select first account by default if available
        if (accountsData.length > 0) {
          setSelectedPlatforms([accountsData[0].id])
        }
      }, "Failed to fetch connected accounts")
    } catch (error) {
      console.error("Error fetching accounts:", error)
    }
  }

  // Fetch accounts on component mount
  useEffect(() => {
    fetchAccounts()
  }, [])

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
      await withErrorHandling(async () => {
        const api = getSocialBuAPI()
        const file = e.target.files![0]
        const media = await api.uploadMedia(file)
        setUploadedMedia([...uploadedMedia, media])
        toast({
          title: "Media uploaded",
          description: "Your media has been uploaded successfully.",
        })
      }, "Failed to upload media")
    } catch (error) {
      console.error("Error uploading media:", error)
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
    if (selectedPlatforms.length === 0) {
      toast({
        title: "No platforms selected",
        description: "Please select at least one platform to post to.",
        variant: "destructive",
      })
      return
    }

    if (!content.trim()) {
      toast({
        title: "No content",
        description: "Please enter some content for your post.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      await withErrorHandling(async () => {
        const api = getSocialBuAPI()

        // Combine date and time for scheduled_at
        const scheduledDate = new Date(date)
        const [hours, minutes] = time.split(":").map(Number)
        scheduledDate.setHours(hours, minutes)

        // Create post data in the new format required by SocialBu API
        const postData = {
          accounts: selectedPlatforms,
          content,
          draft: isDraft,
          // Format the date as "YYYY-MM-DD HH:MM:SS" string instead of ISO format
          publish_at: isDraft ? undefined : format(scheduledDate, "yyyy-MM-dd HH:mm:ss"),
          // Convert uploaded media to the format expected by SocialBu
          existing_attachments: uploadedMedia.length > 0 
            ? uploadedMedia.map(media => ({ 
                upload_token: media.id.toString() 
              }))
            : undefined,
          // Optional fields
          team_id: 0, // Default to 0 if no specific team ID is available
          postback_url: "https://186b-41-139-175-41.ngrok-free.app/dashboard/posts",
          options: {
            post_as_story: false // Set to true for story-type posts
          }
        }

        // Create post
        const post = await api.createPost(postData)

        toast({
          title: isDraft ? "Draft saved" : "Post scheduled",
          description: isDraft
            ? "Your draft has been saved successfully."
            : `Your post has been scheduled for ${format(scheduledDate, "PPP p")}.`,
        })

        // Redirect to posts page
        router.push("/dashboard/posts")
      }, "Failed to create post")
    } catch (error) {
      console.error("Error creating post:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <header className="border-b">
        <div className="container py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Create Post</h1>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setIsDraft(true)
                createPost()
              }}
              disabled={isLoading}
            >
              Save as Draft
            </Button>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline">
                  <Calendar className="mr-2 h-4 w-4" />
                  {date ? format(date, "PPP") : "Schedule"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <CalendarComponent 
                  mode="single" 
                  selected={date} 
                  onSelect={(newDate) => newDate && setDate(newDate)} 
                  initialFocus 
                />
                <div className="p-3 border-t">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <Input type="time" className="w-full" value={time} onChange={(e) => setTime(e.target.value)} />
                  </div>
                  <Button
                    className="w-full mt-3 bg-[#1E5AA8] hover:bg-[#174a8c]"
                    onClick={() => {
                      document
                        .querySelector('[data-state="open"] button[aria-label="Close"]')
                        ?.dispatchEvent(new MouseEvent("click", { bubbles: true }))
                    }}
                  >
                    Confirm Schedule
                  </Button>
                </div>
              </PopoverContent>
            </Popover>
            <Button
              className="bg-[#FF8C2A] hover:bg-[#e67e25]"
              onClick={() => {
                setIsDraft(false)
                createPost()
              }}
              disabled={isLoading}
            >
              {isLoading ? "Publishing..." : "Publish Now"}
            </Button>
          </div>
        </div>
      </header>
      <main className="flex-1 overflow-auto">
        <div className="container py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div>
                      <Label className="text-base font-medium mb-2 block">Select Platforms</Label>
                      <div className="flex flex-wrap gap-3">
                        {accounts.map((account) => {
                          const platform = platformConfig[account.platform] || { icon: ImageIcon, color: "#666" }
                          const PlatformIcon = platform.icon
                          const isSelected = selectedPlatforms.includes(account.id)

                          return (
                            <Button
                              key={account.id}
                              variant={isSelected ? "default" : "outline"}
                              className={isSelected ? "" : ""}
                              style={
                                isSelected
                                  ? { backgroundColor: platform.color }
                                  : { borderColor: platform.color, color: platform.color }
                              }
                              onClick={() => togglePlatform(account.id)}
                            >
                              <PlatformIcon className="mr-2 h-4 w-4" />
                              {account.name}
                            </Button>
                          )
                        })}

                        {accounts.length === 0 && (
                          <div className="text-muted-foreground text-sm">
                            No connected platforms. Please connect a platform first.
                          </div>
                        )}
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="content" className="text-base font-medium mb-2 block">
                        Post Content
                      </Label>
                      <Textarea
                        id="content"
                        placeholder="What would you like to share?"
                        className="min-h-[150px]"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                      />
                      <div className="flex justify-between text-xs text-muted-foreground mt-2">
                        <span>Add #hashtags to increase visibility</span>
                        <span>{content.length}/280 characters</span>
                      </div>
                    </div>

                    <div>
                      <Label className="text-base font-medium mb-2 block">Media</Label>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
                        {uploadedMedia.map((media) => (
                          <div key={media.id} className="relative aspect-square rounded-md overflow-hidden border">
                            <img
                              src={media.url || "/placeholder.svg"}
                              alt={`Uploaded media ${media.id}`}
                              className="w-full h-full object-cover"
                            />
                            <Button
                              variant="destructive"
                              size="icon"
                              className="absolute top-2 right-2 h-6 w-6 rounded-full"
                              onClick={() => removeMedia(media.id)}
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                        <label className="aspect-square flex flex-col items-center justify-center border-dashed border-2 rounded-md cursor-pointer hover:bg-muted/50 transition-colors">
                          <input
                            type="file"
                            className="hidden"
                            accept="image/*,video/*"
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
                            </div>
                          )}
                        </label>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Supported formats: JPG, PNG, GIF, MP4 (max 100MB)
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <Label className="text-base font-medium mb-2 block">Advanced Options</Label>
                  <Tabs defaultValue="general">
                    <TabsList className="mb-4">
                      <TabsTrigger value="general">General</TabsTrigger>
                      <TabsTrigger value="facebook">Facebook</TabsTrigger>
                      <TabsTrigger value="instagram">Instagram</TabsTrigger>
                    </TabsList>
                    <TabsContent value="general">
                      <div className="space-y-4">
                        <div className="flex items-start space-x-2">
                          <Checkbox id="first-comment" />
                          <div className="grid gap-1.5 leading-none">
                            <Label htmlFor="first-comment">Add first comment</Label>
                            <p className="text-sm text-muted-foreground">Automatically add a comment to your post</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Checkbox id="alt-text" />
                          <div className="grid gap-1.5 leading-none">
                            <Label htmlFor="alt-text">Generate alt text for images</Label>
                            <p className="text-sm text-muted-foreground">
                              Automatically generate accessible alt text for uploaded images
                            </p>
                          </div>
                        </div>
                      </div>
                    </TabsContent>
                    <TabsContent value="facebook">
                      <div className="space-y-4">
                        <div className="flex items-start space-x-2">
                          <Checkbox id="fb-link" />
                          <div className="grid gap-1.5 leading-none">
                            <Label htmlFor="fb-link">Include link preview</Label>
                            <p className="text-sm text-muted-foreground">
                              Show a preview card for any links in your post
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Checkbox id="fb-location" />
                          <div className="grid gap-1.5 leading-none">
                            <Label htmlFor="fb-location">Add location</Label>
                            <p className="text-sm text-muted-foreground">Tag a location in your post</p>
                          </div>
                        </div>
                      </div>
                    </TabsContent>
                    <TabsContent value="instagram">
                      <div className="space-y-4">
                        <div className="flex items-start space-x-2">
                          <Checkbox id="ig-carousel" />
                          <div className="grid gap-1.5 leading-none">
                            <Label htmlFor="ig-carousel">Post as carousel</Label>
                            <p className="text-sm text-muted-foreground">Create a multi-image carousel post</p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-2">
                          <Checkbox id="ig-tag" />
                          <div className="grid gap-1.5 leading-none">
                            <Label htmlFor="ig-tag">Tag people</Label>
                            <p className="text-sm text-muted-foreground">Tag accounts in your media</p>
                          </div>
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </div>

            <div>
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-medium mb-4">Preview</h3>
                  <div className="space-y-6">
                    {selectedPlatforms.length > 0 ? (
                      accounts
                        .filter((account) => selectedPlatforms.includes(account.id))
                        .map((account) => {
                          const platform = platformConfig[account.platform] || { icon: ImageIcon, color: "#666" }
                          const PlatformIcon = platform.icon

                          return (
                            <div key={account.id} className="border rounded-lg p-4">
                              <div className="flex items-center gap-3 mb-3">
                                <div className="p-1 rounded-full" style={{ backgroundColor: `${platform.color}20` }}>
                                  <PlatformIcon className="h-5 w-5" style={{ color: platform.color }} />
                                </div>
                                <span className="font-medium">{account.name} Preview</span>
                              </div>
                              <div className="bg-muted rounded-md h-40 flex items-center justify-center mb-3">
                                {uploadedMedia.length > 0 ? (
                                  <div className="w-full h-full flex items-center justify-center">
                                    <img
                                      src={uploadedMedia[0].url || "/placeholder.svg"}
                                      alt="Preview"
                                      className="h-full w-full object-contain"
                                    />
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

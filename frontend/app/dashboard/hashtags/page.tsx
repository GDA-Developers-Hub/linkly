"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Search,
  Hash,
  TrendingUp,
  Save,
  Copy,
  Plus,
  Instagram,
  Twitter,
  Linkedin,
  Facebook,
  RefreshCw,
  Filter,
} from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { getAPI, type Hashtag, type HashtagGroup } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"

export default function HashtagsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPlatform, setSelectedPlatform] = useState("instagram")
  const [activeTab, setActiveTab] = useState("trending")
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [trendingHashtags, setTrendingHashtags] = useState<Hashtag[]>([])
  const [relatedHashtags, setRelatedHashtags] = useState<Hashtag[]>([])
  const [savedGroups, setSavedGroups] = useState<HashtagGroup[]>([])
  const [generatedHashtags, setGeneratedHashtags] = useState<Hashtag[]>([])
  const [contentType, setContentType] = useState("general")
  const [hashtagCount, setHashtagCount] = useState("20")
  const [popularityMix, setPopularityMix] = useState("balanced")
  const [keywords, setKeywords] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const { toast } = useToast()
  const api = getAPI()

  // Fetch trending hashtags and saved groups on component mount
  useEffect(() => {
    fetchTrendingHashtags()
    fetchSavedGroups()
  }, [])

  const fetchTrendingHashtags = async () => {
    setIsRefreshing(true)
    try {
      const hashtags = await api.getTrendingHashtags(selectedPlatform)
      setTrendingHashtags(hashtags)
    } catch (error) {
      console.error("Error fetching trending hashtags:", error)
      toast({
        title: "Error",
        description: "Failed to fetch trending hashtags. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const fetchSavedGroups = async () => {
    try {
      const groups = await api.getSavedHashtagGroups()
      setSavedGroups(groups)
    } catch (error) {
      console.error("Error fetching saved hashtag groups:", error)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: "Input required",
        description: "Please enter a hashtag to search for related tags.",
        variant: "destructive",
      })
      return
    }

    setIsRefreshing(true)
    try {
      const hashtags = await api.getRelatedHashtags(searchQuery, selectedPlatform)
      setRelatedHashtags(hashtags)
      setActiveTab("related")
    } catch (error) {
      console.error("Error searching for related hashtags:", error)
      toast({
        title: "Search failed",
        description: "Failed to find related hashtags. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleGenerateHashtags = async () => {
    if (!keywords.trim()) {
      toast({
        title: "Input required",
        description: "Please enter at least one keyword.",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    try {
      const keywordArray = keywords
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k)
      const hashtags = await api.generateHashtags(
        keywordArray,
        selectedPlatform,
        contentType,
        Number.parseInt(hashtagCount),
        popularityMix,
      )
      setGeneratedHashtags(hashtags)
      toast({
        title: "Hashtags generated",
        description: `Successfully generated ${hashtags.length} hashtags.`,
      })
    } catch (error) {
      console.error("Error generating hashtags:", error)
      toast({
        title: "Generation failed",
        description: "Failed to generate hashtags. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveHashtagGroup = async () => {
    if (generatedHashtags.length === 0) return

    try {
      const groupName = prompt("Enter a name for this hashtag group:")
      if (!groupName) return

      const savedGroup = await api.saveHashtagGroup({
        name: groupName,
        hashtags: generatedHashtags.map(tag => tag.name || tag.hashtag),
        platform: selectedPlatform,
      })

      setSavedGroups((prev) => [savedGroup, ...prev])
      toast({
        title: "Group saved",
        description: "Hashtag group has been saved to your library.",
      })
    } catch (error) {
      console.error("Error saving hashtag group:", error)
      toast({
        title: "Save failed",
        description: "Failed to save hashtag group. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleCopyHashtags = (hashtags: Hashtag[]) => {
    const hashtagText = hashtags.map((tag) => `#${tag.name || tag.hashtag}`).join(" ")
    navigator.clipboard.writeText(hashtagText)
    toast({
      title: "Copied to clipboard",
      description: "Hashtags have been copied to your clipboard.",
    })
  }

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case "instagram":
        return <Instagram className="h-4 w-4 text-pink-500" />
      case "twitter":
        return <Twitter className="h-4 w-4 text-blue-400" />
      case "facebook":
        return <Facebook className="h-4 w-4 text-blue-600" />
      case "linkedin":
        return <Linkedin className="h-4 w-4 text-blue-700" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Hashtag Research</h2>
          <p className="text-muted-foreground">Discover and analyze trending hashtags for your content</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchTrendingHashtags} disabled={isRefreshing}>
            {isRefreshing ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Refresh Data
          </Button>
          <Button onClick={() => setActiveTab("saved")}>
            <Plus className="mr-2 h-4 w-4" />
            Save Hashtag Group
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-4 md:flex-row">
        <div className="w-full md:w-2/3">
          <Card>
            <CardHeader>
              <CardTitle>Hashtag Explorer</CardTitle>
              <CardDescription>Search and analyze hashtags across platforms</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-4 sm:flex-row">
                <div className="relative flex-1">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search hashtags..."
                    className="pl-8"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select platform" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="instagram">Instagram</SelectItem>
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="facebook">Facebook</SelectItem>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="all">All Platforms</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={handleSearch}>
                  <Search className="mr-2 h-4 w-4" />
                  Search
                </Button>
              </div>

              <Tabs defaultValue="trending" value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="trending">Trending</TabsTrigger>
                  <TabsTrigger value="related">Related</TabsTrigger>
                  <TabsTrigger value="saved">Saved</TabsTrigger>
                </TabsList>
                <TabsContent value="trending" className="space-y-4 pt-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    {isRefreshing && trendingHashtags.length === 0 ? (
                      <div className="col-span-2 flex justify-center p-8">
                        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                      </div>
                    ) : trendingHashtags.length > 0 ? (
                      trendingHashtags.map((hashtag, index) => (
                        <div key={index} className="rounded-lg border p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Hash className="h-5 w-5 text-primary" />
                              <span className="text-lg font-medium">#{hashtag.name || hashtag.hashtag}</span>
                            </div>
                            <Button variant="ghost" size="icon" title="Save hashtag">
                              <Save className="h-4 w-4" />
                            </Button>
                          </div>
                          <div className="mt-2 grid grid-cols-2 gap-2">
                            <div>
                              <p className="text-xs text-muted-foreground">Posts</p>
                              <p className="font-medium">{(hashtag.post_count || hashtag.posts || 0).toLocaleString()}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Growth</p>
                              <p className="font-medium">+{hashtag.growth_rate || hashtag.growth || 0}%</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Engagement</p>
                              <p className="font-medium">{hashtag.engagement_rate || hashtag.engagement || 0}%</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Trending</p>
                              <p className="font-medium">{hashtag.is_trending ? "Yes" : "No"}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="col-span-2 text-center text-muted-foreground py-8">
                        No trending hashtags found. Try refreshing the data.
                      </div>
                    )}
                  </div>
                </TabsContent>
                <TabsContent value="related" className="pt-4">
                  {searchQuery ? (
                    <>
                      {isRefreshing ? (
                        <div className="flex justify-center p-8">
                          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                        </div>
                      ) : relatedHashtags.length > 0 ? (
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                          {relatedHashtags.map((hashtag, index) => (
                            <div key={index} className="rounded-lg border p-4">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <Hash className="h-5 w-5 text-primary" />
                                  <span className="text-lg font-medium">#{hashtag.name || hashtag.hashtag}</span>
                                </div>
                                <Button variant="ghost" size="icon" title="Save hashtag">
                                  <Save className="h-4 w-4" />
                                </Button>
                              </div>
                              <div className="mt-2 grid grid-cols-2 gap-2">
                                <div>
                                  <p className="text-xs text-muted-foreground">Posts</p>
                                  <p className="font-medium">{(hashtag.post_count || hashtag.posts || 0).toLocaleString()}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">Growth</p>
                                  <p className="font-medium">+{hashtag.growth_rate || hashtag.growth || 0}%</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">Engagement</p>
                                  <p className="font-medium">{hashtag.engagement_rate || hashtag.engagement || 0}%</p>
                                </div>
                                <div>
                                  <p className="text-xs text-muted-foreground">Trending</p>
                                  <p className="font-medium">{hashtag.is_trending ? "Yes" : "No"}</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="rounded-lg border p-8 text-center">
                          <p className="text-muted-foreground">No related hashtags found for "{searchQuery}"</p>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="rounded-lg border p-8 text-center">
                      <p className="text-muted-foreground">Search for a hashtag to see related tags</p>
                    </div>
                  )}
                </TabsContent>
                <TabsContent value="saved" className="pt-4">
                  {savedGroups.length > 0 ? (
                    <div className="grid gap-4 md:grid-cols-2">
                      {savedGroups.map((group, index) => (
                        <div key={index} className="rounded-lg border p-4">
                          <div className="flex items-center justify-between">
                            <div className="font-medium">{group.name}</div>
                            <Badge variant="outline">{group.hashtags.length}</Badge>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-1">
                            {group.hashtags.slice(0, 5).map((tag, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                #{typeof tag === 'string' ? tag : (tag.name || tag.hashtag)}
                              </Badge>
                            ))}
                            {group.hashtags.length > 5 && (
                              <Badge variant="outline" className="text-xs">
                                +{group.hashtags.length - 5} more
                              </Badge>
                            )}
                          </div>
                          <div className="mt-3 flex items-center justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 px-2"
                              onClick={() => {
                                const formattedTags = Array.isArray(group.hashtags) 
                                  ? group.hashtags.map(tag => 
                                      typeof tag === 'string' ? tag : (tag.name || tag.hashtag)
                                    )
                                  : [];
                                handleCopyHashtags(formattedTags.map(tag => ({ name: tag })));
                              }}
                            >
                              <Copy className="h-3.5 w-3.5" />
                              <span className="ml-1">Copy</span>
                            </Button>
                            <Button variant="ghost" size="sm" className="h-8 px-2">
                              <Filter className="h-3.5 w-3.5" />
                              <span className="ml-1">Edit</span>
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-lg border p-4">
                      <div className="text-center text-muted-foreground">You haven't saved any hashtags yet</div>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        <div className="w-full md:w-1/3 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Hashtag Groups</CardTitle>
              <CardDescription>Your saved hashtag collections</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {savedGroups.length > 0 ? (
                savedGroups.slice(0, 3).map((group, index) => (
                  <div key={index} className="rounded-lg border p-3">
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{group.name}</div>
                      <Badge variant="outline">{group.hashtags.length}</Badge>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {group.hashtags.slice(0, 5).map((tag, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          #{typeof tag === 'string' ? tag : (tag.name || tag.hashtag)}
                        </Badge>
                      ))}
                      {group.hashtags.length > 5 && (
                        <Badge variant="outline" className="text-xs">
                          +{group.hashtags.length - 5} more
                        </Badge>
                      )}
                    </div>
                    <div className="mt-3 flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 px-2"
                        onClick={() => {
                          const formattedTags = Array.isArray(group.hashtags) 
                            ? group.hashtags.map(tag => 
                                typeof tag === 'string' ? tag : (tag.name || tag.hashtag)
                              )
                            : [];
                          handleCopyHashtags(formattedTags.map(tag => ({ name: tag })));
                        }}
                      >
                        <Copy className="h-3.5 w-3.5" />
                        <span className="ml-1">Copy</span>
                      </Button>
                      <Button variant="ghost" size="sm" className="h-8 px-2">
                        <Filter className="h-3.5 w-3.5" />
                        <span className="ml-1">Edit</span>
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-4">No saved hashtag groups yet</div>
              )}
              <Button variant="outline" className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Create New Group
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Hashtag Performance</CardTitle>
              <CardDescription>Engagement by hashtag category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] flex items-center justify-center border rounded">
                <div className="text-center text-muted-foreground">
                  <Hash className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                  <p>Hashtag performance chart</p>
                  <p className="text-xs mt-1">Data visualization will appear here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Hashtag Generator</CardTitle>
          <CardDescription>Create optimized hashtag sets for your content</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="content-type">Content Type</Label>
              <Select value={contentType} onValueChange={setContentType}>
                <SelectTrigger id="content-type">
                  <SelectValue placeholder="Select content type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General Post</SelectItem>
                  <SelectItem value="product">Product Showcase</SelectItem>
                  <SelectItem value="educational">Educational Content</SelectItem>
                  <SelectItem value="behindscenes">Behind the Scenes</SelectItem>
                  <SelectItem value="promotion">Promotion/Sale</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="platform">Platform</Label>
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger id="platform">
                  <SelectValue placeholder="Select platform" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="twitter">Twitter</SelectItem>
                  <SelectItem value="facebook">Facebook</SelectItem>
                  <SelectItem value="linkedin">LinkedIn</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="keywords">Keywords (separated by commas)</Label>
            <Input
              id="keywords"
              placeholder="e.g., marketing, social media, digital"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="hashtag-count">Number of Hashtags</Label>
              <Select value={hashtagCount} onValueChange={setHashtagCount}>
                <SelectTrigger id="hashtag-count">
                  <SelectValue placeholder="Select count" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10 hashtags</SelectItem>
                  <SelectItem value="15">15 hashtags</SelectItem>
                  <SelectItem value="20">20 hashtags</SelectItem>
                  <SelectItem value="30">30 hashtags</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="popularity">Popularity Mix</Label>
              <Select value={popularityMix} onValueChange={setPopularityMix}>
                <SelectTrigger id="popularity">
                  <SelectValue placeholder="Select mix" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="niche">Mostly Niche</SelectItem>
                  <SelectItem value="balanced">Balanced</SelectItem>
                  <SelectItem value="popular">Mostly Popular</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button className="w-full" onClick={handleGenerateHashtags} disabled={isGenerating}>
            {isGenerating ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Hash className="mr-2 h-4 w-4" />
                Generate Hashtags
              </>
            )}
          </Button>

          {generatedHashtags.length > 0 && (
            <div className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div className="font-medium">Generated Hashtags</div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={handleSaveHashtagGroup}>
                    <Save className="mr-2 h-3.5 w-3.5" />
                    Save
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleCopyHashtags(generatedHashtags)}>
                    <Copy className="mr-2 h-3.5 w-3.5" />
                    Copy All
                  </Button>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {generatedHashtags.map((tag, index) => (
                  <Badge key={index} variant="outline" className="text-sm px-3 py-1">
                    #{tag.name || tag.hashtag}
                    {tag.post_count && (
                      <span className="ml-2 text-xs text-muted-foreground">
                        {tag.post_count.toLocaleString()} posts
                      </span>
                    )}
                  </Badge>
                ))}
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
                <div>
                  <span className="text-muted-foreground">
                    Popular ({Math.floor(generatedHashtags.length * 0.25)}):
                  </span>
                  {generatedHashtags
                    .slice(0, Math.floor(generatedHashtags.length * 0.25))
                    .map((t) => `#${t.name || t.hashtag}`)
                    .join(", ")
                    .substring(0, 20)}
                  ...
                </div>
                <div>
                  <span className="text-muted-foreground">Medium ({Math.floor(generatedHashtags.length * 0.5)}):</span>
                  {generatedHashtags
                    .slice(Math.floor(generatedHashtags.length * 0.25), Math.floor(generatedHashtags.length * 0.75))
                    .map((t) => `#${t.name || t.hashtag}`)
                    .join(", ")
                    .substring(0, 20)}
                  ...
                </div>
                <div>
                  <span className="text-muted-foreground">Niche ({Math.floor(generatedHashtags.length * 0.25)}):</span>
                  {generatedHashtags
                    .slice(Math.floor(generatedHashtags.length * 0.75))
                    .map((t) => `#${t.name || t.hashtag}`)
                    .join(", ")
                    .substring(0, 20)}
                  ...
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Sparkles, Save, Copy, ThumbsUp, ThumbsDown, RefreshCw, ImageIcon } from "lucide-react"
import { getAPI, type Caption } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"

export default function CaptionGeneratorPage() {
  const [prompt, setPrompt] = useState("")
  const [platform, setPlatform] = useState("instagram")
  const [tone, setTone] = useState("professional")
  const [length, setLength] = useState(50)
  const [includeHashtags, setIncludeHashtags] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedCaption, setGeneratedCaption] = useState<Caption | null>(null)
  const [savedCaptions, setSavedCaptions] = useState<Caption[]>([])
  const { toast } = useToast()
  const api = getAPI()

  // Fetch saved captions on component mount
  useState(() => {
    const fetchSavedCaptions = async () => {
      try {
        const captions = await api.getSavedCaptions()
        setSavedCaptions(captions)
      } catch (error) {
        console.error("Error fetching saved captions:", error)
      }
    }

    fetchSavedCaptions()
  }, [])

  const handleGenerate = async () => {
    if (!prompt) {
      toast({
        title: "Input required",
        description: "Please enter a prompt to generate a caption.",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)

    try {
      const caption = await api.generateCaption(prompt, platform, tone, length, includeHashtags)
      setGeneratedCaption(caption)
      toast({
        title: "Caption generated",
        description: "Your caption has been successfully generated.",
      })
    } catch (error) {
      console.error("Error generating caption:", error)
      toast({
        title: "Generation failed",
        description: "Failed to generate caption. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveCaption = async () => {
    if (!generatedCaption) return

    try {
      const savedCaption = await api.saveCaption({
        text: generatedCaption.text,
        platform,
        hashtags: generatedCaption.hashtags,
      })

      setSavedCaptions((prev) => [savedCaption, ...prev])

      toast({
        title: "Caption saved",
        description: "Your caption has been saved to your library.",
      })
    } catch (error) {
      console.error("Error saving caption:", error)
      toast({
        title: "Save failed",
        description: "Failed to save caption. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleCopyCaption = () => {
    if (!generatedCaption) return

    navigator.clipboard.writeText(generatedCaption.text)

    toast({
      title: "Copied to clipboard",
      description: "Caption has been copied to your clipboard.",
    })
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Handle image upload logic here
    toast({
      title: "Image uploaded",
      description: "Your image has been uploaded and will be analyzed for caption suggestions.",
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">AI Caption Generator</h2>
          <p className="text-muted-foreground">Create engaging captions for your social media posts</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Generate Caption</CardTitle>
              <CardDescription>Describe what your post is about or upload an image</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="prompt">Prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe what your post is about, e.g., 'A behind-the-scenes look at our product development process'"
                  className="min-h-[100px]"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label>Upload Image (Optional)</Label>
                <div className="flex items-center justify-center border border-dashed rounded-md p-4">
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    id="image-upload"
                    onChange={handleImageUpload}
                  />
                  <label htmlFor="image-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center space-y-2">
                      <ImageIcon className="h-8 w-8 text-muted-foreground" />
                      <div className="text-sm text-muted-foreground">Drag & drop or click to upload</div>
                    </div>
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="platform">Platform</Label>
                  <Select value={platform} onValueChange={setPlatform}>
                    <SelectTrigger id="platform">
                      <SelectValue placeholder="Select platform" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instagram">Instagram</SelectItem>
                      <SelectItem value="twitter">Twitter/X</SelectItem>
                      <SelectItem value="facebook">Facebook</SelectItem>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                      <SelectItem value="tiktok">TikTok</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tone">Tone</Label>
                  <Select value={tone} onValueChange={setTone}>
                    <SelectTrigger id="tone">
                      <SelectValue placeholder="Select tone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="humorous">Humorous</SelectItem>
                      <SelectItem value="inspirational">Inspirational</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="length">Caption Length</Label>
                  <span className="text-sm text-muted-foreground">
                    {length < 33 ? "Short" : length < 66 ? "Medium" : "Long"}
                  </span>
                </div>
                <Slider value={[length]} onValueChange={(values) => setLength(values[0])} max={100} step={1} />
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Switch id="hashtags" checked={includeHashtags} onCheckedChange={setIncludeHashtags} />
                  <Label htmlFor="hashtags">Include Hashtags</Label>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full" onClick={handleGenerate} disabled={isGenerating}>
                {isGenerating ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Generate Caption
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>

          {generatedCaption && (
            <Card>
              <CardHeader>
                <CardTitle>Generated Caption</CardTitle>
                <CardDescription>Your AI-generated caption</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="rounded-lg border p-4">
                  <p className="text-sm">{generatedCaption.text}</p>
                  {generatedCaption.hashtags && generatedCaption.hashtags.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-1">
                      {generatedCaption.hashtags.map((tag, index) => (
                        <Badge key={index} variant="secondary">
                          #{tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="icon">
                    <ThumbsUp className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="icon">
                    <ThumbsDown className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleGenerate}>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Regenerate
                  </Button>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm" onClick={handleSaveCaption}>
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleCopyCaption}>
                    <Copy className="mr-2 h-4 w-4" />
                    Copy
                  </Button>
                </div>
              </CardFooter>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Saved Captions</CardTitle>
              <CardDescription>Your library of saved captions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {savedCaptions.length > 0 ? (
                savedCaptions.slice(0, 3).map((caption, index) => (
                  <div key={index} className="rounded-lg border p-3">
                    <p className="text-sm line-clamp-2">{caption.text}</p>
                    <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                      <span>
                        {caption.date_created ? new Date(caption.date_created).toLocaleDateString() : "Recently saved"}
                      </span>
                      <Badge variant="outline">{caption.platform}</Badge>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-4">No saved captions yet</div>
              )}
              <Button variant="outline" className="w-full">
                View All Saved Captions
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Caption Tips</CardTitle>
              <CardDescription>Best practices for engaging captions</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start">
                  <span className="mr-2 text-primary">•</span>
                  <span>Start with a hook to grab attention in the first line</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-primary">•</span>
                  <span>Include a call-to-action to boost engagement</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-primary">•</span>
                  <span>Use emojis strategically to add personality</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-primary">•</span>
                  <span>Keep hashtags relevant and limit to 5-10 for Instagram</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-primary">•</span>
                  <span>Ask questions to encourage comments</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-primary">•</span>
                  <span>Tell a story that resonates with your audience</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

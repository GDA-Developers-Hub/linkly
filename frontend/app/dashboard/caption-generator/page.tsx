"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Sparkles, Save, Copy, ThumbsUp, ThumbsDown, RefreshCw, ImageIcon, X, Loader2 } from "lucide-react"
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
  const [uploadedImage, setUploadedImage] = useState<{ id: number; url: string } | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
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
    if (!prompt && !uploadedImage) {
      toast({
        title: "Input required",
        description: "Please enter a prompt or upload an image to generate a caption.",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)

    try {
      const response = await api.generateCaption(
        prompt, 
        platform, 
        tone, 
        length, 
        includeHashtags,
        uploadedImage?.id
      )
      
      // Extract the caption from the response
      const captionData = response.caption || response;
      setGeneratedCaption(captionData);
      
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

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    try {
      // Upload the image
      const media = await api.uploadMedia(file)
      setUploadedImage({ id: media.id, url: media.url })
      toast({
        title: "Image uploaded",
        description: "Your image has been uploaded and can be used for caption suggestions.",
      })
    } catch (error) {
      console.error("Error uploading image:", error)
      
      // Create a more descriptive error message
      let errorMessage = "Failed to upload image. Please try again."
      if (error instanceof Error) {
        errorMessage = error.message || errorMessage
      }
      
      toast({
        title: "Upload failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
      if (e.target) e.target.value = ''
    }
  }

  const removeUploadedImage = () => {
    setUploadedImage(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
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
                <Label>Upload Image</Label>
                {uploadedImage ? (
                  <div className="relative">
                    <img 
                      src={uploadedImage.url} 
                      alt="Uploaded" 
                      className="max-h-[200px] rounded-md object-contain w-full" 
                    />
                    <Button
                      variant="destructive"
                      size="icon"
                      className="absolute top-2 right-2 h-6 w-6"
                      onClick={removeUploadedImage}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-center justify-center border border-dashed rounded-md p-4">
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      id="image-upload"
                      ref={fileInputRef}
                      onChange={handleImageUpload}
                      disabled={isUploading}
                    />
                    <label htmlFor="image-upload" className="cursor-pointer">
                      <div className="flex flex-col items-center space-y-2">
                        {isUploading ? (
                          <Loader2 className="h-8 w-8 text-muted-foreground animate-spin" />
                        ) : (
                          <ImageIcon className="h-8 w-8 text-muted-foreground" />
                        )}
                        <div className="text-sm text-muted-foreground">
                          {isUploading ? "Uploading..." : "Drag & drop or click to upload"}
                        </div>
                      </div>
                    </label>
                  </div>
                )}
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
              <Button className="w-full" onClick={handleGenerate} disabled={isGenerating || isUploading}>
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
              <CardTitle>Tips for Great Captions</CardTitle>
              <CardDescription>Boost engagement with your posts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h3 className="font-medium">Tell a Story</h3>
                <p className="text-sm text-muted-foreground">
                  Connect with your audience by sharing personal experiences and stories
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium">Ask Questions</h3>
                <p className="text-sm text-muted-foreground">
                  Boost comments by asking your followers questions about their experiences
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-medium">Call to Action</h3>
                <p className="text-sm text-muted-foreground">
                  Include a clear CTA telling your audience what to do next
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

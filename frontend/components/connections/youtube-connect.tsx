"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Youtube, CheckCircle, Video, Users, Eye } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { SocialAccount } from "@/services/social-platforms-api"

interface YouTubeConnectProps {
  isConnected: boolean
  account?: SocialAccount
  onConnect: () => Promise<void>
  onDisconnect: (accountId: number) => Promise<void>
  isConnecting: boolean
}

export function YouTubeConnect({ 
  isConnected, 
  account, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: YouTubeConnectProps) {
  const { toast } = useToast()
  const [channelData, setChannelData] = useState<any>(null)
  const [recentVideos, setRecentVideos] = useState<any[]>([])

  // Extract YouTube-specific data if available
  useEffect(() => {
    if (account && account.metadata) {
      try {
        const metadata = typeof account.metadata === 'string' 
          ? JSON.parse(account.metadata) 
          : account.metadata

        if (metadata.channel) {
          setChannelData(metadata.channel)
        }
        
        if (metadata.recent_videos) {
          setRecentVideos(metadata.recent_videos.slice(0, 3)) // Only show top 3 videos
        }
      } catch (e) {
        console.error("Error parsing YouTube metadata:", e)
      }
    }
  }, [account])

  const formatNumber = (num: number | string | undefined): string => {
    if (!num) return "0"
    const numValue = typeof num === 'string' ? parseInt(num, 10) : num
    
    if (numValue >= 1000000) {
      return (numValue / 1000000).toFixed(1) + 'M'
    } else if (numValue >= 1000) {
      return (numValue / 1000).toFixed(1) + 'K'
    }
    return numValue.toString()
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-red-600 to-red-500 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Youtube className="h-5 w-5" />
            <CardTitle>YouTube</CardTitle>
          </div>
          {isConnected && (
            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
              <CheckCircle className="mr-1 h-3 w-3" />
              Connected
            </div>
          )}
        </div>
        <CardDescription className="text-red-100">
          Connect and manage your YouTube channel
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        {isConnected && account ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {channelData?.thumbnail ? (
                <img
                  src={channelData.thumbnail}
                  alt={channelData.title || account.account_name}
                  className="h-12 w-12 rounded-full object-cover"
                />
              ) : account.profile_picture_url ? (
                <img
                  src={account.profile_picture_url}
                  alt={account.account_name}
                  className="h-12 w-12 rounded-full object-cover"
                />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-200">
                  <Youtube className="h-6 w-6 text-gray-500" />
                </div>
              )}
              <div>
                <h3 className="font-medium">{channelData?.title || account.account_name}</h3>
                {channelData?.custom_url && (
                  <p className="text-sm text-gray-500">
                    {channelData.custom_url}
                  </p>
                )}
              </div>
            </div>

            {channelData && (
              <div className="grid grid-cols-3 gap-2 rounded-lg bg-gray-50 p-4">
                <div>
                  <p className="text-sm text-gray-500">Subscribers</p>
                  <p className="text-xl font-bold">{formatNumber(channelData.subscriber_count)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Videos</p>
                  <p className="text-xl font-bold">{formatNumber(channelData.video_count)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Views</p>
                  <p className="text-xl font-bold">{formatNumber(channelData.view_count)}</p>
                </div>
              </div>
            )}

            {recentVideos && recentVideos.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-500">Recent Videos</h4>
                <div className="space-y-2">
                  {recentVideos.map((video) => (
                    <div key={video.video_id} className="flex items-start gap-3 rounded-lg border border-gray-100 p-3">
                      {video.thumbnail ? (
                        <img 
                          src={video.thumbnail}
                          alt={video.title}
                          className="h-14 w-24 rounded object-cover"
                        />
                      ) : (
                        <div className="flex h-14 w-24 items-center justify-center rounded bg-gray-100">
                          <Video className="h-6 w-6 text-gray-400" />
                        </div>
                      )}
                      <div className="flex-1 overflow-hidden">
                        <h5 className="mb-1 truncate font-medium">{video.title}</h5>
                        <a 
                          href={`https://youtube.com/watch?v=${video.video_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline"
                        >
                          Watch on YouTube
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Youtube className="mb-2 h-12 w-12 text-gray-400" />
            <h3 className="mb-1 text-lg font-medium">Connect YouTube</h3>
            <p className="mb-4 text-sm text-gray-500">
              Manage your YouTube channel and content
            </p>
            <Button 
              onClick={onConnect} 
              className="bg-red-600 hover:bg-red-700 text-white"
              disabled={isConnecting}
            >
              {isConnecting ? "Connecting..." : "Connect YouTube"}
            </Button>
          </div>
        )}
      </CardContent>
      {isConnected && account && (
        <CardFooter className="bg-gray-50 px-6 py-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => onDisconnect(account.id)}
          >
            Disconnect YouTube
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

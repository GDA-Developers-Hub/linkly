"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Zap, AlertCircle, CheckCircle } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { SocialAccount } from "@/services/social-platforms-api"
import { socialPlatformsApi } from "@/services/social-platforms-api"

interface TikTokConnectProps {
  isConnected: boolean
  account?: SocialAccount
  onConnect: () => Promise<void>
  onDisconnect: (accountId: number) => Promise<void>
  isConnecting: boolean
}

export function TikTokConnect({ 
  isConnected, 
  account, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: TikTokConnectProps) {
  const { toast } = useToast()
  const [followerCount, setFollowerCount] = useState<number | null>(null)
  const [videoStats, setVideoStats] = useState<any>(null)

  // Extract TikTok-specific metrics if available
  useEffect(() => {
    if (account && account.metadata) {
      try {
        const metadata = typeof account.metadata === 'string' 
          ? JSON.parse(account.metadata) 
          : account.metadata

        if (metadata.follower_count) {
          setFollowerCount(metadata.follower_count)
        }
        
        if (metadata.video_stats) {
          setVideoStats(metadata.video_stats)
        }
      } catch (e) {
        console.error("Error parsing TikTok metadata:", e)
      }
    }
  }, [account])

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-black to-gray-800 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            <CardTitle>TikTok</CardTitle>
          </div>
          {isConnected && (
            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
              <CheckCircle className="mr-1 h-3 w-3" />
              Connected
            </div>
          )}
        </div>
        <CardDescription className="text-gray-300">
          Connect and manage your TikTok content
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        {isConnected && account ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {account.profile_picture_url ? (
                <img
                  src={account.profile_picture_url}
                  alt={account.account_name}
                  className="h-12 w-12 rounded-full object-cover"
                />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-200">
                  <Zap className="h-6 w-6 text-gray-500" />
                </div>
              )}
              <div>
                <h3 className="font-medium">{account.account_name}</h3>
                <p className="text-sm text-gray-500">@{account.account_id}</p>
              </div>
            </div>
            
            {followerCount !== null && (
              <div className="grid grid-cols-2 gap-4 rounded-lg bg-gray-50 p-4">
                <div>
                  <p className="text-sm text-gray-500">Followers</p>
                  <p className="text-xl font-bold">{formatNumber(followerCount)}</p>
                </div>
                
                {videoStats && (
                  <div>
                    <p className="text-sm text-gray-500">Videos</p>
                    <p className="text-xl font-bold">{videoStats.video_count || 0}</p>
                  </div>
                )}
                
                {videoStats && videoStats.total_likes > 0 && (
                  <div>
                    <p className="text-sm text-gray-500">Total Likes</p>
                    <p className="text-xl font-bold">{formatNumber(videoStats.total_likes)}</p>
                  </div>
                )}
                
                {videoStats && videoStats.total_comments > 0 && (
                  <div>
                    <p className="text-sm text-gray-500">Comments</p>
                    <p className="text-xl font-bold">{formatNumber(videoStats.total_comments)}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Zap className="mb-2 h-12 w-12 text-gray-400" />
            <h3 className="mb-1 text-lg font-medium">Connect TikTok</h3>
            <p className="mb-4 text-sm text-gray-500">
              Share your content and engage with your audience
            </p>
            <Button 
              onClick={onConnect} 
              className="bg-black hover:bg-gray-800 text-white"
              disabled={isConnecting}
            >
              {isConnecting ? "Connecting..." : "Connect TikTok"}
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
            Disconnect TikTok
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

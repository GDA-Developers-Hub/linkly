"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { AtSign, CheckCircle, MessageCircle, Clock } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { SocialAccount } from "@/services/social-platforms-api"

interface ThreadsConnectProps {
  isConnected: boolean
  account?: SocialAccount
  onConnect: () => Promise<void>
  onDisconnect: (accountId: number) => Promise<void>
  isConnecting: boolean
}

export function ThreadsConnect({ 
  isConnected, 
  account, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: ThreadsConnectProps) {
  const { toast } = useToast()
  const [profileData, setProfileData] = useState<any>(null)
  const [recentPosts, setRecentPosts] = useState<any[]>([])

  // Extract Threads-specific data if available
  useEffect(() => {
    if (account && account.metadata) {
      try {
        const metadata = typeof account.metadata === 'string' 
          ? JSON.parse(account.metadata) 
          : account.metadata

        if (metadata.profile) {
          setProfileData(metadata.profile)
        }
        
        if (metadata.recent_posts) {
          setRecentPosts(metadata.recent_posts.slice(0, 3)) // Only show top 3 posts
        }
      } catch (e) {
        console.error("Error parsing Threads metadata:", e)
      }
    }
  }, [account])

  // Format ISO date to a more readable format
  const formatDate = (isoDate: string): string => {
    if (!isoDate) return "";
    const date = new Date(isoDate);
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    }).format(date);
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-gray-900 to-gray-800 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AtSign className="h-5 w-5" />
            <CardTitle>Threads</CardTitle>
          </div>
          {isConnected && (
            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
              <CheckCircle className="mr-1 h-3 w-3" />
              Connected
            </div>
          )}
        </div>
        <CardDescription className="text-gray-300">
          Connect and manage your Threads account
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        {isConnected && account ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {profileData?.profile_picture_url ? (
                <img
                  src={profileData.profile_picture_url}
                  alt={profileData.username || account.account_name}
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
                  <AtSign className="h-6 w-6 text-gray-500" />
                </div>
              )}
              <div>
                <h3 className="font-medium">
                  {profileData?.username ? `@${profileData.username}` : account.account_name}
                </h3>
                {profileData?.account_type && (
                  <p className="text-sm text-gray-500">
                    {profileData.account_type} Account
                  </p>
                )}
              </div>
            </div>

            {profileData && (
              <div className="rounded-lg bg-gray-50 p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Media Count</p>
                    <p className="text-xl font-bold">{profileData.media_count || '0'}</p>
                  </div>
                  {profileData.follower_count && (
                    <div>
                      <p className="text-sm text-gray-500">Followers</p>
                      <p className="text-xl font-bold">{profileData.follower_count}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {recentPosts && recentPosts.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-500">Recent Threads</h4>
                <div className="space-y-2">
                  {recentPosts.map((post) => (
                    <div key={post.id} className="rounded-lg border border-gray-100 p-3">
                      <div className="mb-2 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <MessageCircle className="h-4 w-4 text-gray-400" />
                          <p className="text-xs text-gray-500">Thread</p>
                        </div>
                        {post.timestamp && (
                          <div className="flex items-center gap-1 text-xs text-gray-400">
                            <Clock className="h-3 w-3" />
                            {formatDate(post.timestamp)}
                          </div>
                        )}
                      </div>
                      {post.caption && (
                        <p className="text-sm line-clamp-2">{post.caption}</p>
                      )}
                      {post.thumbnail_url && (
                        <img 
                          src={post.thumbnail_url}
                          alt={post.caption || "Thread media"}
                          className="mt-2 rounded-md border border-gray-100"
                        />
                      )}
                      {post.permalink && (
                        <a
                          href={post.permalink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-2 inline-block text-xs text-blue-600 hover:underline"
                        >
                          View on Threads
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <AtSign className="mb-2 h-12 w-12 text-gray-400" />
            <h3 className="mb-1 text-lg font-medium">Connect Threads</h3>
            <p className="mb-4 text-sm text-gray-500">
              Share your thoughts and join the conversation
            </p>
            <Button 
              onClick={onConnect} 
              className="bg-black hover:bg-gray-800 text-white"
              disabled={isConnecting}
            >
              {isConnecting ? "Connecting..." : "Connect Threads"}
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
            Disconnect Threads
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { PinIcon, CheckCircle, Bookmark, Image, Users } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { SocialAccount } from "@/services/social-platforms-api"

interface PinterestConnectProps {
  isConnected: boolean
  account?: SocialAccount
  onConnect: () => Promise<void>
  onDisconnect: (accountId: number) => Promise<void>
  isConnecting: boolean
}

export function PinterestConnect({ 
  isConnected, 
  account, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: PinterestConnectProps) {
  const { toast } = useToast()
  const [profileData, setProfileData] = useState<any>(null)
  const [boards, setBoards] = useState<any[]>([])
  const [pins, setPins] = useState<any[]>([])

  // Extract Pinterest-specific data if available
  useEffect(() => {
    if (account && account.metadata) {
      try {
        const metadata = typeof account.metadata === 'string' 
          ? JSON.parse(account.metadata) 
          : account.metadata

        setProfileData({
          username: metadata.username,
          full_name: metadata.full_name,
          profile_image: metadata.profile_image,
          account_type: metadata.account_type
        })
        
        if (metadata.boards) {
          setBoards(metadata.boards.slice(0, 3)) // Only show top 3 boards
        }

        if (metadata.pins) {
          setPins(metadata.pins.slice(0, 2)) // Only show top 2 pins
        }
      } catch (e) {
        console.error("Error parsing Pinterest metadata:", e)
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
      <CardHeader className="bg-gradient-to-r from-red-700 to-red-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PinIcon className="h-5 w-5" />
            <CardTitle>Pinterest</CardTitle>
          </div>
          {isConnected && (
            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
              <CheckCircle className="mr-1 h-3 w-3" />
              Connected
            </div>
          )}
        </div>
        <CardDescription className="text-red-100">
          Share pins and manage your Pinterest boards
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        {isConnected && account ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {profileData?.profile_image ? (
                <img
                  src={profileData.profile_image}
                  alt={profileData.full_name || account.account_name}
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
                  <PinIcon className="h-6 w-6 text-gray-500" />
                </div>
              )}
              <div>
                <h3 className="font-medium">{profileData?.full_name || account.account_name}</h3>
                {profileData?.username && (
                  <p className="text-sm text-gray-500">
                    @{profileData.username}
                  </p>
                )}
              </div>
            </div>

            {boards && boards.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-500">Top Boards</h4>
                <div className="space-y-2">
                  {boards.map((board) => (
                    <div key={board.id} className="flex items-start gap-3 rounded-lg border border-gray-100 p-3">
                      <div className="flex h-12 w-12 items-center justify-center rounded bg-red-50">
                        <Bookmark className="h-6 w-6 text-red-600" />
                      </div>
                      <div className="flex-grow">
                        <h5 className="font-medium">{board.name}</h5>
                        <div className="mt-1 flex items-center gap-4 text-sm text-gray-500">
                          {board.pin_count !== undefined && (
                            <div className="flex items-center gap-1">
                              <Image className="h-4 w-4" />
                              <span>{formatNumber(board.pin_count)} pins</span>
                            </div>
                          )}
                          {board.follower_count !== undefined && (
                            <div className="flex items-center gap-1">
                              <Users className="h-4 w-4" />
                              <span>{formatNumber(board.follower_count)} followers</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {pins && pins.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-500">Recent Pins</h4>
                <div className="grid grid-cols-2 gap-2">
                  {pins.map((pin) => (
                    <div key={pin.id} className="overflow-hidden rounded-lg border border-gray-100">
                      {pin.media?.images?.orig?.url ? (
                        <img 
                          src={pin.media.images.orig.url} 
                          alt={pin.title || "Pinterest Pin"} 
                          className="aspect-square h-32 w-full object-cover"
                        />
                      ) : (
                        <div className="flex aspect-square h-32 w-full items-center justify-center bg-gray-100">
                          <PinIcon className="h-10 w-10 text-gray-300" />
                        </div>
                      )}
                      <div className="p-2">
                        <p className="line-clamp-1 text-sm font-medium">{pin.title || "Untitled Pin"}</p>
                        {pin.board?.name && (
                          <p className="line-clamp-1 text-xs text-gray-500">{pin.board.name}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <PinIcon className="mb-2 h-12 w-12 text-gray-400" />
            <h3 className="mb-1 text-lg font-medium">Connect Pinterest</h3>
            <p className="mb-4 text-sm text-gray-500">
              Share pins and manage your Pinterest boards
            </p>
            <Button 
              onClick={onConnect} 
              className="bg-red-700 hover:bg-red-800 text-white"
              disabled={isConnecting}
            >
              {isConnecting ? "Connecting..." : "Connect Pinterest"}
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
            Disconnect Pinterest
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

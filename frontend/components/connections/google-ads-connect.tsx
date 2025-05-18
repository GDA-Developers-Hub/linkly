"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, CheckCircle, BarChart, Globe, LayoutDashboard } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { SocialAccount } from "@/services/social-platforms-api"

interface GoogleAdsConnectProps {
  isConnected: boolean
  account?: SocialAccount
  onConnect: () => Promise<void>
  onDisconnect: (accountId: number) => Promise<void>
  isConnecting: boolean
}

export function GoogleAdsConnect({ 
  isConnected, 
  account, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: GoogleAdsConnectProps) {
  const { toast } = useToast()
  const [profileData, setProfileData] = useState<any>(null)
  const [adsAccounts, setAdsAccounts] = useState<any[]>([])
  const [analyticsProperties, setAnalyticsProperties] = useState<any[]>([])

  // Extract Google-specific data if available
  useEffect(() => {
    if (account && account.metadata) {
      try {
        const metadata = typeof account.metadata === 'string' 
          ? JSON.parse(account.metadata) 
          : account.metadata

        setProfileData({
          email: metadata.email,
          name: metadata.name,
          picture: metadata.picture
        })
        
        if (metadata.ads_accounts) {
          setAdsAccounts(metadata.ads_accounts)
        }

        if (metadata.analytics_properties) {
          setAnalyticsProperties(metadata.analytics_properties)
        }
      } catch (e) {
        console.error("Error parsing Google Ads metadata:", e)
      }
    }
  }, [account])

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-blue-500 to-green-500 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LineChart className="h-5 w-5" />
            <CardTitle>Google Ads</CardTitle>
          </div>
          {isConnected && (
            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
              <CheckCircle className="mr-1 h-3 w-3" />
              Connected
            </div>
          )}
        </div>
        <CardDescription className="text-blue-50">
          Manage your Google Ads campaigns and analytics
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        {isConnected && account ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {profileData?.picture ? (
                <img
                  src={profileData.picture}
                  alt={profileData.name || account.account_name}
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
                  <LineChart className="h-6 w-6 text-gray-500" />
                </div>
              )}
              <div>
                <h3 className="font-medium">{profileData?.name || account.account_name}</h3>
                {profileData?.email && (
                  <p className="text-sm text-gray-500">{profileData.email}</p>
                )}
              </div>
            </div>

            {adsAccounts && adsAccounts.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-500">
                  {adsAccounts.some(acc => acc.type === 'ads') ? 'Google Ads Accounts' : 'Google Analytics Accounts'}
                </h4>
                <div className="space-y-2">
                  {adsAccounts.map((account, index) => (
                    <div key={account.id || index} className="flex items-start gap-3 rounded-lg border border-gray-100 p-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded bg-blue-50">
                        {account.type === 'ads' ? (
                          <LineChart className="h-5 w-5 text-blue-600" />
                        ) : (
                          <BarChart className="h-5 w-5 text-blue-600" />
                        )}
                      </div>
                      <div className="flex-grow">
                        <h5 className="font-medium">{account.name}</h5>
                        <p className="text-xs text-gray-500">
                          {account.type === 'ads' ? 'Google Ads' : 'Google Analytics'} • ID: {account.id}
                        </p>
                        
                        {account.properties && account.properties.length > 0 && (
                          <div className="mt-2 space-y-1">
                            <p className="text-xs font-medium text-gray-600">Properties:</p>
                            {account.properties.slice(0, 2).map((property, idx) => (
                              <div key={idx} className="flex items-center gap-1 text-xs">
                                <Globe className="h-3 w-3 text-gray-400" />
                                <span>{property.name}</span>
                              </div>
                            ))}
                            {account.properties.length > 2 && (
                              <p className="text-xs text-gray-400">
                                +{account.properties.length - 2} more properties
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analyticsProperties && analyticsProperties.length > 0 && !adsAccounts.some(acc => acc.properties) && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-500">Analytics Properties</h4>
                <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                  {analyticsProperties.slice(0, 4).map((property, index) => (
                    <div key={property.id || index} className="flex items-center gap-2 rounded-lg border border-gray-100 p-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-green-50">
                        <Globe className="h-4 w-4 text-green-600" />
                      </div>
                      <div className="flex-grow overflow-hidden">
                        <p className="truncate text-sm font-medium">{property.name}</p>
                        {property.website && (
                          <p className="truncate text-xs text-gray-500">{property.website}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                {analyticsProperties.length > 4 && (
                  <p className="text-center text-xs text-gray-500">
                    +{analyticsProperties.length - 4} more properties
                  </p>
                )}
              </div>
            )}

            <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-3">
              <div className="flex items-start gap-2">
                <LayoutDashboard className="mt-0.5 h-4 w-4 text-blue-600" />
                <div>
                  <p className="text-sm font-medium text-blue-800">
                    Access your Google Ads dashboard
                  </p>
                  <p className="text-xs text-blue-600">
                    Manage campaigns, view reports, and analyze performance
                  </p>
                  <a
                    href="https://ads.google.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-block text-xs font-medium text-blue-700 hover:underline"
                  >
                    Open Google Ads Dashboard →
                  </a>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <LineChart className="mb-2 h-12 w-12 text-gray-400" />
            <h3 className="mb-1 text-lg font-medium">Connect Google Ads</h3>
            <p className="mb-4 text-sm text-gray-500">
              Manage your advertising campaigns and analytics
            </p>
            <Button 
              onClick={onConnect} 
              className="bg-blue-600 hover:bg-blue-700 text-white"
              disabled={isConnecting}
            >
              {isConnecting ? "Connecting..." : "Connect Google Ads"}
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
            Disconnect Google Ads
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

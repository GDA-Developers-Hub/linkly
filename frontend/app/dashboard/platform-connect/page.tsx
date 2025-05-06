"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import {
  AlertCircle, 
  RefreshCw, 
  Link2, 
  Facebook,
  Twitter, 
  Instagram,
  Linkedin,
  Youtube,
  Plus,
  CheckCircle,
  PinIcon,
  LineChart,
  Info,
  MessageCircle,
  Zap
} from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
// Import the types and API from our services module
import { SocialAccount } from "@/services/social-platforms-api" 
import { socialPlatformsApi } from "@/services/social-platforms-api"
import { useRouter } from "next/navigation"
import { getAPI } from "@/lib/api"
import { CircularNav } from "./CircularNav"

// Platform configurations with expanded icons and platforms
const availablePlatforms = [
  {
    id: "instagram",
    name: "Instagram",
    icon: Instagram,
    description: "Share photos and stories, manage your Instagram presence",
    color: "from-pink-500 via-purple-500 to-orange-500",
    popular: true
  },
  {
    id: "facebook",
    name: "Facebook",
    icon: Facebook,
    description: "Manage your Facebook pages and content",
    color: "from-blue-600 to-blue-500",
    popular: true
  },
  {
    id: "twitter",
    name: "Twitter/X",
    icon: Twitter, 
    description: "Schedule tweets and manage your Twitter presence",
    color: "from-blue-400 to-blue-300",
    popular: true
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    icon: Linkedin,
    description: "Share professional updates and manage company pages",
    color: "from-blue-700 to-blue-600",
    popular: false
  },
  {
    id: "youtube",
    name: "YouTube",
    icon: Youtube,
    description: "Manage your YouTube channel and content",
    color: "from-red-600 to-red-500",
    popular: true
  },
  {
    id: "pinterest",
    name: "Pinterest",
    icon: PinIcon,
    description: "Share pins and manage your Pinterest boards",
    color: "from-red-700 to-red-600",
    popular: false
  },
  {
    id: "google",
    name: "Google Ads",
    icon: LineChart,
    description: "Manage your Google Ads campaigns and analytics",
    color: "from-blue-500 to-green-500",
    popular: true
  },
  {
    id: "tiktok",
    name: "TikTok",
    icon: Zap,
    description: "Create and manage TikTok content and campaigns",
    color: "from-black to-gray-800",
    popular: true
  },
  {
    id: "threads",
    name: "Threads",
    icon: MessageCircle,
    description: "Share text-based updates and join conversations",
    color: "from-purple-600 to-purple-400",
    popular: false
  }
]

export default function PlatformConnectPage() {
  // Initialize as empty array to ensure proper typing
  const [connectedAccounts, setConnectedAccounts] = useState<SocialAccount[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isConnecting, setIsConnecting] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)
  const [selectedPlatformId, setSelectedPlatformId] = useState<string | null>(null)
  const { toast } = useToast()
  const router = useRouter()
  
  // Check authentication status on mount
  useEffect(() => {
    const api = getAPI();
    setIsAuthenticated(api.isAuthenticated());
    
    if (api.isAuthenticated()) {
      loadConnectedAccounts();
    }
  }, []);

  // Function to load connected accounts from API
  const loadConnectedAccounts = async () => {
    setIsLoading(true)
    try {
      const accounts = await socialPlatformsApi.getAccounts()
        setConnectedAccounts(accounts)
    } catch (err: any) {
      console.error('Error loading accounts:', err)
      
      // Handle various errors but don't immediately redirect
      toast({
        title: "Error",
        description: "Failed to load connected accounts",
        variant: "destructive",
      })
      
      // Ensure we have an empty array on error
      setConnectedAccounts([])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle platform selection from circular nav
  const handleSelectPlatform = (platform: { id: string }) => {
    setSelectedPlatformId(platform.id);
    
    // If on the available tab, scroll to the platform card
    setTimeout(() => {
      const platformCard = document.getElementById(`platform-card-${platform.id}`);
      if (platformCard) {
        platformCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  // Handle platform connection
  const handleConnectPlatform = async (platform: any) => {
    setIsConnecting(platform.id)
    try {
      // Get authorization URL and open popup window
      await socialPlatformsApi.initiateOAuth(platform.id)
      
      // Show toast to guide the user
      toast({
        title: "Authorization Started",
        description: `Please complete the authorization in the popup window.`,
      })
      
      // If user is authenticated, poll for new accounts
      if (isAuthenticated) {
        // Set up polling to check for newly connected accounts
        let attempts = 0
        const interval = setInterval(async () => {
          attempts++
          if (attempts > 30) { // Stop after 30 attempts (1 minute)
            clearInterval(interval)
      toast({
              title: "Connection Timeout",
              description: "Please try connecting again",
        variant: "destructive",
            })
            return
          }
          
          try {
            // Check for new accounts
            const updatedAccounts = await socialPlatformsApi.getAccounts()
            
            // Compare account counts
            const currentCount = connectedAccounts.length
            const newAccountsCount = updatedAccounts.length - currentCount
            
            if (newAccountsCount > 0) {
              clearInterval(interval)
              setConnectedAccounts(updatedAccounts)
              
        toast({
                title: "Account Connected",
                description: `Successfully connected ${platform.name}`,
              })
            }
          } catch (e) {
            console.error("Error checking for new accounts:", e)
          }
        }, 2000) // Poll every 2 seconds
      } else {
        // For unauthenticated users, just show a success message
        setTimeout(() => {
          toast({
            title: "Demo Mode",
            description: "In demo mode, connections are simulated. Login for full functionality.",
          })
        }, 5000);
      }
      
    } catch (err: any) {
      console.error('Error connecting platform:', err)
      
      toast({
        title: "Connection Failed",
        description: err.message || "Failed to connect platform. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsConnecting(null)
    }
  }

  // Handle account disconnection
  const handleDisconnectAccount = async (accountId: number) => {
    try {
      await socialPlatformsApi.disconnectAccount(accountId)
      
      // Update local state
      setConnectedAccounts(connectedAccounts.filter(account => account.id !== accountId))
      
      toast({
        title: "Account Disconnected",
        description: "Successfully disconnected account",
      })
    } catch (err) {
      console.error('Error disconnecting account:', err)
      toast({
        title: "Error",
        description: "Failed to disconnect account",
        variant: "destructive",
      })
    }
  }

  // Render a demo/unauthenticated view or the full authenticated view
  if (!isAuthenticated) {
      return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Platform Connect</h2>
            <p className="text-muted-foreground">Connect and manage your social media accounts</p>
          </div>
        </div>

        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Demo Mode</AlertTitle>
          <AlertDescription>
            You are in demo mode. Connections will open OAuth windows but won't fully connect without authentication.
            <div className="mt-4">
              <Button onClick={() => router.push('/login')} variant="outline" size="sm">
                Login for Full Access
              </Button>
            </div>
          </AlertDescription>
        </Alert>

        {/* Add the circular navigation component for demo mode too */}
        <CircularNav 
          platforms={availablePlatforms} 
          onSelectPlatform={handleSelectPlatform} 
          selectedPlatformId={selectedPlatformId}
        />

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {availablePlatforms.map((platform) => (
            <Card 
              key={platform.id} 
              id={`platform-card-${platform.id}`}
              className={`overflow-hidden transition-all duration-300 ${selectedPlatformId === platform.id ? 'ring-2 ring-accent shadow-lg' : ''}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center space-x-2">
                  <div className={`p-3 rounded-full shadow-lg bg-gradient-to-br ${platform.color}`}>
                    <platform.icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">{platform.name}</CardTitle>
                    {platform.popular && (
                      <Badge className="mt-1">Popular</Badge>
                    )}
            </div>
          </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {platform.description}
                </p>
              </CardContent>
              <CardFooter>
                <Button
                  className="w-full"
                  onClick={() => handleConnectPlatform(platform)}
                  disabled={isConnecting === platform.id}
                >
                  {isConnecting === platform.id ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Link2 className="mr-2 h-4 w-4" />
                      Connect {platform.name}
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
            </div>
    );
  }

  // The rest of your authenticated UI with tabs, etc.
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
          <div>
          <h2 className="text-3xl font-bold tracking-tight">Platform Connect</h2>
          <p className="text-muted-foreground">Connect and manage your social media accounts</p>
          </div>
        <Button onClick={loadConnectedAccounts} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
        </div>

      {/* Add the circular navigation component */}
      <CircularNav 
        platforms={availablePlatforms} 
        onSelectPlatform={handleSelectPlatform} 
        selectedPlatformId={selectedPlatformId}
      />

      {connectedAccounts.length === 0 && (
        <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Configuration Required</AlertTitle>
            <AlertDescription>
            Please connect at least one social media account.
            </AlertDescription>
          </Alert>
        )}

      <Tabs defaultValue={connectedAccounts.length > 0 ? "connected" : "available"} className="space-y-4">
        <TabsList>
          <TabsTrigger value="connected">Connected Platforms</TabsTrigger>
          <TabsTrigger value="available">Available Platforms</TabsTrigger>
          </TabsList>

        <TabsContent value="connected">
          {isLoading ? (
            <Card>
              <CardHeader>
                <CardTitle>Loading accounts...</CardTitle>
                    </CardHeader>
              <CardContent className="flex justify-center py-6">
                <RefreshCw className="h-8 w-8 animate-spin" />
                    </CardContent>
                  </Card>
            ) : connectedAccounts.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {connectedAccounts.map((account) => (
                <Card key={account.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                            <div>
                          <CardTitle className="text-base">{account.account_name}</CardTitle>
                          <CardDescription>{account.platform.display_name}</CardDescription>
                        </div>
                      </div>
                      <Badge variant={account.status === 'active' ? 'default' : 'secondary'}>
                        {account.status}
                          </Badge>
                        </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Connected on: {new Date(account.created_at).toLocaleDateString()}
                    </p>
                      </CardContent>
                  <CardFooter className="flex justify-end">
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDisconnectAccount(account.id)}
                    >
                      Disconnect
                    </Button>
                  </CardFooter>
                    </Card>
              ))}
              </div>
            ) : (
            <Card>
              <CardHeader>
                <CardTitle>No Connected Accounts</CardTitle>
                <CardDescription>
                  You haven't connected any social media accounts yet.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <Button onClick={() => {
                  const availableTab = document.querySelector('[value="available"]') as HTMLElement;
                  if (availableTab) availableTab.click();
                }}>
                    <Plus className="mr-2 h-4 w-4" />
                    Connect Platform
                  </Button>
              </CardContent>
            </Card>
            )}
          </TabsContent>

        <TabsContent value="available">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {availablePlatforms.map((platform) => {
                // Add safety check for array before using .some()
                const isConnected = Array.isArray(connectedAccounts) && connectedAccounts.some(
                  account => account?.platform?.name?.toLowerCase() === platform.id.toLowerCase() && account.status === 'active'
                );
                
                return (
                <Card 
                  key={platform.id} 
                  id={`platform-card-${platform.id}`}
                  className={`overflow-hidden transition-all duration-300 ${selectedPlatformId === platform.id ? 'ring-2 ring-accent shadow-lg' : ''}`}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-center space-x-2">
                      <div className={`p-3 rounded-full shadow-lg bg-gradient-to-br ${platform.color}`}>
                        <platform.icon className="h-5 w-5 text-white" />
                          </div>
                          <div>
                        <CardTitle className="text-xl">{platform.name}</CardTitle>
                        {platform.popular && (
                          <Badge className="mt-1">Popular</Badge>
                        )}
                        </div>
                      </div>
                    </CardHeader>
                  <CardContent>
                      <p className="text-sm text-muted-foreground">
                      {platform.description}
                      </p>
                    </CardContent>
                    <CardFooter>
                      <Button
                      className="w-full"
                      onClick={() => handleConnectPlatform(platform)}
                      disabled={isConnecting === platform.id}
                        variant={isConnected ? "outline" : "default"}
                      >
                      {isConnecting === platform.id ? (
                          <>
                            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                            Connecting...
                          </>
                        ) : isConnected ? (
                          <>
                          <CheckCircle className="mr-2 h-4 w-4" />
                            Connected
                          </>
                        ) : (
                          <>
                            <Link2 className="mr-2 h-4 w-4" />
                          Connect {platform.name}
                          </>
                        )}
                      </Button>
                    </CardFooter>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
        </Tabs>
    </div>
  )
}
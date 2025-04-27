"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import {
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
  Youtube,
  TwitterIcon as TikTok,
  PinIcon as Pinterest,
  Link2,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Plus,
  Settings,
  Trash2,
  ExternalLink,
  Info,
} from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Separator } from "@/components/ui/separator"
import { ModeToggle } from "@/components/mode-toggle"
import { getSocialBuAPI, withErrorHandling, type Account } from "@/lib/socialbu-api"
import { useToast } from "@/components/ui/use-toast"

// Map platform names to icons and colors
const platformConfig: Record<string, { icon: any; color: string }> = {
  facebook: { icon: Facebook, color: "#1877F2" },
  instagram: { icon: Instagram, color: "#E1306C" },
  twitter: { icon: Twitter, color: "#1DA1F2" },
  linkedin: { icon: Linkedin, color: "#0A66C2" },
  youtube: { icon: Youtube, color: "#FF0000" },
  tiktok: { icon: TikTok, color: "#000000" },
  pinterest: { icon: Pinterest, color: "#E60023" },
}

export default function PlatformConnectPage() {
  const [activeTab, setActiveTab] = useState("connected")
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [connectedAccounts, setConnectedAccounts] = useState<Account[]>([])
  const [hasError, setHasError] = useState(false)
  const { toast } = useToast()

  // Fetch connected accounts
  const fetchAccounts = async () => {
    setIsRefreshing(true)
    try {
      await withErrorHandling(async () => {
        const api = getSocialBuAPI()
        const accounts = await api.getAccounts()
        setConnectedAccounts(accounts)
        setHasError(accounts.some((account) => account.status === "token_expired" || account.status === "error"))
      }, "Failed to fetch connected accounts")
    } catch (error) {
      console.error("Error fetching accounts:", error)
    } finally {
      setIsRefreshing(false)
    }
  }

  // Disconnect an account
  const disconnectAccount = async (accountId: number) => {
    try {
      await withErrorHandling(async () => {
        const api = getSocialBuAPI()
        await api.disconnectAccount(accountId)
        toast({
          title: "Account disconnected",
          description: "The account has been successfully disconnected.",
        })
        // Refresh accounts list
        fetchAccounts()
      }, "Failed to disconnect account")
    } catch (error) {
      console.error("Error disconnecting account:", error)
    }
  }

  // Fetch accounts on component mount
  useEffect(() => {
    fetchAccounts()
  }, [])

  const availablePlatforms = [
    {
      name: "TikTok",
      platform: "tiktok",
      description: "Share short-form videos to your TikTok account",
      popular: true,
    },
    {
      name: "YouTube",
      platform: "youtube",
      description: "Manage your YouTube channel and video content",
      popular: true,
    },
    {
      name: "Pinterest",
      platform: "pinterest",
      description: "Share pins and manage your Pinterest boards",
      popular: false,
    },
  ]

  // Function to initiate OAuth flow for connecting a new account
  const connectAccount = async (platform: string) => {
    try {
      toast({
        title: "Connecting account",
        description: `Initiating connection to ${platform}...`,
      })

      const api = getSocialBuAPI()

      // Open popup for OAuth flow
      const result = await api.openConnectionPopup(platform)

      toast({
        title: "Account connected",
        description: `Successfully connected to ${result.accountName}`,
      })

      // Refresh accounts list
      fetchAccounts()
    } catch (error) {
      console.error("Error connecting account:", error)
      toast({
        title: "Connection failed",
        description: error instanceof Error ? error.message : "Failed to connect account",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Platform Connect</h2>
          <p className="text-muted-foreground">Connect and manage your social media accounts</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchAccounts} disabled={isRefreshing}>
            {isRefreshing ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Refresh Connections
          </Button>
          <ModeToggle />
        </div>
      </div>

      {hasError && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Connection Status</AlertTitle>
          <AlertDescription>
            One or more of your connected accounts requires attention. Check the status below.
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="connected" value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="connected">Connected Platforms</TabsTrigger>
          <TabsTrigger value="available">Available Platforms</TabsTrigger>
        </TabsList>
        <TabsContent value="connected" className="space-y-4">
          {isRefreshing && connectedAccounts.length === 0 ? (
            <div className="flex justify-center p-8">
              <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : connectedAccounts.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                <Link2 className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No Connected Platforms</h3>
                <p className="text-muted-foreground mt-2">
                  You haven't connected any social media platforms yet. Go to the "Available Platforms" tab to get
                  started.
                </p>
                <Button className="mt-4" onClick={() => setActiveTab("available")}>
                  Connect a Platform
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {connectedAccounts.map((account) => {
                const platform = platformConfig[account.platform] || { icon: Link2, color: "#666" }
                const PlatformIcon = platform.icon

                return (
                  <Card key={account.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="flex h-8 w-8 items-center justify-center rounded-full"
                            style={{ backgroundColor: platform.color }}
                          >
                            <PlatformIcon className="h-4 w-4 text-white" />
                          </div>
                          <div>
                            <CardTitle className="text-base">{account.name}</CardTitle>
                            <CardDescription>{account.platform}</CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {account.status !== "token_expired" && account.status !== "error" ? (
                            <Badge variant="outline" className="bg-green-50 text-green-700 dark:bg-green-900/20">
                              <CheckCircle2 className="mr-1 h-3 w-3" />
                              Connected
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="bg-amber-50 text-amber-700 dark:bg-amber-900/20">
                              <AlertCircle className="mr-1 h-3 w-3" />
                              Needs Attention
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pb-2">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Account Type:</span> {account.type || "Standard"}
                        </div>
                        <div>
                          <span className="text-muted-foreground">Connected:</span>{" "}
                          {account.connected_at ? new Date(account.connected_at).toLocaleDateString() : "Recently"}
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter className="flex justify-between pt-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="outline" size="sm">
                            <Settings className="mr-2 h-3.5 w-3.5" />
                            Manage
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Manage {account.name} Connection</DialogTitle>
                            <DialogDescription>Configure your connection settings and permissions</DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 py-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <div
                                  className="flex h-8 w-8 items-center justify-center rounded-full"
                                  style={{ backgroundColor: platform.color }}
                                >
                                  <PlatformIcon className="h-4 w-4 text-white" />
                                </div>
                                <div>
                                  <div className="font-medium">{account.name}</div>
                                  <div className="text-sm text-muted-foreground">
                                    {account.type || "Standard Account"}
                                  </div>
                                </div>
                              </div>
                              {account.status !== "token_expired" && account.status !== "error" ? (
                                <Badge variant="outline" className="bg-green-50 text-green-700 dark:bg-green-900/20">
                                  <CheckCircle2 className="mr-1 h-3 w-3" />
                                  Connected
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="bg-amber-50 text-amber-700 dark:bg-amber-900/20">
                                  <AlertCircle className="mr-1 h-3 w-3" />
                                  Needs Attention
                                </Badge>
                              )}
                            </div>

                            <Separator />

                            <div className="space-y-2">
                              <h4 className="font-medium">Permissions</h4>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <Label htmlFor={`post-permission-${account.id}`} className="flex items-center gap-2">
                                    <span>Post Content</span>
                                    <Info className="h-3.5 w-3.5 text-muted-foreground" />
                                  </Label>
                                  <Switch id={`post-permission-${account.id}`} defaultChecked />
                                </div>
                                <div className="flex items-center justify-between">
                                  <Label htmlFor={`read-permission-${account.id}`} className="flex items-center gap-2">
                                    <span>Read Content</span>
                                    <Info className="h-3.5 w-3.5 text-muted-foreground" />
                                  </Label>
                                  <Switch id={`read-permission-${account.id}`} defaultChecked />
                                </div>
                                <div className="flex items-center justify-between">
                                  <Label
                                    htmlFor={`insights-permission-${account.id}`}
                                    className="flex items-center gap-2"
                                  >
                                    <span>Access Insights</span>
                                    <Info className="h-3.5 w-3.5 text-muted-foreground" />
                                  </Label>
                                  <Switch id={`insights-permission-${account.id}`} defaultChecked />
                                </div>
                              </div>
                            </div>

                            <Separator />

                            <div className="space-y-2">
                              <h4 className="font-medium">Account Settings</h4>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <Label htmlFor={`auto-sync-${account.id}`} className="flex items-center gap-2">
                                    <span>Auto-sync content</span>
                                  </Label>
                                  <Switch id={`auto-sync-${account.id}`} defaultChecked />
                                </div>
                                <div className="flex items-center justify-between">
                                  <Label htmlFor={`notifications-${account.id}`} className="flex items-center gap-2">
                                    <span>Receive notifications</span>
                                  </Label>
                                  <Switch id={`notifications-${account.id}`} defaultChecked />
                                </div>
                              </div>
                            </div>
                          </div>
                          <DialogFooter className="flex items-center justify-between">
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => {
                                disconnectAccount(account.id)
                                document
                                  .querySelector('[data-state="open"] button[aria-label="Close"]')
                                  ?.dispatchEvent(new MouseEvent("click", { bubbles: true }))
                              }}
                            >
                              <Trash2 className="mr-2 h-3.5 w-3.5" />
                              Disconnect
                            </Button>
                            <div className="flex gap-2">
                              <Button variant="outline">Cancel</Button>
                              <Button>Save Changes</Button>
                            </div>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <Settings className="h-3.5 w-3.5" />
                            <span className="sr-only">More options</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Options</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem>
                            <RefreshCw className="mr-2 h-3.5 w-3.5" />
                            Refresh Token
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <ExternalLink className="mr-2 h-3.5 w-3.5" />
                            View Profile
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive" onClick={() => disconnectAccount(account.id)}>
                            <Trash2 className="mr-2 h-3.5 w-3.5" />
                            Disconnect
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </CardFooter>
                  </Card>
                )
              })}
            </div>
          )}
        </TabsContent>
        <TabsContent value="available" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            {availablePlatforms.map((platform) => {
              const platformInfo = platformConfig[platform.platform] || { icon: Link2, color: "#666" }
              const PlatformIcon = platformInfo.icon

              return (
                <Card key={platform.name} className="overflow-hidden">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className="flex h-8 w-8 items-center justify-center rounded-full"
                          style={{ backgroundColor: platformInfo.color }}
                        >
                          <PlatformIcon className="h-4 w-4 text-white" />
                        </div>
                        <CardTitle className="text-base">{platform.name}</CardTitle>
                      </div>
                      {platform.popular && (
                        <Badge variant="secondary" className="bg-primary/10 text-primary">
                          Popular
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <p className="text-sm text-muted-foreground">{platform.description}</p>
                  </CardContent>
                  <CardFooter className="pt-2">
                    <Button className="w-full" onClick={() => connectAccount(platform.platform)}>
                      <Plus className="mr-2 h-3.5 w-3.5" />
                      Connect
                    </Button>
                  </CardFooter>
                </Card>
              )
            })}

            <Card className="overflow-hidden border-dashed">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                    <Link2 className="h-4 w-4" />
                  </div>
                  <CardTitle className="text-base">Request Platform</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="pb-2">
                <p className="text-sm text-muted-foreground">
                  Don't see the platform you need? Request a new integration.
                </p>
              </CardContent>
              <CardFooter className="pt-2">
                <Button variant="outline" className="w-full">
                  Request Platform
                </Button>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Connection Settings</CardTitle>
          <CardDescription>Manage global settings for all connected platforms</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="auto-refresh">Auto-refresh tokens</Label>
                <p className="text-sm text-muted-foreground">
                  Automatically refresh connection tokens before they expire
                </p>
              </div>
              <Switch id="auto-refresh" defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="sync-profiles">Sync profile changes</Label>
                <p className="text-sm text-muted-foreground">Keep your profile information in sync across platforms</p>
              </div>
              <Switch id="sync-profiles" />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="connection-notifications">Connection notifications</Label>
                <p className="text-sm text-muted-foreground">Receive notifications about connection status changes</p>
              </div>
              <Switch id="connection-notifications" defaultChecked />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

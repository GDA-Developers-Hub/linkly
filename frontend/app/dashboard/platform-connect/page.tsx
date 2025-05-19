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
import { SocialAccount, socialPlatformsApi } from "@/services/social-platforms-api"
import { useRouter } from "next/navigation"
import { getAPI } from "@/lib/api"
import { CircularNav } from "./CircularNav"
// Import auth constants and utilities
import { AUTH } from "@/lib/constants"
import { AuthAPI} from "@/lib/socials-api"

import { initializeOAuth } from "@/lib/oauth-adapter"
// Import auth hook from dedicated hooks directory
import { useSocialAuth } from "@/hooks/use-social-auth"
// Import our custom connection components
import { 
  TikTokConnect, 
  LinkedInConnect, 
  YouTubeConnect, 
  ThreadsConnect,
  PinterestConnect,
  GoogleAdsConnect
} from "@/components/connections"

// Platform configurations with expanded icons and platforms
interface Platform {
  id: string;
  name: string;
  icon: any;
  description: string;
  color: string;
  popular: boolean;
}

const availablePlatforms: Platform[] = [
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

const auth = new AuthAPI()


// Helper function to get platform gradient color
function getPlatformColor(platformName: string): string {
  const platform = availablePlatforms.find(
    p => p.id.toLowerCase() === platformName.toLowerCase()
  )
  return platform?.color || 'from-gray-600 to-gray-500'
}

export default function PlatformConnectPage() {
  // Initialize as empty array to ensure proper typing
  const [connectedAccounts, setConnectedAccounts] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isConnecting, setIsConnecting] = useState<string | boolean>(false);
  const [selectedPlatformId, setSelectedPlatformId] = useState<string>("");
  const [showConnected, setShowConnected] = useState<boolean>(false);
  
  // Auth state
  const { isAuthenticated } = useSocialAuth();
  
  // Toast notifications
  const { toast } = useToast();

  const router = useRouter()
  
  // Check authentication status on mount
  useEffect(() => {
    // Auth state is now handled by the useSocialAuth hook
    // No need to manually set the authentication state
    
    if (isAuthenticated) {
      loadConnectedAccounts();
    }
  }, [isAuthenticated]);

  // Function to load connected accounts is defined below

  useEffect(() => {
    // Load connected accounts on component mount
    loadConnectedAccounts();
    
    // Import our OAuth adapter utilities
    try {
      // Use Promise.all to wait for both imports to complete
      Promise.all([
        import('@/lib/oauth-adapter'),
        import('@/lib/auth-utils')
      ]).catch(e => console.error('Error importing OAuth utilities:', e));
    } catch (e) {
      console.error('Error setting up OAuth utilities:', e);
    }
    
    // Listen for messages from popup windows (OAuth callbacks)
    const handleMessage = (event: MessageEvent) => {
      try {
        // Parse the message data
        const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        
        // Skip messages that don't have our expected format
        if (!data || typeof data !== 'object') {
          return;
        }
        
        // Debug log to help diagnose OAuth callbacks
        console.log('Received OAuth callback message:', JSON.stringify(data, null, 2));
        
        // Check if this is our auth_required message
        if (data.auth_required === true) {
          // Normalize the platform name if present
          let platformName = data.platform || data.platform_id || "";
          
          // Special handling for platforms that use Redis-based auth with AllAuth
          if (data.code_id) {
            // Store the code_id in localStorage for later completion
            const codeId = data.code_id;
            const platform = platformName.toLowerCase();
            
            console.log(`Storing ${platform} OAuth code_id in localStorage:`, codeId ? codeId.substring(0, 8) + '...' : 'None');
            localStorage.setItem(`pending_oauth_${platform}`, codeId);
            
            // Show notification to user
            toast({
              title: "Authentication Required",
              description: `Please log in to complete your ${platformName} connection.`,
              duration: 5000,
            });
            
            // Update UI for the specific platform component if needed
            if (platform === 'linkedin') {
              // Update any LinkedIn-specific state
              const components = document.querySelectorAll('[data-platform="linkedin"]');
              components.forEach(component => {
                component.setAttribute('data-auth-required', 'true');
              });
            }
            
            return;
          }
          
          // Backward compatibility for platforms that use the original OAuth flow
          // Special handling for LinkedIn and YouTube - these might still use both approaches
          if (platformName.toLowerCase().includes('linkedin') || platformName.toLowerCase().includes('youtube')) {
            // Normalize platform name
            platformName = platformName.toLowerCase().includes('linkedin') ? 'linkedin' : 'youtube';
            console.log(`${platformName.charAt(0).toUpperCase() + platformName.slice(1)} OAuth callback received`);
            
            // Check for code_id from Redis storage
            const codeId = data.code_id;
            console.log(`Redis code_id received:`, codeId ? codeId.substring(0, 8) + '...' : 'None');
            
            // Log extra data for debugging
            if (data.code) {
              console.log(`${platformName} partial code received:`, data.code);
            }
            
            // For LinkedIn and YouTube, initiate polling for account changes
            // This works around potential auth issues by checking if the account was connected
            let attempts = 0;
            const pollingInterval = setInterval(async () => {
              attempts++;
              console.log(`${platformName} polling attempt ${attempts}...`);
              if (attempts > 10) { // Stop after 10 attempts
                clearInterval(pollingInterval);
                return;
              }
              
              try {
                const accounts = await socialPlatformsApi.getAccounts();
                const platformAccounts = Array.isArray(accounts) 
                  ? accounts.filter(acc => acc.platform.name.toLowerCase() === platformName.toLowerCase()) 
                  : [];
                  
                if (platformAccounts.length > 0) {
                  clearInterval(pollingInterval);
                  console.log(`${platformName} account found:`, platformAccounts[0]);
                  setConnectedAccounts(accounts);
                  
                  toast({
                    title: `${platformName.charAt(0).toUpperCase() + platformName.slice(1)} Connected`,
                    description: `Your ${platformName} account has been connected successfully!`,
                    variant: "default",
                    duration: 5000,
                  });
                }
              } catch (e) {
                console.error(`Error polling for ${platformName} account:`, e);
              }
            }, 2000); // Poll every 2 seconds
          }
          
          // For legacy OAuth flows that don't use Redis
          if (!data.code_id) {
            const legacyPlatform = data.platform || "social";
            
            // Show notification to user
            toast({
              title: "Authentication Required",
              description: `Completing connection for your ${legacyPlatform} account...`,
              variant: "default",
              duration: 5000,
            });
            
            // Delay the completion slightly to ensure the session is available
            setTimeout(() => {
              // Complete the OAuth flow with the stored code and normalized platform name
              if (legacyPlatform) {
                console.log(`Starting OAuth completion for: ${legacyPlatform}`);
                completeOAuthConnection(legacyPlatform);
              } else {
                console.error('Platform name not provided in auth_required message');
              }
            }, 1000); // 1 second delay to ensure session is available
          }
        } 
        // Special handling for LinkedIn which comes back from the OAuth callback
        else if (data.platform && data.platform.toLowerCase() === 'linkedin') {
          // Handle LinkedIn OAuth flow
          console.log('LinkedIn OAuth callback received:', data)
          
          // Check if auth is required
          if (data.auth_required) {
            console.log('Authentication required for LinkedIn')
            
            // If we also received a code_id, store it for later completion
            if (data.code_id) {
              console.log('Storing LinkedIn code_id for later completion:', data.code_id)
              localStorage.setItem(`pending_oauth_linkedin`, data.code_id)
            }
            
            completeOAuthConnection('linkedin')
          }
          
          // Direct handling of code_id - this is our primary case that needs fixing
          if (data.code_id) {
            console.log('LinkedIn code_id received, completing connection:', data.code_id)
            
            // Complete the OAuth flow using the code_id from Redis
            try {
              toast({
                title: "Completing LinkedIn Connection",
                description: "Finalizing your LinkedIn account connection...",
              })
              
              // Store the code_id for completion after auth if needed
              localStorage.setItem(`pending_oauth_linkedin`, data.code_id)
              
              // If user is already authenticated, complete the connection now
              if (isAuthenticated) {
                console.log('User authenticated, immediately completing LinkedIn connection')
                // Use a slight delay to ensure UI updates first
                setTimeout(() => {
                  completeLinkedInConnection(data.code_id)
                }, 500)
              } else {
                console.log('User not authenticated, LinkedIn connection will complete after login')
                toast({
                  title: "Authentication Required",
                  description: "Please log in to complete your LinkedIn connection.",
                })
              }
            } catch (error) {
              console.error('Error processing LinkedIn connection:', error)
              toast({
                title: "Connection Error",
                description: "There was a problem connecting your LinkedIn account. Please try again.",
                variant: "destructive",
              })
            }
          }
        } 
        // Special handling for YouTube which comes back from the OAuth callback
        else if (data.platform && data.platform.toLowerCase().includes('youtube')) {
          const platformName = 'youtube';
          console.log('YouTube OAuth callback received');
          
          // Log extra data for debugging
          if (data.code) {
            console.log('YouTube partial code received:', data.code);
          }
          
          // For YouTube, initiate polling for account changes right away
          // This works around potential auth issues by checking if the account was connected
          let attempts = 0;
          const pollingInterval = setInterval(async () => {
            attempts++;
            console.log(`YouTube polling attempt ${attempts}...`);
            if (attempts > 10) { // Stop after 10 attempts
              clearInterval(pollingInterval);
              return;
            }
            
            try {
              const accounts = await socialPlatformsApi.getAccounts();
              const youtubeAccounts = Array.isArray(accounts) 
                ? accounts.filter(acc => acc.platform.name.toLowerCase() === 'youtube') 
                : [];
                
              if (youtubeAccounts.length > 0) {
                clearInterval(pollingInterval);
                console.log('YouTube account found:', youtubeAccounts[0]);
                setConnectedAccounts(accounts);
                
                toast({
                  title: "YouTube Connected",
                  description: `Your YouTube account has been connected successfully!`,
                  variant: "default",
                  duration: 5000,
                });
              }
            } catch (e) {
              console.error('Error polling for YouTube account:', e);
            }
          }, 2000); // Poll every 2 seconds
        } 
        // Handle successful connection
        else if (data.success === true && data.account) {
          toast({
            title: "Connection Successful",
            description: `Your ${data.platform || "social"} account has been connected!`,
            variant: "default",
            duration: 5000,
          });
          
          // Refresh account list
          loadConnectedAccounts();
        }
      } catch (error) {
        console.error('Error handling OAuth callback message:', error);
      }
    };

    window.addEventListener("message", handleMessage);
    
    // Clean up event listener on unmount
    return () => {
      window.removeEventListener("message", handleMessage);
    };
  }, []);

  // Function to complete LinkedIn connection with code_id
  const completeLinkedInConnection = async (code_id: string) => {
    try {
      console.log('Completing LinkedIn connection with code_id:', code_id.substring(0, 8) + '...');
      
      // Use the special AllAuth completeOAuth with the code_id
      const result = await socialPlatformsApi.completeOAuthAllAuth('linkedin', code_id);
      
      if (result?.success && result?.account) {
        console.log('LinkedIn connection successful:', result.account);
        toast({
          title: "LinkedIn Connected",
          description: `Your LinkedIn account ${result.account.account_name} has been connected successfully!`,
          variant: "default",
          duration: 5000,
        });
        
        // Refresh account list
        await loadConnectedAccounts();
        
        // Remove the pending token
        localStorage.removeItem(`pending_oauth_linkedin`);
      } else {
        throw new Error(result?.error || 'Unknown error completing LinkedIn connection');
      }
    } catch (error) {
      console.error('Error completing LinkedIn connection:', error);
      toast({
        title: "LinkedIn Connection Failed",
        description: "There was a problem completing your LinkedIn connection. Please try again.",
        variant: "destructive",
      });
    }
  };
  
  // Function to complete OAuth connection after auth_required flag
  const completeOAuthConnection = async (platform: string) => {
    try {
      // Prepare data to send to the backend
      let extraData: Record<string, any> = {}
      
      // Special handling for LinkedIn
      if (platform.toLowerCase() === 'linkedin') {
        console.log('Completing LinkedIn OAuth connection...')
        
        // Get stored state and any other LinkedIn-specific data
        const storedState = localStorage.getItem('linkedin_oauth_state')
        if (storedState) {
          extraData.state = storedState
          console.log('Using stored LinkedIn state for completion:', storedState)
        }
        
        // Check for LinkedIn pending cookie
        if (document.cookie.includes('linkedin_oauth_pending=true')) {
          extraData.fromCookie = true
          console.log('Including cookie information in request')
          
          // Clear the pending cookie once we've used it
          document.cookie = 'linkedin_oauth_pending=; Max-Age=0; path=/; secure;'
        }
      }
      
      // Add timestamp to prevent caching issues
      extraData.timestamp = Date.now()
      
      // Log request details
      console.log(`Sending completeOAuth request for ${platform}:`, extraData)
      
      // Call the complete OAuth endpoint with the platform name and any extra data
      const response = await socialPlatformsApi.completeOAuth(platform, extraData)
      
      console.log(`OAuth completion response for ${platform}:`, response)
      
      if (response && response.success) {
        // Refresh account list
        loadConnectedAccounts()
        
        toast({
          title: "Connection Successful",
          description: `Your ${platform} account has been connected!`,
          variant: "default",
          duration: 5000,
        })
      } else {
        // Handle error
        throw new Error(response?.error || 'Failed to complete connection')
      }
    } catch (err: any) {
      console.error('Error completing OAuth connection:', err)
      
      toast({
        title: "Connection Failed",
        description: err.message || "Failed to complete the connection process.",
        variant: "destructive",
        duration: 5000,
      })
    }
  }
  
  // Function to load connected accounts from API
  const loadConnectedAccounts = async () => {
    setIsLoading(true)
    try {
      const accounts = await socialPlatformsApi.getAccounts()
      // Ensure accounts is always an array
      setConnectedAccounts(Array.isArray(accounts) ? accounts : [])
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
      // Get current auth token if user is authenticated
      const authToken = localStorage.getItem(AUTH.TOKEN_KEY);
      
      // Get authorization URL and open popup window
      const response = await socialPlatformsApi.initiateOAuth(platform.id);
      console.log('OAuth response:', response);
      
      if (!response || !response.authorization_url) {
        throw new Error('No authorization URL received');
      }
      
      // Enhanced state handling for LinkedIn and similar platforms with state inconsistencies
      if (['linkedin', 'youtube'].includes(platform.id.toLowerCase()) && response.authorization_url) {
        // Extract state from authorization URL
        const stateMatch = response.authorization_url.match(/state=([^&]*)/); 
        if (stateMatch && stateMatch[1]) {
          const state = decodeURIComponent(stateMatch[1]);
          // Store in localStorage for use during callback
          localStorage.setItem(`${platform.id.toLowerCase()}_oauth_state`, state);
          // Also add state to URL to ensure it's passed back properly
          console.log(`Enhanced state handling for ${platform.id}: ${state}`);
          
          // Track in memory to check during polling
          // Use safely as a property on the window
          (window as any).pendingOauthState = state;
        }
      }
      
      // Enhance the authorization URL with auth token if available
      let enhancedAuthUrl = response.authorization_url;
      if (isAuthenticated && authToken) {
        // Pass the auth token as a query parameter 
        const separator = enhancedAuthUrl.includes('?') ? '&' : '?';
        enhancedAuthUrl = `${enhancedAuthUrl}${separator}auth_token=${encodeURIComponent(authToken)}`;
        console.log(`Adding auth token to ${platform.id} OAuth URL`);
      }
      
      // Open the authorization URL in a new window
      const authWindow = window.open(
        enhancedAuthUrl,
        `Connect ${platform.name}`,
        `width=600,height=700,left=${window.innerWidth/2 - 300},top=${window.innerHeight/2 - 350},resizable=yes,scrollbars=yes`
      );
      
      if (!authWindow) {
        // If popup was blocked
        toast({
          title: "Popup Blocked",
          description: `Please allow popups for this site and try again.`,
          variant: "destructive",
        });
        setIsConnecting(false);
        return;
      }
      
      // Show toast to guide the user
      toast({
        title: "Authorization Started",
        description: `Please complete the authorization in the popup window.`,
      });
      
      // If user is authenticated, poll for new accounts
      if (isAuthenticated) {
        // Set up polling to check for newly connected accounts
        let attempts = 0;
        const interval = setInterval(async () => {
          attempts++;
          if (attempts > 30) { // Stop after 30 attempts (1 minute)
            clearInterval(interval);
            toast({
              title: "Connection Timeout",
              description: "Please try connecting again",
              variant: "destructive",
            });
            setIsConnecting(false);
            return;
          }
          
          try {
            // Check for new accounts
            const updatedAccounts = await socialPlatformsApi.getAccounts();
            
            // More sophisticated account check - both count and platform match
            const hasNewAccount = updatedAccounts.length > connectedAccounts.length;
            
            // Also check if we have any accounts matching the current platform
            const platformAccounts = updatedAccounts.filter(acc => 
              acc.platform.name.toLowerCase() === platform.id.toLowerCase()
            );
            
            const existingPlatformAccounts = connectedAccounts.filter(acc => 
              acc.platform.name.toLowerCase() === platform.id.toLowerCase()
            );
            
            const hasNewPlatformAccount = platformAccounts.length > existingPlatformAccounts.length;
            
            if (hasNewAccount || hasNewPlatformAccount) {
              console.log(`${platform.id} connection detected: New accounts found`);
              clearInterval(interval);
              setConnectedAccounts(updatedAccounts);
              setIsConnecting(false);
              
              toast({
                title: "Account Connected",
                description: `Successfully connected ${platform.name}`,
              });
            }
          } catch (e) {
            console.error("Error checking for new accounts:", e);
          }
        }, 2000); // Poll every 2 seconds
      } else {
        // For unauthenticated users, just show a success message
        setTimeout(() => {
          toast({
            title: "Demo Mode",
            description: "In demo mode, connections are simulated. Login for full functionality.",
          });
          setIsConnecting(false);
        }, 5000);
      }
    } catch (error) {
      console.error("Error connecting platform:", error);
      toast({
        title: "Connection Error",
        description: `Failed to connect ${platform.name}. Please try again.`,
        variant: "destructive",
      });
      setIsConnecting(false);
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

  // Render the connected accounts tab content
  const renderConnectedAccounts = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center py-10">
          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
          <span>Loading connected accounts...</span>
        </div>
      )
    }
    
    if (connectedAccounts.length === 0) {
      return (
        <div className="space-y-4 py-10 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
            <Link2 className="h-6 w-6 text-gray-500" />
          </div>
          <div>
            <h3 className="text-lg font-medium">No connected accounts</h3>
            <p className="text-muted-foreground">Connect your first account to get started</p>
          </div>
          <Button onClick={() => setShowConnected(false)} variant="outline">
            Browse Available Platforms
          </Button>
        </div>
      )
    }

    // Ensure connectedAccounts is an array before using reduce
    const accountsByPlatform = Array.isArray(connectedAccounts) 
      ? connectedAccounts.reduce((groups: Record<string, SocialAccount[]>, account: SocialAccount) => {
          const platform = account.provider;
          if (!groups[platform]) {
            groups[platform] = [];
          }
          groups[platform].push(account);
          return groups;
        }, {})
      : {} as Record<string, SocialAccount[]>;
    
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Render specialized components for TikTok and LinkedIn */}
        {accountsByPlatform['tiktok']?.map((account: SocialAccount) => (
          <TikTokConnect
            key={account.id}
            isConnected={true}
            account={account}
            onConnect={async () => {}}
            onDisconnect={handleDisconnectAccount}
            isConnecting={false}
          />
        ))}

        {accountsByPlatform['linkedin']?.map((account: SocialAccount) => (
          <LinkedInConnect
            key={account.id}
            isConnected={true}
            account={account}
            onDisconnect={async () => {}}
            isConnecting={false}
          />
        ))}

        {accountsByPlatform['youtube']?.map((account: SocialAccount) => (
          <YouTubeConnect
            key={account.id}
            isConnected={true}
            account={account}
            onConnect={async () => {}}
            onDisconnect={handleDisconnectAccount}
            isConnecting={false}
          />
        ))}

        {accountsByPlatform['threads']?.map((account: SocialAccount) => (
          <ThreadsConnect
            key={account.id}
            isConnected={true}
            account={account}
            onConnect={async () => {}}
            onDisconnect={handleDisconnectAccount}
            isConnecting={false}
          />
        ))}

        {accountsByPlatform['pinterest']?.map((account: SocialAccount) => (
          <PinterestConnect
            key={account.id}
            isConnected={true}
            account={account}
            onConnect={async () => {}}
            onDisconnect={handleDisconnectAccount}
            isConnecting={false}
          />
        ))}

        {accountsByPlatform['google']?.map((account: SocialAccount) => (
          <GoogleAdsConnect
            key={account.id}
            isConnected={true}
            account={account}
            onConnect={async () => {}}
            onDisconnect={handleDisconnectAccount}
            isConnecting={false}
          />
        ))}

        {/* Render generic cards for other platforms */}
        {connectedAccounts
          .filter((account: SocialAccount) => 
            !['tiktok', 'linkedin', 'youtube', 'threads', 'pinterest', 'google'].includes(account.provider)
          )
          .map((account: SocialAccount) => {
            // Determine the appropriate icon based on platform name
            let Icon = Link2;
            switch (account.provider) {
              case 'facebook': Icon = Facebook; break;
              case 'instagram': Icon = Instagram; break;
              case 'twitter': Icon = Twitter; break;
              case 'youtube': Icon = Youtube; break;
              case 'pinterest': Icon = PinIcon; break;
              case 'google': Icon = LineChart; break;
              case 'threads': Icon = MessageCircle; break;
            }
            
            return (
              <Card key={account.id} className="overflow-hidden">
                <CardHeader className={`bg-gradient-to-r ${getPlatformColor(account.provider)}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Icon className="h-5 w-5 text-white" />
                      <CardTitle className="text-white">{account.display_name}</CardTitle>
                    </div>
                    {account.is_primary && (
                      <Badge variant="secondary" className="bg-white/20 text-white">
                        Primary
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="text-white/80">
                    Connected on {new Date(account.created_at).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    {account.profile_picture_url ? (
                      <img
                        src={account.profile_picture_url}
                        alt={account.display_name}
                        className="h-12 w-12 rounded-full object-cover"
                      />
                    ) : (
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-200">
                        <Icon className="h-6 w-6 text-gray-500" />
                      </div>
                    )}
                    <div>
                      <h3 className="font-medium">{account.account_name}</h3>
                      <p className="text-sm text-gray-500">{account.account_id}</p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="bg-gray-50 px-6 py-4">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    onClick={() => handleDisconnectAccount(account.id)}
                  >
                    Disconnect Account
                  </Button>
                </CardFooter>
              </Card>
            )
        })}
      </div>
    )
  }

  // Render available platforms that can be connected
  const renderAvailablePlatforms = () => {
    // If we're in a connecting state, show all platforms, otherwise filter to exclude connected ones
    const filteredPlatforms = isConnecting
      ? availablePlatforms
      : availablePlatforms.filter(platform => {
          // Check if this platform is already connected
          return !connectedAccounts.some(
            account => account.provider === platform.id.toLowerCase()
          )
        })

    if (filteredPlatforms.length === 0) {
      return (
        <div className="space-y-4 py-10 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-medium">All platforms connected!</h3>
            <p className="text-muted-foreground">You've connected all available platforms</p>
          </div>
          <Button onClick={() => setShowConnected(true)} variant="outline">
            View Connected Accounts
          </Button>
        </div>
      )
    }

    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Render specialized components for TikTok and LinkedIn when not connected */}
        {filteredPlatforms.some(p => p.id === 'tiktok') && (
          <TikTokConnect
            isConnected={false}
            onConnect={() => handleConnectPlatform(filteredPlatforms.find(p => p.id === 'tiktok')!)}
            onDisconnect={async () => {}}
            isConnecting={isConnecting === 'tiktok'}
          />
        )}

        {filteredPlatforms.some(p => p.id === 'linkedin') && (
          <LinkedInConnect
            isConnected={false}
            onConnect={() => handleConnectPlatform(filteredPlatforms.find(p => p.id === 'linkedin')!)}
            onDisconnect={async () => {}}
            isConnecting={isConnecting === 'linkedin'}
          />
        )}

        {/* Render generic cards for other platforms */}
        {filteredPlatforms
          .filter(platform => !['tiktok', 'linkedin'].includes(platform.id))
          .map(platform => (
            <Card 
              key={platform.id} 
              id={`platform-card-${platform.id}`} 
              className={`overflow-hidden ${selectedPlatformId === platform.id ? 'ring-2 ring-primary ring-offset-2' : ''}`}
            >
              <CardHeader className={`bg-gradient-to-r ${platform.color}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <platform.icon className="h-5 w-5 text-white" />
                    <CardTitle className="text-white">{platform.name}</CardTitle>
                  </div>
                  {platform.popular && (
                    <Badge variant="secondary" className="bg-white/20 text-white">
                      Popular
                    </Badge>
                  )}
                </div>
                <CardDescription className="text-white/80">
                  {platform.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="flex flex-col items-center justify-center py-4 text-center">
                  <platform.icon className="mb-4 h-12 w-12 text-gray-400" />
                  <h3 className="mb-2 text-lg font-medium">Connect {platform.name}</h3>
                  <p className="mb-4 text-sm text-gray-500">
                    {platform.description}
                  </p>
                </div>
              </CardContent>
              <CardFooter className="bg-gray-50 px-6 py-4">
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
                    <>Connect {platform.name}</>
                  )}
                </Button>
              </CardFooter>
            </Card>
          ))}
      </div>
    )
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
          {/* TikTok and LinkedIn components for unauthenticated users */}
          <TikTokConnect
            isConnected={false}
            onConnect={() => handleConnectPlatform(availablePlatforms.find(p => p.id === 'tiktok')!)}
            onDisconnect={async () => {}}
            isConnecting={isConnecting === 'tiktok'}
          />

          <LinkedInConnect
            isConnected={false}
            onConnect={() => handleConnectPlatform(availablePlatforms.find(p => p.id === 'linkedin')!)}
            onDisconnect={async () => {}}
            isConnecting={isConnecting === 'linkedin'}
          />

          {/* Generic cards for other platforms */}
          {availablePlatforms
            .filter(platform => !['tiktok', 'linkedin'].includes(platform.id))
            .slice(0, 4) // Limit to keep UI clean
            .map(platform => (
              <Card 
                key={platform.id} 
                id={`platform-card-${platform.id}`}
                className={`overflow-hidden ${selectedPlatformId === platform.id ? 'ring-2 ring-primary ring-offset-2' : ''}`}
              >
                <CardHeader className={`bg-gradient-to-r ${platform.color}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <platform.icon className="h-5 w-5 text-white" />
                      <CardTitle className="text-white">{platform.name}</CardTitle>
                    </div>
                    {platform.popular && (
                      <Badge variant="secondary" className="bg-white/20 text-white">
                        Popular
                      </Badge>
                    )}
                  </div>
                  <CardDescription className="text-white/80">
                    {platform.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center justify-center py-4 text-center">
                    <platform.icon className="mb-4 h-12 w-12 text-gray-400" />
                    <h3 className="mb-2 text-lg font-medium">Connect {platform.name}</h3>
                    <p className="mb-4 text-sm text-gray-500">
                      {platform.description}
                    </p>
                  </div>
                </CardContent>
                <CardFooter className="bg-gray-50 px-6 py-4">
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
                      <>Connect {platform.name}</>
                    )}
                  </Button>
                </CardFooter>
              </Card>
            ))}
        </div>
      </div>
    )
  }

  // The main authenticated UI with tabs
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

      <Tabs defaultValue={showConnected ? "connected" : "available"} className="space-y-4">
        <TabsList>
          <TabsTrigger 
            value="connected" 
            onClick={() => setShowConnected(true)}
          >
            Connected Platforms
          </TabsTrigger>
          <TabsTrigger 
            value="available"
            onClick={() => setShowConnected(false)}
          >
            Available Platforms
          </TabsTrigger>
        </TabsList>

        <TabsContent value="connected">
          {renderConnectedAccounts()}
        </TabsContent>

        <TabsContent value="available">
          {renderAvailablePlatforms()}
        </TabsContent>
      </Tabs>
    </div>
  )
}


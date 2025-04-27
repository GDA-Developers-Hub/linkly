import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { SUPPORTED_PLATFORMS, initOAuthFlow, getConnectedPlatforms, disconnectPlatform } from '../Utils/PlatformUtils';
import { isAuthenticated, getAccessToken, getRefreshToken } from '../Utils/Auth';
import { getFullCallbackURL } from '../Utils/OAuthUtils';
import { logOAuthConfig } from '../Utils/OAuthDebug';
import Swal from 'sweetalert2';
import { 
  Twitter, 
  Facebook, 
  Instagram, 
  Linkedin, 
  Youtube, 
  Music, 
  Send,
  RefreshCw,
  CheckCircle,
  XCircle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import axios from 'axios';
import API_BASE_URL from '../Utils/BaseUrl';
import TelegramLoginWidget from '../Utils/TelegramLoginWidget';
import ReactDOM from 'react-dom';

const PlatformConnect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const isRequired = searchParams.get('required') === 'true';

  const [platforms, setPlatforms] = useState(SUPPORTED_PLATFORMS);
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState(null);
  const [useCustomCredentials, setUseCustomCredentials] = useState(false);

  // Map platform IDs to Lucide icons
  const platformIcons = {
    twitter: <Twitter className="h-6 w-6" />,
    facebook: <Facebook className="h-6 w-6" />,
    instagram: <Instagram className="h-6 w-6" />,
    linkedin: <Linkedin className="h-6 w-6" />,
    youtube: <Youtube className="h-6 w-6" />,
    tiktok: <Music className="h-6 w-6" />,
    telegram: <Send className="h-6 w-6" />
  };

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated()) {
      navigate('/login?returnUrl=/platform-connect');
      return;
    }

    // Load connected platforms on initial render
    fetchConnectedPlatforms();
    
    // Show welcome message if required
    if (isRequired) {
      Swal.fire({
        title: 'Connect Your Accounts',
        text: 'Please connect at least one social media account to get started with Linkly.',
        icon: 'info',
        confirmButtonText: 'Let\'s Go!',
      });
    }
    
    // Add event listener for messages from popup
    const handleMessage = (event) => {
      // Verify message is from our origi
      if (event.origin !== window.location.origin) return;
      
      const { type, platform, data, error } = event.data;
      
      if (type === 'OAUTH_SUCCESS' && platform) {
        console.log(`OAuth successful for ${platform}:`, data);
        fetchConnectedPlatforms();
        Swal.fire({
          title: 'Connected!',
          text: `Your ${platform} account has been successfully connected.`,
          icon: 'success',
          timer: 2000,
          showConfirmButton: false
        });
      } else if (type === 'OAUTH_ERROR') {
        console.error('OAuth error:', error);
        Swal.fire({
          title: 'Connection Error',
          text: error || 'Failed to connect account. Please try again.',
          icon: 'error'
        });
      }
    };
    
    window.addEventListener('message', handleMessage);
    
    // Clean up event listener
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [navigate, isRequired]);

  const fetchConnectedPlatforms = async () => {
    setLoading(true);
    try {
      console.log('Fetching connected platforms...');
      const connected = await getConnectedPlatforms();
      console.log("Connected platforms response:", JSON.stringify(connected));
      
      // Handle empty array or undefined properly
      setConnectedPlatforms(connected || []);
      
      // Update platforms with connection status
      setPlatforms(prevPlatforms => 
        prevPlatforms.map(platform => ({
          ...platform,
          connected: connected?.some(conn => conn.platform === platform.id) || false,
          accountType: connected?.find(conn => conn.platform === platform.id)?.account_type || null,
          profileData: connected?.find(conn => conn.platform === platform.id)?.profile || null
        }))
      );
    } catch (error) {
      console.error("Error fetching connected platforms:", error);
      console.log("Error status:", error.response?.status);
      console.log("Error data:", JSON.stringify(error.response?.data));
      
      // Only show error toast for non-404 errors
      // 404 likely means the endpoint doesn't exist in this version
      if (!error.response || error.response.status !== 404) {
        Swal.fire({
          title: 'Error',
          text: 'Failed to load your connected accounts. Please try again.',
          icon: 'error',
        });
      } else {
        console.log('API endpoint not found, assuming no connected platforms');
      }
      
      // Set empty array to prevent errors
      setConnectedPlatforms([]);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = (platform) => {
    setConnectingPlatform(platform.id);
    
    // Special case for Telegram - use Telegram Login Widget
    if (platform.id === 'telegram') {
      Swal.fire({
        title: 'Connect Telegram',
        html: `
          <div id="telegram-login-container" class="flex justify-center my-3">
            <script 
              async 
              src="https://telegram.org/js/telegram-widget.js?22" 
              data-telegram-login="linkly_ai_bot" 
              data-size="large"
              data-radius="8"
              data-request-access="write"
              data-userpic="true"
              data-onauth="window.onTelegramAuth(user)"
            ></script>
            <div id="telegram-fallback" style="display:none; margin-top: 15px; text-align: center;">
              <p>If the Telegram login button doesn't appear, please:</p>
              <ol style="text-align: left; margin-top: 10px;">
                <li>Make sure you're not blocking third-party scripts</li>
                <li>Try refreshing the page</li>
                <li>Ensure the Telegram bot token is correctly configured in the backend</li>
              </ol>
              <button id="manual-telegram-login" style="margin-top: 15px; background-color: #3390ec; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;">
                Open Telegram Bot
              </button>
            </div>
          </div>
        `,
        showCloseButton: true,
        showConfirmButton: false,
        didOpen: () => {
          console.log('Initializing Telegram login widget');
          
          // Show fallback message if widget doesn't load within 3 seconds
          setTimeout(() => {
            const container = document.getElementById('telegram-login-container');
            const fallback = document.getElementById('telegram-fallback');
            if (container && !container.querySelector('.telegram-login-button') && fallback) {
              console.log('Telegram widget not loaded, showing fallback');
              fallback.style.display = 'block';
              
              // Add click handler for manual button
              const manualButton = document.getElementById('manual-telegram-login');
              if (manualButton) {
                manualButton.addEventListener('click', () => {
                  // Open Telegram bot in a new tab
                  window.open('https://t.me/linkly_ai_bot', '_blank');
                  
                  Swal.fire({
                    title: 'Manual Connection',
                    text: 'Please message the bot on Telegram and follow the instructions there to connect your account.',
                    icon: 'info'
                  });
                });
              }
            }
          }, 3000);
          
          // Define the global auth handler function
          window.onTelegramAuth = async (userData) => {
            console.log('Telegram auth data received:', userData);
            
            try {
              // Send the auth data to the backend
              const response = await axios.post(
                `${API_BASE_URL}/users/connect/telegram/`, 
                userData,
                {
                  headers: {
                    'Authorization': `Bearer ${getAccessToken()}`
                  }
                }
              );
              
              console.log('Telegram connection response:', response.data);
              
              // Close the dialog
              Swal.close();
              
              // Show success message
              Swal.fire({
                title: 'Connected!',
                text: 'Your Telegram account has been successfully connected.',
                icon: 'success',
                timer: 2000,
                showConfirmButton: false
              });
              
              // Refresh connected platforms list
              fetchConnectedPlatforms();
            } catch (error) {
              console.error('Error connecting Telegram account:', error);
              Swal.fire({
                title: 'Connection Error',
                text: error.response?.data?.error || 'Failed to connect your Telegram account. Please try again.',
                icon: 'error'
              });
            }
          };
        }
      });
      
      // Reset connecting platform state
      setConnectingPlatform(null);
      return;
    }
    
    // Handle direct login methods for Facebook and Instagram
    if (platform.id === 'facebook' || platform.id === 'instagram') {
      // Log OAuth configuration details for debugging
      logOAuthConfig(platform.id);
      
      // Use the direct login endpoint
      const loginUrl = `${API_BASE_URL}/users/auth/login/${platform.id}/`;
      console.log(`Redirecting to ${platform.id} login URL:`, loginUrl);
      window.location.href = loginUrl;
      return;
    }
    
    // Generate a unique state parameter for this OAuth flow
    const stateParam = platform.id + '_' + Math.random().toString(36).substring(2, 15);
    
    // Store custom credentials flag in the state if needed
    const effectiveState = useCustomCredentials ? `custom_${stateParam}` : stateParam;
    
    // Use the getFullCallbackURL utility for consistent redirect URIs
    let redirectUri = getFullCallbackURL(platform.id);
    
    // Log the redirect URI for debugging
    console.log(`Using redirect URI for ${platform.id}:`, redirectUri);
    
    // Use a direct URL for the API call to avoid parameter encoding issues
    const apiUrl = `${API_BASE_URL}/users/auth/init/?platform=${platform.id}&redirect_uri=${encodeURIComponent(redirectUri)}&use_client_credentials=${useCustomCredentials}`;
    console.log('Using direct API URL:', apiUrl);
    
    // Make the OAuth initialization call
    axios.get(apiUrl, {
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`
      }
    })
    .then(response => {
      if (response.data && response.data.auth_url) {
        let authUrl = response.data.auth_url;
        
        // For Twitter, add personalization_id
        if (platform.id === 'twitter' && authUrl.includes('twitter.com')) {
          const personalizationId = `v1_${Math.random().toString(36).substring(2, 15)}`;
          const separator = authUrl.includes('?') ? '&' : '?';
          authUrl = `${authUrl}${separator}personalization_id=${personalizationId}`;
          console.log('Added personalization_id to Twitter auth URL');
        }
        
        console.log(`Redirecting to ${platform.id} auth URL:`, authUrl);
        
        // For all platforms, open in a popup window instead of redirecting the page
        // Calculate center position for the popup
        const width = 600;
        const height = 700;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;
        
        // Open popup window
        const popup = window.open(
          authUrl,
          `${platform.id.charAt(0).toUpperCase() + platform.id.slice(1)}Auth`,
          `width=${width},height=${height},left=${left},top=${top},toolbar=0,scrollbars=1,status=1,resizable=1,location=1`
        );
        
        if (!popup || popup.closed || typeof popup.closed === 'undefined') {
          // Popup was blocked
          setConnectingPlatform(null);
          Swal.fire({
            title: 'Popup Blocked',
            text: `Please allow popups for this site to connect your ${platform.name} account.`,
            icon: 'warning'
          });
        }
      } else {
        throw new Error('Failed to get authorization URL');
      }
    })
    .catch(error => {
      console.error(`Error initializing ${platform.id} OAuth flow:`, error);
      setConnectingPlatform(null);
      Swal.fire({
        title: 'Connection Error',
        text: `Failed to connect to ${platform.id}: ${error.response?.data?.error || error.message}`,
        icon: 'error'
      });
    });
  };

  const handleDisconnect = async (platform) => {
    try {
      await Swal.fire({
        title: `Disconnect ${platform.name}?`,
        text: `Are you sure you want to disconnect your ${platform.name} account?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, disconnect',
        cancelButtonText: 'Cancel',
      }).then(async (result) => {
        if (result.isConfirmed) {
          setConnectingPlatform(platform.id);
          await disconnectPlatform(platform.id);
          
          Swal.fire({
            title: 'Disconnected',
            text: `Your ${platform.name} account has been disconnected.`,
            icon: 'success',
            timer: 2000,
            showConfirmButton: false,
          });
          
          // Refresh the list
          fetchConnectedPlatforms();
        }
      });
    } catch (error) {
      console.error(`Error disconnecting ${platform.name}:`, error);
      Swal.fire({
        title: 'Error',
        text: `Failed to disconnect ${platform.name}. Please try again.`,
        icon: 'error',
      });
    } finally {
      setConnectingPlatform(null);
    }
  };

  const handleContinue = () => {
    navigate('/dashboard');
  };

  const refreshConnections = () => {
    fetchConnectedPlatforms();
    Swal.fire({
      title: 'Refreshing',
      text: 'Updating your connected accounts...',
      icon: 'info',
      timer: 1500,
      showConfirmButton: false
    });
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mb-4"></div>
          <p className="text-gray-600">Loading your connected accounts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600 mb-4">Connect Your Platforms</h1>
          <p className="text-gray-600 max-w-2xl mx-auto mb-6">
            Connect your social media accounts to manage them all in one place. 
            Linkly makes it easy to schedule posts, analyze performance, and grow your online presence.
          </p>
          
          <button 
            onClick={refreshConnections}
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Connections
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {platforms.map((platform) => (
            <div 
              key={platform.id}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <div className="p-2 rounded-full bg-blue-50 text-blue-600 mr-3">
                    {platformIcons[platform.id] || <ExternalLink className="h-6 w-6" />}
                  </div>
                  <h2 className="text-xl font-semibold text-gray-800">{platform.name}</h2>
                  {platform.connected && (
                    <span className="ml-auto flex items-center text-green-600 text-sm font-medium">
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Connected
                    </span>
                  )}
                </div>
                
                <p className="text-gray-600 mb-5">
                  {platform.description}
                </p>
                
                {platform.connected && platform.profileData && (
                  <div className="mb-5 p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="flex items-center">
                      {platform.profileData.profile_picture && (
                        <img 
                          src={platform.profileData.profile_picture} 
                          alt={platform.profileData.username || platform.profileData.name || 'Profile'}
                          className="w-10 h-10 rounded-full mr-3"
                        />
                      )}
                      <div className="flex-1">
                        <div className="font-medium">
                          {platform.profileData.username || platform.profileData.name || 'Connected Account'}
                        </div>
                        {platform.accountType && (
                          <div className="text-xs text-gray-500">
                            {platform.accountType.charAt(0).toUpperCase() + platform.accountType.slice(1)} Account
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {platform.connected ? (
                  <button
                    onClick={() => handleDisconnect(platform)}
                    disabled={connectingPlatform === platform.id}
                    className="w-full py-2 rounded-lg font-medium transition-colors flex items-center justify-center bg-red-50 text-red-600 border border-red-100 hover:bg-red-100"
                  >
                    {connectingPlatform === platform.id ? (
                      <>
                        <div className="animate-spin h-4 w-4 border-2 border-red-600 border-t-transparent rounded-full mr-2"></div>
                        Disconnecting...
                      </>
                    ) : (
                      <>
                        <XCircle className="h-4 w-4 mr-2" />
                        Disconnect
                      </>
                    )}
                  </button>
                ) : (
                  <button
                    onClick={() => handleConnect(platform)}
                    disabled={connectingPlatform === platform.id}
                    className="w-full py-2 rounded-lg font-medium transition-colors flex items-center justify-center bg-blue-600 text-white hover:bg-blue-700"
                  >
                    {connectingPlatform === platform.id ? (
                      <>
                        <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                        Connecting...
                      </>
                    ) : (
                      <>
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Connect
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center">
          <button
            onClick={handleContinue}
            className={`px-8 py-3 rounded-lg font-medium flex items-center justify-center mx-auto bg-blue-600 text-white hover:bg-blue-700 transition-colors ${
              isRequired && connectedPlatforms.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={isRequired && connectedPlatforms.length === 0}
          >
            Continue to Dashboard
            <ChevronRight className="h-4 w-4 ml-2" />
          </button>
          
          {isRequired && connectedPlatforms.length === 0 && (
            <p className="text-amber-600 mt-2">
              Please connect at least one platform to continue.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PlatformConnect; 
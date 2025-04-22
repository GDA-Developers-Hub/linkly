import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { SUPPORTED_PLATFORMS, initOAuthFlow, getConnectedPlatforms, disconnectPlatform } from '../Utils/PlatformUtils';
import { isAuthenticated, getAccessToken, getRefreshToken } from '../Utils/Auth';
import Swal from 'sweetalert2';
import PlatformCredentialsModal from './PlatformCredentialsModal';

const PlatformConnect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const isRequired = searchParams.get('required') === 'true';

  const [platforms, setPlatforms] = useState(SUPPORTED_PLATFORMS);
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);

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
      // Verify message is from our origin
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

  const handleConnect = async (platform, useCustomCredentials = false) => {
    setConnectingPlatform(platform.id);
    let authWindow = null;
    
    try {
      // Open the window first, directly triggered by the user's click
      authWindow = window.open('about:blank', `${platform.name} Authorization`, 'width=600,height=700');
      
      if (!authWindow) {
        throw new Error('Popup blocked! Please allow popups for this site to connect your account.');
      }
      
      // Get the current URL for the redirect_uri - make sure it matches backend expectations
      const redirectUri = `${window.location.origin}/oauth-callback`;
      console.log(`Using redirect URI: ${redirectUri} for ${platform.name}`);
      
      // Initialize OAuth flow
      console.log(`Initializing OAuth flow for ${platform.name}...`);
      const authUrl = await initOAuthFlow(platform.id, redirectUri, useCustomCredentials);
      
      // Navigate the already-opened window to the authorization URL
      if (authWindow) {
        console.log(`Redirecting popup to ${platform.name} authorization...`);
        authWindow.location.href = authUrl;
        
        // For Twitter specifically, add a longer timeout
        if (platform.id === 'twitter') {
          console.log("Setting up Twitter-specific event handling");
          // Set a timeout to check if we need to refresh the platforms list
          // This is a fallback in case the window.postMessage doesn't work
          setTimeout(() => {
            if (connectingPlatform === platform.id) {
              console.log("Twitter connection timeout reached, refreshing platforms");
              fetchConnectedPlatforms();
              setConnectingPlatform(null);
            }
          }, 30000); // 30 second timeout for Twitter
        }
      } else {
        throw new Error('The authorization window was closed before it could be used.');
      }
      
      // We don't need to poll for window close anymore, as we'll receive a message
      // when the authentication is complete
      
    } catch (error) {
      console.error(`Error connecting to ${platform.name}:`, error);
      if (authWindow && !authWindow.closed) {
        authWindow.close();
      }
      
      Swal.fire({
        title: 'Connection Error',
        text: error.message || `Failed to connect to ${platform.name}. Please try again.`,
        icon: 'error',
      });
    } finally {
      // Reset connecting state after a reasonable timeout if something goes wrong
      setTimeout(() => {
        if (connectingPlatform === platform.id) {
          console.log(`Resetting connecting state for ${platform.id} after timeout`);
          setConnectingPlatform(null);
        }
      }, 60000); // 1 minute timeout
    }
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

  const openCredentialsModal = (platform) => {
    setSelectedPlatform(platform);
    setModalOpen(true);
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
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-blue-600 mb-4">Connect Your Platforms</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Connect your social media accounts to manage them all in one place. 
            Linkly makes it easy to schedule posts, analyze performance, and grow your online presence.
          </p>
          
          {/* Debug section - only visible in development */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-4 p-3 bg-gray-100 rounded-lg inline-block text-left text-xs">
              <p className="font-medium mb-1">Auth Debug:</p>
              <p>Access Token: {getAccessToken() ? '✅ Present' : '❌ Missing'}</p>
              <p>Refresh Token: {getRefreshToken() ? '✅ Present' : '❌ Missing'}</p>
              <button
                className="mt-2 px-3 py-1 bg-gray-200 rounded text-gray-600 hover:bg-gray-300"
                onClick={() => {
                  const accessToken = getAccessToken();
                  Swal.fire({
                    title: 'Token Info',
                    text: accessToken ? `Token: ${accessToken.slice(0, 20)}...` : 'No token found',
                    icon: accessToken ? 'info' : 'warning'
                  });
                }}
              >
                Inspect Token
              </button>
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {platforms.map((platform) => (
            <div 
              key={platform.id}
              className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">{platform.icon}</span>
                  <h2 className="text-xl font-semibold text-gray-800">{platform.name}</h2>
                  {platform.connected && (
                    <span className="ml-auto px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                      Connected
                    </span>
                  )}
                </div>
                
                <p className="text-gray-600 mb-5">
                  {platform.description}
                </p>
                
                {platform.connected && platform.profileData && (
                  <div className="mb-5 p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      {platform.profileData.profile_picture && (
                        <img 
                          src={platform.profileData.profile_picture} 
                          alt={platform.profileData.username || platform.profileData.name || 'Profile'}
                          className="w-10 h-10 rounded-full mr-3"
                        />
                      )}
                      <div>
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
                    className="w-full py-2 rounded-lg font-medium transition-colors bg-red-50 text-red-600 border border-red-200 hover:bg-red-100"
                  >
                    {connectingPlatform === platform.id ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin h-5 w-5 border-2 border-t-transparent rounded-full mr-2"></div>
                        Disconnecting...
                      </span>
                    ) : (
                      'Disconnect'
                    )}
                  </button>
                ) : (
                  <div className="space-y-2">
                    <button
                      onClick={() => handleConnect(platform)}
                      disabled={connectingPlatform === platform.id}
                      className="w-full py-2 rounded-lg font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700"
                    >
                      {connectingPlatform === platform.id ? (
                        <span className="flex items-center justify-center">
                          <div className="animate-spin h-5 w-5 border-2 border-t-transparent rounded-full mr-2"></div>
                          Connecting...
                        </span>
                      ) : (
                        'Connect'
                      )}
                    </button>
                    
                    <button
                      onClick={() => openCredentialsModal(platform)}
                      disabled={connectingPlatform === platform.id}
                      className="w-full py-2 rounded-lg font-medium transition-colors border border-gray-300 text-gray-700 hover:bg-gray-100"
                    >
                      Use My Own Credentials
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="text-center">
          <button
            onClick={handleContinue}
            className={`px-8 py-3 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors ${
              isRequired && connectedPlatforms.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={isRequired && connectedPlatforms.length === 0}
          >
            Continue to Dashboard
          </button>
          
          {isRequired && connectedPlatforms.length === 0 && (
            <p className="text-amber-600 mt-2">
              Please connect at least one platform to continue.
            </p>
          )}
        </div>
      </div>
      
      {/* Credentials Modal */}
      <PlatformCredentialsModal 
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        platform={selectedPlatform}
        onConnect={handleConnect}
      />
    </div>
  );
};

export default PlatformConnect; 
import React, { useState, useEffect } from 'react';
import OAuthLoginButton from '../components/OAuthLoginButton';
import { createOAuthURL, getFullCallbackURL } from '../Utils/OAuthUtils';
import { API_ENDPOINTS } from '../constants/endpoints';
import API_BASE_URL from '../Utils/BaseUrl';
import axios from 'axios';
import { getAccessToken } from '../Utils/Auth';
import Swal from 'sweetalert2';

/**
 * OAuth Demo Page
 * 
 * This page demonstrates the different OAuth login options and configurations
 */
const OAuthDemo = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [lastConnectedProfile, setLastConnectedProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Fetch connected platforms on mount
  useEffect(() => {
    fetchConnectedPlatforms();
  }, []);
  
  const fetchConnectedPlatforms = async () => {
    setIsLoading(true);
    try {
      const token = getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data && response.data.connected_platforms) {
        setConnectedPlatforms(response.data.connected_platforms || []);
      } else {
        // If user has no connected_platforms field, create an empty array
        setConnectedPlatforms([]);
      }
    } catch (error) {
      console.error('Error fetching connected platforms:', error);
      Swal.fire({
        title: 'Error',
        text: 'Failed to load connected platforms',
        icon: 'error',
        timer: 3000
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSuccess = (data) => {
    console.log('OAuth Success:', data);
    
    if (data.connected && !connectedPlatforms.some(p => p.platform === data.platform)) {
      setConnectedPlatforms([...connectedPlatforms, { 
        platform: data.platform,
        profile: data.profile
      }]);
    }
    
    setLastConnectedProfile(data);
    
    // Refresh the platforms list to get updated data
    fetchConnectedPlatforms();
  };
  
  const handleError = (error) => {
    console.error('OAuth Error:', error);
    Swal.fire({
      title: 'Connection Error',
      text: error.message || 'Failed to connect platform',
      icon: 'error',
      timer: 3000
    });
  };
  
  const handleInitiateOAuth = async (platform) => {
    try {
      setIsLoading(true);
      
      // Get access token if user is logged in
      const token = getAccessToken();
      
      // Create the params for the request
      const redirectUri = getFullCallbackURL(platform);
      const params = new URLSearchParams();
      params.append('platform', platform);
      params.append('redirect_uri', redirectUri);
      
      // Make the request to initialize OAuth
      const requestUrl = `${API_BASE_URL}/users/auth/init/?${params.toString()}`;
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await axios.get(requestUrl, { headers });
      
      if (response.data && response.data.auth_url) {
        // Store code_verifier if provided (for PKCE)
        if (response.data.code_verifier && response.data.state) {
          const storeKey = `pkce_verifier_${response.data.state}`;
          sessionStorage.setItem(storeKey, response.data.code_verifier);
          console.log(`Stored code verifier for ${platform} with state ${response.data.state}`);
        }
        
        // Open the auth URL in a popup
        const authUrl = response.data.auth_url;
        const width = 600;
        const height = 700;
        const left = window.screen.width / 2 - width / 2;
        const top = window.screen.height / 2 - height / 2;
        
        // Add event listener for messages from the popup
        const messageHandler = (event) => {
          const { type, platform: responsePlatform, data, error } = event.data || {};
          
          if (type === 'OAUTH_SUCCESS' && responsePlatform === platform) {
            window.removeEventListener('message', messageHandler);
            handleSuccess(data);
          } else if (type === 'OAUTH_ERROR') {
            window.removeEventListener('message', messageHandler);
            handleError(error);
          }
        };
        
        window.addEventListener('message', messageHandler);
        
        // Open the popup
        const popup = window.open(
          authUrl,
          `${platform}_oauth`,
          `width=${width},height=${height},left=${left},top=${top},toolbar=0,scrollbars=1,status=1,resizable=1`
        );
        
        if (!popup || popup.closed || typeof popup.closed === 'undefined') {
          window.removeEventListener('message', messageHandler);
          throw new Error('Popup was blocked by the browser');
        }
        
        // Check if popup was closed
        const checkClosed = setInterval(() => {
          if (!popup || popup.closed) {
            clearInterval(checkClosed);
            window.removeEventListener('message', messageHandler);
            setIsLoading(false);
          }
        }, 1000);
      } else {
        throw new Error('Failed to get authorization URL');
      }
    } catch (error) {
      console.error(`Error initiating ${platform} OAuth:`, error);
      Swal.fire({
        title: 'Error',
        text: error.message || `Failed to connect to ${platform}`,
        icon: 'error',
        timer: 3000
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>OAuth Integration Demo</h1>
      
      <p>
        This page demonstrates the different OAuth login options and how they integrate
        with the backend using our custom OAuth utilities.
      </p>
      
      <h2>Social Login Options</h2>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '15px',
        marginBottom: '30px'
      }}>
        <OAuthLoginButton 
          platform="facebook" 
          onSuccess={handleSuccess}
          onError={handleError}
          onClick={() => handleInitiateOAuth('facebook')}
        />
        
        <OAuthLoginButton 
          platform="linkedin" 
          onSuccess={handleSuccess}
          onError={handleError}
          onClick={() => handleInitiateOAuth('linkedin')}
        />
        
        <OAuthLoginButton 
          platform="twitter" 
          onSuccess={handleSuccess}
          onError={handleError}
          onClick={() => handleInitiateOAuth('twitter')}
        />
        
        <OAuthLoginButton 
          platform="instagram" 
          onSuccess={handleSuccess}
          onError={handleError}
          onClick={() => handleInitiateOAuth('instagram')}
        />
        
        <OAuthLoginButton 
          platform="tiktok" 
          onSuccess={handleSuccess}
          onError={handleError}
          onClick={() => handleInitiateOAuth('tiktok')}
        />
        
        <OAuthLoginButton 
          platform="google" 
          onSuccess={handleSuccess}
          onError={handleError}
          onClick={() => handleInitiateOAuth('google')}
        />
      </div>
      
      <div style={{ display: 'flex', gap: '30px' }}>
        <div style={{ flex: '1' }}>
          <h2>Connected Platforms</h2>
          
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <div style={{ 
                display: 'inline-block', 
                width: '20px', 
                height: '20px', 
                border: '2px solid #ccc', 
                borderTopColor: '#3498db', 
                borderRadius: '50%',
                animation: 'spin 1s infinite linear'
              }}></div>
              <p>Loading connected platforms...</p>
            </div>
          ) : connectedPlatforms.length === 0 ? (
            <p>No platforms connected yet. Click one of the buttons above to connect.</p>
          ) : (
            <ul style={{ paddingLeft: '20px' }}>
              {connectedPlatforms.map(platform => (
                <li key={platform.platform} style={{ marginBottom: '10px' }}>
                  <strong style={{ textTransform: 'capitalize' }}>{platform.platform}</strong>
                  {platform.profile && platform.profile.username && (
                    <span> - {platform.profile.username}</span>
                  )}
                </li>
              ))}
            </ul>
          )}
          
          <button 
            onClick={fetchConnectedPlatforms}
            style={{
              padding: '8px 16px',
              background: '#f0f0f0',
              border: 'none',
              borderRadius: '4px',
              marginTop: '10px',
              cursor: 'pointer'
            }}
          >
            Refresh List
          </button>
        </div>
        
        <div style={{ flex: '1' }}>
          <h2>Last Connected Profile</h2>
          
          {lastConnectedProfile ? (
            <div style={{ 
              background: '#f7f7f7', 
              padding: '15px', 
              borderRadius: '5px',
              fontSize: '14px' 
            }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>Platform:</strong> {lastConnectedProfile.platform}
              </div>
              
              {lastConnectedProfile.username && (
                <div style={{ marginBottom: '8px' }}>
                  <strong>Username:</strong> {lastConnectedProfile.username}
                </div>
              )}
              
              {lastConnectedProfile.profileUrl && (
                <div style={{ marginBottom: '8px' }}>
                  <strong>Profile URL:</strong>{' '}
                  <a href={lastConnectedProfile.profileUrl} target="_blank" rel="noopener noreferrer">
                    {lastConnectedProfile.profileUrl}
                  </a>
                </div>
              )}
              
              <pre style={{ 
                marginTop: '15px',
                background: '#333',
                color: '#fff',
                padding: '10px',
                borderRadius: '3px',
                fontSize: '12px',
                overflow: 'auto'
              }}>
                {JSON.stringify(lastConnectedProfile, null, 2)}
              </pre>
            </div>
          ) : (
            <p>No profile connected yet. Connect to a platform to see details.</p>
          )}
        </div>
      </div>
      
      <h2>API Endpoints Reference</h2>
      
      <div style={{ marginTop: '20px' }}>
        <h3>Authorization URL</h3>
        <code style={{ background: '#f0f0f0', padding: '8px', display: 'block', marginBottom: '15px' }}>
          {API_ENDPOINTS.OAUTH_AUTHORIZE}?platform=PLATFORM_NAME
        </code>
        
        <h3>Platform Callbacks</h3>
        <ul style={{ paddingLeft: '20px' }}>
          {Object.entries(API_ENDPOINTS)
            .filter(([key]) => key.includes('CALLBACK'))
            .map(([key, value]) => (
              <li key={key} style={{ marginBottom: '10px' }}>
                <strong>{key}:</strong> <code>{value}</code>
              </li>
            ))}
        </ul>
        
        <h3>Full Callback URLs (used in OAuth flows)</h3>
        <div style={{ marginTop: '10px' }}>
          <ul style={{ paddingLeft: '20px' }}>
            {['linkedin', 'twitter', 'facebook', 'instagram', 'tiktok', 'google'].map(platform => (
              <li key={platform} style={{ marginBottom: '10px' }}>
                <strong style={{ textTransform: 'capitalize' }}>{platform}:</strong>{' '}
                <code style={{ wordBreak: 'break-all' }}>{getFullCallbackURL(platform)}</code>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      <style jsx="true">{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default OAuthDemo; 
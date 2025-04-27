import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { handleOAuthRedirect, processOAuthData, getFullCallbackURL } from '../Utils/OAuthUtils';
import Swal from 'sweetalert2';
import axios from 'axios';
import API_BASE_URL from '../Utils/BaseUrl';
import { getAccessToken } from '../Utils/Auth';

/**
 * OAuth Callback Component
 * 
 * This component handles redirects from OAuth providers and processes
 * the callback parameters. It shows loading states, success/error messages
 * and can close itself when used in a popup context.
 */
const OAuthCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('Processing OAuth response...');
  const [data, setData] = useState(null);
  
  // Check if this component is loaded in a popup
  const isPopup = window.opener && window.opener !== window;
  
  useEffect(() => {
    const processCallback = async () => {
      try {
        // Parse URL parameters
        const callbackData = handleOAuthRedirect(location);
        const { platform, error, code, state, isError } = callbackData;
        
        if (isError) {
          setStatus('error');
          setMessage(`Authentication failed: ${error}`);
          
          if (isPopup) {
            // Send error message to opener
            window.opener.postMessage({
              type: 'OAUTH_ERROR',
              platform,
              error: { message: error }
            }, '*');
            
            // Close popup after a short delay
            setTimeout(() => window.close(), 1500);
          }
          return;
        }
        
        if (!platform || !code) {
          setStatus('error');
          setMessage('Missing required parameters (platform or code)');
          return;
        }
        
        // Get the PKCE code verifier from session storage if available
        let codeVerifier = null;
        if (state) {
          const storeKey = `pkce_verifier_${state}`;
          codeVerifier = sessionStorage.getItem(storeKey);
          if (codeVerifier) {
            console.log(`Retrieved code verifier for state ${state}, length: ${codeVerifier.length}`);
          }
        }
        
        // Real API call to exchange the code for access token
        setStatus('processing');
        setMessage(`Exchanging authorization code for ${platform}...`);
        
        try {
          // Prepare parameters for the callback
          const params = new URLSearchParams();
          params.append('code', code);
          params.append('state', state || '');
          
          if (codeVerifier) {
            params.append('code_verifier', codeVerifier);
          }
          
          // Add redirect_uri parameter
          const redirectUri = getFullCallbackURL(platform);
          params.append('redirect_uri', redirectUri);
            
          // Make the API call to exchange the code
          const token = getAccessToken();
          const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
          
          // Use the appropriate endpoint for the callback
          const callbackUrl = `${API_BASE_URL}/users/auth/callback/${platform}/?${params.toString()}`;
          console.log(`Making API call to: ${callbackUrl}`);
            
          const response = await axios.get(callbackUrl, { headers });
          
          // Process successful response
          const profileData = response.data;
          setStatus('success');
          setMessage(`Successfully authenticated with ${platform}`);
          
          const processedData = processOAuthData(platform, profileData);
          setData(processedData);
          
          if (isPopup) {
            // Send success message to opener
            window.opener.postMessage({
              type: 'OAUTH_SUCCESS',
              platform,
              data: processedData
            }, '*');
            
            // Close popup after a short delay
            setTimeout(() => window.close(), 1500);
          } else {
            // In non-popup mode, show a success message
            Swal.fire({
              position: 'top-start',
              icon: 'success',
              title: `Connected to ${platform}`,
              text: processedData.username ? `Connected as ${processedData.username}` : undefined,
              showConfirmButton: false,
              timer: 2000
            });
            
            // Redirect to home page or profile page
            setTimeout(() => navigate('/platform-connect'), 2000);
          }
        } catch (apiError) {
          console.error('API error:', apiError);
          setStatus('error');
          setMessage(apiError.response?.data?.error || 'Failed to exchange authorization code');
          
          if (isPopup) {
            // Send error message to opener
            window.opener.postMessage({
              type: 'OAUTH_ERROR',
              platform,
              error: { 
                message: apiError.response?.data?.error || 'Failed to exchange authorization code',
                details: apiError.response?.data
              }
            }, '*');
            
            // Close popup after a short delay
            setTimeout(() => window.close(), 1500);
          }
        }
      } catch (err) {
        console.error('Error processing OAuth callback:', err);
        setStatus('error');
        setMessage(err.message || 'An unexpected error occurred');
        
        if (isPopup) {
          // Send error message to opener
          window.opener.postMessage({
            type: 'OAUTH_ERROR',
            error: { message: err.message || 'An unexpected error occurred' }
          }, '*');
          
          // Close popup after a short delay
          setTimeout(() => window.close(), 1500);
        }
      }
    };
    
    processCallback();
  }, [location, navigate]);
  
  // Simple status display
  let statusColor = '#333';
  let statusIcon = '⏳';
  
  if (status === 'success') {
    statusColor = '#4caf50';
    statusIcon = '✅';
  } else if (status === 'error') {
    statusColor = '#f44336';
    statusIcon = '❌';
  } else if (status === 'processing') {
    statusColor = '#2196f3';
    statusIcon = '🔄';
  }
  
  return (
    <div style={{ 
      padding: '20px', 
      textAlign: 'center',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: isPopup ? '100vh' : '200px'
    }}>
      <div style={{ 
        fontSize: '24px', 
        marginBottom: '10px',
        color: statusColor 
      }}>
        {statusIcon}
      </div>
      
      <h3 style={{ margin: '0 0 10px 0', color: statusColor }}>
        {status === 'loading' ? 'Processing' : 
         status === 'processing' ? 'Connecting' :
         status === 'success' ? 'Success' : 'Error'}
      </h3>
      
      <p style={{ margin: '0 0 20px 0' }}>{message}</p>
      
      {data && status === 'success' && (
        <div style={{ 
          textAlign: 'left',
          padding: '15px',
          background: '#f7f7f7',
          borderRadius: '5px',
          width: '100%',
          maxWidth: '400px'
        }}>
          <div style={{ marginBottom: '10px' }}>
            <strong>Platform:</strong> {data.platform}
          </div>
          
          {data.username && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Username:</strong> {data.username}
            </div>
          )}
          
          {data.profileUrl && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Profile URL:</strong>{' '}
              <a href={data.profileUrl} target="_blank" rel="noopener noreferrer">
                {data.profileUrl}
              </a>
            </div>
          )}
        </div>
      )}
      
      {!isPopup && status !== 'loading' && status !== 'processing' && (
        <button
          onClick={() => navigate('/platform-connect')}
          style={{
            marginTop: '20px',
            padding: '8px 16px',
            background: '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Return to Platform Connect
        </button>
      )}
    </div>
  );
};

export default OAuthCallback; 
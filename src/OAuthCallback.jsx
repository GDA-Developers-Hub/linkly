import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { handleOAuthCallback } from './Utils/PlatformUtils';
import Swal from 'sweetalert2';

const OAuthCallback = () => {
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing your login...');
  const [details, setDetails] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    async function processOAuth() {
      try {
        // Get URL parameters
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');
        const error = params.get('error');
        const errorDescription = params.get('error_description');
        
        console.log(`OAuth callback received with parameters: Code exists: ${Boolean(code)}, State: ${state?.substring(0, 10)}...`);
        
        // Check for errors from OAuth provider
        if (error) {
          console.error('OAuth provider returned error:', error);
          const errorMsg = errorDescription || error;
          setStatus('error');
          setMessage(`Authentication failed: ${errorMsg}`);
          setDetails(`Error code: ${error}`);
          return;
        }
        
        // Validate required parameters
        if (!code || !state) {
          console.error('Missing required OAuth parameters', { code, state });
          setStatus('error');
          setMessage('Missing required authentication parameters');
          setDetails(`Code exists: ${Boolean(code)}, State exists: ${Boolean(state)}`);
          return;
        }
        
        // Extract platform from state parameter
        // Format is typically platform_randomString
        let platform = 'unknown';
        if (state.includes('_')) {
          platform = state.split('_')[0];
          console.log(`Extracted platform from state: ${platform}`);
        } else {
          // Try to determine from URL or other means
          console.log(`Unable to extract platform from state, checking URL path`);
          
          // Default to twitter if we can't determine (temporary workaround)
          platform = 'twitter';
          console.log(`Using default platform: ${platform}`);
        }
        
        // Check if code_verifier is in sessionStorage
        const storeKey = `pkce_verifier_${state}`;
        const codeVerifier = sessionStorage.getItem(storeKey);
        
        console.log(`Looking for code_verifier with key: ${storeKey}`);
        
        if (!codeVerifier) {
          console.warn(`No code_verifier found for state: ${state}`);
          setDetails(`No code_verifier found for state: ${state}. This might cause authorization to fail.`);
          
          // List all sessionStorage items to help debug
          const allKeys = [];
          for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            allKeys.push(key);
          }
          console.log('All sessionStorage keys:', allKeys);
        } else {
          console.log(`Found code_verifier for state ${state}, length: ${codeVerifier.length}`);
        }
        
        console.log(`Processing ${platform} OAuth callback with code: ${code.substring(0, 10)}...`);
        
        // Handle the OAuth callback
        const result = await handleOAuthCallback(platform, code, state);
        
        console.log(`OAuth callback successful:`, result);
        setStatus('success');
        setMessage(`Successfully connected to ${platform}!`);
        
        // Close this window with message to parent
        if (window.opener) {
          // Send a message to the opener window
          window.opener.postMessage({
            type: 'OAUTH_SUCCESS',
            platform: platform,
            data: result
          }, window.location.origin);
          
          // Close this popup window after a short delay
          setTimeout(() => {
            window.close();
          }, 1000);
        } else {
          // No opener, redirect back to platforms page
          setTimeout(() => {
            navigate('/platform-connect');
          }, 1500);
        }
      } catch (error) {
        console.error('Error during OAuth callback processing:', error);
        setStatus('error');
        setMessage(error.response?.data?.error || error.message || 'Authentication failed');
        
        // Show more detailed error information
        if (error.response?.data) {
          setDetails(JSON.stringify(error.response.data, null, 2));
        } else if (error.request) {
          setDetails('No response received from server');
        } else {
          setDetails(error.stack || 'Unknown error occurred');
        }
        
        if (window.opener) {
          // Send error to parent window
          window.opener.postMessage({
            type: 'OAUTH_ERROR',
            error: error.response?.data?.error || error.message || 'Authentication failed'
          }, window.location.origin);
          
          // Close this popup window after showing error briefly
          setTimeout(() => {
            window.close();
          }, 5000);  // Longer timeout to allow reading the error
        }
      }
    }
    
    processOAuth();
  }, [navigate, location]);
  
  // Render a simple loading/status screen
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow-md">
        {status === 'processing' && (
          <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mb-4"></div>
        )}
        {status === 'success' && (
          <div className="text-green-500 text-5xl mb-4">✓</div>
        )}
        {status === 'error' && (
          <div className="text-red-500 text-5xl mb-4">✗</div>
        )}
        
        <p className={`${status === 'error' ? 'text-red-600' : 'text-gray-700'} text-lg font-medium`}>
          {message}
        </p>
        
        {details && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-left text-xs overflow-auto max-h-40">
            <pre className="whitespace-pre-wrap break-all">{details}</pre>
          </div>
        )}
        
        <p className="text-sm text-gray-500 mt-4">
          {status === 'success' ? 'This window will close automatically.' : ''}
          {status === 'error' ? 'This window will close automatically soon. Check the console for more details.' : ''}
        </p>
      </div>
    </div>
  );
};

export default OAuthCallback; 
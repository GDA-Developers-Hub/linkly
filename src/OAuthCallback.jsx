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
          
          // Show error toast
          Swal.fire({
            title: 'Connection Failed',
            text: errorMsg,
            icon: 'error',
            confirmButtonText: 'Close'
          }).then(() => {
            window.close();
          });
          return;
        }
        
        // Validate required parameters
        if (!code || !state) {
          console.error('Missing required OAuth parameters', { code, state });
          setStatus('error');
          setMessage('Missing required authentication parameters');
          setDetails(`Code exists: ${Boolean(code)}, State exists: ${Boolean(state)}`);
          
          // Show error toast
          Swal.fire({
            title: 'Connection Failed',
            text: 'Missing required authentication parameters',
            icon: 'error',
            confirmButtonText: 'Close'
          }).then(() => {
            window.close();
          });
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
        
        // Send a message to the opener window if it exists
        if (window.opener) {
          window.opener.postMessage({
            type: 'OAUTH_SUCCESS',
            platform: platform,
            data: result
          }, window.location.origin);
        }
        
        // Platform-specific success messages
        let title = 'Account Connected!';
        let message = `Your ${platform} account has been successfully connected.`;
        
        if (platform === 'twitter') {
          title = 'Twitter Connected!';
          message = 'Your Twitter account has been successfully connected. You can now post tweets from Linkly!';
        } else if (platform === 'youtube') {
          title = 'YouTube Connected!';
          message = 'Your YouTube account has been successfully connected. You can now manage your videos from Linkly!';
        } else if (platform === 'facebook') {
          title = 'Facebook Connected!';
          message = 'Your Facebook account has been successfully connected. You can now manage your Facebook page from Linkly!';
        } else if (platform === 'instagram') {
          title = 'Instagram Connected!';
          message = 'Your Instagram account has been successfully connected. You can now post photos from Linkly!';
        } else if (platform === 'linkedin') {
          title = 'LinkedIn Connected!';
          message = 'Your LinkedIn account has been successfully connected. You can now post updates from Linkly!';
        }
        
        // Show success toast with options based on whether we're in a popup
        if (window.opener) {
          // If in a popup, show auto-closing message
          Swal.fire({
            title: title,
            text: message,
            icon: 'success',
            timer: 2000,
            showConfirmButton: false
          }).then(() => {
            window.close();
          });
        } else {
          // If not in a popup (direct navigation), show regular options
          Swal.fire({
            title: title,
            text: message,
            icon: 'success',
            showCancelButton: true,
            confirmButtonText: 'Go to Dashboard',
            cancelButtonText: 'Close'
          }).then((result) => {
            if (result.isConfirmed) {
              navigate('/dashboard');
            }
          });
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
        
        // Show error toast
        Swal.fire({
          title: 'Connection Failed',
          text: error.response?.data?.error || error.message || 'Authentication failed',
          icon: 'error',
          confirmButtonText: 'Close'
        }).then(() => {
          window.close();
        });
        
        if (window.opener) {
          // Send error to parent window
          window.opener.postMessage({
            type: 'OAUTH_ERROR',
            error: error.response?.data?.error || error.message || 'Authentication failed'
          }, window.location.origin);
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
        
        {status === 'success' && (
          <div className="mt-6">
            <button
              onClick={() => {
                if (window.opener) {
                  window.opener.location.href = '/dashboard';
                  window.close();
                } else {
                  navigate('/dashboard');
                }
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors mr-3"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => window.close()}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
            >
              Close Window
            </button>
          </div>
        )}
        
        {status === 'error' && (
          <button
            onClick={() => window.close()}
            className="mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Close Window
          </button>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;
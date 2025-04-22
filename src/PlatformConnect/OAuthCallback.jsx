import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { handleOAuthCallback } from '../Utils/PlatformUtils';
import Swal from 'sweetalert2';

const OAuthCallback = () => {
  const location = useLocation();
  const [status, setStatus] = useState('processing');

  useEffect(() => {
    const processOAuthCallback = async () => {
      try {
        // Get query parameters from URL
        const searchParams = new URLSearchParams(location.search);
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const platform = getPlatformFromState(state);
        
        if (!code || !platform) {
          setStatus('error');
          Swal.fire({
            title: 'Connection Failed',
            text: 'Missing authorization parameters. Please try again.',
            icon: 'error',
            confirmButtonText: 'Close'
          }).then(() => {
            window.close();
          });
          return;
        }
        
        // Process the callback with the backend
        await handleOAuthCallback(platform, code, state);
        
        setStatus('success');
        Swal.fire({
          title: 'Connection Successful',
          text: 'Your account has been connected successfully!',
          icon: 'success',
          timer: 2000,
          showConfirmButton: false
        }).then(() => {
          window.close();
        });
      } catch (error) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        Swal.fire({
          title: 'Connection Failed',
          text: error.response?.data?.message || error.message || 'Failed to complete authentication. Please try again.',
          icon: 'error',
          confirmButtonText: 'Close'
        }).then(() => {
          window.close();
        });
      }
    };
    
    processOAuthCallback();
  }, [location]);
  
  // Extract platform from state parameter
  const getPlatformFromState = (state) => {
    if (!state) return null;
    
    // Try to extract platform from state
    // Different platforms might format their state differently
    // This is a simple approach - you might need to adjust based on your backend implementation
    const platforms = ['twitter', 'facebook', 'instagram', 'linkedin', 'youtube', 'tiktok', 'telegram'];
    
    for (const platform of platforms) {
      if (state.includes(platform)) {
        return platform;
      }
    }
    
    // If no platform found in state, check the URL path
    const path = location.pathname;
    for (const platform of platforms) {
      if (path.includes(platform)) {
        return platform;
      }
    }
    
    return null;
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="text-center p-8 max-w-md">
        <div className="mb-6">
          {status === 'processing' && (
            <div className="inline-block animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full"></div>
          )}
          {status === 'success' && (
            <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-green-100 text-green-600 text-xl">
              ✓
            </div>
          )}
          {status === 'error' && (
            <div className="inline-flex items-center justify-center h-12 w-12 rounded-full bg-red-100 text-red-600 text-xl">
              ✗
            </div>
          )}
        </div>
        
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          {status === 'processing' && 'Connecting your account...'}
          {status === 'success' && 'Account Connected!'}
          {status === 'error' && 'Connection Failed'}
        </h1>
        
        <p className="text-gray-600 mb-6">
          {status === 'processing' && 'Please wait while we complete the authorization process.'}
          {status === 'success' && 'You can now close this window and return to Linkly.'}
          {status === 'error' && 'We encountered an error connecting your account. Please try again.'}
        </p>
        
        {status !== 'processing' && (
          <button 
            onClick={() => window.close()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close Window
          </button>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback; 
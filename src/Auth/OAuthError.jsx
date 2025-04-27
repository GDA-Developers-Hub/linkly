import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

const OAuthError = () => {
  const [error, setError] = useState('');
  const [platform, setPlatform] = useState('');
  const [details, setDetails] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Parse URL parameters
    const searchParams = new URLSearchParams(location.search);
    const errorParam = searchParams.get('error');
    const platformParam = searchParams.get('platform');
    const detailsParam = searchParams.get('details');
    
    console.log('OAuth Error - Platform:', platformParam);
    console.log('OAuth Error - Error:', errorParam);
    console.log('OAuth Error - Details:', detailsParam);
    
    if (errorParam) {
      setError(errorParam);
    }
    
    if (platformParam) {
      setPlatform(platformParam);
    }
    
    if (detailsParam) {
      setDetails(detailsParam);
    }
    
    // Notify parent window if this is in popup mode
    if (window.opener) {
      try {
        window.opener.postMessage({
          type: 'OAUTH_ERROR',
          platform: platformParam,
          error: errorParam,
          details: detailsParam
        }, '*');
        console.log('Sent error message to parent window');
      } catch (err) {
        console.error('Failed to communicate with parent window:', err);
      }
    }
    
    // Show error notification
    Swal.fire({
      title: 'Connection Failed',
      text: errorParam || 'An error occurred during the authentication process.',
      icon: 'error',
      confirmButtonText: 'Try Again',
      showCancelButton: true,
      cancelButtonText: 'Cancel',
      position: 'top-start', // Position on left side
      showClass: {
        popup: 'animate__animated animate__fadeInLeft'
      },
    }).then((result) => {
      if (result.isConfirmed) {
        // Redirect back to connect page
        navigate('/platform-connect');
      } else {
        // Go to dashboard
        navigate('/dashboard');
      }
    });
  }, [location, navigate]);

  // Parse and display a more user-friendly error message
  const getErrorMessage = () => {
    if (!error) return 'An unknown error occurred during authentication.';
    
    // Handle common OAuth error messages
    if (error.includes('expired')) {
      return 'Your authentication session expired. Please try connecting again.';
    }
    
    if (error.includes('invalid')) {
      return 'Invalid authentication data. Please try again.';
    }
    
    if (error.includes('permissions') || error.includes('scope')) {
      return 'Insufficient permissions. Please allow all requested permissions.';
    }
    
    if (error.includes('code verifier') || error.includes('PKCE')) {
      return 'Security verification failed. Please try again with a new session.';
    }
    
    if (error.includes('state parameter')) {
      return 'Authentication session expired or was invalid. Please try again.';
    }

    // Return the original error if no specific handling
    return error;
  };

  // Helper function to provide troubleshooting steps
  const getTroubleshootingSteps = () => {
    const steps = [];
    
    // General step for all errors
    steps.push('Try logging out and logging back in to refresh your session.');
    
    // Platform-specific steps
    if (platform === 'linkedin') {
      steps.push('Make sure you are logged into LinkedIn in your browser.');
      steps.push('Try clearing your browser cookies and cache.');
    } else if (platform === 'twitter') {
      steps.push('Ensure your Twitter account has the necessary permissions.');
      steps.push('Try using a different browser if the issue persists.');
    }
    
    // Error-specific steps
    if (error.includes('expired') || error.includes('state parameter')) {
      steps.push('Your session may have timed out. Please try the connection again quickly after initiating it.');
    }
    
    if (error.includes('permissions') || error.includes('scope')) {
      steps.push('When authorizing, make sure to accept all requested permissions.');
    }
    
    return steps;
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow-md">
        <div className="text-red-500 text-5xl mb-4">✗</div>
        <h1 className="text-2xl font-bold mb-4">Connection Failed</h1>
        <p className="text-gray-700 mb-6">
          {platform 
            ? `We couldn't connect your ${platform} account.` 
            : 'We couldn\'t complete the connection.'}
        </p>
        
        <div className="mt-2 p-3 bg-red-50 rounded-lg text-left">
          <p className="text-red-800 font-medium">Error Details:</p>
          <p className="text-red-700">{getErrorMessage()}</p>
          {details && (
            <p className="text-red-600 text-sm mt-2 italic">{details}</p>
          )}
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 rounded-lg text-left">
          <p className="text-blue-800 font-medium">Troubleshooting Steps:</p>
          <ul className="text-blue-700 list-disc pl-5">
            {getTroubleshootingSteps().map((step, index) => (
              <li key={index} className="mt-1">{step}</li>
            ))}
          </ul>
        </div>
        
        <div className="mt-6">
          <button
            onClick={() => navigate('/platform-connect')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors mr-3"
          >
            Try Again
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default OAuthError; 
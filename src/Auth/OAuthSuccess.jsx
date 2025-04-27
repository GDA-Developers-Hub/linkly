import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

const OAuthSuccess = () => {
  const [platform, setPlatform] = useState('');
  const [userData, setUserData] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Parse URL parameters
    const searchParams = new URLSearchParams(location.search);
    const platformParam = searchParams.get('platform');
    const userData = location.state?.userData || {};
    
    console.log('OAuth Success - Platform:', platformParam);
    console.log('OAuth Success - User Data:', userData);
    
    // Store data from the response
    if (platformParam) {
      setPlatform(platformParam);
      setUserData(userData);
      
      // Different messages based on platform
      let title, message;
      
      switch (platformParam.toLowerCase()) {
        case 'linkedin':
          title = 'LinkedIn Connected!';
          message = 'Your LinkedIn account has been successfully connected. You can now post updates and share content through Linkly.';
          break;
        case 'twitter':
          title = 'Twitter Connected!';
          message = 'Your Twitter account has been successfully connected. You can now post tweets from Linkly!';
          break;
        case 'facebook':
          title = 'Facebook Connected!';
          message = 'Your Facebook account has been successfully connected. You can now manage your Facebook page from Linkly!';
          break;
        case 'instagram':
          title = 'Instagram Connected!';
          message = 'Your Instagram account has been successfully connected. You can now post photos from Linkly!';
          break;
        default:
          title = 'Account Connected!';
          message = `Your ${platformParam} account has been successfully connected to Linkly.`;
      }
      
      // Notify parent window if this is in popup mode
      if (window.opener) {
        try {
          window.opener.postMessage({
            type: 'OAUTH_SUCCESS',
            platform: platformParam,
            data: userData
          }, '*');
          console.log('Sent success message to parent window');
        } catch (err) {
          console.error('Failed to communicate with parent window:', err);
        }
      }
      
      // Show success notification
      Swal.fire({
        title: title,
        text: message,
        icon: 'success',
        confirmButtonText: 'Go to Dashboard',
        position: 'top-start', // Position on left side
        showClass: {
          popup: 'animate__animated animate__fadeInLeft'
        },
      }).then((result) => {
        if (result.isConfirmed) {
          navigate('/dashboard');
        }
      });
    } else {
      // If no platform specified, show generic success
      Swal.fire({
        title: 'Connection Successful',
        text: 'Your account has been successfully connected to Linkly.',
        icon: 'success',
        confirmButtonText: 'Continue',
        position: 'top-start', // Position on left side
        showClass: {
          popup: 'animate__animated animate__fadeInLeft'
        },
      }).then((result) => {
        if (result.isConfirmed) {
          navigate('/dashboard');
        }
      });
    }
  }, [location, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow-md">
        <div className="text-green-500 text-5xl mb-4">✓</div>
        <h1 className="text-2xl font-bold mb-4">Connection Successful!</h1>
        <p className="text-gray-700 mb-6">
          {platform 
            ? `Your ${platform} account has been successfully connected to Linkly.` 
            : 'Your account has been successfully connected to Linkly.'}
        </p>
        
        {userData && userData.profile && (
          <div className="mt-4 p-3 bg-gray-50 rounded text-left">
            <h3 className="font-semibold mb-2">Connected Account:</h3>
            {userData.profile.name && <p>Name: {userData.profile.name}</p>}
            {userData.profile.email && <p>Email: {userData.profile.email}</p>}
            {userData.profile.username && <p>Username: {userData.profile.username}</p>}
          </div>
        )}
        
        <div className="mt-6">
          <button
            onClick={() => navigate('/platform-connect')}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors mr-3"
          >
            Connect More Platforms
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default OAuthSuccess; 
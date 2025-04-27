import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

const SocialAuthSuccess = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const processAuth = () => {
      try {
        // Parse query parameters
        const params = new URLSearchParams(location.search);
        const platform = params.get('platform');
        const error = params.get('error');
        const message = params.get('message');
        
        console.log('Social auth redirect params:', { platform, error, message });
        
        if (error) {
          // Show error message
          Swal.fire({
            title: 'Connection Failed',
            text: message || `Failed to connect ${platform} account.`,
            icon: 'error',
            confirmButtonText: 'Ok'
          }).then(() => {
            navigate('/platform-connect');
          });
          return;
        }
        
        // Get profile information
        const profile = {
          name: params.get('name') || '',
          username: params.get('username') || '',
          email: params.get('email') || '',
          picture: params.get('picture') || ''
        };
        
        // Show success message
        let title = 'Account Connected!';
        let successMessage = `Your ${platform} account has been successfully connected.`;
        
        // Platform-specific messages
        if (platform === 'facebook') {
          title = 'Facebook Connected!';
          successMessage = 'Your Facebook account has been successfully connected. You can now post updates from Linkly!';
        } else if (platform === 'instagram') {
          title = 'Instagram Connected!';
          successMessage = 'Your Instagram account has been successfully connected. You can now share photos from Linkly!';
        }
        
        Swal.fire({
          title: title,
          text: successMessage,
          icon: 'success',
          confirmButtonText: 'Continue'
        }).then(() => {
          navigate('/platform-connect');
        });
        
      } catch (error) {
        console.error('Error processing social auth success:', error);
        
        Swal.fire({
          title: 'Connection Error',
          text: 'An unexpected error occurred while processing your social login.',
          icon: 'error',
          confirmButtonText: 'Ok'
        }).then(() => {
          navigate('/platform-connect');
        });
      } finally {
        setIsProcessing(false);
      }
    };
    
    processAuth();
  }, [location, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="text-center max-w-md p-8 bg-white rounded-lg shadow-md">
        {isProcessing ? (
          <>
            <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mb-4"></div>
            <p className="text-lg font-medium text-gray-700">Processing authentication...</p>
          </>
        ) : (
          <p className="text-lg font-medium text-gray-700">Redirecting you...</p>
        )}
      </div>
    </div>
  );
};

export default SocialAuthSuccess; 
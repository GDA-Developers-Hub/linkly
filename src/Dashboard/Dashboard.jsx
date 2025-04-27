import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getConnectedPlatforms } from '../Utils/PlatformUtils';
import Swal from 'sweetalert2';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    // Check if user has connected platforms on component mount
    checkConnectedPlatforms();
  }, []);

  const checkConnectedPlatforms = async () => {
    try {
      setLoading(true);
      console.log('Dashboard: Checking for connected platforms...');
      
      // Fetch connected platforms from API
      const platforms = await getConnectedPlatforms();
      console.log('Dashboard: Connected platforms received:', JSON.stringify(platforms));
      setConnectedPlatforms(platforms);
      
      // If no platforms are connected, redirect to platform-connect
      if (!platforms || platforms.length === 0) {
        console.log('Dashboard: No connected platforms found, redirecting to platform-connect');
        setRedirecting(true);
        
        // Show notification about redirection
        Swal.fire({
          title: 'Account Connection Required',
          text: 'You need to connect at least one social media account to use the dashboard',
          icon: 'info',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000,
          timerProgressBar: true
        });
        
        // Navigate to platform connection page with required flag
        navigate('/platform-connect?required=true');
      } else {
        console.log(`Dashboard: ${platforms.length} connected platforms found, showing dashboard`);
      }
    } catch (error) {
      console.error('Dashboard: Error checking connected platforms:', error);
      
      // For persistent errors, you may want to still allow access to dashboard
      // Or implement a retry mechanism
    } finally {
      setLoading(false);
    }
  };

  // Show loading state while checking platforms
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Show a placeholder if redirecting (this will be very brief)
  if (redirecting) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600">Redirecting to platform connection...</p>
        </div>
      </div>
    );
  }

  // If we have connected platforms, show the actual dashboard
  return (
    <div className="p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Your Dashboard</h1>
        <p className="text-gray-600">
          Welcome to Linkly! You have {connectedPlatforms.length} connected {connectedPlatforms.length === 1 ? 'account' : 'accounts'}.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Connected platforms summary */}
        <div className="bg-white shadow rounded-lg p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Connected Platforms</h2>
          <ul className="space-y-3">
            {connectedPlatforms.map((platform, index) => (
              <li key={index} className="flex items-center space-x-3">
                <span className="text-xl">{getPlatformIcon(platform.platform)}</span>
                <span className="font-medium">{getPlatformName(platform.platform)}</span>
                {platform.account_type === 'business' && (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                    Business
                  </span>
                )}
              </li>
            ))}
          </ul>
          <button 
            onClick={() => navigate('/platform-connect')}
            className="mt-4 w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Manage Connections
          </button>
        </div>
        
        {/* Dashboard widgets would go here */}
        <div className="bg-white shadow rounded-lg p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Recent Analytics</h2>
          <p className="text-gray-500">Your engagement metrics will appear here.</p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6 border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Upcoming Posts</h2>
          <p className="text-gray-500">Your scheduled content will appear here.</p>
        </div>
      </div>
    </div>
  );
};

// Helper function to get platform icon
const getPlatformIcon = (platformId) => {
  const icons = {
    twitter: '🐦',
    facebook: '📘',
    instagram: '📷',
    linkedin: '💼',
    youtube: '📹',
    tiktok: '🎵',
    telegram: '📱',
  };
  return icons[platformId] || '📱';
};

// Helper function to get platform name
const getPlatformName = (platformId) => {
  const names = {
    twitter: 'Twitter',
    facebook: 'Facebook',
    instagram: 'Instagram',
    linkedin: 'LinkedIn',
    youtube: 'YouTube',
    tiktok: 'TikTok',
    telegram: 'Telegram',
  };
  return names[platformId] || platformId;
};

export default Dashboard; 
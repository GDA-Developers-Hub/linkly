import React, { useState } from 'react';
import axios from 'axios';
import { getAccessToken } from '../Utils/Auth';
import API_BASE_URL from '../Utils/BaseUrl';

const PlatformCredentialsModal = ({ isOpen, onClose, platform, onConnect }) => {
  const [credentials, setCredentials] = useState({
    clientId: '',
    clientSecret: '',
    redirectUri: `${window.location.origin}/oauth-callback`
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');



  

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 1. Save the credentials to the database
      const token = getAccessToken();
      
      await axios.post(`${API_BASE_URL}/users/platform-credentials/`, {
        platform: platform.id,
        client_id: credentials.clientId,
        client_secret: credentials.clientSecret,
        redirect_uri: credentials.redirectUri
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // 2. Proceed with the connection process using the custom credentials
      onConnect(platform, true);
      onClose();
    } catch (error) {
      console.error('Error saving credentials:', error);
      setError(error.response?.data?.detail || 'Failed to save credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-xl font-semibold text-gray-800">
            Connect {platform?.name} with Your Own Credentials
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-6">
          <p className="text-gray-600 mb-4">
            Enter your developer credentials for {platform?.name} to use your own registered application.
          </p>
          
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
              <p className="text-red-700">{error}</p>
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="clientId">
                Client ID
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="clientId"
                name="clientId"
                type="text"
                value={credentials.clientId}
                onChange={handleChange}
                required
                placeholder={`Your ${platform?.name} Client ID`}
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="clientSecret">
                Client Secret
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="clientSecret"
                name="clientSecret"
                type="password"
                value={credentials.clientSecret}
                onChange={handleChange}
                required
                placeholder={`Your ${platform?.name} Client Secret`}
              />
            </div>
            
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="redirectUri">
                Redirect URI
              </label>
              <input
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                id="redirectUri"
                name="redirectUri"
                type="text"
                value={credentials.redirectUri}
                onChange={handleChange}
                required
                readOnly
              />
              <p className="text-xs text-gray-500 mt-1">
                Use this URI in your developer console when registering your app.
              </p>
            </div>
            
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className={`px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </span>
                ) : (
                  'Connect'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PlatformCredentialsModal; 
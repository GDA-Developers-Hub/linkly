/**
 * OAuth Debugging Utilities
 * 
 * This file contains utilities for diagnosing OAuth-related issues
 * in the Linkly application.
 */

import API_BASE_URL from './BaseUrl';
import { API_ENDPOINTS } from '../constants/endpoints';

/**
 * Tests the availability of various OAuth endpoints
 * @param {string} platform - The platform to test (e.g., 'instagram', 'linkedin')
 * @returns {Promise<object>} - Results of the availability tests
 */
export const testOAuthEndpoints = async (platform) => {
  const results = {
    platform,
    timestamp: new Date().toISOString(),
    endpoints: {}
  };
  
  // Get platform-specific endpoint
  const platformUppercase = platform.toUpperCase();
  const callbackEndpoint = API_ENDPOINTS[`${platformUppercase}_CALLBACK`] || API_ENDPOINTS.OAUTH_CALLBACK;
  
  // List of endpoints to test
  const endpointsToTest = [
    { name: 'direct_login', url: `${API_BASE_URL}/users/auth/login/${platform}/` },
    { name: 'callback', url: `${API_BASE_URL}${callbackEndpoint}` },
    { name: 'oauth_init', url: `${API_BASE_URL}/users/auth/init/?platform=${platform}` }
  ];
  
  // Test each endpoint
  for (const endpoint of endpointsToTest) {
    try {
      console.log(`Testing endpoint: ${endpoint.url}`);
      
      // Just make a HEAD request to see if endpoint exists
      const response = await fetch(endpoint.url, { 
        method: 'HEAD',
        mode: 'no-cors' // To prevent CORS issues during testing
      });
      
      results.endpoints[endpoint.name] = {
        url: endpoint.url,
        status: 'reachable' // With no-cors we can't get the actual status
      };
    } catch (error) {
      results.endpoints[endpoint.name] = {
        url: endpoint.url,
        status: 'error',
        error: error.message
      };
    }
  }
  
  console.log('OAuth endpoint test results:', results);
  return results;
};

/**
 * Logs detailed information about the current OAuth configuration
 * @param {string} platform - The platform to check
 * @returns {object} - Configuration details
 */
export const logOAuthConfig = (platform) => {
  const platformUppercase = platform.toUpperCase();
  const config = {
    platform,
    base_url: API_BASE_URL,
    endpoints: {
      callback: API_ENDPOINTS[`${platformUppercase}_CALLBACK`] || API_ENDPOINTS.OAUTH_CALLBACK,
      authorize: API_ENDPOINTS.OAUTH_AUTHORIZE,
      direct_login: `/users/auth/login/${platform}/`
    },
    full_urls: {
      callback: `${API_BASE_URL}${API_ENDPOINTS[`${platformUppercase}_CALLBACK`] || API_ENDPOINTS.OAUTH_CALLBACK}`,
      authorize: `${API_BASE_URL}${API_ENDPOINTS.OAUTH_AUTHORIZE}`,
      direct_login: `${API_BASE_URL}/users/auth/login/${platform}/`
    }
  };
  
  console.log(`OAuth configuration for ${platform}:`, config);
  return config;
};

export default {
  testOAuthEndpoints,
  logOAuthConfig
}; 
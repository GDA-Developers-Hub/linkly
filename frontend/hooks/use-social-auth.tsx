'use client';

import { useState, useEffect } from 'react';
import { getAPI } from '@/lib/api';
import { AUTH } from '@/lib/constants';
import { socialPlatformsApi } from '@/services/social-platforms-api';
import { getPendingOAuthConnections } from '@/lib/auth-utils';

/**
 * Hook to manage authentication state for social platforms
 * @returns Object containing authentication state and functions
 */
export function useSocialAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [user, setUser] = useState<any>(null);
  
  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsLoading(true);
        const api = getAPI();
        const isLoggedIn = api.isAuthenticated();
        setIsAuthenticated(isLoggedIn);
        
        if (isLoggedIn) {
          try {
            // Try to fetch user profile if available
            const accounts = await socialPlatformsApi.getAccounts();
            if (Array.isArray(accounts) && accounts.length > 0) {
              // Use the first account's details for the user
              const account = accounts[0];
              setUser({
                id: account.id,
                name: account.account_name || (account as any).name || 'User',
                profile_pic: account.profile_picture_url || ''
              });
            }
          } catch (error) {
            console.error('Error fetching user data:', error);
          }
          
          // Check for pending OAuth connections
          const pendingConnections = getPendingOAuthConnections();
          if (pendingConnections.length > 0) {
            console.log('Found pending OAuth connections:', pendingConnections);
          }
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
    
    // Add event listener for auth changes (e.g., token expiry)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === AUTH.TOKEN_KEY) {
        const hasToken = !!e.newValue;
        setIsAuthenticated(hasToken);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);
  
  // Function to log out
  const logout = () => {
    localStorage.removeItem(AUTH.TOKEN_KEY);
    localStorage.removeItem(AUTH.REFRESH_TOKEN_KEY);
    setIsAuthenticated(false);
    setUser(null);
  };
  
  return {
    isAuthenticated,
    isLoading,
    user,
    logout,
  };
}

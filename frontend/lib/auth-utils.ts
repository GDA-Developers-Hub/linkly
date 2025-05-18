/**
 * Authentication utilities for Linkly
 * This module provides utilities for authentication-related tasks
 * including handling pending OAuth connections after login
 */

import { useState, useEffect } from 'react';
import { socialPlatformsApi } from '@/services/social-platforms-api';
import { useToast } from '@/components/ui/use-toast';
import { getAPI } from '@/lib/api';
import { AUTH } from './constants';

/**
 * NOTE: The useSocialAuth hook has been moved to frontend/hooks/use-social-auth.tsx
 * Import it from there instead.
 */

/**
 * Check for pending OAuth connections in local storage
 * @returns Array of platform names that have pending connections
 */
export function getPendingOAuthConnections(): string[] {
  if (typeof window === 'undefined') return [];
  
  const pendingConnections: string[] = [];
  
  // Check all localStorage items for pending OAuth connections
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('pending_oauth_')) {
      const platform = key.replace('pending_oauth_', '');
      pendingConnections.push(platform);
    }
  }
  
  return pendingConnections;
  
}

/**
 * Complete all pending OAuth connections stored in localStorage
 * This should be called after successful login
 * @returns Promise that resolves with the connected accounts
 */
export async function completePendingOAuthConnections() {
  const pendingConnections = getPendingOAuthConnections();
  const connectedAccounts = [];
  
  for (const platform of pendingConnections) {
    try {
      // Get the code_id from localStorage
      const codeId = localStorage.getItem(`pending_oauth_${platform}`);
      if (!codeId) continue;
      
      console.log(`Completing pending ${platform} connection with code_id: ${codeId.substring(0, 8)}...`);
      
      // Complete the OAuth flow using our AllAuth integration
      const result = await socialPlatformsApi.completeOAuthAllAuth(platform, codeId);
      
      if (result?.success && result?.account) {
        connectedAccounts.push(result.account);
      }
      
      // Remove the pending connection from localStorage
      localStorage.removeItem(`pending_oauth_${platform}`);
      
    } catch (error) {
      console.error(`Error completing ${platform} connection:`, error);
    }
  }
  
  return connectedAccounts;
}

/**
 * This hook can be used to automatically check for and complete
 * pending OAuth connections after login
 */
export function useCompletePendingOAuthConnections() {
  const { toast } = useToast();
  
  /**
   * Check and complete pending OAuth connections
   * Call this function after a successful login
   */
  const checkAndCompletePendingConnections = async () => {
    const pendingConnections = getPendingOAuthConnections();
    
    if (pendingConnections.length === 0) return;
    
    toast({
      title: "Completing social connections...",
      description: `Found ${pendingConnections.length} pending social platform connection(s)`,
      duration: 5000,
    });
    
    try {
      const connectedAccounts = await completePendingOAuthConnections();
      
      if (connectedAccounts.length > 0) {
        toast({
          title: "Social accounts connected!",
          description: `Successfully connected ${connectedAccounts.length} account(s)`,
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Error completing pending connections:', error);
      toast({
        title: "Connection Error",
        description: "Failed to complete pending social connections",
        variant: "destructive",
        duration: 5000,
      });
    }
  };
  
  return { checkAndCompletePendingConnections };
}

/**
 * Store OAuth data for later completion
 * @param platform Platform name (e.g., 'facebook', 'linkedin')
 * @param codeId Code ID from Redis
 */
export function storePendingOAuthConnection(platform: string, codeId: string): void {
  if (typeof window !== 'undefined' && platform && codeId) {
    localStorage.setItem(`pending_oauth_${platform}`, codeId);
    console.log(`Stored pending OAuth connection for ${platform} with code ID: ${codeId.substring(0, 8)}...`);
  }
}

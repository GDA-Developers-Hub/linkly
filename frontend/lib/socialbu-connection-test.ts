import { toast } from "@/components/ui/use-toast"
import { type Account } from "@/lib/socials-api"

// Interface for connection test result
export interface ConnectionTestResult {
  status: 'connected' | 'auth_error' | 'error';
  message: string;
  account_details?: Account;
  platform?: string;
  accounts?: Account[];
  local_account_info?: any;
  error?: string;
}

/**
 * Tests the connection to API
 * @param accountId Optional account ID to test specific account connection
 * @returns ConnectionTestResult object with status and details
 */
export async function testSocialBuConnection(accountId?: number): Promise<ConnectionTestResult> {
  try {
    // Create mock accounts
    const mockAccounts = [
      { id: 1, name: "Facebook Page", platform: "facebook", account_type: "page" },
      { id: 2, name: "Instagram", platform: "instagram", account_type: "profile" },
      { id: 3, name: "Twitter", platform: "twitter", account_type: "profile" }
    ];
    
    // Call the mock endpoint
    let endpoint = "test_connection";
    if (accountId) {
      endpoint += `?account_id=${accountId}`;
    }
    
    // Simulate a test connection
    const mockResult: ConnectionTestResult = {
      status: 'connected',
      message: 'Connection successful',
      accounts: mockAccounts
    };
    
    // If account ID is provided, check if it exists in our mock data
    if (accountId) {
      const account = mockAccounts.find(acc => acc.id === accountId);
      if (account) {
        mockResult.account_details = account;
        mockResult.platform = account.platform;
      } else {
        mockResult.status = 'error';
        mockResult.message = `Account with ID ${accountId} not found`;
      }
    }
    
    console.log('[Mock] Connection test result:', mockResult);
    
    return mockResult;
  } catch (error) {
    console.error('[Mock] Connection test failed:', error);
    
    // Format the error response
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error during connection test',
      error: String(error)
    };
  }
}

/**
 * Test connection to API and show toast with result
 * @param accountId Optional account ID to test
 * @returns The test result
 */
export async function testAndNotify(accountId?: number): Promise<ConnectionTestResult> {
  try {
    const result = await testSocialBuConnection(accountId);
    
    if (result.status === 'connected') {
      toast({
        title: "Connection successful",
        description: result.message,
        variant: "default",
      });
    } else if (result.status === 'auth_error') {
      toast({
        title: "Authentication error",
        description: "Your authentication has expired. Please reconnect your account.",
        variant: "destructive",
      });
    } else {
      toast({
        title: "Connection error",
        description: result.message,
        variant: "destructive",
      });
    }
    
    return result;
  } catch (error) {
    toast({
      title: "Connection test failed",
      description: error instanceof Error ? error.message : "Unknown error",
      variant: "destructive",
    });
    
    return {
      status: 'error',
      message: 'Connection test failed',
      error: String(error)
    };
  }
}

/**
 * Diagnoses issues with account ID mismatch
 * Checks if the account exists and if not, suggests connection status
 * @param accountId The account ID to check
 */
export async function diagnoseAccountIdIssue(accountId: number): Promise<string> {
  try {
    const result = await testSocialBuConnection(accountId);
    
    if (result.status === 'connected') {
      return `Account ${accountId} is valid and connected. Platform: ${result.platform || 'Unknown'}`;
    } else if (result.status === 'auth_error') {
      return `Your authentication has expired. Please reconnect your account.`;
    } else if (result.accounts && result.accounts.length > 0) {
      // List available accounts to help user identify the correct one
      const accountsList = result.accounts
        .map(acc => `- ${acc.name} (ID: ${acc.id}, Platform: ${acc.platform || 'Unknown'})`)
        .join('\n');
        
      return `Account ID ${accountId} was not found. Available accounts:\n${accountsList}`;
    } else if (result.local_account_info) {
      return `Account ${accountId} exists in local database but not connected. 
              Local info: ${result.local_account_info.platform} account "${result.local_account_info.account_name}" 
              Status: ${result.local_account_info.status}`;
    } else {
      return `Account ID ${accountId} not found. Please verify the ID or reconnect your social media account.`;
    }
  } catch (error) {
    return `Error diagnosing account issue: ${error instanceof Error ? error.message : String(error)}`;
  }
}

// https://twitter.com/i/oauth2/authorize?client_id=WFZUOThVQmpjS1E4ZldpRTNkQm86MTpjaQ&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fsocial_platforms%2Foauth%2Fcallback%2Ftwitter%2F&response_type=code&scope=tweet.read+tweet.write+users.read+offline.access&state=uYA8PnCCqshzCFt1v7ssX-gnYHJ6f9Bo9aY_8Hp6x8o&code_challenge=e2E9YThkfZWrU0oJKCgzFhBPhHKrFQi8rreaA1gDaIw&code_challenge_method=S256

// https://twitter.com/i/oauth2/authorize?client_id=WFZUOThVQmpjS1E4ZldpRTNkQm86MTpjaQ&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fsocial_platforms%2Foauth%2Fcallback%2Ftwitter%2F&response_type=code&scope=tweet.read+tweet.write+users.read+offline.access&state=uYA8PnCCqshzCFt1v7ssX-gnYHJ6f9Bo9aY_8Hp6x8o&code_challenge=e2E9YThkfZWrU0oJKCgzFhBPhHKrFQi8rreaA1gDaIw&code_challenge_method=S256

// http://localhost:8000/api/social_platforms/oauth/callback/twitter/?state=uYA8PnCCqshzCFt1v7ssX-gnYHJ6f9Bo9aY_8Hp6x8o&code=XzRkR3BUWkpaQ1VRT2hwblJIMnJSbGRwRF9zNTBNZXEzTWFqWmZ1RGpXdi1FOjE3NDcxMzA3MzQ0NDI6MToxOmFjOjE
"use client"

import { ConnectionTester } from "@/components/socialbu/connection-tester"
import { PageHeader } from "@/components/ui/page-header"
import { Separator } from "@/components/ui/separator"

export default function ConnectionTestPage() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <PageHeader
        heading="SocialBu Connection Tester"
        subheading="Diagnose and fix issues with your SocialBu API connection and social media accounts"
      />
      
      <Separator />
      
      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Connection Test Tool</h3>
          <p className="text-muted-foreground">
            Use this tool to verify your SocialBu API connection is working properly and to diagnose issues with specific account IDs.
          </p>
          <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
            <li>Test your API connection to see if your authentication token is valid</li>
            <li>Verify specific account IDs exist in SocialBu</li>
            <li>Diagnose why specific posts might be failing</li>
            <li>Find available accounts when you're not sure which ID to use</li>
          </ul>
        </div>
        
        <div>
          <ConnectionTester />
        </div>
      </div>
      
      <Separator className="my-8" />
      
      <div className="space-y-4">
        <h3 className="text-lg font-medium">Common Issues</h3>
        
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border p-4 space-y-2">
            <h4 className="font-medium">Authentication Errors</h4>
            <p className="text-sm text-muted-foreground">
              If you see authentication errors, your SocialBu token has likely expired. Try reconnecting your account
              by visiting the Accounts page and clicking "Connect" for the platform you want to use.
            </p>
          </div>
          
          <div className="rounded-lg border p-4 space-y-2">
            <h4 className="font-medium">Account ID Not Found</h4>
            <p className="text-sm text-muted-foreground">
              If an account ID is not found, it may mean the account was disconnected from SocialBu or the account ID is incorrect.
              Check the list of accounts in the diagnosis results to find the correct ID.
            </p>
          </div>
          
          <div className="rounded-lg border p-4 space-y-2">
            <h4 className="font-medium">Connection Issues</h4>
            <p className="text-sm text-muted-foreground">
              If you can't connect to SocialBu at all, check your internet connection and make sure the SocialBu API is available.
              You may need to check the server logs for more details.
            </p>
          </div>
          
          <div className="rounded-lg border p-4 space-y-2">
            <h4 className="font-medium">Post Creation Failures</h4>
            <p className="text-sm text-muted-foreground">
              If posts are failing to create, verify the account ID is correct and that you're including all required fields.
              Some platforms have specific requirements for post content and media.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 
"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { getSocialBuAPI } from "@/lib/socialbu-api"
import { Loader2, AlertCircle, Copy, CheckCircle, Facebook, Instagram, Twitter, Linkedin, RefreshCw, Check, AlertTriangle, XCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Account {
  id: number
  name: string
  platform: string
  type: string
  status?: string
  image?: string
  in_database: boolean
}

interface AccountsResponse {
  user_id: string
  accounts: Account[]
  count: number
}

interface AccountCheckerProps {
  onValidAccountSelect?: (accountId: number) => void
}

// Create a simple spinner component
function Spinner() {
  return <Loader2 className="h-6 w-6 animate-spin" />;
}

export function AccountChecker({ onValidAccountSelect }: AccountCheckerProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [userId, setUserId] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<number | null>(null)

  // Platform icons
  const platformIcons: Record<string, React.ReactNode> = {
    facebook: <Facebook className="text-blue-600" />,
    instagram: <Instagram className="text-pink-600" />,
    twitter: <Twitter className="text-blue-400" />,
    x: <Twitter className="text-black" />,
    linkedin: <Linkedin className="text-blue-700" />,
    default: <CheckCircle className="text-green-500" />
  }

  // Load accounts on mount
  useEffect(() => {
    fetchAccounts()
  }, [])

  // Fetch accounts from the API
  const fetchAccounts = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const api = getSocialBuAPI()
      const response = await fetch('/api/socialbu/my_accounts/')
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to fetch accounts')
      }
      
      const data: AccountsResponse = await response.json()
      setAccounts(data.accounts)
      setUserId(data.user_id)
    } catch (err) {
      console.error('Error fetching accounts:', err)
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  // Copy account ID to clipboard
  const copyAccountId = (id: number) => {
    navigator.clipboard.writeText(id.toString())
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  // Get platform icon
  const getPlatformIcon = (platform: string) => {
    const key = platform.toLowerCase()
    return platformIcons[key] || platformIcons.default
  }

  const getPlatformColor = (platform: string) => {
    const colors: Record<string, string> = {
      facebook: "bg-blue-600",
      instagram: "bg-pink-600",
      twitter: "bg-blue-400",
      x: "bg-black",
      linkedin: "bg-blue-800",
      youtube: "bg-red-600",
      tiktok: "bg-black"
    }
    
    return colors[platform.toLowerCase()] || "bg-gray-500"
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Checking Your Accounts</CardTitle>
          <CardDescription>Verifying your SocialBu accounts...</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center items-center py-6">
          <Spinner />
        </CardContent>
      </Card>
    )
  }
  
  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="text-yellow-500" />
            Account Verification Failed
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchAccounts} className="w-full mt-2">
            <RefreshCw className="w-4 h-4 mr-2" /> Try Again
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Check className="text-green-500" />
          Your Connected Accounts
        </CardTitle>
        <CardDescription>
          {userId ? (
            <>SocialBu User ID: <span className="font-mono">{userId}</span></>
          ) : (
            "These are the accounts you can post to"
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {accounts.length === 0 ? (
          <div className="text-center py-4">
            <XCircle className="mx-auto mb-2 text-red-500" />
            <p>You have no connected social media accounts</p>
            <Button onClick={fetchAccounts} className="mt-4">
              <RefreshCw className="w-4 h-4 mr-2" /> Refresh
            </Button>
          </div>
        ) : (
          <>
            <div className="grid gap-2">
              {accounts.map((account) => (
                <div 
                  key={account.id} 
                  className="flex items-center justify-between p-2 border rounded-md hover:bg-muted/50 cursor-pointer"
                  onClick={() => onValidAccountSelect && onValidAccountSelect(account.id)}
                >
                  <div className="flex items-center gap-2">
                    {account.image ? (
                      <img src={account.image} alt={account.name} className="w-8 h-8 rounded-full" />
                    ) : (
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${getPlatformColor(account.platform)}`}>
                        {account.platform.slice(0, 1).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <p className="font-medium">{account.name}</p>
                      <p className="text-xs text-muted-foreground">
                        ID: {account.id} • {account.type || account.platform}
                      </p>
                    </div>
                  </div>
                  <Badge variant={account.status === "connected" ? "outline" : "secondary"}>
                    {account.status || "connected"}
                  </Badge>
                </div>
              ))}
            </div>
            <Button onClick={fetchAccounts} variant="outline" className="w-full mt-4">
              <RefreshCw className="w-4 h-4 mr-2" /> Refresh Accounts
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  )
} 
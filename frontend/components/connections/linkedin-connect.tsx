"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Linkedin, CheckCircle, Building2 } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { SocialAccount } from "@/services/social-platforms-api"

interface LinkedInConnectProps {
  isConnected: boolean
  account?: SocialAccount
  onConnect: () => Promise<void>
  onDisconnect: (accountId: number) => Promise<void>
  isConnecting: boolean
}

export function LinkedInConnect({ 
  isConnected, 
  account, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: LinkedInConnectProps) {
  const { toast } = useToast()
  const [companyPages, setCompanyPages] = useState<any[]>([])
  const [fullName, setFullName] = useState<string>("")
  const [email, setEmail] = useState<string>("") 
  const [authRequired, setAuthRequired] = useState<boolean>(false)

  // Extract LinkedIn-specific data if available
  useEffect(() => {
    if (account && account.metadata) {
      try {
        const metadata = typeof account.metadata === 'string' 
          ? JSON.parse(account.metadata) 
          : account.metadata

        if (metadata.company_pages) {
          setCompanyPages(metadata.company_pages)
        }
        
        if (metadata.full_name) {
          setFullName(metadata.full_name)
        } else if (metadata.first_name && metadata.last_name) {
          setFullName(`${metadata.first_name} ${metadata.last_name}`)
        }
        
        if (metadata.email) {
          setEmail(metadata.email)
        }
      } catch (e) {
        console.error("Error parsing LinkedIn metadata:", e)
      }
    }
  }, [account])

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-blue-700 to-blue-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Linkedin className="h-5 w-5" />
            <CardTitle>LinkedIn</CardTitle>
          </div>
          {isConnected && (
            <div className="flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
              <CheckCircle className="mr-1 h-3 w-3" />
              Connected
            </div>
          )}
        </div>
        <CardDescription className="text-blue-100">
          Share professional updates and manage company pages
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6">
        {isConnected && account ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              {account.profile_picture_url ? (
                <img
                  src={account.profile_picture_url}
                  alt={account.account_name}
                  className="h-12 w-12 rounded-full object-cover"
                />
              ) : (
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-200">
                  <Linkedin className="h-6 w-6 text-gray-500" />
                </div>
              )}
              <div>
                <h3 className="font-medium">{fullName || account.account_name}</h3>
                {email && <p className="text-sm text-gray-500">{email}</p>}
              </div>
            </div>
            
            {companyPages && companyPages.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-500">Company Pages</h4>
                <div className="rounded-lg border border-gray-200">
                  {companyPages.map((page, index) => (
                    <div key={page.id} className={`flex items-center gap-2 p-3 ${index !== companyPages.length - 1 ? 'border-b border-gray-200' : ''}`}>
                      {page.logo_url ? (
                        <img 
                          src={page.logo_url} 
                          alt={page.name} 
                          className="h-8 w-8 rounded object-cover" 
                        />
                      ) : (
                        <div className="flex h-8 w-8 items-center justify-center rounded bg-blue-100">
                          <Building2 className="h-4 w-4 text-blue-600" />
                        </div>
                      )}
                      <div>
                        <p className="text-sm font-medium">{page.name}</p>
                        {page.vanity_name && (
                          <p className="text-xs text-gray-500">
                            linkedin.com/company/{page.vanity_name}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Linkedin className="mb-2 h-12 w-12 text-gray-400" />
            <h3 className="mb-1 text-lg font-medium">Connect LinkedIn</h3>
            <p className="mb-4 text-sm text-gray-500">
              Share professional updates and manage company pages
            </p>
            {authRequired ? (
              <div className="space-y-3">
                <div className="rounded-md bg-amber-50 p-4">
                  <p className="text-sm text-amber-800">
                    Please log in to complete your LinkedIn connection.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setAuthRequired(false)}
                  className="w-full"
                >
                  Try Again
                </Button>
              </div>
            ) : (
              <Button 
                onClick={onConnect} 
                className="bg-blue-700 hover:bg-blue-600 text-white"
                disabled={isConnecting}
              >
                {isConnecting ? "Connecting..." : "Connect LinkedIn"}
              </Button>
            )}
          </div>
        )}
      </CardContent>
      {isConnected && account && (
        <CardFooter className="bg-gray-50 px-6 py-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => onDisconnect(account.id)}
          >
            Disconnect LinkedIn
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

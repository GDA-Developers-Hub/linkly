"use client"

import { useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"

export default function AuthCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    // Get the platform and code from the URL
    const platform = searchParams.get('platform')
    const code = searchParams.get('code')
    const error = searchParams.get('error')
    const error_description = searchParams.get('error_description')

    // Redirect back to the platform connect page with the parameters
    const redirectUrl = new URL('/dashboard/platform-connect', window.location.origin)
    
    if (platform) redirectUrl.searchParams.set('platform', platform)
    if (code) redirectUrl.searchParams.set('code', code)
    if (error) redirectUrl.searchParams.set('error', error)
    if (error_description) redirectUrl.searchParams.set('error_description', error_description)

    router.replace(redirectUrl.toString())
  }, [])

  return (
    <div className="container flex items-center justify-center min-h-screen py-10">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center">Connecting Account</CardTitle>
          <CardDescription className="text-center">
            Please wait while we connect your account...
          </CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center py-6">
          <Loader2 className="h-8 w-8 animate-spin" />
        </CardContent>
      </Card>
    </div>
  )
} 
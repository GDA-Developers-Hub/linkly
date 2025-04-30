"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { testAndNotify, diagnoseAccountIdIssue, type ConnectionTestResult } from "@/lib/socialbu-connection-test"
import { Loader2, CheckCircle, XCircle, HelpCircle } from "lucide-react"

export function ConnectionTester() {
  const [loading, setLoading] = useState(false)
  const [accountId, setAccountId] = useState<string>("")
  const [result, setResult] = useState<ConnectionTestResult | null>(null)
  const [diagnosis, setDiagnosis] = useState<string | null>(null)

  // Test general API connection
  const testConnection = async () => {
    setLoading(true)
    setResult(null)
    setDiagnosis(null)
    
    try {
      const result = await testAndNotify()
      setResult(result)
    } catch (error) {
      console.error("Error testing connection:", error)
    } finally {
      setLoading(false)
    }
  }

  // Test specific account connection
  const testAccountConnection = async () => {
    if (!accountId || isNaN(parseInt(accountId))) {
      setDiagnosis("Please enter a valid account ID (number only)")
      return
    }
    
    setLoading(true)
    setResult(null)
    setDiagnosis(null)
    
    try {
      const id = parseInt(accountId)
      const result = await testAndNotify(id)
      setResult(result)
      
      // Get more detailed diagnosis
      const diagnosisResult = await diagnoseAccountIdIssue(id)
      setDiagnosis(diagnosisResult)
    } catch (error) {
      console.error("Error testing account connection:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle>SocialBu Connection Tester</CardTitle>
        <CardDescription>
          Diagnose connection issues with the SocialBu API
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Button 
            variant="outline" 
            disabled={loading} 
            onClick={testConnection} 
            className="w-full"
          >
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <HelpCircle className="mr-2 h-4 w-4" />
            )}
            Test API Connection
          </Button>
        </div>
        
        <div className="flex space-x-2">
          <Input
            type="text"
            placeholder="Enter Account ID"
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            className="flex-1"
          />
          <Button 
            variant="secondary" 
            disabled={loading || !accountId} 
            onClick={testAccountConnection}
          >
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <CheckCircle className="mr-2 h-4 w-4" />
            )}
            Test Account
          </Button>
        </div>
        
        {result && (
          <div className={`p-4 rounded-md ${
            result.status === 'connected' ? 'bg-green-50 text-green-700' : 
            result.status === 'auth_error' ? 'bg-orange-50 text-orange-700' : 
            'bg-red-50 text-red-700'
          }`}>
            <div className="font-medium">
              {result.status === 'connected' ? (
                <div className="flex items-center">
                  <CheckCircle className="mr-2 h-5 w-5" />
                  Connected
                </div>
              ) : result.status === 'auth_error' ? (
                <div className="flex items-center">
                  <XCircle className="mr-2 h-5 w-5" />
                  Authentication Error
                </div>
              ) : (
                <div className="flex items-center">
                  <XCircle className="mr-2 h-5 w-5" />
                  Connection Error
                </div>
              )}
            </div>
            <div className="mt-1 text-sm">
              {result.message}
            </div>
          </div>
        )}
        
        {diagnosis && (
          <div className="p-4 rounded-md bg-blue-50 text-blue-700">
            <div className="font-medium">Diagnosis</div>
            <div className="mt-1 text-sm whitespace-pre-line">
              {diagnosis}
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="text-sm text-gray-500">
        Use this tool to diagnose issues with SocialBu API connections and accounts
      </CardFooter>
    </Card>
  )
} 
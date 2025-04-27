"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function ApiTestPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [endpoint, setEndpoint] = useState('subscriptions/plans/')
  const [email, setEmail] = useState('test@example.com')
  const [password, setPassword] = useState('password123')
  
  const testApiCall = async () => {
    setLoading(true)
    setResult('Testing connection...')
    
    try {
      const response = await fetch('/api/debug', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ endpoint }),
      })
      
      console.log('Debug API Response:', response)
      const data = await response.json()
      setResult(`Response: ${JSON.stringify(data, null, 2)}`)
    } catch (error) {
      console.error('Test failed:', error)
      setResult(`Exception: ${(error as Error).message}`)
    } finally {
      setLoading(false)
    }
  }
  
  const testNextApi = async () => {
    setLoading(true)
    setResult('Testing Next.js API route...')
    
    try {
      const response = await fetch('/api/debug')
      console.log('Next.js API Response:', response)
      
      if (response.ok) {
        const data = await response.json()
        setResult(`Next.js API Success: ${JSON.stringify(data, null, 2)}`)
      } else {
        setResult(`Next.js API Error: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('Next.js API test failed:', error)
      setResult(`Exception: ${(error as Error).message}`)
    } finally {
      setLoading(false)
    }
  }
  
  const testDirect = async () => {
    setLoading(true)
    setResult('Testing direct Django access...')
    
    try {
      // Direct fetch to Django API
      const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
      const url = `/api/${cleanEndpoint}`;
      
      console.log(`Testing direct access to: ${url}`);
      const response = await fetch(url)
      console.log('Direct API Response:', response)
      
      if (response.ok) {
        const data = await response.json()
        setResult(`Direct Success: ${JSON.stringify(data, null, 2)}`)
      } else {
        setResult(`Direct Error: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('Direct test failed:', error)
      setResult(`Exception: ${(error as Error).message}`)
    } finally {
      setLoading(false)
    }
  }
  
  const testLogin = async () => {
    setLoading(true)
    setResult('Testing login...')
    
    try {
      // First try the debug endpoint
      const response = await fetch('/api/login-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password 
        }),
      })
      
      console.log('Login Test Response:', response)
      const data = await response.json()
      setResult(`Login Test Results:\n${JSON.stringify(data, null, 2)}`)
    } catch (error) {
      console.error('Login test failed:', error)
      setResult(`Exception: ${(error as Error).message}`)
    } finally {
      setLoading(false)
    }
  }
  
  const testAccounts = async () => {
    setLoading(true)
    setResult('Testing accounts endpoint...')
    
    try {
      // Test with trailing slash
      const url = '/api/accounts/';
      console.log(`Testing accounts endpoint at: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('linkly_access_token')}`,
        },
      });
      
      console.log('Accounts Response:', response);
      
      if (response.ok) {
        const data = await response.json();
        setResult(`Accounts Success: ${JSON.stringify(data, null, 2)}`);
      } else {
        try {
          const errorData = await response.json();
          setResult(`Accounts Error (${response.status} ${response.statusText}):\n${JSON.stringify(errorData, null, 2)}`);
        } catch (e) {
          const errorText = await response.text();
          setResult(`Accounts Error (${response.status} ${response.statusText}):\n${errorText || "Empty response"}`);
        }
      }
    } catch (error) {
      console.error('Accounts test failed:', error);
      setResult(`Exception: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };
  
  const testSocialBuAccounts = async () => {
    setLoading(true)
    setResult('Testing SocialBu accounts endpoint...')
    
    try {
      // Test the SocialBu accounts endpoint with trailing slash
      const url = '/api/socialbu/accounts/';
      console.log(`Testing SocialBu accounts endpoint at: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('linkly_access_token')}`,
        },
      });
      
      console.log('SocialBu Accounts Response:', response);
      
      if (response.ok) {
        const data = await response.json();
        setResult(`SocialBu Accounts Success: ${JSON.stringify(data, null, 2)}`);
      } else {
        try {
          const errorData = await response.json();
          setResult(`SocialBu Accounts Error (${response.status} ${response.statusText}):\n${JSON.stringify(errorData, null, 2)}`);
        } catch (e) {
          const errorText = await response.text();
          setResult(`SocialBu Accounts Error (${response.status} ${response.statusText}):\n${errorText || "Empty response"}`);
        }
      }
    } catch (error) {
      console.error('SocialBu Accounts test failed:', error);
      setResult(`Exception: ${(error as Error).message}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container py-10">
      <Card>
        <CardHeader>
          <CardTitle>API Connection Test</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="general">
            <TabsList className="mb-4">
              <TabsTrigger value="general">General API Testing</TabsTrigger>
              <TabsTrigger value="login">Login Testing</TabsTrigger>
              <TabsTrigger value="accounts">Accounts Testing</TabsTrigger>
            </TabsList>
            
            <TabsContent value="general">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">API Endpoint:</label>
                  <div className="flex gap-2">
                    <Input 
                      value={endpoint} 
                      onChange={(e) => setEndpoint(e.target.value)}
                      placeholder="e.g., subscriptions/plans/"
                      className="flex-1"
                    />
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  <Button onClick={testApiCall} disabled={loading} variant="default">
                    {loading ? 'Testing...' : 'Test via Debug API'}
                  </Button>
                  
                  <Button onClick={testNextApi} disabled={loading} variant="outline">
                    Test Next.js API
                  </Button>
                  
                  <Button onClick={testDirect} disabled={loading} variant="secondary">
                    Test Direct Access
                  </Button>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="login">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Email:</label>
                  <Input 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="test@example.com"
                    className="mb-3"
                  />
                  
                  <label className="block text-sm font-medium mb-1">Password:</label>
                  <Input 
                    type="password"
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="password"
                  />
                </div>
                
                <Button onClick={testLogin} disabled={loading} variant="default">
                  {loading ? 'Testing Login...' : 'Test Login API'}
                </Button>
              </div>
            </TabsContent>
            
            <TabsContent value="accounts">
              <div className="space-y-4">
                <p className="text-sm text-gray-500">
                  Test account endpoints to diagnose JSON parsing errors.
                  Make sure you're logged in with a valid token before testing.
                </p>
                
                <div className="flex flex-wrap gap-2">
                  <Button onClick={testAccounts} disabled={loading} variant="default">
                    {loading ? 'Testing...' : 'Test Regular Accounts'}
                  </Button>
                  
                  <Button onClick={testSocialBuAccounts} disabled={loading} variant="secondary">
                    {loading ? 'Testing...' : 'Test SocialBu Accounts'}
                  </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
          
          {result && (
            <div className="mt-4 p-4 bg-gray-100 rounded overflow-auto max-h-96">
              <pre>{result}</pre>
            </div>
          )}
          
          <div className="mt-6">
            <h3 className="font-medium">Manual Test Links:</h3>
            <ul className="mt-2 space-y-2">
              <li>
                <a href="/api/debug" target="_blank" className="text-blue-500 hover:underline">
                  GET /api/debug (Next.js API test)
                </a>
              </li>
              <li>
                <a href="/api/subscriptions/plans/" target="_blank" className="text-blue-500 hover:underline">
                  GET /api/subscriptions/plans/ (direct Django API)
                </a>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 
"use client"

import Link from "next/link"
import { redirect } from "next/navigation"
import { useRouter } from 'next/navigation'
import React, { useEffect, useState } from "react"
import { LuLayoutDashboard, LuSettings, LuCode, LuLink, LuClipboardList, LuLogOut } from "react-icons/lu"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import Swal from 'sweetalert2'
import { useAuth } from "@/contexts/auth-context"
import { getAPI, type Plan as APIPlan } from "@/lib/api"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { AppSidebar } from "@/components/app-sidebar"

// Adapt the Plan interface to match what's used in this component
interface Plan {
  id: number
  name: string
  description: string
  price: string | number
  interval?: string
  frequency?: string
  features: string[]
  is_active: boolean
}

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, hasValidToken, isLoading, validateToken, logout } = useAuth()
  const [hasSubscription, setHasSubscription] = useState<boolean | null>(null)
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  const [isSubscriptionLoading, setIsSubscriptionLoading] = useState(false)
  const [isPlansLoading, setIsPlansLoading] = useState(false)
  const router = useRouter()
  const api = getAPI()

  // Check for valid token and subscription status
  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log("Dashboard: No authentication check - unrestricted access")
        
        // Load available plans
        fetchPlans()
      } catch (error) {
        console.error("Dashboard: Error loading plans:", error)
      } finally {
        setIsSubscriptionLoading(false)
      }
    }
    
    if (!isLoading) {
      checkAuth()
    }
  }, [isLoading])

  const fetchPlans = async () => {
    try {
      setIsPlansLoading(true)
      const availablePlans = await api.getPlans()
      console.log("Available plans:", availablePlans)
      
      // Transform API plans to match our component's Plan interface
      const transformedPlans = availablePlans.map(plan => ({
        id: plan.id,
        name: plan.name,
        description: plan.description,
        price: plan.price,
        interval: plan.frequency,
        features: [
          `${plan.post_limit} posts`,
          `${plan.account_limit} accounts`,
          `${plan.team_members} team members`,
          plan.analytics_access ? 'Analytics access' : '',
          plan.ai_generation ? 'AI generation' : '',
          plan.post_scheduling ? 'Post scheduling' : '',
          plan.calendar_view ? 'Calendar view' : ''
        ].filter(feature => feature !== ''),
        is_active: plan.is_active
      }))
      
      setPlans(transformedPlans)
    } catch (error) {
      console.error("Error fetching plans:", error)
      Swal.fire({
        title: 'Error',
        text: 'Failed to load subscription plans. Please try again later.',
        icon: 'error',
        confirmButtonText: 'Ok'
      })
    } finally {
      setIsPlansLoading(false)
    }
  }

  const handleSubscribe = async () => {
    if (!selectedPlanId) {
      Swal.fire({
        title: 'Please select a plan',
        text: 'You need to select a subscription plan to continue',
        icon: 'warning',
        confirmButtonText: 'Ok'
      })
      return
    }

    try {
      setIsSubscriptionLoading(true)
      // Pass the numeric ID directly
      const subscription = await api.createSubscription(selectedPlanId)
      console.log("Subscription created:", subscription)
      Swal.fire({
        title: 'Success',
        text: 'Your subscription has been activated!',
        icon: 'success',
        confirmButtonText: 'Continue'
      }).then(() => {
        setHasSubscription(true)
      })
    } catch (error) {
      console.error("Error creating subscription:", error)
      Swal.fire({
        title: 'Subscription Failed',
        text: 'There was an error activating your subscription. Please try again.',
        icon: 'error',
        confirmButtonText: 'Ok'
      })
    } finally {
      setIsSubscriptionLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
  }

  // Show loading state while initial auth check is in progress
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="space-y-4 w-full max-w-md p-8">
          <Skeleton className="h-12 w-1/2 mx-auto" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-8 w-3/4 mx-auto" />
          <Skeleton className="h-8 w-1/2 mx-auto" />
        </div>
      </div>
    )
  }

  // If subscription status is still loading, show loading state
  if (hasSubscription === null && isSubscriptionLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="space-y-4 w-full max-w-md p-8">
          <Skeleton className="h-12 w-1/2 mx-auto" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-8 w-3/4 mx-auto" />
          <Skeleton className="h-8 w-1/2 mx-auto" />
        </div>
      </div>
    )
  }

  // If no subscription, show subscription selection UI
  if (hasSubscription === false) {
    return (
      <div className="flex min-h-screen flex-col">
        <div className="flex min-h-[calc(100vh-4rem)] flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
          <div className="mx-auto max-w-6xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Choose a Subscription Plan</h1>
                <p className="text-muted-foreground">
                  Subscribe to a plan to access all features.
                </p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {isPlansLoading ? (
                // Show skeleton loading for plans
                Array(3).fill(0).map((_, index) => (
                  <Card key={index} className="overflow-hidden">
                    <CardHeader className="p-6">
                      <Skeleton className="h-6 w-1/2" />
                      <Skeleton className="h-10 w-full" />
                    </CardHeader>
                    <CardContent className="p-6 pt-0">
                      <Skeleton className="h-6 w-full mb-2" />
                      <Skeleton className="h-6 w-full mb-2" />
                      <Skeleton className="h-6 w-full mb-2" />
                      <div className="mt-6">
                        <Skeleton className="h-10 w-full" />
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                plans.map((plan) => (
                  <Card 
                    key={plan.id} 
                    className={`overflow-hidden cursor-pointer transition-all ${selectedPlanId === plan.id ? 'ring-2 ring-primary' : ''}`}
                    onClick={() => setSelectedPlanId(plan.id)}
                  >
                    <CardHeader className="p-6">
                      <CardTitle className="flex items-center justify-between">
                        {plan.name}
                        <span className="text-2xl font-bold">${plan.price}/{plan.interval}</span>
                      </CardTitle>
                      <p className="text-sm text-muted-foreground">{plan.description}</p>
                    </CardHeader>
                    <CardContent className="p-6 pt-0">
                      <ul className="space-y-2">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="flex items-center gap-2 text-sm">
                            <span className="text-green-500">✓</span> {feature}
                          </li>
                        ))}
                      </ul>
                      <Button 
                        className="mt-6 w-full" 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedPlanId(plan.id);
                        }}
                      >
                        {selectedPlanId === plan.id ? 'Selected' : 'Select Plan'}
                      </Button>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
            <div className="flex justify-end mt-6">
              <Button 
                size="lg" 
                onClick={handleSubscribe} 
                disabled={!selectedPlanId || isSubscriptionLoading}
              >
                {isSubscriptionLoading ? 'Processing...' : 'Continue with Selected Plan'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Main dashboard layout with modern sidebar
  return (
    <div className="flex min-h-screen w-full bg-muted/10">
      <div className="md:w-16 lg:w-64 flex-shrink-0">
        <AppSidebar />
      </div>
      
      <main className="flex-1 w-full">
        <div className="flex h-16 items-center justify-end gap-4 border-b bg-background px-4">
          {user && (
            <div className="flex items-center gap-4">
              <div className="text-right text-sm mr-2">
                <p className="font-medium">{user.full_name || user.email}</p>
                <p className="text-xs text-muted-foreground">{user.email}</p>
              </div>
              <Avatar className="h-9 w-9">
                <AvatarImage src="/placeholder-user.jpg" alt={user.full_name || user.email} />
                <AvatarFallback>{user.full_name?.[0] || user.email?.[0] || 'U'}</AvatarFallback>
              </Avatar>
            </div>
          )}
        </div>
        
        <div className="p-4 md:p-6">
          {children}
        </div>
      </main>
    </div>
  )
}

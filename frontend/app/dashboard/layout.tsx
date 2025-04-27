"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { AppSidebar } from "@/components/app-sidebar"
import { useAuth } from "@/contexts/auth-context"
import { getAPI } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const [authChecked, setAuthChecked] = useState(false)
  const router = useRouter()
  const { toast } = useToast()
  const api = getAPI()

  // Debug log current authentication state
  useEffect(() => {
    console.log("Dashboard layout - auth state:", { 
      isAuthenticated, 
      isLoading, 
      hasUser: !!user,
      hasToken: api.isAuthenticated(),
    });
  }, [isAuthenticated, isLoading, user]);

  useEffect(() => {
    const checkSubscription = async () => {
      try {
        // Only check if authenticated and not loading
        if (isAuthenticated && !isLoading) {
          console.log("Dashboard - checking subscription status");
          const subscription = await api.getCurrentSubscription();
          console.log("Dashboard - subscription status:", subscription);
          
          if (!subscription) {
            console.log("Dashboard - no active subscription found, redirecting");
            toast({
              title: "Subscription required",
              description: "Please select a subscription plan to continue.",
              variant: "destructive",
            });
            router.push("/auth/subscription");
          } else {
            setAuthChecked(true);
          }
        }
      } catch (error) {
        console.error("Error checking subscription:", error);
        // Don't redirect on error, might be temporary backend issue
      }
    };

    if (isAuthenticated && !isLoading) {
      checkSubscription();
    }
  }, [isAuthenticated, isLoading, router, toast]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      console.log("Dashboard - not authenticated, redirecting to login");
      toast({
        title: "Authentication required",
        description: "Please log in to access the dashboard.",
      });
      router.push("/auth/login");
    }
  }, [isAuthenticated, isLoading, router, toast]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <main className="flex-1 overflow-auto p-4 md:p-6 md:ml-64">{children}</main>
    </div>
  );
}

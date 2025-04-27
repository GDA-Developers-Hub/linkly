"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { getAPI, type User, type LoginData, type RegisterData } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import Swal from 'sweetalert2'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginData) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Helper function to format error messages from API responses
const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error;
  
  let errorMessage = '';
  
  if (error && typeof error === 'object') {
    // Handle array of errors or object with field errors
    Object.entries(error).forEach(([field, messages]) => {
      if (Array.isArray(messages)) {
        messages.forEach(message => {
          errorMessage += `${field}: ${message}<br>`;
        });
      } else if (typeof messages === 'string') {
        errorMessage += `${field}: ${messages}<br>`;
      }
    });
  }
  
  return errorMessage || 'An error occurred';
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { toast } = useToast()
  const api = getAPI()

  useEffect(() => {
    // Check if user is authenticated on mount
    const checkAuth = async () => {
      try {
        console.log("Auth check - tokens exist:", api.isAuthenticated());
        if (api.isAuthenticated()) {
          console.log("Auth check - fetching user profile");
          const userData = await api.getProfile()
          console.log("Auth check - user profile received:", userData);
          setUser(userData)
        } else {
          console.log("Auth check - no tokens found");
        }
      } catch (error) {
        console.error("Error checking authentication:", error)
        // Clear tokens if there's an error
        console.log("Auth check - clearing tokens due to error");
        api.clearTokens()
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (data: LoginData) => {
    setIsLoading(true)
    try {
      const response = await api.login(data)
      setUser(response.user)
      toast({
        title: "Login successful",
        description: `Welcome back, ${response.user.first_name}!`,
      })
      
      // Authenticate with SocialBu if possible
      try {
        // SocialBu authentication is handled on the backend automatically
        // when accessing secured endpoints, so we don't need to do anything here
        console.log("Auto-authenticating with SocialBu in the background")
      } catch (error) {
        console.error("SocialBu authentication error (non-critical):", error)
      }
      
      // Check if user has an active subscription
      try {
        const subscription = await api.getCurrentSubscription()
        if (subscription) {
          // User has a subscription, go to dashboard
          router.push("/dashboard")
        } else {
          // User doesn't have a subscription, go to plan selection
          router.push("/auth/subscription")
        }
      } catch (error) {
        // If there's an error checking subscription, redirect to subscription page
        router.push("/auth/subscription")
      }
    } catch (error: any) {
      console.error("Login error:", error)
      
      // Extract error message from API response
      let errorMessage = "Login failed";
      
      if (error.message) {
        errorMessage = error.message;
      } else if (error.response?.data) {
        errorMessage = formatErrorMessage(error.response.data);
      }
      
      // Use SweetAlert2 for error toast
      Swal.fire({
        title: 'Login Failed',
        html: errorMessage,
        icon: 'error',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
      });
      
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (data: RegisterData) => {
    setIsLoading(true)
    console.log("Starting registration process for:", data.email)
    
    try {
      console.log("Sending registration request to backend API")
      const response = await api.register(data)
      console.log("Registration successful. Response:", response)
      
      // User is automatically logged in after registration
      setUser(response.user)
      
      toast({
        title: "Registration successful",
        description: `Welcome to Linkly, ${response.user.first_name}!`,
      })
      
      console.log("SocialBu integration should be complete on the backend")
      
      // Redirect directly to the login page for SocialBu integration
      router.push("/auth/login")
    } catch (error: any) {
      console.error("Registration error:", error)
      console.error("Registration error details:", error.response?.data || {})
      
      // Extract error message from API response
      const errorData = error.response?.data || {};
      
      // Use SweetAlert2 for error toast
      Swal.fire({
        title: 'Registration Failed',
        html: formatErrorMessage(errorData),
        icon: 'error',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
      });
      
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await api.logout()
      setUser(null)
      toast({
        title: "Logged out",
        description: "You have been successfully logged out.",
      })
      router.push("/")
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

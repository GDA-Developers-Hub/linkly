"use client"

import React, { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { getAPI, type User, type LoginData, type RegisterData } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import Swal from 'sweetalert2'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  hasValidToken: boolean
  isLoading: boolean
  login: (data: LoginData) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  validateToken: () => Promise<boolean>
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
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [hasValidToken, setHasValidToken] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { toast } = useToast()
  const api = getAPI()

  // Function to validate token with backend
  const validateToken = async (): Promise<boolean> => {
    try {
      // First check if tokens exist in localStorage
      const accessToken = localStorage.getItem("accessToken")
      const refreshToken = localStorage.getItem("refreshToken")
      
      if (!accessToken || !refreshToken) {
        return false
      }
      
      // Verify token validity by making a profile request
      const userData = await api.getProfile()
      if (userData) {
        setUser(userData)
        return true
      }
      return false
    } catch (error) {
      console.error("Token validation failed:", error)
      // Clear invalid tokens
      localStorage.removeItem("accessToken")
      localStorage.removeItem("refreshToken")
      return false
    }
  }

  useEffect(() => {
    const initAuth = async () => {
      try {
        const isValid = await validateToken()
        setHasValidToken(isValid)
        setIsAuthenticated(isValid)
      } catch (error) {
        console.error("Authentication validation error:", error)
        setHasValidToken(false)
        setIsAuthenticated(false)
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (data: LoginData) => {
    setIsLoading(true)
    try {
      const response = await api.login(data)
      setUser(response.user)
      setHasValidToken(true)
      setIsAuthenticated(true)
      toast({
        title: "Login successful",
        description: `Welcome back, ${response.user.first_name}!`,
      })
      
      // Go directly to dashboard - it will handle subscription check
      router.push("/dashboard")
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
      setHasValidToken(true)
      setIsAuthenticated(true)
      
      toast({
        title: "Registration successful",
        description: `Welcome to Linkly, ${response.user.first_name}!`,
      })
      
      // Go directly to dashboard - it will handle subscription check
      router.push("/dashboard")
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
      setIsAuthenticated(false)
      setHasValidToken(false)
      toast({
        title: "Logged out",
        description: "You have been successfully logged out.",
      })
      router.push("/")
    } catch (error) {
      console.error("Logout error:", error)
      // Even if logout fails, clear everything locally
      localStorage.removeItem("accessToken")
      localStorage.removeItem("refreshToken")
      setUser(null)
      setIsAuthenticated(false)
      setHasValidToken(false)
      router.push("/")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        hasValidToken,
        isLoading,
        login,
        register,
        logout,
        validateToken,
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

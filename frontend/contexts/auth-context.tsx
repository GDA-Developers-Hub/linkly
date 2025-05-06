"use client"

import React, { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { getAPI, type User, type LoginData, type RegisterData } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import Swal from 'sweetalert2'

// Safe localStorage access
const safeStorage = {
  getItem: (key: string): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(key);
    }
    return null;
  },
  setItem: (key: string, value: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, value);
    }
  },
  removeItem: (key: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
  }
};

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

  // Function to validate token
  const validateToken = async (): Promise<boolean> => {
    // Check if we have an access token in localStorage
    const token = safeStorage.getItem("accessToken")
    
    if (!token) {
      return false
    }
    
    try {
      // We'll try to get the user profile with the token
      const user = await api.getProfile()
      setUser(user)
      setIsAuthenticated(true)
      setHasValidToken(true)
      return true
    } catch (error) {
      console.log("Token validation failed:", error)
      // Clear user data from localStorage
      safeStorage.removeItem("accessToken")
      safeStorage.removeItem("refreshToken")
      safeStorage.removeItem("user")
      
      setUser(null)
      setIsAuthenticated(false)
      setHasValidToken(false)
      return false
    }
  }

  // Check auth status on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Try to get stored user data
        const userData = safeStorage.getItem("user")
        if (userData) {
          try {
            setUser(JSON.parse(userData))
          } catch (e) {
            console.error("Error parsing user data from localStorage", e)
          }
        }

        // Validate token
        const isValid = await validateToken()
        
        if (!isValid && typeof window !== 'undefined') {
          // In Next.js App Router, we don't have router.pathname, so use window.location.pathname
          const currentPath = window.location.pathname;
          if (currentPath !== "/login" && currentPath !== "/register") {
            // If token is invalid and user is not on login/register page,
            // they may need to be redirected, but we'll let the page component handle that
            console.log("Token is invalid, user may need to re-authenticate")
          }
        }
      } catch (error) {
        console.error("Error initializing auth:", error)
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (data: LoginData) => {
    setIsLoading(true)
    console.log("Starting login process for:", data.email)
    
    try {
      const response = await api.login(data)
      console.log("Login successful! Response:", response)
      
      // Store tokens - ensure we handle both object formats that Django might return
      if (response.tokens) {
        console.log('Token structure:', Object.keys(response.tokens));
        
        if (response.tokens.access) {
          console.log('Storing access token, length:', response.tokens.access.length);
          safeStorage.setItem('accessToken', response.tokens.access);
        }
        
        if (response.tokens.refresh) {
          console.log('Storing refresh token, length:', response.tokens.refresh.length);
          safeStorage.setItem('refreshToken', response.tokens.refresh);
        }
      } else {
        // Handle direct token in response for backward compatibility
        // Check if response has any token-like properties (this might be from a different API format)
        const accessToken = (response as any).access || (response as any).access_token;
        if (accessToken) {
          console.log('Storing access token, length:', accessToken.length);
          safeStorage.setItem('accessToken', accessToken);
          
          const refreshToken = (response as any).refresh || (response as any).refresh_token;
          if (refreshToken) {
            console.log('Storing refresh token, length:', refreshToken.length);
            safeStorage.setItem('refreshToken', refreshToken);
          }
        } else {
          console.warn('No tokens found in registration response');
        }
      }
      
      // Verify tokens were stored correctly
      console.log('Tokens saved to localStorage:', {
        access: safeStorage.getItem('accessToken') ? 'present' : 'missing',
        refresh: safeStorage.getItem('refreshToken') ? 'present' : 'missing'
      });
      
      // Save user data to localStorage
      safeStorage.setItem('user', JSON.stringify(response.user))
      
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
      // Log the response data to ensure we're receiving the tokens correctly
      console.log('Registration response data structure:', Object.keys(response));
      
      // Store tokens - ensure we handle both object formats that Django might return
      if (response.tokens) {
        console.log('Token structure:', Object.keys(response.tokens));
        
        if (response.tokens.access) {
          console.log('Storing access token, length:', response.tokens.access.length);
          safeStorage.setItem('accessToken', response.tokens.access);
        }
        
        if (response.tokens.refresh) {
          console.log('Storing refresh token, length:', response.tokens.refresh.length);
          safeStorage.setItem('refreshToken', response.tokens.refresh);
        }
      } else {
        // Handle direct token in response for backward compatibility
        // Check if response has any token-like properties (this might be from a different API format)
        const accessToken = (response as any).access || (response as any).access_token;
        if (accessToken) {
          console.log('Storing access token, length:', accessToken.length);
          safeStorage.setItem('accessToken', accessToken);
          
          const refreshToken = (response as any).refresh || (response as any).refresh_token;
          if (refreshToken) {
            console.log('Storing refresh token, length:', refreshToken.length);
            safeStorage.setItem('refreshToken', refreshToken);
          }
        } else {
          console.warn('No tokens found in registration response');
        }
      }
      
      // Verify tokens were stored correctly
      console.log('Tokens saved to localStorage after registration:', {
        access: safeStorage.getItem('accessToken') ? 'present' : 'missing',
        refresh: safeStorage.getItem('refreshToken') ? 'present' : 'missing'
      });
      
      // Save user data to localStorage
      safeStorage.setItem('user', JSON.stringify(response.user))
      
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
      // Clear user data from localStorage
      safeStorage.removeItem('user')
      safeStorage.removeItem('accessToken')
      safeStorage.removeItem('refreshToken')
      
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
      safeStorage.removeItem("accessToken")
      safeStorage.removeItem("refreshToken")
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

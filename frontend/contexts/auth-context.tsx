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
  // Initialize user state from localStorage if available
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window !== 'undefined') {
      const storedUser = localStorage.getItem('user')
      return storedUser ? JSON.parse(storedUser) : null
    }
    return null
  })
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
      
      console.log('Token validation check:', {
        accessToken: accessToken ? 'present' : 'missing',
        refreshToken: refreshToken ? 'present' : 'missing'
      });
      
      if (!accessToken || !refreshToken) {
        console.warn('Missing tokens during validation');
        return false
      }
      
      // Verify token validity by making a profile request
      const userData = await api.getProfile()
      if (userData) {
        // Update localStorage with latest user data
        localStorage.setItem('user', JSON.stringify(userData))
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
      // Make direct fetch call without authentication headers for login
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
      const loginUrl = `${baseUrl}/users/token/`;
      
      console.log('Making direct login request to:', loginUrl);
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const responseData = await response.json();
      
      // Log the response data to ensure we're receiving the tokens correctly
      console.log('Login response data structure:', Object.keys(responseData));
      
      // Store tokens - ensure we handle both object formats that Django might return
      if (responseData.access || responseData.access_token) {
        const accessToken = responseData.access || responseData.access_token;
        console.log('Storing access token, length:', accessToken.length);
        localStorage.setItem('accessToken', accessToken);
      } else {
        console.warn('No access token found in response');
      }
      
      if (responseData.refresh || responseData.refresh_token) {
        const refreshToken = responseData.refresh || responseData.refresh_token;
        console.log('Storing refresh token, length:', refreshToken.length);
        localStorage.setItem('refreshToken', refreshToken);
      } else {
        console.warn('No refresh token found in response');
      }
      
      // Verify tokens were stored correctly
      console.log('Tokens saved to localStorage:', {
        access: localStorage.getItem('accessToken') ? 'present' : 'missing',
        refresh: localStorage.getItem('refreshToken') ? 'present' : 'missing'
      });
      
      // Save user data to localStorage
      localStorage.setItem('user', JSON.stringify(responseData.user))
      
      setUser(responseData.user)
      setHasValidToken(true)
      setIsAuthenticated(true)
      toast({
        title: "Login successful",
        description: `Welcome back, ${responseData.user.first_name}!`,
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
          localStorage.setItem('accessToken', response.tokens.access);
        }
        
        if (response.tokens.refresh) {
          console.log('Storing refresh token, length:', response.tokens.refresh.length);
          localStorage.setItem('refreshToken', response.tokens.refresh);
        }
      } else if (response.access || response.access_token) {
        // Direct token in response
        const accessToken = response.access || response.access_token;
        console.log('Storing access token, length:', accessToken.length);
        localStorage.setItem('accessToken', accessToken);
        
        const refreshToken = response.refresh || response.refresh_token;
        if (refreshToken) {
          console.log('Storing refresh token, length:', refreshToken.length);
          localStorage.setItem('refreshToken', refreshToken);
        }
      } else {
        console.warn('No tokens found in registration response');
      }
      
      // Verify tokens were stored correctly
      console.log('Tokens saved to localStorage after registration:', {
        access: localStorage.getItem('accessToken') ? 'present' : 'missing',
        refresh: localStorage.getItem('refreshToken') ? 'present' : 'missing'
      });
      
      // Save user data to localStorage
      localStorage.setItem('user', JSON.stringify(response.user))
      
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
      localStorage.removeItem('user')
      
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

"use client"

import React, { useState, useEffect } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import Swal from 'sweetalert2'
import axios from 'axios'
import API_BASE_URL from "../Utils/BaseUrl"
import { loginUser, setAuthTokens, getAccessToken, getRefreshToken } from "../Utils/Auth"

export function LoginForm() {
  const navigate = useNavigate()
  const location = useLocation()
  const searchParams = new URLSearchParams(location.search)
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [needs2FA, setNeeds2FA] = useState(false)
  const [userId, setUserId] = useState(null)

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    two_factor_code: "",
  })
  
  // Revert: Initialize fieldErrors back to an empty object
  const [fieldErrors, setFieldErrors] = useState({});

  // Check for URL parameters
  useEffect(() => {
    // Check if the user was redirected from registration
    const registered = searchParams.get('registered')
    if (registered === 'true') {
      Swal.fire({
        title: 'Success!',
        text: 'Registration successful! Please log in.',
        icon: 'success',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
      })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Run only once when component mounts

  const handleChange = (e) => { // Removed type React.ChangeEvent<HTMLInputElement>
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    
    // Clear error for the field being edited
    if (fieldErrors[name]) { // Removed "as keyof typeof fieldErrors"
      setFieldErrors(prev => {
        const updatedErrors = { ...prev };
        delete updatedErrors[name];
        return updatedErrors;
      });
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setFieldErrors({})

    try {
      // Make the login request directly with axios for more control
      const response = await axios.post(`${API_BASE_URL}/users/login/`, {
        email: formData.email,
        password: formData.password,
        ...(formData.two_factor_code && { two_factor_code: formData.two_factor_code })
      });
      
      console.log('Login response:', response.data);
      
      // Check if 2FA is needed
      if (response.data.requires_2fa) {
        setNeeds2FA(true);
        setUserId(response.data.user_id);
        setIsLoading(false);
        return;
      }

      // If we have tokens, store them
      if (response.data.access && response.data.refresh) {
        // Explicitly store tokens in localStorage
        localStorage.setItem('accessToken', response.data.access);
        localStorage.setItem('refreshToken', response.data.refresh);
        
        // Store user data if available
        if (response.data.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        
        // Set authorization header for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        console.log('Tokens stored in localStorage:', {
          accessToken: localStorage.getItem('accessToken') ? 'present' : 'missing',
          refreshToken: localStorage.getItem('refreshToken') ? 'present' : 'missing'
        });
        
        Swal.fire({
          title: 'Success!',
          text: 'Logged in successfully',
          icon: 'success',
          toast: true,
          position: 'top-end',
          showConfirmButton: false,
          timer: 3000,
          timerProgressBar: true
        });

        // Check if there are any connected accounts
        await checkConnectedAccounts();
      } else {
        throw new Error('No authentication tokens received from server');
      }
    } catch (err) {
      console.error('Error during login:', err);
      
      // Handle different types of errors
      if (err.response?.status === 401) {
        setFieldErrors({ general: ['Invalid email or password'] });
      } else if (err.response?.data?.detail) {
        setFieldErrors({ general: [err.response.data.detail] });
      } else if (err.response?.data?.errors) {
        setFieldErrors(err.response.data.errors);
      } else {
        setFieldErrors({ general: [err.message || 'An unexpected error occurred'] });
      }

      Swal.fire({
        title: 'Login Failed',
        text: err.response?.data?.detail || err.message || 'An unexpected error occurred',
        icon: 'error',
        confirmButtonText: 'OK'
      });
    } finally {
      setIsLoading(false);
    }
  }

  // Function to check if user has connected accounts
  const checkConnectedAccounts = async () => {
    try {
      // Set loading state
      setIsLoading(true);
      
      // Get the token from localStorage
      const token = localStorage.getItem('accessToken');
      if (!token) {
        console.error("No access token found after login");
        // If no token, just redirect to dashboard
        navigate("/dashboard");
        return;
      }
      
      console.log("Checking connected accounts with token:", token.slice(0, 10) + '...');

      try {
        // Get connected accounts using axios
        const response = await axios.get(`${API_BASE_URL}/users/accounts/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        console.log("Connected accounts response:", JSON.stringify(response.data));

        // Check if user has no connected accounts
        if (!response.data?.accounts || 
            (Array.isArray(response.data.accounts) && response.data.accounts.length === 0)) {
          // Show a notification that we're redirecting to connect platforms
          Swal.fire({
            title: 'Action Required',
            text: 'You need to connect at least one social media account to continue',
            icon: 'info',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
          });
          
          // Redirect to connect platforms page
          navigate("/platform-connect?required=true");
          return;
        } else {
          // User has connected accounts, proceed to dashboard or return URL
          const returnUrl = searchParams.get('returnUrl') || '/dashboard';
          navigate(returnUrl);
        }
      } catch (apiError) {
        console.error("API error when checking accounts:", apiError);
        console.log("Error status:", apiError.response?.status);
        console.log("Error data:", JSON.stringify(apiError.response?.data));
        
        // Check if it's a 404 (endpoint doesn't exist) or other server error
        if (apiError.response?.status === 404) {
          console.log("API endpoint not found, assuming this is an older API version without the accounts endpoint");
          // If API endpoint doesn't exist, just go to dashboard instead of platform connect
          navigate("/dashboard");
        } else if (apiError.response?.status === 401) {
          console.log("Authentication error, redirecting to login");
          // Authentication error, redirect to login
          Swal.fire({
            title: 'Session Expired',
            text: 'Your session has expired. Please log in again.',
            icon: 'warning',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
          });
          navigate("/login");
        } else {
          // For other errors, go to dashboard
          console.log("Other API error, proceeding to dashboard");
          navigate("/dashboard");
        }
      }
    } catch (error) {
      console.error("Error in checkConnectedAccounts function:", error);
      // Redirect to dashboard as fallback
      navigate("/dashboard");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // Main container styling
    <div className="flex h-screen w-full items-center justify-center bg-slate-900">
      {/* Form container (Card replacement) */}
      <div className="w-full max-w-[550px] border border-slate-700 rounded-xl p-6 sm:p-8 bg-slate-800/90 shadow-xl backdrop-blur-sm">
        {/* Header section (CardHeader replacement) */}
        <div className="mb-6 text-center">
          {/* Logo placeholder */}
          <div className="flex justify-center mb-4">
            <span className="text-4xl font-bold text-blue-400">Linkly</span>
          </div>
          {/* Title (CardTitle replacement) */}
          <h2 className="text-2xl font-semibold mb-2 text-white">Sign in to Linkly</h2>
          {/* Description (CardDescription replacement) */}
          <p className="text-slate-300 text-sm mb-3">Enter your credentials to access your account</p>

          {/* General error message banner */}
          {fieldErrors.general && (
            <div className="bg-red-900/50 border border-red-700 text-red-200 p-3 rounded-lg mt-3 text-sm" role="alert">
              <span>{fieldErrors.general[0]}</span>
            </div>
          )}
        </div>

        {/* Auth type selector tabs */}
        <div className="flex w-full border border-slate-600 rounded-lg overflow-hidden mb-6">
          <Link 
            to="/login"
            className="flex-1 py-3 px-4 flex items-center justify-center gap-2 text-base transition-all duration-200 bg-blue-600 text-white font-medium"
          >
            Sign In
          </Link>
          <Link 
            to="/signup"
            className="flex-1 py-3 px-4 flex items-center justify-center gap-2 text-base transition-all duration-200 text-slate-300 hover:bg-slate-700"
          >
            Create Account
          </Link>
        </div>

        {/* Content section (CardContent replacement) */}
        <div>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {!needs2FA ? (
              <>
                {/* Email Field */}
                <div className="mb-4">
                  <label htmlFor="email" className="block text-sm font-medium mb-1 text-slate-200">Email</label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="name@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    disabled={isLoading}
                    className={`w-full p-2.5 mt-1 border bg-slate-700/80 text-white ${fieldErrors.email ? 'border-red-500' : 'border-slate-600'} rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  />
                  {fieldErrors.email && (
                    <p className="text-red-400 text-xs mt-1">{fieldErrors.email[0]}</p>
                  )}
                </div>

                {/* Password Field */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-1">
                    <label htmlFor="password" className="block text-sm font-medium text-slate-200">Password</label>
                    {/* Use react-router-dom Link */}
                    <Link to="/forgot-password" className="text-xs text-blue-400 hover:text-blue-300 font-medium">
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      disabled={isLoading}
                      className={`w-full p-2.5 pr-16 mt-1 border bg-slate-700/80 text-white ${fieldErrors.password ? 'border-red-500' : 'border-slate-600'} rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    />
                    {/* Button for show/hide password */}
                    <button
                      type="button"
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-300 hover:text-white"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={isLoading}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {/* Replace icons with text */}
                      {showPassword ? 'Hide' : 'Show'}
                    </button>
                  </div>
                  {fieldErrors.password && (
                    <p className="text-red-400 text-xs mt-1">{fieldErrors.password[0]}</p>
                  )}
                </div>
              </>
            ) : (
              /* 2FA Field */
              <div className="mb-4">
                <label htmlFor="two_factor_code" className="block text-sm font-medium mb-1 text-slate-200">Two-Factor Authentication Code</label>
                <input
                  id="two_factor_code"
                  name="two_factor_code"
                  type="text"
                  placeholder="123456"
                  value={formData.two_factor_code}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  className={`w-full p-2.5 mt-1 border bg-slate-700/80 text-white ${fieldErrors.two_factor_code ? 'border-red-500' : 'border-slate-600'} rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500`}
                />
                {fieldErrors.two_factor_code && (
                  <p className="text-red-400 text-xs mt-1">{fieldErrors.two_factor_code[0]}</p>
                )}
              </div>
            )}

            {/* Submit Button */}
            <button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium p-3 rounded-lg mt-2 transition-colors shadow-md"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {needs2FA ? "Verifying..." : "Signing in..."}
                </span>
              ) : needs2FA ? (
                "Verify Code"
              ) : (
                "Sign in"
              )}
            </button>

            {/* Signup Link */}
            <div className="text-center text-sm mt-3 text-slate-300">
              Don't have an account?{" "}
              {/* Use react-router-dom Link */}
              <Link to="/signup" className="text-blue-400 hover:text-blue-300 font-medium">
                Sign up
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
} 
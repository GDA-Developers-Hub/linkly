"use client"

import React, { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import Swal from 'sweetalert2'
import axios from 'axios'
import API_BASE_URL from "../Utils/BaseUrl"

export function SignupForm() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [accountType, setAccountType] = useState('personal')

  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    password2: "",
    is_business: false,
    company_name: "",
    phone_number: ""
  })

  const [fieldErrors, setFieldErrors] = useState({})

  const handleAccountTypeChange = (value) => {
    setAccountType(value)
    setFormData(prev => ({ 
      ...prev, 
      is_business: value === 'business' 
    }))
    
    setFieldErrors({})
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
    
    if (fieldErrors[name]) {
      setFieldErrors(prev => {
        const updatedErrors = { ...prev }
        delete updatedErrors[name]
        return updatedErrors
      })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setFieldErrors({})

    let errors = {}
    if (formData.password !== formData.password2) {
      errors.password = ["Passwords don't match"]
    }
    if (!formData.username.trim()) {
      errors.username = ["Username is required"]
    }
    if (formData.is_business && !formData.company_name.trim()) {
      errors.company_name = ["Company name is required for business accounts"]
    }
    if (Object.keys(errors).length > 0) {
        setFieldErrors(errors)
        setIsLoading(false)
        Swal.fire({
            title: 'Validation Error',
            text: 'Please check the highlighted fields.',
            icon: 'warning',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        })
        return
    }

    try {
      console.log('Submitting registration data:', { ...formData, password: '***', password2: '***' })
      
      // Fix the URL template string
      const registerUrl = `${API_BASE_URL}/users/register/`;
      console.log('Using register URL:', registerUrl);
      
      // Use fetch instead of axios to see if it's an axios-specific issue
      const response = await fetch(registerUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password2: formData.password2,
          is_business: formData.is_business,
          company_name: formData.company_name || "",
          phone_number: formData.phone_number || ""
        }),
        // No credentials/cookies
        credentials: 'omit' 
      });
      
      // Check response type
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        console.log('Server response:', data);
        
        if (!response.ok) {
          // Handle non-200 responses
          if (data.errors) {
            setFieldErrors(data.errors);
            throw new Error('Please check the highlighted fields.');
          } else if (data.message) {
            setFieldErrors({ general: [data.message] });
            throw new Error(data.message);
          } else {
            throw new Error(`Server responded with status: ${response.status}`);
          }
        }
        
        if (data.status === 'success') {
          Swal.fire({
            title: 'Success!',
            text: 'Account created successfully',
            icon: 'success',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
          });
          
          navigate("/login?registered=true");
        } else {
          throw new Error(data.message || 'Registration failed');
        }
      } else {
        // Handle non-JSON response (HTML, etc.)
        const text = await response.text();
        console.error('Non-JSON response received:', text.substring(0, 500) + '...');
        
        // Log detailed information for debugging
        console.error('Response status:', response.status);
        console.error('Response headers:', Object.fromEntries(response.headers.entries()));
        
        throw new Error(`Server error: Received non-JSON response (${response.status})`);
      }
    } catch (err) {
      console.error('Registration error in handleSubmit:', err);
      
      // The error message is already handled above for response errors
      const errorMessage = err.message || 'An unexpected error occurred';
      
      // Only set fieldErrors if not already set
      if (!Object.keys(fieldErrors).length) {
        setFieldErrors({ general: [errorMessage] });
      }
      
      Swal.fire({
        title: 'Registration Failed',
        text: errorMessage,
        icon: 'error',
        confirmButtonText: 'OK'
      });
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen w-full items-center justify-center bg-slate-900">
      <div className="w-full max-w-[550px] border border-slate-700 rounded-xl p-6 sm:p-8 bg-slate-800/90 shadow-xl backdrop-blur-sm">
        <div className="mb-6 text-center">
          <div className="flex justify-center mb-4">
            <span className="text-4xl font-bold text-blue-400">Linkly</span>
          </div>
          <h2 className="text-2xl font-semibold mb-2 text-white">Create an account</h2>
          <p className="text-slate-300 text-sm">Enter your information to get started with Linkly</p>
          
          {fieldErrors.general && (
            <div className="bg-red-900/50 border border-red-700 text-red-200 p-3 rounded-lg mt-3 text-sm" role="alert">
              <span>{fieldErrors.general[0]}</span>
            </div>
          )}
        </div>
        
        <div className="space-y-6">
          {/* Auth type selector tabs */}
          <div className="flex w-full border border-slate-600 rounded-lg overflow-hidden mb-6">
            <Link 
              to="/login"
              className="flex-1 py-3 px-4 flex items-center justify-center gap-2 text-base transition-all duration-200 text-slate-300 hover:bg-slate-700"
            >
              Sign In
            </Link>
            <Link 
              to="/signup"
              className="flex-1 py-3 px-4 flex items-center justify-center gap-2 text-base transition-all duration-200 bg-blue-600 text-white font-medium"
            >
              Create Account
            </Link>
          </div>
          
          {/* Account type selector tabs */}
          <div className="flex w-full border border-slate-600 rounded-lg overflow-hidden">
            <button 
              type="button"
              className={`flex-1 py-3 px-4 flex items-center justify-center gap-2 text-base transition-all duration-200 ${
                accountType === 'personal' 
                  ? 'bg-blue-600 text-white font-medium' 
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
              onClick={() => handleAccountTypeChange('personal')}
            >
              <span className="inline-block mr-1.5">👤</span> Personal
            </button>
            <button 
              type="button"
              className={`flex-1 py-3 px-4 flex items-center justify-center gap-2 text-base transition-all duration-200 ${
                accountType === 'business' 
                  ? 'bg-blue-600 text-white font-medium' 
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
              onClick={() => handleAccountTypeChange('business')}
            >
              <span className="inline-block mr-1.5">🏢</span> Business
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-200 mb-1">
                  Email address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors bg-slate-700/80 text-white ${
                    fieldErrors.email ? 'border-red-500 bg-red-900/30' : 'border-slate-600'
                  }`}
                  placeholder="Enter your email"
                  required
                />
                {fieldErrors.email && (
                  <p className="mt-1 text-sm text-red-400">{fieldErrors.email[0]}</p>
                )}
              </div>

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-slate-200 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors bg-slate-700/80 text-white ${
                    fieldErrors.username ? 'border-red-500 bg-red-900/30' : 'border-slate-600'
                  }`}
                  placeholder="Choose a username"
                  required
                />
                {fieldErrors.username && (
                  <p className="mt-1 text-sm text-red-400">{fieldErrors.username[0]}</p>
                )}
              </div>

              {accountType === 'business' && (
                <div>
                  <label htmlFor="company_name" className="block text-sm font-medium text-slate-200 mb-1">
                    Company Name
                  </label>
                  <input
                    type="text"
                    id="company_name"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleChange}
                    className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors bg-slate-700/80 text-white ${
                      fieldErrors.company_name ? 'border-red-500 bg-red-900/30' : 'border-slate-600'
                    }`}
                    placeholder="Enter company name"
                  />
                  {fieldErrors.company_name && (
                    <p className="mt-1 text-sm text-red-400">{fieldErrors.company_name[0]}</p>
                  )}
                </div>
              )}

              <div>
                <label htmlFor="phone_number" className="block text-sm font-medium text-slate-200 mb-1">
                  Phone Number (optional)
                </label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-slate-700/80 text-white"
                  placeholder="Enter phone number"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-200 mb-1">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors bg-slate-700/80 text-white ${
                      fieldErrors.password ? 'border-red-500 bg-red-900/30' : 'border-slate-600'
                    }`}
                    placeholder="Create a password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-300 hover:text-white"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
                {fieldErrors.password && (
                  <p className="mt-1 text-sm text-red-400">{fieldErrors.password[0]}</p>
                )}
              </div>

              <div>
                <label htmlFor="password2" className="block text-sm font-medium text-slate-200 mb-1">
                  Confirm Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password2"
                    name="password2"
                    value={formData.password2}
                    onChange={handleChange}
                    className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors bg-slate-700/80 text-white ${
                      fieldErrors.password2 ? 'border-red-500 bg-red-900/30' : 'border-slate-600'
                    }`}
                    placeholder="Confirm your password"
                    required
                  />
                </div>
                {fieldErrors.password2 && (
                  <p className="mt-1 text-sm text-red-400">{fieldErrors.password2[0]}</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-3 px-4 text-white bg-blue-600 rounded-lg font-medium shadow-md ${
                isLoading 
                  ? 'opacity-70 cursor-not-allowed' 
                  : 'hover:bg-blue-700 active:bg-blue-800'
              } transition-colors duration-200`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </span>
              ) : (
                'Create Account'
              )}
            </button>

            <p className="text-center text-sm text-slate-300 mt-4">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">
                Sign in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
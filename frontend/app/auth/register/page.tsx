"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Eye, EyeOff } from "lucide-react"
import Swal from 'sweetalert2'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useAuth } from "@/contexts/auth-context"

export default function RegisterPage() {
  const { register, isLoading } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    password_confirm: "",
    account_type: "personal",
    terms_accepted: false,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }))
    
    // Clear error when user edits field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const handleRadioChange = (value: string) => {
    setFormData((prev) => ({ ...prev, account_type: value }))
  }
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.first_name) {
      newErrors.first_name = "First name is required"
    }
    
    if (!formData.last_name) {
      newErrors.last_name = "Last name is required"
    }
    
    if (!formData.email) {
      newErrors.email = "Email is required"
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid"
    }
    
    if (!formData.password) {
      newErrors.password = "Password is required"
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters"
    }
    
    if (!formData.password_confirm) {
      newErrors.password_confirm = "Please confirm your password"
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = "Passwords do not match"
    }
    
    if (!formData.terms_accepted) {
      newErrors.terms_accepted = "You must accept the Terms of Service and Privacy Policy"
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      // Display validation errors using SweetAlert2
      const errorMessage = Object.entries(errors)
        .map(([field, message]) => `${field}: ${message}`)
        .join('<br>')
      
      Swal.fire({
        title: 'Validation Error',
        html: errorMessage,
        icon: 'error',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
      })
      return
    }

    try {
      await register({
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm,
        account_type: formData.account_type as "personal" | "business",
      })
    } catch (error) {
      // Error is handled by the auth context
      console.error("Registration submission error:", error)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="mx-auto max-w-md w-full">
        <CardHeader className="space-y-2 text-center">
          <div className="flex justify-center mb-4">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-[#FF8C2A]">
              <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-3xl">L</div>
            </div>
            <span className="text-[#1E5AA8] font-bold text-3xl ml-2 self-center">inkly</span>
          </div>
          <CardTitle className="text-2xl">Create an account</CardTitle>
          <CardDescription>Sign up for Linkly to manage your social media</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">First name</Label>
                <Input
                  id="first_name"
                  name="first_name"
                  placeholder="John"
                  required
                  value={formData.first_name}
                  onChange={handleChange}
                  className={errors.first_name ? "border-red-500" : ""}
                />
                {errors.first_name && <p className="text-red-500 text-sm mt-1">{errors.first_name}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Last name</Label>
                <Input
                  id="last_name"
                  name="last_name"
                  placeholder="Doe"
                  required
                  value={formData.last_name}
                  onChange={handleChange}
                  className={errors.last_name ? "border-red-500" : ""}
                />
                {errors.last_name && <p className="text-red-500 text-sm mt-1">{errors.last_name}</p>}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="name@example.com"
                required
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? "border-red-500" : ""}
              />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className={errors.password ? "border-red-500" : ""}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                  <span className="sr-only">Toggle password visibility</span>
                </Button>
              </div>
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password_confirm">Confirm Password</Label>
              <Input
                id="password_confirm"
                name="password_confirm"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                required
                value={formData.password_confirm}
                onChange={handleChange}
                className={errors.password_confirm ? "border-red-500" : ""}
              />
              {errors.password_confirm && <p className="text-red-500 text-sm mt-1">{errors.password_confirm}</p>}
            </div>
            <div className="space-y-2">
              <Label>Account type</Label>
              <RadioGroup value={formData.account_type} onValueChange={handleRadioChange} className="flex">
                <div className="flex items-center space-x-2 flex-1">
                  <RadioGroupItem value="personal" id="personal" />
                  <Label htmlFor="personal" className="font-normal">
                    Personal
                  </Label>
                </div>
                <div className="flex items-center space-x-2 flex-1">
                  <RadioGroupItem value="business" id="business" />
                  <Label htmlFor="business" className="font-normal">
                    Business
                  </Label>
                </div>
              </RadioGroup>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="terms_accepted"
                name="terms_accepted"
                className={`h-4 w-4 rounded border-gray-300 ${errors.terms_accepted ? "border-red-500" : ""}`}
                required
                checked={formData.terms_accepted}
                onChange={handleChange}
                aria-label="Accept Terms and Conditions"
              />
              <Label htmlFor="terms_accepted" className="text-sm font-normal">
                I agree to the{" "}
                <Link href="/terms" className="text-[#1E5AA8] hover:underline">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" className="text-[#1E5AA8] hover:underline">
                  Privacy Policy
                </Link>
              </Label>
            </div>
            {errors.terms_accepted && <p className="text-red-500 text-sm mt-1">{errors.terms_accepted}</p>}
            <Button type="submit" className="w-full bg-[#FF8C2A] hover:bg-[#e67e25]" disabled={isLoading}>
              {isLoading ? "Creating Account..." : "Create Account"}
            </Button>
          </form>
        </CardContent>
        <CardFooter>
          <div className="text-center w-full text-sm">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-[#1E5AA8] hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}

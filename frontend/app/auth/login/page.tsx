"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Eye, EyeOff, Facebook, Instagram, Linkedin, Twitter } from "lucide-react"
import Swal from 'sweetalert2'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/contexts/auth-context"
import Image from "next/image"
import logo from "@/public/logo-no-bg.png"

export default function LoginPage() {
  const { login, isLoading } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error when user edits field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.email) {
      newErrors.email = "Email is required"
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid"
    }
    
    if (!formData.password) {
      newErrors.password = "Password is required"
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
      await login(formData)
    } catch (error) {
      // Error is handled by the auth context
      console.error("Login submission error:", error)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="mx-auto max-w-md w-full">
        <CardHeader className="space-y-2 text-center">
          <div className="flex justify-center mb-4">
            <Image src={logo} alt="Logo" width={120} height={120} />
          </div>
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>Sign in to your Linkly account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
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
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  id="remember" 
                  className="h-4 w-4 rounded border-gray-300" 
                  aria-label="Remember me"
                />
                <Label htmlFor="remember" className="text-sm font-normal">
                  Remember me
                </Label>
              </div>
              <Link href="/auth/reset-password" className="text-sm text-[#1E5AA8] hover:underline">
                Forgot password?
              </Link>
            </div>
            <Button type="submit" className="w-full bg-[#FF8C2A] hover:bg-[#e67e25]" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator />
              </div>
            </div>

            {/* <div className="mt-4 grid grid-cols-4 gap-2">
              <Button variant="outline" className="w-full">
                <Facebook className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full">
                <Twitter className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full">
                <Instagram className="h-4 w-4" />
              </Button>
              <Button variant="outline" className="w-full">
                <Linkedin className="h-4 w-4" />
              </Button>
            </div> */}
          </div>
        </CardContent>
        <CardFooter>
          <div className="text-center w-full text-sm">
            Don&apos;t have an account?{" "}
            <Link href="/auth/register" className="text-[#1E5AA8] hover:underline font-medium">
              Sign up
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}

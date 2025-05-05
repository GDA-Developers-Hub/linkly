'use client'

import dynamic from 'next/dynamic'
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/contexts/auth-context"

// Dynamically import the Toaster component to reduce initial bundle size
const Toaster = dynamic(() => import("@/components/ui/toaster").then(mod => mod.Toaster), {
  ssr: false
})

export default function ClientProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
      <AuthProvider>
        {children}
        <Toaster />
      </AuthProvider>
    </ThemeProvider>
  )
} 
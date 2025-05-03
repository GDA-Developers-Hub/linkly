import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/contexts/auth-context"
import { Toaster } from "@/components/ui/toaster"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Linkly - Social Media Management Platform",
  description: "Connect and manage all your social media accounts in one place. Schedule posts, analyze performance, and grow your social media presence.",
  generator: 'v0.dev',
  metadataBase: new URL('https://linkly-social.web.app'),
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "32x32" },
      { url: "/logo-no-bg.png", type: "image/png", sizes: "192x192" }
    ],
    shortcut: ["/favicon.ico"],
    apple: [
      { url: "/logo-no-bg.png", sizes: "180x180", type: "image/png" }
    ]
  },
  manifest: "/manifest.json",
  openGraph: {
    title: "Linkly - Social Media Management Platform",
    description: "Connect and manage all your social media accounts in one place. Schedule posts, analyze performance, and grow your social media presence.",
    images: [{ url: "/logo-no-bg.png", width: 400, height: 400, alt: "Linkly Logo" }],
    type: "website",
    siteName: "Linkly",
    url: "https://linkly-social.web.app"
  },
  twitter: {
    card: "summary_large_image",
    title: "Linkly - Social Media Management Platform",
    description: "Connect and manage all your social media accounts in one place",
    images: [{ url: "/logo-no-bg.png", alt: "Linkly Logo" }],
    site: "@linkly"
  }
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}

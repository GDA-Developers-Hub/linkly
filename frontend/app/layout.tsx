'use client'

import React from "react"
import { Inter } from "next/font/google"
import "./globals.css"
import ClientProviders from "@/components/client-providers"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>Linkly - Social Media Management Platform</title>
        <meta 
          name="description" 
          content="Connect and manage all your social media accounts in one place. Schedule posts, analyze performance, and grow your social media presence." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="icon" type="image/png" sizes="192x192" href="/logo-no-bg.png" />
        <link rel="apple-touch-icon" type="image/png" sizes="180x180" href="/logo-no-bg.png" />
        <link rel="manifest" href="/manifest.json" />
        
        {/* Open Graph */}
        <meta property="og:title" content="Linkly - Social Media Management Platform" />
        <meta property="og:description" content="Connect and manage all your social media accounts in one place. Schedule posts, analyze performance, and grow your social media presence." />
        <meta property="og:image" content="/logo-no-bg.png" />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="Linkly" />
        <meta property="og:url" content="https://linkly-social.web.app" />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Linkly - Social Media Management Platform" />
        <meta name="twitter:description" content="Connect and manage all your social media accounts in one place" />
        <meta name="twitter:image" content="/logo-no-bg.png" />
        <meta name="twitter:site" content="@linkly" />
      </head>
      <body className={inter.className}>
        <ClientProviders>{children}</ClientProviders>
      </body>
    </html>
  )
}

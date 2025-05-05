import React from "react"
import { Inter } from "next/font/google"
import "./globals.css"
import ClientProviders from "@/components/client-providers"
import { Metadata } from "next"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: 'Linkly - Social Media Management Platform',
  description: 'Connect and manage all your social media accounts in one place. Schedule posts, analyze performance, and grow your social media presence.',
  openGraph: {
    title: 'Linkly - Social Media Management Platform',
    description: 'Connect and manage all your social media accounts in one place. Schedule posts, analyze performance, and grow your social media presence.',
    images: ['/logo-no-bg.png'],
    type: 'website',
    siteName: 'Linkly',
    url: 'https://linkly-social.web.app'
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Linkly - Social Media Management Platform',
    description: 'Connect and manage all your social media accounts in one place',
    images: ['/logo-no-bg.png'],
    creator: '@linkly'
  },
  icons: {
    icon: '/favicon.ico',
    apple: '/logo-no-bg.png'
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
        <ClientProviders>{children}</ClientProviders>
      </body>
    </html>
  )
}

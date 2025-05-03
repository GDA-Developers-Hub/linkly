"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  LayoutDashboard,
  Calendar,
  BarChart3,
  Settings,
  FileText,
  Menu,
  X,
  Hash,
  Sparkles,
  Link2,
  ChartBarIcon,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useIsMobile } from "@/components/ui/use-mobile"

interface SidebarProps {
  className?: string
}

export function AppSidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const isMobile = useIsMobile()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Reset sidebar state when switching between mobile and desktop
  useEffect(() => {
    if (isMobile) {
      setIsCollapsed(false)
      setIsSidebarOpen(false)
    } else {
      setIsSidebarOpen(true)
    }
  }, [isMobile])

  const toggleSidebar = () => {
    if (isMobile) {
      setIsSidebarOpen(!isSidebarOpen)
    } else {
      setIsCollapsed(!isCollapsed)
    }
  }

  const routes = [
    {
      label: "Dashboard",
      icon: LayoutDashboard,
      href: "/dashboard",
      active: pathname === "/dashboard",
    },
    {
      label: "Platform Connect",
      icon: Link2,
      href: "/dashboard/platform-connect",
      active: pathname === "/dashboard/platform-connect",
    },
    {
      label: "Posts",
      icon: FileText,
      href: "/dashboard/posts",
      active: pathname.includes("/dashboard/posts"),
    },
    {
      label: "Caption Generator",
      icon: Sparkles,
      href: "/dashboard/caption-generator",
      active: pathname === "/dashboard/caption-generator",
    },
    {
      label: "Hashtag Research",
      icon: Hash,
      href: "/dashboard/hashtags",
      active: pathname === "/dashboard/hashtags",
    },
    {
      label: "Calendar",
      icon: Calendar,
      href: "/dashboard/calendar",
      active: pathname === "/dashboard/calendar",
    },
    {
      label: "Analytics",
      icon: BarChart3,
      href: "/dashboard/analytics",
      active: pathname === "/dashboard/analytics",
    },
    {
      label: "Settings",
      icon: Settings,
      href: "/dashboard/settings",
      active: pathname === "/dashboard/settings",
    },
    {
      name: 'Google Ads',
      href: '/dashboard/google-ads',
      icon: ChartBarIcon,
      current: pathname === '/dashboard/google-ads',
    },
  ]

  return (
    <>
      {/* Mobile Toggle Button - Always visible on mobile */}
      {isMobile && (
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="fixed top-4 left-4 z-50 md:hidden">
          {isSidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </Button>
      )}

      {/* Desktop Toggle Button - Only visible when sidebar is collapsed */}
      {!isMobile && isCollapsed && (
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="fixed top-4 left-4 z-50 hidden md:flex">
          <Menu className="h-6 w-6" />
        </Button>
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex flex-col border-r bg-background shadow-md transition-all duration-300",
          isMobile
            ? isSidebarOpen
              ? "w-64 translate-x-0"
              : "w-64 -translate-x-full"
            : isCollapsed
              ? "w-16 translate-x-0"
              : "w-64 translate-x-0",
          className,
        )}
      >
        <div
          className={cn(
            "flex h-16 items-center border-b px-4",
            isCollapsed && !isMobile ? "justify-center" : "justify-between",
          )}
        >
          {(!isCollapsed || isMobile) && (
            <Link href="/dashboard" className="flex items-center gap-2">
              <Image 
                src="/logo-no-bg.png" 
                alt="Linkly" 
                width={32} 
                height={32} 
                className="h-8 w-auto"
              />
              <span className="font-bold text-lg">Linkly</span>
            </Link>
          )}
          {/* Show just the logo when collapsed */}
          {isCollapsed && !isMobile && (
            <Link href="/dashboard" className="flex items-center justify-center">
              <Image 
                src="/logo-no-bg.png" 
                alt="Linkly" 
                width={24} 
                height={24} 
                className="h-8 w-auto"
              />
            </Link>
          )}

          {/* Toggle button inside sidebar - only visible on desktop and when sidebar is expanded */}
          {!isMobile && !isCollapsed && (
            <Button variant="ghost" size="icon" onClick={toggleSidebar} className="h-8 w-8">
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        <ScrollArea className="flex-1 py-2">
          <nav className="grid gap-1 px-2">
            {routes.map((route) => (
              <Link
                key={route.href}
                href={route.href}
                onClick={() => isMobile && setIsSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  route.active 
                    ? "bg-primary text-primary-foreground" 
                    : "hover:bg-muted",
                  isCollapsed && !isMobile ? "justify-center" : "",
                )}
              >
                <route.icon className={cn("h-5 w-5", route.active ? "text-primary-foreground" : "text-muted-foreground")} />
                {(!isCollapsed || isMobile) && <span>{route.label}</span>}
              </Link>
            ))}
          </nav>
        </ScrollArea>
      </aside>
    </>
  )
}

"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import { Menu, X } from "lucide-react"
import logo from "@/public/logo-no-bg.png"
import { motion } from "framer-motion"
import { useTheme } from "next-themes"

export function MainNav() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const pathname = usePathname()
  const { theme } = useTheme()

  // Handle scroll event to change header appearance
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const isActive = (path: string) => {
    return pathname === path
  }

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className={`sticky top-0 z-50 border-b transition-all duration-300 ${
        scrolled ? "bg-background/80 backdrop-blur-md" : "bg-background"
      }`}
    >
      <div className="container mx-auto flex h-20 items-center justify-between px-5">
        <div className="flex items-center gap-2 w-48 h-36">
          <Link href="/" className="flex items-center">
            <Image 
              src={logo} 
              alt="Linkly Logo" 
              className="w-32 h-auto filter brightness-110 contrast-125"
              style={{ 
                filter: theme === 'dark' ? 'brightness(1.4) contrast(1.1)' : 'none' 
              }}
            />
          </Link>
        </div>

        <div className="hidden md:flex items-center gap-6">
          <nav className="flex items-center gap-6">
            <Link
              href="/#features"
              className={`text-sm font-medium hover:text-primary transition-colors ${
                isActive("/#features") ? "text-primary" : ""
              }`}
            >
              Features
            </Link>
            <Link
              href="/#how-it-works"
              className={`text-sm font-medium hover:text-primary transition-colors ${
                isActive("/#how-it-works") ? "text-primary" : ""
              }`}
            >
              How It Works
            </Link>
            <Link
              href="/pricing"
              className={`text-sm font-medium hover:text-primary transition-colors ${
                isActive("/pricing") ? "text-primary" : ""
              }`}
            >
              Pricing
            </Link>
            <Link
              href="/#testimonials"
              className={`text-sm font-medium hover:text-primary transition-colors ${
                isActive("/#testimonials") ? "text-primary" : ""
              }`}
            >
              Testimonials
            </Link>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="ghost" asChild>
              <Link href="/auth/login">Log in</Link>
            </Button>
            <Button asChild className="bg-[#FF8C2A] hover:bg-[#e67e25] text-white">
              <Link href="/auth/register">Try for free</Link>
            </Button>
            <ModeToggle />
          </div>
        </div>

        <div className="flex items-center gap-2 md:hidden">
          <ModeToggle />
          <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </div>

      {/* Mobile menu */}
      <div
        className={`md:hidden border-t overflow-hidden transition-all duration-300 ${
          isMenuOpen ? "max-h-96" : "max-h-0"
        }`}
      >
        <nav className="flex flex-col gap-4 p-4">
          <Link
            href="/#features"
            className={`text-sm font-medium hover:text-primary ${isActive("/#features") ? "text-primary" : ""}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Features
          </Link>
          <Link
            href="/#how-it-works"
            className={`text-sm font-medium hover:text-primary ${isActive("/#how-it-works") ? "text-primary" : ""}`}
            onClick={() => setIsMenuOpen(false)}
          >
            How It Works
          </Link>
          <Link
            href="/pricing"
            className={`text-sm font-medium hover:text-primary ${isActive("/pricing") ? "text-primary" : ""}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Pricing
          </Link>
          <Link
            href="/#testimonials"
            className={`text-sm font-medium hover:text-primary ${isActive("/#testimonials") ? "text-primary" : ""}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Testimonials
          </Link>
          <div className="flex flex-col gap-2 pt-2 border-t">
            <Button variant="outline" asChild className="w-full">
              <Link href="/auth/login">Log in</Link>
            </Button>
            <Button asChild className="w-full bg-[#FF8C2A] hover:bg-[#e67e25] text-white">
              <Link href="/auth/register">Try for free</Link>
            </Button>
          </div>
        </nav>
      </div>
    </motion.header>
  )
} 
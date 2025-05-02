"use client"

import type React from "react"
import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { motion, useInView } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import Image from "next/image"
import logo from "@/public/logo-no-bg.png"
import socialbu from "@/public/socialbu-logo.png"
import {
  ChevronRight,
  ArrowRight,
  Menu,
  X,
  Globe,
  BarChart3,
  Zap,
  MessageSquare,
  Share2,
  Users,
  TrendingUp,
  ExternalLink,
} from "lucide-react"
import { PlatformIcons } from "@/components/platform-icons"
import { SocialIntegrationIllustrationV2 } from "@/components/illustrations/social-integration-illustration-v2"
import { useTheme } from "next-themes"
import { useIsMobile } from "@/components/ui/use-mobile"

interface Testimonial {
  id: number
  quote: string
  author: string
  role: string
  company?: string
  avatar?: string
}

interface Partner {
  id: number
  name: string
  logo: string
  description: string
}

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6 },
  },
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
}

const fadeInScale = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5 },
  },
}

const fadeInLeft = {
  hidden: { opacity: 0, x: -50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.6 },
  },
}

const fadeInRight = {
  hidden: { opacity: 0, x: 50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.6 },
  },
}

// Custom hook for scroll animations
function useScrollAnimation(threshold = 0.2) {
  const ref = useRef<HTMLElement>(null)
  const isInView = useInView(ref, { once: true, amount: threshold })

  return [ref, isInView] as const
}

export function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const { theme } = useTheme()
  const isMobile = useIsMobile()

  const [testimonials] = useState<Testimonial[]>([
    {
      id: 1,
      quote: "Linkly has transformed how we manage our social media. The time savings alone are worth every penny!",
      author: "Sarah Johnson",
      role: "Marketing Director",
      company: "TechVision Inc.",
      avatar: "/placeholder.svg?height=80&width=80",
    },
    {
      id: 2,
      quote: "The analytics and insights have helped us increase engagement by over 40% in just two months.",
      author: "Michael Chen",
      role: "Social Media Manager",
      company: "Global Brands",
      avatar: "/placeholder.svg?height=80&width=80",
    },
    {
      id: 3,
      quote: "As a small business owner, Linkly gives me enterprise-level tools at a price I can afford.",
      author: "Jessica Williams",
      role: "Founder",
      company: "Bright Ideas Co.",
      avatar: "/placeholder.svg?height=80&width=80",
    },
  ])

  const [partners] = useState<Partner[]>([
    {
      id: 1,
      name: "SocialBu",
      logo: "/placeholder.svg?height=60&width=180",
      description: "Our premier partner for advanced social media analytics and reporting.",
    },
    {
      id: 2,
      name: "MarketPro",
      logo: "/placeholder.svg?height=60&width=180",
      description: "Integration partner for enhanced marketing automation.",
    },
    {
      id: 3,
      name: "AdGenius",
      logo: "/placeholder.svg?height=60&width=180",
      description: "Powering our upcoming advertising platform features.",
    },
  ])

  // Animation refs
  const [heroRef, heroInView] = useScrollAnimation(0.1)
  const [featuresRef, featuresInView] = useScrollAnimation()
  const [howItWorksRef, howItWorksInView] = useScrollAnimation()
  const [partnersRef, partnersInView] = useScrollAnimation()
  const [testimonialsRef, testimonialsInView] = useScrollAnimation()
  const [futureRef, futureInView] = useScrollAnimation()
  const [trustedByRef, trustedByInView] = useScrollAnimation()

  // Handle scroll event to change header appearance
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  // Handle smooth scrolling for anchor links
  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault()
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
      setIsMenuOpen(false)
    }
  }

  const features = [
    {
      title: "Multi-platform Management",
      description: "Schedule and publish content across all major social networks from one dashboard.",
      icon: Globe,
    },
    {
      title: "AI-powered Caption Generator",
      description: "Create optimized captions with trending keywords and SEO principles.",
      icon: MessageSquare,
    },
    {
      title: "Content Calendar",
      description: "Visual planning with an intuitive drag-and-drop interface.",
      icon: BarChart3,
    },
    {
      title: "Real-time Engagement",
      description: "Monitor engagement and get smart response suggestions instantly.",
      icon: Zap,
    },
  ]

  const trustedByCompanies = [
    "/placeholder.svg?height=40&width=120",
    "/placeholder.svg?height=40&width=120",
    "/placeholder.svg?height=40&width=120",
    "/placeholder.svg?height=40&width=120",
    "/placeholder.svg?height=40&width=120",
    "/placeholder.svg?height=40&width=120",
  ]

  const futureFeatures = [
    {
      title: "Advanced Ad Management",
      description: "Create, manage, and optimize ad campaigns across multiple platforms with AI-powered targeting.",
      icon: TrendingUp,
    },
    {
      title: "Cross-Platform Analytics",
      description: "Comprehensive analytics dashboard with unified metrics across all your social platforms.",
      icon: BarChart3,
    },
    {
      title: "Audience Insights",
      description: "Deep demographic and behavioral analysis of your audience across all platforms.",
      icon: Users,
    },
  ]

  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden">
      {/* Navigation */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className={`sticky top-0 z-50 border-b transition-all duration-300 ${
          scrolled ? "bg-background/80 backdrop-blur-md" : "bg-background"
        }`}
      >
        <div className="container mx-auto flex h-25 sm:h-20 items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-2 w-40 h-30">
            <Image src={logo} alt="Linkly Logo" className="w-25 h-30" />
          </div>

          <div className="hidden md:flex items-center gap-6">
            <nav className="flex items-center gap-6">
              <a
                href="#features"
                onClick={(e) => scrollToSection(e, "features")}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                onClick={(e) => scrollToSection(e, "how-it-works")}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                How It Works
              </a>
              <Link href="/pricing" className="text-sm font-medium hover:text-primary transition-colors">
                Pricing
              </Link>
              <a
                href="#partners"
                onClick={(e) => scrollToSection(e, "partners")}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Partners
              </a>
              <a
                href="#testimonials"
                onClick={(e) => scrollToSection(e, "testimonials")}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Testimonials
              </a>
            </nav>
            <div className="flex items-center gap-2">
              <Button variant="ghost" asChild>
                <Link href="/auth/login">Log in</Link>
              </Button>
              <Button asChild>
                <Link href="/dashboard">Try for free</Link>
              </Button>
              <ModeToggle />
            </div>
          </div>

          <div className="flex items-center gap-2 md:hidden">
            <ModeToggle />
            <Button variant="ghost" size="icon" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        <div
          className={`md:hidden border-t overflow-hidden transition-all duration-300 ${
            isMenuOpen ? "max-h-[400px]" : "max-h-0"
          }`}
        >
          <nav className="flex flex-col gap-4 p-4">
            <a
              href="#features"
              onClick={(e) => scrollToSection(e, "features")}
              className="text-sm font-medium hover:text-primary"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              onClick={(e) => scrollToSection(e, "how-it-works")}
              className="text-sm font-medium hover:text-primary"
            >
              How It Works
            </a>
            <Link href="/pricing" className="text-sm font-medium hover:text-primary">
              Pricing
            </Link>
            <a
              href="#partners"
              onClick={(e) => scrollToSection(e, "partners")}
              className="text-sm font-medium hover:text-primary"
            >
              Partners
            </a>
            <a
              href="#testimonials"
              onClick={(e) => scrollToSection(e, "testimonials")}
              className="text-sm font-medium hover:text-primary"
            >
              Testimonials
            </a>
            <div className="flex flex-col gap-2 pt-2 border-t">
              <Button variant="outline" asChild className="w-full">
                <Link href="/auth/login">Log in</Link>
              </Button>
              <Button asChild className="w-full">
                <Link href="/dashboard">Try for free</Link>
              </Button>
            </div>
          </nav>
        </div>
      </motion.header>

      <main className="flex-1">
        {/* Hero Section */}
        <section
          ref={heroRef}
          className="relative py-16 sm:py-20 md:py-28 bg-gradient-to-br from-violet-950 via-indigo-900 to-blue-900 overflow-hidden"
        >
          {/* Background elements */}
          <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-400/20 via-transparent to-transparent"></div>

          {/* Floating elements for futuristic look */}
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>

          <div className="container relative mx-auto px-4 sm:px-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <motion.div
                className="text-center md:text-left"
                initial="hidden"
                animate={heroInView ? "visible" : "hidden"}
                variants={fadeInLeft}
              >
                <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-white bg-white/20 rounded-full backdrop-blur-sm">
                  Social Media Management Simplified
                </div>
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white md:text-5xl lg:text-6xl">
                  Connect Your Digital World, <span className="text-cyan-300">Seamlessly</span>
                </h1>
                <p className="mt-4 sm:mt-6 text-base sm:text-lg text-white/80 md:text-xl max-w-xl mx-auto md:mx-0">
                  Linkly integrates all your social profiles, Google profiles, and digital identities into one unified
                  link. Manage your entire online presence from a single dashboard.
                </p>
                <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
                  <Button
                    size="lg"
                    asChild
                    className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white border-0"
                  >
                    <Link href="/dashboard">
                      Get started
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    asChild
                    className="bg-transparent text-white border-white hover:bg-white/10"
                  >
                    <a href="#features" onClick={(e) => scrollToSection(e, "features")}>
                      Learn more
                    </a>
                  </Button>
                </div>
              </motion.div>

              {/* Social Media Integration Illustration */}
              <motion.div
                className="flex justify-center"
                initial="hidden"
                animate={heroInView ? "visible" : "hidden"}
                variants={fadeInRight}
              >
                <div className="relative w-full max-w-md">
                  <SocialIntegrationIllustrationV2 />
                </div>
              </motion.div>
            </div>

            {/* Platform Icons */}
            <motion.div
              className="mt-12 sm:mt-16"
              initial={{ opacity: 0, y: 20 }}
              animate={heroInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
              transition={{ delay: 0.6, duration: 0.6 }}
            >
              <PlatformIcons />
            </motion.div>
          </div>
        </section>

        {/* Trusted By Section */}
        {/* <section id="trusted-by" ref={trustedByRef} className="py-12 sm:py-16 bg-muted/30">
          <div className="container mx-auto px-4 sm:px-6">
            <motion.div
              className="text-center"
              initial="hidden"
              animate={trustedByInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <h2 className="text-xl sm:text-2xl font-medium mb-8">Trusted by innovative companies worldwide</h2>
              <div className="flex flex-wrap justify-center items-center gap-8 sm:gap-12">
                {trustedByCompanies.map((logo, index) => (
                  <motion.div
                    key={index}
                    className="grayscale hover:grayscale-0 transition-all duration-300"
                    variants={fadeInScale}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Image
                      src={logo || "/placeholder.svg"}
                      alt={`Trusted company ${index + 1}`}
                      width={120}
                      height={40}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section> */}

        {/* Features Section */}
        <section id="features" ref={featuresRef} className="py-16 sm:py-20 bg-background">
          <div className="container mx-auto px-4 sm:px-6">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Features
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight md:text-4xl">
                All-in-one Performance Marketing Solution
              </h2>
              <p className="mt-4 text-base sm:text-lg text-muted-foreground">
                Maximize your social media presence with minimal effort using our comprehensive platform.
              </p>
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 grid gap-6 sm:gap-8 md:grid-cols-2 lg:grid-cols-4"
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  className="rounded-xl border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md hover:border-primary/50 hover:translate-y-[-4px]"
                  variants={fadeInScale}
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium">{feature.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
                </motion.div>
              ))}
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 flex justify-center"
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
              variants={fadeInUp}
              transition={{ delay: 0.6 }}
            >
              <Button size="lg" asChild className="bg-primary hover:bg-primary/90">
                <Link href="/dashboard">
                  Explore all features
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </motion.div>
          </div>
        </section>

        {/* How It Works */}
        <section
          id="how-it-works"
          ref={howItWorksRef}
          className="py-16 sm:py-20 bg-gradient-to-b from-background to-muted/30"
        >
          <div className="container mx-auto px-4 sm:px-6">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={howItWorksInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Process
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight md:text-4xl">How Linkly Works</h2>
              <p className="mt-4 text-base sm:text-lg text-muted-foreground">
                Three simple steps to transform your social media management
              </p>
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 grid gap-8 md:grid-cols-3 relative"
              initial="hidden"
              animate={howItWorksInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {/* Connector lines for desktop */}
              <div className="hidden md:block absolute top-8 left-[16.67%] w-[33.33%] h-0.5 bg-gradient-to-r from-primary to-primary/50"></div>
              <div className="hidden md:block absolute top-8 left-[50%] w-[33.33%] h-0.5 bg-gradient-to-r from-primary/50 to-primary/20"></div>

              <motion.div className="flex flex-col items-center text-center relative" variants={fadeInUp}>
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/80 text-primary-foreground z-10 shadow-lg">
                  <span className="text-xl font-bold">1</span>
                </div>
                <h3 className="mt-6 text-xl font-medium">Connect Your Accounts</h3>
                <p className="mt-2 text-muted-foreground">
                  Link all your social media profiles to create a unified digital presence.
                </p>
              </motion.div>

              <motion.div className="flex flex-col items-center text-center relative" variants={fadeInUp}>
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/80 text-primary-foreground z-10 shadow-lg">
                  <span className="text-xl font-bold">2</span>
                </div>
                <h3 className="mt-6 text-xl font-medium">Create & Schedule Content</h3>
                <p className="mt-2 text-muted-foreground">
                  Use our AI tools to generate optimized content and schedule it across platforms.
                </p>
              </motion.div>

              <motion.div className="flex flex-col items-center text-center relative" variants={fadeInUp}>
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/80 text-primary-foreground z-10 shadow-lg">
                  <span className="text-xl font-bold">3</span>
                </div>
                <h3 className="mt-6 text-xl font-medium">Analyze & Optimize</h3>
                <p className="mt-2 text-muted-foreground">
                  Track performance metrics and get actionable insights to improve your strategy.
                </p>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Future Prospects Section */}
        <section id="future" ref={futureRef} className="py-16 sm:py-20 bg-background">
          <div className="container mx-auto px-4 sm:px-6">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={futureInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Coming Soon
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight md:text-4xl">The Future of Linkly</h2>
              <p className="mt-4 text-base sm:text-lg text-muted-foreground">
                We're constantly evolving to bring you cutting-edge social media management tools
              </p>
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 grid gap-6 sm:gap-8 md:grid-cols-3"
              initial="hidden"
              animate={futureInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {futureFeatures.map((feature, index) => (
                <motion.div
                  key={index}
                  className="rounded-xl border border-dashed border-primary/30 bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md hover:border-primary/50"
                  variants={fadeInScale}
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium">{feature.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
                </motion.div>
              ))}
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 p-6 sm:p-8 rounded-xl bg-gradient-to-r from-indigo-50 to-cyan-50 dark:from-indigo-950/30 dark:to-cyan-950/30 border border-indigo-100 dark:border-indigo-900/50"
              initial="hidden"
              animate={futureInView ? "visible" : "hidden"}
              variants={fadeInUp}
              transition={{ delay: 0.4 }}
            >
              <div className="flex flex-col md:flex-row gap-6 items-center">
                <div className="flex-1">
                  <h3 className="text-xl sm:text-2xl font-bold mb-2">Introducing Ad Management</h3>
                  <p className="text-muted-foreground mb-4">
                    Our upcoming ad management platform will allow you to create, manage, and optimize ad campaigns
                    across multiple platforms with AI-powered targeting and optimization.
                  </p>
                  <Button variant="outline" className="group">
                    Join the waitlist
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
                <div className="flex-shrink-0 w-full md:w-1/3 aspect-video bg-gradient-to-br from-indigo-100 to-cyan-100 dark:from-indigo-900/50 dark:to-cyan-900/50 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-16 w-16 text-primary/70" />
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Partners Section */}
        <section id="partners" ref={partnersRef} className="py-16 sm:py-20 bg-muted/30">
          <div className="container mx-auto px-4 sm:px-6">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={partnersInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Partnerships
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight md:text-4xl">Our Strategic Partners</h2>
              <p className="mt-4 text-base sm:text-lg text-muted-foreground">
                We collaborate with industry leaders to bring you the best social media management experience
              </p>
            </motion.div>

            {/* <motion.div
              className="mt-12 sm:mt-16 grid gap-6 sm:gap-8 md:grid-cols-3"
              initial="hidden"
              animate={partnersInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {partners.map((partner, index) => (
                <motion.div
                  key={index}
                  className="rounded-xl border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md flex flex-col items-center text-center"
                  variants={fadeInScale}
                >
                  <Image
                    src={partner.logo || "/placeholder.svg"}
                    alt={partner.name}
                    width={180}
                    height={60}
                    className="mb-4"
                  />
                  <h3 className="text-lg font-medium">{partner.name}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{partner.description}</p>
                  <Button variant="ghost" size="sm" className="mt-4 group">
                    Learn more
                    <ExternalLink className="ml-2 h-3 w-3 transition-transform group-hover:translate-x-1" />
                  </Button>
                </motion.div>
              ))}
            </motion.div> */}

            {/* SocialBu Featured Partner */}
            <motion.div
              className="mt-12 sm:mt-16 p-6 sm:p-8 rounded-xl bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/30 dark:to-indigo-950/30 border border-purple-100 dark:border-purple-900/50"
              initial="hidden"
              animate={partnersInView ? "visible" : "hidden"}
              variants={fadeInUp}
              transition={{ delay: 0.4 }}
            >
              <div className="flex flex-col md:flex-row gap-6 items-center">
                <div className="flex-shrink-0 w-full md:w-1/3 aspect-video bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/50 dark:to-indigo-900/50 rounded-lg flex items-center justify-center">
                  <Image src={socialbu} alt="SocialBu" width={200} height={80} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl sm:text-2xl font-bold mb-2">Featured Partner: SocialBu</h3>
                  <p className="text-muted-foreground mb-4">
                    Our premier partnership with SocialBu enhances Linkly's analytics capabilities, providing you with
                    deeper insights and more powerful reporting tools. Together, we're revolutionizing how businesses
                    understand and leverage their social media presence.
                  </p>
                  <Button variant="outline" className="group">
                    Explore partnership
                    <Share2 className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Button>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section id="testimonials" ref={testimonialsRef} className="py-16 sm:py-20 bg-background">
          <div className="container mx-auto px-4 sm:px-6">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={testimonialsInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Testimonials
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight md:text-4xl">What Our Customers Say</h2>
              <p className="mt-4 text-base sm:text-lg text-muted-foreground">
                Discover how Linkly has transformed social media management for businesses of all sizes
              </p>
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 grid gap-6 sm:gap-8 md:grid-cols-3"
              initial="hidden"
              animate={testimonialsInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={testimonial.id}
                  className="rounded-xl border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md flex flex-col"
                  variants={fadeInScale}
                >
                  <div className="flex-1">
                    <div className="flex mb-4">
                      {[...Array(5)].map((_, i) => (
                        <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    <p className="text-muted-foreground italic mb-4">"{testimonial.quote}"</p>
                  </div>
                  <div className="flex items-center mt-4 pt-4 border-t">
                    {testimonial.avatar && (
                      <Image
                        src={testimonial.avatar || "/placeholder.svg"}
                        alt={testimonial.author}
                        width={40}
                        height={40}
                        className="rounded-full mr-3"
                      />
                    )}
                    <div>
                      <h4 className="font-medium">{testimonial.author}</h4>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
                        {testimonial.company ? `, ${testimonial.company}` : ""}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            <motion.div
              className="mt-12 sm:mt-16 flex justify-center"
              initial="hidden"
              animate={testimonialsInView ? "visible" : "hidden"}
              variants={fadeInUp}
              transition={{ delay: 0.4 }}
            >
              <Button asChild>
                <Link href="/dashboard">
                  Start your free trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </motion.div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 sm:py-20 bg-gradient-to-br from-indigo-900 via-violet-900 to-purple-900 text-white">
          <div className="container mx-auto px-4 sm:px-6">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
                Ready to transform your social media strategy?
              </h2>
              <p className="text-base sm:text-lg text-white/80 mb-8 max-w-2xl mx-auto">
                Join thousands of businesses that use Linkly to streamline their social media management and boost
                engagement.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" asChild className="bg-white text-indigo-900 hover:bg-white/90">
                  <Link href="/dashboard">
                    Get started for free
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="border-white text-white hover:bg-white/10">
                  <Link href="/pricing">View pricing</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-background py-12">
        <div className="container mx-auto px-4 sm:px-6">
          <motion.div
            className="grid gap-8 md:grid-cols-4"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div>
              <div className="flex items-center gap-2">
                <Image src={logo || "/placeholder.svg"} alt="Linkly Logo" className="w-25 h-25" />
              </div>
              <p className="mt-4 text-sm text-muted-foreground">Connect Your Digital World, Seamlessly.</p>
              <div className="flex gap-4 mt-4">
                <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fillRule="evenodd"
                      d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"
                      clipRule="evenodd"
                    />
                  </svg>
                </Link>
                <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </Link>
                <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fillRule="evenodd"
                      d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </Link>
                <Link href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      fillRule="evenodd"
                      d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10c5.51 0 10-4.48 10-10S17.51 2 12 2zm6.605 4.61a8.502 8.502 0 011.93 5.314c-.281-.054-3.101-.629-5.943-.271-.065-.141-.12-.293-.184-.445a25.416 25.416 0 00-.564-1.236c3.145-1.28 4.577-3.124 4.761-3.362zM12 3.475c2.17 0 4.154.813 5.662 2.148-.152.216-1.443 1.941-4.48 3.08-1.399-2.57-2.95-4.675-3.189-5A8.687 8.687 0 0112 3.475zm-3.633.803a53.896 53.896 0 013.167 4.935c-3.992 1.063-7.517 1.04-7.896 1.04a8.581 8.581 0 014.729-5.975zM3.453 12.01v-.26c.37.01 4.512.065 8.775-1.215.25.477.477.965.694 1.453-.109.033-.228.065-.336.098-4.404 1.42-6.747 5.303-6.942 5.629a8.522 8.522 0 01-2.19-5.705zM12 20.547a8.482 8.482 0 01-5.239-1.8c.152-.315 1.888-3.656 6.703-5.337.022-.01.033-.01.054-.022a35.318 35.318 0 011.823 6.475 8.4 8.4 0 01-3.341.684zm4.761-1.465c-.086-.52-.542-3.015-1.659-6.084 2.679-.423 5.022.271 5.314.369a8.468 8.468 0 01-3.655 5.715z"
                      clipRule="evenodd"
                    />
                  </svg>
                </Link>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium">Product</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <Link
                    href="#features"
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Features
                  </Link>
                </li>
                <li>
                  <Link
                    href="/pricing"
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link
                    href="#testimonials"
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Testimonials
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                    Integrations
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                    API
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-medium">Company</h3>
              <ul className="mt-4 space-y-2">
                {["About", "Blog", "Careers", "Press", "Contact"].map((item, index) => (
                  <li key={index}>
                    <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                      {item}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-medium">Legal</h3>
              <ul className="mt-4 space-y-2">
                {["Terms", "Privacy", "Cookies", "Licenses", "Settings"].map((item, index) => (
                  <li key={index}>
                    <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                      {item}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>

          <motion.div
            className="mt-12 border-t pt-8"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            viewport={{ once: true }}
          >
            <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
              <p className="text-sm text-muted-foreground">
                &copy; {new Date().getFullYear()} Linkly. All rights reserved.
              </p>
              <div className="flex items-center gap-4">
                <Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Pricing
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Terms
                </Link>
                <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Privacy
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </footer>
    </div>
  )
}

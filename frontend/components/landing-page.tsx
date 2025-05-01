"use client"

import React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { useInView } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import Image from "next/image"
import logo from "@/public/logo-no-bg.png"
import { ChevronRight, CheckCircle2, ArrowRight, Menu, X } from "lucide-react"
import { PlatformIcons } from "@/components/platform-icons"
import { SocialIntegrationIllustrationV2 } from "@/components/illustrations/social-integration-illustration-v2"
import { useTheme } from "next-themes"
import { useMobile } from "@/hooks/use-mobile"

interface Testimonial {
  id: number
  quote: string
  author: string
  role: string
}

interface PricingPlan {
  id: number
  name: string
  price: number
  description: string
  features: string[]
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
  const ref = React.useRef(null)
  const isInView = useInView(ref, { once: true, amount: threshold })

  return [ref, isInView]
}

export function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const { theme } = useTheme()
  const isMobile = useMobile()
  const [testimonials, setTestimonials] = useState<Testimonial[]>([
    {
      id: 1,
      quote: "Linkly has transformed how we manage our social media. The time savings alone are worth every penny!",
      author: "Sarah Johnson",
      role: "Marketing Director",
    },
    {
      id: 2,
      quote: "The analytics and insights have helped us increase engagement by over 40% in just two months.",
      author: "Michael Chen",
      role: "Social Media Manager",
    },
    {
      id: 3,
      quote: "As a small business owner, Linkly gives me enterprise-level tools at a price I can afford.",
      author: "Jessica Williams",
      role: "Founder, Bright Ideas Co.",
    },
  ])
  const [pricingPlans, setPricingPlans] = useState<PricingPlan[]>([
    {
      id: 1,
      name: "Starter",
      price: 9,
      description: "Perfect for individuals and small businesses just getting started.",
      features: ["2 social accounts", "30 scheduled posts per month", "Basic analytics", "24/7 support"],
    },
    {
      id: 2,
      name: "Professional",
      price: 19,
      description: "Ideal for growing businesses with active social presence.",
      features: [
        "5 social accounts",
        "Unlimited scheduled posts",
        "Advanced analytics",
        "Content calendar",
        "Team collaboration (2 users)",
      ],
    },
    {
      id: 3,
      name: "Enterprise",
      price: 49,
      description: "For large organizations with complex social media needs.",
      features: [
        "Unlimited social accounts",
        "Unlimited scheduled posts",
        "Custom analytics and reporting",
        "Content calendar with approval workflow",
        "Team collaboration (unlimited users)",
        "Dedicated account manager",
      ],
    },
  ])

  // Animation refs
  const [heroRef, heroInView] = useScrollAnimation(0.1)
  const [featuresRef, featuresInView] = useScrollAnimation()
  const [howItWorksRef, howItWorksInView] = useScrollAnimation()
  const [pricingRef, pricingInView] = useScrollAnimation()
  const [testimonialRef, testimonialInView] = useScrollAnimation()
  const [ctaRef, ctaInView] = useScrollAnimation(0.5)

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
      icon: CheckCircle2,
    },
    {
      title: "AI-powered Caption Generator",
      description: "Create optimized captions with trending keywords and SEO principles.",
      icon: CheckCircle2,
    },
    {
      title: "Content Calendar",
      description: "Visual planning with an intuitive drag-and-drop interface.",
      icon: CheckCircle2,
    },
    {
      title: "Real-time Engagement",
      description: "Monitor engagement and get smart response suggestions instantly.",
      icon: CheckCircle2,
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
        <div className="container mx-auto flex h-20 items-center justify-between px-5">
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
              <a
                href="#pricing"
                onClick={(e) => scrollToSection(e, "pricing")}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Pricing
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
            <a
              href="#pricing"
              onClick={(e) => scrollToSection(e, "pricing")}
              className="text-sm font-medium hover:text-primary"
            >
              Pricing
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
          className={`relative py-20 md:py-28 ${theme === "dark" ? "bg-[#050a14]" : "bg-[#0a0e1a]"} overflow-hidden`}
        >
          {/* Background pattern */}
          <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-90"></div>

          <div className="container relative mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <motion.div
                className="text-center md:text-left"
                initial="hidden"
                animate={heroInView ? "visible" : "hidden"}
                variants={fadeInLeft}
              >
                <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-white bg-white/20 rounded-full">
                  Social Media Management Simplified
                </div>
                <h1 className="text-4xl font-bold tracking-tight text-white md:text-6xl">
                  Connect Your Digital World, <span className="text-cyan-300">Seamlessly</span>
                </h1>
                <p className="mt-6 text-lg text-white/80 md:text-xl">
                  Linkly integrates all your social profiles, Google profiles, and digital identities into one unified
                  link. Manage your entire online presence from a single dashboard.
                </p>
                <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:justify-start">
                  <Button size="lg" asChild className="bg-cyan-500 hover:bg-cyan-600 text-white">
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
              className="mt-16"
              initial={{ opacity: 0, y: 20 }}
              animate={heroInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
              transition={{ delay: 0.6, duration: 0.6 }}
            >
              <PlatformIcons />
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" ref={featuresRef} className="bg-white py-20 dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Features
              </div>
              <h2 className="text-3xl font-bold tracking-tight md:text-4xl">All-in-one Performance Marketing Solution</h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Maximize your social media presence with minimal effort using our comprehensive platform.
              </p>
            </motion.div>

            <motion.div
              className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4"
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  className="rounded-lg border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md hover:border-primary/50"
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
              className="mt-16 flex justify-center"
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
        <section id="how-it-works" ref={howItWorksRef} className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={howItWorksInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Process
              </div>
              <h2 className="text-3xl font-bold tracking-tight md:text-4xl">How Linkly Works</h2>
              <p className="mt-4 text-lg text-muted-foreground">
                Three simple steps to transform your social media management
              </p>
            </motion.div>

            <motion.div
              className="mt-16 grid gap-8 md:grid-cols-3 relative"
              initial="hidden"
              animate={howItWorksInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {/* Connector lines for desktop */}
              <div className="hidden md:block absolute top-8 left-[16.67%] w-[33.33%] h-0.5 bg-gradient-to-r from-primary to-primary/50"></div>
              <div className="hidden md:block absolute top-8 left-[50%] w-[33.33%] h-0.5 bg-gradient-to-r from-primary/50 to-primary/20"></div>

              <motion.div className="flex flex-col items-center text-center relative" variants={fadeInUp}>
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground z-10">
                  <span className="text-xl font-bold">1</span>
                </div>
                <h3 className="mt-6 text-xl font-medium">Connect Your Accounts</h3>
                <p className="mt-2 text-muted-foreground">
                  Link all your social media profiles to create a unified digital presence.
                </p>
              </motion.div>

              <motion.div className="flex flex-col items-center text-center relative" variants={fadeInUp}>
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground z-10">
                  <span className="text-xl font-bold">2</span>
                </div>
                <h3 className="mt-6 text-xl font-medium">Create & Schedule Content</h3>
                <p className="mt-2 text-muted-foreground">
                  Use our AI tools to generate optimized content and schedule it across platforms.
                </p>
              </motion.div>

              <motion.div className="flex flex-col items-center text-center relative" variants={fadeInUp}>
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground z-10">
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

        {/* Pricing Section */}
        <section id="pricing" ref={pricingRef} className="bg-white py-20 dark:bg-gray-900">
          <div className="container mx-auto px-4">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={pricingInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Pricing
              </div>
              <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Simple, Transparent Pricing</h2>
              <p className="mt-4 text-lg text-muted-foreground">Choose the plan that's right for your business</p>
            </motion.div>

            <motion.div
              className="mt-16 grid gap-8 md:grid-cols-3"
              initial="hidden"
              animate={pricingInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {/* Pricing Plans */}
              {pricingPlans.map((plan) => (
                <motion.div
                  key={plan.id}
                  className="rounded-lg border bg-card p-8 shadow-sm transition-all duration-300 hover:shadow-md hover:border-primary/50"
                  variants={fadeInScale}
                  whileHover={{ y: -5, transition: { duration: 0.3 } }}
                >
                  <h3 className="text-lg font-medium">{plan.name}</h3>
                  <div className="mt-4 flex items-baseline">
                    <span className="text-3xl font-bold">${plan.price}</span>
                    <span className="ml-1 text-muted-foreground">/month</span>
                  </div>
                  <p className="mt-4 text-sm text-muted-foreground">{plan.description}</p>
                  <ul className="mt-6 space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center">
                        <CheckCircle2 className="mr-2 h-4 w-4 text-primary" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button className="mt-8 w-full" variant="outline">
                    Get started
                  </Button>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Testimonials */}
        <section id="testimonials" ref={testimonialRef} className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <motion.div
              className="mx-auto max-w-3xl text-center"
              initial="hidden"
              animate={testimonialInView ? "visible" : "hidden"}
              variants={fadeInUp}
            >
              <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
                Testimonials
              </div>
              <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Loved by Businesses Worldwide</h2>
              <p className="mt-4 text-lg text-muted-foreground">See what our customers have to say about Linkly</p>
            </motion.div>

            <motion.div
              className="mt-16 grid gap-8 md:grid-cols-3"
              initial="hidden"
              animate={testimonialInView ? "visible" : "hidden"}
              variants={staggerContainer}
            >
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={testimonial.id}
                  className="rounded-lg border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-md hover:border-primary/50"
                  variants={index % 2 === 0 ? fadeInLeft : fadeInRight}
                >
                  <div className="flex h-10 items-center">
                    <svg className="h-8 w-8 text-primary/40" fill="currentColor" viewBox="0 0 32 32" aria-hidden="true">
                      <path d="M9.352 4C4.456 7.456 1 13.12 1 19.36c0 5.088 3.072 8.064 6.624 8.064 3.36 0 5.856-2.688 5.856-5.856 0-3.168-2.208-5.472-5.088-5.472-.576 0-1.344.096-1.536.192.48-3.264 3.552-7.104 6.624-9.024L9.352 4zm16.512 0c-4.8 3.456-8.256 9.12-8.256 15.36 0 5.088 3.072 8.064 6.624 8.064 3.264 0 5.856-2.688 5.856-5.856 0-3.168-2.304-5.472-5.184-5.472-.576 0-1.248.096-1.44.192.48-3.264 3.456-7.104 6.528-9.024L25.864 4z" />
                    </svg>
                  </div>
                  <p className="mt-4 text-lg">{testimonial.quote}</p>
                  <div className="mt-6 flex items-center">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-sm font-medium text-primary">
                        {testimonial.author
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </span>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium">{testimonial.author}</p>
                      <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* CTA Section */}
        <section ref={ctaRef} className="bg-primary text-primary-foreground py-20">
          <div className="container mx-auto px-4 text-center">
            <motion.div
              className="mx-auto max-w-3xl"
              initial="hidden"
              animate={ctaInView ? "visible" : "hidden"}
              variants={fadeInUp}
              whileInView={{
                scale: [1, 1.02, 1],
                transition: {
                  duration: 2,
                  repeat: Number.POSITIVE_INFINITY,
                  repeatType: "reverse",
                },
              }}
            >
              <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Ready to transform your social media?</h2>
              <p className="mt-4 text-lg opacity-90">
                Join thousands of businesses using Linkly to streamline their social media management.
              </p>
              <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:justify-center">
                <Button size="lg" variant="secondary" asChild className="bg-white text-primary hover:bg-white/90">
                  <Link href="/dashboard">
                    Get started for free
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="bg-transparent border-white text-white hover:bg-white/10"
                  asChild
                >
                  <a href="#pricing" onClick={(e) => scrollToSection(e, "pricing")}>
                    View pricing
                  </a>
                </Button>
              </div>
            </motion.div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-background py-12">
        <div className="container mx-auto px-4">
          <motion.div
            className="grid gap-8 md:grid-cols-4"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div>
              <div className="flex items-center gap-2">
                 <Image src={logo} alt="Linkly Logo" className="w-35 h-25" />
              </div>
              <p className="mt-4 text-sm text-muted-foreground">Connect Your Digital World, Seamlessly.</p>
            </div>

            <div>
              <h3 className="text-sm font-medium">Product</h3>
              <ul className="mt-4 space-y-2">
                {["Features", "Pricing", "Testimonials", "Integrations", "API"].map((item, index) => (
                  <li key={index}>
                    <Link href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                      {item}
                    </Link>
                  </li>
                ))}
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
              </div>
            </div>
          </motion.div>
        </div>
      </footer>
    </div>
  )
}

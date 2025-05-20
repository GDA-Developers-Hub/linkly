"use client"

import * as React from "react"
import Link from "next/link"
import { motion, useInView } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import Image from "next/image"
import logo from "@/public/logo-no-bg.png"
import socialbu from "@/public/socialbu-logo.png"
import linklyVideo from "@/public/linkly.mp4"
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
  ArrowUpRight,
  ChevronLeft,
  Play,
  PlayCircle,
} from "lucide-react"
import { PlatformIcons } from "@/components/platform-icons"
import { SocialIntegrationIllustrationV2 } from "@/components/illustrations/social-integration-illustration-v2"
import { useTheme } from "next-themes"
import { useIsMobile } from "@/components/ui/use-mobile"
import { cn } from "@/lib/utils"
import { AspectRatio } from "@/components/ui/aspect-ratio"
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel"
import { SiteFooter } from "@/components/site-footer"

// TypewriterEffect component for animated typing
const TypewriterEffect = ({ 
  text, 
  duration = 1.5, 
  delay = 0,
  className = "" 
}: { 
  text: string; 
  duration?: number; 
  delay?: number;
  className?: string;
}) => {
  const [displayText, setDisplayText] = React.useState("");
  
  React.useEffect(() => {
    let timeout: NodeJS.Timeout;
    let currentIndex = 0;
    let currentText = "";
    
    const typeNextCharacter = () => {
      if (currentIndex < text.length) {
        currentText += text.charAt(currentIndex);
        setDisplayText(currentText);
        currentIndex++;
        
        // Calculate typing speed with some randomness for realism
        const typingSpeed = (duration * 1000) / text.length * (0.5 + Math.random());
        timeout = setTimeout(typeNextCharacter, typingSpeed);
      }
    };
    
    // Start typing after the specified delay
    const startTimeout = setTimeout(() => {
      typeNextCharacter();
    }, delay * 1000);
    
    return () => {
      clearTimeout(timeout);
      clearTimeout(startTimeout);
    };
  }, [text, duration, delay]);
  
  return <span className={className}>{displayText}</span>;
};

interface Feature {
  title: string
  description: string
  icon: React.ElementType
}

// Custom hook for scroll animations
function useScrollAnimation(threshold = 0.2) {
  const ref = React.useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, amount: threshold })
  return [ref, isInView] as const
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

export function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false)
  const [scrolled, setScrolled] = React.useState(false)
  const { theme } = useTheme()
  const isMobile = useIsMobile()

  // Animation refs
  const [heroRef, heroInView] = useScrollAnimation(0.1)
  const [featuresRef, featuresInView] = useScrollAnimation()
  const [howItWorksRef, howItWorksInView] = useScrollAnimation()
  const [trustedByRef, trustedByInView] = useScrollAnimation()

  // Video state management
  const [isVideoPlaying, setIsVideoPlaying] = React.useState(false)
  const [isVideoLoaded, setIsVideoLoaded] = React.useState(false)
  const [showPreview, setShowPreview] = React.useState(true)
  const [isVideoEnded, setIsVideoEnded] = React.useState(false)
  const videoRef = React.useRef<HTMLVideoElement>(null)

  const handleVideoPlay = () => {
    if (videoRef.current) {
      if (videoRef.current.paused) {
        videoRef.current.play()
        setIsVideoPlaying(true)
        setShowPreview(false)
        setIsVideoEnded(false)
      } else {
        videoRef.current.pause()
        setIsVideoPlaying(false)
      }
    }
  }

  const handleVideoEnd = () => {
    setIsVideoEnded(true)
    setIsVideoPlaying(false)
  }

  const handleVideoLoad = () => {
    setIsVideoLoaded(true)
  }

  // Preload video when component mounts
  React.useEffect(() => {
    const video = videoRef.current
    if (video) {
      video.preload = "metadata" // Only load video metadata initially
      video.load()
    }
  }, [])

  // Cleanup video on unmount
  React.useEffect(() => {
    const video = videoRef.current
    return () => {
      if (video) {
        video.pause()
        video.src = ""
        video.load()
      }
    }
  }, [])

  // Handle scroll event to change header appearance
  React.useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  // Handle smooth scrolling for anchor links
  const scrollToSection = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault()
    const target = e.currentTarget
    const id = target.getAttribute("href")?.replace("#", "")
    if (id) {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
      setIsMenuOpen(false)
      }
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

  // Add this for carousel autoplay control
  const [api, setApi] = React.useState<any>()
  
  React.useEffect(() => {
    if (!api) return;
    
    // Start autoplay
    const autoplayInterval = setInterval(() => {
      api.scrollNext();
    }, 3000); // Change slide every 3 seconds
    
    // Clear interval on component unmount
    return () => clearInterval(autoplayInterval);
  }, [api]);

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile-optimized header */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className={cn(
          "sticky top-0 z-50 w-full border-b transition-all duration-300",
          scrolled ? "bg-background/90 backdrop-blur-md shadow-sm" : "bg-background"
        )}
      >
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 group" aria-label="Linkly Home">
              <div className="relative h-12 w-40 overflow-visible">
                <Image 
                  src={logo} 
                  alt="Linkly Logo" 
                  className="object-contain scale-100 group-hover:scale-105 transition-transform duration-200" 
                  fill
                  priority 
                  sizes="(max-width: 768px) 120px, 160px"
                />
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <a
                href="#features"
                onClick={scrollToSection}
                className="text-sm font-medium hover:text-[#FF8C2A] transition-colors relative after:absolute after:bottom-[-2px] after:left-0 after:h-[2px] after:w-0 after:bg-[#FF8C2A] after:transition-all hover:after:w-full"
                aria-label="View Features"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                onClick={scrollToSection}
                className="text-sm font-medium hover:text-[#FF8C2A] transition-colors relative after:absolute after:bottom-[-2px] after:left-0 after:h-[2px] after:w-0 after:bg-[#FF8C2A] after:transition-all hover:after:w-full"
                aria-label="Learn How It Works"
              >
                How it works
              </a>
              <div className="flex items-center space-x-4 ml-2">
                <ModeToggle />
                <Button 
                  asChild 
                  className="bg-[#FF8C2A] hover:bg-[#e67e25] text-white font-semibold shadow-lg hover:shadow-xl transition-all px-5"
                  size="sm"
                >
                  <Link href="/auth/register">Get Started</Link>
                </Button>
              </div>
            </nav>

            {/* Mobile Navigation Button */}
            <div className="flex md:hidden items-center space-x-4">
            <ModeToggle />
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                {isMenuOpen ? (
                  <X className="h-6 w-6" />
                ) : (
                  <Menu className="h-6 w-6" />
                )}
            </Button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden"
        >
            <nav className="container mx-auto px-4 py-4 flex flex-col space-y-4 border-t bg-background/95 backdrop-blur-sm">
            <a
              href="#features"
                onClick={scrollToSection}
                className="flex items-center justify-between py-2 text-sm font-medium hover:text-primary transition-colors"
            >
              Features
                <ChevronRight className="h-4 w-4" />
            </a>
            <a
              href="#how-it-works"
                onClick={scrollToSection}
                className="flex items-center justify-between py-2 text-sm font-medium hover:text-primary transition-colors"
            >
                How it works
                <ChevronRight className="h-4 w-4" />
            </a>
              <Button asChild className="w-full bg-[#FF8C2A] hover:bg-[#e67e25] text-white">
                <Link href="/auth/register">Get Started</Link>
              </Button>
          </nav>
          </motion.div>
        )}
      </motion.header>

      <main className="flex-1">
        {/* Hero Section */}
        <section
          ref={heroRef as React.RefObject<HTMLDivElement>}
          className="relative overflow-hidden py-2 md:py-2 bg-gradient-to-br from-[#FF8C2A]/20 via-white dark:via-gray-900 to-blue-500/10 dark:to-blue-500/5"
          aria-labelledby="hero-heading"
        >
          {/* Background elements - optimized for performance */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <motion.div 
              className="absolute top-0 left-0 w-full h-full opacity-10"
              initial={{ backgroundSize: '100%' }}
              animate={{ 
                backgroundPosition: ['0% 0%', '100% 100%'],
                backgroundSize: ['100%', '120%', '100%'] 
              }}
              transition={{ duration: 20, repeat: Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
              style={{
                backgroundImage: 'radial-gradient(circle at center, rgba(255,140,42,0.8) 0%, transparent 70%)',
                filter: 'blur(60px)',
                willChange: 'background-position, background-size'
              }}
            />
            <motion.div 
              className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-blue-500/20"
              initial={{ scale: 1, opacity: 0.2 }}
              animate={{ scale: [1, 1.1, 1], opacity: [0.2, 0.3, 0.2] }}
              transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
              style={{ filter: 'blur(40px)', willChange: 'transform, opacity' }}
            />
            <motion.div
              className="absolute h-40 w-40 bottom-20 left-20 rounded-full bg-[#FF8C2A]/30"
              initial={{ y: -10, opacity: 0.2 }}
              animate={{ y: [-10, 10, -10], opacity: [0.2, 0.4, 0.2] }}
              transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
              style={{ filter: 'blur(30px)', willChange: 'transform, opacity' }}
            />
          </div>

          <motion.div
            initial="hidden"
            animate={heroInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="container px-4 mx-auto relative z-10"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <motion.div variants={fadeInLeft} className="text-center lg:text-left">
                <div className="inline-block mb-4 px-4 py-1 rounded-full bg-[#FF8C2A]/10 text-[#FF8C2A] font-medium text-sm backdrop-blur-sm">
                  <motion.span 
                    initial={{ opacity: 0, x: -10 }} 
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5, duration: 0.5 }}
                  >
                    Powerful Social Media Tool
                  </motion.span>
                </div>
                <h1 
                  id="hero-heading"
                  className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-[#FF8C2A] dark:from-white dark:to-[#FF8C2A]"
                >
                  <span className="inline-block">Simplify Your</span>{" "}
                  <span className="inline-block">Social Media</span>{" "}
                  <span className="inline-block">Management</span>
                </h1>
                <p className="text-lg md:text-xl text-muted-foreground dark:text-gray-200 mb-8 max-w-xl mx-auto lg:mx-0 leading-relaxed">
                  Schedule posts, analyze performance, and grow your social media presence with our all-in-one platform designed for businesses of all sizes.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <Button 
                      size="lg" 
                      className="bg-gradient-to-r from-[#FF8C2A] to-[#e67e25] text-white w-full sm:w-auto shadow-lg hover:shadow-xl transition-all border-0 font-medium" 
                      asChild
                    >
                      <Link href="/auth/register">
                        Get Started
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: 'spring', stiffness: 400, damping: 10 }}
                  >
                    <Button
                      size="lg"
                      className="w-full sm:w-auto bg-white/80 dark:bg-white/10 text-gray-800 dark:text-white border border-gray-200 dark:border-gray-700 hover:bg-white dark:hover:bg-white/20 transition-all shadow-md hover:shadow-lg font-medium"
                      asChild
                    >
                      <a href="#features" onClick={scrollToSection}>
                        Learn more
                      </a>
                    </Button>
                  </motion.div>
                </div>
                <div className="mt-8 flex items-center justify-center lg:justify-start">
                  <div className="flex -space-x-2">
                    {[
                      "https://randomuser.me/api/portraits/women/32.jpg",
                      "https://randomuser.me/api/portraits/men/44.jpg",
                      "https://randomuser.me/api/portraits/women/68.jpg",
                      "https://randomuser.me/api/portraits/men/75.jpg"
                    ].map((avatar, i) => (
                      <motion.div 
                        key={i} 
                        className="w-9 h-9 rounded-full border-2 border-white dark:border-gray-800 shadow-sm overflow-hidden"
                        initial={{ opacity: 0, x: -5 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.8 + (i * 0.1), duration: 0.3 }}
                      >
                        <Image 
                          src={avatar} 
                          alt={`Customer ${i+1}`}
                          width={36}
                          height={36}
                          className="h-full w-full object-cover"
                          unoptimized
                        />
                      </motion.div>
                    ))}
                  </div>
                  <motion.div 
                    className="ml-3 text-sm text-muted-foreground"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.2, duration: 0.5 }}
                  >
                    <span className="font-semibold text-gray-900 dark:text-white">2,500+</span> satisfied customers
                  </motion.div>
                </div>
              </motion.div>
              <motion.div variants={fadeInRight} className="relative flex justify-center lg:justify-end">
                <div className="w-full max-w-xl h-[400px] md:h-[450px] rounded-xl shadow-2xl border-4 border-white dark:border-gray-800 bg-gradient-to-br from-white to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center relative overflow-hidden">
                  <div className="absolute inset-0 bg-[url('/vibrant-tech-unveiling.png')] bg-cover bg-center opacity-10 dark:opacity-20"></div>
                  <PlatformIcons />
                  
                  {/* Floating elements */}
                  <motion.div 
                    className="absolute top-10 right-10 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg"
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: [-5, 5, -5], rotate: [-2, 2, -2], opacity: 1 }}
                    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 0.2 }}
                  >
                    <Share2 className="w-5 h-5 text-[#FF8C2A]" />
                  </motion.div>
                  
                  <motion.div 
                    className="absolute bottom-10 left-10 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg"
                    initial={{ y: -20, opacity: 0 }}
                    animate={{ y: [5, -5, 5], rotate: [2, -2, 2], opacity: 1 }}
                    transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
                  >
                    <BarChart3 className="w-5 h-5 text-blue-500" />
                  </motion.div>
                  
                  {/* Glowing effect */}
                  <motion.div
                    className="absolute inset-0 pointer-events-none"
                    initial={{ boxShadow: 'inset 0 0 30px rgba(255, 140, 42, 0.3)' }}
                    animate={{ 
                      boxShadow: [
                        'inset 0 0 30px rgba(255, 140, 42, 0.3)', 
                        'inset 0 0 50px rgba(255, 140, 42, 0.5)', 
                        'inset 0 0 30px rgba(255, 140, 42, 0.3)'
                      ] 
                    }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                  />
                </div>
                
                {/* Stats card */}
                <motion.div 
                  className="absolute -bottom-5 -left-5 lg:left-auto lg:-right-5 bg-white dark:bg-gray-800 p-3 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700"
                  initial={{ opacity: 0, y: 20, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ delay: 1, duration: 0.5 }}
                  whileHover={{ y: -5, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-green-100 dark:bg-green-900/30">
                      <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Growth Rate</div>
                      <div className="font-bold text-green-600 dark:text-green-400">+147%</div>
                    </div>
                  </div>
                </motion.div>
                
                {/* Additional stat card */}
                <motion.div 
                  className="absolute -top-5 -right-5 lg:-left-5 lg:right-auto bg-white dark:bg-gray-800 p-3 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700"
                  initial={{ opacity: 0, y: -20, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ delay: 1.2, duration: 0.5 }}
                  whileHover={{ y: 5, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900/30">
                      <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Engagement</div>
                      <div className="font-bold text-blue-600 dark:text-blue-400">+89%</div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            </div>
            
            {/* Brand logos */}
            <motion.div 
              className="mt-16 pt-8 border-t border-gray-200 dark:border-gray-800"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.4, duration: 0.5 }}
            >
              <p className="text-center text-sm text-muted-foreground mb-6">Trusted by leading brands worldwide</p>
              <div className="flex flex-wrap justify-center gap-x-12 gap-y-6 opacity-70">
                {["/google-logo.png", "/facebook-logo.svg", "/instagram-logo.svg", "/twitter-logo.svg"].map((logo, i) => (
                  <div key={i} className="h-8 w-auto relative grayscale hover:grayscale-0 transition-all duration-300">
                    <Image src={logo} alt="Brand logo" width={100} height={32} className="h-full w-auto object-contain" />
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section
          id="features"
          ref={featuresRef as React.RefObject<HTMLDivElement>}
          className="py-19 md:py-20 bg-gradient-to-r from-white via-gray-50 to-white dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 relative overflow-hidden"
        >
            {/* Background elements */}
            <div className="absolute inset-0 overflow-hidden">
              <svg className="absolute top-0 left-0 w-full opacity-20 dark:opacity-10" viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="a" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur in="SourceGraphic" stdDeviation="50" />
                  </filter>
                </defs>
                <g filter="url(#a)">
                  <circle cx="150" cy="150" r="40" fill="#FF8C2A" />
                  <circle cx="650" cy="150" r="40" fill="#4F46E5" />
                  <circle cx="150" cy="650" r="40" fill="#4F46E5" />
                  <circle cx="650" cy="650" r="40" fill="#FF8C2A" />
                </g>
              </svg>
            </div>

            <motion.div
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
              variants={staggerContainer}
              className="container px-4 mx-auto relative z-10"
            >
              <motion.div variants={fadeInUp} className="text-center mb-16">
                <div className="inline-block mb-3">
                  <span className="inline-block px-4 py-1 rounded-full bg-[#FF8C2A]/10 text-[#FF8C2A] font-medium text-sm">
                    Revolutionary Features
                  </span>
                </div>
                <h2 className="text-3xl md:text-4xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-[#FF8C2A] dark:from-white dark:to-[#FF8C2A]">
                  Powerful Features for Modern Social Media
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  Everything you need to manage your social media presence effectively and grow your audience.
                </p>
              </motion.div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    variants={fadeInUp}
                    className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all border border-gray-100 dark:border-gray-800 flex flex-col items-center text-center group hover:border-[#FF8C2A]/30 dark:hover:border-[#FF8C2A]/30"
                    whileHover={{ y: -5, transition: { duration: 0.2 } }}
                  >
                    <div className="relative mb-6">
                      <div className="absolute inset-0 bg-[#FF8C2A]/20 blur-xl rounded-full transform group-hover:scale-110 transition-transform"></div>
                      <div className="relative bg-gradient-to-br from-[#FF8C2A] to-[#e67e25] p-3 rounded-xl text-white shadow-lg group-hover:shadow-xl transition-all">
                        <feature.icon className="h-6 w-6 group-hover:scale-110 transition-transform" />
                      </div>
                    </div>
                    <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white group-hover:text-[#FF8C2A] dark:group-hover:text-[#FF8C2A] transition-colors">{feature.title}</h3>
                    <p className="text-muted-foreground">{feature.description}</p>
                  </motion.div>
                ))}
              </div>

              {/* Feature highlight */}
              <motion.div
                variants={fadeInUp}
                className="mt-20 bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700"
              >
                <div className="grid md:grid-cols-2 gap-0">
                  <div className="p-8 md:p-12 flex flex-col justify-center">
                    <div className="inline-block mb-3 px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs font-semibold">
                      COMING SOON
                    </div>
                    <h3 className="text-2xl md:text-3xl font-bold mb-4 text-gray-900 dark:text-white">AI-Powered Content Creation</h3>
                    <p className="text-muted-foreground mb-6">
                      Our advanced AI algorithms analyze trending content and help you create engaging posts that resonate with your audience, saving you time and increasing engagement.
                    </p>
                    <ul className="space-y-3 mb-6">
                      {['Smart caption generation', 'Hashtag recommendations', 'Optimal posting time suggestions'].map((item, i) => (
                        <li key={i} className="flex items-center">
                          <div className="mr-2 flex-shrink-0 p-1 bg-green-100 dark:bg-green-900/30 rounded-full">
                            <svg className="h-4 w-4 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          </div>
                          <span className="text-gray-700 dark:text-gray-300">{item}</span>
                        </li>
                      ))}
                    </ul>
                    <Button className="bg-[#FF8C2A] hover:bg-[#e67e25] text-white w-full sm:w-auto shadow-md">
                      Join the Waitlist
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                  <div className="relative h-60 md:h-auto">
                    <div 
                      className="absolute inset-0 bg-cover bg-center opacity-30" 
                      style={{
                        backgroundImage: "url('https://images.unsplash.com/photo-1506815444479-bfdb1e96c566?q=80&auto=format&fit=crop')",
                        backgroundPosition: 'center 35%'
                      }}
                    ></div>
                    <div className="absolute inset-0 bg-gradient-to-r from-[#FF8C2A]/40 to-blue-500/40"></div>
                    <div className="absolute inset-0 flex items-center justify-center p-6">
                      <motion.div 
                        className="w-full max-w-sm p-5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg shadow-xl"
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 4, repeat: Infinity, repeatType: 'reverse' }}
                      >
                        <div className="flex items-center mb-3">
                          <div className="w-8 h-8 rounded-full bg-[#FF8C2A] flex items-center justify-center mr-3">
                            <MessageSquare className="h-4 w-4 text-white" />
                          </div>
                          <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        </div>
                        
                        {/* Caption with typing animation */}
                        <motion.div 
                          className="mb-3 font-medium text-sm text-gray-800 dark:text-gray-200"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.5 }}
                        >
                          <TypewriterEffect text="Creating perfect caption..." duration={2} />
                        </motion.div>
                        
                        <div className="bg-gray-100 dark:bg-gray-700/50 p-3 rounded-lg mb-4">
                          <motion.div
                            className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 2.5 }}
                          >
                            <TypewriterEffect 
                              text="Enjoying the sunrise views with our new summer collection! ☀️ Perfect for your morning routine and daily inspiration." 
                              duration={3} 
                              delay={2.5}
                            />
                          </motion.div>
                        </div>
                        
                        {/* Hashtags */}
                        <motion.div 
                          className="flex flex-wrap gap-2 mb-4"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 6 }}
                        >
                          <TypewriterEffect 
                            text="#summervibes #morningroutine #inspiration #lifestyle #trending" 
                            duration={2} 
                            delay={6}
                            className="text-[#FF8C2A] dark:text-[#FF8C2A] text-sm font-medium"
                          />
                        </motion.div>
                        
                        <div className="h-10 w-full bg-[#FF8C2A]/80 hover:bg-[#FF8C2A] rounded text-white font-medium flex items-center justify-center cursor-pointer transition-colors">
                          Use This Caption
                        </div>
                      </motion.div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
        </section>

        {/* How It Works Section */}
        <section
          id="how-it-works"
          ref={howItWorksRef as React.RefObject<HTMLDivElement>}
          className="py-20 md:py-10 relative overflow-hidden"
        >
          {/* Creative background elements */}
          <div className="absolute inset-0 overflow-hidden opacity-10">
            <div className="absolute h-96 w-96 rounded-full bg-[#FF8C2A]/30 blur-3xl -top-20 -right-20"></div>
            <div className="absolute h-96 w-96 rounded-full bg-blue-500/30 blur-3xl -bottom-20 -left-20"></div>
            <motion.div
              className="absolute top-1/4 left-1/3 h-64 w-64 rounded-full border-2 border-dashed border-[#FF8C2A]/30"
              animate={{ rotate: 360 }}
              transition={{ duration: 100, repeat: Infinity, ease: "linear" }}
            />
          </div>

          <motion.div
            initial="hidden"
            animate={howItWorksInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="container px-4 mx-auto relative z-10"
          >
            <motion.div variants={fadeInUp} className="text-center mb-16">
              <div className="inline-block mb-3 relative">
                <span className="inline-block px-4 py-1 rounded-full bg-[#FF8C2A]/10 text-[#FF8C2A] font-medium text-sm">
                  Simple Four-Step Process
                </span>
              </div>
              <h2 className="text-3xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-[#FF8C2A] via-[#FF8C2A]/90 to-blue-500 bg-clip-text text-transparent">
                How Linkly Works
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Get started in minutes with our intuitive platform designed for businesses of all sizes.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <motion.div variants={fadeInLeft} className="order-2 lg:order-1">
                <div className="space-y-12">
                  <motion.div 
                    className="flex items-start gap-6 group"
                    initial={{ opacity: 0, y: 20 }}
                    animate={howItWorksInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                  >
                    <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-br from-[#FF8C2A] to-[#FF8C2A]/80 flex items-center justify-center shadow-lg shadow-[#FF8C2A]/20 group-hover:shadow-xl group-hover:shadow-[#FF8C2A]/30 transition-all">
                      <span className="text-white font-bold text-xl">1</span>
                    </div>
                    <div className="pt-2">
                      <h3 className="text-2xl font-semibold mb-3 flex items-center group-hover:text-[#FF8C2A] transition-colors">
                        Connect Your Accounts
                        <ArrowUpRight className="ml-2 h-5 w-5 text-[#FF8C2A]" />
                      </h3>
                      <p className="text-muted-foreground text-lg">
                        Link your social media accounts in just a few clicks. We support all major platforms.
                      </p>
                    </div>
                  </motion.div>

                  <motion.div 
                    className="flex items-start gap-6 group"
                    initial={{ opacity: 0, y: 20 }}
                    animate={howItWorksInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                  >
                    <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-br from-[#FF8C2A] to-[#FF8C2A]/80 flex items-center justify-center shadow-lg shadow-[#FF8C2A]/20 group-hover:shadow-xl group-hover:shadow-[#FF8C2A]/30 transition-all">
                      <span className="text-white font-bold text-xl">2</span>
                    </div>
                    <div className="pt-2">
                      <h3 className="text-2xl font-semibold mb-3 flex items-center group-hover:text-[#FF8C2A] transition-colors">
                        Plan Your Content
                        <ArrowUpRight className="ml-2 h-5 w-5 text-[#FF8C2A]" />
                      </h3>
                      <p className="text-muted-foreground text-lg">
                        Use our visual calendar to schedule and organize your content across all platforms.
                      </p>
                    </div>
                  </motion.div>

                  <motion.div
                    className="flex items-start gap-6 group"
                    initial={{ opacity: 0, y: 20 }}
                    animate={howItWorksInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                  >
                    <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-br from-[#FF8C2A] to-[#FF8C2A]/80 flex items-center justify-center shadow-lg shadow-[#FF8C2A]/20 group-hover:shadow-xl group-hover:shadow-[#FF8C2A]/30 transition-all">
                      <span className="text-white font-bold text-xl">3</span>
                    </div>
                    <div className="pt-2">
                      <h3 className="text-2xl font-semibold mb-3 flex items-center group-hover:text-[#FF8C2A] transition-colors">
                        Analyze & Optimize
                        <ArrowUpRight className="ml-2 h-5 w-5 text-[#FF8C2A]" />
                      </h3>
                      <p className="text-muted-foreground text-lg">
                        Track performance and get AI-powered suggestions to improve your content strategy.
                      </p>
                    </div>
                  </motion.div>

                  <motion.div
                    className="flex items-start gap-6 relative group"
                    initial={{ opacity: 0, y: 20 }}
                    animate={howItWorksInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                    transition={{ duration: 0.5, delay: 0.7 }}
                  >
                    {/* Highlight for Google Ads section */}
                    <motion.div
                      className="absolute -inset-6 rounded-xl bg-gradient-to-r from-[#FF8C2A]/5 to-transparent z-0"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 1, duration: 0.8 }}
                    />
                    
                    <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-br from-[#FF8C2A] to-[#FF8C2A]/80 flex items-center justify-center shadow-lg shadow-[#FF8C2A]/20 group-hover:shadow-xl group-hover:shadow-[#FF8C2A]/30 transition-all z-10">
                      <span className="text-white font-bold text-xl">4</span>
                    </div>
                    <div className="pt-2 z-10">
                      <div className="flex items-center mb-1">
                        <span className="px-2 py-0.5 bg-[#FF8C2A]/10 text-[#FF8C2A] text-xs font-semibold rounded-full">
                          Featured Integration
                        </span>
                      </div>
                      <h3 className="text-2xl font-semibold mb-3 flex items-center group-hover:text-[#FF8C2A] transition-colors">
                        Google & YouTube Integration
                        <ArrowUpRight className="ml-2 h-5 w-5 text-[#FF8C2A]" />
                      </h3>
                      <p className="text-muted-foreground text-lg font-medium">
                        Seamlessly connect your Google Ads and YouTube campaigns with your social media strategy for maximum ROI.
                      </p>
                      <div className="mt-3 flex flex-wrap items-center gap-y-2">
                        <div className="mr-4 flex items-center">
                          <motion.div 
                            className="h-4 w-4 rounded-full bg-green-500 mr-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          />
                          <span className="text-sm">Real-time data</span>
                        </div>
                        <div className="mr-4 flex items-center">
                          <motion.div 
                            className="h-4 w-4 rounded-full bg-blue-500 mr-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, delay: 0.5, repeat: Infinity }}
                          />
                          <span className="text-sm">Unified metrics</span>
                        </div>
                        <div className="flex items-center">
                          <motion.div 
                            className="h-4 w-4 rounded-full bg-red-500 mr-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, delay: 1, repeat: Infinity }}
                          />
                          <span className="text-sm">YouTube analytics</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </motion.div>

              <motion.div
                variants={fadeInRight} 
                className="order-1 lg:order-2"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={howItWorksInView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.7 }}
              >
                <div className="relative w-full h-[500px] rounded-xl shadow-2xl overflow-hidden bg-gradient-to-br from-[#FF8C2A]/10 via-blue-500/5 to-purple-500/10">
                  {/* Gradient overlay */}
                  <motion.div 
                    className="absolute inset-0 bg-gradient-to-br from-[#FF8C2A]/10 via-transparent to-blue-500/5 z-10"
                    animate={{ 
                      opacity: [0.3, 0.7, 0.3],
                      rotate: [0, 5, 0]
                    }}
                    transition={{ 
                      duration: 8, 
                      repeat: Infinity,
                      repeatType: 'reverse'
                    }}
                  />
                  
                  <div className="absolute inset-0 flex items-center justify-center z-0">
                    <SocialIntegrationIllustrationV2 />
                  </div>
                  
                  {/* Animated Google logo highlight */}
                  <motion.div 
                    className="absolute bottom-10 right-10 bg-white rounded-full p-2 shadow-xl z-20 flex items-center justify-center"
                    animate={{ 
                      y: [0, -10, 0],
                      boxShadow: [
                        '0 0 0 rgba(255, 140, 42, 0.4)',
                        '0 0 20px rgba(255, 140, 42, 0.6)',
                        '0 0 0 rgba(255, 140, 42, 0.4)'
                      ]
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    <div className="flex items-center space-x-1 px-3 py-1">
                      <span className="text-blue-500 font-bold">G</span>
                      <span className="text-red-500 font-bold">o</span>
                      <span className="text-[#FF8C2A] font-bold">o</span>
                      <span className="text-blue-500 font-bold">g</span>
                      <span className="text-green-500 font-bold">l</span>
                      <span className="text-red-500 font-bold">e</span>
                      <span className="text-xs ml-1 text-gray-700">Ads</span>
                    </div>
                  </motion.div>

                  {/* Animated YouTube logo highlight */}
                  <motion.div
                    className="absolute top-10 right-14 bg-white rounded-full p-2 shadow-xl z-20 flex items-center justify-center"
                    animate={{ 
                      y: [0, 10, 0],
                      boxShadow: [
                        '0 0 0 rgba(234, 67, 53, 0.4)',
                        '0 0 20px rgba(234, 67, 53, 0.6)',
                        '0 0 0 rgba(234, 67, 53, 0.4)'
                      ]
                    }}
                    transition={{ duration: 3.5, delay: 1, repeat: Infinity }}
                  >
                    <div className="flex items-center px-3 py-1">
                      <span className="text-red-600 font-bold text-sm">YouTube</span>
                    </div>
                  </motion.div>

                  {/* Animated elements */}
                  <motion.div
                    className="absolute h-20 w-20 bg-blue-500/10 rounded-full z-10"
                    style={{ top: '20%', left: '20%' }}
                    animate={{ 
                      y: [0, -15, 0], 
                      opacity: [0.5, 1, 0.5],
                      scale: [1, 1.1, 1]
                    }}
                    transition={{ 
                      duration: 4, 
                      repeat: Infinity,
                      repeatType: 'reverse'
                    }}
                  />
                  <motion.div 
                    className="absolute h-15 w-15 bg-[#FF8C2A]/20 rounded-full z-10"
                    style={{ bottom: '30%', right: '15%' }}
                    animate={{ 
                      y: [0, 15, 0], 
                      opacity: [0.6, 1, 0.6],
                      scale: [1, 1.2, 1]
                    }}
                    transition={{ 
                      duration: 3.5, 
                      repeat: Infinity,
                      repeatType: 'reverse',
                      delay: 0.5
                    }}
                  />
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Product Demo Video Section */}
          <motion.div 
            variants={fadeInUp}
            className="mt-20 pt-10 border-t border-gray-200 dark:border-gray-800 max-w-6xl mx-auto"
          >
            <div className="text-center mb-10">
              <h3 className="text-2xl md:text-3xl font-bold mb-4 text-gray-900 dark:text-white">See Linkly in Action</h3>
                              <p className="text-muted-foreground max-w-2xl mx-auto">
                  Watch our comprehensive demonstration of Linkly's powerful features and intuitive workflow in action.
                </p>
            </div>

            <div className="relative rounded-xl overflow-hidden shadow-2xl border-4 border-white dark:border-gray-800">
              <div className="relative w-full aspect-video bg-black">
                {/* Preview Image */}
                {showPreview && (
                  <div 
                    className="absolute inset-0 bg-cover bg-center cursor-pointer"
                    style={{ 
                      backgroundImage: 'url(https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=2940)',
                      filter: 'brightness(0.8)'
                    }}
                    onClick={handleVideoPlay}
                  >
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="bg-white/90 rounded-full p-4 transform transition-transform hover:scale-110">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FF8C2A" className="h-12 w-12">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                )}

                {/* Loading Spinner */}
                {!isVideoLoaded && !showPreview && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#FF8C2A] border-t-transparent"></div>
                  </div>
                )}

                {/* Video End State with Logo */}
                {isVideoEnded && (
                  <div 
                    className="absolute inset-0 bg-black/90 flex flex-col items-center justify-center cursor-pointer"
                    onClick={handleVideoPlay}
                  >
                    <div className="relative h-20 w-48 mb-4">
                      <Image 
                        src={logo} 
                        alt="Linkly Logo" 
                        className="object-contain" 
                        fill
                        sizes="(max-width: 768px) 120px, 160px"
                      />
                    </div>
                    <Button
                      size="lg"
                      className="bg-[#FF8C2A] text-white hover:bg-[#e67e25] hover:scale-105 transform transition-all duration-200 shadow-xl"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleVideoPlay()
                      }}
                    >
                      Watch Again
                      <PlayCircle className="ml-2 h-5 w-5" />
                    </Button>
                  </div>
                )}

                <video
                  ref={videoRef}
                  className="w-full h-full object-cover"
                  playsInline
                  preload="metadata"
                  onLoadedData={handleVideoLoad}
                  onClick={handleVideoPlay}
                  onEnded={handleVideoEnd}
                >
                  <source src="/Linkly.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                
                {/* Video controls overlay - always visible on mobile, visible on hover for desktop */}
                {!showPreview && (
                  <div 
                    className="absolute inset-0 flex items-center justify-center bg-black/40 md:opacity-0 md:hover:opacity-100 transition-opacity duration-300"
                    onClick={handleVideoPlay}
                  >
                    <Button
                      size="lg"
                      className="bg-white/90 text-gray-900 hover:bg-white hover:scale-105 transform transition-all duration-200 shadow-xl"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleVideoPlay()
                      }}
                    >
                      {isVideoPlaying ? (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-8 w-8">
                          <rect x="6" y="4" width="4" height="16" />
                          <rect x="14" y="4" width="4" height="16" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-8 w-8">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </section>
      </main>

      {/* Footer */}
      <SiteFooter />
    </div>
  )
}


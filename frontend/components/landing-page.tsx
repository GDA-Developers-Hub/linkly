"use client"

import * as React from "react"
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
  ArrowUpRight,
  ChevronLeft,
} from "lucide-react"
import { PlatformIcons } from "@/components/platform-icons"
import { SocialIntegrationIllustrationV2 } from "@/components/illustrations/social-integration-illustration-v2"
import { useTheme } from "next-themes"
import { useIsMobile } from "@/components/ui/use-mobile"
import { cn } from "@/lib/utils"
import { AspectRatio } from "@/components/ui/aspect-ratio"
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel"
import { PartnerCarousel } from "@/components/partner-carousel"

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

  const [testimonials] = React.useState<Testimonial[]>([
    {
      id: 1,
      quote: "Linkly has transformed how we manage our social media. The time savings alone are worth every penny!",
      author: "Sarah Johnson",
      role: "Marketing Director",
      company: "TechVision Inc.",
      avatar: "/placeholder-user.jpg",
    },
    {
      id: 2,
      quote: "The analytics and insights have helped us increase engagement by over 40% in just two months.",
      author: "Michael Chen",
      role: "Social Media Manager",
      company: "Global Brands",
      avatar: "/placeholder-user.jpg",
    },
    {
      id: 3,
      quote: "As a small business owner, Linkly gives me enterprise-level tools at a price I can afford.",
      author: "Jessica Williams",
      role: "Founder",
      company: "Bright Ideas Co.",
      avatar: "/placeholder-user.jpg",
    },
  ])

  const [partners] = React.useState<Partner[]>([
    {
      id: 1,
      name: "Google",
      logo: "/google-logo.png",
      description: "Search and advertising partner powering our analytics and ad campaigns.",
    },
    {
      id: 2,
      name: "SocialBu",
      logo: "/socialbu-logo.png",
      description: "Our premier partner for advanced social media analytics and reporting.",
    },
    {
      id: 3,
      name: "AWS",
      logo: "/aws-logo.svg",
      description: "Cloud infrastructure powering our scalable platform services.",
    },
    {
      id: 4,
      name: "LinkedIn",
      logo: "/linkedin-logo.png",
      description: "Professional networking and B2B marketing partner.",
    },
    {
      id: 5,
      name: "Instagram",
      logo: "/instagram-logo.svg",
      description: "Visual storytelling and influencer marketing partner.",
    },
    {
      id: 6,
      name: "WhatsApp",
      logo: "/whatsapp-logo.svg",
      description: "Messaging integration for customer engagement and support.",
    },
    {
      id: 7,
      name: "Facebook",
      logo: "/facebook-logo.svg", 
      description: "Community engagement and advertising partner.",
    },
    {
      id: 8,
      name: "Twitter",
      logo: "/twitter-logo.svg",
      description: "Real-time conversation and trend monitoring partner.",
    },
    {
      id: 9,
      name: "TikTok",
      logo: "/tiktok-logo.png",
      description: "Short-form video content and trending social platform.",
    },
    {
      id: 10,
      name: "YouTube",
      logo: "/youtube-logo.svg",
      description: "Video content hosting and marketing platform integration.",
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

  // Remove the video state variables and functions
  const [videoStream, setVideoStream] = React.useState<MediaStream | null>(null)
  const [isRecording, setIsRecording] = React.useState(false)
  const [recordedChunks, setRecordedChunks] = React.useState<BlobPart[]>([])
  const [recordedVideoUrl, setRecordedVideoUrl] = React.useState<string | null>(null)
  const [showRecorder, setShowRecorder] = React.useState(false)
  const videoRef = React.useRef<HTMLVideoElement>(null)
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null)

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user', width: 1280, height: 720 },
        audio: true 
      });
      setVideoStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setShowRecorder(true);
    } catch (err) {
      console.error("Error accessing camera:", err);
      // Fallback if camera access fails
      setRecordedVideoUrl("/linkly-demo.mp4");
    }
  };

  const startRecording = () => {
    if (!videoStream) return;
    
    setRecordedChunks([]);
    const mediaRecorder = new MediaRecorder(videoStream, { mimeType: 'video/webm' });
    
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        setRecordedChunks(prev => [...prev, e.data]);
      }
    };
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setRecordedVideoUrl(url);
    };
    
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);
    
    // Auto-stop after 30 seconds
    setTimeout(() => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        stopRecording();
      }
    }, 30000);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const resetRecording = () => {
    if (recordedVideoUrl) {
      URL.revokeObjectURL(recordedVideoUrl);
    }
    setRecordedVideoUrl(null);
    setRecordedChunks([]);
  };

  const stopCamera = () => {
    if (videoStream) {
      videoStream.getTracks().forEach(track => track.stop());
      setVideoStream(null);
    }
    setShowRecorder(false);
    resetRecording();
  };

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
      }
      if (recordedVideoUrl) {
        URL.revokeObjectURL(recordedVideoUrl);
      }
    };
  }, [videoStream, recordedVideoUrl]);

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
          scrolled ? "bg-background/80 backdrop-blur-md" : "bg-background"
        )}
      >
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <Image src={logo} alt="Linkly Logo" className="h-12 w-auto" priority />
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              <a
                href="#features"
                onClick={scrollToSection}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                onClick={scrollToSection}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                How it works
              </a>
              <a
                href="#partners"
                onClick={scrollToSection}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Partners
              </a>
              <a
                href="#testimonials"
                onClick={scrollToSection}
                className="text-sm font-medium hover:text-primary transition-colors"
              >
                Testimonials
              </a>
              <div className="flex items-center space-x-4">
                <ModeToggle />
                <Button asChild className="bg-[#FF8C2A] hover:bg-[#e67e25] text-white">
                  <Link href="/auth/register">Try for free</Link>
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
            <a
              href="#partners"
                onClick={scrollToSection}
                className="flex items-center justify-between py-2 text-sm font-medium hover:text-primary transition-colors"
            >
              Partners
                <ChevronRight className="h-4 w-4" />
            </a>
            <a
              href="#testimonials"
                onClick={scrollToSection}
                className="flex items-center justify-between py-2 text-sm font-medium hover:text-primary transition-colors"
            >
              Testimonials
                <ChevronRight className="h-4 w-4" />
              </a>
              <Button asChild className="w-full bg-[#FF8C2A] hover:bg-[#e67e25] text-white">
                <Link href="/auth/register">Try for free</Link>
              </Button>
          </nav>
          </motion.div>
        )}
      </motion.header>

      <main className="flex-1">
        {/* Hero Section */}
        <section
          ref={heroRef as React.RefObject<HTMLDivElement>}
          className="relative overflow-hidden py-20 md:py-32 bg-gradient-to-br from-[#FF8C2A]/10 via-white to-[#FF8C2A]/5"
        >
              <motion.div
                initial="hidden"
                animate={heroInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="container px-4 mx-auto"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <motion.div variants={fadeInLeft} className="text-center lg:text-left">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 text-gray-900 dark:text-white">
                  Simplify Your Social Media Management
                </h1>
                <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto lg:mx-0">
                  Schedule posts, analyze performance, and grow your social media presence with our all-in-one platform.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                  <Button size="lg" className="bg-[#FF8C2A] hover:bg-[#e67e25] text-white w-full sm:w-auto shadow-lg transition-transform hover:scale-105" asChild>
                    <Link href="/auth/register">
                      Try for free
                      <ChevronRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button
                    size="lg"
                    className="w-full sm:w-auto bg-transparent text-foreground border-foreground hover:bg-foreground/10 transition-transform hover:scale-105"
                    asChild
                  >
                    <a href="#features" onClick={scrollToSection}>
                      Learn more
                    </a>
                  </Button>
                </div>
              </motion.div>
              <motion.div variants={fadeInRight} className="relative flex justify-center lg:justify-end">
                <div className="w-full max-w-xl h-[400px] rounded-xl shadow-2xl border-4 border-white dark:border-gray-900 bg-gradient-to-br from-background to-muted/50 flex items-center justify-center">
                  <PlatformIcons />
                </div>
              </motion.div>
            </div>
            </motion.div>
        </section>

        {/* Features Section */}
        <section
          id="features"
          ref={featuresRef as React.RefObject<HTMLDivElement>}
          className="py-20 md:py-32 bg-muted/50"
        >
            <motion.div
              initial="hidden"
              animate={featuresInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="container px-4 mx-auto"
          >
            <motion.div variants={fadeInUp} className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900 dark:text-white">Powerful Features for Modern Social Media</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Everything you need to manage your social media presence effectively and grow your audience.
              </p>
            </motion.div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  variants={fadeInUp}
                  className="bg-background rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow border border-gray-100 dark:border-gray-800 flex flex-col items-center text-center group"
                >
                  <feature.icon className="h-12 w-12 text-[#FF8C2A] mb-4 group-hover:scale-110 transition-transform" />
                  <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </motion.div>
              ))}
            </div>
            </motion.div>
        </section>

        {/* How It Works Section */}
        <section
          id="how-it-works"
          ref={howItWorksRef as React.RefObject<HTMLDivElement>}
          className="py-20 md:py-32 relative overflow-hidden"
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
                        Google Ads Integration
                        <ArrowUpRight className="ml-2 h-5 w-5 text-[#FF8C2A]" />
                      </h3>
                      <p className="text-muted-foreground text-lg font-medium">
                        Seamlessly connect your Google Ads campaigns with your social media strategy for maximum ROI.
                      </p>
                      <div className="mt-3 flex items-center">
                        <div className="mr-4 flex items-center">
                          <motion.div 
                            className="h-4 w-4 rounded-full bg-green-500 mr-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          />
                          <span className="text-sm">Real-time data</span>
                        </div>
                        <div className="flex items-center">
                          <motion.div 
                            className="h-4 w-4 rounded-full bg-blue-500 mr-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, delay: 0.5, repeat: Infinity }}
                          />
                          <span className="text-sm">Unified metrics</span>
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
        </section>

        {/* Partners Section */}
        <section
          id="partners"
          ref={partnersRef as React.RefObject<HTMLDivElement>}
          className="py-20 md:py-32 bg-muted/50 relative overflow-hidden"
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
            animate={partnersInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="container px-4 mx-auto relative z-10"
          >
            <motion.div variants={fadeInUp} className="text-center mb-16">
              <div className="inline-block mb-3">
                <span className="inline-block px-4 py-1 rounded-full bg-[#FF8C2A]/10 text-[#FF8C2A] font-medium text-sm">
                  Trusted Partnerships
                </span>
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900 dark:text-white">Our Technology Partners</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                We work with industry leaders to provide you with the best social media management experience.
              </p>
            </motion.div>

            <motion.div 
              variants={fadeInUp}
              className="max-w-6xl mx-auto"
            >
              <PartnerCarousel partners={partners} />
            </motion.div>
          </motion.div>
        </section>

        {/* Testimonials Section */}
        <section
          id="testimonials"
          ref={testimonialsRef as React.RefObject<HTMLDivElement>}
          className="py-20 md:py-32"
        >
            <motion.div
              initial="hidden"
              animate={testimonialsInView ? "visible" : "hidden"}
            variants={staggerContainer}
            className="container px-4 mx-auto"
          >
            <motion.div variants={fadeInUp} className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900 dark:text-white">What Our Customers Say</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Join thousands of satisfied customers who have transformed their social media management with Linkly.
              </p>
            </motion.div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={testimonial.id}
                  variants={fadeInScale}
                  className="bg-background rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-shadow border border-gray-100 dark:border-gray-800 flex flex-col"
                >
                  <div className="flex items-center gap-4 mb-4">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold shadow ${
                        index % 3 === 0 ? 'bg-[#FF8C2A]' : 
                        index % 3 === 1 ? 'bg-blue-500' : 
                        'bg-green-500'
                      }`}
                    >
                      {testimonial.author.split(' ').map(name => name[0]).join('')}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">{testimonial.author}</h3>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
                        {testimonial.company && ` at ${testimonial.company}`}
                      </p>
                    </div>
                  </div>
                  <p className="text-muted-foreground">{testimonial.quote}</p>
                </motion.div>
              ))}
            </div>
            </motion.div>
        </section>

        {/* CTA Section */}
        <section className="py-20 md:py-32 bg-gradient-to-r from-[#FF8C2A]/10 via-white to-[#FF8C2A]/5">
          <div className="container px-4 mx-auto">
            <div className="text-center text-gray-900 dark:text-white">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Transform Your Social Media?</h2>
              <p className="text-lg mb-8 max-w-2xl mx-auto opacity-90">
                Join thousands of businesses already using Linkly to grow their social media presence.
              </p>
              <Button
                size="lg"
                className="bg-[#FF8C2A] text-white hover:bg-[#e67e25] transition-transform hover:scale-105 shadow-lg"
                asChild
              >
                <Link href="/auth/register">
                  Get Started Now
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-12 md:py-16 bg-background border-t">
        <div className="container px-4 mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div>
              <Link href="/" className="flex items-center mb-6">
                <Image src={logo} alt="Linkly Logo" className="h-12 w-auto" priority />
              </Link>
              <p className="text-sm text-muted-foreground">
                Simplify your social media management with our powerful platform.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-3">
                <li>
                  <a href="#features" onClick={scrollToSection} className="text-sm text-muted-foreground hover:text-primary">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#how-it-works" onClick={scrollToSection} className="text-sm text-muted-foreground hover:text-primary">
                    How it works
                  </a>
                </li>
                <li>
                  <a href="#partners" onClick={scrollToSection} className="text-sm text-muted-foreground hover:text-primary">
                    Partners
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-3">
                <li>
                  <Link href="/about" className="text-sm text-muted-foreground hover:text-primary">
                    About us
                  </Link>
                </li>
                <li>
                  <Link href="/contact" className="text-sm text-muted-foreground hover:text-primary">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link href="/privacy" className="text-sm text-muted-foreground hover:text-primary">
                    Privacy
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Connect</h3>
              <ul className="space-y-3">
                <li>
                  <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                    Twitter
                  </a>
                </li>
                <li>
                  <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                    LinkedIn
                  </a>
                  </li>
                <li>
                  <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                    Instagram
                  </a>
                  </li>
              </ul>
            </div>
              </div>
          <div className="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; {new Date().getFullYear()} Linkly. All rights reserved.</p>
            </div>
        </div>
      </footer>
    </div>
  )
}

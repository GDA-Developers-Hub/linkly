"use client"

import React, { useState, useEffect, useRef } from 'react'
import Link from "next/link"
import { motion, useInView } from "framer-motion"
import { Button } from "@/components/ui/button"
import { CheckCircle2, ChevronRight } from "lucide-react"

// Custom hook for scroll animations
function useScrollAnimation(threshold = 0.1): [React.RefObject<HTMLElement>, boolean] {
  const ref = useRef<HTMLElement>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries: IntersectionObserverEntry[]) => {
        const [entry] = entries
        if (entry) {
          setIsVisible(entry.intersectionRatio > threshold)
        }
      },
      { threshold }
    )

    const currentRef = ref.current
    if (currentRef) {
      observer.observe(currentRef)
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef)
      }
    }
  }, [threshold])

  return [ref, isVisible]
}

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
}

const fadeInScale = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.6 } }
}

const fadeInLeft = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.6 } }
}

const fadeInRight = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.6 } }
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
}

function Pricing() {
  const [scrolled, setScrolled] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  
  // Use custom scroll animation hooks
  const [pricingRef, pricingInView] = useScrollAnimation()
  const [testimonialRef, testimonialInView] = useScrollAnimation()
  const [ctaRef, ctaInView] = useScrollAnimation(0.5)

  interface PricingPlan {
    id: number
    name: string
    price: number
    description: string
    features: string[]
  }

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

  // Sample testimonials data
  const testimonials = [
    {
      id: 1,
      quote: "Linkly has transformed how we manage our social media presence. The scheduling features save us hours every week.",
      author: "Sarah Johnson",
      role: "Marketing Director, TechFlow"
    },
    {
      id: 2,
      quote: "The analytics provided by Linkly helped us increase our engagement by 45% in just two months.",
      author: "Michael Chen",
      role: "Social Media Manager, GrowthHub"
    },
    {
      id: 3,
      quote: "As a small business owner, I was looking for an affordable solution. Linkly provides enterprise-level features at a price I can afford.",
      author: "Emily Rodriguez",
      role: "Founder, Artisan Crafts"
    }
  ]

  return (
    <div>
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
                <Link href="/pricing">
                  View pricing
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

export default Pricing
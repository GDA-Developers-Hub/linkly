"use client"

import React from "react"
import { useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { CheckCircle2, ChevronRight } from "lucide-react"

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

export default function PricingPage() {
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
  ]);

  return (
    <>
      {/* Pricing Hero Section */}
      <section className="bg-primary/5 py-20">
        <div className="container mx-auto px-4">
          <motion.div
            className="mx-auto max-w-3xl text-center"
            initial="hidden"
            animate="visible" 
            variants={fadeInUp}
          >
            <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
              Pricing
            </div>
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl">Simple, Transparent Pricing</h1>
            <p className="mt-4 text-lg text-muted-foreground">
              Choose the plan that's right for your business. All plans include a 14-day free trial.
            </p>
          </motion.div>

          <motion.div
            className="mt-16 grid gap-8 md:grid-cols-3"
            initial="hidden"
            animate="visible"
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
                <Button className="mt-8 w-full" variant={plan.id === 2 ? "default" : "outline"}>
                  Get started
                </Button>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            className="mx-auto max-w-3xl text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-block px-3 py-1 mb-4 text-xs font-semibold text-primary bg-primary/10 rounded-full">
              FAQ
            </div>
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Frequently Asked Questions</h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Everything you need to know about our pricing and plans
            </p>
          </motion.div>

          <div className="mt-16 mx-auto max-w-4xl">
            <motion.div
              className="grid gap-6 md:grid-cols-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <div className="rounded-lg border bg-card p-6">
                <h3 className="text-lg font-medium">Can I switch plans later?</h3>
                <p className="mt-2 text-muted-foreground">
                  Yes, you can upgrade or downgrade your plan at any time. Changes will be reflected on your next billing cycle.
                </p>
              </div>
              <div className="rounded-lg border bg-card p-6">
                <h3 className="text-lg font-medium">What happens after my trial?</h3>
                <p className="mt-2 text-muted-foreground">
                  After your 14-day trial, you'll be automatically subscribed to your chosen plan. You can cancel anytime before the trial ends.
                </p>
              </div>
              <div className="rounded-lg border bg-card p-6">
                <h3 className="text-lg font-medium">Do you offer discounts?</h3>
                <p className="mt-2 text-muted-foreground">
                  We offer special pricing for non-profits and educational institutions. Contact our sales team for more information.
                </p>
              </div>
              <div className="rounded-lg border bg-card p-6">
                <h3 className="text-lg font-medium">Is there a setup fee?</h3>
                <p className="mt-2 text-muted-foreground">
                  No, there are no hidden fees. The price you see is the price you pay.
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary text-primary-foreground py-16">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            className="mx-auto max-w-3xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">Ready to get started?</h2>
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
              >
                Contact sales
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  )
} 
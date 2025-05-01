import { Metadata } from "next"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

export const metadata: Metadata = {
  title: "Linkly - Pricing",
  description: "Simple, transparent pricing for Linkly - Connect your digital world, seamlessly.",
}

interface PricingLayoutProps {
  children: React.ReactNode
}

export default function PricingLayout({ children }: PricingLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <MainNav />
      <main className="flex-1">{children}</main>
      <SiteFooter />
    </div>
  )
} 
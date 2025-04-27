"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Check, Zap, Globe, Users, Calendar, BarChart4, Sparkles } from "lucide-react"
import { useAuth } from "@/contexts/auth-context"
import { getAPI, type Plan } from "@/lib/api"
import { useToast } from "@/components/ui/use-toast"
import Swal from 'sweetalert2'

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function SubscriptionPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { user } = useAuth()
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [pageLoading, setPageLoading] = useState(true)
  const api = getAPI()

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const fetchedPlans = await api.getPlans()
        
        // Ensure plans is an array
        if (Array.isArray(fetchedPlans)) {
          setPlans(fetchedPlans)
          
          // Default select the first plan
          if (fetchedPlans.length > 0) {
            setSelectedPlanId(fetchedPlans[0].id)
          }
        } else {
          console.error("Invalid plans data:", fetchedPlans)
          setPlans([])
          toast({
            title: "Error",
            description: "Received invalid plan data from server",
            variant: "destructive"
          })
        }
      } catch (error) {
        console.error("Error fetching plans:", error)
        toast({
          title: "Error",
          description: "Could not load subscription plans. Please try again later.",
          variant: "destructive"
        })
        setPlans([]) // Ensure plans is an empty array in case of error
      } finally {
        setPageLoading(false)
      }
    }

    fetchPlans()
  }, [])

  const handleContinue = async () => {
    if (!selectedPlanId) {
      toast({
        title: "Error",
        description: "Please select a plan to continue",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)
    try {
      // For this implementation, we're creating a subscription without payment processing
      // In a real app, you would handle payment collection first
      await api.createSubscription(selectedPlanId, "dummy-payment-method-id")
      
      toast({
        title: "Success",
        description: "Your subscription has been set up successfully!",
        variant: "default"
      })
      
      // Redirect to dashboard
      router.push("/dashboard")
    } catch (error) {
      console.error("Error creating subscription:", error)
      
      Swal.fire({
        title: 'Subscription Error',
        text: 'Failed to create your subscription. Please try again.',
        icon: 'error',
        confirmButtonText: 'OK'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const getPlanIcon = (featureName: string) => {
    switch(featureName) {
      case 'posts': return <Zap className="h-5 w-5 text-indigo-400" />;
      case 'accounts': return <Globe className="h-5 w-5 text-emerald-400" />;
      case 'team': return <Users className="h-5 w-5 text-amber-400" />;
      case 'analytics': return <BarChart4 className="h-5 w-5 text-purple-400" />;
      case 'ai': return <Sparkles className="h-5 w-5 text-blue-400" />;
      case 'scheduling': return <Calendar className="h-5 w-5 text-rose-400" />;
      default: return <Check className="h-5 w-5 text-[#FF8C2A]" />;
    }
  }

  if (pageLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 to-black">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-[#FF8C2A] border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-gray-900 to-black p-4">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
      
      <div className="relative mx-auto max-w-5xl w-full z-10">
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="relative h-12 w-12 overflow-hidden rounded-full bg-[#FF8C2A]">
              <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-3xl">L</div>
            </div>
            <span className="text-[#1E5AA8] font-bold text-3xl ml-2 self-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">inkly</span>
          </div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-300">Choose Your Plan</h1>
          <p className="text-gray-400 mt-2 max-w-md mx-auto">Elevate your social media strategy with our specialized subscription options</p>
        </div>

        {plans.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <Card 
                key={plan.id}
                className={`backdrop-blur-sm bg-black/50 border border-gray-800 hover:border-gray-700 transition-all duration-300 overflow-hidden group ${
                  selectedPlanId === plan.id 
                    ? "ring-2 ring-[#FF8C2A] shadow-lg shadow-[#FF8C2A]/20" 
                    : ""
                }`}
              >
                <div className={`h-1.5 w-full ${selectedPlanId === plan.id ? "bg-gradient-to-r from-[#FF8C2A] to-[#FF8C2A]/60" : "bg-transparent"}`}></div>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-white text-xl">{plan.name}</CardTitle>
                      <CardDescription className="text-gray-400 mt-1">{plan.description}</CardDescription>
                    </div>
                    <Badge variant="outline" className="bg-black/30 text-gray-300 border-gray-700">
                      {plan.frequency}
                    </Badge>
                  </div>
                  <div className="mt-5">
                    <span className="text-4xl font-bold text-white">${parseFloat(plan.price).toFixed(2)}</span>
                    <span className="text-gray-400">/{plan.frequency}</span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-5">
                  <ul className="space-y-3">
                    <li className="flex items-start gap-3">
                      {getPlanIcon('posts')}
                      <span className="text-gray-300"><span className="font-semibold text-white">{plan.post_limit}</span> posts per month</span>
                    </li>
                    <li className="flex items-start gap-3">
                      {getPlanIcon('accounts')}
                      <span className="text-gray-300"><span className="font-semibold text-white">{plan.account_limit}</span> social accounts</span>
                    </li>
                    <li className="flex items-start gap-3">
                      {getPlanIcon('team')}
                      <span className="text-gray-300"><span className="font-semibold text-white">{plan.team_members}</span> team member{plan.team_members > 1 ? 's' : ''}</span>
                    </li>
                    {plan.analytics_access && (
                      <li className="flex items-start gap-3">
                        {getPlanIcon('analytics')}
                        <span className="text-gray-300">Advanced analytics</span>
                      </li>
                    )}
                    {plan.ai_generation && (
                      <li className="flex items-start gap-3">
                        {getPlanIcon('ai')}
                        <span className="text-gray-300">AI content generation</span>
                      </li>
                    )}
                    {plan.post_scheduling && (
                      <li className="flex items-start gap-3">
                        {getPlanIcon('scheduling')}
                        <span className="text-gray-300">Automated scheduling</span>
                      </li>
                    )}
                    {plan.calendar_view && (
                      <li className="flex items-start gap-3">
                        <Calendar className="h-5 w-5 text-teal-400" />
                        <span className="text-gray-300">Calendar view</span>
                      </li>
                    )}
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button
                    onClick={() => setSelectedPlanId(plan.id)}
                    variant={selectedPlanId === plan.id ? "default" : "outline"}
                    className={`w-full transition-all duration-300 rounded-lg ${
                      selectedPlanId === plan.id 
                        ? "bg-gradient-to-r from-[#FF8C2A] to-[#FF6B2A] text-white hover:shadow-lg hover:shadow-orange-600/20" 
                        : "bg-black/30 border-gray-700 text-gray-300 hover:text-white hover:bg-black/50"
                    }`}
                  >
                    {selectedPlanId === plan.id ? "Selected" : "Select Plan"}
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        ) : (
          <div className="col-span-3 text-center p-8 bg-black/30 border border-gray-800 rounded-xl backdrop-blur-sm">
            <h3 className="text-lg font-medium text-white">No subscription plans available</h3>
            <p className="text-gray-400 mt-2">Please try again later or contact support.</p>
            <Button onClick={() => router.push('/dashboard')} className="mt-4 bg-[#1E5AA8] hover:bg-[#174a8c]">
              Go to Dashboard
            </Button>
          </div>
        )}

        <div className="mt-12 text-center">
          <Button 
            onClick={handleContinue} 
            className="bg-gradient-to-r from-[#1E5AA8] to-[#3A7AE8] hover:shadow-lg hover:shadow-blue-600/20 px-10 py-6 text-lg transition-all duration-300"
            disabled={isLoading || !selectedPlanId}
          >
            {isLoading ? (
              <div className="flex items-center">
                <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                <span>Processing...</span>
              </div>
            ) : (
              <div className="flex items-center">
                <span>Activate Selected Plan</span>
                <Zap className="ml-2 h-5 w-5" />
              </div>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

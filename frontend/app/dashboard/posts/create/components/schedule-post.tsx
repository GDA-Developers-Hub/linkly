import { Calendar } from "@/components/ui/calendar"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { CalendarIcon, Clock } from "lucide-react"
import { TimePickerDemo } from "./time-picker"
import { useToast } from "@/components/ui/use-toast"

interface SchedulePostProps {
  date: Date | undefined
  setDate: (date: Date | undefined) => void
  selectedPlatforms: string[]
}

export function SchedulePost({ date, setDate, selectedPlatforms }: SchedulePostProps) {
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const suggestOptimalTime = async () => {
    if (selectedPlatforms.length === 0) {
      toast({
        title: "No platforms selected",
        description: "Please select at least one platform to get optimal posting time.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      const platform = selectedPlatforms[0] // Use first selected platform

      const response = await fetch('/api/ai/optimal-time/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform,
          timezone,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get optimal time suggestion')
      }

      const data = await response.json()
      
      // Parse the suggested time
      const now = new Date()
      const [hours, minutes] = data.bestTime.split(':').map(Number)
      const suggestedDate = new Date(now)
      suggestedDate.setHours(hours, minutes, 0, 0)

      // If suggested time is earlier than now, set it for tomorrow
      if (suggestedDate < now) {
        suggestedDate.setDate(suggestedDate.getDate() + 1)
      }

      setDate(suggestedDate)
      
      toast({
        title: "Optimal time suggested",
        description: data.explanation || "Based on your platform and timezone.",
      })
    } catch (error) {
      console.error('Error getting optimal time:', error)
      toast({
        title: "Suggestion failed",
        description: "Could not get optimal posting time. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col space-y-4">
      <div className="flex items-center space-x-4">
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-[240px] justify-start text-left font-normal",
                !date && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date ? format(date, "PPP") : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              selected={date}
              onSelect={setDate}
              initialFocus
            />
          </PopoverContent>
        </Popover>

        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-[140px] justify-start text-left font-normal",
                !date && "text-muted-foreground"
              )}
              disabled={!date}
            >
              <Clock className="mr-2 h-4 w-4" />
              {date ? format(date, "HH:mm") : <span>Pick time</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <div className="p-4">
              <TimePickerDemo date={date} setDate={setDate} />
            </div>
          </PopoverContent>
        </Popover>

        <Button
          variant="secondary"
          onClick={suggestOptimalTime}
          disabled={isLoading}
        >
          {isLoading ? "Suggesting..." : "Suggest optimal time"}
        </Button>
      </div>
    </div>
  )
} 
import { useState } from 'react'
 
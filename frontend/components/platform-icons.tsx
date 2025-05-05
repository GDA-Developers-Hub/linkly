'use client'

import { memo } from "react"
import {
  Facebook,
  Instagram,
  Twitter,
  Youtube,
  TwitterIcon as TikTok,
  PinIcon as Pinterest,
  MessageSquareIcon as Discord,
  Camera as Snapchat,
  Hash as Threads
} from "lucide-react"

// Calculate positions for icons on a single orbit
const calculatePosition = (index: number, total: number) => {
  const radius = 42; // Radius for the single orbit - exactly matching the screenshot
  
  // Calculate angle, distribute evenly
  const angle = (index * 2 * Math.PI) / total - Math.PI / 2; // Start from top
  
  const x = 50 + radius * Math.cos(angle);
  const y = 50 + radius * Math.sin(angle);
  
  return { top: `${y}%`, left: `${x}%` };
}

// Platform configuration to match the circular layout in the screenshot
const platformConfig = [
  {
    name: "Instagram",
    icon: Instagram,
    color: "bg-[#E1306C]",
  },
  {
    name: "Facebook",
    icon: Facebook,
    color: "bg-[#1877F2]",
  },
  {
    name: "TikTok",
    icon: TikTok,
    color: "bg-black",
  },
  {
    name: "Pinterest",
    icon: Pinterest,
    color: "bg-[#E60023]",
  },
  {
    name: "Discord",
    icon: Discord,
    color: "bg-[#5865F2]",
  },
  {
    name: "Threads",
    icon: Threads,
    color: "bg-black",
  },
  {
    name: "YouTube",
    icon: Youtube,
    color: "bg-[#FF0000]",
  },
  {
    name: "Snapchat",
    icon: Snapchat,
    color: "bg-[#FFFC00] text-black",
  },
  {
    name: "Twitter",
    icon: Twitter,
    color: "bg-[#1DA1F2]",
  }
].map((platform, index, array) => ({
  ...platform,
  position: calculatePosition(index, array.length)
}))

// Define position type for TypeScript
type Position = {
  top: string;
  left: string;
}

// Simple platform icon component
const PlatformIcon = memo(({ 
  platform,
  index
}: { 
  platform: typeof platformConfig[0],
  index: number
}) => {
  const position = platform.position as Position;

  return (
    <div
      className="absolute"
      style={{
        top: position.top,
        left: position.left,
        transform: 'translate(-50%, -50%)',
        zIndex: 10
      }}
    >
      <div 
        className={`w-10 h-10 ${platform.color} rounded-full flex items-center justify-center shadow-md`}
      >
        <platform.icon className="h-5 w-5 text-white" />
      </div>
    </div>
  )
})

PlatformIcon.displayName = 'PlatformIcon'

// Main component that displays the orange circle with L surrounded by social media icons
function PlatformIconsComponent() {
  return (
    <div className="relative w-full h-full min-h-[400px] flex items-center justify-center">
      {/* Main content area */}
      <div className="relative w-[340px] h-[340px] md:w-[400px] md:h-[400px]">
        {/* Orbit ring - thin white circle */}
        <div className="absolute inset-0 rounded-full border border-gray-200 opacity-30"></div>

        {/* Connection dots - small dots on orbit line */}
        {[...Array(18)].map((_, i) => {
          const angle = (i * 20 * Math.PI) / 180;
          const radius = 42;
          return (
            <div 
              key={i}
              className="absolute h-1.5 w-1.5 bg-orange-200 rounded-full"
              style={{
                top: `${50 + radius * Math.sin(angle)}%`,
                left: `${50 + radius * Math.cos(angle)}%`,
                transform: 'translate(-50%, -50%)',
              }}
            />
          );
        })}
        
        {/* Central Logo - Simple orange circle with L */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-28 h-28 md:w-32 md:h-32 z-20">
          {/* White circular shadow */}
          <div className="absolute inset-0 rounded-full bg-white shadow-md -z-10"></div>
          
          {/* Orange circle with L */}
          <div className="w-full h-full rounded-full bg-[#FF8C2A] flex items-center justify-center">
            {/* Letter L */}
            <span className="text-6xl font-bold text-white">
              L
            </span>
          </div>
        </div>

        {/* Social Media Icons */}
        {platformConfig.map((platform, index) => (
          <PlatformIcon
            key={platform.name}
            platform={platform}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}

// Export the component
export const PlatformIcons = memo(PlatformIconsComponent)

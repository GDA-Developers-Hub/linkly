"use client"

import { motion } from "framer-motion"
import {
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
  Youtube,
  TwitterIcon as TikTok,
  PinIcon as Pinterest,
  MessageSquareIcon as Discord,
  Camera as Snapchat,
  Hash as Threads
} from "lucide-react"

// Platform configuration with icons, colors, and hover colors
const platformConfig = [
  {
    name: "Facebook",
    icon: Facebook,
    color: "bg-[#1877F2] hover:bg-[#0c63d4]",
    position: { top: "0%", left: "50%" }
  },
  {
    name: "Instagram",
    icon: Instagram,
    color: "bg-gradient-to-tr from-[#f43b47] to-[#453a94] hover:from-[#d43b47] hover:to-[#353a94]",
    position: { top: "50%", left: "100%" }
  },
  {
    name: "Twitter",
    icon: Twitter,
    color: "bg-[#1DA1F2] hover:bg-[#0d8ed9]",
    position: { top: "100%", left: "50%" }
  },
  {
    name: "LinkedIn",
    icon: Linkedin,
    color: "bg-[#0A66C2] hover:bg-[#084d94]",
    position: { top: "50%", left: "0%" }
  },
  {
    name: "YouTube",
    icon: Youtube,
    color: "bg-[#FF0000] hover:bg-[#cc0000]",
    position: { top: "15%", left: "85%" }
  },
  {
    name: "TikTok",
    icon: TikTok,
    color: "bg-black hover:bg-gray-900",
    position: { top: "20%", left: "15%" }
  },
  {
    name: "Pinterest",
    icon: Pinterest,
    color: "bg-[#E60023] hover:bg-[#b3001b]",
    position: { top: "80%", left: "15%" }
  },
  {
    name: "Discord",
    icon: Discord,
    color: "bg-[#5865F2] hover:bg-[#454fd9]",
    position: { top: "70%", left: "85%" }
  },
  {
    name: "Snapchat",
    icon: Snapchat,
    color: "bg-[#FFFC00] hover:bg-[#e6e300] text-black",
    position: { top: "35%", left: "25%" }
  },
  {
    name: "Threads",
    icon: Threads,
    color: "bg-black hover:bg-gray-900",
    position: { top: "65%", left: "25%" }
  }
]

export function PlatformIcons() {
  return (
    <div className="relative w-full h-full min-h-[400px]">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative w-64 h-64 md:w-80 md:h-80">
          {/* Central Logo */}
          <motion.div 
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-28 h-28 md:w-40 md:h-40 bg-white rounded-full shadow-xl flex items-center justify-center z-10"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="w-24 h-24 md:w-36 md:h-36 rounded-full bg-gradient-to-br from-[#FF8C2A] to-[#e67e25] flex items-center justify-center">
              <span className="text-3xl md:text-5xl font-bold text-white">L</span>
            </div>
          </motion.div>

          {/* Orbiting Platforms */}
          <motion.div 
            className="absolute w-full h-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
          >
            {platformConfig.map((platform, index) => (
              <motion.div
                key={platform.name}
                className="absolute"
                style={{
                  top: platform.position.top,
                  left: platform.position.left,
                  transform: 'translate(-50%, -50%)'
                }}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                <motion.div 
                  className={`w-12 h-12 ${platform.color} rounded-full flex items-center justify-center shadow-lg cursor-pointer transition-transform duration-200 hover:scale-110`}
                  whileHover={{ scale: 1.2 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <platform.icon className="h-6 w-6 text-white" />
                </motion.div>
              </motion.div>
            ))}
          </motion.div>

          {/* Connection Lines */}
          <motion.div 
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className="w-full h-full border-2 border-[#FF8C2A]/30 rounded-full animate-pulse"></div>
          </motion.div>
          <motion.div 
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            <div className="w-3/4 h-3/4 border-2 border-[#FF8C2A]/20 rounded-full"></div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { SocialAccount } from "@/services/social-platforms-api"

// Platform type definition
interface Platform {
  id: string;
  name: string;
  icon: React.ElementType;
  description: string;
  color: string;
  popular: boolean;
}

// Props for the CircularNav component
interface CircularNavProps {
  platforms: Platform[];
  onSelectPlatform: (platform: Platform) => void;
  selectedPlatformId: string | null;
}

// Calculate position on the circle
const calculatePosition = (index: number, total: number, radius: number) => {
  const angleStep = (2 * Math.PI) / total;
  const angle = index * angleStep - Math.PI / 2; // Start from top
  
  return {
    x: radius * Math.cos(angle),
    y: radius * Math.sin(angle)
  };
};

// Main circular navigation component
export function CircularNav({ platforms, onSelectPlatform, selectedPlatformId }: CircularNavProps) {
  const [isHovering, setIsHovering] = useState<string | null>(null);
  const [rotationOffset, setRotationOffset] = useState(0);
  
  // Subtle continuous rotation
  useEffect(() => {
    const interval = setInterval(() => {
      setRotationOffset(prev => (prev + 0.1) % 360);
    }, 100);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="relative flex items-center justify-center w-full my-8" style={{ height: '400px' }}>
      {/* Central Logo */}
      <motion.div 
        className="absolute z-20 w-20 h-20 rounded-full bg-gradient-to-r from-orange-500 to-orange-400 flex items-center justify-center text-4xl font-bold text-white shadow-xl"
        initial={{ scale: 0 }}
        animate={{ 
          scale: [0.9, 1, 0.9],
          transition: { 
            repeat: Infinity, 
            duration: 3 
          }
        }}
      >
        L
      </motion.div>
      
      {/* Orbital Rings */}
      <motion.div 
        className="absolute w-72 h-72 rounded-full border-2 border-gray-700 opacity-25"
        animate={{ rotate: rotationOffset }}
        transition={{ ease: "linear", duration: 1 }}
      />
      <motion.div 
        className="absolute w-96 h-96 rounded-full border border-gray-700 opacity-20"
        animate={{ rotate: -rotationOffset }}
        transition={{ ease: "linear", duration: 1 }}
      />
      
      {/* Platform Icons */}
      {platforms.map((platform: Platform, index: number) => {
        const position = calculatePosition(
          index, 
          platforms.length, 
          150 // radius
        );
        
        const isSelected = selectedPlatformId === platform.id;
        const isHovered = isHovering === platform.id;
        
        return (
          <motion.div
            key={platform.id}
            className={`absolute cursor-pointer rounded-full flex items-center justify-center
                      ${isSelected ? 'ring-2 ring-white ring-offset-2' : ''}`}
            style={{ zIndex: isSelected || isHovered ? 10 : 1 }}
            initial={{ opacity: 0, scale: 0, x: 0, y: 0 }}
            animate={{ 
              opacity: 1, 
              scale: isSelected ? 1.2 : isHovered ? 1.1 : 1,
              x: position.x, 
              y: position.y,
              transition: { 
                type: "spring", 
                stiffness: 300, 
                damping: 25,
                delay: index * 0.05 
              }
            }}
            whileHover={{ scale: 1.1 }}
            onHoverStart={() => setIsHovering(platform.id)}
            onHoverEnd={() => setIsHovering(null)}
            onClick={() => onSelectPlatform(platform)}
          >
            <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${platform.color} 
                        flex items-center justify-center shadow-lg`}>
              <platform.icon className="h-6 w-6 text-white" />
            </div>
            
            {/* Tooltip on hover or selection */}
            {(isHovered || isSelected) && (
              <motion.div 
                className="absolute top-full mt-2 px-2 py-1 bg-black bg-opacity-75 text-white text-xs rounded whitespace-nowrap"
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
              >
                {platform.name}
              </motion.div>
            )}
          </motion.div>
        );
      })}
    </div>
  );
} 
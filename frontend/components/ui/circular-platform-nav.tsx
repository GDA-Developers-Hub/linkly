"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"

// Platform icon component
type PlatformIconProps = {
  icon: React.ElementType;
  color: string;
  index: number;
  total: number;
  size?: number;
  isSelected?: boolean;
  onClick?: () => void;
  name: string;
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

// Individual platform icon
const PlatformIcon = ({ icon: Icon, color, index, total, size = 50, isSelected = false, onClick, name }: PlatformIconProps) => {
  const position = calculatePosition(index, total, 150);
  
  return (
    <motion.div
      className="absolute"
      initial={{ opacity: 0, scale: 0 }}
      animate={{ 
        opacity: 1, 
        scale: isSelected ? 1.2 : 1,
        x: position.x, 
        y: position.y,
        transition: { 
          type: "spring", 
          stiffness: 300, 
          damping: 20,
          delay: index * 0.05 
        }
      }}
      whileHover={{ scale: 1.1, zIndex: 10 }}
      style={{ zIndex: isSelected ? 10 : 1 }}
    >
      <motion.div
        className={`cursor-pointer ${isSelected ? 'ring-2 ring-white' : ''}`}
        onClick={onClick}
      >
        <div className={`flex items-center justify-center rounded-full w-${size / 4} h-${size / 4} bg-gradient-to-br ${color} shadow-lg`} style={{ width: `${size}px`, height: `${size}px` }}>
          <Icon className="text-white" style={{ width: `${size * 0.5}px`, height: `${size * 0.5}px` }} />
        </div>
        {isSelected && (
          <motion.div 
            className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full mt-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs whitespace-nowrap"
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {name}
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
};

// Central logo component
const CentralLogo = () => {
  return (
    <motion.div
      className="absolute z-20 rounded-full bg-gradient-to-r from-orange-500 to-orange-400 flex items-center justify-center text-white font-bold shadow-xl"
      style={{ width: '80px', height: '80px', fontSize: '2.5rem' }}
      initial={{ scale: 0.8 }}
      animate={{ 
        scale: [1, 1.05, 1],
        transition: { 
          repeat: Infinity, 
          repeatType: "reverse", 
          duration: 3,
        }
      }}
    >
      L
    </motion.div>
  );
};

// Orbital rings
const OrbitalRings = () => {
  return (
    <>
      <motion.div
        className="absolute rounded-full border-2 border-gray-700/20"
        style={{ width: '320px', height: '320px' }}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 0.3 }}
        transition={{ duration: 1 }}
      />
      <motion.div
        className="absolute rounded-full border border-gray-700/10"
        style={{ width: '380px', height: '380px' }}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 0.2 }}
        transition={{ duration: 1.2 }}
      />
    </>
  );
};

// Main circular navigation component
type CircularPlatformNavProps = {
  platforms: any[];
  onSelectPlatform: (platform: any) => void;
  selectedPlatformId?: string | null;
}

export function CircularPlatformNav({ platforms, onSelectPlatform, selectedPlatformId }: CircularPlatformNavProps) {
  const [rotationOffset, setRotationOffset] = useState(0);
  
  // Auto-rotate slowly
  useEffect(() => {
    const interval = setInterval(() => {
      setRotationOffset((prev) => (prev + 0.05) % 360);
    }, 100);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="relative flex items-center justify-center w-full" style={{ height: '400px' }}>
      <motion.div 
        className="relative"
        animate={{ rotate: rotationOffset }}
        transition={{ ease: "linear", duration: 2 }}
      >
        <OrbitalRings />
        
        {platforms.map((platform, index) => (
          <PlatformIcon
            key={platform.id}
            icon={platform.icon}
            color={platform.color}
            index={index}
            total={platforms.length}
            isSelected={selectedPlatformId === platform.id}
            onClick={() => onSelectPlatform(platform)}
            name={platform.name}
          />
        ))}
      </motion.div>
      
      <CentralLogo />
    </div>
  );
}

export default CircularPlatformNav; 
"use client"

import { memo, useState, useEffect } from "react"
import { motion, useAnimation, AnimatePresence } from "framer-motion"
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
  Hash as Threads,
  BarChart3 as Analytics
} from "lucide-react"

// Calculate positions for icons on a single orbit
const calculatePosition = (index: number, total: number) => {
  const radius = 42; // Radius for the single orbit

  // Calculate angle, distribute evenly
  const angle = (index * 2 * Math.PI) / total - Math.PI / 2; // Start from top

  const x = 50 + radius * Math.cos(angle);
  const y = 50 + radius * Math.sin(angle);

  // Return position (no orbitIndex needed)
  return { top: `${y}%`, left: `${x}%` };
}

// Platform configuration (no orbitIndex needed)
const platformConfig = [
  {
    name: "Facebook",
    icon: Facebook,
    color: "bg-[#1877F2] hover:bg-[#0c63d4]",
  },
  {
    name: "Instagram",
    icon: Instagram,
    color: "bg-gradient-to-tr from-[#f43b47] to-[#453a94] hover:from-[#d43b47] hover:to-[#353a94]",
  },
  {
    name: "Twitter",
    icon: Twitter,
    color: "bg-[#1DA1F2] hover:bg-[#0d8ed9]",
  },
  {
    name: "LinkedIn",
    icon: Linkedin,
    color: "bg-[#0A66C2] hover:bg-[#084d94]",
  },
  {
    name: "YouTube",
    icon: Youtube,
    color: "bg-[#FF0000] hover:bg-[#cc0000]",
  },
  {
    name: "TikTok",
    icon: TikTok,
    color: "bg-black hover:bg-gray-900",
  },
  {
    name: "Pinterest",
    icon: Pinterest,
    color: "bg-[#E60023] hover:bg-[#b3001b]",
  },
  {
    name: "Discord",
    icon: Discord,
    color: "bg-[#5865F2] hover:bg-[#454fd9]",
  },
  {
    name: "Snapchat",
    icon: Snapchat,
    color: "bg-[#FFFC00] hover:bg-[#e6e300] text-black",
  },
  {
    name: "Threads",
    icon: Threads,
    color: "bg-black hover:bg-gray-900",
  },
  {
    name: "Analytics",
    icon: Analytics,
    color: "bg-[#6366f1] hover:bg-[#4f46e5]",
  }
].map((platform, index, array) => ({
  ...platform,
  position: calculatePosition(index, array.length)
}))

// Define position type for TypeScript (simplified)
type Position = {
  top: string;
  left: string;
  // orbitIndex is removed
}

// Memoized platform icon component
const PlatformIcon = memo(({
  platform,
  index,
  activeIcon,
  setActiveIcon
}: { 
  platform: typeof platformConfig[0],
  index: number,
  activeIcon: string | null,
  setActiveIcon: (name: string | null) => void
}) => {
  const controls = useAnimation();
  const isActive = activeIcon === platform.name;
  const position = platform.position as Position; // Use updated Position type

  useEffect(() => {
    if (isActive) {
      controls.start({
        scale: 1.3,
        zIndex: 50,
        boxShadow: '0 0 30px rgba(255,140,42,0.5)'
      });
    } else {
      controls.start({
        scale: 1,
        zIndex: 10,
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
      });
    }
  }, [isActive, controls]);

  return (
    <motion.div
      key={platform.name}
      className="absolute"
      style={{
        top: position.top,
        left: position.left,
        transform: 'translate(-50%, -50%)' // Center the icon on its position
      }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ 
        delay: index * 0.1, // Stagger initial appearance
        type: "spring",
        stiffness: 260,
        damping: 20
      }}
    >
       <motion.div 
        className={`w-11 h-11 md:w-14 md:h-14 ${platform.color} rounded-full flex items-center justify-center shadow-lg cursor-pointer transition-all duration-300`}
        whileHover={{ 
          scale: 1.2,
          zIndex: 30,
          boxShadow: '0 0 20px rgba(255,140,42,0.3)'
        }}
        whileTap={{ scale: 0.9 }}
        animate={controls}
        onHoverStart={() => setActiveIcon(platform.name)}
        onHoverEnd={() => setActiveIcon(null)}
        onTap={() => setActiveIcon(isActive ? null : platform.name)}
      >
        <platform.icon className="h-5 w-5 md:h-6 md:w-6 text-white" />
      </motion.div>
      
      {isActive && (
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 5 }}
          className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 bg-black bg-opacity-80 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-50"
        >
          {platform.name}
        </motion.div>
      )}
    </motion.div>
  )
})

PlatformIcon.displayName = 'PlatformIcon'

// Rays emanating from the center
const CenterRays = () => {
  return (
    <div className="absolute inset-0">
      {[...Array(12)].map((_, i) => {
        const angle = (i * 30 * Math.PI) / 180;
        const length = Math.random() * 15 + 5; // Random length for rays
        
        return (
          <motion.div
            key={i}
            className="absolute top-1/2 left-1/2 h-0.5 origin-left"
            style={{
              rotate: `${angle}rad`,
              width: `${length}%`,
              backgroundColor: 'rgba(255, 140, 42, 0.15)',
            }}
            initial={{ opacity: 0, scaleX: 0 }}
            animate={{ 
              opacity: [0.3, 0.6, 0.3], 
              scaleX: 1,
            }}
            transition={{
              duration: 3,
              delay: i * 0.2,
              repeat: Infinity,
              repeatType: "reverse"
            }}
          />
        );
      })}
    </div>
  );
};

// Memoized decorative dot component
const DecorativeDot = memo(({ index }: { index: number }) => {
  const angle = (index * 30 * Math.PI) / 180
  const radius = 48 + (index % 3) * 2 // Vary radius slightly for more interesting pattern
  const x = 50 + radius * Math.cos(angle)
  const y = 50 + radius * Math.sin(angle)
  const size = 0.5 + Math.random() * 0.5 // Random sizes for dots
  
  return (
    <motion.div
      className="absolute bg-[#FF8C2A]/30 rounded-full"
      style={{
        top: `${y}%`,
        left: `${x}%`,
        width: `${size}rem`,
        height: `${size}rem`,
        transform: 'translate(-50%, -50%)'
      }}
      initial={{ opacity: 0 }}
      animate={{ 
        opacity: [0.2, 0.6, 0.2],
        scale: [1, 1.2, 1],
      }}
      transition={{ 
        delay: index * 0.1, 
        duration: 3 + index % 3,
        repeat: Infinity
      }}
    />
  )
})

DecorativeDot.displayName = 'DecorativeDot'

// Orbital rings component - Simplified to one main visual ring
const OrbitalRings = () => {
  return (
    <>
      {/* Single Main Ring - Adjust size to match the icon orbit radius */}
      <motion.div 
        className="absolute inset-0 flex items-center justify-center"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
      >
        <div 
          className="w-[84%] h-[84%] border-2 border-[#FF8C2A]/20 rounded-full" // w-84% corresponds roughly to radius 42
        />
      </motion.div>
      {/* Optional inner rings for visual depth, can be removed if needed */}
       <motion.div 
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
        <motion.div 
          className="w-[70%] h-[70%] border border-[#FF8C2A]/10 rounded-full"
          animate={{ rotate: -360 }} // Keep some subtle counter-rotation maybe?
          transition={{ duration: 280, repeat: Infinity, ease: "linear" }}
        />
      </motion.div>
       <motion.div 
        className="absolute inset-0 flex items-center justify-center"
        initial={{ opacity: 0, scale: 0.7 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.7, duration: 0.8 }}
      >
        <motion.div 
          className="w-[50%] h-[50%] border border-[#FF8C2A]/15 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 240, repeat: Infinity, ease: "linear" }}
        />
          </motion.div>
    </>
  );
}

// Connection lines effect around logo
const ConnectionLines = () => {
  // Generate random positions for connections
  const generateConnections = () => {
    return Array.from({ length: 6 }, (_, i) => {
      const angle = (i * 60 * Math.PI) / 180;
      const innerRadius = 15;
      const outerRadius = 40;
      
      return { 
        x1: 50 + innerRadius * Math.cos(angle),
        y1: 50 + innerRadius * Math.sin(angle),
        x2: 50 + outerRadius * Math.cos(angle),
        y2: 50 + outerRadius * Math.sin(angle),
        angle,
        radius: outerRadius // Add radius property to fix linter error
      };
    });
  };
  
  const connections = generateConnections();
  
  return (
    <div className="absolute inset-0 pointer-events-none">
      {connections.map((conn, i) => (
        <motion.div
          key={i}
          className="absolute top-1/2 left-1/2 origin-center h-[1px]"
          style={{
            width: `${conn.radius}%`,
            rotate: `${conn.angle}rad`,
            background: 'linear-gradient(90deg, rgba(255,140,42,0.8) 0%, rgba(255,140,42,0.1) 100%)',
            transformOrigin: 'left center',
          }}
          initial={{ opacity: 0, scaleX: 0 }}
          animate={{ 
            opacity: [0, 0.8, 0],
            scaleX: [0, 1, 0],
          }}
          transition={{
            duration: 2 + (i % 3),
            delay: i * 0.7,
            repeat: Infinity,
            repeatType: "loop",
            repeatDelay: Math.random() * 2 + 1
          }}
        />
      ))}
      
      {/* Pulse rings emanating outward */}
      {[1, 2, 3].map((_, i) => (
        <motion.div
          key={i}
          className="absolute top-1/2 left-1/2 rounded-full border border-[#FF8C2A]/30"
          style={{
            width: 20,
            height: 20,
            x: -10,
            y: -10,
          }}
          initial={{ scale: 0, opacity: 0.5 }}
          animate={{ 
            scale: 6,
            opacity: 0,
          }}
          transition={{
            duration: 3,
            delay: i * 1.5,
            repeat: Infinity,
            ease: "easeOut"
          }}
        />
      ))}
    </div>
  );
};

// Particles floating around the logo
const NetworkParticles = () => {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {[...Array(15)].map((_, i) => {
        const size = Math.random() * 3 + 1;
        const angle = Math.random() * Math.PI * 2;
        const distance = 20 + Math.random() * 25;
        const speed = 10 + Math.random() * 20;
        const delay = Math.random() * 5;
        
        const x = 50 + distance * Math.cos(angle);
        const y = 50 + distance * Math.sin(angle);
        
        return (
          <motion.div
            key={i}
            className="absolute rounded-full bg-[#FF8C2A]/60"
            style={{
              width: size,
              height: size,
              x: `${x}%`,
              y: `${y}%`,
              translateX: '-50%',
              translateY: '-50%',
            }}
            animate={{
              x: [
                `${x}%`, 
                `${50 + (distance - 5) * Math.cos(angle + 0.5)}%`,
                `${50 + distance * Math.cos(angle + 1)}%`,
                `${x}%`
              ],
              y: [
                `${y}%`, 
                `${50 + (distance - 5) * Math.sin(angle + 0.5)}%`,
                `${50 + distance * Math.sin(angle + 1)}%`,
                `${y}%`
              ],
              opacity: [0.2, 0.8, 0.2],
            }}
            transition={{
              duration: speed,
              delay: delay,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        );
      })}
    </div>
  );
};

function PlatformIconsComponent() {
  const [activeIcon, setActiveIcon] = useState<string | null>(null);

  return (
    <div className="relative w-full h-full min-h-[450px] flex items-center justify-center">
      {/* Background container */}
      <div className="absolute w-[95%] h-[95%] bg-white/5 rounded-3xl backdrop-blur-sm border border-white/10"></div>

      {/* Main content area */}
      <div className="relative w-[340px] h-[340px] md:w-[420px] md:h-[420px]">
        {/* Background glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#FF8C2A]/10 via-transparent to-[#FF8C2A]/5 rounded-full filter blur-xl"></div>
        
        {/* Animated pulse around center */}
        <motion.div
          className="absolute inset-0 bg-[#FF8C2A]/5 rounded-full"
          animate={{
            scale: [1, 1.05, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        {/* Network particles */}
        <NetworkParticles />
        
        {/* Center rays */}
        <CenterRays />

        {/* Visual Orbital Rings */}
        <OrbitalRings />

        {/* Central Logo */}
        <motion.div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 md:w-40 md:h-40 rounded-full bg-white/90 backdrop-blur-md shadow-[0_0_30px_rgba(255,140,42,0.4)] flex items-center justify-center z-30 border-[3px] border-white"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ 
            scale: 1, 
            rotate: 0,
            boxShadow: ['0 0 30px rgba(255,140,42,0.4)', '0 0 50px rgba(255,140,42,0.6)', '0 0 30px rgba(255,140,42,0.4)']
          }}
          transition={{ 
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.1,
            boxShadow: {
              duration: 3,
              repeat: Infinity,
              repeatType: "reverse"
            }
          }}
        >
          {/* Connection lines effect */}
          <ConnectionLines />
          
          {/* Inner gradient ring */}
          <motion.div
            className="absolute inset-1 rounded-full opacity-50"
            style={{
              background: 'linear-gradient(135deg, rgba(255,140,42,0.2) 0%, rgba(255,140,42,0) 50%, rgba(255,140,42,0.2) 100%)'
            }}
            animate={{ rotate: 360 }}
            transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Main orange circle */}
          <motion.div 
            className="w-28 h-28 md:w-36 md:h-36 rounded-full bg-gradient-to-br from-[#FF8C2A] to-[#e67e25] flex items-center justify-center shadow-inner relative"
            initial={{ opacity: 0 }}
            animate={{ 
              opacity: 1,
              background: [
                'linear-gradient(135deg, #FF8C2A, #e67e25)',
                'linear-gradient(135deg, #FF9F45, #e67e25)',
                'linear-gradient(135deg, #FF8C2A, #e67e25)'
              ]
            }}
            transition={{ 
              delay: 0.5, 
              duration: 0.5,
              background: {
                duration: 3,
                repeat: Infinity,
                repeatType: "reverse"
              }
            }}
          >
            {/* Network connection dots */}
            <div className="absolute inset-0">
              {[...Array(5)].map((_, i) => {
                const angle = (i * (360 / 5) * Math.PI) / 180;
                const r = 40; // % of circle radius
                return (
                  <motion.div
                    key={i}
                    className="absolute h-1.5 w-1.5 bg-white rounded-full"
                    style={{
                      top: `${50 + r * Math.sin(angle)}%`,
                      left: `${50 + r * Math.cos(angle)}%`,
                      transform: 'translate(-50%, -50%)',
                    }}
                    animate={{
                      opacity: [0.3, 0.9, 0.3],
                      scale: [0.8, 1, 0.8],
                    }}
                    transition={{
                      duration: 1.5,
                      delay: i * 0.3,
                      repeat: Infinity,
                      repeatType: "reverse"
                    }}
                  />
                );
              })}
            </div>
            
            {/* Highlight overlay */}
            <div className="absolute inset-0 rounded-full overflow-hidden">
              <div className="absolute top-0 right-0 left-0 h-[40%] bg-white/10 blur-sm" />
            </div>
            
            {/* Letter L */}
            <motion.div 
              className="absolute inset-0 flex items-center justify-center"
              animate={{ 
                scale: [1, 1.02, 1]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse"
              }}
            >
              <motion.span 
                className="text-6xl md:text-7xl font-bold text-white tracking-tight z-10"
                style={{ fontFamily: 'system-ui, sans-serif' }}
                animate={{ 
                  textShadow: ['0 0 0px rgba(255,255,255,0.3)', '0 0 15px rgba(255,255,255,0.6)', '0 0 0px rgba(255,255,255,0.3)']
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  repeatType: "reverse"
                }}
              >
                L
              </motion.span>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Single Orbit Container for all icons */}
        <motion.div
          className="absolute inset-0"
          animate={{ rotate: 360 }}
          transition={{
            duration: 50, // Adjust rotation speed as needed
            repeat: Infinity,
            ease: "linear"
          }}
        >
          <AnimatePresence>
            {platformConfig.map((platform, index) => (
                <PlatformIcon
                  key={platform.name}
                  platform={platform}
                  index={index} 
                  activeIcon={activeIcon}
                  setActiveIcon={setActiveIcon}
                />
            ))}
          </AnimatePresence>
        </motion.div>

        {/* Decorative dots */}
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(18)].map((_, i) => (
            <DecorativeDot key={i} index={i} />
          ))}
        </div>
      </div>

      {/* External Labels - Positioned outside the main container */}
      <motion.div
        className="absolute top-[15%] right-[10%] md:right-[15%] z-40"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.5 }}
      >
        <div className="bg-white rounded-full px-4 py-1.5 shadow-lg flex items-center space-x-1">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <span className="text-sm font-medium text-red-600">YouTube</span>
        </div>
      </motion.div>

      <motion.div
        className="absolute bottom-[15%] right-[10%] md:right-[15%] z-40"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.4, duration: 0.5 }}
      >
        <div className="bg-white rounded-full px-4 py-1.5 shadow-lg flex items-center space-x-1">
          <span className="text-sm font-medium text-blue-600">G</span>
          <span className="text-sm font-medium text-red-500">o</span>
          <span className="text-sm font-medium text-yellow-500">o</span>
          <span className="text-sm font-medium text-blue-600">g</span>
          <span className="text-sm font-medium text-green-600">l</span>
          <span className="text-sm font-medium text-red-500">e</span>
          <span className="text-xs ml-1 text-gray-700">Ads</span>
        </div>
      </motion.div>
    </div>
  )
}

// Memoized component showing users managing social accounts
function SocialNetworkUsersComponent() {
  const [activeUser, setActiveUser] = useState<number | null>(null);
  
  // User profile configurations
  const userProfiles = [
    { color: "#FF8C2A", position: { top: "20%", left: "15%" } },
    { color: "#1877F2", position: { top: "25%", left: "75%" } },
    { color: "#E60023", position: { top: "65%", left: "80%" } },
    { color: "#1DA1F2", position: { top: "70%", left: "25%" } },
    { color: "#0A66C2", position: { top: "45%", left: "90%" } },
    { color: "#5865F2", position: { top: "10%", left: "45%" } },
  ];

  return (
    <div className="relative w-full h-full min-h-[400px] flex items-center justify-center">
      {/* Light background container with rounded corners */}
      <div className="absolute w-[95%] h-[95%] bg-white/5 rounded-3xl backdrop-blur-sm border border-white/10"></div>
      
      <div className="relative w-[340px] h-[340px] md:w-[420px] md:h-[420px]">
        {/* Background glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#FF8C2A]/10 via-transparent to-[#FF8C2A]/5 rounded-full filter blur-xl"></div>
        
        {/* Connection network lines */}
        <div className="absolute inset-0">
          {userProfiles.map((user, i) => (
            userProfiles.slice(i + 1).map((targetUser, j) => (
              <motion.div
                key={`${i}-${j}`}
                className="absolute top-0 left-0 h-0.5 bg-gradient-to-r from-[#FF8C2A]/40 to-[#FF8C2A]/10 z-0"
                style={{
                  width: '100%',
                  top: `calc(${user.position.top} - 10px)`,
                  left: `calc(${user.position.left} - 10px)`,
                  transformOrigin: '0 0',
                  rotate: `${Math.atan2(
                    parseFloat(targetUser.position.top) - parseFloat(user.position.top),
                    parseFloat(targetUser.position.left) - parseFloat(user.position.left)
                  )}rad`,
                  scale: Math.sqrt(
                    Math.pow(parseFloat(targetUser.position.top) - parseFloat(user.position.top), 2) +
                    Math.pow(parseFloat(targetUser.position.left) - parseFloat(user.position.left), 2)
                  ) / 100,
                }}
                initial={{ opacity: 0 }}
                animate={{ 
                  opacity: [0.1, 0.5, 0.1],
                  scaleX: [0.8, 1, 0.8],
                }}
                transition={{
                  duration: 3 + Math.random() * 2,
                  delay: i * 0.3,
                  repeat: Infinity,
                  repeatType: "reverse"
                }}
              />
            ))
          ))}
        </div>

        {/* Data packets traveling on the network */}
        <div className="absolute inset-0">
          {userProfiles.map((user, i) => (
            userProfiles.slice(i + 1).filter((_, idx) => (i + idx) % 2 === 0).map((targetUser, j) => (
              <motion.div
                key={`packet-${i}-${j}`}
                className="absolute h-2 w-2 rounded-full bg-white shadow-[0_0_10px_rgba(255,255,255,0.7)] z-10"
                style={{
                  top: `calc(${user.position.top} - 4px)`,
                  left: `calc(${user.position.left} - 4px)`,
                }}
                animate={{
                  top: [`calc(${user.position.top} - 4px)`, `calc(${targetUser.position.top} - 4px)`],
                  left: [`calc(${user.position.left} - 4px)`, `calc(${targetUser.position.left} - 4px)`],
                  scale: [0.8, 1.2, 0.8],
                }}
                transition={{
                  duration: 2 + Math.random() * 2,
                  delay: i * 0.5,
                  repeat: Infinity,
                  repeatType: "mirror",
                  ease: "easeInOut"
                }}
              />
            ))
          ))}
        </div>
        
        {/* User profile circles with phone illustrations */}
        {userProfiles.map((user, index) => (
          <motion.div
            key={`user-${index}`}
            className="absolute"
            style={{
              top: user.position.top,
              left: user.position.left,
              zIndex: activeUser === index ? 30 : 20,
            }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ 
              delay: index * 0.15,
              type: "spring",
              stiffness: 260,
              damping: 20
            }}
            whileHover={{ 
              scale: 1.15,
              zIndex: 30,
              filter: "drop-shadow(0 0 12px rgba(255,140,42,0.5))"
            }}
            onHoverStart={() => setActiveUser(index)}
            onHoverEnd={() => setActiveUser(null)}
          >
            {/* Phone device frame */}
            <motion.div 
              className="relative flex flex-col items-center"
              animate={{ 
                y: [0, -3, 0],
                rotate: [0, index % 2 === 0 ? 3 : -3, 0]
              }}
              transition={{
                duration: 3 + (index % 3),
                repeat: Infinity,
                repeatType: "reverse",
                ease: "easeInOut"
              }}
            >
              {/* Phone device */}
              <div className="relative w-14 h-20 md:w-16 md:h-24 bg-gray-900 rounded-xl overflow-hidden border-[2px] border-gray-700 shadow-xl flex flex-col">
                {/* Phone screen with social icons */}
                <div className={`flex-1 bg-gradient-to-br from-${user.color}/80 to-${user.color}/50 p-1 flex flex-wrap content-start gap-1 justify-center`}>
                  {/* Miniature social icons on phone screen */}
                  <motion.div className="w-2 h-2 rounded-full bg-blue-500" 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                  <motion.div className="w-2 h-2 rounded-full bg-pink-500" 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.8, delay: 0.2, repeat: Infinity }}
                  />
                  <motion.div className="w-2 h-2 rounded-full bg-green-500" 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.2, delay: 0.4, repeat: Infinity }}
                  />
                  <motion.div className="w-2 h-2 rounded-full bg-yellow-500" 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.7, delay: 0.3, repeat: Infinity }}
                  />
                </div>
                
                {/* Phone home button */}
                <div className="h-2 flex justify-center items-center">
                  <div className="w-2 h-2 rounded-full bg-gray-700"></div>
                </div>
              </div>
              
              {/* Person avatar below the phone */}
              <motion.div 
                className={`w-8 h-8 rounded-full bg-white mt-1 border-2 border-${user.color} shadow-lg overflow-hidden`}
                animate={{ 
                  boxShadow: ['0 0 0px rgba(255,255,255,0)', '0 0 10px rgba(255,140,42,0.4)', '0 0 0px rgba(255,255,255,0)']
                }}
                transition={{ 
                  duration: 2,
                  delay: index * 0.2,
                  repeat: Infinity
                }}
              >
                <div className="w-full h-3/5 bg-gray-200"></div>
                <div className="w-full h-2/5 bg-blue-500"></div>
              </motion.div>
              
              {/* Chat bubble */}
              {activeUser === index && (
                <motion.div 
                  className="absolute top-0 right-0 transform translate-x-[80%] -translate-y-[30%]"
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0 }}
                >
                  <div className="relative bg-white rounded-lg p-2 shadow-lg">
                    <div className="absolute w-3 h-3 bg-white transform rotate-45 -left-1 top-1/2 -translate-y-1/2"></div>
                    <div className="flex gap-1 items-center">
                      {[...Array(3)].map((_, i) => (
                        <motion.div 
                          key={i} 
                          className={`w-3 h-3 rounded-full`} 
                          style={{ 
                            backgroundColor: i === 0 ? '#1877F2' : i === 1 ? '#E60023' : '#1DA1F2'
                          }}
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ 
                            duration: 0.5, 
                            delay: i * 0.2, 
                            repeat: Infinity,
                            repeatType: "reverse" 
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        ))}
        
        {/* Center hub element */}
        <motion.div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 rounded-full bg-white/90 backdrop-blur-md shadow-[0_0_30px_rgba(255,140,42,0.4)] flex items-center justify-center z-20 border-[3px] border-white"
          initial={{ scale: 0 }}
          animate={{ 
            scale: 1,
            boxShadow: ['0 0 30px rgba(255,140,42,0.4)', '0 0 50px rgba(255,140,42,0.6)', '0 0 30px rgba(255,140,42,0.4)']
          }}
          transition={{ 
            type: "spring",
            stiffness: 260,
            damping: 20,
            delay: 0.3,
            boxShadow: {
              duration: 3,
              repeat: Infinity,
              repeatType: "reverse"
            }
          }}
        >
          <motion.div 
            className="w-20 h-20 rounded-full bg-gradient-to-br from-[#FF8C2A] to-[#e67e25] flex items-center justify-center shadow-inner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
          >
            {/* Network icon */}
            <motion.svg 
              width="32" 
              height="32" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
              animate={{ 
                scale: [1, 1.1, 1],
                opacity: [0.9, 1, 0.9]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                repeatType: "reverse"
              }}
            >
              <path d="M17 6.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm-6 5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm-6 5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm12 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z" 
                fill="white" />
              <path d="M16.4 8.56a1 1 0 0 1-.13 1.4.984.984 0 0 1-1.4-.12l-3.46-4.13a1 1 0 0 1 .12-1.4 1 1 0 0 1 1.41.12l3.46 4.13zm-7.93 1.87a1 1 0 0 1-.13 1.4.984.984 0 0 1-1.4-.12L3.56 7.56a1 1 0 0 1 .12-1.4 1 1 0 0 1 1.41.12l3.38 4.15zm8.6 2.54a1 1 0 0 1 1.39.15l3.3 4.1a1 1 0 1 1-1.54 1.28l-3.3-4.1a1 1 0 0 1 .15-1.43z"
                fill="white" />
            </motion.svg>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

// Export memoized component
export const SocialNetworkUsers = memo(SocialNetworkUsersComponent)

// Export memoized component
export const PlatformIcons = memo(PlatformIconsComponent)

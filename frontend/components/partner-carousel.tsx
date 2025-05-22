"use client"

import * as React from "react"
import Image from "next/image"
import { motion } from "framer-motion"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface Partner {
  id: number
  name: string
  logo: string
  description: string
}

interface PartnerCarouselProps {
  partners: Partner[]
}

export function PartnerCarousel({ partners }: PartnerCarouselProps) {
  const [activeIndex, setActiveIndex] = React.useState(0)
  const [dragging, setDragging] = React.useState(false)
  const [dragStartX, setDragStartX] = React.useState(0)
  const [dragOffset, setDragOffset] = React.useState(0)
  const [imageLoaded, setImageLoaded] = React.useState<{[key: number]: boolean}>({})
  
  // Calculate visible partners based on screen size
  const [visiblePartners, setVisiblePartners] = React.useState(4)
  
  React.useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 640) {
        setVisiblePartners(1)
      } else if (window.innerWidth < 768) {
        setVisiblePartners(2)
      } else if (window.innerWidth < 1024) {
        setVisiblePartners(3)
      } else {
        setVisiblePartners(4)
      }
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  
  // Auto-advance carousel
  React.useEffect(() => {
    const interval = setInterval(() => {
      if (!dragging) {
        handleNext()
      }
    }, 3000)
    
    return () => clearInterval(interval)
  }, [activeIndex, dragging])
  
  const handleNext = () => {
    setActiveIndex((prev) => (prev + 1) % Math.max(1, partners.length - visiblePartners + 1))
  }
  
  const handlePrev = () => {
    setActiveIndex((prev) => (prev - 1 + Math.max(1, partners.length - visiblePartners + 1)) % Math.max(1, partners.length - visiblePartners + 1))
  }
  
  const handleDragStart = (e: React.MouseEvent | React.TouchEvent) => {
    setDragging(true)
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
    setDragStartX(clientX)
  }
  
  const handleDragMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!dragging) return
    
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
    const delta = clientX - dragStartX
    setDragOffset(delta)
  }
  
  const handleDragEnd = () => {
    if (dragOffset > 50) {
      handlePrev()
    } else if (dragOffset < -50) {
      handleNext()
    }
    
    setDragging(false)
    setDragOffset(0)
  }

  const handleImageLoad = (id: number) => {
    setImageLoaded(prev => ({...prev, [id]: true}))
  }
  
  return (
    <div className="relative w-full overflow-hidden">
      <div 
        className="flex"
        style={{ 
          transform: `translateX(calc(-${activeIndex * 100 / visiblePartners}% + ${dragOffset}px))`,
          transition: dragging ? 'none' : 'transform 0.5s ease-in-out'
        }}
        onMouseDown={handleDragStart}
        onMouseMove={handleDragMove}
        onMouseUp={handleDragEnd}
        onMouseLeave={handleDragEnd}
        onTouchStart={handleDragStart}
        onTouchMove={handleDragMove}
        onTouchEnd={handleDragEnd}
      >
        {partners.map((partner) => (
          <motion.div
            key={partner.id}
            className={`flex-none px-2 w-full sm:w-1/${Math.min(visiblePartners, 2)} md:w-1/${Math.min(visiblePartners, 3)} lg:w-1/${Math.min(visiblePartners, 4)}`}
            whileHover={{ scale: 1.05 }}
          >
            <div className="bg-background rounded-2xl p-6 shadow-2xl transition-all border border-gray-100 dark:border-gray-800 flex flex-col items-center text-center h-full">
              <div className="mb-6 mx-auto h-20 w-20 relative flex items-center justify-center">
                <motion.div 
                  className="absolute inset-0 rounded-full bg-gradient-to-r from-[#FF8C2A]/10 to-blue-500/10"
                  animate={{ 
                    scale: [1, 1.1, 1],
                    opacity: [0.7, 1, 0.7],
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
                
                <Image
                  src={partner.logo}
                  alt={partner.name + ' logo'}
                  width={80}
                  height={40}
                  className="max-h-16 max-w-[80px] object-contain relative z-10"
                  onError={(e) => {
                    // Fallback to placeholder if image fails to load
                    const imgElement = e.currentTarget as HTMLImageElement;
                    imgElement.src = `https://placehold.co/200x80/FF8C2A/FFFFFF?text=${partner.name}`;
                  }}
                />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">{partner.name}</h3>
              <p className="text-muted-foreground text-center text-sm">{partner.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
      
      <button 
        onClick={handlePrev}
        className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white text-[#FF8C2A] p-2 rounded-full shadow-md hidden sm:flex items-center justify-center"
        aria-label="Previous slide"
      >
        <ChevronLeft className="h-6 w-6" />
      </button>
      
      <button 
        onClick={handleNext}
        className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white text-[#FF8C2A] p-2 rounded-full shadow-md hidden sm:flex items-center justify-center"
        aria-label="Next slide"
      >
        <ChevronRight className="h-6 w-6" />
      </button>
      
      <div className="mt-4 flex justify-center gap-2">
        {Array.from({ length: Math.max(1, partners.length - visiblePartners + 1) }).map((_, i) => (
          <motion.button
            key={i}
            className={`h-2 w-2 rounded-full ${i === activeIndex ? 'bg-[#FF8C2A]' : 'bg-gray-300'}`}
            onClick={() => setActiveIndex(i)}
            animate={i === activeIndex ? { 
              scale: [1, 1.5, 1], 
              opacity: [0.5, 1, 0.5] 
            } : {}}
            transition={{ duration: 2, repeat: Infinity }}
          />
        ))}
      </div>
    </div>
  )
} 
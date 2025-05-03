"use client"

import { useState, useEffect } from "react"

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Function to check if screen is mobile width
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768) // 768px is standard md breakpoint
    }

    // Set initial value
    checkIsMobile()

    // Add event listener for window resize
    window.addEventListener("resize", checkIsMobile)

    // Clean up event listener on component unmount
    return () => window.removeEventListener("resize", checkIsMobile)
  }, [])

  return isMobile
}

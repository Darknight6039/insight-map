'use client'

import { motion } from 'framer-motion'

interface AxialLogoProps {
  size?: number
  className?: string
}

export default function AxialLogo({ size = 40, className = "" }: AxialLogoProps) {
  return (
    <motion.div
      className={`flex items-center gap-3 ${className}`}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.2 }}
    >
      <div className="relative">
        <svg 
          width={size} 
          height={size} 
          viewBox="0 0 256 256" 
          className="drop-shadow-lg"
        >
          <defs>
            <linearGradient id="axial-gradient" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#003366"/>
              <stop offset="50%" stopColor="#0055AA"/>
              <stop offset="100%" stopColor="#00d4aa"/>
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#00d4aa" floodOpacity="0.3"/>
            </filter>
          </defs>
          
          {/* Forme principale "A" stylisée */}
          <path
            d="M128 32 L64 200 L96 200 L108 168 L148 168 L160 200 L192 200 L128 32 Z M118 140 L138 140 L128 112 Z"
            fill="url(#axial-gradient)"
            filter="url(#glow)"
          />
          
          {/* Accent décoratif */}
          <circle
            cx="128"
            cy="220"
            r="8"
            fill="#00d4aa"
            opacity="0.8"
          />
        </svg>
      </div>
      
      <div className="flex flex-col">
        <motion.span 
          className="text-xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          AXIAL
        </motion.span>
        <motion.span 
          className="text-xs text-axial-accent font-medium tracking-wider"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          INTELLIGENCE
        </motion.span>
      </div>
    </motion.div>
  )
}

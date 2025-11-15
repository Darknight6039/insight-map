'use client'

import { motion } from 'framer-motion'

interface ProgressBarProps {
  progress: number
  message: string
  isVisible: boolean
}

export default function ProgressBar({ progress, message, isVisible }: ProgressBarProps) {
  if (!isVisible) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="fixed bottom-8 right-8 bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 shadow-xl border border-gray-700 min-w-[320px] z-50"
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-200">{message}</span>
          <span className="text-sm text-gray-400">{progress}%</span>
        </div>
        
        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
            className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
          />
        </div>
      </div>
    </motion.div>
  )
}


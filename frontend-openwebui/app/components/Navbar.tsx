'use client'

import { motion } from 'framer-motion'
import AxialLogo from './AxialLogo'

export default function Navbar() {
  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="navbar-glass z-50"
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <AxialLogo size={36} />
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 px-4 py-2 glass rounded-xl">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-300">Système opérationnel</span>
        </div>
      </div>
    </motion.nav>
  )
}

'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Menu, X, Settings, Bell, User, Sparkles } from 'lucide-react'
import AxialLogo from './AxialLogo'

interface NavbarProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  selectedBusiness: string
  setSelectedBusiness: (business: string) => void
  businessTypes: Array<{ id: string; name: string; color: string }>
}

export default function Navbar({ 
  sidebarOpen, 
  setSidebarOpen, 
  selectedBusiness, 
  setSelectedBusiness, 
  businessTypes 
}: NavbarProps) {
  const [notificationCount] = useState(3)

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="navbar-glass z-50"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left section */}
        <div className="flex items-center gap-6">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <motion.button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 rounded-xl glass hover:bg-white/20 transition-colors lg:hidden"
            >
              {sidebarOpen ? (
                <X className="w-5 h-5 text-white" />
              ) : (
                <Menu className="w-5 h-5 text-white" />
              )}
            </motion.button>
            
            <AxialLogo size={36} />
          </div>

          {/* Business type selector - Desktop */}
          <div className="hidden lg:flex items-center gap-3">
            <span className="text-sm text-gray-400">Secteur:</span>
            <div className="flex gap-2">
              {businessTypes.map((business) => (
                <motion.button
                  key={business.id}
                  onClick={() => setSelectedBusiness(business.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                    selectedBusiness === business.id
                      ? 'bg-axial-accent text-white'
                      : 'glass text-gray-300 hover:bg-white/20'
                  }`}
                >
                  {business.name.replace(/^\p{Emoji}/u, '').trim()}
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-4">
          {/* Status indicator */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 glass rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-300">Système opérationnel</span>
          </div>

          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="relative p-2 glass rounded-xl hover:bg-white/20 transition-colors"
          >
            <Bell className="w-5 h-5 text-white" />
            {notificationCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center"
              >
                {notificationCount}
              </motion.span>
            )}
          </motion.button>

          {/* Settings */}
          <motion.button
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            className="p-2 glass rounded-xl hover:bg-white/20 transition-all duration-300"
          >
            <Settings className="w-5 h-5 text-white" />
          </motion.button>

          {/* User profile */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-3 p-2 glass rounded-xl hover:bg-white/20 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-sm font-medium text-white">Utilisateur</p>
              <p className="text-xs text-gray-400">Analyste Senior</p>
            </div>
          </motion.button>
        </div>
      </div>

      {/* Mobile business selector */}
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ 
          height: sidebarOpen ? 'auto' : 0, 
          opacity: sidebarOpen ? 1 : 0 
        }}
        className="lg:hidden overflow-hidden border-t border-white/10 mt-4 pt-4"
      >
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-gray-400 w-full mb-2">Secteur d'activité:</span>
          {businessTypes.map((business) => (
            <motion.button
              key={business.id}
              onClick={() => setSelectedBusiness(business.id)}
              whileTap={{ scale: 0.95 }}
              className={`px-3 py-2 text-sm rounded-lg transition-all ${
                selectedBusiness === business.id
                  ? 'bg-axial-accent text-white'
                  : 'glass text-gray-300'
              }`}
            >
              {business.name}
            </motion.button>
          ))}
        </div>
      </motion.div>
    </motion.nav>
  )
}

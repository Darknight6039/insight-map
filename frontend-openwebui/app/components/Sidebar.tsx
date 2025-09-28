'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, Brain, BarChart3, FileText, Settings, X, Home } from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  activeTab: string
  setActiveTab: (tab: string) => void
}

const menuItems = [
  { id: 'chat', name: 'Chat Expert', icon: MessageCircle, description: 'Assistance IA personnalisée' },
  { id: 'analysis', name: 'Analyses', icon: Brain, description: 'Outils d\'analyse stratégique' },
  { id: 'dashboard', name: 'Dashboard', icon: BarChart3, description: 'Métriques et aperçu' },
  { id: 'documents', name: 'Documents', icon: FileText, description: 'Gestion des fichiers PDF' },
]

export default function Sidebar({ isOpen, onClose, activeTab, setActiveTab }: SidebarProps) {
  return (
    <>
      {/* Static sidebar on large screens */}
      <div className="hidden lg:block">
        <div className="sidebar-liquid open z-40">
          {/* Header (no close button on desktop) */}
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-xl font-bold text-white">Navigation</h2>
          </div>

          {/* Menu Items */}
          <nav className="space-y-2">
            {menuItems.map((item, index) => {
              const Icon = item.icon
              const isActive = activeTab === item.id
              return (
                <motion.button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full p-4 rounded-xl text-left transition-all duration-300 ${
                    isActive 
                      ? 'bg-gradient-to-r from-axial-blue to-axial-accent text-white shadow-lg'
                      : 'glass hover:bg-white/20 text-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${isActive ? 'bg-white/20' : 'bg-white/10'}` }>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium">{item.name}</h3>
                      <p className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-400'}` }>
                        {item.description}
                      </p>
                    </div>
                    {isActive && (
                      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="w-2 h-2 bg-white rounded-full" />
                    )}
                  </div>
                </motion.button>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="absolute bottom-6 left-6 right-6">
            <div className="glass p-4 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center">
                  <Home className="w-4 h-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Insight MVP</p>
                  <p className="text-xs text-gray-400">v1.0.0</p>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Statut système</span>
                <div className="flex items-center gap-1">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                  <span>Opérationnel</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile/Tablet overlay sidebar */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
            />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 120 }}
              className="sidebar-liquid open z-50 lg:hidden"
            >
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-xl font-bold text-white">Navigation</h2>
                <motion.button
                  onClick={onClose}
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 glass rounded-xl hover:bg-white/20 transition-all"
                >
                  <X className="w-5 h-5 text-white" />
                </motion.button>
              </div>
              <nav className="space-y-2">
                {menuItems.map((item, index) => {
                  const Icon = item.icon
                  const isActive = activeTab === item.id
                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => { setActiveTab(item.id); onClose(); }}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      whileHover={{ scale: 1.02, x: 5 }}
                      whileTap={{ scale: 0.98 }}
                      className={`w-full p-4 rounded-xl text-left transition-all duration-300 ${
                        isActive ? 'bg-gradient-to-r from-axial-blue to-axial-accent text-white shadow-lg' : 'glass hover:bg-white/20 text-gray-300'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-lg ${isActive ? 'bg-white/20' : 'bg-white/10'}` }>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium">{item.name}</h3>
                          <p className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-400'}` }>
                            {item.description}
                          </p>
                        </div>
                        {isActive && (<motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="w-2 h-2 bg-white rounded-full" />)}
                      </div>
                    </motion.button>
                  )
                })}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

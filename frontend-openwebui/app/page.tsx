'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageCircle, 
  Brain, 
  FileText, 
  TrendingUp, 
  Shield, 
  Search,
  Sparkles,
  Download,
  Settings,
  Menu,
  X
} from 'lucide-react'
import AnalysisPanel from './components/AnalysisPanel'
import ChatInterface from './components/ChatInterface'
import Dashboard from './components/Dashboard'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import AxialLogo from './components/AxialLogo'
import Link from 'next/link'

const analysisTypes = [
  {
    id: 'synthese_executive',
    name: 'Synthèse Exécutive',
    description: 'Vue d\'ensemble stratégique et recommandations',
    icon: Brain,
    color: 'from-blue-500 to-cyan-500',
    business: ['finance_banque', 'tech_digital', 'retail_commerce']
  },
  {
    id: 'analyse_concurrentielle', 
    name: 'Analyse Concurrentielle',
    description: 'Mapping concurrentiel et positionnement',
    icon: TrendingUp,
    color: 'from-purple-500 to-pink-500',
    business: ['finance_banque', 'tech_digital', 'retail_commerce']
  },
  {
    id: 'veille_technologique',
    name: 'Veille Technologique', 
    description: 'Innovations et tendances tech',
    icon: Sparkles,
    color: 'from-green-500 to-teal-500',
    business: ['tech_digital', 'finance_banque']
  },
  {
    id: 'analyse_risques',
    name: 'Analyse des Risques',
    description: 'Cartographie et mitigation des risques',
    icon: Shield,
    color: 'from-red-500 to-orange-500',
    business: ['finance_banque', 'tech_digital', 'retail_commerce']
  },
  {
    id: 'etude_marche',
    name: 'Étude de Marché',
    description: 'Analyse marché et opportunités',
    icon: FileText,
    color: 'from-yellow-500 to-amber-500',
    business: ['retail_commerce', 'finance_banque', 'tech_digital']
  }
]

const businessTypes = [
  { id: 'finance_banque', name: '🏦 Finance & Banque', color: 'text-blue-400' },
  { id: 'tech_digital', name: '💻 Tech & Digital', color: 'text-purple-400' },
  { id: 'retail_commerce', name: '🛍️ Retail & Commerce', color: 'text-green-400' }
]

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('chat')
  const [selectedBusiness, setSelectedBusiness] = useState('finance_banque')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen w-full">
      <Navbar 
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        selectedBusiness={selectedBusiness}
        setSelectedBusiness={setSelectedBusiness}
        businessTypes={businessTypes}
      />
      
      {/* Always render sidebar container so desktop version is visible */}
      <Sidebar 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="pt-20 px-4 pb-6 w-full">
        <div className="w-full max-w-none">
          {/* Header avec effet glass */}
          <motion.div
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="glass-card mb-8 text-center"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="mb-4"
            >
              <AxialLogo size={80} className="justify-center" />
            </motion.div>
            <motion.p 
              className="text-xl text-gray-300 max-w-2xl mx-auto"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              Intelligence stratégique propulsée par l'IA avec design liquid glass immersif
            </motion.p>
            
            {/* Business type selector */}
            <motion.div 
              className="flex flex-wrap justify-center gap-4 mt-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {businessTypes.map((business) => (
                <button
                  key={business.id}
                  onClick={() => setSelectedBusiness(business.id)}
                  className={`glass-button ${business.color} ${
                    selectedBusiness === business.id 
                      ? 'ring-2 ring-axial-accent bg-white/20' 
                      : ''
                  }`}
                >
                  {business.name}
                </button>
              ))}
            </motion.div>
          </motion.div>

          {/* Main content area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:pl-80">
            {/* Main Interface - 2/3 width on large screens */}
            <div className="lg:col-span-2">
              <AnimatePresence mode="wait">
                {activeTab === 'chat' && (
                  <motion.div
                    key="chat-inline"
                    initial={{ x: -300, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -300, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ChatInterface selectedBusiness={selectedBusiness} />
                  </motion.div>
                )}
                
                {activeTab === 'analysis' && (
                  <motion.div
                    key="analysis"
                    initial={{ x: -300, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -300, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <AnalysisPanel 
                      analysisTypes={analysisTypes}
                      selectedBusiness={selectedBusiness}
                    />
                  </motion.div>
                )}

                {activeTab === 'dashboard' && (
                  <motion.div
                    key="dashboard"
                    initial={{ x: -300, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -300, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Dashboard />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Side panel - 1/3 width */}
            <div className="space-y-6">
              {/* Quick actions */}
              <motion.div
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="glass-card"
              >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-axial-accent" />
                  Actions Rapides
                </h3>
                <div className="space-y-3">
                  {analysisTypes
                    .filter(type => type.business.includes(selectedBusiness))
                    .slice(0, 3)
                    .map((analysis) => {
                      const Icon = analysis.icon
                      return (
                        <motion.button
                          key={analysis.id}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="w-full glass-button text-left p-4 glow-on-hover"
                          onClick={() => setActiveTab('analysis')}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg bg-gradient-to-r ${analysis.color}`}>
                              <Icon className="w-4 h-4 text-white" />
                            </div>
                            <div>
                              <div className="text-white font-medium text-sm">
                                {analysis.name}
                              </div>
                              <div className="text-gray-400 text-xs">
                                {analysis.description}
                              </div>
                            </div>
                          </div>
                        </motion.button>
                      )
                    })
                  }
                </div>
              </motion.div>

              {/* Recent activity */}
              <motion.div
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="glass-card"
              >
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-axial-accent" />
                  Activité Récente
                </h3>
                <div className="space-y-3">
                  {[
                    { type: 'Synthèse', time: '2 min', status: 'completed' },
                    { type: 'Analyse Concurrentielle', time: '5 min', status: 'completed' },
                    { type: 'Veille Tech', time: '15 min', status: 'processing' }
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ x: 20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.8 + index * 0.1 }}
                      className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                      <div>
                        <div className="text-white text-sm font-medium">{item.type}</div>
                        <div className="text-gray-400 text-xs">Il y a {item.time}</div>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${
                        item.status === 'completed' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'
                      }`} />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

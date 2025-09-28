'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import ChatInterface from '../components/ChatInterface'
import AxialLogo from '../components/AxialLogo'

const businessTypes = [
  { id: 'finance_banque', name: '🏦 Finance & Banque', color: 'text-blue-400' },
  { id: 'tech_digital', name: '💻 Tech & Digital', color: 'text-purple-400' },
  { id: 'retail_commerce', name: '🛍️ Retail & Commerce', color: 'text-green-400' }
]

export default function ChatPage() {
  const [selectedBusiness, setSelectedBusiness] = useState('finance_banque')

  return (
    <div className="min-h-screen w-full">
      {/* Header avec navigation de retour */}
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="navbar-glass"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Bouton retour */}
          <Link href="/" className="flex items-center gap-3 text-white hover:text-axial-accent transition-colors">
            <motion.div
              whileHover={{ scale: 1.1, x: -3 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 glass rounded-xl hover:bg-white/20 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </motion.div>
            <span className="hidden sm:block font-medium">Retour au Dashboard</span>
          </Link>

          {/* Logo central cliquable → retour au menu principal */}
          <Link href="/" className="block" aria-label="Retour au menu principal">
            <AxialLogo size={32} className="cursor-pointer" />
          </Link>

          {/* Sélecteur de secteur */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-400 hidden sm:block">Secteur:</span>
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
                  {business.name.replace(/^\S+\s+/, '').trim()}
                </motion.button>
              ))}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Contenu principal */}
      {/* Ajouter un padding-top suffisant pour la navbar fixe */}
      <main className="pt-24 md:pt-28 px-4 pb-6 w-full">
        <div className="w-full max-w-none">
          {/* Titre de page */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-6 flex-shrink-0"
          >
            <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent mb-2">
              Expert IA Spécialisé
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Assistance personnalisée en intelligence stratégique pour le secteur{' '}
              <span className="text-accent font-medium">
                {businessTypes.find(b => b.id === selectedBusiness)?.name.replace(/^\S+\s+/, '').trim()}
              </span>
            </p>
          </motion.div>

          {/* Interface de chat */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex-1 overflow-hidden"
          >
            <ChatInterface selectedBusiness={selectedBusiness} />
          </motion.div>
        </div>
      </main>
    </div>
  )
}

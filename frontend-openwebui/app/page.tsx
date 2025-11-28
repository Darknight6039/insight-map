'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  FileText, 
  TrendingUp, 
  Shield, 
  Sparkles
} from 'lucide-react'
import AnalysisPanel from './components/AnalysisPanel'
import Navbar from './components/Navbar'
import AxialLogo from './components/AxialLogo'
import ChatWidget from './components/ChatWidget'

const analysisTypes = [
  {
    id: 'synthese_executive',
    name: 'Synthèse Exécutive',
    description: 'Vue d\'ensemble stratégique et recommandations',
    icon: Brain,
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'analyse_concurrentielle', 
    name: 'Analyse Concurrentielle',
    description: 'Mapping concurrentiel et positionnement',
    icon: TrendingUp,
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'veille_technologique',
    name: 'Veille Technologique', 
    description: 'Innovations et tendances tech',
    icon: Sparkles,
    color: 'from-green-500 to-teal-500'
  },
  {
    id: 'analyse_risques',
    name: 'Analyse des Risques',
    description: 'Cartographie et mitigation des risques',
    icon: Shield,
    color: 'from-red-500 to-orange-500'
  },
  {
    id: 'etude_marche',
    name: 'Étude de Marché',
    description: 'Analyse marché et opportunités',
    icon: FileText,
    color: 'from-yellow-500 to-amber-500'
  },
  {
    id: 'analyse_approfondie',
    name: 'Analyse Approfondie',
    description: 'Rapport exhaustif avec 60 sources (8000-10000 mots)',
    icon: FileText,
    color: 'from-indigo-500 to-blue-500'
  }
]

export default function HomePage() {
  const [showAnalysis, setShowAnalysis] = useState(false)
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null)

  const handleAnalysisClick = (analysisId: string) => {
    setSelectedAnalysis(analysisId)
    setShowAnalysis(true)
  }

  return (
    <div className="min-h-screen w-full">
      <Navbar />
      
      <main className="pt-24 px-4 pb-6 w-full">
        <div className="max-w-6xl mx-auto">
          {/* Header avec logo */}
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
              Intelligence stratégique par IA. Rapports professionnels et export PDF.
            </motion.p>
          </motion.div>

          {/* Affichage conditionnel : grille ou panel d'analyse */}
          {!showAnalysis ? (
            /* Grille de boutons de rapports */
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-2xl font-semibold text-white mb-6 text-center">
                Générer un Rapport
              </h2>
              
              <div className="analysis-grid">
                {analysisTypes.map((analysis, index) => {
                  const Icon = analysis.icon
                  return (
                    <motion.div
                      key={analysis.id}
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * index }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleAnalysisClick(analysis.id)}
                      className="analysis-card glow-on-hover cursor-pointer"
                    >
                      <div className="flex items-start gap-4">
                        <div className={`p-4 rounded-xl bg-gradient-to-r ${analysis.color} flex-shrink-0`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        
                        <div className="flex-1">
                          <h3 className="font-semibold text-white text-lg mb-1">
                            {analysis.name}
                          </h3>
                          <p className="text-sm text-gray-400">
                            {analysis.description}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          ) : (
            /* Panel d'analyse */
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <button
                onClick={() => setShowAnalysis(false)}
                className="glass-button mb-6 flex items-center gap-2 text-sm"
              >
                ← Retour aux rapports
              </button>
              
              <AnalysisPanel 
                analysisTypes={analysisTypes}
                initialAnalysisType={selectedAnalysis}
              />
            </motion.div>
          )}
        </div>
      </main>

      {/* Chat Widget flottant */}
      <ChatWidget />
    </div>
  )
}

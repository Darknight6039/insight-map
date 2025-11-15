'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, TrendingUp, Sparkles, Shield, FileText, Download, Play, Clock } from 'lucide-react'
import { toast } from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import ProgressBar from './ProgressBar'

interface AnalysisType {
  id: string
  name: string
  description: string
  icon: any
  color: string
  business: string[]
}

interface AnalysisPanelProps {
  analysisTypes: AnalysisType[]
  selectedBusiness: string
}

interface AnalysisResult {
  id: string
  title: string
  content: string
  timestamp: Date
  type: string
  sources: any[]
}

export default function AnalysisPanel({ analysisTypes, selectedBusiness }: AnalysisPanelProps) {
  const [activeAnalysis, setActiveAnalysis] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [selectedResult, setSelectedResult] = useState<AnalysisResult | null>(null)
  
  // États pour barre de progression
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')

  const filteredAnalyses = analysisTypes.filter(analysis => 
    analysis.business.includes(selectedBusiness)
  )

  const runAnalysis = async (analysisId: string) => {
    if (!query.trim()) {
      toast.error('Veuillez entrer une requête d\'analyse')
      return
    }

    setIsLoading(true)
    setActiveAnalysis(analysisId)
    setProgress(0)

    // Étape 1 : Initialisation (10%)
    setProgress(10)
    setProgressMessage('🔍 Recherche documents RAG...')
    await new Promise(resolve => setTimeout(resolve, 500))

    // Créer un résultat placeholder pour le streaming
    const resultId = Date.now().toString()
    const placeholderResult: AnalysisResult = {
      id: resultId,
      title: `${analysisTypes.find(a => a.id === analysisId)?.name} - ${query}`,
      content: '',
      timestamp: new Date(),
      type: analysisId,
      sources: []
    }

    setResults(prev => [placeholderResult, ...prev])
    setSelectedResult(placeholderResult)

    // Étape 2 : Préparation (25%)
    setProgress(25)
    setProgressMessage('📝 Préparation de la requête...')

    try {
      // Étape 3 : Génération (30%)
      setProgress(30)
      const isDeepAnalysis = analysisId.includes('approfondi')
      setProgressMessage(
        isDeepAnalysis 
          ? '🌐 Génération rapport avec 60 sources (1-2 min)...'
          : '🌐 Génération rapport (30-60s)...'
      )

      // Utiliser l'endpoint backend /extended-analysis pour le streaming
      const response = await fetch('http://localhost:8006/extended-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          business_type: selectedBusiness,
          analysis_type: analysisId,
          query: query,
          title: placeholderResult.title
        })
      })

      // Simuler progression pendant attente backend
      // (le backend prend 45-120s selon type, on simule progression)
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) return 90 // Cap à 90% jusqu'à réponse
          return prev + 5
        })
      }, 3000) // +5% toutes les 3s

      const data = await response.json()
      clearInterval(progressInterval)

      if (!response.ok) {
        throw new Error('Erreur lors de l\'analyse')
      }

      // Étape 4 : Finalisation (95%)
      setProgress(95)
      setProgressMessage('✅ Formatage du rapport...')
      await new Promise(resolve => setTimeout(resolve, 500))

      // Mettre à jour le résultat avec les données complètes
      const finalResult: AnalysisResult = {
        id: resultId,
        title: data.title || placeholderResult.title,
        content: data.content || 'Aucun contenu généré',
        timestamp: new Date(),
        type: analysisId,
        sources: data.sources || []
      }

      setResults(prev => prev.map(r => r.id === resultId ? finalResult : r))
      setSelectedResult(finalResult)

      // Étape 5 : Terminé (100%)
      setProgress(100)
      setProgressMessage('✅ Rapport généré avec succès!')
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.success('✅ Analyse terminée avec succès !')

    } catch (error) {
      console.error('Erreur analyse:', error)
      toast.error('❌ Erreur lors de l\'analyse')
      
      // Supprimer le résultat en cas d'erreur
      setResults(prev => prev.filter(r => r.id !== resultId))
      setSelectedResult(null)
    } finally {
      setIsLoading(false)
      setActiveAnalysis(null)
      setProgress(0)
      setProgressMessage('')
    }
  }

  const exportToPDF = async (result: AnalysisResult) => {
    try {
      const response = await fetch('http://localhost:8004/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: result.type,
          title: result.title,
          content: result.content,
          sources: result.sources,
          metadata: {
            business_type: selectedBusiness,
            generated_at: result.timestamp
          }
        })
      })

      if (!response.ok) {
        throw new Error('Erreur génération PDF')
      }

      const data = await response.json()
      
      // Télécharger le PDF
      const pdfResponse = await fetch(`http://localhost:8004/export/${data.id}`)
      if (!pdfResponse.ok) {
        throw new Error('Erreur téléchargement PDF')
      }

      const blob = await pdfResponse.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${result.title}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success('PDF exporté avec succès !')

    } catch (error) {
      console.error('Erreur export PDF:', error)
      toast.error('Erreur lors de l\'export PDF')
    }
  }

  return (
    <div className="space-y-6">
      {/* Barre de progression */}
      <ProgressBar 
        progress={progress}
        message={progressMessage}
        isVisible={isLoading}
      />
      {/* Query input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Brain className="w-6 h-6 text-axial-accent" />
          Analyses Spécialisées
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Sujet d'analyse
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ex: Analyse du marché des cryptomonnaies en 2024..."
              className="input-liquid w-full min-h-[80px] resize-none"
              disabled={isLoading}
            />
          </div>
        </div>
      </motion.div>

      {/* Analysis buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card"
      >
        <h3 className="text-lg font-semibold text-white mb-4">
          Types d'analyses disponibles
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredAnalyses.map((analysis) => {
            const Icon = analysis.icon
            const isActive = activeAnalysis === analysis.id
            
            return (
              <motion.button
                key={analysis.id}
                onClick={() => runAnalysis(analysis.id)}
                disabled={isLoading || !query.trim()}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`glass-button p-6 text-left transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed ${
                  isActive ? 'ring-2 ring-axial-accent bg-white/20' : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${analysis.color} flex-shrink-0`}>
                    {isActive && isLoading ? (
                      <div className="loading-liquid w-6 h-6"></div>
                    ) : (
                      <Icon className="w-6 h-6 text-white" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <h4 className="font-semibold text-white mb-1">
                      {analysis.name}
                    </h4>
                    <p className="text-sm text-gray-400 mb-2">
                      {analysis.description}
                    </p>
                    
                    <div className="flex items-center gap-2 text-xs text-axial-accent">
                      {isActive && isLoading ? (
                        <>
                          <Clock className="w-3 h-3" />
                          <span>Analyse en cours...</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3 h-3" />
                          <span>Lancer l'analyse</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </motion.button>
            )
          })}
        </div>
      </motion.div>

      {/* Results */}
      {results.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-4"
        >
          {/* Results list */}
          <div className="glass-card">
            <h3 className="text-lg font-semibold text-white mb-4">
              Résultats d'analyses ({results.length})
            </h3>
            
            <div className="space-y-3">
              {results.map((result) => {
                const analysisType = analysisTypes.find(a => a.id === result.type)
                const Icon = analysisType?.icon || FileText
                
                return (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`p-4 rounded-xl cursor-pointer transition-all duration-300 ${
                      selectedResult?.id === result.id 
                        ? 'bg-white/20 ring-1 ring-axial-accent' 
                        : 'bg-white/5 hover:bg-white/10'
                    }`}
                    onClick={() => setSelectedResult(result)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${analysisType?.color || 'from-gray-500 to-gray-600'}`}>
                          <Icon className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white text-sm">
                            {result.title}
                          </h4>
                          <p className="text-xs text-gray-400">
                            {result.timestamp.toLocaleString()}
                          </p>
                        </div>
                      </div>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          exportToPDF(result)
                        }}
                        className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                      >
                        <Download className="w-4 h-4 text-axial-accent" />
                      </button>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {/* Selected result content */}
          {selectedResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">
                  {selectedResult.title}
                </h3>
                <button
                  onClick={() => exportToPDF(selectedResult)}
                  className="btn-liquid flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Export PDF
                </button>
              </div>
              
              <div className="prose prose-invert prose-sm max-w-none bg-black/20 p-6 rounded-xl">
                <ReactMarkdown>{selectedResult.content}</ReactMarkdown>
              </div>
              
              {selectedResult.sources.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-semibold text-white mb-3">Sources</h4>
                  <div className="space-y-2">
                    {selectedResult.sources.map((source, index) => (
                      <div key={index} className="text-sm text-gray-400 p-3 bg-black/20 rounded-lg">
                        <span className="text-axial-accent">[Réf. {index + 1}]</span> {source.text}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  )
}

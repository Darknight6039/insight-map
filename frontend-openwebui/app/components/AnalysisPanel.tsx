'use client'

import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, TrendingUp, Sparkles, Shield, FileText, Download, Play, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface AnalysisType {
  id: string
  name: string
  description: string
  icon: any
  color: string
}

interface AnalysisPanelProps {
  analysisTypes: AnalysisType[]
  initialAnalysisType?: string | null
}

interface AnalysisResult {
  id: string
  title: string
  content: string
  timestamp: Date
  type: string
  sources: any[]
}

interface SSEProgress {
  progress: number
  step: string
  message: string
  done?: boolean
  error?: boolean
  data?: any
}

export default function AnalysisPanel({ analysisTypes, initialAnalysisType }: AnalysisPanelProps) {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResult[]>([])
  
  // États pour barre de progression SSE
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')
  const [progressStep, setProgressStep] = useState('')
  
  const abortControllerRef = useRef<AbortController | null>(null)

  // Trouver le type d'analyse sélectionné
  const selectedAnalysisType = analysisTypes.find(a => a.id === initialAnalysisType) || analysisTypes[0]
  const Icon = selectedAnalysisType.icon

  const runAnalysisWithSSE = async () => {
    if (!query.trim()) {
      toast.error('Veuillez entrer une requête d\'analyse')
      return
    }

    setIsLoading(true)
    setProgress(0)
    setProgressMessage('🚀 Démarrage...')
    setProgressStep('start')

    // Créer un résultat placeholder
    const resultId = Date.now().toString()

    try {
      abortControllerRef.current = new AbortController()
      
      // Appel SSE pour streaming
      const response = await fetch('http://localhost:8006/extended-analysis/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: selectedAnalysisType.id,
          query: query,
          title: `${selectedAnalysisType.name} - ${query.substring(0, 50)}...`
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      if (!reader) {
        throw new Error('Streaming non supporté')
      }

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        
        // Traiter les événements SSE
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || '' // Garder le dernier fragment incomplet

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: SSEProgress = JSON.parse(line.substring(6))
              
              // Mettre à jour la progression
              setProgress(data.progress)
              setProgressMessage(data.message)
              setProgressStep(data.step)

              // Si terminé avec succès
              if (data.done && data.data) {
                const finalResult: AnalysisResult = {
                  id: resultId,
                  title: data.data.title,
                  content: data.data.content,
                  timestamp: new Date(),
                  type: selectedAnalysisType.id,
                  sources: data.data.sources || []
                }

                setResults(prev => [finalResult, ...prev])
                toast.success('✅ Rapport généré avec succès !')
              }

              // Si erreur
              if (data.error) {
                throw new Error(data.message)
              }
            } catch (parseError) {
              // Ignorer les erreurs de parsing JSON partiel
            }
          }
        }
      }

    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Erreur SSE:', error)
        toast.error(`❌ Erreur: ${error.message || 'Erreur lors de l\'analyse'}`)
      }
    } finally {
      setIsLoading(false)
      setProgress(0)
      setProgressMessage('')
      setProgressStep('')
    }
  }

  const exportToPDF = async (result: AnalysisResult) => {
    try {
      toast.loading('📄 Génération du PDF...')
      
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
            generated_at: result.timestamp
          }
        })
      })

      if (!response.ok) {
        throw new Error('Erreur génération PDF')
      }

      const data = await response.json()
      
      const pdfResponse = await fetch(`http://localhost:8004/export/${data.id}`)
      if (!pdfResponse.ok) {
        throw new Error('Erreur téléchargement PDF')
      }

      const blob = await pdfResponse.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${result.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.dismiss()
      toast.success('✅ PDF téléchargé avec succès !')

    } catch (error) {
      toast.dismiss()
      console.error('Erreur export PDF:', error)
      toast.error('❌ Erreur lors de l\'export PDF')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      runAnalysisWithSSE()
    }
  }

  return (
    <div className="space-y-6">
      {/* Barre de progression SSE temps réel */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card border border-axial-accent/30"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-full bg-axial-accent/20 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-axial-accent animate-spin" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-green-500 flex items-center justify-center pulse-glow">
                  <span className="text-xs text-white font-bold">{Math.round(progress)}%</span>
                </div>
              </div>
              <div className="flex-1">
                <p className="text-white font-medium">{progressMessage}</p>
                <p className="text-sm text-gray-400">Étape: {progressStep}</p>
              </div>
            </div>
            
            {/* Barre de progression animée */}
            <div className="relative h-3 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-axial-accent to-emerald-400 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
              {/* Effet shimmer */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                animate={{ x: ['-100%', '100%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              />
            </div>
            
            {/* Estimation temps restant */}
            <p className="text-xs text-gray-500 mt-2 text-center">
              {progress < 35 ? 'Préparation...' : 
               progress < 85 ? 'Génération en cours (45-90s restantes)...' : 
               'Finalisation...'}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Carte d'analyse sélectionnée avec champ de saisie */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        {/* Type d'analyse sélectionné */}
        <div className="flex items-center gap-4 mb-6">
          <div className={`p-4 rounded-xl bg-gradient-to-r ${selectedAnalysisType.color} flex-shrink-0`}>
            <Icon className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-white">
              {selectedAnalysisType.name}
            </h2>
            <p className="text-gray-400">
              {selectedAnalysisType.description}
            </p>
          </div>
        </div>
        
        {/* Champ de saisie */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Décrivez votre sujet d'analyse
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ex: Analyse du marché des cryptomonnaies en 2024, stratégies des leaders et opportunités..."
              className="input-liquid w-full min-h-[120px] resize-none"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-2">
              Ctrl+Entrée pour lancer l'analyse
            </p>
          </div>
          
          {/* Bouton de génération */}
          <motion.button
            onClick={runAnalysisWithSSE}
            disabled={isLoading || !query.trim()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`w-full btn-liquid py-4 text-lg font-semibold flex items-center justify-center gap-3 
              ${isLoading || !query.trim() ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? (
              <>
                <Clock className="w-5 h-5 animate-spin" />
                Génération en cours... ({progress}%)
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Générer le rapport
              </>
            )}
          </motion.button>
        </div>
      </motion.div>

      {/* Résultats - UNIQUEMENT bouton téléchargement, PAS de texte brut */}
      {results.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="glass-card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Rapports générés ({results.length})
            </h3>
            
            <div className="space-y-3">
              {results.map((result) => {
                const analysisType = analysisTypes.find(a => a.id === result.type)
                const ResultIcon = analysisType?.icon || FileText
                
                return (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all duration-300 border border-white/10"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-gradient-to-r ${analysisType?.color || 'from-gray-500 to-gray-600'}`}>
                          <ResultIcon className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white text-sm">
                            {result.title}
                          </h4>
                          <p className="text-xs text-gray-400">
                            {result.timestamp.toLocaleString()} • {result.sources?.length || 0} sources
                          </p>
                        </div>
                      </div>
                      
                      {/* SEUL BOUTON: Télécharger PDF */}
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => exportToPDF(result)}
                        className="btn-liquid flex items-center gap-2 px-4 py-2"
                      >
                        <Download className="w-4 h-4" />
                        Télécharger PDF
                      </motion.button>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LayoutDashboard, TrendingUp, Sparkles, Shield, FileText, Download, Play, Clock, CheckCircle, AlertCircle, Lightbulb, Search, Zap, FileSearch, X, Loader2, Brain, Scale } from 'lucide-react'
import { toast } from 'sonner'
import { useTranslation } from '../context/LanguageContext'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { Button } from './ui/button'

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

interface ProgressDetail {
  icon: any
  label: string
  range: [number, number]
  color: string
}

export default function AnalysisPanel({ analysisTypes, initialAnalysisType }: AnalysisPanelProps) {
  const { t, language } = useTranslation()
  const { user } = useSupabaseAuth()
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8006'
  const REPORT_URL = process.env.NEXT_PUBLIC_REPORT_URL || 'http://localhost:8004'

  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [includeRecommendations, setIncludeRecommendations] = useState(true)

  // États pour barre de progression SSE améliorée
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')
  const [progressStep, setProgressStep] = useState('')
  const [sourcesCount, setSourcesCount] = useState(0)
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [logs, setLogs] = useState<string[]>([])

  const abortControllerRef = useRef<AbortController | null>(null)

  // Détails des étapes avec icônes et couleurs
  const progressSteps: ProgressDetail[] = [
    { icon: FileSearch, label: 'Recherche documentaire', range: [0, 15], color: '#10B981' },
    { icon: Search, label: 'Analyse contextuelle', range: [15, 30], color: '#3B82F6' },
    { icon: Zap, label: 'Croisement de données', range: [30, 85], color: '#8B5CF6' },
    { icon: Brain, label: 'Analyse des sources', range: [85, 95], color: '#F59E0B' },
    { icon: CheckCircle, label: 'Finalisation', range: [95, 100], color: '#06B6D4' },
  ]

  // Timer pour le temps écoulé
  useEffect(() => {
    if (isLoading && startTime) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000))
      }, 1000)
      return () => clearInterval(interval)
    }
  }, [isLoading, startTime])

  // Déterminer l'étape actuelle
  const getCurrentStep = () => {
    return progressSteps.find(step =>
      progress >= step.range[0] && progress <= step.range[1]
    ) || progressSteps[0]
  }

  const currentStep = getCurrentStep()

  // Calculer le temps estimé restant
  const getEstimatedTime = () => {
    if (progress === 0 || elapsedTime === 0) return 'Calcul...'
    const totalEstimated = (elapsedTime / progress) * 100
    const remaining = Math.max(0, Math.ceil(totalEstimated - elapsedTime))
    return `~${remaining}s`
  }

  // Déterminer la vitesse de progression
  const getProgressSpeed = () => {
    if (elapsedTime === 0) return 'normal'
    const progressRate = progress / elapsedTime
    if (progressRate > 1.5) return 'rapide'
    if (progressRate < 0.5) return 'lent'
    return 'normal'
  }

  const speedColors = {
    rapide: 'text-green-400',
    normal: 'text-blue-400',
    lent: 'text-yellow-400'
  }

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
    setProgressMessage(t('analysis.preparation'))
    setProgressStep('start')
    setSourcesCount(0)
    setStartTime(new Date())
    setElapsedTime(0)
    setLogs(['Initialisation de l\'analyse...'])

    // Créer un résultat placeholder
    const resultId = Date.now().toString()

    try {
      abortControllerRef.current = new AbortController()

      setLogs(prev => [...prev, 'Connexion au backend...'])

      // Appel SSE pour streaming
      const response = await fetch(`${BACKEND_URL}/extended-analysis/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: selectedAnalysisType.id,
          query: query,
          title: `${selectedAnalysisType.name} - ${query.substring(0, 50)}...`,
          include_recommendations: includeRecommendations,
          language: language
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`)
      }

      setLogs(prev => [...prev, 'Connexion établie, streaming démarré'])

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

              // Ajouter au log
              setLogs(prev => [...prev.slice(-9), `${data.progress}% - ${data.message}`])

              // Extraire le nombre de sources si présent
              const sourcesMatch = data.message.match(/(\d+)\s+sources?/i)
              if (sourcesMatch) {
                setSourcesCount(parseInt(sourcesMatch[1]))
              }

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
                setLogs(prev => [...prev, 'Rapport généré avec succès !'])
                toast.success(t('analysis.reportSuccess'))

                // Auto-save report to database (without triggering PDF download)
                try {
                  await fetch(`${REPORT_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      user_id: user?.id,
                      analysis_type: selectedAnalysisType.id,
                      title: data.data.title,
                      content: data.data.content,
                      sources: data.data.sources || [],
                      metadata: { generated_at: new Date().toISOString() }
                    })
                  })
                  console.log('Report auto-saved to database')
                } catch (saveError) {
                  console.error('Auto-save failed:', saveError)
                }
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
        setLogs(prev => [...prev, `Erreur: ${error.message}`])
        toast.error(`Erreur: ${error.message || 'Erreur lors de l\'analyse'}`)
      } else {
        setLogs(prev => [...prev, 'Analyse annulée par l\'utilisateur'])
        toast.error('Analyse annulée')
      }
    } finally {
      setIsLoading(false)
      setProgress(0)
      setProgressMessage('')
      setProgressStep('')
      setStartTime(null)
    }
  }

  const cancelAnalysis = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsLoading(false)
    }
  }

  const exportToPDF = async (result: AnalysisResult) => {
    try {
      toast.loading(t('analysis.pdfGenerating'))

      const response = await fetch(`${REPORT_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.id || 1,
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

      const pdfResponse = await fetch(`${REPORT_URL}/export/${data.id}`)
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
      toast.success(t('analysis.pdfSuccess'))

    } catch (error) {
      toast.dismiss()
      console.error('Erreur export PDF:', error)
      toast.error(t('analysis.pdfError'))
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      runAnalysisWithSSE()
    }
  }

  return (
    <div className="space-y-6">
      {/* Barre de progression SSE temps réel - Version améliorée */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card border border-axial-accent/30"
          >
            {/* En-tête avec infos principales */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-4 flex-1">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-axial-accent/30 to-purple-500/30 flex items-center justify-center">
                    <currentStep.icon className="w-8 h-8 text-white animate-pulse" style={{ color: currentStep.color }} />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-7 h-7 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg pulse-glow">
                    <span className="text-xs text-white font-bold">{Math.round(progress)}%</span>
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-lg font-bold text-white">{currentStep.label}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${speedColors[getProgressSpeed()]} bg-white/10`}>
                      {getProgressSpeed() === 'rapide' && 'Rapide'}
                      {getProgressSpeed() === 'normal' && 'Normal'}
                      {getProgressSpeed() === 'lent' && 'Lent'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-1">{progressMessage}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {elapsedTime}s écoulé
                    </span>
                    <span className="flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      {getEstimatedTime()} restant
                    </span>
                    {sourcesCount > 0 && (
                      <span className="flex items-center gap-1 text-green-400">
                        <FileSearch className="w-3 h-3" />
                        {sourcesCount} sources
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Bouton d'annulation */}
              <Button
                variant="ghost"
                size="icon"
                onClick={cancelAnalysis}
                title="Annuler l'analyse"
                className="text-destructive hover:bg-destructive/20"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Barre de progression animée principale */}
            <div className="relative h-3 bg-gray-800 rounded-full overflow-hidden mb-4">
              <motion.div
                className="absolute inset-y-0 left-0 rounded-full"
                style={{
                  background: `linear-gradient(90deg, ${currentStep.color}, ${currentStep.color}dd)`,
                  boxShadow: `0 0 20px ${currentStep.color}80`
                }}
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
              </motion.div>
            </div>

            {/* Étapes détaillées */}
            <div className="grid grid-cols-5 gap-2 mb-4">
              {progressSteps.map((step, index) => {
                const isActive = progress >= step.range[0] && progress <= step.range[1]
                const isCompleted = progress > step.range[1]
                const StepIcon = step.icon

                return (
                  <div
                    key={index}
                    className={`flex flex-col items-center gap-1 p-2 rounded-lg transition-all ${isActive ? 'bg-white/10 ring-2 ring-axial-accent/50' :
                      isCompleted ? 'bg-green-500/10' : 'bg-gray-800/50'
                      }`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${isActive ? 'bg-axial-accent/30 animate-pulse' :
                      isCompleted ? 'bg-green-500/30' : 'bg-gray-700/50'
                      }`}>
                      <StepIcon
                        className={`w-4 h-4 ${isActive ? 'text-axial-accent' :
                          isCompleted ? 'text-green-400' : 'text-gray-500'
                          }`}
                      />
                    </div>
                    <span className={`text-[10px] text-center leading-tight ${isActive ? 'text-white font-medium' :
                      isCompleted ? 'text-green-400' : 'text-gray-500'
                      }`}>
                      {step.label}
                    </span>
                    <span className="text-[9px] text-gray-600">
                      {step.range[0]}-{step.range[1]}%
                    </span>
                  </div>
                )
              })}
            </div>

            {/* Mini-logs déroulants */}
            <div className="bg-gray-900/50 rounded-lg p-3 max-h-32 overflow-y-auto">
              <div className="flex items-center gap-2 mb-2">
                <Loader2 className="w-3 h-3 text-axial-accent animate-spin" />
                <span className="text-xs font-medium text-gray-400">Activité en temps réel</span>
              </div>
              <div className="space-y-1">
                {logs.slice(-5).map((log, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-xs text-gray-400 font-mono"
                  >
                    {log}
                  </motion.div>
                ))}
              </div>
            </div>
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
              {t('analysis.describeSubject')}
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('analysis.placeholder')}
              className="input-liquid w-full min-h-[120px] resize-none"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-2">
              {t('analysis.ctrlEnter')}
            </p>
          </div>

          {/* Toggle Recommandations */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${includeRecommendations ? 'bg-axial-accent/20' : 'bg-gray-500/20'}`}>
                <Lightbulb className={`w-5 h-5 ${includeRecommendations ? 'text-axial-accent' : 'text-gray-400'}`} />
              </div>
              <div>
                <p className="text-white font-medium">{t('analysis.includeRecommendations')}</p>
                <p className="text-xs text-gray-400">
                  {includeRecommendations
                    ? t('analysis.includeRecommendationsDesc')
                    : t('analysis.noRecommendationsDesc')}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              onClick={() => setIncludeRecommendations(!includeRecommendations)}
              className={`relative inline-flex h-6 w-11 p-0 items-center rounded-full transition-colors duration-200 focus-visible:ring-axial-accent focus-visible:ring-offset-axial-dark ${includeRecommendations ? 'bg-axial-accent hover:bg-axial-accent/90' : 'bg-gray-600 hover:bg-gray-500'
                }`}
              disabled={isLoading}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ${includeRecommendations ? 'translate-x-6' : 'translate-x-1'
                  }`}
              />
            </Button>
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
                {t('analysis.generating')} ({progress}%)
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                {t('analysis.generateReport')}
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
              {t('analysis.generatedReports')} ({results.length})
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
                            {result.timestamp.toLocaleString()} • {result.sources?.length || 0} {t('analysis.sources')}
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
                        {t('analysis.downloadPdf')}
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

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  TrendingUp,
  Shield,
  Sparkles,
  Scale,
  ArrowLeft
} from 'lucide-react'
import MainLayout from './components/layout/MainLayout'
import HeroSection from './components/dashboard/HeroSection'
import ReportCard from './components/dashboard/ReportCard'
import AnalysisPanel from './components/AnalysisPanel'
import { Button } from './components/ui/button'
import { useTranslation } from './context/LanguageContext'

const analysisTypesConfig = [
  { id: 'synthese_executive', icon: LayoutDashboard, gradient: 'purple' as const, color: 'from-blue-500 to-cyan-500' },
  { id: 'analyse_concurrentielle', icon: TrendingUp, gradient: 'violet' as const, color: 'from-purple-500 to-pink-500' },
  { id: 'veille_technologique', icon: Sparkles, gradient: 'teal' as const, color: 'from-green-500 to-teal-500' },
  { id: 'analyse_risques', icon: Shield, gradient: 'orange' as const, color: 'from-red-500 to-orange-500' },
  { id: 'analyse_reglementaire', icon: Scale, gradient: 'pink' as const, color: 'from-amber-500 to-yellow-500' }
]

export default function HomePage() {
  const { t } = useTranslation()
  const router = useRouter()
  const [showAnalysis, setShowAnalysis] = useState(false)
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null)

  // Build analysisTypes with translated names
  const analysisTypes = analysisTypesConfig.map(config => ({
    ...config,
    name: t(`analysis.types.${config.id}`),
    description: t(`analysis.types.${config.id}_desc`)
  }))

  const handleAnalysisClick = (analysisId: string) => {
    setSelectedAnalysis(analysisId)
    setShowAnalysis(true)
  }

  return (
    <MainLayout>
      {/* Hero Section */}
      <HeroSection />

      {/* Conditional display: grid or analysis panel */}
      {!showAnalysis ? (
        /* Report cards grid */
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-xl font-semibold text-foreground mb-6">
            {t('home.generateReport')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analysisTypes.map((analysis, index) => (
              <motion.div
                key={analysis.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <ReportCard
                  title={analysis.name}
                  description={analysis.description}
                  icon={analysis.icon}
                  gradient={analysis.gradient}
                  onClick={() => handleAnalysisClick(analysis.id)}
                />
              </motion.div>
            ))}
          </div>
        </motion.div>
      ) : (
        /* Analysis Panel */
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Button
            variant="outline"
            onClick={() => setShowAnalysis(false)}
            className="mb-6 gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('home.backToReports')}
          </Button>

          <AnalysisPanel
            analysisTypes={analysisTypes}
            initialAnalysisType={selectedAnalysis}
          />
        </motion.div>
      )}
    </MainLayout>
  )
}

'use client'

import { useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  TrendingUp,
  Shield,
  Sparkles,
  BarChart3,
  Scale
} from 'lucide-react'
import MainLayout from './components/layout/MainLayout'
import HeroSection from './components/dashboard/HeroSection'
import ReportCard from './components/dashboard/ReportCard'
import { useTranslation } from './context/LanguageContext'

const analysisTypesConfig = [
  { id: 'synthese_executive', icon: LayoutDashboard, gradient: 'purple' as const },
  { id: 'analyse_concurrentielle', icon: TrendingUp, gradient: 'violet' as const },
  { id: 'veille_technologique', icon: Sparkles, gradient: 'teal' as const },
  { id: 'analyse_risques', icon: Shield, gradient: 'orange' as const },
  { id: 'etude_marche', icon: BarChart3, gradient: 'pink' as const },
  { id: 'analyse_reglementaire', icon: Scale, gradient: 'blue' as const }
]

export default function HomePage() {
  const { t } = useTranslation()
  const router = useRouter()

  // Build analysisTypes with translated names
  const analysisTypes = analysisTypesConfig.map(config => ({
    ...config,
    name: t(`analysis.types.${config.id}`),
    description: t(`analysis.types.${config.id}_desc`)
  }))

  const handleAnalysisClick = (analysisId: string) => {
    router.push(`/report/${analysisId}`)
  }

  return (
    <MainLayout>
      {/* Hero Section */}
      <HeroSection />

      {/* Report cards grid */}
      <section>
        <h2 className="text-xl font-semibold text-foreground mb-6">
          {t('home.generateReport')}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analysisTypes.map((analysis) => (
            <ReportCard
              key={analysis.id}
              title={analysis.name}
              description={analysis.description}
              icon={analysis.icon}
              gradient={analysis.gradient}
              onClick={() => handleAnalysisClick(analysis.id)}
            />
          ))}
        </div>
      </section>
    </MainLayout>
  )
}

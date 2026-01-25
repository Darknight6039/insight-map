'use client'

import { useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  TrendingUp,
  Shield,
  Sparkles,
  BarChart3,
  ArrowLeft,
  Scale
} from 'lucide-react'
import MainLayout from '../../components/layout/MainLayout'
import AnalysisPanel from '../../components/AnalysisPanel'
import { Button } from '../../components/ui/button'
import { useTranslation } from '../../context/LanguageContext'

const analysisTypesConfig = [
  { id: 'synthese_executive', icon: LayoutDashboard, gradient: 'purple' as const, color: 'from-blue-500 to-cyan-500' },
  { id: 'analyse_concurrentielle', icon: TrendingUp, gradient: 'violet' as const, color: 'from-purple-500 to-pink-500' },
  { id: 'veille_technologique', icon: Sparkles, gradient: 'teal' as const, color: 'from-green-500 to-teal-500' },
  { id: 'analyse_risques', icon: Shield, gradient: 'orange' as const, color: 'from-red-500 to-orange-500' },
  { id: 'etude_marche', icon: BarChart3, gradient: 'pink' as const, color: 'from-pink-500 to-rose-500' },
  { id: 'analyse_reglementaire', icon: Scale, gradient: 'blue' as const, color: 'from-blue-600 to-indigo-500' }
]

export default function ReportPage({ params }: { params: { reportType: string } }) {
  const { t } = useTranslation()
  const router = useRouter()

  // Build analysisTypes with translated names
  const analysisTypes = analysisTypesConfig.map(config => ({
    ...config,
    name: t(`analysis.types.${config.id}`),
    description: t(`analysis.types.${config.id}_desc`)
  }))

  // Find the current analysis type
  const currentType = analysisTypes.find(a => a.id === params.reportType)

  return (
    <MainLayout>
      {/* Back button */}
      <Button
        variant="outline"
        onClick={() => router.push('/')}
        className="mb-6 gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        {t('home.backToReports') || 'Retour aux rapports'}
      </Button>

      {/* Page title */}
      {currentType && (
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className={`p-2 rounded-lg gradient-icon-${currentType.gradient}`}>
              <currentType.icon className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">
              {currentType.name}
            </h1>
          </div>
          <p className="text-muted-foreground">
            {currentType.description}
          </p>
        </div>
      )}

      {/* Analysis Panel */}
      <AnalysisPanel
        analysisTypes={analysisTypes}
        initialAnalysisType={params.reportType}
      />
    </MainLayout>
  )
}

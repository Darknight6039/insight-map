'use client'

import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  Check,
  AlertTriangle,
  Clock,
  Mail,
  FileText,
  Trash2,
  Edit,
  Eye,
  PlayCircle,
  Loader2
} from 'lucide-react'
import { useTranslation } from '../context/LanguageContext'
import { Button } from './ui/button'

interface ActionParameters {
  [key: string]: any
}

interface ProposedAction {
  action_type: string
  label: string
  description: string
  parameters: ActionParameters
  requires_confirmation: boolean
}

interface ActionConfirmDialogProps {
  isOpen: boolean
  action: ProposedAction | null
  onConfirm: () => void
  onCancel: () => void
  isExecuting?: boolean
}

// Mapping des types d'action vers les icones
const ACTION_ICONS: Record<string, React.ReactNode> = {
  create_watch: <Clock className="w-5 h-5" />,
  update_watch: <Edit className="w-5 h-5" />,
  delete_watch: <Trash2 className="w-5 h-5" />,
  list_watches: <Eye className="w-5 h-5" />,
  generate_report: <FileText className="w-5 h-5" />,
  view_watch_details: <Eye className="w-5 h-5" />
}

// Mapping des types d'action vers les couleurs
const ACTION_COLORS: Record<string, string> = {
  create_watch: 'from-green-500 to-emerald-600',
  update_watch: 'from-blue-500 to-indigo-600',
  delete_watch: 'from-red-500 to-rose-600',
  list_watches: 'from-purple-500 to-violet-600',
  generate_report: 'from-amber-500 to-orange-600',
  view_watch_details: 'from-cyan-500 to-teal-600'
}

// Labels en francais pour les parametres
const PARAM_LABELS: Record<string, string> = {
  name: 'Nom',
  topic: 'Sujet',
  sector: 'Secteur',
  report_type: 'Type de rapport',
  frequency: 'Frequence',
  cron_expression: 'Expression cron',
  email_recipients: 'Destinataires',
  query: 'Requete',
  analysis_type: 'Type d\'analyse',
  include_recommendations: 'Inclure recommandations',
  watch_id: 'ID de la veille',
  is_active: 'Active'
}

// Labels pour les valeurs connues
const VALUE_LABELS: Record<string, string> = {
  // Analysis types
  synthese_executive: 'Synthese Executive',
  analyse_concurrentielle: 'Analyse Concurrentielle',
  veille_technologique: 'Veille Technologique',
  analyse_risques: 'Analyse des Risques',
  analyse_reglementaire: 'Analyse Reglementaire',
  // Sectors
  general: 'General',
  finance_banque: 'Finance & Banque',
  tech_digital: 'Tech & Digital',
  retail_commerce: 'Retail & Commerce',
  industrie: 'Industrie',
  sante: 'Sante',
  energie: 'Energie',
  // Frequencies
  daily: 'Quotidienne',
  weekly_monday: 'Hebdomadaire (Lundi)',
  weekly_friday: 'Hebdomadaire (Vendredi)',
  biweekly: 'Bi-hebdomadaire',
  monthly: 'Mensuelle'
}

function formatParamValue(key: string, value: any): string {
  if (value === true) return 'Oui'
  if (value === false) return 'Non'
  if (Array.isArray(value)) {
    return value.join(', ') || 'Aucun'
  }
  if (typeof value === 'string') {
    return VALUE_LABELS[value] || value
  }
  return String(value)
}

export default function ActionConfirmDialog({
  isOpen,
  action,
  onConfirm,
  onCancel,
  isExecuting = false
}: ActionConfirmDialogProps) {
  const { t } = useTranslation()
  
  if (!action) return null
  
  const icon = ACTION_ICONS[action.action_type] || <PlayCircle className="w-5 h-5" />
  const colorClass = ACTION_COLORS[action.action_type] || 'from-gray-500 to-gray-600'
  const isDestructive = action.action_type === 'delete_watch'
  
  // Filtrer les parametres vides ou null
  const visibleParams = Object.entries(action.parameters).filter(
    ([_, value]) => value !== null && value !== undefined && value !== ''
  )

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={onCancel}
          />
          
          {/* Dialog */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md"
          >
            <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl overflow-hidden">
              {/* Header */}
              <div className={`bg-gradient-to-r ${colorClass} p-4`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-white">
                      {icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-white text-lg">
                        Confirmer l'action
                      </h3>
                      <p className="text-white/80 text-sm">
                        {action.label}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={onCancel}
                    disabled={isExecuting}
                    className="text-white hover:bg-white/10"
                  >
                    <X className="w-5 h-5" />
                  </Button>
                </div>
              </div>
              
              {/* Content */}
              <div className="p-4">
                {/* Description */}
                <p className="text-gray-300 text-sm mb-4">
                  {action.description}
                </p>
                
                {/* Destructive warning */}
                {isDestructive && (
                  <div className="flex items-start gap-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg mb-4">
                    <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-red-400 text-sm font-medium">
                        Action irreversible
                      </p>
                      <p className="text-red-400/80 text-xs">
                        Cette action ne peut pas etre annulee.
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Parameters */}
                {visibleParams.length > 0 && (
                  <div className="space-y-2 mb-4">
                    <h4 className="text-gray-400 text-xs uppercase tracking-wider font-medium">
                      Parametres
                    </h4>
                    <div className="bg-gray-800/50 rounded-lg p-3 space-y-2">
                      {visibleParams.map(([key, value]) => (
                        <div key={key} className="flex justify-between items-start">
                          <span className="text-gray-400 text-sm">
                            {PARAM_LABELS[key] || key}:
                          </span>
                          <span className="text-white text-sm text-right max-w-[60%] break-words">
                            {formatParamValue(key, value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              {/* Actions */}
              <div className="p-4 bg-gray-800/50 border-t border-gray-700 flex gap-3">
                <Button
                  variant="secondary"
                  onClick={onCancel}
                  disabled={isExecuting}
                  className="flex-1"
                >
                  Annuler
                </Button>
                <Button
                  variant={isDestructive ? "destructive" : "default"}
                  onClick={onConfirm}
                  disabled={isExecuting}
                  className="flex-1"
                >
                  {isExecuting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Execution...
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4" />
                      Confirmer
                    </>
                  )}
                </Button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Clock, 
  Mail, 
  Calendar, 
  Play, 
  Pause, 
  Trash2, 
  Plus, 
  Search,
  CheckCircle,
  XCircle,
  Loader2,
  ChevronDown,
  Settings,
  History,
  Bell,
  RefreshCw,
  Edit
} from 'lucide-react'

const SCHEDULER_URL = process.env.NEXT_PUBLIC_SCHEDULER_URL || 'http://localhost:8007'

// Types
interface Watch {
  id: number
  name: string
  topic: string
  sector: string
  report_type: string
  keywords: string[]
  sources_preference: string
  cron_expression: string
  email_recipients: string[]
  is_active: boolean
  created_at: string
  next_run: string | null
}

interface WatchHistory {
  id: number
  watch_id: number
  executed_at: string
  status: string
  report_id: number | null
  error_message: string | null
  execution_time_seconds: number | null
}

interface CronPreset {
  id: string
  name: string
  cron: string
  description: string
}

// Report type options
const reportTypes = [
  { id: 'synthese_executive', name: 'Synthèse Exécutive' },
  { id: 'analyse_concurrentielle', name: 'Analyse Concurrentielle' },
  { id: 'veille_technologique', name: 'Veille Technologique' },
  { id: 'analyse_risques', name: 'Analyse des Risques' },
  { id: 'etude_marche', name: 'Étude de Marché' },
  { id: 'analyse_approfondie', name: 'Analyse Approfondie (60 sources)' },
]

// Sector options
const sectors = [
  { id: 'general', name: 'Général' },
  { id: 'finance_banque', name: 'Finance & Banque' },
  { id: 'tech_digital', name: 'Tech & Digital' },
  { id: 'retail_commerce', name: 'Retail & Commerce' },
  { id: 'industrie', name: 'Industrie' },
  { id: 'sante', name: 'Santé' },
  { id: 'energie', name: 'Énergie' },
]

export default function WatchesPanel() {
  const [watches, setWatches] = useState<Watch[]>([])
  const [presets, setPresets] = useState<CronPreset[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingWatch, setEditingWatch] = useState<Watch | null>(null)
  const [selectedWatch, setSelectedWatch] = useState<Watch | null>(null)
  const [showHistory, setShowHistory] = useState(false)
  const [history, setHistory] = useState<WatchHistory[]>([])
  const [error, setError] = useState<string | null>(null)
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    topic: '',
    sector: 'general',
    report_type: 'synthese_executive',
    keywords: '',
    cron_expression: '0 8 * * 1',
    email_recipients: '',
  })

  // Cron expression parts state
  const [cronParts, setCronParts] = useState({
    minute: '0',
    hour: '8',
    dayOfMonth: '*',
    month: '*',
    dayOfWeek: '1',
  })

  // Parse cron expression to parts
  const parseCronExpression = (cron: string) => {
    const parts = cron.split(' ')
    if (parts.length === 5) {
      // Normaliser l'heure pour éviter les problèmes de format (08 vs 8)
      const hour = parts[1] === '*' ? '*' : parseInt(parts[1], 10).toString()
      return {
        minute: parts[0],
        hour: hour,
        dayOfMonth: parts[2],
        month: parts[3],
        dayOfWeek: parts[4],
      }
    }
    return { minute: '0', hour: '8', dayOfMonth: '*', month: '*', dayOfWeek: '1' }
  }

  // Build cron expression from parts
  const buildCronExpression = (parts: typeof cronParts) => {
    return `${parts.minute} ${parts.hour} ${parts.dayOfMonth} ${parts.month} ${parts.dayOfWeek}`
  }

  // Update cron expression when parts change (but not when formData changes externally)
  useEffect(() => {
    const newCron = buildCronExpression(cronParts)
    setFormData(prev => {
      if (prev.cron_expression !== newCron) {
        return { ...prev, cron_expression: newCron }
      }
      return prev
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cronParts.minute, cronParts.hour, cronParts.dayOfMonth, cronParts.month, cronParts.dayOfWeek])

  // Fetch watches on mount
  useEffect(() => {
    fetchWatches()
    fetchPresets()
  }, [])

  const fetchWatches = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${SCHEDULER_URL}/watches`)
      if (!response.ok) throw new Error('Failed to fetch watches')
      const data = await response.json()
      setWatches(data)
    } catch (err) {
      setError('Impossible de charger les veilles')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchPresets = async () => {
    try {
      const response = await fetch(`${SCHEDULER_URL}/presets`)
      if (response.ok) {
        const data = await response.json()
        setPresets(data.presets)
      }
    } catch (err) {
      console.error('Failed to fetch presets:', err)
    }
  }

  const fetchHistory = async (watchId: number) => {
    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}/history`)
      if (response.ok) {
        const data = await response.json()
        setHistory(data)
      }
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }

  const loadWatchForEdit = (watch: Watch) => {
    const parts = parseCronExpression(watch.cron_expression)
    setCronParts(parts)
    setFormData({
      name: watch.name,
      topic: watch.topic,
      sector: watch.sector,
      report_type: watch.report_type,
      keywords: watch.keywords.join(', '),
      cron_expression: watch.cron_expression,
      email_recipients: watch.email_recipients.join(', '),
    })
    setEditingWatch(watch)
    setShowCreateForm(true)
  }

  const createWatch = async () => {
    try {
      const payload = {
        ...formData,
        keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k),
        email_recipients: formData.email_recipients.split(',').map(e => e.trim()).filter(e => e),
      }
      
      const response = await fetch(`${SCHEDULER_URL}/watches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to create watch')
      }
      
      await fetchWatches()
      setShowCreateForm(false)
      setEditingWatch(null)
      resetForm()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const updateWatch = async () => {
    if (!editingWatch) return
    
    try {
      const payload = {
        ...formData,
        keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k),
        email_recipients: formData.email_recipients.split(',').map(e => e.trim()).filter(e => e),
      }
      
      const response = await fetch(`${SCHEDULER_URL}/watches/${editingWatch.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to update watch')
      }
      
      await fetchWatches()
      setShowCreateForm(false)
      setEditingWatch(null)
      resetForm()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const toggleWatch = async (watchId: number) => {
    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}/toggle`, {
        method: 'POST',
      })
      if (response.ok) {
        await fetchWatches()
      }
    } catch (err) {
      console.error('Failed to toggle watch:', err)
    }
  }

  const deleteWatch = async (watchId: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette veille ?')) return
    
    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        await fetchWatches()
        setSelectedWatch(null)
      }
    } catch (err) {
      console.error('Failed to delete watch:', err)
    }
  }

  const triggerWatch = async (watchId: number) => {
    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}/trigger`, {
        method: 'POST',
      })
      if (response.ok) {
        setError(null)
        alert('Veille déclenchée avec succès !')
      }
    } catch (err) {
      console.error('Failed to trigger watch:', err)
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      topic: '',
      sector: 'general',
      report_type: 'synthese_executive',
      keywords: '',
      cron_expression: '0 8 * * 1',
      email_recipients: '',
    })
    setCronParts({
      minute: '0',
      hour: '8',
      dayOfMonth: '*',
      month: '*',
      dayOfWeek: '1',
    })
    setEditingWatch(null)
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      success: 'bg-green-500/20 text-green-400 border-green-500/30',
      failed: 'bg-red-500/20 text-red-400 border-red-500/30',
      running: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    }
    return styles[status] || styles.pending
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Bell className="w-7 h-7 text-cyan-400" />
            Veilles Automatisées
          </h1>
          <p className="text-gray-400 mt-1">
            Configurez des rapports automatiques envoyés par email
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={fetchWatches}
            className="glass-button flex items-center gap-2 px-4 py-2"
          >
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
          <button
            onClick={() => setShowCreateForm(true)}
            className="primary-button flex items-center gap-2 px-4 py-2"
          >
            <Plus className="w-4 h-4" />
            Nouvelle veille
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-400"
        >
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">
            Fermer
          </button>
        </motion.div>
      )}

      {/* Create form modal */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowCreateForm(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
                {editingWatch ? (
                  <>
                    <Edit className="w-5 h-5 text-cyan-400" />
                    Modifier la veille
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5 text-cyan-400" />
                    Créer une nouvelle veille
                  </>
                )}
              </h2>

              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Nom de la veille *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="glass-input w-full"
                    placeholder="Ex: Veille secteur bancaire"
                  />
                </div>

                {/* Topic */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Sujet à analyser *
                  </label>
                  <input
                    type="text"
                    value={formData.topic}
                    onChange={e => setFormData({ ...formData, topic: e.target.value })}
                    className="glass-input w-full"
                    placeholder="Ex: Évolution des taux d'intérêt en Europe"
                  />
                </div>

                {/* Sector & Report Type */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Secteur
                    </label>
                    <select
                      value={formData.sector}
                      onChange={e => setFormData({ ...formData, sector: e.target.value })}
                      className="glass-input w-full"
                    >
                      {sectors.map(s => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Type de rapport
                    </label>
                    <select
                      value={formData.report_type}
                      onChange={e => setFormData({ ...formData, report_type: e.target.value })}
                      className="glass-input w-full"
                    >
                      {reportTypes.map(r => (
                        <option key={r.id} value={r.id}>{r.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Keywords */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Mots-clés (séparés par des virgules)
                  </label>
                  <input
                    type="text"
                    value={formData.keywords}
                    onChange={e => setFormData({ ...formData, keywords: e.target.value })}
                    className="glass-input w-full"
                    placeholder="Ex: taux, BCE, inflation, crédit"
                  />
                </div>

                {/* Schedule */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Fréquence d'exécution
                  </label>
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    {presets.map(preset => (
                      <button
                        key={preset.id}
                        type="button"
                        onClick={() => {
                          const parts = parseCronExpression(preset.cron)
                          setCronParts(parts)
                          setFormData({ ...formData, cron_expression: preset.cron })
                        }}
                        className={`glass-button text-sm py-2 px-3 ${
                          formData.cron_expression === preset.cron 
                            ? 'bg-cyan-500/20 border-cyan-500/50' 
                            : ''
                        }`}
                      >
                        {preset.name}
                      </button>
                    ))}
                  </div>
                  
                  {/* Custom schedule with dropdowns */}
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      {/* Minute */}
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                          Minute
                        </label>
                        <select
                          value={cronParts.minute}
                          onChange={e => setCronParts({ ...cronParts, minute: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                          {Array.from({ length: 60 }, (_, i) => (
                            <option key={i} value={i.toString()}>
                              {i.toString().padStart(2, '0')}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Hour */}
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                          Heure
                        </label>
                        <select
                          value={cronParts.hour}
                          onChange={e => {
                            const selectedHour = e.target.value
                            setCronParts({ ...cronParts, hour: selectedHour })
                          }}
                          className="glass-input w-full text-sm"
                        >
                          {Array.from({ length: 24 }, (_, i) => {
                            const hourValue = i.toString()
                            const hourDisplay = i.toString().padStart(2, '0')
                            return (
                              <option key={i} value={hourValue}>
                                {hourDisplay}h
                              </option>
                            )
                          })}
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                      {/* Day of Week */}
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                          Jour de la semaine
                        </label>
                        <select
                          value={cronParts.dayOfWeek}
                          onChange={e => setCronParts({ ...cronParts, dayOfWeek: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                          <option value="*">Tous les jours</option>
                          <option value="0">Dimanche</option>
                          <option value="1">Lundi</option>
                          <option value="2">Mardi</option>
                          <option value="3">Mercredi</option>
                          <option value="4">Jeudi</option>
                          <option value="5">Vendredi</option>
                          <option value="6">Samedi</option>
                        </select>
                      </div>

                      {/* Day of Month */}
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                          Jour du mois
                        </label>
                        <select
                          value={cronParts.dayOfMonth}
                          onChange={e => setCronParts({ ...cronParts, dayOfMonth: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                          <option value="*">Tous les jours</option>
                          {Array.from({ length: 31 }, (_, i) => (
                            <option key={i + 1} value={(i + 1).toString()}>
                              {i + 1}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Month */}
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                          Mois
                        </label>
                        <select
                          value={cronParts.month}
                          onChange={e => setCronParts({ ...cronParts, month: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                          <option value="*">Tous les mois</option>
                          <option value="1">Janvier</option>
                          <option value="2">Février</option>
                          <option value="3">Mars</option>
                          <option value="4">Avril</option>
                          <option value="5">Mai</option>
                          <option value="6">Juin</option>
                          <option value="7">Juillet</option>
                          <option value="8">Août</option>
                          <option value="9">Septembre</option>
                          <option value="10">Octobre</option>
                          <option value="11">Novembre</option>
                          <option value="12">Décembre</option>
                        </select>
                      </div>
                    </div>

                    {/* Display cron expression */}
                    <div className="mt-2 p-2 bg-gray-800/50 rounded border border-gray-700">
                      <p className="text-xs text-gray-400 mb-1">Expression cron générée :</p>
                      <code className="text-xs font-mono text-cyan-400">
                        {formData.cron_expression}
                      </code>
                    </div>
                  </div>
                </div>

                {/* Email recipients */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Destinataires email * (séparés par des virgules)
                  </label>
                  <input
                    type="text"
                    value={formData.email_recipients}
                    onChange={e => setFormData({ ...formData, email_recipients: e.target.value })}
                    className="glass-input w-full"
                    placeholder="Ex: john@company.com, jane@company.com"
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                  <button
                    onClick={() => { setShowCreateForm(false); resetForm(); }}
                    className="glass-button px-6 py-2"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={editingWatch ? updateWatch : createWatch}
                    disabled={!formData.name || !formData.topic || !formData.email_recipients}
                    className="primary-button px-6 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {editingWatch ? 'Enregistrer les modifications' : 'Créer la veille'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Watches list */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
        </div>
      ) : watches.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-card text-center py-16"
        >
          <Bell className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-400 mb-2">
            Aucune veille configurée
          </h3>
          <p className="text-gray-500 mb-6">
            Créez votre première veille automatisée pour recevoir des rapports par email
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="primary-button inline-flex items-center gap-2 px-6 py-3"
          >
            <Plus className="w-5 h-5" />
            Créer une veille
          </button>
        </motion.div>
      ) : (
        <div className="grid gap-4">
          {watches.map((watch, index) => (
            <motion.div
              key={watch.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-card hover:border-cyan-500/30 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-white">
                      {watch.name}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs border ${
                      watch.is_active 
                        ? 'bg-green-500/20 text-green-400 border-green-500/30'
                        : 'bg-gray-500/20 text-gray-400 border-gray-500/30'
                    }`}>
                      {watch.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <p className="text-gray-400 mb-3">{watch.topic}</p>
                  
                  <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-2 text-gray-500">
                      <Search className="w-4 h-4" />
                      {reportTypes.find(r => r.id === watch.report_type)?.name || watch.report_type}
                    </div>
                    <div className="flex items-center gap-2 text-gray-500">
                      <Clock className="w-4 h-4" />
                      {watch.cron_expression}
                    </div>
                    <div className="flex items-center gap-2 text-gray-500">
                      <Mail className="w-4 h-4" />
                      {watch.email_recipients.length} destinataire(s)
                    </div>
                    {watch.next_run && (
                      <div className="flex items-center gap-2 text-cyan-400">
                        <Calendar className="w-4 h-4" />
                        Prochaine: {formatDate(watch.next_run)}
                      </div>
                    )}
                  </div>
                  
                  {watch.keywords && watch.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {watch.keywords.map((kw, i) => (
                        <span 
                          key={i}
                          className="px-2 py-1 bg-white/5 rounded-lg text-xs text-gray-400"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => loadWatchForEdit(watch)}
                    className="glass-button p-2 hover:bg-cyan-500/20"
                    title="Modifier"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => triggerWatch(watch.id)}
                    className="glass-button p-2 hover:bg-green-500/20"
                    title="Exécuter maintenant"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => toggleWatch(watch.id)}
                    className={`glass-button p-2 ${
                      watch.is_active ? 'hover:bg-yellow-500/20' : 'hover:bg-green-500/20'
                    }`}
                    title={watch.is_active ? 'Désactiver' : 'Activer'}
                  >
                    {watch.is_active ? (
                      <Pause className="w-4 h-4" />
                    ) : (
                      <Play className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setSelectedWatch(watch)
                      setShowHistory(true)
                      fetchHistory(watch.id)
                    }}
                    className="glass-button p-2 hover:bg-blue-500/20"
                    title="Historique"
                  >
                    <History className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteWatch(watch.id)}
                    className="glass-button p-2 hover:bg-red-500/20"
                    title="Supprimer"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* History modal */}
      <AnimatePresence>
        {showHistory && selectedWatch && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowHistory(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card w-full max-w-2xl max-h-[80vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <History className="w-5 h-5 text-cyan-400" />
                Historique - {selectedWatch.name}
              </h2>

              {history.length === 0 ? (
                <p className="text-gray-400 text-center py-8">
                  Aucune exécution enregistrée
                </p>
              ) : (
                <div className="space-y-3">
                  {history.map(h => (
                    <div
                      key={h.id}
                      className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        {h.status === 'success' ? (
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        ) : h.status === 'failed' ? (
                          <XCircle className="w-5 h-5 text-red-400" />
                        ) : h.status === 'running' ? (
                          <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                        ) : (
                          <Clock className="w-5 h-5 text-yellow-400" />
                        )}
                        <div>
                          <p className="text-white text-sm">
                            {formatDate(h.executed_at)}
                          </p>
                          {h.error_message && (
                            <p className="text-red-400 text-xs mt-1 max-w-md truncate">
                              {h.error_message}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {h.execution_time_seconds && (
                          <span className="text-xs text-gray-500">
                            {h.execution_time_seconds}s
                          </span>
                        )}
                        <span className={`px-2 py-1 rounded-full text-xs border ${getStatusBadge(h.status)}`}>
                          {h.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-end pt-4 mt-4 border-t border-white/10">
                <button
                  onClick={() => setShowHistory(false)}
                  className="glass-button px-6 py-2"
                >
                  Fermer
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

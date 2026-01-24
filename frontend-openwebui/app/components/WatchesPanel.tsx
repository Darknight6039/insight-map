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
import { useTranslation } from '../context/LanguageContext'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { Button } from './ui/button'

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

// Report type IDs (names will be translated)
const reportTypeIds = [
  'synthese_executive',
  'analyse_concurrentielle',
  'veille_technologique',
  'analyse_risques',
  'analyse_reglementaire',
]

// Sector IDs (names will be translated)
const sectorIds = [
  'general',
  'finance_banque',
  'tech_digital',
  'retail_commerce',
  'industrie',
  'sante',
  'energie',
]

export default function WatchesPanel() {
  const { t } = useTranslation()
  const { user } = useSupabaseAuth()
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
  
  // Frequency type for agenda-style selector
  const [frequencyType, setFrequencyType] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>('weekly')
  const [selectedDays, setSelectedDays] = useState<number[]>([1]) // 0=Sun, 1=Mon, etc.

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

  // Fetch watches on mount and when user changes
  useEffect(() => {
    if (user?.id) {
      fetchWatches()
      fetchPresets()
    }
  }, [user?.id])

  const fetchWatches = async () => {
    try {
      setLoading(true)
      // Pass user_id to filter watches by current user (Supabase UUID)
      const url = user?.id
        ? `${SCHEDULER_URL}/watches?user_id=${user.id}`
        : `${SCHEDULER_URL}/watches`
      const response = await fetch(url)
      if (!response.ok) throw new Error('Failed to fetch watches')
      const data = await response.json()
      setWatches(data)
    } catch (err) {
      setError(t('watches.loadError'))
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
        user_id: user?.id,  // Include Supabase UUID for user ownership
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
        user_id: user?.id,  // Include Supabase UUID for user ownership
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
    if (!confirm(t('watches.deleteConfirm'))) return
    
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
        alert(t('watches.triggerSuccess'))
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
      {/* Actions bar */}
      <div className="flex items-center justify-end gap-2">
        <Button variant="outline" onClick={fetchWatches}>
          <RefreshCw className="w-4 h-4" />
          {t('common.refresh')}
        </Button>
        <Button variant="default" onClick={() => setShowCreateForm(true)}>
          <Plus className="w-4 h-4" />
          {t('watches.newWatch')}
        </Button>
      </div>

      {/* Error message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-red-400"
        >
          {error}
          <Button variant="link" onClick={() => setError(null)} className="ml-4">
            {t('common.close')}
          </Button>
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
                    {t('watches.editWatch')}
                  </>
                ) : (
                  <>
                    <Plus className="w-5 h-5 text-cyan-400" />
                    {t('watches.createNewWatch')}
                  </>
                )}
              </h2>

              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('watches.watchName')}
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    className="glass-input w-full"
                    placeholder={t('watches.watchNamePlaceholder')}
                  />
                </div>

                {/* Topic */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('watches.topicToAnalyze')}
                  </label>
                  <input
                    type="text"
                    value={formData.topic}
                    onChange={e => setFormData({ ...formData, topic: e.target.value })}
                    className="glass-input w-full"
                    placeholder={t('watches.topicPlaceholder')}
                  />
                </div>

                {/* Sector & Report Type */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('watches.sector')}
                    </label>
                    <select
                      value={formData.sector}
                      onChange={e => setFormData({ ...formData, sector: e.target.value })}
                      className="glass-input w-full"
                    >
                      {sectorIds.map(id => (
                        <option key={id} value={id}>{t(`watches.sectors.${id}`)}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      {t('watches.reportType')}
                    </label>
                    <select
                      value={formData.report_type}
                      onChange={e => setFormData({ ...formData, report_type: e.target.value })}
                      className="glass-input w-full"
                    >
                      {reportTypeIds.map(id => (
                        <option key={id} value={id}>{t(`analysis.types.${id}`)}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Keywords */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('watches.keywords')}
                  </label>
                  <input
                    type="text"
                    value={formData.keywords}
                    onChange={e => setFormData({ ...formData, keywords: e.target.value })}
                    className="glass-input w-full"
                    placeholder={t('watches.keywordsPlaceholder')}
                  />
                </div>

                {/* Schedule - Agenda style */}
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-gray-300">
                    {t('watches.executionFrequency')}
                  </label>
                  
                  {/* Frequency type selector */}
                  <div className="grid grid-cols-4 gap-2">
                    {[
                      { id: 'daily', label: t('watches.frequencyDaily'), icon: '1' },
                      { id: 'weekly', label: t('watches.frequencyWeekly'), icon: '7' },
                      { id: 'monthly', label: t('watches.frequencyMonthly'), icon: '30' },
                      { id: 'custom', label: t('watches.frequencyCustom'), icon: '*' },
                    ].map(freq => (
                      <Button
                        key={freq.id}
                        type="button"
                        variant={frequencyType === freq.id ? 'accent' : 'glass'}
                        onClick={() => {
                          setFrequencyType(freq.id as any)
                          // Set default cron based on frequency
                          if (freq.id === 'daily') {
                            setCronParts({ ...cronParts, dayOfWeek: '*', dayOfMonth: '*' })
                            setFormData({ ...formData, cron_expression: `${cronParts.minute} ${cronParts.hour} * * *` })
                          } else if (freq.id === 'weekly') {
                            setCronParts({ ...cronParts, dayOfMonth: '*', dayOfWeek: '1' })
                            setFormData({ ...formData, cron_expression: `${cronParts.minute} ${cronParts.hour} * * 1` })
                          } else if (freq.id === 'monthly') {
                            setCronParts({ ...cronParts, dayOfWeek: '*', dayOfMonth: '1' })
                            setFormData({ ...formData, cron_expression: `${cronParts.minute} ${cronParts.hour} 1 * *` })
                          }
                        }}
                        className="flex flex-col items-center gap-1 p-3 h-auto"
                      >
                        <span className="text-lg font-bold">{freq.icon}</span>
                        <span className="text-xs">{freq.label}</span>
                      </Button>
                    ))}
                  </div>
                  
                  {/* Execution time */}
                      <div>
                    <label className="block text-xs font-medium text-gray-400 mb-2">
                      {t('watches.executionTime')}
                        </label>
                    <div className="flex items-center gap-2">
                      <select
                        value={cronParts.hour}
                        onChange={e => {
                          setCronParts({ ...cronParts, hour: e.target.value })
                        }}
                        className="glass-input w-24 text-sm text-center"
                      >
                        {Array.from({ length: 24 }, (_, i) => (
                          <option key={i} value={i.toString()}>
                            {i.toString().padStart(2, '0')}h
                          </option>
                        ))}
                      </select>
                      <span className="text-gray-500">:</span>
                        <select
                          value={cronParts.minute}
                          onChange={e => setCronParts({ ...cronParts, minute: e.target.value })}
                        className="glass-input w-24 text-sm text-center"
                        >
                        {[0, 15, 30, 45].map(m => (
                          <option key={m} value={m.toString()}>
                            {m.toString().padStart(2, '0')}
                            </option>
                          ))}
                        </select>
                    </div>
                      </div>

                  {/* Weekly day selector */}
                  {frequencyType === 'weekly' && (
                      <div>
                      <label className="block text-xs font-medium text-gray-400 mb-2">
                        {t('watches.selectDays')}
                      </label>
                      <div className="flex gap-2">
                        {[
                          { value: '1', label: 'L' },
                          { value: '2', label: 'M' },
                          { value: '3', label: 'M' },
                          { value: '4', label: 'J' },
                          { value: '5', label: 'V' },
                          { value: '6', label: 'S' },
                          { value: '0', label: 'D' },
                        ].map(day => (
                          <Button
                            key={day.value}
                            type="button"
                            variant={cronParts.dayOfWeek === day.value ? 'accent' : 'glass'}
                            size="icon"
                            onClick={() => {
                              const newValue = day.value
                              setCronParts({ ...cronParts, dayOfWeek: newValue })
                              setFormData({ ...formData, cron_expression: `${cronParts.minute} ${cronParts.hour} * * ${newValue}` })
                            }}
                            className="w-10 h-10 text-sm font-medium"
                          >
                            {day.label}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Monthly day selector */}
                  {frequencyType === 'monthly' && (
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-2">
                        {t('watches.selectDayOfMonth')}
                        </label>
                        <select
                        value={cronParts.dayOfMonth}
                          onChange={e => {
                          setCronParts({ ...cronParts, dayOfMonth: e.target.value })
                          setFormData({ ...formData, cron_expression: `${cronParts.minute} ${cronParts.hour} ${e.target.value} * *` })
                          }}
                        className="glass-input w-32 text-sm"
                        >
                        {Array.from({ length: 28 }, (_, i) => (
                          <option key={i + 1} value={(i + 1).toString()}>
                            {i + 1}
                              </option>
                        ))}
                        </select>
                      </div>
                  )}

                  {/* Custom cron (advanced) */}
                  {frequencyType === 'custom' && (
                    <div className="space-y-3 p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                            {t('watches.dayOfWeek')}
                        </label>
                        <select
                          value={cronParts.dayOfWeek}
                          onChange={e => setCronParts({ ...cronParts, dayOfWeek: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                            <option value="*">{t('watches.allDays')}</option>
                            <option value="1-5">Lun-Ven</option>
                            {['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'].map((day, i) => (
                              <option key={i} value={i.toString()}>{day}</option>
                            ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                            {t('watches.dayOfMonth')}
                        </label>
                        <select
                          value={cronParts.dayOfMonth}
                          onChange={e => setCronParts({ ...cronParts, dayOfMonth: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                            <option value="*">{t('watches.allDays')}</option>
                          {Array.from({ length: 31 }, (_, i) => (
                              <option key={i + 1} value={(i + 1).toString()}>{i + 1}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-400 mb-1">
                            {t('watches.month')}
                        </label>
                        <select
                          value={cronParts.month}
                          onChange={e => setCronParts({ ...cronParts, month: e.target.value })}
                          className="glass-input w-full text-sm"
                        >
                            <option value="*">{t('watches.allMonths')}</option>
                            {[
                              'Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin',
                              'Juil', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'
                            ].map((month, i) => (
                              <option key={i + 1} value={(i + 1).toString()}>{month}</option>
                            ))}
                        </select>
                      </div>
                    </div>
                      <div className="p-2 bg-gray-800/50 rounded border border-gray-700">
                        <p className="text-xs text-gray-400 mb-1">{t('watches.cronGenerated')}</p>
                      <code className="text-xs font-mono text-cyan-400">
                        {formData.cron_expression}
                      </code>
                    </div>
                  </div>
                  )}
                </div>

                {/* Email recipients */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {t('watches.emailRecipients')}
                  </label>
                  <input
                    type="text"
                    value={formData.email_recipients}
                    onChange={e => setFormData({ ...formData, email_recipients: e.target.value })}
                    className="glass-input w-full"
                    placeholder={t('watches.emailRecipientsPlaceholder')}
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-5 border-t border-white/10">
                  <Button
                    variant="outline"
                    onClick={() => { setShowCreateForm(false); resetForm(); }}
                  >
                    {t('common.cancel')}
                  </Button>
                  <Button
                    variant="default"
                    onClick={editingWatch ? updateWatch : createWatch}
                    disabled={!formData.name || !formData.topic || !formData.email_recipients}
                  >
                    {editingWatch ? t('watches.saveChanges') : t('watches.createWatch')}
                  </Button>
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
            {t('watches.noWatches')}
          </h3>
          <p className="text-gray-500 mb-6">
            {t('watches.noWatchesDesc')}
          </p>
          <Button
            variant="default"
            onClick={() => setShowCreateForm(true)}
            size="lg"
          >
            <Plus className="w-5 h-5" />
            {t('watches.createWatch')}
          </Button>
        </motion.div>
      ) : (
        <div className="grid gap-4">
          {watches.map((watch, index) => (
            <motion.div
              key={watch.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="p-5 rounded-xl bg-white/[0.03] border border-white/10 hover:border-cyan-500/30 hover:bg-white/[0.05] transition-all duration-300"
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
                      {watch.is_active ? t('common.active') : t('common.inactive')}
                    </span>
                  </div>
                  
                  <p className="text-gray-400 mb-3">{watch.topic}</p>
                  
                  <div className="flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center gap-2 text-gray-500">
                      <Search className="w-4 h-4" />
                      {t(`analysis.types.${watch.report_type}`)}
                    </div>
                    <div className="flex items-center gap-2 text-gray-500">
                      <Clock className="w-4 h-4" />
                      {watch.cron_expression}
                    </div>
                    <div className="flex items-center gap-2 text-gray-500">
                      <Mail className="w-4 h-4" />
                      {watch.email_recipients.length} {t('watches.recipients')}
                    </div>
                    {watch.next_run && (
                      <div className="flex items-center gap-2 text-cyan-400">
                        <Calendar className="w-4 h-4" />
                        {t('watches.nextRun')} {formatDate(watch.next_run)}
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

                <div className="flex items-center gap-1.5">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => loadWatchForEdit(watch)}
                    title="Modifier"
                    className="text-muted-foreground hover:text-primary"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => triggerWatch(watch.id)}
                    title="Executer maintenant"
                    className="text-muted-foreground hover:text-green-400 hover:bg-green-500/10"
                  >
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => toggleWatch(watch.id)}
                    title={watch.is_active ? 'Desactiver' : 'Activer'}
                    className={watch.is_active
                      ? 'text-yellow-400 hover:text-yellow-300 hover:bg-yellow-500/10'
                      : 'text-muted-foreground hover:text-green-400 hover:bg-green-500/10'
                    }
                  >
                    {watch.is_active ? (
                      <Pause className="w-4 h-4" />
                    ) : (
                      <Play className="w-4 h-4" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setSelectedWatch(watch)
                      setShowHistory(true)
                      fetchHistory(watch.id)
                    }}
                    title="Historique"
                    className="text-muted-foreground hover:text-blue-400 hover:bg-blue-500/10"
                  >
                    <History className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => deleteWatch(watch.id)}
                    title="Supprimer"
                    className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
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
                {t('watches.history')} - {selectedWatch.name}
              </h2>

              {history.length === 0 ? (
                <p className="text-gray-400 text-center py-8">
                  {t('watches.noHistory')}
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
                <Button
                  variant="outline"
                  onClick={() => setShowHistory(false)}
                >
                  {t('common.close')}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

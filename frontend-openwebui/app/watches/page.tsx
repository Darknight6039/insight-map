'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import MainLayout from '../components/layout/MainLayout'
import VeilleCard from '../components/veilles/VeilleCard'
import NewVeilleSheet, { VeilleFormData } from '../components/veilles/NewVeilleSheet'
import ConfirmDialog from '../components/ConfirmDialog'
import { useTranslation } from '../context/LanguageContext'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { Bell, Plus, Clock, Mail, Search, Filter, X, Calendar, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'

const SCHEDULER_URL = process.env.NEXT_PUBLIC_SCHEDULER_URL || 'http://localhost:8007'

interface Watch {
  id: number
  name: string
  subject: string
  sector?: string
  report_type?: string
  keywords?: string
  schedule?: string
  cron_expression?: string
  recipients?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  next_run?: string
  last_run?: string
}

interface HistoryEntry {
  id: number
  watch_id: number
  status: 'success' | 'failure' | 'running'
  executed_at: string
  completed_at?: string
  error_message?: string
  report_id?: number
}

export default function WatchesPage() {
  const { t } = useTranslation()
  const { user } = useSupabaseAuth()

  // State
  const [watches, setWatches] = useState<Watch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all')

  // Sheet state
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingWatch, setEditingWatch] = useState<VeilleFormData | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Delete confirmation
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; name: string } | null>(null)

  // Trigger state
  const [triggeringId, setTriggeringId] = useState<number | null>(null)

  // History modal
  const [historyModal, setHistoryModal] = useState<{ watchId: number; watchName: string } | null>(null)
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)

  // Fetch watches
  const fetchWatches = useCallback(async () => {
    if (!user?.id) return

    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${SCHEDULER_URL}/watches?user_id=${user.id}`)

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setWatches(data)
    } catch (err) {
      console.error('Error fetching watches:', err)
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement des veilles')
    } finally {
      setLoading(false)
    }
  }, [user?.id])

  useEffect(() => {
    fetchWatches()
  }, [fetchWatches])

  // Create or update watch
  const handleSubmit = async (formData: VeilleFormData) => {
    if (!user?.id) return

    setIsSubmitting(true)

    try {
      const payload = {
        user_id: user.id,
        name: formData.name,
        subject: formData.subject,
        sector: formData.sector,
        report_type: formData.reportType,
        keywords: formData.keywords,
        schedule: formData.frequencyLabel,
        cron_expression: formData.cronExpression,
        recipients: formData.recipients,
        is_active: true
      }

      let response

      if (formData.id) {
        // Update existing
        response = await fetch(`${SCHEDULER_URL}/watches/${formData.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
      } else {
        // Create new
        response = await fetch(`${SCHEDULER_URL}/watches`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Erreur ${response.status}`)
      }

      setSheetOpen(false)
      setEditingWatch(null)
      fetchWatches()
    } catch (err) {
      console.error('Error saving watch:', err)
      setError(err instanceof Error ? err.message : 'Erreur lors de la sauvegarde')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Toggle watch active/inactive
  const toggleWatch = async (watchId: number) => {
    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}/toggle`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`)
      }

      // Update local state
      setWatches(prev => prev.map(w =>
        w.id === watchId ? { ...w, is_active: !w.is_active } : w
      ))
    } catch (err) {
      console.error('Error toggling watch:', err)
      setError('Erreur lors du changement de statut')
    }
  }

  // Trigger watch manually
  const triggerWatch = async (watchId: number) => {
    setTriggeringId(watchId)

    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}/trigger`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`)
      }

      // Optionally show success message
    } catch (err) {
      console.error('Error triggering watch:', err)
      setError('Erreur lors du déclenchement')
    } finally {
      setTriggeringId(null)
    }
  }

  // Delete watch
  const deleteWatch = async (watchId: number) => {
    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`)
      }

      setWatches(prev => prev.filter(w => w.id !== watchId))
      setDeleteConfirm(null)
    } catch (err) {
      console.error('Error deleting watch:', err)
      setError('Erreur lors de la suppression')
    }
  }

  // Fetch history
  const fetchHistory = async (watchId: number) => {
    setHistoryLoading(true)

    try {
      const response = await fetch(`${SCHEDULER_URL}/watches/${watchId}/history`)

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`)
      }

      const data = await response.json()
      setHistory(data)
    } catch (err) {
      console.error('Error fetching history:', err)
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }

  // Open edit mode
  const openEdit = (watch: Watch) => {
    setEditingWatch({
      id: watch.id,
      name: watch.name,
      subject: watch.subject,
      sector: watch.sector || '',
      reportType: watch.report_type || 'deep',
      keywords: watch.keywords || '',
      frequency: 'custom',
      frequencyLabel: watch.schedule || 'Personnalisé',
      time: '09:00',
      dayOfWeek: '1',
      dayOfMonth: '1',
      recipients: watch.recipients || '',
      cronExpression: watch.cron_expression
    })
    setSheetOpen(true)
  }

  // Open history modal
  const openHistory = (watch: Watch) => {
    setHistoryModal({ watchId: watch.id, watchName: watch.name })
    fetchHistory(watch.id)
  }

  // Filter watches
  const filteredWatches = watches.filter(watch => {
    const matchesSearch =
      watch.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      watch.subject.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'active' && watch.is_active) ||
      (statusFilter === 'inactive' && !watch.is_active)

    return matchesSearch && matchesStatus
  })

  // Stats
  const activeCount = watches.filter(w => w.is_active).length
  const inactiveCount = watches.filter(w => !w.is_active).length

  return (
    <MainLayout>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-8"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl gradient-icon-teal">
              <Bell className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground tracking-tight">
                {t('watches.title')}
              </h1>
              <p className="text-muted-foreground mt-1">
                {t('watches.subtitle')}
              </p>
            </div>
          </div>

          {/* Stats rapides */}
          <div className="hidden md:flex items-center gap-3">
            <Badge variant="outline" className="gap-2 py-2 px-4">
              <Clock className="w-4 h-4 text-primary" />
              {activeCount} {t('watches.active')}
            </Badge>
            <Badge variant="outline" className="gap-2 py-2 px-4">
              <Mail className="w-4 h-4 text-green-500" />
              {inactiveCount} {t('watches.inactive')}
            </Badge>
          </div>
        </div>
      </motion.div>

      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4 mb-6"
      >
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder={t('watches.search')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filter */}
        <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as typeof statusFilter)}>
          <SelectTrigger className="w-[160px]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t('watches.all')}</SelectItem>
            <SelectItem value="active">{t('watches.active')}</SelectItem>
            <SelectItem value="inactive">{t('watches.inactive')}</SelectItem>
          </SelectContent>
        </Select>

        {/* New Watch Button */}
        <Button onClick={() => { setEditingWatch(null); setSheetOpen(true) }}>
          <Plus className="w-4 h-4 mr-2" />
          {t('watches.new')}
        </Button>
      </motion.div>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mb-6 p-4 rounded-lg bg-destructive/10 border border-destructive/20 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-destructive" />
              <span className="text-destructive">{error}</span>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setError(null)}>
              <X className="w-4 h-4" />
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : filteredWatches.length === 0 ? (
          <div className="text-center py-20">
            <Bell className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              {watches.length === 0 ? t('watches.noWatches') : t('watches.noResults')}
            </h3>
            <p className="text-muted-foreground mb-6">
              {watches.length === 0 ? t('watches.noWatchesDescription') : t('watches.noResultsDescription')}
            </p>
            {watches.length === 0 && (
              <Button onClick={() => { setEditingWatch(null); setSheetOpen(true) }}>
                <Plus className="w-4 h-4 mr-2" />
                {t('watches.createFirst')}
              </Button>
            )}
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredWatches.map((watch, index) => (
              <motion.div
                key={watch.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <VeilleCard
                  id={watch.id}
                  title={watch.name}
                  description={watch.subject}
                  isActive={watch.is_active}
                  reportType={watch.report_type || 'Analyse Approfondie'}
                  sourceCount={5}
                  schedule={watch.schedule || 'Non planifié'}
                  recipients={watch.recipients?.split(',').filter(r => r.trim()).length || 0}
                  nextRun={watch.next_run}
                  tags={watch.keywords?.split(',').filter(k => k.trim()).slice(0, 3)}
                  onEdit={() => openEdit(watch)}
                  onToggle={() => toggleWatch(watch.id)}
                  onTrigger={() => triggerWatch(watch.id)}
                  onHistory={() => openHistory(watch)}
                  onDelete={() => setDeleteConfirm({ id: watch.id, name: watch.name })}
                  isTriggering={triggeringId === watch.id}
                />
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>

      {/* New/Edit Sheet */}
      <NewVeilleSheet
        open={sheetOpen}
        onOpenChange={setSheetOpen}
        editData={editingWatch}
        onSubmit={handleSubmit}
        isEditing={!!editingWatch}
      />

      {/* Delete Confirmation */}
      <AnimatePresence>
        {deleteConfirm && (
          <ConfirmDialog
            message={`${t('watches.deleteConfirm')} "${deleteConfirm.name}" ?`}
            onConfirm={() => deleteWatch(deleteConfirm.id)}
            onCancel={() => setDeleteConfirm(null)}
          />
        )}
      </AnimatePresence>

      {/* History Modal */}
      <AnimatePresence>
        {historyModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setHistoryModal(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-card border border-border rounded-xl w-full max-w-lg max-h-[80vh] overflow-hidden"
              onClick={e => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <div>
                  <h3 className="font-semibold text-foreground">{t('watches.history')}</h3>
                  <p className="text-sm text-muted-foreground">{historyModal.watchName}</p>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setHistoryModal(null)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>

              {/* Content */}
              <div className="p-4 overflow-y-auto max-h-[calc(80vh-80px)]">
                {historyLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  </div>
                ) : history.length === 0 ? (
                  <div className="text-center py-8">
                    <Calendar className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                    <p className="text-muted-foreground">{t('watches.noHistory')}</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {history.map((entry) => (
                      <div
                        key={entry.id}
                        className="flex items-start gap-3 p-3 rounded-lg bg-secondary/50"
                      >
                        {entry.status === 'success' ? (
                          <CheckCircle className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                        ) : entry.status === 'failure' ? (
                          <XCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
                        ) : (
                          <Loader2 className="w-5 h-5 text-primary animate-spin shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-medium text-foreground">
                              {entry.status === 'success' ? t('watches.executionSuccess') :
                               entry.status === 'failure' ? t('watches.executionFailed') :
                               t('watches.executionRunning')}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {new Date(entry.executed_at).toLocaleString()}
                            </span>
                          </div>
                          {entry.error_message && (
                            <p className="text-xs text-destructive mt-1">{entry.error_message}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </MainLayout>
  )
}

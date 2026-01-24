'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  Download,
  Trash2,
  Search,
  Filter,
  Calendar,
  ChevronDown,
  CheckSquare,
  Square,
  Archive
} from 'lucide-react'
import Navbar from '../components/Navbar'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { useTranslation } from '../context/LanguageContext'
import ConfirmDialog from '../components/ConfirmDialog'
import { Button } from '../components/ui/button'

interface Report {
  id: number
  title: string
  content: string
  analysis_type: string
  created_at: string
  user_id: number
}

interface GroupedReports {
  today: Report[]
  yesterday: Report[]
  lastWeek: Report[]
  lastMonth: Report[]
  older: Report[]
}

export default function ReportsHistoryPage() {
  const { t } = useTranslation()
  const { token, user, isLoading: authLoading } = useSupabaseAuth()
  const [reports, setReports] = useState<Report[]>([])
  const [filteredReports, setFilteredReports] = useState<Report[]>([])
  const [fetchingReports, setFetchingReports] = useState(false)
  const [hasFetched, setHasFetched] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedReports, setSelectedReports] = useState<Set<number>>(new Set())
  const [showFilters, setShowFilters] = useState(false)
  const [reportToDelete, setReportToDelete] = useState<number | null>(null)

  // Combined loading state: auth loading OR fetching reports (but not yet fetched)
  const loading = authLoading || (fetchingReports && !hasFetched)

  const analysisTypes = [
    { id: 'all', label: t('reports.allTypes') },
    { id: 'synthese_executive', label: t('analysis.types.synthese_executive') },
    { id: 'analyse_concurrentielle', label: t('analysis.types.analyse_concurrentielle') },
    { id: 'veille_technologique', label: t('analysis.types.veille_technologique') },
    { id: 'analyse_risques', label: t('analysis.types.analyse_risques') },
    { id: 'analyse_reglementaire', label: t('analysis.types.analyse_reglementaire') }
  ]

  useEffect(() => {
    // Only fetch when auth is ready and user is available
    if (!authLoading && user?.id && !hasFetched) {
      fetchReports()
    }
  }, [authLoading, user?.id, hasFetched])

  useEffect(() => {
    filterReports()
  }, [reports, searchQuery, selectedType])

  const fetchReports = async () => {
    try {
      setFetchingReports(true)
      const reportUrl = process.env.NEXT_PUBLIC_REPORT_URL || 'http://localhost:8004'
      // Pass user_id to filter reports by current user (Supabase UUID)
      const url = user?.id ? `${reportUrl}/reports?user_id=${user.id}` : `${reportUrl}/reports`
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setReports(data)
      }
    } catch (error) {
      console.error('Error fetching reports:', error)
    } finally {
      setFetchingReports(false)
      setHasFetched(true)
    }
  }

  const filterReports = () => {
    let filtered = [...reports]

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(report =>
        report.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Type filter
    if (selectedType !== 'all') {
      filtered = filtered.filter(report => report.analysis_type === selectedType)
    }

    setFilteredReports(filtered)
  }

  const groupReportsByTime = (reports: Report[]): GroupedReports => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const lastWeek = new Date(today)
    lastWeek.setDate(lastWeek.getDate() - 7)
    const lastMonth = new Date(today)
    lastMonth.setMonth(lastMonth.getMonth() - 1)

    const grouped: GroupedReports = {
      today: [],
      yesterday: [],
      lastWeek: [],
      lastMonth: [],
      older: []
    }

    reports.forEach(report => {
      const reportDate = new Date(report.created_at)

      if (reportDate >= today) {
        grouped.today.push(report)
      } else if (reportDate >= yesterday) {
        grouped.yesterday.push(report)
      } else if (reportDate >= lastWeek) {
        grouped.lastWeek.push(report)
      } else if (reportDate >= lastMonth) {
        grouped.lastMonth.push(report)
      } else {
        grouped.older.push(report)
      }
    })

    return grouped
  }

  const handleDownloadPdf = async (reportId: number, title: string) => {
    try {
      const reportUrl = process.env.NEXT_PUBLIC_REPORT_URL || 'http://localhost:8004'
      // Pass user_id to verify ownership (Supabase UUID)
      const url = user?.id
        ? `${reportUrl}/export/${reportId}?user_id=${user.id}`
        : `${reportUrl}/export/${reportId}`
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${title}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error downloading PDF:', error)
    }
  }

  const handleDeleteReport = async (reportId: number) => {
    try {
      const reportUrl = process.env.NEXT_PUBLIC_REPORT_URL || 'http://localhost:8004'
      // Pass user_id to verify ownership (Supabase UUID)
      const url = user?.id
        ? `${reportUrl}/reports/${reportId}?user_id=${user.id}`
        : `${reportUrl}/reports/${reportId}`
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setReports(reports.filter(r => r.id !== reportId))
        setSelectedReports(prev => {
          const newSet = new Set(prev)
          newSet.delete(reportId)
          return newSet
        })
      }
    } catch (error) {
      console.error('Error deleting report:', error)
    } finally {
      setReportToDelete(null)
    }
  }

  const toggleReportSelection = (reportId: number) => {
    setSelectedReports(prev => {
      const newSet = new Set(prev)
      if (newSet.has(reportId)) {
        newSet.delete(reportId)
      } else {
        newSet.add(reportId)
      }
      return newSet
    })
  }

  const toggleSelectAll = () => {
    if (selectedReports.size === filteredReports.length) {
      setSelectedReports(new Set())
    } else {
      setSelectedReports(new Set(filteredReports.map(r => r.id)))
    }
  }

  const handleExportSelected = async () => {
    for (const reportId of selectedReports) {
      const report = reports.find(r => r.id === reportId)
      if (report) {
        await handleDownloadPdf(reportId, report.title)
        // Small delay between downloads to avoid browser blocking
        await new Promise(resolve => setTimeout(resolve, 500))
      }
    }
  }

  const groupedReports = groupReportsByTime(filteredReports)
  const hasReports = filteredReports.length > 0

  const ReportCard = ({ report }: { report: Report }) => {
    const isSelected = selectedReports.has(report.id)
    const analysisTypeName = analysisTypes.find(t => t.id === report.analysis_type)?.label || report.analysis_type
    const createdDate = new Date(report.created_at).toLocaleString()
    const preview = report.content.substring(0, 200) + (report.content.length > 200 ? '...' : '')

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className={`glass-card hover:border-cyan-500/30 transition-all cursor-pointer ${
          isSelected ? 'border-cyan-500/50 bg-cyan-500/5' : ''
        }`}
      >
        <div className="flex gap-4">
          {/* Selection checkbox */}
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation()
              toggleReportSelection(report.id)
            }}
            className="flex-shrink-0 mt-1 h-6 w-6"
          >
            {isSelected ? (
              <CheckSquare className="w-5 h-5 text-cyan-400" />
            ) : (
              <Square className="w-5 h-5 text-gray-400 hover:text-cyan-400" />
            )}
          </Button>

          {/* Report icon */}
          <div className="flex-shrink-0">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
          </div>

          {/* Report content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4 mb-2">
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-white truncate mb-1">
                  {report.title}
                </h3>
                <div className="flex items-center gap-3 text-sm text-gray-400">
                  <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400">
                    {analysisTypeName}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {createdDate}
                  </span>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDownloadPdf(report.id, report.title)
                  }}
                  title={t('reports.downloadPdf')}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <Download className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation()
                    setReportToDelete(report.id)
                  }}
                  title={t('reports.deleteReport')}
                  className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Preview */}
            <p className="text-sm text-gray-400 mt-2 line-clamp-2">
              {preview}
            </p>
          </div>
        </div>
      </motion.div>
    )
  }

  const TimeSection = ({ title, reports }: { title: string; reports: Report[] }) => {
    if (reports.length === 0) return null

    return (
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
          {title}
          <span className="text-sm text-gray-400 font-normal">({reports.length})</span>
        </h3>
        <div className="space-y-3">
          {reports.map(report => (
            <ReportCard key={report.id} report={report} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen w-full">
      <Navbar />

      <main className="pt-24 px-4 pb-6 w-full">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="glass-card mb-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  {t('reports.title')}
                </h1>
                <p className="text-gray-400">{t('reports.subtitle')}</p>
              </div>

              {selectedReports.size > 0 && (
                <motion.button
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  onClick={handleExportSelected}
                  className="glass-button flex items-center gap-2"
                >
                  <Archive className="w-4 h-4" />
                  {t('reports.exportSelected')} ({selectedReports.size})
                </motion.button>
              )}
            </div>

            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('reports.searchPlaceholder')}
                  className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500/50"
                />
              </div>

              {/* Filter by type */}
              <div className="relative">
                <Button
                  variant="outline"
                  onClick={() => setShowFilters(!showFilters)}
                  className="w-full sm:w-auto justify-between"
                >
                  <Filter className="w-4 h-4" />
                  {analysisTypes.find(t => t.id === selectedType)?.label}
                  <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
                </Button>

                <AnimatePresence>
                  {showFilters && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 top-full mt-2 w-64 glass-card z-50"
                    >
                      {analysisTypes.map(type => (
                        <Button
                          key={type.id}
                          variant="ghost"
                          onClick={() => {
                            setSelectedType(type.id)
                            setShowFilters(false)
                          }}
                          className={`w-full text-left px-3 py-2 text-sm h-auto justify-start font-normal ${
                            selectedType === type.id
                              ? 'bg-cyan-500/20 text-cyan-400'
                              : 'text-gray-300 hover:bg-white/10'
                          }`}
                        >
                          {type.label}
                        </Button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Select/Deselect all */}
              {hasReports && (
                <Button
                  variant="outline"
                  onClick={toggleSelectAll}
                >
                  {selectedReports.size === filteredReports.length ? (
                    <>
                      <CheckSquare className="w-4 h-4" />
                      {t('reports.deselectAll')}
                    </>
                  ) : (
                    <>
                      <Square className="w-4 h-4" />
                      {t('reports.selectAll')}
                    </>
                  )}
                </Button>
              )}
            </div>
          </motion.div>

          {/* Reports list */}
          {loading ? (
            <div className="glass-card text-center py-12">
              <div className="inline-block w-8 h-8 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-400">{t('common.loading')}</p>
            </div>
          ) : !hasReports ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card text-center py-12"
            >
              <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                {t('reports.noReports')}
              </h3>
              <p className="text-gray-400">{t('reports.noReportsDesc')}</p>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <TimeSection title={t('reports.today')} reports={groupedReports.today} />
              <TimeSection title={t('reports.yesterday')} reports={groupedReports.yesterday} />
              <TimeSection title={t('reports.lastWeek')} reports={groupedReports.lastWeek} />
              <TimeSection title={t('reports.lastMonth')} reports={groupedReports.lastMonth} />
              <TimeSection title={t('reports.older')} reports={groupedReports.older} />
            </motion.div>
          )}
        </div>
      </main>

      {/* Delete confirmation dialog */}
      {reportToDelete && (
        <ConfirmDialog
          message={t('reports.deleteConfirm')}
          onConfirm={() => handleDeleteReport(reportToDelete)}
          onCancel={() => setReportToDelete(null)}
        />
      )}

      {/* Click outside to close filters */}
      {showFilters && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowFilters(false)}
        />
      )}
    </div>
  )
}

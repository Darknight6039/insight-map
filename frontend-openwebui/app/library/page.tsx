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
  Clock,
  Briefcase,
  Bell,
  Loader2
} from 'lucide-react'
import MainLayout from '../components/layout/MainLayout'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { useTranslation } from '../context/LanguageContext'
import ConfirmDialog from '../components/ConfirmDialog'
import { Card, CardContent } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { cn } from '@/lib/utils'

interface Document {
  id: number
  user_id: number
  document_type: string
  title: string
  content: string | null
  file_path: string | null
  analysis_type: string | null
  business_type: string | null
  report_id: number | null
  watch_id: number | null
  extra_data: Record<string, any>
  created_at: string
}

interface DocumentListResponse {
  total: number
  skip: number
  limit: number
  documents: Document[]
}

export default function DocumentLibraryPage() {
  const { token } = useSupabaseAuth()
  const { t } = useTranslation()
  const [documents, setDocuments] = useState<Document[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedAnalysisType, setSelectedAnalysisType] = useState('all')
  const [showFilters, setShowFilters] = useState(false)
  const [documentToDelete, setDocumentToDelete] = useState<number | null>(null)

  const documentTypes = [
    { id: 'all', label: t('library.all'), icon: null },
    { id: 'report', label: t('library.reports'), icon: FileText },
    { id: 'watch', label: t('library.watches'), icon: Bell }
  ]

  const analysisTypes = [
    { id: 'all', label: t('library.allTypes') },
    { id: 'synthese_executive', label: t('analysis.types.synthese_executive') },
    { id: 'analyse_concurrentielle', label: t('analysis.types.analyse_concurrentielle') },
    { id: 'veille_technologique', label: t('analysis.types.veille_technologique') },
    { id: 'analyse_risques', label: t('analysis.types.analyse_risques') },
    { id: 'analyse_reglementaire', label: t('analysis.types.analyse_reglementaire') }
  ]

  useEffect(() => {
    if (token) {
      fetchDocuments()
    }
  }, [token])

  useEffect(() => {
    filterDocuments()
  }, [documents, searchQuery, selectedType, selectedAnalysisType])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      const response = await fetch(`${apiUrl}/api/memory/documents?limit=100`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data: DocumentListResponse = await response.json()
        setDocuments(data.documents)
      } else {
        console.error('Failed to fetch documents:', response.statusText)
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterDocuments = () => {
    let filtered = [...documents]

    if (searchQuery) {
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (doc.content && doc.content.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(doc => doc.document_type === selectedType)
    }

    if (selectedAnalysisType !== 'all') {
      filtered = filtered.filter(doc => doc.analysis_type === selectedAnalysisType)
    }

    filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    setFilteredDocuments(filtered)
  }

  const handleDelete = async (id: number) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      const response = await fetch(`${apiUrl}/api/memory/documents/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setDocuments(documents.filter(d => d.id !== id))
        setDocumentToDelete(null)
      }
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }

  const handleDownload = async (doc: Document) => {
    if (!doc.report_id) return

    try {
      const reportUrl = process.env.NEXT_PUBLIC_REPORT_URL || 'http://localhost:8004'
      const response = await fetch(`${reportUrl}/export/${doc.report_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${doc.title}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error downloading document:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return t('library.today')
    if (days === 1) return t('library.yesterday')
    if (days < 7) return t('library.daysAgo').replace('{days}', String(days))
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  const truncateText = (text: string, maxLength: number = 200) => {
    if (!text || text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  const groupDocumentsByDate = () => {
    const groups: Record<string, Document[]> = {
      today: [],
      yesterday: [],
      lastWeek: [],
      lastMonth: [],
      older: []
    }

    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
    const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)

    filteredDocuments.forEach(doc => {
      const docDate = new Date(doc.created_at)
      if (docDate >= today) groups.today.push(doc)
      else if (docDate >= yesterday) groups.yesterday.push(doc)
      else if (docDate >= lastWeek) groups.lastWeek.push(doc)
      else if (docDate >= lastMonth) groups.lastMonth.push(doc)
      else groups.older.push(doc)
    })

    return groups
  }

  const groupedDocs = groupDocumentsByDate()

  const renderDocumentGroup = (title: string, docs: Document[]) => {
    if (docs.length === 0) return null

    return (
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-primary" />
          {title}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {docs.map(doc => (
            <Card
              key={doc.id}
              className="group card-interactive"
            >
              <CardContent className="p-5">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className={cn(
                    "p-2 rounded-lg",
                    doc.document_type === 'report'
                      ? "gradient-icon-blue"
                      : "gradient-icon-orange"
                  )}>
                    {doc.document_type === 'report'
                      ? <FileText className="w-5 h-5 text-white" />
                      : <Bell className="w-5 h-5 text-white" />
                    }
                  </div>
                  <div className="flex gap-1">
                    {doc.report_id && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDownload(doc)}
                        className="h-8 w-8 text-muted-foreground hover:text-primary"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDocumentToDelete(doc.id)}
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Title */}
                <h4 className="text-foreground font-semibold mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                  {doc.title}
                </h4>

                {/* Metadata */}
                <div className="flex flex-wrap gap-2 mb-3">
                  <Badge variant={doc.document_type === 'report' ? 'default' : 'secondary'}>
                    {doc.document_type === 'report' ? t('library.report') : t('library.watch')}
                  </Badge>
                  {doc.analysis_type && (
                    <Badge variant="outline">
                      {doc.analysis_type.replace(/_/g, ' ')}
                    </Badge>
                  )}
                </div>

                {/* Content Preview */}
                {doc.content && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-3">
                    {truncateText(doc.content)}
                  </p>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between text-xs text-muted-foreground pt-3 border-t border-border">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatDate(doc.created_at)}
                  </div>
                  {doc.business_type && (
                    <div className="flex items-center gap-1">
                      <Briefcase className="w-3 h-3" />
                      {doc.business_type}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <MainLayout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 rounded-xl gradient-icon-purple">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              {t('library.title')}
            </h1>
            <p className="text-muted-foreground">
              {t('library.subtitle')
                .replace('{total}', String(documents.length))
                .replace('{reports}', String(filteredDocuments.filter(d => d.document_type === 'report').length))
                .replace('{watches}', String(filteredDocuments.filter(d => d.document_type === 'watch').length))}
            </p>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('library.searchPlaceholder')}
            className="pl-12"
          />
        </div>

        {/* Type Filters */}
        <div className="flex items-center gap-3 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="gap-2"
          >
            <Filter className="w-4 h-4" />
            {t('library.filters')}
            <ChevronDown className={cn("w-4 h-4 transition-transform", showFilters && "rotate-180")} />
          </Button>

          {documentTypes.map((type) => (
            <Button
              key={type.id}
              variant={selectedType === type.id ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedType(type.id)}
              className="gap-2"
            >
              {type.icon && <type.icon className="w-4 h-4" />}
              {type.label}
            </Button>
          ))}
        </div>

        {/* Analysis Type Filters */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-2 flex-wrap"
            >
              {analysisTypes.map((type) => (
                <Button
                  key={type.id}
                  variant={selectedAnalysisType === type.id ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedAnalysisType(type.id)}
                >
                  {type.label}
                </Button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-12 h-12 animate-spin text-primary" />
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="text-center py-20">
          <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground text-lg">
            {searchQuery || selectedType !== 'all' || selectedAnalysisType !== 'all'
              ? t('library.noDocumentsFiltered')
              : t('library.noDocuments')}
          </p>
        </div>
      ) : (
        <div>
          {renderDocumentGroup(t('library.today'), groupedDocs.today)}
          {renderDocumentGroup(t('library.yesterday'), groupedDocs.yesterday)}
          {renderDocumentGroup(t('library.thisWeek'), groupedDocs.lastWeek)}
          {renderDocumentGroup(t('library.thisMonth'), groupedDocs.lastMonth)}
          {renderDocumentGroup(t('library.older'), groupedDocs.older)}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {documentToDelete && (
        <ConfirmDialog
          title={t('library.deleteDocument')}
          message={t('library.deleteConfirm')}
          onConfirm={() => handleDelete(documentToDelete)}
          onCancel={() => setDocumentToDelete(null)}
          confirmText={t('library.confirmDelete')}
          cancelText={t('library.cancelDelete')}
        />
      )}
    </MainLayout>
  )
}

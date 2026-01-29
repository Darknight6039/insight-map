'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare,
  Trash2,
  Search,
  Filter,
  ChevronDown,
  Clock,
  Brain,
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

interface Conversation {
  id: number
  user_id: number
  query: string
  response: string
  conversation_type: string
  analysis_type: string | null
  business_type: string | null
  created_at: string
}

interface ConversationListResponse {
  total: number
  skip: number
  limit: number
  conversations: Conversation[]
}

export default function ConversationHistoryPage() {
  const { token } = useSupabaseAuth()
  const { t } = useTranslation()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [filteredConversations, setFilteredConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [showFilters, setShowFilters] = useState(false)
  const [conversationToDelete, setConversationToDelete] = useState<number | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const conversationTypes = [
    { id: 'all', label: t('history.allTypes') },
    { id: 'chat', label: t('history.chat') },
    { id: 'analysis', label: t('history.analysis') }
  ]

  useEffect(() => {
    if (token) {
      fetchConversations()
    }
  }, [token])

  useEffect(() => {
    filterConversations()
  }, [conversations, searchQuery, selectedType])

  const fetchConversations = async () => {
    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      const response = await fetch(`${apiUrl}/api/memory/conversations?limit=100`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data: ConversationListResponse = await response.json()
        setConversations(data.conversations)
      } else {
        console.error('Failed to fetch conversations:', response.statusText)
      }
    } catch (error) {
      console.error('Error fetching conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterConversations = () => {
    let filtered = [...conversations]

    if (searchQuery) {
      filtered = filtered.filter(conv =>
        conv.query.toLowerCase().includes(searchQuery.toLowerCase()) ||
        conv.response.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(conv => conv.conversation_type === selectedType)
    }

    filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    setFilteredConversations(filtered)
  }

  const handleDelete = async (id: number) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      const response = await fetch(`${apiUrl}/api/memory/conversations/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setConversations(conversations.filter(c => c.id !== id))
        setConversationToDelete(null)
      }
    } catch (error) {
      console.error('Error deleting conversation:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (hours < 1) return t('history.aFewMinutesAgo')
    if (hours < 24) return t('history.hoursAgo').replace('{count}', String(hours))
    if (days === 1) return t('history.yesterday')
    if (days < 7) return t('history.daysAgo').replace('{count}', String(days))
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  const truncateText = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <MainLayout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 rounded-xl gradient-icon-violet">
            <MessageSquare className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              {t('history.title')}
            </h1>
            <p className="text-muted-foreground">
              {t('history.subtitle').replace('{count}', String(conversations.length))}
            </p>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('history.searchPlaceholder')}
            className="pl-12"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-3 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="gap-2"
          >
            <Filter className="w-4 h-4" />
            {t('history.filters')}
            <ChevronDown className={cn("w-4 h-4 transition-transform", showFilters && "rotate-180")} />
          </Button>

          {conversationTypes.map((type) => (
            <Button
              key={type.id}
              variant={selectedType === type.id ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedType(type.id)}
            >
              {type.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Conversations List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-12 h-12 animate-spin text-primary" />
        </div>
      ) : filteredConversations.length === 0 ? (
        <div className="text-center py-20">
          <MessageSquare className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground text-lg">
            {searchQuery || selectedType !== 'all'
              ? t('history.noConversationsFiltered')
              : t('history.noConversations')}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <AnimatePresence>
            {filteredConversations.map((conversation) => (
              <motion.div
                key={conversation.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card className="card-interactive">
                  <CardContent className="p-6">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3 flex-1">
                        <div className={cn(
                          "p-2 rounded-lg",
                          conversation.conversation_type === 'analysis'
                            ? "gradient-icon-purple"
                            : "gradient-icon-blue"
                        )}>
                          {conversation.conversation_type === 'analysis'
                            ? <Brain className="w-4 h-4 text-white" />
                            : <MessageSquare className="w-4 h-4 text-white" />
                          }
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant={conversation.conversation_type === 'analysis' ? 'default' : 'secondary'}>
                              {conversation.conversation_type === 'analysis' ? t('history.analysis') : t('history.chat')}
                            </Badge>
                            {conversation.analysis_type && (
                              <Badge variant="outline">
                                {conversation.analysis_type.replace(/_/g, ' ')}
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            {formatDate(conversation.created_at)}
                          </div>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setConversationToDelete(conversation.id)}
                        className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Query */}
                    <div className="mb-3">
                      <div className="text-sm text-muted-foreground mb-1 font-medium">{t('history.question')}</div>
                      <div className="text-foreground">
                        {expandedId === conversation.id
                          ? conversation.query
                          : truncateText(conversation.query)}
                      </div>
                    </div>

                    {/* Response */}
                    <div className="mb-3">
                      <div className="text-sm text-muted-foreground mb-1 font-medium">{t('history.response')}</div>
                      <div className="text-muted-foreground text-sm">
                        {expandedId === conversation.id
                          ? conversation.response
                          : truncateText(conversation.response, 200)}
                      </div>
                    </div>

                    {/* Expand/Collapse */}
                    {(conversation.query.length > 150 || conversation.response.length > 200) && (
                      <Button
                        variant="link"
                        size="sm"
                        onClick={() => setExpandedId(expandedId === conversation.id ? null : conversation.id)}
                        className="p-0 h-auto text-primary"
                      >
                        {expandedId === conversation.id ? t('history.showLess') : t('history.showMore')}
                      </Button>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {conversationToDelete && (
        <ConfirmDialog
          title={t('history.deleteConversation')}
          message={t('history.deleteConfirm')}
          onConfirm={() => handleDelete(conversationToDelete)}
          onCancel={() => setConversationToDelete(null)}
          confirmText={t('history.confirmDelete')}
          cancelText={t('history.cancelDelete')}
        />
      )}
    </MainLayout>
  )
}

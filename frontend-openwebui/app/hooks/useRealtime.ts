'use client'

/**
 * =============================================================================
 * Real-time Hooks pour Supabase
 * =============================================================================
 * Ces hooks permettent d'écouter les changements en temps réel sur les tables.
 */

import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js'

// =============================================================================
// TYPES
// =============================================================================

type PostgresChangeEvent = 'INSERT' | 'UPDATE' | 'DELETE' | '*'

interface RealtimeConfig<T> {
  table: string
  schema?: string
  event?: PostgresChangeEvent
  filter?: string
  onInsert?: (payload: T) => void
  onUpdate?: (payload: { old: T; new: T }) => void
  onDelete?: (payload: T) => void
  onChange?: (payload: RealtimePostgresChangesPayload<T>) => void
}

// =============================================================================
// GENERIC REALTIME HOOK
// =============================================================================

/**
 * Hook générique pour écouter les changements sur une table
 */
export function useRealtimeSubscription<T = any>(config: RealtimeConfig<T>) {
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const {
      table,
      schema = 'public',
      event = '*',
      filter,
      onInsert,
      onUpdate,
      onDelete,
      onChange,
    } = config

    const channelName = `realtime-${table}-${Date.now()}`

    const channel = supabase
      .channel(channelName)
      .on(
        'postgres_changes' as any,
        {
          event,
          schema,
          table,
          ...(filter ? { filter } : {}),
        },
        (payload: RealtimePostgresChangesPayload<T>) => {
          console.log(`Realtime event on ${table}:`, payload.eventType)

          // Callback générique
          if (onChange) {
            onChange(payload)
          }

          // Callbacks spécifiques
          switch (payload.eventType) {
            case 'INSERT':
              if (onInsert) onInsert(payload.new as T)
              break
            case 'UPDATE':
              if (onUpdate) onUpdate({ old: payload.old as T, new: payload.new as T })
              break
            case 'DELETE':
              if (onDelete) onDelete(payload.old as T)
              break
          }
        }
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          setIsSubscribed(true)
          console.log(`Subscribed to ${table} changes`)
        } else if (status === 'CHANNEL_ERROR') {
          setError(new Error(`Failed to subscribe to ${table}`))
        }
      })

    return () => {
      console.log(`Unsubscribing from ${table}`)
      supabase.removeChannel(channel)
      setIsSubscribed(false)
    }
  }, [config.table, config.filter])

  return { isSubscribed, error }
}

// =============================================================================
// SPECIALIZED HOOKS
// =============================================================================

/**
 * Hook pour écouter les nouvelles conversations en temps réel
 */
export function useRealtimeConversations(
  userId: string | null,
  onNewConversation?: (conversation: any) => void
) {
  const [conversations, setConversations] = useState<any[]>([])

  const handleInsert = useCallback((newConversation: any) => {
    setConversations((prev) => [newConversation, ...prev])
    if (onNewConversation) {
      onNewConversation(newConversation)
    }
  }, [onNewConversation])

  const { isSubscribed, error } = useRealtimeSubscription({
    table: 'user_conversations',
    event: 'INSERT',
    filter: userId ? `user_id=eq.${userId}` : undefined,
    onInsert: handleInsert,
  })

  return {
    conversations,
    setConversations,
    isSubscribed,
    error,
  }
}

/**
 * Hook pour écouter les nouveaux documents en temps réel
 */
export function useRealtimeDocuments(
  userId: string | null,
  onNewDocument?: (document: any) => void
) {
  const [documents, setDocuments] = useState<any[]>([])

  const handleInsert = useCallback((newDocument: any) => {
    setDocuments((prev) => [newDocument, ...prev])
    if (onNewDocument) {
      onNewDocument(newDocument)
    }
  }, [onNewDocument])

  const { isSubscribed, error } = useRealtimeSubscription({
    table: 'user_documents',
    event: 'INSERT',
    filter: userId ? `user_id=eq.${userId}` : undefined,
    onInsert: handleInsert,
  })

  return {
    documents,
    setDocuments,
    isSubscribed,
    error,
  }
}

/**
 * Hook pour écouter les exécutions de veilles en temps réel
 */
export function useRealtimeWatchHistory(
  userId: string | null,
  onWatchExecuted?: (execution: any) => void
) {
  const [executions, setExecutions] = useState<any[]>([])

  const handleInsert = useCallback((newExecution: any) => {
    setExecutions((prev) => [newExecution, ...prev])
    if (onWatchExecuted) {
      onWatchExecuted(newExecution)
    }
  }, [onWatchExecuted])

  const { isSubscribed, error } = useRealtimeSubscription({
    table: 'watch_history',
    event: 'INSERT',
    filter: userId ? `user_id=eq.${userId}` : undefined,
    onInsert: handleInsert,
  })

  return {
    executions,
    setExecutions,
    isSubscribed,
    error,
  }
}

/**
 * Hook pour le dashboard admin - écoute toutes les activités
 */
export function useRealtimeActivityLogs(onNewActivity?: (activity: any) => void) {
  const [activities, setActivities] = useState<any[]>([])

  const handleInsert = useCallback((newActivity: any) => {
    setActivities((prev) => [newActivity, ...prev.slice(0, 99)]) // Garde les 100 dernières
    if (onNewActivity) {
      onNewActivity(newActivity)
    }
  }, [onNewActivity])

  const { isSubscribed, error } = useRealtimeSubscription({
    table: 'activity_logs',
    event: 'INSERT',
    onInsert: handleInsert,
  })

  return {
    activities,
    setActivities,
    isSubscribed,
    error,
  }
}

/**
 * Hook pour écouter les changements sur les configurations de veilles
 */
export function useRealtimeWatchConfigs(
  userId: string | null,
  callbacks?: {
    onUpdate?: (watch: any) => void
    onDelete?: (watch: any) => void
  }
) {
  const { isSubscribed, error } = useRealtimeSubscription({
    table: 'watch_configs',
    event: '*',
    filter: userId ? `user_id=eq.${userId}` : undefined,
    onUpdate: callbacks?.onUpdate ? ({ new: watch }) => callbacks.onUpdate!(watch) : undefined,
    onDelete: callbacks?.onDelete,
  })

  return { isSubscribed, error }
}

// =============================================================================
// NOTIFICATION HELPERS
// =============================================================================

/**
 * Hook combiné pour les notifications utilisateur
 * Écoute les nouveaux documents et les exécutions de veilles
 */
export function useUserNotifications(userId: string | null) {
  const [notifications, setNotifications] = useState<Array<{
    id: string
    type: 'document' | 'watch_execution'
    title: string
    message: string
    timestamp: Date
    read: boolean
  }>>([])

  // Écouter les nouveaux documents
  useRealtimeDocuments(userId, (document) => {
    setNotifications((prev) => [
      {
        id: `doc-${document.id}`,
        type: 'document',
        title: 'Nouveau document',
        message: document.title || 'Un nouveau document est disponible',
        timestamp: new Date(),
        read: false,
      },
      ...prev,
    ])
  })

  // Écouter les exécutions de veilles
  useRealtimeWatchHistory(userId, (execution) => {
    const isSuccess = execution.status === 'success'
    setNotifications((prev) => [
      {
        id: `watch-${execution.id}`,
        type: 'watch_execution',
        title: isSuccess ? 'Veille exécutée' : 'Erreur de veille',
        message: isSuccess
          ? 'Votre veille automatique a été exécutée avec succès'
          : `Erreur: ${execution.error_message || 'Une erreur est survenue'}`,
        timestamp: new Date(),
        read: false,
      },
      ...prev,
    ])
  })

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    )
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }, [])

  const clearNotifications = useCallback(() => {
    setNotifications([])
  }, [])

  const unreadCount = notifications.filter((n) => !n.read).length

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    clearNotifications,
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  useRealtimeSubscription,
  useRealtimeConversations,
  useRealtimeDocuments,
  useRealtimeWatchHistory,
  useRealtimeActivityLogs,
  useRealtimeWatchConfigs,
  useUserNotifications,
}

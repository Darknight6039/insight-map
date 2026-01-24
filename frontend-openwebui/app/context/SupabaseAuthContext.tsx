'use client'

/**
 * =============================================================================
 * Supabase Auth Context
 * =============================================================================
 * Ce contexte remplace AuthContext.tsx et gère l'authentification via Supabase.
 * Inclut la gestion automatique des sessions et le rafraîchissement des tokens.
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import {
  supabase,
  SupabaseUser,
  extractUserFromSession,
  signInWithEmail,
  signUpWithEmail,
  signOut as supabaseSignOut,
  isAdmin as checkIsAdmin,
} from '../lib/supabase'
import type { Session, AuthChangeEvent } from '@supabase/supabase-js'

// =============================================================================
// TYPES
// =============================================================================

interface SupabaseAuthContextType {
  user: SupabaseUser | null
  session: Session | null
  token: string | null  // For backward compatibility with legacy API calls
  isLoading: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  error: string | null

  // Actions
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, fullName: string, invitationCode: string) => Promise<void>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
  clearError: () => void
}

// =============================================================================
// CONTEXT
// =============================================================================

const SupabaseAuthContext = createContext<SupabaseAuthContextType | undefined>(undefined)

// Routes publiques (pas besoin d'être connecté)
const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password', '/reset-password']

// =============================================================================
// PROVIDER
// =============================================================================

export function SupabaseAuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const router = useRouter()
  const pathname = usePathname()

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname || '')
  const isAuthenticated = !!user
  const isAdmin = checkIsAdmin(user)

  // ---------------------------------------------------------------------------
  // Session Management
  // ---------------------------------------------------------------------------

  const handleSession = useCallback((newSession: Session | null) => {
    if (newSession) {
      setSession(newSession as any)
      const extractedUser = extractUserFromSession(newSession)
      setUser(extractedUser)
    } else {
      setSession(null)
      setUser(null)
    }
  }, [])

  // Initialisation et écoute des changements d'état d'authentification
  useEffect(() => {
    let mounted = true

    // Récupérer la session initiale
    const initializeAuth = async () => {
      try {
        const { data: { session: initialSession } } = await supabase.auth.getSession()

        if (mounted) {
          handleSession(initialSession)
          setIsLoading(false)
        }
      } catch (err) {
        console.error('Error initializing auth:', err)
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    initializeAuth()

    // Écouter les changements d'authentification
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, newSession: Session | null) => {
        console.log('Auth state changed:', event)

        if (mounted) {
          handleSession(newSession)

          // Actions spécifiques selon l'événement
          switch (event) {
            case 'SIGNED_IN':
              // Rediriger vers la page d'accueil si on est sur une page publique
              if (isPublicRoute) {
                router.push('/')
              }
              break

            case 'SIGNED_OUT':
              // Rediriger vers login
              router.push('/login')
              break

            case 'TOKEN_REFRESHED':
              console.log('Token refreshed successfully')
              break

            case 'USER_UPDATED':
              // Rafraîchir les données utilisateur
              if (newSession) {
                const updatedUser = extractUserFromSession(newSession)
                setUser(updatedUser)
              }
              break
          }
        }
      }
    )

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [handleSession, router, isPublicRoute])

  // Redirection basée sur l'état d'authentification
  useEffect(() => {
    if (!isLoading) {
      if (!user && !isPublicRoute) {
        // Utilisateur non connecté sur une route protégée
        router.push('/login')
      } else if (user && isPublicRoute && pathname !== '/reset-password') {
        // Utilisateur connecté sur une route publique (sauf reset-password)
        router.push('/')
      }
    }
  }, [user, isLoading, isPublicRoute, router, pathname])

  // ---------------------------------------------------------------------------
  // Auth Actions
  // ---------------------------------------------------------------------------

  const signIn = async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const { session: newSession } = await signInWithEmail(email, password)
      handleSession(newSession)
      router.push('/')
    } catch (err: any) {
      console.error('Sign in error:', err)
      setError(err.message || 'Erreur lors de la connexion')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const signUp = async (
    email: string,
    password: string,
    fullName: string,
    invitationCode: string
  ) => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await signUpWithEmail(email, password, fullName, invitationCode)

      // Si on a reçu une session, l'utiliser
      if (data.access_token) {
        const { data: { session: newSession } } = await supabase.auth.getSession()
        handleSession(newSession)
      }

      router.push('/')
    } catch (err: any) {
      console.error('Sign up error:', err)
      setError(err.message || 'Erreur lors de l\'inscription')
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const signOut = async () => {
    setIsLoading(true)
    setError(null)

    try {
      await supabaseSignOut()
      setUser(null)
      setSession(null)
      router.push('/login')
    } catch (err: any) {
      console.error('Sign out error:', err)
      setError(err.message || 'Erreur lors de la déconnexion')
    } finally {
      setIsLoading(false)
    }
  }

  const refreshUser = async () => {
    try {
      const { data: { session: refreshedSession } } = await supabase.auth.refreshSession()
      handleSession(refreshedSession)
    } catch (err) {
      console.error('Error refreshing user:', err)
    }
  }

  const clearError = () => setError(null)

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const value: SupabaseAuthContextType = {
    user,
    session: session as any,
    token: session?.access_token || null,  // For backward compatibility
    isLoading,
    isAuthenticated,
    isAdmin,
    error,
    signIn,
    signUp,
    signOut,
    refreshUser,
    clearError,
  }

  return (
    <SupabaseAuthContext.Provider value={value}>
      {children}
    </SupabaseAuthContext.Provider>
  )
}

// =============================================================================
// HOOK
// =============================================================================

export function useSupabaseAuth() {
  const context = useContext(SupabaseAuthContext)
  if (context === undefined) {
    throw new Error('useSupabaseAuth must be used within a SupabaseAuthProvider')
  }
  return context
}

// =============================================================================
// HOC pour protéger les composants (optionnel)
// =============================================================================

export function withSupabaseAuth<P extends object>(
  Component: React.ComponentType<P>,
  requireAdmin: boolean = false
) {
  return function ProtectedComponent(props: P) {
    const { user, isLoading, isAdmin } = useSupabaseAuth()
    const router = useRouter()

    useEffect(() => {
      if (!isLoading) {
        if (!user) {
          router.push('/login')
        } else if (requireAdmin && !isAdmin) {
          router.push('/')
        }
      }
    }, [user, isLoading, isAdmin, router])

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )
    }

    if (!user || (requireAdmin && !isAdmin)) {
      return null
    }

    return <Component {...props} />
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

export default SupabaseAuthContext

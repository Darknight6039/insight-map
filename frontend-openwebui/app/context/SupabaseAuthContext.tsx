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

  // Onboarding status
  onboardingCompleted: boolean | null
  isCheckingOnboarding: boolean

  // Actions
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, fullName: string, invitationCode: string) => Promise<void>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
  refreshOnboardingStatus: () => Promise<boolean | null>
  skipOnboarding: () => Promise<boolean>
  clearError: () => void
}

// =============================================================================
// CONTEXT
// =============================================================================

const SupabaseAuthContext = createContext<SupabaseAuthContextType | undefined>(undefined)

// Routes publiques (pas besoin d'être connecté)
const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password', '/reset-password', '/onboarding']

// =============================================================================
// PROVIDER
// =============================================================================

export function SupabaseAuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<SupabaseUser | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Onboarding status tracking
  const [onboardingCompleted, setOnboardingCompleted] = useState<boolean | null>(null)
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false)

  const router = useRouter()
  const pathname = usePathname()

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname || '')
  const isAuthenticated = !!user
  const isAdmin = checkIsAdmin(user)

  // ---------------------------------------------------------------------------
  // Onboarding Status Check
  // ---------------------------------------------------------------------------

  const checkOnboardingStatus = useCallback(async (userId: string): Promise<boolean | null> => {
    try {
      setIsCheckingOnboarding(true)
      const memoryUrl = process.env.NEXT_PUBLIC_MEMORY_URL || 'http://localhost:8008'
      const response = await fetch(
        `${memoryUrl}/internal/user/onboarding-status?user_id=${userId}`
      )
      if (response.ok) {
        const data = await response.json()
        setOnboardingCompleted(data.completed)
        return data.completed
      }
      // If API fails, assume onboarding is completed to not block users
      setOnboardingCompleted(true)
      return true
    } catch (err) {
      console.error('Error checking onboarding status:', err)
      // Fail-safe: assume completed to not block users
      setOnboardingCompleted(true)
      return true
    } finally {
      setIsCheckingOnboarding(false)
    }
  }, [])

  const refreshOnboardingStatus = useCallback(async (): Promise<boolean | null> => {
    if (user?.id) {
      return await checkOnboardingStatus(user.id)
    }
    return null
  }, [user?.id, checkOnboardingStatus])

  const skipOnboarding = useCallback(async (): Promise<boolean> => {
    // Créer un company_profile minimal pour marquer l'onboarding comme "passé"
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      const response = await fetch(`${apiUrl}/api/contexts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: 'Profil (à compléter)',
          context_type: 'company_profile',
          content: '# Profil Entreprise\n\n*Onboarding passé - Vous pouvez compléter ce profil plus tard dans les paramètres.*',
          is_active: true
        })
      })

      if (response.ok) {
        setOnboardingCompleted(true)
        return true
      }
      return false
    } catch (err) {
      console.error('Error skipping onboarding:', err)
      // En cas d'erreur, permettre quand même de passer (UX)
      setOnboardingCompleted(true)
      return true
    }
  }, [session?.access_token])

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

          // Vérifier le statut onboarding si l'utilisateur est connecté
          if (initialSession?.user?.id) {
            await checkOnboardingStatus(initialSession.user.id)
          }

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
              // Vérifier le statut onboarding - la redirection est gérée par le useEffect
              if (newSession?.user?.id) {
                await checkOnboardingStatus(newSession.user.id)
              }
              // Note: La redirection est gérée par le useEffect de redirection
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
  }, [handleSession, router, checkOnboardingStatus])

  // Redirection basée sur l'état d'authentification ET le statut onboarding
  useEffect(() => {
    // Attendre que le chargement initial et la vérification onboarding soient terminés
    if (isLoading || isCheckingOnboarding) return

    // Cas 1: Utilisateur non connecté sur une route protégée → login
    if (!user && !isPublicRoute) {
      router.push('/login')
      return
    }

    // Cas 2: Utilisateur connecté mais onboarding non complété → forcer onboarding
    if (user && onboardingCompleted === false && pathname !== '/onboarding') {
      router.push('/onboarding')
      return
    }

    // Cas 3: Utilisateur connecté + onboarding complété + sur route publique → home
    // Exception: reset-password doit rester accessible
    if (user && onboardingCompleted === true && isPublicRoute &&
        pathname !== '/reset-password') {
      router.push('/')
      return
    }
  }, [user, isLoading, isCheckingOnboarding, onboardingCompleted, isPublicRoute, router, pathname])

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
      setOnboardingCompleted(null)  // Reset onboarding status
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
    onboardingCompleted,
    isCheckingOnboarding,
    signIn,
    signUp,
    signOut,
    refreshUser,
    refreshOnboardingStatus,
    skipOnboarding,
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

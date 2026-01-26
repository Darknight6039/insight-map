/**
 * =============================================================================
 * Supabase Client Configuration
 * =============================================================================
 * Ce module configure et exporte le client Supabase pour le frontend.
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js'

// =============================================================================
// CONFIGURATION
// =============================================================================

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:8000'
// HARDCODED FALLBACK FOR DEBUGGING
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlzcyI6InN1cGFiYXNlIiwiaWF0IjoxNzY4OTQyNDYxLCJleHAiOjIwODQzMDI0NjF9.hnBbeD2v3MbiZs8g29lPyCZC_1MyPdmoYhHDCJ7Oveo'

if (!supabaseAnonKey) {
  console.warn('NEXT_PUBLIC_SUPABASE_ANON_KEY is not set')
}

// =============================================================================
// CLIENT SINGLETON
// =============================================================================

let supabaseClient: SupabaseClient | null = null

export function getSupabaseClient(): SupabaseClient {
  if (!supabaseClient) {
    supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true,
        storage: typeof window !== 'undefined' ? window.localStorage : undefined,
      },
      realtime: {
        params: {
          eventsPerSecond: 10,
        },
      },
    })
  }
  return supabaseClient
}

// Export direct du client pour faciliter l'usage
export const supabase = getSupabaseClient()

// =============================================================================
// TYPES
// =============================================================================

export interface SupabaseUser {
  id: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
  created_at?: string
  last_sign_in_at?: string
}

export interface Session {
  access_token: string
  refresh_token: string
  expires_in: number
  expires_at?: number
  user: SupabaseUser
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Extrait les informations utilisateur depuis la session Supabase
 */
export function extractUserFromSession(session: any): SupabaseUser | null {
  if (!session?.user) return null

  const userMetadata = session.user.user_metadata || {}
  const appMetadata = session.user.app_metadata || {}

  return {
    id: session.user.id,
    email: session.user.email || '',
    full_name: userMetadata.full_name,
    role: appMetadata.role || 'user',
    is_active: appMetadata.is_active !== false,
    created_at: session.user.created_at,
    last_sign_in_at: session.user.last_sign_in_at,
  }
}

/**
 * Vérifie si l'utilisateur est admin
 */
export function isAdmin(user: SupabaseUser | null): boolean {
  return user?.role === 'admin'
}

/**
 * Récupère le token d'accès actuel
 */
export async function getAccessToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token || null
}

/**
 * Crée les headers d'authentification pour les appels API
 */
export async function getAuthHeaders(): Promise<HeadersInit> {
  const token = await getAccessToken()
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  }
}

// =============================================================================
// AUTH FUNCTIONS
// =============================================================================

/**
 * Connexion avec email et mot de passe
 */
export async function signInWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })

  if (error) throw error
  return data
}

/**
 * Inscription avec email et mot de passe
 * Note: L'inscription nécessite une validation côté backend (invitation code)
 */
export async function signUpWithEmail(
  email: string,
  password: string,
  fullName?: string,
  invitationCode?: string
) {
  // L'inscription passe par le backend pour valider le code d'invitation
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName,
      invitation_code: invitationCode,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Erreur lors de l\'inscription')
  }

  const data = await response.json()

  // Stocker la session manuellement si nécessaire
  if (data.access_token) {
    await supabase.auth.setSession({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
    })
  }

  return data
}

/**
 * Déconnexion
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) throw error
}

/**
 * Rafraîchir la session
 */
export async function refreshSession() {
  const { data, error } = await supabase.auth.refreshSession()
  if (error) throw error
  return data
}

/**
 * Demande de réinitialisation de mot de passe
 */
export async function requestPasswordReset(email: string) {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  })
  if (error) throw error
}

/**
 * Mise à jour du mot de passe
 */
export async function updatePassword(newPassword: string) {
  const { error } = await supabase.auth.updateUser({
    password: newPassword,
  })
  if (error) throw error
}

/**
 * Mise à jour du profil
 */
export async function updateProfile(data: { full_name?: string }) {
  const { error } = await supabase.auth.updateUser({
    data: data,
  })
  if (error) throw error
}

// =============================================================================
// EXPORTS
// =============================================================================

export default supabase

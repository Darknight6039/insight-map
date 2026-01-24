'use client'

/**
 * =============================================================================
 * Application Providers
 * =============================================================================
 * Encapsule tous les providers de contexte de l'application.
 * Utilise SupabaseAuthProvider pour l'authentification via Supabase.
 */

import { SupabaseAuthProvider } from './context/SupabaseAuthContext'
import { LanguageProvider } from './context/LanguageContext'
import { ThemeProvider } from './components/ThemeProvider'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <LanguageProvider>
        <SupabaseAuthProvider>
          {children}
        </SupabaseAuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  )
}

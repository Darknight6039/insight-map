'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import frTranslations from '../locales/fr.json'
import enTranslations from '../locales/en.json'

type Language = 'fr' | 'en'

interface TranslationData {
  [key: string]: string | TranslationData
}

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
  toggleLanguage: () => void
}

const translations: Record<Language, TranslationData> = {
  fr: frTranslations as TranslationData,
  en: enTranslations as TranslationData
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

const STORAGE_KEY = 'app-language'

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>('fr')
  const [isHydrated, setIsHydrated] = useState(false)

  // Load language from localStorage on mount
  useEffect(() => {
    const storedLanguage = localStorage.getItem(STORAGE_KEY) as Language | null
    if (storedLanguage && (storedLanguage === 'fr' || storedLanguage === 'en')) {
      setLanguageState(storedLanguage)
    }
    setIsHydrated(true)
  }, [])

  // Set language and persist to localStorage
  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang)
    localStorage.setItem(STORAGE_KEY, lang)
  }, [])

  // Toggle between languages
  const toggleLanguage = useCallback(() => {
    const newLang = language === 'fr' ? 'en' : 'fr'
    setLanguage(newLang)
  }, [language, setLanguage])

  // Translation function with nested key support (e.g., "nav.reports")
  const t = useCallback((key: string): string => {
    const keys = key.split('.')
    let result: string | TranslationData = translations[language]
    
    for (const k of keys) {
      if (result && typeof result === 'object' && k in result) {
        result = result[k]
      } else {
        // Return key if translation not found
        console.warn(`Translation not found for key: ${key}`)
        return key
      }
    }
    
    if (typeof result === 'string') {
      return result
    }
    
    // Return key if result is not a string
    return key
  }, [language])

  // Prevent hydration mismatch by not rendering until hydrated
  if (!isHydrated) {
    return null
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, toggleLanguage }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useTranslation() {
  const context = useContext(LanguageContext)
  if (context === undefined) {
    throw new Error('useTranslation must be used within a LanguageProvider')
  }
  return context
}

export function useLanguage() {
  return useTranslation()
}


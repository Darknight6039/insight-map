'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FileText, Bell, LogOut, User, ChevronDown, Shield, Settings, Users, Globe, MessageSquare, Library } from 'lucide-react'
import AxialLogo from './AxialLogo'
import { Button } from './ui/button'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { useTranslation } from '../context/LanguageContext'

export default function Navbar() {
  const pathname = usePathname()
  const { user, signOut, isAuthenticated, isAdmin } = useSupabaseAuth()
  const { t, language, setLanguage } = useTranslation()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const navLinks = [
    { href: '/', label: t('nav.newReport'), icon: FileText },
    { href: '/library', label: 'Bibliothèque', icon: Library },
    { href: '/history', label: 'Historique', icon: MessageSquare },
    { href: '/watches', label: t('nav.watches'), icon: Bell },
  ]

  // Don't render navbar on login page
  if (pathname === '/login' || pathname === '/register') {
    return null
  }

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="navbar-glass z-50"
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center">
          <AxialLogo size={36} />
        </Link>

        {/* Navigation links */}
        <div className="flex items-center gap-2">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{label}</span>
              </Link>
            )
          })}
          
          {/* Language Toggle */}
          <div className="flex items-center gap-1 ml-2 px-2 py-1 glass rounded-lg">
            <Globe className="w-4 h-4 text-gray-400 mr-1" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLanguage('fr')}
              className={`px-2 py-1 h-auto text-xs font-medium ${
                language === 'fr'
                  ? 'bg-cyan-500/20 text-cyan-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              FR
            </Button>
            <span className="text-gray-600">|</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLanguage('en')}
              className={`px-2 py-1 h-auto text-xs font-medium ${
                language === 'en'
                  ? 'bg-cyan-500/20 text-cyan-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              EN
            </Button>
          </div>
        </div>

        {/* User menu */}
        {isAuthenticated && user ? (
          <div className="relative">
            <Button
              variant="ghost"
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 px-4 py-2 glass rounded-xl hover:bg-white/10 h-auto"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[var(--axial-accent)] to-[var(--accent)] flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="text-left hidden sm:block">
                <p className="text-sm font-medium text-white truncate max-w-[120px]">
                  {user.full_name || user.email.split('@')[0]}
                </p>
                <p className="text-xs text-gray-400 flex items-center gap-1">
                  {isAdmin && <Shield className="w-3 h-3" />}
                  {isAdmin ? 'Admin' : t('nav.user')}
                </p>
              </div>
              <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
            </Button>

            <AnimatePresence>
              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 top-full mt-2 w-56 glass-card p-2 z-50"
                >
                  <div className="px-3 py-2 border-b border-white/10 mb-2">
                    <p className="text-sm font-medium text-white truncate">{user.email}</p>
                    <p className="text-xs text-gray-400">
                      {isAdmin ? 'Admin' : t('nav.user')}
                    </p>
                  </div>
                  
                  {/* Profile link */}
                  <Link
                    href="/profile"
                    onClick={() => setShowUserMenu(false)}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <Settings className="w-4 h-4" />
                    {t('nav.profile')}
                  </Link>
                  
                  {/* Admin link */}
                  {isAdmin && (
                    <Link
                      href="/admin"
                      onClick={() => setShowUserMenu(false)}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--axial-accent)] hover:bg-[var(--axial-accent)]/10 rounded-lg transition-colors"
                    >
                      <Users className="w-4 h-4" />
                      {t('nav.admin')}
                    </Link>
                  )}
                  
                  <div className="my-1 border-t border-white/10"></div>
                  
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setShowUserMenu(false)
                      signOut()
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 justify-start h-auto"
                  >
                    <LogOut className="w-4 h-4" />
                    {t('nav.logout')}
                  </Button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ) : (
          <div className="flex items-center gap-2 px-4 py-2 glass rounded-xl">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-300">{t('nav.systemOperational')}</span>
          </div>
        )}
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </motion.nav>
  )
}

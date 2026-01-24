'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useTheme } from 'next-themes'
import {
  FileText, Bell, LogOut, User, ChevronDown, Shield, Settings,
  Users, Globe, MessageSquare, Library, Menu, Moon, Sun, CreditCard
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './ui/button'
import { Avatar, AvatarFallback } from './ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { useTranslation } from '../context/LanguageContext'

export default function Navbar() {
  const pathname = usePathname()
  const router = useRouter()
  const { theme, setTheme } = useTheme()
  const { user, signOut, isAuthenticated, isAdmin } = useSupabaseAuth()
  const { t, language, setLanguage } = useTranslation()
  const [isNavMenuOpen, setIsNavMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)

  // Navigation items
  const navItems = [
    { label: t('nav.newReport'), icon: FileText, path: '/' },
    { label: 'Bibliothèque', icon: Library, path: '/library' },
    { label: 'Historique', icon: MessageSquare, path: '/history' },
    { label: t('nav.watches'), icon: Bell, path: '/watches' },
    ...(isAdmin ? [{ label: t('nav.admin'), icon: Users, path: '/admin' }] : []),
  ]

  // Get current page label
  const currentNavItem = navItems.find(item => item.path === pathname) || navItems[0]

  // Toggle language
  const toggleLanguage = () => {
    setLanguage(language === 'fr' ? 'en' : 'fr')
  }

  // Don't render navbar on login/register pages
  if (pathname === '/login' || pathname === '/register' || pathname === '/forgot-password' || pathname === '/reset-password') {
    return null
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex flex-col leading-tight">
          <span className="font-bold text-xl text-foreground tracking-wide">AXIAL</span>
          <span className="text-[10px] text-primary font-semibold tracking-[0.2em] -mt-1">INTELLIGENCE</span>
        </Link>

        {/* Navigation Dropdown */}
        <DropdownMenu open={isNavMenuOpen} onOpenChange={setIsNavMenuOpen}>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="gap-2 min-w-[160px] justify-between">
              <div className="flex items-center gap-2">
                <Menu className="w-4 h-4" />
                <currentNavItem.icon className="w-4 h-4" />
                <span>{currentNavItem.label}</span>
              </div>
              <ChevronDown className={cn(
                "w-4 h-4 text-muted-foreground transition-transform",
                isNavMenuOpen && "rotate-180"
              )} />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="center" className="w-48">
            {navItems.map((item) => {
              const isActive = pathname === item.path
              const Icon = item.icon
              return (
                <DropdownMenuItem
                  key={item.path}
                  onClick={() => router.push(item.path)}
                  className={cn(
                    "cursor-pointer gap-2",
                    isActive && "bg-primary/10 text-primary font-medium"
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </DropdownMenuItem>
              )
            })}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Right Controls */}
        <div className="flex items-center gap-2">
          {/* Language Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={toggleLanguage}
            className="gap-2"
          >
            <Globe className="w-4 h-4" />
            {language.toUpperCase()}
          </Button>

          {/* Theme Toggle */}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>

          {/* Status Indicator */}
          <div className="flex items-center gap-3 px-4 py-2 rounded-lg border border-border bg-secondary/50">
            <span className="status-indicator" />
            <span className="text-sm text-foreground">{t('nav.systemOperational')}</span>
          </div>

          {/* User Menu */}
          {isAuthenticated && user ? (
            <DropdownMenu open={isUserMenuOpen} onOpenChange={setIsUserMenuOpen}>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-3 pl-2 pr-3 h-10">
                  <Avatar className="h-7 w-7 gradient-icon-purple">
                    <AvatarFallback className="bg-transparent text-white text-xs">
                      <User className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col items-start text-left">
                    <span className="text-sm font-medium text-foreground truncate max-w-[120px]">
                      {user.full_name || user.email?.split('@')[0] || 'User'}
                    </span>
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      {isAdmin && <Shield className="w-3 h-3" />}
                      {isAdmin ? 'Admin' : t('nav.user')}
                    </span>
                  </div>
                  <ChevronDown className={cn(
                    "w-4 h-4 text-muted-foreground transition-transform",
                    isUserMenuOpen && "rotate-180"
                  )} />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <div className="px-3 py-2">
                  <p className="text-sm font-medium text-foreground truncate">{user.email}</p>
                  <p className="text-xs text-muted-foreground">{isAdmin ? 'Admin' : t('nav.user')}</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => router.push('/profile')} className="cursor-pointer">
                  <Settings className="w-4 h-4 mr-2" />
                  {t('nav.profile')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/pricing')} className="cursor-pointer">
                  <CreditCard className="w-4 h-4 mr-2" />
                  {t('nav.pricing') || 'Tarifs'}
                </DropdownMenuItem>
                {isAdmin && (
                  <DropdownMenuItem onClick={() => router.push('/admin')} className="text-primary cursor-pointer">
                    <Users className="w-4 h-4 mr-2" />
                    {t('nav.admin')}
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-destructive focus:text-destructive cursor-pointer"
                  onClick={signOut}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  {t('nav.logout')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button variant="outline" onClick={() => router.push('/login')}>
              {t('nav.login') || 'Connexion'}
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}

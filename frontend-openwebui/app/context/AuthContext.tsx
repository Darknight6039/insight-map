'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'

// Types
interface User {
  id: number
  email: string
  full_name: string | null
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string, invitationCode: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Storage keys
const TOKEN_KEY = 'insight_token'
const USER_KEY = 'insight_user'

// Public routes that don't require authentication
const PUBLIC_ROUTES = ['/login', '/register', '/forgot-password', '/reset-password']

// Provider component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  // Check if current route is public
  const isPublicRoute = PUBLIC_ROUTES.some(route => pathname?.startsWith(route))

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem(TOKEN_KEY)
        const storedUser = localStorage.getItem(USER_KEY)

        if (storedToken && storedUser) {
          setToken(storedToken)
          setUser(JSON.parse(storedUser))
          
          // Verify token is still valid
          try {
            const response = await fetch(`${API_URL}/auth/me`, {
              headers: {
                'Authorization': `Bearer ${storedToken}`
              }
            })
            
            if (response.ok) {
              const userData = await response.json()
              setUser(userData)
              localStorage.setItem(USER_KEY, JSON.stringify(userData))
            } else {
              // Token invalid, clear storage
              localStorage.removeItem(TOKEN_KEY)
              localStorage.removeItem(USER_KEY)
              setToken(null)
              setUser(null)
            }
          } catch (error) {
            console.error('Error verifying token:', error)
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error)
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  // Redirect logic
  useEffect(() => {
    if (!isLoading) {
      if (!user && !isPublicRoute) {
        router.push('/login')
      } else if (user && isPublicRoute) {
        router.push('/')
      }
    }
  }, [user, isLoading, isPublicRoute, router])

  // Login function
  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Erreur de connexion')
    }

    const data: AuthResponse = await response.json()
    
    // Store in state and localStorage
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    
    router.push('/')
  }, [router])

  // Register function
  const register = useCallback(async (
    email: string, 
    password: string, 
    fullName: string, 
    invitationCode: string
  ) => {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        email, 
        password, 
        full_name: fullName,
        invitation_code: invitationCode 
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Erreur d\'inscription')
    }

    const data: AuthResponse = await response.json()
    
    // Store in state and localStorage
    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    
    router.push('/')
  }, [router])

  // Logout function
  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    router.push('/login')
  }, [router])

  // Refresh user data
  const refreshUser = useCallback(async () => {
    if (!token) return

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
        localStorage.setItem(USER_KEY, JSON.stringify(userData))
      }
    } catch (error) {
      console.error('Error refreshing user:', error)
    }
  }, [token])

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    login,
    register,
    logout,
    refreshUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// HOC for protected pages (optional utility)
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  requireAdmin: boolean = false
) {
  return function ProtectedComponent(props: P) {
    const { user, isLoading, isAdmin } = useAuth()
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
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )
    }

    if (!user || (requireAdmin && !isAdmin)) {
      return null
    }

    return <Component {...props} />
  }
}


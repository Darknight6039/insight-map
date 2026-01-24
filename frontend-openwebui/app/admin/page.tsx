'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Users, 
  UserPlus, 
  Mail, 
  Shield, 
  ShieldOff,
  Copy, 
  Check, 
  Trash2, 
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  ArrowLeft,
  Ticket,
  AlertCircle,
  BarChart3,
  Activity,
  FileText,
  Search,
  LogIn,
  MessageSquare,
  Calendar,
  TrendingUp,
  Eye,
  Bell
} from 'lucide-react'
import Link from 'next/link'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { useRouter } from 'next/navigation'
import MainLayout from '../components/layout/MainLayout'
import { Button } from '../components/ui/button'

interface User {
  id: number
  email: string
  full_name: string | null
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

interface Invitation {
  id: number
  code: string
  email: string | null
  created_at: string
  expires_at: string
  used_at: string | null
}

interface PasswordReset {
  id: number
  email: string
  token: string | null
  created_at: string
  expires_at: string
  used_at: string | null
}

interface DashboardStats {
  total_users: number
  active_users: number
  total_reports: number
  total_logins_today: number
  total_logins_week: number
  total_activities_today: number
  reports_today: number
  reports_week: number
  total_watches: number
  watches_created_week: number
  watches_triggered_week: number
}

interface ActivityChartData {
  date: string
  logins: number
  reports: number
  chats: number
  searches: number
  watches: number
}

interface ReportTypeStats {
  type: string
  count: number
}

interface ActivityLog {
  id: number
  user_id: number | null
  user_email: string | null
  user_name: string | null
  action: string
  resource_type: string | null
  resource_id: number | null
  details: string | null
  created_at: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export default function AdminPage() {
  const { user, token, isAdmin, isLoading: authLoading } = useSupabaseAuth()
  const router = useRouter()
  
  const [activeTab, setActiveTab] = useState<'dashboard' | 'users' | 'invitations' | 'resets'>('dashboard')
  const [users, setUsers] = useState<User[]>([])
  const [invitations, setInvitations] = useState<Invitation[]>([])
  const [passwordResets, setPasswordResets] = useState<PasswordReset[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Dashboard state
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [activityByDay, setActivityByDay] = useState<ActivityChartData[]>([])
  const [reportsByType, setReportsByType] = useState<ReportTypeStats[]>([])
  const [recentActivities, setRecentActivities] = useState<ActivityLog[]>([])
  const [chartDays, setChartDays] = useState(7)
  const [dateRange, setDateRange] = useState({ start: '', end: '' })
  
  // Invitation form
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteExpiry, setInviteExpiry] = useState(7)
  const [isCreatingInvite, setIsCreatingInvite] = useState(false)
  const [newInviteCode, setNewInviteCode] = useState('')
  const [copiedCode, setCopiedCode] = useState(false)

  // Redirect non-admins
  useEffect(() => {
    if (!authLoading && (!user || !isAdmin)) {
      router.push('/')
    }
  }, [user, isAdmin, authLoading, router])

  // Fetch data
  const fetchUsers = useCallback(async () => {
    if (!token) return
    try {
      const response = await fetch(`${API_URL}/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setUsers(data)
      }
    } catch (err) {
      console.error('Error fetching users:', err)
    }
  }, [token])

  const fetchInvitations = useCallback(async () => {
    if (!token) return
    try {
      const response = await fetch(`${API_URL}/admin/invitations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setInvitations(data)
      }
    } catch (err) {
      console.error('Error fetching invitations:', err)
    }
  }, [token])

  const fetchPasswordResets = useCallback(async () => {
    if (!token) return
    try {
      const response = await fetch(`${API_URL}/admin/password-resets`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setPasswordResets(data)
      }
    } catch (err) {
      console.error('Error fetching password resets:', err)
    }
  }, [token])

  // Dashboard data fetchers
  const fetchDashboardStats = useCallback(async () => {
    if (!token) return
    try {
      let url = `${API_URL}/admin/dashboard/stats`
      const params = new URLSearchParams()
      if (dateRange.start) params.append('start_date', dateRange.start)
      if (dateRange.end) params.append('end_date', dateRange.end)
      if (params.toString()) url += `?${params.toString()}`
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setDashboardStats(data)
      }
    } catch (err) {
      console.error('Error fetching dashboard stats:', err)
    }
  }, [token, dateRange])

  const fetchDashboardCharts = useCallback(async () => {
    if (!token) return
    try {
      const response = await fetch(`${API_URL}/admin/dashboard/charts?days=${chartDays}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setActivityByDay(data.activity_by_day || [])
        setReportsByType(data.reports_by_type || [])
      }
    } catch (err) {
      console.error('Error fetching charts:', err)
    }
  }, [token, chartDays])

  const fetchRecentActivities = useCallback(async () => {
    if (!token) return
    try {
      let url = `${API_URL}/admin/dashboard/activities?limit=20`
      if (dateRange.start) url += `&start_date=${dateRange.start}`
      if (dateRange.end) url += `&end_date=${dateRange.end}`
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setRecentActivities(data)
      }
    } catch (err) {
      console.error('Error fetching activities:', err)
    }
  }, [token, dateRange])

  useEffect(() => {
    const loadData = async () => {
      if (!token || !isAdmin) return
      setIsLoading(true)
      await Promise.all([
        fetchUsers(), 
        fetchInvitations(), 
        fetchPasswordResets(),
        fetchDashboardStats(),
        fetchDashboardCharts(),
        fetchRecentActivities()
      ])
      setIsLoading(false)
    }
    loadData()
  }, [token, isAdmin, fetchUsers, fetchInvitations, fetchPasswordResets, fetchDashboardStats, fetchDashboardCharts, fetchRecentActivities])

  // Create invitation
  const handleCreateInvitation = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsCreatingInvite(true)
    setError('')
    setNewInviteCode('')

    try {
      const response = await fetch(`${API_URL}/admin/invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: inviteEmail || null,
          expires_in_days: inviteExpiry
        })
      })

      if (response.ok) {
        const data = await response.json()
        setNewInviteCode(data.code)
        setInviteEmail('')
        fetchInvitations()
      } else {
        const err = await response.json()
        setError(err.detail || 'Erreur lors de la création')
      }
    } catch (err) {
      setError('Erreur de connexion')
    } finally {
      setIsCreatingInvite(false)
    }
  }

  // Toggle user active status
  const handleToggleUserActive = async (userId: number) => {
    try {
      const response = await fetch(`${API_URL}/admin/users/${userId}/toggle-active`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        fetchUsers()
      }
    } catch (err) {
      console.error('Error toggling user:', err)
    }
  }

  // Copy invitation code
  const copyToClipboard = async (code: string) => {
    await navigator.clipboard.writeText(code)
    setCopiedCode(true)
    setTimeout(() => setCopiedCode(false), 2000)
  }

  // Format date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Check if invitation expired
  const isExpired = (expiresAt: string) => {
    return new Date(expiresAt) < new Date()
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-liquid"></div>
      </div>
    )
  }

  if (!isAdmin) {
    return null
  }

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="glass-card mb-6"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link 
                  href="/"
                  className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-gray-400" />
                </Link>
                <div>
                  <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Shield className="w-6 h-6 text-[var(--axial-accent)]" />
                    Administration
                  </h1>
                  <p className="text-gray-400 text-sm">Gérer les utilisateurs et les invitations</p>
                </div>
              </div>
              
              <Button
                variant="outline"
                onClick={() => {
                  fetchUsers();
                  fetchInvitations();
                  fetchPasswordResets();
                  fetchDashboardStats();
                  fetchDashboardCharts();
                  fetchRecentActivities();
                }}
              >
                <RefreshCw className="w-4 h-4" />
                Actualiser
              </Button>
            </div>
          </motion.div>

          {/* Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            <Button
              variant={activeTab === 'dashboard' ? 'default' : 'outline'}
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-6 py-3 h-auto ${
                activeTab === 'dashboard'
                  ? 'bg-[var(--axial-accent)] text-white hover:bg-[var(--axial-accent)]/90'
                  : 'glass text-gray-400 hover:text-white hover:bg-white/10 border-white/10'
              }`}
            >
              <BarChart3 className="w-5 h-5" />
              Dashboard
            </Button>
            <Button
              variant={activeTab === 'users' ? 'default' : 'outline'}
              onClick={() => setActiveTab('users')}
              className={`flex items-center gap-2 px-6 py-3 h-auto ${
                activeTab === 'users'
                  ? 'bg-[var(--axial-accent)] text-white hover:bg-[var(--axial-accent)]/90'
                  : 'glass text-gray-400 hover:text-white hover:bg-white/10 border-white/10'
              }`}
            >
              <Users className="w-5 h-5" />
              Utilisateurs ({users.length})
            </Button>
            <Button
              variant={activeTab === 'invitations' ? 'default' : 'outline'}
              onClick={() => setActiveTab('invitations')}
              className={`flex items-center gap-2 px-6 py-3 h-auto ${
                activeTab === 'invitations'
                  ? 'bg-[var(--axial-accent)] text-white hover:bg-[var(--axial-accent)]/90'
                  : 'glass text-gray-400 hover:text-white hover:bg-white/10 border-white/10'
              }`}
            >
              <Ticket className="w-5 h-5" />
              Invitations ({invitations.length})
            </Button>
            <Button
              variant={activeTab === 'resets' ? 'default' : 'outline'}
              onClick={() => setActiveTab('resets')}
              className={`flex items-center gap-2 px-6 py-3 h-auto ${
                activeTab === 'resets'
                  ? 'bg-[var(--axial-accent)] text-white hover:bg-[var(--axial-accent)]/90'
                  : 'glass text-gray-400 hover:text-white hover:bg-white/10 border-white/10'
              }`}
            >
              <Mail className="w-5 h-5" />
              Réinitialisations ({passwordResets.filter(r => !r.used_at && !isExpired(r.expires_at)).length})
            </Button>
          </div>

          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' ? (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="space-y-6"
              >
                {/* Date Filter */}
                <div className="glass-card">
                  <div className="flex flex-wrap items-end gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Date de début</label>
                      <input
                        type="date"
                        value={dateRange.start}
                        onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                        className="glass-input px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-1">Date de fin</label>
                      <input
                        type="date"
                        value={dateRange.end}
                        onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                        className="glass-input px-3 py-2"
                      />
                    </div>
                    <Button
                      onClick={() => {
                        fetchDashboardStats()
                        fetchRecentActivities()
                      }}
                    >
                      <Calendar className="w-4 h-4" />
                      Appliquer
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setDateRange({ start: '', end: '' })
                        fetchDashboardStats()
                        fetchRecentActivities()
                      }}
                    >
                      Réinitialiser
                    </Button>
                  </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="glass-card text-center">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-2">
                      <Users className="w-6 h-6 text-blue-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{dashboardStats?.total_users || 0}</div>
                    <div className="text-sm text-gray-400">Utilisateurs</div>
                    <div className="text-xs text-green-400 mt-1">{dashboardStats?.active_users || 0} actifs</div>
                  </div>
                  
                  <div className="glass-card text-center">
                    <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-2">
                      <FileText className="w-6 h-6 text-purple-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{dashboardStats?.total_reports || 0}</div>
                    <div className="text-sm text-gray-400">Rapports</div>
                    <div className="text-xs text-green-400 mt-1">+{dashboardStats?.reports_week || 0} cette semaine</div>
                  </div>
                  
                  <div className="glass-card text-center">
                    <div className="w-12 h-12 rounded-full bg-cyan-500/20 flex items-center justify-center mx-auto mb-2">
                      <Eye className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{dashboardStats?.total_watches || 0}</div>
                    <div className="text-sm text-gray-400">Veilles</div>
                    <div className="text-xs text-green-400 mt-1">+{dashboardStats?.watches_created_week || 0} cette semaine</div>
                  </div>
                  
                  <div className="glass-card text-center">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-2">
                      <LogIn className="w-6 h-6 text-green-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{dashboardStats?.total_logins_today || 0}</div>
                    <div className="text-sm text-gray-400">Connexions</div>
                    <div className="text-xs text-gray-500 mt-1">{dashboardStats?.total_logins_week || 0} cette semaine</div>
                  </div>
                  
                  <div className="glass-card text-center">
                    <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center mx-auto mb-2">
                      <Activity className="w-6 h-6 text-orange-400" />
                    </div>
                    <div className="text-2xl font-bold text-white">{dashboardStats?.total_activities_today || 0}</div>
                    <div className="text-sm text-gray-400">Activités</div>
                    <div className="text-xs text-gray-500 mt-1">aujourd&apos;hui</div>
                  </div>
                </div>

                {/* Charts Row */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Activity Chart */}
                  <div className="glass-card">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-[var(--axial-accent)]" />
                        Activité par jour
                      </h3>
                      <select
                        value={chartDays}
                        onChange={(e) => {
                          setChartDays(Number(e.target.value))
                          fetchDashboardCharts()
                        }}
                        className="glass-input px-3 py-1 text-sm"
                      >
                        <option value={7}>7 jours</option>
                        <option value={14}>14 jours</option>
                        <option value={30}>30 jours</option>
                      </select>
                    </div>
                    
                    <div className="h-48 flex items-end gap-1">
                      {activityByDay.map((day, i) => {
                        const total = day.logins + day.reports + day.chats + day.searches + (day.watches || 0)
                        const maxTotal = Math.max(...activityByDay.map(d => d.logins + d.reports + d.chats + d.searches + (d.watches || 0)), 1)
                        const height = (total / maxTotal) * 100
                        
                        return (
                          <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            <div 
                              className="w-full bg-gradient-to-t from-[var(--axial-accent)] to-[var(--accent)] rounded-t transition-all"
                              style={{ height: `${Math.max(height, 2)}%` }}
                              title={`${day.date}: ${total} activités`}
                            />
                            <span className="text-[10px] text-gray-500 rotate-[-45deg] origin-top-left whitespace-nowrap">
                              {day.date.slice(5)}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                    
                    <div className="flex flex-wrap justify-center gap-3 mt-4 text-xs">
                      <span className="flex items-center gap-1"><LogIn className="w-3 h-3 text-green-400" /> Connexions</span>
                      <span className="flex items-center gap-1"><FileText className="w-3 h-3 text-purple-400" /> Rapports</span>
                      <span className="flex items-center gap-1"><Eye className="w-3 h-3 text-cyan-400" /> Veilles</span>
                      <span className="flex items-center gap-1"><Search className="w-3 h-3 text-blue-400" /> Recherches</span>
                    </div>
                  </div>

                  {/* Reports by Type */}
                  <div className="glass-card">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                      <FileText className="w-5 h-5 text-[var(--axial-accent)]" />
                      Rapports par type
                    </h3>
                    
                    {reportsByType.length === 0 || (reportsByType.length === 1 && reportsByType[0].count === 0) ? (
                      <div className="text-center py-8 text-gray-500">
                        Aucune donnée disponible
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {reportsByType.map((rt, i) => {
                          const maxCount = Math.max(...reportsByType.map(r => r.count), 1)
                          const width = (rt.count / maxCount) * 100
                          const colors = ['bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-orange-500', 'bg-pink-500']
                          
                          return (
                            <div key={i}>
                              <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-300 capitalize">{rt.type}</span>
                                <span className="text-white font-medium">{rt.count}</span>
                              </div>
                              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full ${colors[i % colors.length]} rounded-full transition-all`}
                                  style={{ width: `${width}%` }}
                                />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </div>

                {/* Recent Activities */}
                <div className="glass-card">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                    <Activity className="w-5 h-5 text-[var(--axial-accent)]" />
                    Activités récentes
                  </h3>
                  
                  {recentActivities.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      Aucune activité enregistrée
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {recentActivities.map((activity) => {
                        const actionIcons: Record<string, React.ReactNode> = {
                          login: <LogIn className="w-4 h-4 text-green-400" />,
                          report_created: <FileText className="w-4 h-4 text-purple-400" />,
                          search: <Search className="w-4 h-4 text-blue-400" />,
                          chat_message: <MessageSquare className="w-4 h-4 text-orange-400" />,
                          watch_created: <Eye className="w-4 h-4 text-cyan-400" />,
                          watch_updated: <Eye className="w-4 h-4 text-cyan-400" />,
                          watch_triggered: <Bell className="w-4 h-4 text-yellow-400" />,
                          watch_deleted: <Eye className="w-4 h-4 text-red-400" />,
                        }
                        
                        const actionLabels: Record<string, string> = {
                          login: 's\'est connecté',
                          report_created: 'a créé un rapport',
                          search: 'a effectué une recherche',
                          chat_message: 'a envoyé un message',
                          watch_created: 'a créé une veille',
                          watch_updated: 'a modifié une veille',
                          watch_triggered: 'a déclenché une veille',
                          watch_deleted: 'a supprimé une veille',
                        }
                        
                        return (
                          <div 
                            key={activity.id}
                            className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                          >
                            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                              {actionIcons[activity.action] || <Activity className="w-4 h-4 text-gray-400" />}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-white truncate">
                                  {activity.user_name || activity.user_email || 'Utilisateur inconnu'}
                                </span>
                                <span className="text-gray-400 text-sm">
                                  {actionLabels[activity.action] || activity.action}
                                </span>
                              </div>
                              {activity.details && (
                                <div className="text-xs text-gray-500 truncate">{activity.details}</div>
                              )}
                            </div>
                            <div className="text-xs text-gray-500 whitespace-nowrap">
                              {new Date(activity.created_at).toLocaleString('fr-FR', {
                                day: '2-digit',
                                month: 'short',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </motion.div>
            ) : activeTab === 'users' ? (
              <motion.div
                key="users"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                {/* Users List */}
                <div className="glass-card">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5 text-[var(--axial-accent)]" />
                    Liste des utilisateurs
                  </h2>
                  
                  <div className="space-y-3">
                    {users.map((u) => (
                      <motion.div
                        key={u.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex items-center justify-between p-4 rounded-xl border ${
                          u.is_active 
                            ? 'bg-white/5 border-white/10' 
                            : 'bg-red-500/10 border-red-500/20'
                        }`}
                      >
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            u.role === 'admin' 
                              ? 'bg-gradient-to-br from-[var(--axial-accent)] to-[var(--accent)]'
                              : 'bg-gray-600'
                          }`}>
                            {u.role === 'admin' ? (
                              <Shield className="w-5 h-5 text-white" />
                            ) : (
                              <Users className="w-5 h-5 text-white" />
                            )}
                          </div>
                          
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-white">
                                {u.full_name || u.email.split('@')[0]}
                              </p>
                              {u.role === 'admin' && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-[var(--axial-accent)]/20 text-[var(--axial-accent)]">
                                  Admin
                                </span>
                              )}
                              {!u.is_active && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-400">
                                  Désactivé
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-400">{u.email}</p>
                            <p className="text-xs text-gray-500">
                              Inscrit le {formatDate(u.created_at)}
                            </p>
                          </div>
                        </div>
                        
                        {u.id !== user?.id && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleToggleUserActive(u.id)}
                            className={u.is_active
                              ? 'text-muted-foreground hover:text-destructive hover:bg-destructive/10'
                              : 'text-muted-foreground hover:text-green-400 hover:bg-green-500/10'
                            }
                            title={u.is_active ? 'Désactiver' : 'Activer'}
                          >
                            {u.is_active ? (
                              <ShieldOff className="w-5 h-5" />
                            ) : (
                              <Shield className="w-5 h-5" />
                            )}
                          </Button>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            ) : activeTab === 'invitations' ? (
              <motion.div
                key="invitations"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Create Invitation Form */}
                <div className="glass-card">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <UserPlus className="w-5 h-5 text-[var(--axial-accent)]" />
                    Créer une invitation
                  </h2>
                  
                  <form onSubmit={handleCreateInvitation} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">
                          Email (optionnel)
                        </label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                          <input
                            type="email"
                            value={inviteEmail}
                            onChange={(e) => setInviteEmail(e.target.value)}
                            placeholder="Laisser vide pour invitation générique"
                            className="glass-input w-full pl-10"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">
                          Expiration
                        </label>
                        <div className="relative">
                          <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                          <select
                            value={inviteExpiry}
                            onChange={(e) => setInviteExpiry(Number(e.target.value))}
                            className="glass-input w-full pl-10 appearance-none"
                          >
                            <option value={1}>1 jour</option>
                            <option value={3}>3 jours</option>
                            <option value={7}>7 jours</option>
                            <option value={14}>14 jours</option>
                            <option value={30}>30 jours</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    
                    {error && (
                      <div className="flex items-center gap-2 text-red-400 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                      </div>
                    )}
                    
                    <Button
                      type="submit"
                      disabled={isCreatingInvite}
                    >
                      {isCreatingInvite ? (
                        <RefreshCw className="w-5 h-5 animate-spin" />
                      ) : (
                        <UserPlus className="w-5 h-5" />
                      )}
                      Générer une invitation
                    </Button>
                  </form>
                  
                  {/* New invitation code */}
                  <AnimatePresence>
                    {newInviteCode && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 p-4 rounded-xl bg-green-500/10 border border-green-500/30"
                      >
                        <p className="text-green-400 text-sm mb-2 flex items-center gap-2">
                          <CheckCircle className="w-4 h-4" />
                          Invitation créée avec succès !
                        </p>
                        <div className="flex items-center gap-2">
                          <code className="flex-1 p-3 rounded-lg bg-black/30 text-white text-sm font-mono break-all">
                            {newInviteCode}
                          </code>
                          <Button
                            size="icon"
                            onClick={() => copyToClipboard(newInviteCode)}
                          >
                            {copiedCode ? (
                              <Check className="w-5 h-5" />
                            ) : (
                              <Copy className="w-5 h-5" />
                            )}
                          </Button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Invitations List */}
                <div className="glass-card">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Ticket className="w-5 h-5 text-[var(--axial-accent)]" />
                    Invitations existantes
                  </h2>
                  
                  {invitations.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                      Aucune invitation créée
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {invitations.map((inv) => {
                        const expired = isExpired(inv.expires_at)
                        const used = !!inv.used_at
                        
                        return (
                          <motion.div
                            key={inv.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`p-4 rounded-xl border ${
                              used
                                ? 'bg-green-500/10 border-green-500/20'
                                : expired
                                  ? 'bg-red-500/10 border-red-500/20'
                                  : 'bg-white/5 border-white/10'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  {used ? (
                                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-400">
                                      <CheckCircle className="w-3 h-3" />
                                      Utilisée
                                    </span>
                                  ) : expired ? (
                                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-400">
                                      <XCircle className="w-3 h-3" />
                                      Expirée
                                    </span>
                                  ) : (
                                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">
                                      <Clock className="w-3 h-3" />
                                      Active
                                    </span>
                                  )}
                                  {inv.email && (
                                    <span className="text-xs text-gray-500">
                                      Pour: {inv.email}
                                    </span>
                                  )}
                                </div>
                                
                                <code className="text-sm text-gray-300 font-mono block truncate">
                                  {inv.code}
                                </code>
                                
                                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                  <span>Créée: {formatDate(inv.created_at)}</span>
                                  <span>Expire: {formatDate(inv.expires_at)}</span>
                                  {inv.used_at && (
                                    <span>Utilisée: {formatDate(inv.used_at)}</span>
                                  )}
                                </div>
                              </div>
                              
                              {!used && !expired && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => copyToClipboard(inv.code)}
                                  title="Copier le code"
                                  className="text-muted-foreground hover:text-foreground"
                                >
                                  <Copy className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          </motion.div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </motion.div>
            ) : activeTab === 'resets' ? (
              <motion.div
                key="resets"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {/* Password Resets List */}
                <div className="glass-card">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Mail className="w-5 h-5 text-[var(--axial-accent)]" />
                    Demandes de réinitialisation
                  </h2>
                  
                  <p className="text-gray-400 text-sm mb-4">
                    Les utilisateurs peuvent demander une réinitialisation via la page de connexion.
                    Partagez le lien ci-dessous avec l&apos;utilisateur concerné.
                  </p>
                  
                  {passwordResets.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                      Aucune demande de réinitialisation
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {passwordResets.map((reset) => {
                        const expired = isExpired(reset.expires_at)
                        const used = !!reset.used_at
                        const isActive = !used && !expired && reset.token
                        
                        return (
                          <motion.div
                            key={reset.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`p-4 rounded-xl border ${
                              used
                                ? 'bg-green-500/10 border-green-500/20'
                                : expired
                                  ? 'bg-red-500/10 border-red-500/20'
                                  : 'bg-blue-500/10 border-blue-500/20'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="font-medium text-white">{reset.email}</span>
                                  {used ? (
                                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-400">
                                      <CheckCircle className="w-3 h-3" />
                                      Utilisée
                                    </span>
                                  ) : expired ? (
                                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-400">
                                      <XCircle className="w-3 h-3" />
                                      Expirée
                                    </span>
                                  ) : (
                                    <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400">
                                      <Clock className="w-3 h-3" />
                                      Active
                                    </span>
                                  )}
                                </div>
                                
                                {isActive && (
                                  <div className="mb-2">
                                    <p className="text-xs text-gray-500 mb-1">Lien de réinitialisation :</p>
                                    <code className="text-sm text-gray-300 font-mono block truncate bg-black/30 p-2 rounded">
                                      {typeof window !== 'undefined' ? window.location.origin : ''}/reset-password?token={reset.token}
                                    </code>
                                  </div>
                                )}
                                
                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                  <span>Demandée: {formatDate(reset.created_at)}</span>
                                  <span>Expire: {formatDate(reset.expires_at)}</span>
                                  {reset.used_at && (
                                    <span>Utilisée: {formatDate(reset.used_at)}</span>
                                  )}
                                </div>
                              </div>
                              
                              {isActive && reset.token && (
                                <Button
                                  size="icon"
                                  onClick={() => copyToClipboard(`${typeof window !== 'undefined' ? window.location.origin : ''}/reset-password?token=${reset.token}`)}
                                  title="Copier le lien"
                                >
                                  <Copy className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          </motion.div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
    </MainLayout>
  )
}


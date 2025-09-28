'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  FileText, 
  Brain, 
  Users, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  Activity
} from 'lucide-react'

interface DashboardStats {
  totalAnalyses: number
  completedToday: number
  activeUsers: number
  avgProcessingTime: number
}

interface RecentActivity {
  id: string
  type: string
  title: string
  status: 'completed' | 'processing' | 'failed'
  timestamp: Date
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalAnalyses: 0,
    completedToday: 0,
    activeUsers: 0,
    avgProcessingTime: 0
  })
  
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Simuler des données pour l'instant
      setTimeout(() => {
        setStats({
          totalAnalyses: 247,
          completedToday: 12,
          activeUsers: 8,
          avgProcessingTime: 45
        })

        setRecentActivity([
          {
            id: '1',
            type: 'Synthèse Exécutive',
            title: 'Analyse du marché crypto',
            status: 'completed',
            timestamp: new Date(Date.now() - 5 * 60 * 1000)
          },
          {
            id: '2',
            type: 'Veille Technologique',
            title: 'IA générative en finance',
            status: 'processing',
            timestamp: new Date(Date.now() - 15 * 60 * 1000)
          },
          {
            id: '3',
            type: 'Analyse Concurrentielle',
            title: 'Fintech européennes',
            status: 'completed',
            timestamp: new Date(Date.now() - 30 * 60 * 1000)
          },
          {
            id: '4',
            type: 'Analyse des Risques',
            title: 'Cyber-sécurité bancaire',
            status: 'failed',
            timestamp: new Date(Date.now() - 45 * 60 * 1000)
          }
        ])

        setIsLoading(false)
      }, 1000)

    } catch (error) {
      console.error('Erreur chargement dashboard:', error)
      setIsLoading(false)
    }
  }

  const StatCard = ({ 
    title, 
    value, 
    icon: Icon, 
    color, 
    change 
  }: { 
    title: string
    value: string | number
    icon: any
    color: string
    change?: string 
  }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card glow-on-hover"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {change && (
            <p className={`text-xs ${change.includes('+') ? 'text-green-400' : 'text-red-400'}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-r ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  )

  if (isLoading) {
    return (
      <div className="glass-card h-64 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-liquid mx-auto mb-4"></div>
          <p className="text-gray-400">Chargement du dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
      >
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-3">
          <Activity className="w-7 h-7 text-axial-accent" />
          Dashboard Intelligence
        </h2>
        <p className="text-gray-400">Vue d'ensemble de votre activité d'analyse stratégique</p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Analyses Totales"
          value={stats.totalAnalyses}
          icon={Brain}
          color="from-blue-500 to-cyan-500"
          change="+12% ce mois"
        />
        
        <StatCard
          title="Complétées Aujourd'hui"
          value={stats.completedToday}
          icon={CheckCircle}
          color="from-green-500 to-teal-500"
          change="+3 depuis hier"
        />
        
        <StatCard
          title="Utilisateurs Actifs"
          value={stats.activeUsers}
          icon={Users}
          color="from-purple-500 to-pink-500"
          change="+2 cette semaine"
        />
        
        <StatCard
          title="Temps Moyen (sec)"
          value={stats.avgProcessingTime}
          icon={Clock}
          color="from-orange-500 to-red-500"
          change="-8% optimisation"
        />
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card"
      >
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          <Clock className="w-5 h-5 text-axial-accent" />
          Activité Récente
        </h3>
        
        <div className="space-y-4">
          {recentActivity.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'completed' 
                    ? 'bg-green-500' 
                    : activity.status === 'processing'
                    ? 'bg-yellow-500 animate-pulse'
                    : 'bg-red-500'
                }`} />
                
                <div>
                  <h4 className="font-medium text-white text-sm">
                    {activity.title}
                  </h4>
                  <p className="text-xs text-gray-400">
                    {activity.type} • {activity.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {activity.status === 'completed' && (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                )}
                {activity.status === 'processing' && (
                  <div className="loading-liquid w-4 h-4"></div>
                )}
                {activity.status === 'failed' && (
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                )}
                
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === 'completed'
                    ? 'bg-green-500/20 text-green-400'
                    : activity.status === 'processing'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {activity.status === 'completed' ? 'Terminé' :
                   activity.status === 'processing' ? 'En cours' : 'Échec'}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Performance Chart Placeholder */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="glass-card"
      >
        <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-axial-accent" />
          Tendances d'Usage
        </h3>
        
        <div className="h-64 flex items-center justify-center bg-black/20 rounded-xl">
          <div className="text-center">
            <TrendingUp className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">Graphique de performance</p>
            <p className="text-sm text-gray-500">À implémenter avec Chart.js</p>
          </div>
        </div>
      </motion.div>

      {/* System Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="glass-card"
      >
        <h3 className="text-xl font-semibold text-white mb-6">État du Système</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { service: 'API Gateway', status: 'online', uptime: '99.9%' },
            { service: 'RAG Service', status: 'online', uptime: '99.7%' },
            { service: 'Vector DB', status: 'online', uptime: '99.8%' }
          ].map((service, index) => (
            <div key={index} className="p-4 rounded-xl bg-white/5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{service.service}</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-xs text-green-400">En ligne</span>
                </div>
              </div>
              <p className="text-sm text-gray-400">Uptime: {service.uptime}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Save,
  CheckCircle,
  AlertCircle,
  ArrowLeft,
  Shield,
  Calendar,
  FileText,
  Upload,
  Type,
  Trash2,
  Building,
  Plus,
  ToggleLeft,
  ToggleRight,
  HardDrive,
  Edit3
} from 'lucide-react'

// Types for multi-context
interface ContextItem {
  id: number
  name: string
  context_type: 'text' | 'document'
  preview?: string
  filename?: string
  file_type?: string
  content_size: number
  is_active: boolean
  created_at: string
  updated_at: string
}

interface StorageQuota {
  user_id: number
  total_used_bytes: number
  max_bytes: number
  used_percentage: number
  remaining_bytes: number
}
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import MainLayout from '../components/layout/MainLayout'
import { Button } from '../components/ui/button'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export default function ProfilePage() {
  const { user, token, isLoading: authLoading, refreshUser } = useSupabaseAuth()
  const router = useRouter()

  // Profile form
  const [fullName, setFullName] = useState('')
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [profileSuccess, setProfileSuccess] = useState(false)
  const [profileError, setProfileError] = useState('')

  // Password form
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPasswords, setShowPasswords] = useState(false)
  const [isSavingPassword, setIsSavingPassword] = useState(false)
  const [passwordSuccess, setPasswordSuccess] = useState(false)
  const [passwordError, setPasswordError] = useState('')

  // Multi-context management
  const [contexts, setContexts] = useState<ContextItem[]>([])
  const [storageQuota, setStorageQuota] = useState<StorageQuota | null>(null)
  const [isLoadingContexts, setIsLoadingContexts] = useState(true)
  const [showAddContext, setShowAddContext] = useState(false)
  const [contextType, setContextType] = useState<'text' | 'document'>('text')
  const [contextName, setContextName] = useState('')
  const [contextText, setContextText] = useState('')
  const [contextDocument, setContextDocument] = useState<File | null>(null)
  const [isSavingContext, setIsSavingContext] = useState(false)
  const [contextSuccess, setContextSuccess] = useState(false)
  const [contextError, setContextError] = useState('')
  const [editingContextId, setEditingContextId] = useState<number | null>(null)

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '')
    }
  }, [user])

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [user, authLoading, router])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileError('')
    setProfileSuccess(false)
    setIsSavingProfile(true)

    try {
      const response = await fetch(`${API_URL}/auth/profile?full_name=${encodeURIComponent(fullName)}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setProfileSuccess(true)
        refreshUser()
        setTimeout(() => setProfileSuccess(false), 3000)
      } else {
        const data = await response.json()
        setProfileError(data.detail || 'Erreur lors de la sauvegarde')
      }
    } catch (err) {
      setProfileError('Erreur de connexion au serveur')
    } finally {
      setIsSavingProfile(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError('')
    setPasswordSuccess(false)

    if (newPassword !== confirmPassword) {
      setPasswordError('Les mots de passe ne correspondent pas')
      return
    }

    if (newPassword.length < 6) {
      setPasswordError('Le mot de passe doit contenir au moins 6 caractères')
      return
    }

    setIsSavingPassword(true)

    try {
      const response = await fetch(`${API_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      })

      if (response.ok) {
        setPasswordSuccess(true)
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
        setTimeout(() => setPasswordSuccess(false), 3000)
      } else {
        const data = await response.json()
        setPasswordError(data.detail || 'Erreur lors du changement de mot de passe')
      }
    } catch (err) {
      setPasswordError('Erreur de connexion au serveur')
    } finally {
      setIsSavingPassword(false)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    })
  }

  // Fetch contexts and quota on load
  useEffect(() => {
    const fetchContextsAndQuota = async () => {
      if (!token) return
      setIsLoadingContexts(true)
      try {
        const [ctxRes, quotaRes] = await Promise.all([
          fetch(`${API_URL}/api/contexts`, { headers: { 'Authorization': `Bearer ${token}` } }),
          fetch(`${API_URL}/api/contexts/quota`, { headers: { 'Authorization': `Bearer ${token}` } })
        ])
        if (ctxRes.ok) {
          const data = await ctxRes.json()
          setContexts(data.contexts || [])
        }
        if (quotaRes.ok) {
          const quotaData = await quotaRes.json()
          setStorageQuota(quotaData)
        }
      } catch (err) {
        console.log('Error fetching contexts:', err)
      } finally {
        setIsLoadingContexts(false)
      }
    }
    fetchContextsAndQuota()
  }, [token])

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'Ko', 'Mo', 'Go']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const handleSaveContext = async () => {
    setContextError('')
    setContextSuccess(false)
    setIsSavingContext(true)

    try {
      let content = ''
      let name = contextName || 'Nouveau contexte'

      if (contextType === 'text') {
        content = contextText
        if (!content) throw new Error('Veuillez entrer du contenu')
      } else if (contextDocument) {
        // Read document content (for now, use filename as content placeholder)
        // The actual content extraction will happen server-side
        const formData = new FormData()
        formData.append('file', contextDocument)
        const uploadRes = await fetch(`${API_URL}/context/upload`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })
        if (!uploadRes.ok) throw new Error('Erreur lors de l\'upload')
        // Refresh contexts after upload
        const ctxRes = await fetch(`${API_URL}/api/contexts`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (ctxRes.ok) {
          const data = await ctxRes.json()
          setContexts(data.contexts || [])
        }
        setContextSuccess(true)
        setShowAddContext(false)
        resetContextForm()
        setTimeout(() => setContextSuccess(false), 3000)
        return
      } else {
        throw new Error('Veuillez selectionner un fichier')
      }

      // Create text context via new API
      const response = await fetch(`${API_URL}/api/contexts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: name,
          context_type: contextType,
          content: content,
          is_active: true
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erreur lors de la sauvegarde')
      }

      const newContext = await response.json()
      setContexts(prev => [newContext, ...prev])

      // Refresh quota
      const quotaRes = await fetch(`${API_URL}/api/contexts/quota`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (quotaRes.ok) {
        setStorageQuota(await quotaRes.json())
      }

      setContextSuccess(true)
      setShowAddContext(false)
      resetContextForm()
      setTimeout(() => setContextSuccess(false), 3000)
    } catch (err: any) {
      setContextError(err.message || 'Erreur lors de la sauvegarde du contexte')
    } finally {
      setIsSavingContext(false)
    }
  }

  const resetContextForm = () => {
    setContextName('')
    setContextText('')
    setContextDocument(null)
    setContextType('text')
    setEditingContextId(null)
  }

  const handleDeleteContext = async (contextId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/contexts/${contextId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok || response.status === 204) {
        setContexts(prev => prev.filter(c => c.id !== contextId))
        // Refresh quota
        const quotaRes = await fetch(`${API_URL}/api/contexts/quota`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (quotaRes.ok) {
          setStorageQuota(await quotaRes.json())
        }
      }
    } catch (err) {
      setContextError('Erreur lors de la suppression')
    }
  }

  const handleToggleContextActive = async (contextId: number, currentActive: boolean) => {
    try {
      const response = await fetch(`${API_URL}/api/contexts/${contextId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_active: !currentActive })
      })
      if (response.ok) {
        const updatedContext = await response.json()
        setContexts(prev => prev.map(c => c.id === contextId ? updatedContext : c))
      }
    } catch (err) {
      setContextError('Erreur lors de la mise à jour')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
      if (!validTypes.includes(file.type)) {
        setContextError('Format non supporté. Utilisez PDF, DOCX ou TXT.')
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        setContextError('Fichier trop volumineux (max 10 Mo)')
        return
      }
      setContextDocument(file)
      setContextName(file.name.replace(/\.[^/.]+$/, ''))
      setContextError('')
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-liquid"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="glass-card mb-6"
          >
            <div className="flex items-center gap-4">
              <Link 
                href="/"
                className="p-2 rounded-lg hover:bg-accent/10 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-muted-foreground" />
              </Link>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
                  <User className="w-6 h-6 text-[var(--axial-accent)]" />
                  Mon Profil
                </h1>
                <p className="text-muted-foreground text-sm">Gérer vos informations et votre mot de passe</p>
              </div>
            </div>
          </motion.div>

          {/* User Info Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card mb-6"
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[var(--axial-accent)] to-[var(--accent)] flex items-center justify-center">
                <User className="w-8 h-8 text-foreground" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-foreground">
                  {user.full_name || user.email.split('@')[0]}
                </h2>
                <p className="text-muted-foreground flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {user.email}
                </p>
                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Shield className="w-3 h-3" />
                    {user.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Membre depuis {formatDate(user.created_at)}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Profile Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card mb-6"
          >
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-[var(--axial-accent)]" />
              Informations du profil
            </h3>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              {profileError && (
                <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {profileError}
                </div>
              )}

              {profileSuccess && (
                <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3 text-green-400 text-sm">
                  <CheckCircle className="w-4 h-4 flex-shrink-0" />
                  Profil mis à jour avec succès
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Nom complet
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="glass-input w-full pl-12 pr-4"
                    placeholder="Votre nom complet"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="glass-input w-full pl-12 pr-4 opacity-50 cursor-not-allowed"
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">L&apos;email ne peut pas être modifié</p>
              </div>

              <Button
                type="submit"
                disabled={isSavingProfile}
              >
                {isSavingProfile ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Save className="w-5 h-5" />
                )}
                Enregistrer
              </Button>
            </form>
          </motion.div>

          {/* Multi-Context Management */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="glass-card mb-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Building className="w-5 h-5 text-[var(--axial-accent)]" />
                Contextes entreprise
              </h3>
              <Button
                variant="default"
                size="sm"
                onClick={() => setShowAddContext(!showAddContext)}
                className="flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Ajouter
              </Button>
            </div>

            <p className="text-sm text-muted-foreground mb-4">
              Ajoutez plusieurs contextes pour personnaliser vos analyses. Les contextes actifs sont utilisés par l&apos;IA.
            </p>

            {/* Storage quota bar */}
            {storageQuota && (
              <div className="mb-4 p-3 bg-muted/50 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground flex items-center gap-2">
                    <HardDrive className="w-4 h-4" />
                    Stockage utilisé
                  </span>
                  <span className="text-sm text-foreground">
                    {formatBytes(storageQuota.total_used_bytes)} / {formatBytes(storageQuota.max_bytes)}
                  </span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      storageQuota.used_percentage > 90 ? 'bg-red-500' :
                      storageQuota.used_percentage > 70 ? 'bg-yellow-500' : 'bg-cyan-500'
                    }`}
                    style={{ width: `${Math.min(storageQuota.used_percentage, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {contextError && (
              <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm mb-4">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {contextError}
              </div>
            )}

            {contextSuccess && (
              <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3 text-green-400 text-sm mb-4">
                <CheckCircle className="w-4 h-4 flex-shrink-0" />
                Contexte enregistré avec succès
              </div>
            )}

            {/* Add new context form */}
            {showAddContext && (
              <div className="mb-4 p-4 bg-muted/50 rounded-xl border border-border">
                <h4 className="text-sm font-medium text-foreground mb-3">Nouveau contexte</h4>

                {/* Context name */}
                <div className="mb-3">
                  <input
                    type="text"
                    value={contextName}
                    onChange={(e) => setContextName(e.target.value)}
                    className="glass-input w-full px-4"
                    placeholder="Nom du contexte (ex: Présentation entreprise)"
                  />
                </div>

                {/* Context type selector */}
                <div className="flex gap-2 mb-3">
                  <Button
                    type="button"
                    variant={contextType === 'text' ? 'accent' : 'glass'}
                    onClick={() => setContextType('text')}
                    size="sm"
                    className="flex-1 flex items-center justify-center gap-2"
                  >
                    <Type className="w-4 h-4" />
                    Texte
                  </Button>
                  <Button
                    type="button"
                    variant={contextType === 'document' ? 'accent' : 'glass'}
                    onClick={() => setContextType('document')}
                    size="sm"
                    className="flex-1 flex items-center justify-center gap-2"
                  >
                    <FileText className="w-4 h-4" />
                    Document
                  </Button>
                </div>

                {/* Text input */}
                {contextType === 'text' && (
                  <div className="space-y-2">
                    <textarea
                      value={contextText}
                      onChange={(e) => setContextText(e.target.value)}
                      className="glass-input w-full h-32 resize-none px-4"
                      placeholder="Décrivez votre entreprise, secteur, objectifs..."
                      maxLength={50000}
                    />
                    <p className="text-xs text-muted-foreground text-right">
                      {contextText.length} / 50 000 caractères
                    </p>
                  </div>
                )}

                {/* Document upload */}
                {contextType === 'document' && (
                  <div className="space-y-2">
                    <label className="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-border rounded-xl cursor-pointer hover:bg-muted/50 transition-colors">
                      <div className="flex flex-col items-center justify-center py-4">
                        <Upload className="w-6 h-6 text-muted-foreground mb-1" />
                        <p className="text-sm text-muted-foreground">
                          {contextDocument ? contextDocument.name : 'Cliquez pour upload'}
                        </p>
                        <p className="text-xs text-muted-foreground">PDF, DOCX, TXT (max 10 Mo)</p>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx,.txt"
                        onChange={handleFileChange}
                      />
                    </label>
                  </div>
                )}

                <div className="flex gap-2 mt-3">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { setShowAddContext(false); resetContextForm(); }}
                  >
                    Annuler
                  </Button>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={handleSaveContext}
                    disabled={isSavingContext || (contextType === 'text' && !contextText) || (contextType === 'document' && !contextDocument)}
                  >
                    {isSavingContext ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <Save className="w-4 h-4" />
                    )}
                    Enregistrer
                  </Button>
                </div>
              </div>
            )}

            {/* Contexts list */}
            {isLoadingContexts ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
              </div>
            ) : contexts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Building className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Aucun contexte enregistré</p>
                <p className="text-sm text-muted-foreground">Cliquez sur &quot;Ajouter&quot; pour créer votre premier contexte</p>
              </div>
            ) : (
              <div className="space-y-2">
                {contexts.map((ctx) => (
                  <div
                    key={ctx.id}
                    className={`flex items-center justify-between p-3 rounded-xl transition-all ${
                      ctx.is_active
                        ? 'bg-cyan-500/10 border border-cyan-500/30'
                        : 'bg-muted/50 border border-border'
                    }`}
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      {ctx.context_type === 'text' ? (
                        <Type className={`w-5 h-5 flex-shrink-0 ${ctx.is_active ? 'text-cyan-400' : 'text-muted-foreground'}`} />
                      ) : (
                        <FileText className={`w-5 h-5 flex-shrink-0 ${ctx.is_active ? 'text-cyan-400' : 'text-muted-foreground'}`} />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm font-medium truncate ${ctx.is_active ? 'text-cyan-400' : 'text-foreground'}`}>
                          {ctx.name}
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                          {ctx.preview ? `${ctx.preview.substring(0, 50)}...` : ctx.filename || 'Document'}
                          {' • '}{formatBytes(ctx.content_size)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleToggleContextActive(ctx.id, ctx.is_active)}
                        title={ctx.is_active ? 'Désactiver' : 'Activer'}
                        className="text-muted-foreground hover:text-foreground"
                      >
                        {ctx.is_active ? (
                          <ToggleRight className="w-5 h-5 text-cyan-400" />
                        ) : (
                          <ToggleLeft className="w-5 h-5" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteContext(ctx.id)}
                        title="Supprimer"
                        className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>

          {/* Password Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card"
          >
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-[var(--axial-accent)]" />
              Changer le mot de passe
            </h3>

            <form onSubmit={handleChangePassword} className="space-y-4">
              {passwordError && (
                <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {passwordError}
                </div>
              )}

              {passwordSuccess && (
                <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3 text-green-400 text-sm">
                  <CheckCircle className="w-4 h-4 flex-shrink-0" />
                  Mot de passe modifié avec succès
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Mot de passe actuel
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="glass-input w-full pl-12 pr-12"
                    placeholder="••••••••"
                    required
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowPasswords(!showPasswords)}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPasswords ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </Button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Nouveau mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="glass-input w-full pl-12 pr-4"
                    placeholder="••••••••"
                    required
                    minLength={6}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Confirmer le nouveau mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="glass-input w-full pl-12 pr-4"
                    placeholder="••••••••"
                    required
                    minLength={6}
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={isSavingPassword}
              >
                {isSavingPassword ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Lock className="w-5 h-5" />
                )}
                Changer le mot de passe
              </Button>
            </form>
          </motion.div>
        </div>
    </MainLayout>
  )
}


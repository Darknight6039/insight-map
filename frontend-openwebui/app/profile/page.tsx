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
  Building
} from 'lucide-react'
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

  // Context form
  const [contextType, setContextType] = useState<'text' | 'document'>('text')
  const [contextText, setContextText] = useState('')
  const [contextDocument, setContextDocument] = useState<File | null>(null)
  const [currentContextInfo, setCurrentContextInfo] = useState<{ type: string; name?: string; preview?: string } | null>(null)
  const [isSavingContext, setIsSavingContext] = useState(false)
  const [contextSuccess, setContextSuccess] = useState(false)
  const [contextError, setContextError] = useState('')

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

  // Fetch current context on load
  useEffect(() => {
    const fetchContext = async () => {
      if (!token) return
      try {
        const response = await fetch(`${API_URL}/context/current`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          const data = await response.json()
          if (data && data.type) {
            setCurrentContextInfo(data)
            if (data.type === 'text') {
              setContextType('text')
              setContextText(data.preview || '')
            } else {
              setContextType('document')
            }
          }
        }
      } catch (err) {
        console.log('No context found or error fetching')
      }
    }
    fetchContext()
  }, [token])

  const handleSaveContext = async () => {
    setContextError('')
    setContextSuccess(false)
    setIsSavingContext(true)

    try {
      if (contextType === 'text') {
        const response = await fetch(`${API_URL}/context/text`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ content: contextText })
        })
        if (!response.ok) throw new Error('Erreur lors de la sauvegarde')
        setCurrentContextInfo({ type: 'text', preview: contextText.substring(0, 100) })
      } else if (contextDocument) {
        const formData = new FormData()
        formData.append('file', contextDocument)
        const response = await fetch(`${API_URL}/context/upload`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })
        if (!response.ok) throw new Error('Erreur lors de l\'upload')
        setCurrentContextInfo({ type: 'document', name: contextDocument.name })
      }
      setContextSuccess(true)
      setTimeout(() => setContextSuccess(false), 3000)
    } catch (err) {
      setContextError('Erreur lors de la sauvegarde du contexte')
    } finally {
      setIsSavingContext(false)
    }
  }

  const handleDeleteContext = async () => {
    try {
      await fetch(`${API_URL}/context`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setCurrentContextInfo(null)
      setContextText('')
      setContextDocument(null)
    } catch (err) {
      setContextError('Erreur lors de la suppression')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
      if (!validTypes.includes(file.type)) {
        setContextError('Format non supporte. Utilisez PDF, DOCX ou TXT.')
        return
      }
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setContextError('Fichier trop volumineux (max 10 Mo)')
        return
      }
      setContextDocument(file)
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
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-400" />
              </Link>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                  <User className="w-6 h-6 text-[var(--axial-accent)]" />
                  Mon Profil
                </h1>
                <p className="text-gray-400 text-sm">Gérer vos informations et votre mot de passe</p>
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
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">
                  {user.full_name || user.email.split('@')[0]}
                </h2>
                <p className="text-gray-400 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {user.email}
                </p>
                <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
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
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
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
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Nom complet
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="glass-input w-full pl-12"
                    placeholder="Votre nom complet"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="glass-input w-full pl-12 opacity-50 cursor-not-allowed"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">L&apos;email ne peut pas être modifié</p>
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

          {/* Context Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="glass-card mb-6"
          >
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <Building className="w-5 h-5 text-[var(--axial-accent)]" />
              Contexte de votre entreprise
            </h3>
            <p className="text-sm text-gray-400 mb-4">
              Fournissez des informations sur votre entreprise pour personnaliser les analyses et veilles.
            </p>

            {contextError && (
              <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm mb-4">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {contextError}
              </div>
            )}

            {contextSuccess && (
              <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-3 text-green-400 text-sm mb-4">
                <CheckCircle className="w-4 h-4 flex-shrink-0" />
                Contexte enregistre avec succes
              </div>
            )}

            {/* Current context indicator */}
            {currentContextInfo && (
              <div className="flex items-center justify-between bg-cyan-500/10 border border-cyan-500/30 rounded-xl px-4 py-3 mb-4">
                <div className="flex items-center gap-3">
                  {currentContextInfo.type === 'text' ? (
                    <Type className="w-5 h-5 text-cyan-400" />
                  ) : (
                    <FileText className="w-5 h-5 text-cyan-400" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-cyan-400">
                      Contexte actif : {currentContextInfo.type === 'text' ? 'Texte' : 'Document'}
                    </p>
                    {currentContextInfo.name && (
                      <p className="text-xs text-gray-400">{currentContextInfo.name}</p>
                    )}
                    {currentContextInfo.preview && (
                      <p className="text-xs text-gray-400 truncate max-w-xs">
                        {currentContextInfo.preview}...
                      </p>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleDeleteContext}
                  title="Supprimer le contexte"
                  className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            )}

            {/* Context type selector */}
            <div className="flex gap-2 mb-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setContextType('text')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 h-auto rounded-xl transition-all ${
                  contextType === 'text'
                    ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                }`}
              >
                <Type className="w-5 h-5" />
                <span className="font-medium">Saisie texte</span>
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setContextType('document')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 h-auto rounded-xl transition-all ${
                  contextType === 'document'
                    ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                }`}
              >
                <FileText className="w-5 h-5" />
                <span className="font-medium">Document</span>
              </Button>
            </div>

            {/* Text input */}
            {contextType === 'text' && (
              <div className="space-y-3">
                <textarea
                  value={contextText}
                  onChange={(e) => setContextText(e.target.value)}
                  className="glass-input w-full h-40 resize-none"
                  placeholder="Decrivez votre entreprise, secteur d'activite, objectifs strategiques, marche cible, concurrents principaux..."
                  maxLength={5000}
                />
                <p className="text-xs text-gray-500 text-right">
                  {contextText.length} / 5000 caracteres
                </p>
              </div>
            )}

            {/* Document upload */}
            {contextType === 'document' && (
              <div className="space-y-3">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-white/20 rounded-xl cursor-pointer hover:bg-white/5 transition-colors">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-8 h-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-400">
                      {contextDocument 
                        ? contextDocument.name 
                        : 'Cliquez ou glissez votre document'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      PDF, DOCX, TXT (max 10 Mo)
                    </p>
                  </div>
                  <input 
                    type="file" 
                    className="hidden" 
                    accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                    onChange={handleFileChange}
                  />
                </label>
                {contextDocument && (
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <FileText className="w-4 h-4" />
                    <span>{contextDocument.name}</span>
                    <span className="text-gray-500">
                      ({(contextDocument.size / 1024).toFixed(1)} Ko)
                    </span>
                  </div>
                )}
              </div>
            )}

            <Button
              type="button"
              onClick={handleSaveContext}
              disabled={isSavingContext || (contextType === 'text' && !contextText) || (contextType === 'document' && !contextDocument)}
              className="mt-4"
            >
              {isSavingContext ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Save className="w-5 h-5" />
              )}
              Enregistrer le contexte
            </Button>
          </motion.div>

          {/* Password Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
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
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Mot de passe actuel
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
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
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Nouveau mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="glass-input w-full pl-12"
                    placeholder="••••••••"
                    required
                    minLength={6}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Confirmer le nouveau mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type={showPasswords ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="glass-input w-full pl-12"
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


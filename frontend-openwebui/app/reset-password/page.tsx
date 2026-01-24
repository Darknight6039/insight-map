'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Lock, Eye, EyeOff, CheckCircle, AlertCircle, ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ResetPasswordPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isValidating, setIsValidating] = useState(true)
  const [isValid, setIsValid] = useState(false)
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isSuccess, setIsSuccess] = useState(false)

  // Validate token on mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setIsValidating(false)
        setError('Token manquant')
        return
      }

      try {
        const response = await fetch(`${API_URL}/auth/validate-reset-token?token=${token}`)
        if (response.ok) {
          const data = await response.json()
          setIsValid(true)
          setEmail(data.email)
        } else {
          setError('Ce lien est invalide ou a expiré')
        }
      } catch (err) {
        setError('Erreur de connexion au serveur')
      } finally {
        setIsValidating(false)
      }
    }

    validateToken()
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    if (newPassword.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword })
      })

      if (response.ok) {
        setIsSuccess(true)
        setTimeout(() => {
          router.push('/login')
        }, 3000)
      } else {
        const data = await response.json()
        setError(data.detail || 'Une erreur est survenue')
      }
    } catch (err) {
      setError('Erreur de connexion au serveur')
    } finally {
      setIsLoading(false)
    }
  }

  if (isValidating) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex flex-col items-center gap-1">
            <span className="text-4xl font-bold tracking-tight text-primary">AXIAL</span>
            <span className="text-sm font-medium tracking-[0.3em] text-muted-foreground uppercase">Intelligence</span>
          </div>
          {isValid && email && (
            <p className="text-muted-foreground mt-4">
              Compte : <span className="text-foreground font-medium">{email}</span>
            </p>
          )}
        </div>

        {/* Main Card */}
        <Card className="border-border/50 shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Réinitialiser le mot de passe</CardTitle>
            <CardDescription>
              Choisissez un nouveau mot de passe sécurisé
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!isValid ? (
              <div className="text-center py-4">
                <div className="w-16 h-16 rounded-full bg-destructive/20 flex items-center justify-center mx-auto mb-4">
                  <AlertCircle className="w-8 h-8 text-destructive" />
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Lien invalide
                </h2>
                <p className="text-muted-foreground text-sm mb-4">
                  {error || 'Ce lien de réinitialisation est invalide ou a expiré.'}
                </p>
                <Link
                  href="/forgot-password"
                  className="text-primary hover:underline text-sm"
                >
                  Demander un nouveau lien
                </Link>
              </div>
            ) : isSuccess ? (
              <div className="text-center py-4">
                <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Mot de passe modifié
                </h2>
                <p className="text-muted-foreground text-sm">
                  Redirection vers la page de connexion...
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/30 rounded-lg px-4 py-3 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="newPassword">Nouveau mot de passe</Label>
                  <div className="relative">
                    <Input
                      id="newPassword"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="pr-10"
                      required
                      minLength={6}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <Eye className="w-4 h-4 text-muted-foreground" />
                      )}
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
                  <Input
                    id="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    minLength={6}
                  />
                </div>

                <Button type="submit" className="w-full gap-2" disabled={isLoading}>
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Lock className="h-4 w-4" />
                  )}
                  Réinitialiser le mot de passe
                </Button>
              </form>
            )}

            {/* Back to login */}
            <div className="mt-6 text-center">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-primary hover:underline text-sm"
              >
                <ArrowLeft className="w-4 h-4" />
                Retour à la connexion
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-6">
          © {new Date().getFullYear()} Axial Intelligence. Tous droits réservés.
        </p>
      </div>
    </div>
  )
}

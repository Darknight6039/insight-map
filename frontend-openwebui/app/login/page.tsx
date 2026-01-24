'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Eye, EyeOff, LogIn, Loader2, CreditCard, User, Ticket } from 'lucide-react'
import Link from 'next/link'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

type AuthMode = 'login' | 'register'

export default function LoginPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const initialMode = searchParams.get('mode') === 'register' ? 'register' : 'login'
  const [mode, setMode] = useState<AuthMode>(initialMode)

  // Update mode if query param changes
  useEffect(() => {
    const modeParam = searchParams.get('mode')
    if (modeParam === 'register') {
      setMode('register')
    }
  }, [searchParams])

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [invitationCode, setInvitationCode] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { signIn, signUp } = useSupabaseAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (mode === 'login') {
        await signIn(email, password)
      } else {
        await signUp(email, password, fullName, invitationCode)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login')
    setError('')
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
          <p className="text-muted-foreground mt-4">
            {mode === 'login'
              ? 'Connectez-vous pour accéder à la plateforme'
              : 'Rejoignez la plateforme d\'intelligence stratégique'
            }
          </p>
        </div>

        {/* Login Card */}
        <Card className="border-border/50 shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">
              {mode === 'login' ? 'Connexion' : 'Créer un compte'}
            </CardTitle>
            <CardDescription>
              {mode === 'login'
                ? 'Entrez vos identifiants pour continuer'
                : 'Remplissez le formulaire pour créer votre compte'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Error Message */}
              {error && (
                <div className="bg-destructive/10 border border-destructive/30 rounded-lg px-4 py-3 text-destructive text-sm">
                  {error}
                </div>
              )}

              {/* Full Name (Register only) */}
              {mode === 'register' && (
                <div className="space-y-2">
                  <Label htmlFor="fullName">Nom complet</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="fullName"
                      type="text"
                      placeholder="Jean Dupont"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="pl-10"
                      required={mode === 'register'}
                    />
                  </div>
                </div>
              )}

              {/* Email */}
              <div className="space-y-2">
                <Label htmlFor="email">Adresse email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="nom@entreprise.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>

              {/* Password */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Mot de passe</Label>
                  {mode === 'login' && (
                    <Link
                      href="/forgot-password"
                      className="text-sm text-primary hover:underline"
                    >
                      Mot de passe oublié ?
                    </Link>
                  )}
                </div>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pr-10"
                    required
                    autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
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

              {/* Invitation Code (Register only) */}
              {mode === 'register' && (
                <div className="space-y-2">
                  <Label htmlFor="invitationCode">Code d&apos;invitation</Label>
                  <div className="relative">
                    <Ticket className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="invitationCode"
                      type="text"
                      placeholder="Entrez votre code d'invitation"
                      value={invitationCode}
                      onChange={(e) => setInvitationCode(e.target.value)}
                      className="pl-10"
                      required={mode === 'register'}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Vous devez avoir reçu un code d&apos;invitation d&apos;un administrateur
                  </p>
                </div>
              )}

              {/* Submit Button */}
              <Button type="submit" className="w-full gap-2" disabled={isLoading}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <LogIn className="h-4 w-4" />
                )}
                {mode === 'login' ? 'Se connecter' : 'Créer mon compte'}
              </Button>
            </form>

            {/* Toggle Mode */}
            <div className="mt-6 text-center text-sm text-muted-foreground">
              {mode === 'login' ? (
                <>
                  Vous avez un code d&apos;invitation ?{' '}
                  <Button
                    variant="link"
                    onClick={toggleMode}
                    className="px-0 text-primary"
                  >
                    Créer un compte
                  </Button>
                </>
              ) : (
                <>
                  Vous avez déjà un compte ?{' '}
                  <Button
                    variant="link"
                    onClick={toggleMode}
                    className="px-0 text-primary"
                  >
                    Se connecter
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Pricing Link */}
        <div className="mt-6 text-center">
          <Button
            variant="outline"
            onClick={() => router.push('/pricing')}
            className="gap-2"
          >
            <CreditCard className="w-4 h-4" />
            Voir les tarifs
          </Button>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-6">
          © {new Date().getFullYear()} Axial Intelligence. Tous droits réservés.
        </p>
      </div>
    </div>
  )
}

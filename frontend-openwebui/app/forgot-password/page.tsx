'use client'

import { useState } from 'react'
import { Mail, ArrowLeft, Send, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })

      if (response.ok) {
        setIsSubmitted(true)
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
            Récupération de mot de passe
          </p>
        </div>

        {/* Main Card */}
        <Card className="border-border/50 shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Mot de passe oublié</CardTitle>
            <CardDescription>
              Entrez votre email pour demander une réinitialisation
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!isSubmitted ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="flex items-center gap-2 bg-destructive/10 border border-destructive/30 rounded-lg px-4 py-3 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                  </div>
                )}

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

                <Button type="submit" className="w-full gap-2" disabled={isLoading}>
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  Envoyer la demande
                </Button>
              </form>
            ) : (
              <div className="text-center py-4">
                <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  Demande envoyée
                </h2>
                <p className="text-muted-foreground text-sm mb-4">
                  Si cet email est associé à un compte, un administrateur pourra vous fournir
                  un lien de réinitialisation.
                </p>
                <p className="text-muted-foreground text-xs">
                  Contactez votre administrateur pour obtenir le lien.
                </p>
              </div>
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

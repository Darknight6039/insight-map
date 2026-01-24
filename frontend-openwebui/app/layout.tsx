import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Axial Intelligence - Strategic AI Platform',
  description: 'Plateforme d\'intelligence stratégique par IA. Rapports d\'analyse, chat expert et export PDF.',
  keywords: ['intelligence', 'stratégie', 'analyse', 'IA', 'consultation', 'rapports', 'business'],
  authors: [{ name: 'Axial' }],
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <meta name="theme-color" content="#0a050f" />
      </head>
      <body className={`${inter.className} min-h-screen bg-background text-foreground antialiased`}>
        <Providers>
          <div className="relative min-h-screen">
            {/* Main content */}
            <main className="relative z-10">
              {children}
            </main>

            {/* Toast notifications */}
            <Toaster
              position="top-right"
              theme="dark"
              richColors
              closeButton
            />
          </div>
        </Providers>
      </body>
    </html>
  )
}

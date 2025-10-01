import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'

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
    <html lang="fr" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
        <meta name="theme-color" content="#003366" />
      </head>
      <body className={`${inter.className} min-h-screen`}>
        <div className="relative min-h-screen">
          {/* Background liquid blobs */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none">
            <div className="liquid-blob absolute top-1/4 left-1/4 w-96 h-96 rounded-full"></div>
            <div className="liquid-blob absolute top-3/4 right-1/4 w-80 h-80 rounded-full" style={{animationDelay: '2s'}}></div>
            <div className="liquid-blob absolute top-1/2 left-3/4 w-72 h-72 rounded-full" style={{animationDelay: '4s'}}></div>
          </div>
          
          {/* Main content */}
          <main className="relative z-10">
            {children}
          </main>
          
          {/* Toast notifications */}
          <Toaster 
            position="top-right"
            toastOptions={{
              className: 'glass-card text-white',
              duration: 4000,
              style: {
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: '#e2e8f0',
              },
            }}
          />
        </div>
      </body>
    </html>
  )
}

'use client'

import { ReactNode } from "react"
import Header from "./Header"
import ChatWidget from "../ChatWidget"
import { useSupabaseAuth } from "@/context/SupabaseAuthContext"

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const { isAuthenticated } = useSupabaseAuth()

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-8">
        {children}
      </main>

      {/* ChatWidget - only show when authenticated */}
      {isAuthenticated && <ChatWidget />}
    </div>
  )
}

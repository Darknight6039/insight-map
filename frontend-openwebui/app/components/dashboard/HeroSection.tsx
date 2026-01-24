'use client'

import { useTranslation } from "@/context/LanguageContext"

export default function HeroSection() {
  const { t } = useTranslation()

  return (
    <div className="relative overflow-hidden rounded-2xl bg-card border border-border p-8 mb-10">
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/5" />

      <div className="relative flex flex-col items-center text-center gap-4">
        {/* Brand */}
        <div className="flex flex-col items-center leading-tight">
          <h1 className="text-4xl font-bold text-foreground tracking-wide">AXIAL</h1>
          <span className="text-lg text-primary font-semibold tracking-[0.3em]">INTELLIGENCE</span>
        </div>

        {/* Tagline */}
        <p className="text-muted-foreground max-w-lg mt-2">
          {t('home.tagline') || "Plateforme d'intelligence stratégique par IA. Rapports d'analyse, chat expert et export PDF."}
        </p>
      </div>
    </div>
  )
}

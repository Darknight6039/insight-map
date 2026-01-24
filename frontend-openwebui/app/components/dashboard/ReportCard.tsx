'use client'

import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface ReportCardProps {
  title: string
  description: string
  icon: LucideIcon
  gradient: "purple" | "violet" | "pink" | "orange" | "teal" | "blue"
  onClick?: () => void
}

const gradientClasses = {
  purple: "gradient-icon-purple",
  violet: "gradient-icon-violet",
  pink: "gradient-icon-pink",
  orange: "gradient-icon-orange",
  teal: "gradient-icon-teal",
  blue: "gradient-icon-blue",
}

export default function ReportCard({ title, description, icon: Icon, gradient, onClick }: ReportCardProps) {
  return (
    <div
      onClick={onClick}
      className="group p-6 rounded-xl bg-card border border-border card-interactive animate-fade-in"
    >
      <div className="flex items-start gap-4">
        <div
          className={cn(
            "w-12 h-12 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-110",
            gradientClasses[gradient]
          )}
        >
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div className="flex flex-col gap-1">
          <h3 className="font-semibold text-foreground">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
    </div>
  )
}

'use client'

import { Edit, Play, Pause, History, Trash2, Search, Clock, Mail, Calendar, PlayCircle } from "lucide-react"
import { Badge } from "../ui/badge"
import { Button } from "../ui/button"
import { useTranslation } from "../../context/LanguageContext"

interface VeilleCardProps {
  id: number
  title: string
  description: string
  isActive: boolean
  reportType?: string
  sourceCount?: number
  schedule: string
  recipients: number
  nextRun?: string
  tags?: string[]
  onEdit?: () => void
  onToggle?: () => void
  onTrigger?: () => void
  onHistory?: () => void
  onDelete?: () => void
  isTriggering?: boolean
}

export default function VeilleCard({
  id,
  title,
  description,
  isActive,
  reportType = "Analyse Approfondie",
  sourceCount = 5,
  schedule,
  recipients,
  nextRun,
  tags = [],
  onEdit,
  onToggle,
  onTrigger,
  onHistory,
  onDelete,
  isTriggering = false,
}: VeilleCardProps) {
  const { t } = useTranslation()

  return (
    <div className="p-6 rounded-xl bg-card border border-border transition-all hover:border-primary/30 hover:shadow-md">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <h3 className="font-semibold text-foreground truncate">{title}</h3>
          {isActive ? (
            <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/30 text-xs shrink-0">
              {t('watches.active')}
            </Badge>
          ) : (
            <Badge variant="outline" className="text-muted-foreground text-xs shrink-0">
              {t('watches.inactive')}
            </Badge>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 shrink-0 ml-4">
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9"
            onClick={onEdit}
            title={t('common.edit')}
          >
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9"
            onClick={onTrigger}
            disabled={isTriggering}
            title={t('watches.triggerNow')}
          >
            <PlayCircle className={`w-4 h-4 ${isTriggering ? 'animate-spin' : ''}`} />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9"
            onClick={onToggle}
            title={isActive ? t('watches.pause') : t('watches.activate')}
          >
            {isActive ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9"
            onClick={onHistory}
            title={t('watches.history')}
          >
            <History className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 hover:text-destructive hover:border-destructive"
            onClick={onDelete}
            title={t('common.delete')}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{description}</p>

      {/* Meta Info */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mb-4">
        <div className="flex items-center gap-1.5">
          <Search className="w-4 h-4" />
          <span>{reportType} ({sourceCount} sources)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span>{schedule}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Mail className="w-4 h-4" />
          <span>{recipients} {t('watches.recipient')}{recipients > 1 ? 's' : ''}</span>
        </div>
        {nextRun && (
          <div className="flex items-center gap-1.5 text-primary">
            <Calendar className="w-4 h-4" />
            <span>{t('watches.nextRun')}: {nextRun}</span>
          </div>
        )}
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, index) => (
            <Badge key={index} variant="secondary" className="text-xs font-normal">
              {tag}
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}

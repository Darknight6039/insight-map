'use client'

import { useState, useMemo, useEffect } from "react"
import { Plus, Clock, Calendar, CalendarDays, CalendarClock, Edit } from "lucide-react"
import { useTranslation } from "../../context/LanguageContext"
import { Button } from "../ui/button"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "../ui/sheet"

interface NewVeilleSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit?: (data: VeilleFormData) => void
  editData?: VeilleFormData | null
  isEditing?: boolean
}

export interface VeilleFormData {
  id?: number
  name: string
  subject: string
  sector: string
  reportType: string
  keywords: string
  frequency: string
  frequencyLabel: string
  time: string
  dayOfWeek: string
  dayOfMonth: string
  recipients: string
  cronExpression?: string
}

const frequencyOptions = [
  { id: "every-hour", label: "Toutes les heures", icon: Clock, category: "frequent", cron: "0 * * * *" },
  { id: "every-6-hours", label: "Toutes les 6 heures", icon: Clock, category: "frequent", cron: "0 */6 * * *" },
  { id: "every-12-hours", label: "Toutes les 12 heures", icon: Clock, category: "frequent", cron: "0 */12 * * *" },
  { id: "daily-morning", label: "Tous les jours à 8h", icon: Calendar, category: "daily", cron: "0 8 * * *" },
  { id: "daily-noon", label: "Tous les jours à 12h", icon: Calendar, category: "daily", cron: "0 12 * * *" },
  { id: "daily-evening", label: "Tous les jours à 18h", icon: Calendar, category: "daily", cron: "0 18 * * *" },
  { id: "daily-custom", label: "Tous les jours (heure personnalisée)", icon: Calendar, category: "daily", cron: "custom" },
  { id: "weekdays-morning", label: "Jours ouvrés à 8h", icon: CalendarDays, category: "weekly", cron: "0 8 * * 1-5" },
  { id: "weekdays-evening", label: "Jours ouvrés à 18h", icon: CalendarDays, category: "weekly", cron: "0 18 * * 1-5" },
  { id: "weekly-monday", label: "Chaque lundi à 9h", icon: CalendarDays, category: "weekly", cron: "0 9 * * 1" },
  { id: "weekly-friday", label: "Chaque vendredi à 17h", icon: CalendarDays, category: "weekly", cron: "0 17 * * 5" },
  { id: "weekly-custom", label: "Hebdomadaire (personnalisé)", icon: CalendarDays, category: "weekly", cron: "custom" },
  { id: "biweekly", label: "Toutes les 2 semaines", icon: CalendarClock, category: "monthly", cron: "0 9 */14 * *" },
  { id: "monthly-1st", label: "Le 1er de chaque mois", icon: CalendarClock, category: "monthly", cron: "0 9 1 * *" },
  { id: "monthly-15th", label: "Le 15 de chaque mois", icon: CalendarClock, category: "monthly", cron: "0 9 15 * *" },
  { id: "monthly-last", label: "Dernier jour du mois", icon: CalendarClock, category: "monthly", cron: "0 9 L * *" },
  { id: "monthly-custom", label: "Mensuel (personnalisé)", icon: CalendarClock, category: "monthly", cron: "custom" },
  { id: "quarterly", label: "Trimestriel", icon: CalendarClock, category: "other", cron: "0 9 1 */3 *" },
]

const sectors = [
  { id: "general", label: "Général" },
  { id: "finance_banque", label: "Finance & Banque" },
  { id: "tech_digital", label: "Tech & Digital" },
  { id: "sante", label: "Santé" },
  { id: "energie", label: "Énergie" },
  { id: "retail_commerce", label: "Retail & Commerce" },
  { id: "immobilier", label: "Immobilier" },
  { id: "industrie", label: "Industrie" },
  { id: "services", label: "Services" },
]

const reportTypes = [
  { id: "synthese_executive", label: "Synthèse Exécutive" },
  { id: "analyse_concurrentielle", label: "Analyse Concurrentielle" },
  { id: "veille_technologique", label: "Veille Technologique" },
  { id: "analyse_risques", label: "Analyse des Risques" },
  { id: "etude_marche", label: "Étude de Marché" },
  { id: "analyse_reglementaire", label: "Analyse Réglementaire" },
]

const hours = Array.from({ length: 24 }, (_, i) => ({
  value: i.toString(),
  label: `${i.toString().padStart(2, "0")}:00`
}))

const daysOfWeek = [
  { value: "1", label: "Lundi" },
  { value: "2", label: "Mardi" },
  { value: "3", label: "Mercredi" },
  { value: "4", label: "Jeudi" },
  { value: "5", label: "Vendredi" },
  { value: "6", label: "Samedi" },
  { value: "0", label: "Dimanche" },
]

const daysOfMonth = Array.from({ length: 31 }, (_, i) => ({
  value: (i + 1).toString(),
  label: `${i + 1}`
}))

const defaultFormData: VeilleFormData = {
  name: "",
  subject: "",
  sector: "general",
  reportType: "synthese_executive",
  keywords: "",
  frequency: "daily-morning",
  frequencyLabel: "Tous les jours à 8h",
  time: "8",
  dayOfWeek: "1",
  dayOfMonth: "1",
  recipients: "",
}

export default function NewVeilleSheet({
  open,
  onOpenChange,
  onSubmit,
  editData,
  isEditing = false
}: NewVeilleSheetProps) {
  const { t } = useTranslation()
  const [formData, setFormData] = useState<VeilleFormData>(defaultFormData)

  // Reset form when opening/closing or when editData changes
  useEffect(() => {
    if (open && editData) {
      setFormData(editData)
    } else if (!open) {
      setFormData(defaultFormData)
    }
  }, [open, editData])

  const showTimeSelect = formData.frequency.includes("custom")
  const showDayOfWeekSelect = formData.frequency === "weekly-custom"
  const showDayOfMonthSelect = formData.frequency === "monthly-custom"

  const scheduleDescription = useMemo(() => {
    const freq = frequencyOptions.find(f => f.id === formData.frequency)
    if (!freq) return ""

    if (formData.frequency === "daily-custom") {
      return `Tous les jours à ${formData.time.padStart(2, "0")}:00`
    }
    if (formData.frequency === "weekly-custom") {
      const day = daysOfWeek.find(d => d.value === formData.dayOfWeek)?.label
      return `Chaque ${day} à ${formData.time.padStart(2, "0")}:00`
    }
    if (formData.frequency === "monthly-custom") {
      return `Le ${formData.dayOfMonth} de chaque mois à ${formData.time.padStart(2, "0")}:00`
    }
    return freq.label
  }, [formData])

  const generateCronExpression = (): string => {
    const freq = frequencyOptions.find(f => f.id === formData.frequency)
    if (!freq) return "0 8 * * *"

    if (freq.cron !== "custom") {
      return freq.cron
    }

    const minute = "0"
    const hour = formData.time

    if (formData.frequency === "daily-custom") {
      return `${minute} ${hour} * * *`
    }
    if (formData.frequency === "weekly-custom") {
      return `${minute} ${hour} * * ${formData.dayOfWeek}`
    }
    if (formData.frequency === "monthly-custom") {
      return `${minute} ${hour} ${formData.dayOfMonth} * *`
    }

    return "0 8 * * *"
  }

  const handleFrequencyChange = (value: string) => {
    const freq = frequencyOptions.find(f => f.id === value)
    setFormData({
      ...formData,
      frequency: value,
      frequencyLabel: freq?.label || value
    })
  }

  const handleSubmit = () => {
    const cronExpression = generateCronExpression()
    onSubmit?.({
      ...formData,
      frequencyLabel: scheduleDescription,
      cronExpression
    })
    setFormData(defaultFormData)
    onOpenChange(false)
  }

  const isFormValid = formData.name.trim() && formData.subject.trim() && formData.recipients.trim()

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-xl overflow-y-auto bg-background">
        <SheetHeader className="mb-6">
          <SheetTitle className="flex items-center gap-2 text-primary">
            {isEditing ? (
              <>
                <Edit className="w-5 h-5" />
                {t('watches.editWatch')}
              </>
            ) : (
              <>
                <Plus className="w-5 h-5" />
                {t('watches.newWatch')}
              </>
            )}
          </SheetTitle>
        </SheetHeader>

        <div className="space-y-6">
          {/* Name */}
          <div className="space-y-2">
            <Label>{t('watches.watchName')}</Label>
            <Input
              placeholder={t('watches.watchNamePlaceholder')}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          {/* Subject */}
          <div className="space-y-2">
            <Label>{t('watches.topicToAnalyze')}</Label>
            <Input
              placeholder={t('watches.topicPlaceholder')}
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            />
          </div>

          {/* Sector & Report Type */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>{t('watches.sector')}</Label>
              <Select value={formData.sector} onValueChange={(v) => setFormData({ ...formData, sector: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {sectors.map((s) => (
                    <SelectItem key={s.id} value={s.id}>{t(`watches.sectors.${s.id}`) || s.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>{t('watches.reportType')}</Label>
              <Select value={formData.reportType} onValueChange={(v) => setFormData({ ...formData, reportType: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {reportTypes.map((r) => (
                    <SelectItem key={r.id} value={r.id}>{t(`analysis.types.${r.id}`) || r.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Keywords */}
          <div className="space-y-2">
            <Label>{t('watches.keywords')}</Label>
            <Input
              placeholder={t('watches.keywordsPlaceholder')}
              value={formData.keywords}
              onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
            />
          </div>

          {/* Frequency */}
          <div className="space-y-3">
            <Label>{t('watches.executionFrequency')}</Label>
            <Select value={formData.frequency} onValueChange={handleFrequencyChange}>
              <SelectTrigger className="h-12">
                <SelectValue>
                  <div className="flex items-center gap-2">
                    {(() => {
                      const freq = frequencyOptions.find(f => f.id === formData.frequency)
                      const Icon = freq?.icon || Clock
                      return (
                        <>
                          <Icon className="w-4 h-4 text-primary" />
                          <span>{freq?.label}</span>
                        </>
                      )
                    })()}
                  </div>
                </SelectValue>
              </SelectTrigger>
              <SelectContent className="max-h-80">
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">Fréquent</div>
                {frequencyOptions.filter(f => f.category === "frequent").map((freq) => (
                  <SelectItem key={freq.id} value={freq.id}>
                    <div className="flex items-center gap-2">
                      <freq.icon className="w-4 h-4 text-muted-foreground" />
                      {freq.label}
                    </div>
                  </SelectItem>
                ))}
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground mt-2">Quotidien</div>
                {frequencyOptions.filter(f => f.category === "daily").map((freq) => (
                  <SelectItem key={freq.id} value={freq.id}>
                    <div className="flex items-center gap-2">
                      <freq.icon className="w-4 h-4 text-muted-foreground" />
                      {freq.label}
                    </div>
                  </SelectItem>
                ))}
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground mt-2">Hebdomadaire</div>
                {frequencyOptions.filter(f => f.category === "weekly").map((freq) => (
                  <SelectItem key={freq.id} value={freq.id}>
                    <div className="flex items-center gap-2">
                      <freq.icon className="w-4 h-4 text-muted-foreground" />
                      {freq.label}
                    </div>
                  </SelectItem>
                ))}
                <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground mt-2">Mensuel & Plus</div>
                {frequencyOptions.filter(f => f.category === "monthly" || f.category === "other").map((freq) => (
                  <SelectItem key={freq.id} value={freq.id}>
                    <div className="flex items-center gap-2">
                      <freq.icon className="w-4 h-4 text-muted-foreground" />
                      {freq.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Custom Time/Day Selects */}
          {(showTimeSelect || showDayOfWeekSelect || showDayOfMonthSelect) && (
            <div className="grid grid-cols-3 gap-4">
              {showDayOfWeekSelect && (
                <div className="space-y-2">
                  <Label>Jour</Label>
                  <Select value={formData.dayOfWeek} onValueChange={(v) => setFormData({ ...formData, dayOfWeek: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {daysOfWeek.map((d) => (
                        <SelectItem key={d.value} value={d.value}>{d.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              {showDayOfMonthSelect && (
                <div className="space-y-2">
                  <Label>Jour du mois</Label>
                  <Select value={formData.dayOfMonth} onValueChange={(v) => setFormData({ ...formData, dayOfMonth: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {daysOfMonth.map((d) => (
                        <SelectItem key={d.value} value={d.value}>{d.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
              {showTimeSelect && (
                <div className="space-y-2">
                  <Label>Heure</Label>
                  <Select value={formData.time} onValueChange={(v) => setFormData({ ...formData, time: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {hours.map((h) => (
                        <SelectItem key={h.value} value={h.value}>{h.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          )}

          {/* Schedule Summary */}
          <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
            <div className="flex items-center gap-2 text-primary mb-1">
              <CalendarClock className="w-4 h-4" />
              <span className="text-sm font-medium">Planification</span>
            </div>
            <p className="text-foreground font-medium">{scheduleDescription}</p>
          </div>

          {/* Recipients */}
          <div className="space-y-2">
            <Label>{t('watches.emailRecipients')}</Label>
            <Input
              placeholder={t('watches.emailRecipientsPlaceholder')}
              value={formData.recipients}
              onChange={(e) => setFormData({ ...formData, recipients: e.target.value })}
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={handleSubmit} disabled={!isFormValid} className="gap-2">
              {isEditing ? t('watches.saveChanges') : t('watches.createWatch')}
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}

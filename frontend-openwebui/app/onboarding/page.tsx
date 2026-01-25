'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Building2, Rocket, Users, ChevronRight, ChevronLeft } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Checkbox } from '../components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group'
import { useSupabaseAuth } from '../context/SupabaseAuthContext'
import { useTranslation } from '../context/LanguageContext'
import { cn } from '@/lib/utils'

type OrganizationType = 'startup' | 'support_structure' | 'other' | ''

interface OnboardingData {
  organizationName: string
  country: string
  organizationType: OrganizationType
  otherType: string
  sector: string
  employeeCount: string
  revenueRange: string
  startupStage: string
  technologies: string[]
  isAIStartup: boolean | null
  aiTypes: string[]
  structureTypes: string[]
  startupsAccompanied: string
  accompaniedStages: string[]
  specializationSectors: string[]
  accompanimentTypes: string[]
}

const initialData: OnboardingData = {
  organizationName: '',
  country: '',
  organizationType: '',
  otherType: '',
  sector: '',
  employeeCount: '',
  revenueRange: '',
  startupStage: '',
  technologies: [],
  isAIStartup: null,
  aiTypes: [],
  structureTypes: [],
  startupsAccompanied: '',
  accompaniedStages: [],
  specializationSectors: [],
  accompanimentTypes: [],
}

const countries = [
  'France', 'Belgique', 'Suisse', 'Canada', 'Luxembourg', 'Maroc', 'Tunisie',
  'Sénégal', "Côte d'Ivoire", 'Allemagne', 'Espagne', 'Italie', 'Royaume-Uni', 'États-Unis', 'Autre'
]

const sectors = [
  'Fintech', 'Healthtech', 'Edtech', 'Cleantech', 'Foodtech', 'Legaltech',
  'Insurtech', 'Proptech', 'Retailtech', 'Logistique', 'Cybersécurité', 'E-commerce', 'Autre'
]

const employeeRanges = ['1–5', '6–10', '11–25', '26–50', '51–100', '100+']
const revenueRanges = ['0 – 100k€', '100k€ – 500k€', '500k€ – 1M€', '1M€ – 5M€', '5M€+']
const startupStages = ['Bootstrap', 'Pre-seed', 'Seed', 'Série A', 'Série B', 'Série C ou plus']
const technologyOptions = ['IA / Machine Learning', 'SaaS', 'Fintech', 'Web3 / Blockchain', 'Data / Analytics', 'Autre']
const aiTypeOptions = ['LLM / NLP', 'Computer Vision', 'Recommandation', 'Automatisation / Agents', 'Autre']
const structureTypeOptions = ['Incubateur', 'Accélérateur', 'Association', 'Fonds VC', 'Fonds VC avec programme d\'accélération']
const startupsAccompaniedRanges = ['<10', '10–25', '26–50', '50+']
const accompaniedStageOptions = ['Idéation', 'Pre-seed', 'Seed', 'Série A+']
const specializationSectorOptions = ['Fintech', 'Healthtech', 'Edtech', 'Cleantech', 'Deeptech', 'Impact', 'IA', 'SaaS', 'Généraliste']
const accompanimentTypeOptions = ['Mentorat', 'Financement', 'Go-to-market', 'Produit / Tech', 'IA / Data', 'Juridique / Réglementaire']

export default function OnboardingPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { token } = useSupabaseAuth()
  const [currentStep, setCurrentStep] = useState(1)
  const [data, setData] = useState<OnboardingData>(initialData)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const totalSteps = data.organizationType === 'startup' || data.organizationType === 'support_structure' ? 2 : 1

  const updateData = (field: keyof OnboardingData, value: any) => {
    setData(prev => ({ ...prev, [field]: value }))
  }

  const toggleArrayValue = (field: keyof OnboardingData, value: string) => {
    const currentArray = data[field] as string[]
    if (currentArray.includes(value)) {
      updateData(field, currentArray.filter(v => v !== value))
    } else {
      updateData(field, [...currentArray, value])
    }
  }

  const canProceed = () => {
    if (currentStep === 1) {
      return data.organizationName && data.country && data.organizationType &&
        (data.organizationType !== 'other' || data.otherType)
    }
    return true
  }

  const formatCompanyProfileContent = (): string => {
    let content = `# Fiche Entreprise\n\n`
    content += `**Nom de l'organisation:** ${data.organizationName}\n`
    content += `**Pays:** ${data.country}\n`
    content += `**Type:** ${data.organizationType === 'startup' ? 'Startup' : data.organizationType === 'support_structure' ? 'Structure d\'accompagnement' : data.otherType || 'Autre'}\n\n`

    if (data.organizationType === 'startup') {
      if (data.sector) content += `**Secteur:** ${data.sector}\n`
      if (data.employeeCount) content += `**Nombre d'employés:** ${data.employeeCount}\n`
      if (data.revenueRange) content += `**Chiffre d'affaires:** ${data.revenueRange}\n`
      if (data.startupStage) content += `**Stade:** ${data.startupStage}\n`
      if (data.technologies.length > 0) content += `**Technologies:** ${data.technologies.join(', ')}\n`
      if (data.isAIStartup !== null) content += `**Startup IA:** ${data.isAIStartup ? 'Oui' : 'Non'}\n`
      if (data.aiTypes.length > 0) content += `**Types d'IA:** ${data.aiTypes.join(', ')}\n`
    } else if (data.organizationType === 'support_structure') {
      if (data.structureTypes.length > 0) content += `**Types de structure:** ${data.structureTypes.join(', ')}\n`
      if (data.startupsAccompanied) content += `**Startups accompagnées:** ${data.startupsAccompanied}\n`
      if (data.accompaniedStages.length > 0) content += `**Stades accompagnés:** ${data.accompaniedStages.join(', ')}\n`
      if (data.specializationSectors.length > 0) content += `**Secteurs de spécialisation:** ${data.specializationSectors.join(', ')}\n`
      if (data.accompanimentTypes.length > 0) content += `**Types d'accompagnement:** ${data.accompanimentTypes.join(', ')}\n`
    }

    return content
  }

  const saveCompanyProfile = async () => {
    if (!token) return false

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      const content = formatCompanyProfileContent()

      const response = await fetch(`${apiUrl}/api/contexts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: 'Fiche Entreprise',
          context_type: 'company_profile',
          content: content,
          is_active: true
        })
      })

      return response.ok
    } catch (error) {
      console.error('Error saving company profile:', error)
      return false
    }
  }

  const handleNext = async () => {
    if (currentStep < totalSteps) {
      setCurrentStep(prev => prev + 1)
    } else {
      setIsSubmitting(true)
      const success = await saveCompanyProfile()
      setIsSubmitting(false)

      if (success) {
        router.push('/')
      } else {
        console.error('Failed to save company profile')
        router.push('/')
      }
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleSkip = () => {
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl shadow-xl border-border/50">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full bg-primary/10">
              <Building2 className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl">{t('onboarding.title') || 'Configurez votre profil entreprise'}</CardTitle>
          <CardDescription className="text-base">
            {t('onboarding.subtitle') || 'Ces informations permettront de personnaliser vos analyses'}
          </CardDescription>

          {/* Progress indicator */}
          <div className="flex items-center justify-center gap-2 mt-4">
            {Array.from({ length: totalSteps }, (_, i) => (
              <div
                key={i}
                className={cn(
                  'h-2 rounded-full transition-all',
                  i + 1 === currentStep ? 'w-8 bg-primary' : 'w-2 bg-muted',
                  i + 1 < currentStep && 'bg-primary/50'
                )}
              />
            ))}
          </div>
        </CardHeader>

        <CardContent className="space-y-6 pt-4">
          {currentStep === 1 && (
            <div className="space-y-5">
              <h3 className="font-semibold text-lg border-b pb-2">
                {t('onboarding.step1.title') || 'Informations générales'}
              </h3>

              {/* Organization Name */}
              <div className="space-y-2">
                <Label htmlFor="orgName">{t('onboarding.step1.orgName') || "Nom de l'organisation"}</Label>
                <Input
                  id="orgName"
                  value={data.organizationName}
                  onChange={(e) => updateData('organizationName', e.target.value)}
                  placeholder={t('onboarding.step1.orgNamePlaceholder') || 'Votre entreprise'}
                />
              </div>

              {/* Country */}
              <div className="space-y-2">
                <Label>{t('onboarding.step1.country') || 'Pays'}</Label>
                <Select value={data.country} onValueChange={(v) => updateData('country', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder={t('onboarding.step1.countryPlaceholder') || 'Sélectionnez un pays'} />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {countries.map(country => (
                      <SelectItem key={country} value={country}>{country}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Organization Type */}
              <div className="space-y-3">
                <Label>{t('onboarding.step1.orgType') || "Type d'organisation"}</Label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => updateData('organizationType', 'startup')}
                    className={cn(
                      'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
                      data.organizationType === 'startup'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    )}
                  >
                    <Rocket className="h-6 w-6" />
                    <span className="font-medium">Startup</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => updateData('organizationType', 'support_structure')}
                    className={cn(
                      'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
                      data.organizationType === 'support_structure'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    )}
                  >
                    <Users className="h-6 w-6" />
                    <span className="font-medium text-sm">Structure d'accompagnement</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => updateData('organizationType', 'other')}
                    className={cn(
                      'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all',
                      data.organizationType === 'other'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    )}
                  >
                    <Building2 className="h-6 w-6" />
                    <span className="font-medium">Autre</span>
                  </button>
                </div>

                {data.organizationType === 'other' && (
                  <Input
                    value={data.otherType}
                    onChange={(e) => updateData('otherType', e.target.value)}
                    placeholder={t('onboarding.step1.otherPlaceholder') || 'Précisez...'}
                    className="mt-3"
                  />
                )}
              </div>
            </div>
          )}

          {currentStep === 2 && data.organizationType === 'startup' && (
            <div className="space-y-5">
              <h3 className="font-semibold text-lg border-b pb-2">
                {t('onboarding.step2.startupTitle') || 'Informations startup'}
              </h3>

              {/* Sector */}
              <div className="space-y-2">
                <Label>{t('onboarding.step2.sector') || "Secteur d'activité"}</Label>
                <Select value={data.sector} onValueChange={(v) => updateData('sector', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un secteur" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {sectors.map(sector => (
                      <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Employee Count */}
              <div className="space-y-2">
                <Label>{t('onboarding.step2.employees') || "Nombre d'employés"}</Label>
                <Select value={data.employeeCount} onValueChange={(v) => updateData('employeeCount', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez une tranche" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {employeeRanges.map(range => (
                      <SelectItem key={range} value={range}>{range}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Revenue Range */}
              <div className="space-y-2">
                <Label>{t('onboarding.step2.revenue') || "Chiffre d'affaires"}</Label>
                <Select value={data.revenueRange} onValueChange={(v) => updateData('revenueRange', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez une tranche" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {revenueRanges.map(range => (
                      <SelectItem key={range} value={range}>{range}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Startup Stage */}
              <div className="space-y-2">
                <Label>{t('onboarding.step2.stage') || 'Stade de développement'}</Label>
                <Select value={data.startupStage} onValueChange={(v) => updateData('startupStage', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez un stade" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {startupStages.map(stage => (
                      <SelectItem key={stage} value={stage}>{stage}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Technologies */}
              <div className="space-y-3">
                <Label>{t('onboarding.step2.technologies') || 'Technologies utilisées'}</Label>
                <div className="grid grid-cols-2 gap-2">
                  {technologyOptions.map(tech => (
                    <div key={tech} className="flex items-center space-x-2">
                      <Checkbox
                        id={`tech-${tech}`}
                        checked={data.technologies.includes(tech)}
                        onCheckedChange={() => toggleArrayValue('technologies', tech)}
                      />
                      <label htmlFor={`tech-${tech}`} className="text-sm cursor-pointer">
                        {tech}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Is AI Startup */}
              <div className="space-y-3">
                <Label>{t('onboarding.step2.isAIStartup') || 'Startup IA ?'}</Label>
                <RadioGroup
                  value={data.isAIStartup === null ? '' : data.isAIStartup ? 'yes' : 'no'}
                  onValueChange={(v) => updateData('isAIStartup', v === 'yes')}
                  className="flex gap-4"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="yes" id="ai-yes" />
                    <label htmlFor="ai-yes" className="cursor-pointer">Oui</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="no" id="ai-no" />
                    <label htmlFor="ai-no" className="cursor-pointer">Non</label>
                  </div>
                </RadioGroup>
              </div>

              {/* AI Types (if AI startup) */}
              {data.isAIStartup && (
                <div className="space-y-3 p-4 bg-muted/50 rounded-lg">
                  <Label>{t('onboarding.step2.aiTypes') || "Types d'IA"}</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {aiTypeOptions.map(type => (
                      <div key={type} className="flex items-center space-x-2">
                        <Checkbox
                          id={`ai-${type}`}
                          checked={data.aiTypes.includes(type)}
                          onCheckedChange={() => toggleArrayValue('aiTypes', type)}
                        />
                        <label htmlFor={`ai-${type}`} className="text-sm cursor-pointer">
                          {type}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {currentStep === 2 && data.organizationType === 'support_structure' && (
            <div className="space-y-5">
              <h3 className="font-semibold text-lg border-b pb-2">
                {t('onboarding.step2.structureTitle') || 'Informations structure'}
              </h3>

              {/* Structure Types */}
              <div className="space-y-3">
                <Label>Type de structure</Label>
                <div className="grid grid-cols-1 gap-2">
                  {structureTypeOptions.map(type => (
                    <div key={type} className="flex items-center space-x-2">
                      <Checkbox
                        id={`struct-${type}`}
                        checked={data.structureTypes.includes(type)}
                        onCheckedChange={() => toggleArrayValue('structureTypes', type)}
                      />
                      <label htmlFor={`struct-${type}`} className="text-sm cursor-pointer">
                        {type}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Startups Accompanied */}
              <div className="space-y-2">
                <Label>Nombre de startups accompagnées</Label>
                <Select value={data.startupsAccompanied} onValueChange={(v) => updateData('startupsAccompanied', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez une tranche" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover">
                    {startupsAccompaniedRanges.map(range => (
                      <SelectItem key={range} value={range}>{range}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Accompanied Stages */}
              <div className="space-y-3">
                <Label>Stades accompagnés</Label>
                <div className="grid grid-cols-2 gap-2">
                  {accompaniedStageOptions.map(stage => (
                    <div key={stage} className="flex items-center space-x-2">
                      <Checkbox
                        id={`stage-${stage}`}
                        checked={data.accompaniedStages.includes(stage)}
                        onCheckedChange={() => toggleArrayValue('accompaniedStages', stage)}
                      />
                      <label htmlFor={`stage-${stage}`} className="text-sm cursor-pointer">
                        {stage}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Specialization Sectors */}
              <div className="space-y-3">
                <Label>Secteurs de spécialisation</Label>
                <div className="grid grid-cols-2 gap-2">
                  {specializationSectorOptions.map(sector => (
                    <div key={sector} className="flex items-center space-x-2">
                      <Checkbox
                        id={`spec-${sector}`}
                        checked={data.specializationSectors.includes(sector)}
                        onCheckedChange={() => toggleArrayValue('specializationSectors', sector)}
                      />
                      <label htmlFor={`spec-${sector}`} className="text-sm cursor-pointer">
                        {sector}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Accompaniment Types */}
              <div className="space-y-3">
                <Label>Types d'accompagnement</Label>
                <div className="grid grid-cols-2 gap-2">
                  {accompanimentTypeOptions.map(type => (
                    <div key={type} className="flex items-center space-x-2">
                      <Checkbox
                        id={`acc-${type}`}
                        checked={data.accompanimentTypes.includes(type)}
                        onCheckedChange={() => toggleArrayValue('accompanimentTypes', type)}
                      />
                      <label htmlFor={`acc-${type}`} className="text-sm cursor-pointer">
                        {type}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex justify-between pt-4 border-t">
            <div className="flex gap-2">
              {currentStep > 1 ? (
                <Button variant="outline" onClick={handleBack}>
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Retour
                </Button>
              ) : (
                <Button variant="ghost" onClick={handleSkip} className="text-muted-foreground">
                  Passer cette étape
                </Button>
              )}
            </div>
            <Button onClick={handleNext} disabled={!canProceed() || isSubmitting}>
              {isSubmitting ? (
                'Enregistrement...'
              ) : currentStep < totalSteps ? (
                <>
                  Suivant
                  <ChevronRight className="h-4 w-4 ml-1" />
                </>
              ) : (
                <>
                  Terminer
                  <ChevronRight className="h-4 w-4 ml-1" />
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

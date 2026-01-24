'use client'

import { motion } from 'framer-motion'
import { Calendar, Link, ArrowRight, TrendingUp, AlertCircle, Mail, X } from 'lucide-react'
import { useTranslation } from '../context/LanguageContext'
import { Button } from './ui/button'

interface WatchArticle {
  title: string
  source: string
  date: string
  summary: string
  implications: string
  url?: string
}

interface WatchPreviewProps {
  subject: string
  date: string
  articles: WatchArticle[]
  onClose: () => void
  onSend?: () => void
}

export default function WatchPreview({ subject, date, articles, onClose, onSend }: WatchPreviewProps) {
  const { t } = useTranslation()
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-2xl w-full max-w-3xl max-h-[85vh] overflow-hidden shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Email Header */}
        <div className="bg-gradient-to-r from-cyan-600 to-blue-600 px-6 py-5 text-white">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              <span className="text-sm font-medium opacity-90">Apercu Email</span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="text-white hover:bg-white/20"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 opacity-75" />
            <span className="text-sm opacity-75">{date}</span>
          </div>
          <h1 className="text-xl font-bold mt-2">{subject}</h1>
        </div>
        
        {/* Email Content */}
        <div className="overflow-y-auto max-h-[calc(85vh-180px)]">
          <div className="p-6 space-y-6">
            {/* Introduction */}
            <p className="text-gray-600 text-sm leading-relaxed">
              Voici les actualites cles de la semaine concernant <strong>{subject}</strong>. 
              Cette veille a ete generee automatiquement par Prometheus.
            </p>
            
            {/* Articles */}
            {articles.map((article, index) => (
              <div 
                key={index}
                className="border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg transition-shadow"
              >
                {/* Article Header */}
                <div className="bg-gray-50 px-5 py-3 border-b border-gray-200">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-base">
                        {article.title}
                      </h3>
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Link className="w-3 h-3" />
                          {article.source}
                        </span>
                        <span>{article.date}</span>
                      </div>
                    </div>
                    {article.url && (
                      <a 
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-600 hover:text-cyan-700 text-sm flex items-center gap-1"
                      >
                        Lire
                        <ArrowRight className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
                
                {/* Article Summary */}
                <div className="px-5 py-4">
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {article.summary}
                  </p>
                </div>
                
                {/* Implications */}
                <div className="bg-amber-50 border-t border-amber-100 px-5 py-4">
                  <div className="flex items-start gap-3">
                    <div className="p-1.5 rounded-lg bg-amber-100">
                      <TrendingUp className="w-4 h-4 text-amber-600" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-amber-800 mb-1">
                        Implications marche
                      </h4>
                      <p className="text-sm text-amber-700 leading-relaxed">
                        {article.implications}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Footer */}
            <div className="border-t border-gray-200 pt-5 mt-6">
              <p className="text-xs text-gray-400 text-center">
                Ce rapport a ete genere automatiquement par Prometheus - Axial Intelligence.
                <br />
                Pour modifier vos preferences de veille, connectez-vous a votre espace.
              </p>
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div className="border-t border-gray-200 px-6 py-4 bg-gray-50 flex items-center justify-end gap-3">
          <Button
            variant="ghost"
            onClick={onClose}
          >
            Fermer
          </Button>
          {onSend && (
            <Button onClick={onSend}>
              <Mail className="w-4 h-4" />
              Envoyer maintenant
            </Button>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}

// Example mock data for testing
export const mockWatchArticles: WatchArticle[] = [
  {
    title: "La BCE maintient ses taux directeurs, signalant une pause dans le cycle de hausse",
    source: "Banque de France",
    date: "10 Jan 2026",
    summary: "La Banque centrale europeenne a decide de maintenir ses taux directeurs inchanges lors de sa derniere reunion, marquant une pause dans le cycle de resserrement monetaire engage depuis 2022. Cette decision reflete les signes de ralentissement de l'inflation dans la zone euro.",
    implications: "Cette stabilisation des taux pourrait beneficier aux entreprises en quete de financement, avec des conditions de credit potentiellement plus favorables au premier semestre 2026. Les secteurs immobilier et de la construction devraient particulierement en profiter.",
    url: "https://www.banque-france.fr"
  },
  {
    title: "Nouvelle reglementation europeenne sur l'IA : ce qui change pour les entreprises",
    source: "Commission europeenne",
    date: "8 Jan 2026",
    summary: "L'AI Act entre en vigueur avec de nouvelles exigences de conformite pour les systemes d'intelligence artificielle a haut risque. Les entreprises disposent de 24 mois pour se mettre en conformite avec les nouvelles regles.",
    implications: "Les entreprises utilisant des systemes d'IA devront investir dans l'audit et la documentation de leurs algorithmes. Les couts de mise en conformite sont estimes entre 5% et 15% des budgets IT selon la taille de l'organisation.",
    url: "https://ec.europa.eu"
  }
]

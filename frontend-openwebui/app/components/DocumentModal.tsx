'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Source {
  id: number;
  doc_id: number | string;
  title?: string;
  author?: string;
  year?: number;
  page?: number;
  doc_type?: string;
  text: string;
  score?: number;
  apa_citation?: string;
  document_url?: string;
}

interface DocumentModalProps {
  isOpen: boolean;
  source: Source | null;
  onClose: () => void;
}

/**
 * Modal de prévisualisation de document style Perplexity
 * Affiche les détails complets du document avec option d'ouverture
 */
export const DocumentModal: React.FC<DocumentModalProps> = ({ 
  isOpen, 
  source, 
  onClose 
}) => {
  // Fermer avec Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Bloquer le scroll du body
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!source) return null;

  const handleOpenDocument = () => {
    if (source.document_url) {
      window.open(source.document_url, '_blank');
    } else {
      // Fallback: télécharger ou afficher le doc_id
      alert(`Document ${source.doc_id} - URL non disponible pour l'instant`);
    }
  };

  const getScoreBadge = (score?: number) => {
    if (!score) return null;
    
    const percentage = Math.round(score * 100);
    let colorClass = 'bg-blue-500';
    if (percentage >= 80) colorClass = 'bg-green-500';
    else if (percentage >= 50) colorClass = 'bg-blue-500';
    else colorClass = 'bg-yellow-500';

    return (
      <div className={`inline-flex items-center gap-1 px-3 py-1 ${colorClass} text-white rounded-full text-sm font-semibold`}>
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        {percentage}% pertinent
      </div>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', duration: 0.3 }}
              className="w-full max-w-3xl max-h-[85vh] bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 overflow-hidden pointer-events-auto"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 px-6 py-4 border-b border-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="inline-flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-full text-lg font-bold">
                        {source.id}
                      </span>
                      <div>
                        <h2 className="text-xl font-bold text-white">
                          {source.title || `Document #${source.doc_id}`}
                        </h2>
                        {source.author && (
                          <p className="text-sm text-gray-300">
                            {source.author}
                            {source.year && ` · ${source.year}`}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      {source.doc_type && (
                        <span className="px-3 py-1 bg-blue-900/50 text-blue-200 rounded-full text-xs font-medium">
                          {source.doc_type}
                        </span>
                      )}
                      {source.page && (
                        <span className="px-3 py-1 bg-gray-800 text-gray-300 rounded-full text-xs font-medium">
                          Page {source.page}
                        </span>
                      )}
                      {getScoreBadge(source.score)}
                    </div>
                  </div>
                  
                  <button
                    onClick={onClose}
                    className="ml-4 p-2 hover:bg-white/10 rounded-lg transition-colors group"
                    aria-label="Fermer"
                  >
                    <svg 
                      className="w-6 h-6 text-gray-400 group-hover:text-white transition-colors" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="overflow-y-auto max-h-[calc(85vh-200px)] p-6 space-y-6">
                {/* Extrait du document */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
                    Extrait du Document
                  </h3>
                  <div className="p-6 bg-gray-800/50 rounded-xl border-l-4 border-blue-500">
                    <p className="text-base text-gray-200 leading-relaxed italic">
                      "{source.text}"
                    </p>
                  </div>
                </div>

                {/* Citation APA */}
                {source.apa_citation && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
                      Citation APA
                    </h3>
                    <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700">
                      <p className="text-sm text-gray-300 font-mono leading-relaxed">
                        {source.apa_citation}
                      </p>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(source.apa_citation || '');
                          // Feedback visuel (optionnel)
                          const btn = event?.currentTarget;
                          if (btn) {
                            btn.textContent = '✓ Copié !';
                            setTimeout(() => {
                              btn.textContent = '📋 Copier';
                            }, 2000);
                          }
                        }}
                        className="mt-3 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                      >
                        📋 Copier la citation
                      </button>
                    </div>
                  </div>
                )}

                {/* Métadonnées additionnelles */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
                    Informations
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-gray-800/30 rounded-lg">
                      <p className="text-xs text-gray-500 mb-1">ID Document</p>
                      <p className="text-sm font-medium text-white">#{source.doc_id}</p>
                    </div>
                    {source.score !== undefined && (
                      <div className="p-3 bg-gray-800/30 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Score de Pertinence</p>
                        <p className="text-sm font-medium text-white">
                          {(source.score * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Footer avec actions */}
              <div className="bg-gray-800/50 px-6 py-4 border-t border-gray-700 flex items-center justify-between">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
                >
                  Fermer
                </button>
                <div className="flex gap-3">
                  <button
                    onClick={handleOpenDocument}
                    className="
                      px-6 py-2.5 
                      bg-gradient-to-r from-blue-600 to-blue-500 
                      hover:from-blue-500 hover:to-blue-400
                      text-white font-medium rounded-lg
                      transition-all duration-200
                      shadow-lg shadow-blue-500/30
                      hover:shadow-xl hover:shadow-blue-500/40
                      flex items-center gap-2
                    "
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Ouvrir le Document
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

export default DocumentModal;

'use client';

import React, { useState } from 'react';
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

interface SourceCitationProps {
  index: number;
  source: Source;
  onViewDocument?: (source: Source) => void;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ 
  index, 
  source, 
  onViewDocument 
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState<'top' | 'bottom'>('top');

  const handleMouseEnter = (e: React.MouseEvent) => {
    setIsHovered(true);
    
    // Détecter si on est près du bas de la page pour afficher le tooltip en haut
    const rect = e.currentTarget.getBoundingClientRect();
    const spaceBelow = window.innerHeight - rect.bottom;
    setTooltipPosition(spaceBelow < 300 ? 'top' : 'bottom');
  };

  const handleClick = () => {
    if (onViewDocument) {
      onViewDocument(source);
    }
  };

  // Déterminer la couleur en fonction du score de pertinence
  const getScoreColor = (score?: number) => {
    if (!score) return 'bg-blue-500';
    if (score > 0.8) return 'bg-green-500';
    if (score > 0.5) return 'bg-blue-500';
    return 'bg-yellow-500';
  };

  // Formater le texte de prévisualisation
  const previewText = source.text.length > 200 
    ? source.text.substring(0, 200) + '...' 
    : source.text;

  return (
    <span className="relative inline-block">
      <motion.button
        type="button"
        onClick={handleClick}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={() => setIsHovered(false)}
        className={`
          inline-flex items-center justify-center
          min-w-[24px] h-[20px] px-1.5 mx-0.5
          text-[11px] font-semibold
          ${getScoreColor(source.score)} text-white
          rounded-md cursor-pointer
          transition-all duration-200
          hover:scale-110 hover:shadow-lg
          focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-400
        `}
        whileHover={{ y: -2 }}
        whileTap={{ scale: 0.95 }}
      >
        {index}
      </motion.button>

      {/* Tooltip de prévisualisation */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, y: tooltipPosition === 'top' ? 10 : -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: tooltipPosition === 'top' ? 10 : -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={`
              absolute z-50 w-[320px] 
              ${tooltipPosition === 'top' ? 'bottom-full mb-2' : 'top-full mt-2'}
              left-1/2 transform -translate-x-1/2
              pointer-events-none
            `}
          >
            <div className="bg-gray-900 text-white rounded-lg shadow-2xl p-4 border border-gray-700">
              {/* Header avec métadonnées */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  {source.title && (
                    <h4 className="text-sm font-semibold text-white mb-1">
                      {source.title}
                    </h4>
                  )}
                  {source.author && (
                    <p className="text-xs text-gray-400">
                      {source.author}
                      {source.year && ` (${source.year})`}
                    </p>
                  )}
                </div>
                {source.score && (
                  <div className="ml-2 text-xs font-medium text-green-400">
                    {Math.round(source.score * 100)}%
                  </div>
                )}
              </div>

              {/* Type de document */}
              {source.doc_type && (
                <div className="mb-2">
                  <span className="inline-block px-2 py-0.5 text-xs font-medium bg-blue-900 text-blue-200 rounded">
                    {source.doc_type}
                  </span>
                  {source.page && (
                    <span className="ml-2 text-xs text-gray-400">
                      p. {source.page}
                    </span>
                  )}
                </div>
              )}

              {/* Extrait du document */}
              <div className="mb-3 p-3 bg-gray-800 rounded text-xs leading-relaxed text-gray-300 italic border-l-2 border-blue-500">
                "{previewText}"
              </div>

              {/* Citation APA */}
              {source.apa_citation && (
                <div className="mb-3 pt-2 border-t border-gray-700">
                  <p className="text-[10px] text-gray-400 leading-relaxed">
                    {source.apa_citation}
                  </p>
                </div>
              )}

              {/* Action */}
              <div className="flex items-center justify-between pt-2 border-t border-gray-700">
                <span className="text-xs text-gray-400">
                  Cliquez pour voir le document
                </span>
                <svg 
                  className="w-4 h-4 text-gray-400" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M9 5l7 7-7 7" 
                  />
                </svg>
              </div>

              {/* Triangle pointer */}
              <div 
                className={`
                  absolute left-1/2 transform -translate-x-1/2
                  ${tooltipPosition === 'top' ? 'top-full' : 'bottom-full'}
                  w-3 h-3 bg-gray-900 border-gray-700 rotate-45
                  ${tooltipPosition === 'top' ? 'border-b border-r -mt-1.5' : 'border-t border-l -mb-1.5'}
                `}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  );
};

export default SourceCitation;

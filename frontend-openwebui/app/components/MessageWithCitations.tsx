'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { SourceCitation } from './SourceCitation';

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

interface MessageWithCitationsProps {
  content: string;
  sources: Source[];
  onViewDocument?: (source: Source) => void;
}

/**
 * Composant qui parse le markdown et remplace les citations [¹][²][³] 
 * par des badges cliquables style Perplexity
 */
export const MessageWithCitations: React.FC<MessageWithCitationsProps> = ({ 
  content, 
  sources,
  onViewDocument 
}) => {
  // Parser et remplacer les citations inline
  const parsedContent = useMemo(() => {
    if (!content || sources.length === 0) return content;

    // Regex pour détecter [¹], [²], [³], etc. (caractères exposants Unicode)
    // Aussi détecter [1], [2], [3] au cas où
    const citationPattern = /\[([¹²³⁴⁵⁶⁷⁸⁹⁰]+|\d+)\]/g;

    // Mapping caractères exposants vers nombres
    const superscriptToNumber: { [key: string]: number } = {
      '¹': 1, '²': 2, '³': 3, '⁴': 4, '⁵': 5,
      '⁶': 6, '⁷': 7, '⁸': 8, '⁹': 9, '⁰': 0
    };

    const convertSuperscript = (sup: string): number => {
      if (/^\d+$/.test(sup)) return parseInt(sup, 10);
      
      let result = 0;
      for (const char of sup) {
        result = result * 10 + (superscriptToNumber[char] || 0);
      }
      return result;
    };

    // Séparer le contenu en parties avant et après la bibliographie
    const bibliographyIndex = content.indexOf('## 📚 Sources');
    const mainContent = bibliographyIndex >= 0 
      ? content.substring(0, bibliographyIndex) 
      : content;
    const bibliography = bibliographyIndex >= 0 
      ? content.substring(bibliographyIndex) 
      : '';

    // Remplacer les citations dans le contenu principal
    const parts: (string | { type: 'citation', index: number })[] = [];
    let lastIndex = 0;
    let match;

    while ((match = citationPattern.exec(mainContent)) !== null) {
      // Ajouter le texte avant la citation
      if (match.index > lastIndex) {
        parts.push(mainContent.substring(lastIndex, match.index));
      }

      // Ajouter la citation
      const citationNumber = convertSuperscript(match[1]);
      parts.push({ type: 'citation', index: citationNumber });

      lastIndex = match.index + match[0].length;
    }

    // Ajouter le reste du texte
    if (lastIndex < mainContent.length) {
      parts.push(mainContent.substring(lastIndex));
    }

    return { parts, bibliography };
  }, [content, sources]);

  // Composant de rendu avec citations
  const renderContentWithCitations = () => {
    if (!parsedContent || typeof parsedContent === 'string') {
      return (
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      );
    }

    const { parts, bibliography } = parsedContent;

    return (
      <div className="space-y-4">
        {/* Contenu principal avec citations inline */}
        <div className="prose prose-invert max-w-none">
          {parts.map((part, idx) => {
            if (typeof part === 'string') {
              return (
                <ReactMarkdown key={idx} remarkPlugins={[remarkGfm]}>
                  {part}
                </ReactMarkdown>
              );
            } else if (part.type === 'citation') {
              // Trouver la source correspondante
              const source = sources.find(s => s.id === part.index);
              if (source) {
                return (
                  <SourceCitation
                    key={idx}
                    index={part.index}
                    source={source}
                    onViewDocument={onViewDocument}
                  />
                );
              }
              // Si source non trouvée, afficher le numéro tel quel
              return <span key={idx}>[{part.index}]</span>;
            }
            return null;
          })}
        </div>

        {/* Bibliographie (optionnelle, déjà dans le markdown) */}
        {bibliography && (
          <div className="mt-8 pt-6 border-t border-gray-700/50">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              className="prose prose-invert prose-sm max-w-none"
            >
              {bibliography}
            </ReactMarkdown>
          </div>
        )}

        {/* Affichage alternatif: Sources en cards si pas de bibliographie markdown */}
        {!bibliography && sources.length > 0 && (
          <div className="mt-8 pt-6 border-t border-gray-700/50">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              📚 Sources Consultées
            </h3>
            <div className="grid grid-cols-1 gap-3">
              {sources.map((source) => (
                <div
                  key={source.id}
                  onClick={() => onViewDocument?.(source)}
                  className="
                    p-4 bg-gray-800/50 rounded-lg border border-gray-700/50
                    hover:bg-gray-800 hover:border-gray-600 transition-all cursor-pointer
                    group
                  "
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                        {source.id}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      {source.title && (
                        <h4 className="text-sm font-medium text-white mb-1 group-hover:text-blue-400 transition-colors">
                          {source.title}
                        </h4>
                      )}
                      {source.apa_citation ? (
                        <p className="text-xs text-gray-400 mb-2">
                          {source.apa_citation}
                        </p>
                      ) : (
                        <p className="text-xs text-gray-400 mb-2">
                          {source.author && `${source.author} `}
                          {source.year && `(${source.year}) `}
                          {source.page && `p. ${source.page}`}
                        </p>
                      )}
                      <p className="text-sm text-gray-300 line-clamp-2 italic">
                        "{source.text.substring(0, 150)}..."
                      </p>
                    </div>
                    {source.score !== undefined && (
                      <div className="flex-shrink-0 text-xs font-medium text-green-400">
                        {Math.round(source.score * 100)}%
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return <div className="message-with-citations">{renderContentWithCitations()}</div>;
};

export default MessageWithCitations;

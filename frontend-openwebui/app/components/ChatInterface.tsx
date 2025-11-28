'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Sparkles, Copy } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { toast } from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

export default function ChatInterface() {
  const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8006'
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: '👋 Bonjour ! Je suis votre assistant. Comment puis-je vous aider ?',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessageWithStreaming = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Créer un message assistant vide pour le streaming
    const assistantId = (Date.now() + 1).toString()
    const assistantMessage: Message = {
      id: assistantId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    }
    setMessages(prev => [...prev, assistantMessage])

    try {
      // Utiliser l'endpoint streaming
      const response = await fetch(`${backendBaseUrl}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: messages.slice(-6).map(m => ({ 
            role: m.type === 'user' ? 'user' : 'assistant', 
            content: m.content 
          }))
        })
      })

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let streamedContent = ''

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          
          // Nettoyer le chunk (enlever [DONE] si présent)
          const cleanChunk = chunk.replace('[DONE]', '').trim()
          if (cleanChunk) {
            streamedContent += cleanChunk
            
            // Mettre à jour le message en temps réel
            setMessages(prev => prev.map(m => 
              m.id === assistantId 
                ? { ...m, content: streamedContent }
                : m
            ))
          }
        }
      }

      // Marquer le streaming comme terminé
      setMessages(prev => prev.map(m => 
        m.id === assistantId 
          ? { ...m, isStreaming: false }
          : m
      ))

    } catch (error: any) {
      console.error('Erreur chat streaming:', error)
      
      // Fallback vers l'endpoint non-streaming
      try {
        const fallbackResponse = await fetch(`${backendBaseUrl}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userMessage.content,
            conversation_history: []
          })
        })

        if (fallbackResponse.ok) {
          const data = await fallbackResponse.json()
          setMessages(prev => prev.map(m => 
            m.id === assistantId 
              ? { ...m, content: data.response || '❌ Pas de réponse', isStreaming: false }
              : m
          ))
        } else {
          throw new Error('Fallback failed')
        }
      } catch (fallbackError) {
        setMessages(prev => prev.map(m => 
          m.id === assistantId 
            ? { ...m, content: '❌ Erreur de connexion. Veuillez réessayer.', isStreaming: false }
            : m
        ))
        toast.error('Erreur de communication')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessageWithStreaming()
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success('Copié !')
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages - zone scrollable */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] ${
                message.type === 'user' 
                  ? 'bg-axial-accent/30 rounded-2xl rounded-tr-md' 
                  : 'bg-white/10 rounded-2xl rounded-tl-md'
              } px-4 py-2.5`}>
                <div className="flex items-start gap-2">
                  {message.type === 'assistant' && (
                    <div className="w-6 h-6 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Bot className="w-3 h-3 text-white" />
                    </div>
                  )}
                  
                  <div className="flex-1 min-w-0">
                    <div className="prose prose-invert prose-sm max-w-none text-sm">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                      
                      {/* Curseur de streaming */}
                      {message.isStreaming && (
                        <span className="inline-block w-2 h-4 bg-axial-accent ml-1 animate-pulse" />
                      )}
                    </div>
                    
                    {!message.isStreaming && (
                      <div className="flex items-center justify-between mt-1.5">
                        <span className="text-[10px] text-gray-500">
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {message.type === 'assistant' && (
                          <button
                            onClick={() => copyMessage(message.content)}
                            className="p-1 hover:bg-white/10 rounded transition-colors"
                          >
                            <Copy className="w-3 h-3 text-gray-400" />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {message.type === 'user' && (
                    <div className="w-6 h-6 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <User className="w-3 h-3 text-white" />
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading dots */}
        {isLoading && !messages.some(m => m.isStreaming) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-white/10 rounded-2xl rounded-tl-md px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center">
                  <Bot className="w-3 h-3 text-white" />
                </div>
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input - compact */}
      <div className="p-3 border-t border-white/10">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Posez votre question..."
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm resize-none focus:outline-none focus:ring-2 focus:ring-axial-accent/50 placeholder-gray-500"
            rows={1}
            disabled={isLoading}
          />
          
          <motion.button
            onClick={sendMessageWithStreaming}
            disabled={!input.trim() || isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2.5 rounded-xl bg-axial-accent text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
        
        <div className="flex items-center justify-center mt-2 text-[10px] text-gray-500">
          <Sparkles className="w-3 h-3 mr-1" />
          <span>Entrée pour envoyer</span>
        </div>
      </div>
    </div>
  )
}

'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Sparkles, Copy, Download } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { toast } from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  businessContext?: string
}

interface ChatInterfaceProps {
  selectedBusiness: string
}

export default function ChatInterface({ selectedBusiness }: ChatInterfaceProps) {
  const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8006'
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: '👋 Bonjour ! Je suis votre expert en intelligence stratégique. Comment puis-je vous aider aujourd\'hui ?',
      timestamp: new Date(),
      businessContext: 'Généraliste'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Abort streaming on unmount
  useEffect(() => {
    return () => abortRef.current?.abort()
  }, [])

  const stopStreaming = () => {
    abortRef.current?.abort()
    setIsLoading(false)
  }

  const sendMessage = async () => {
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

    try {
      // Streaming via /chat/stream (texte chunké)
      abortRef.current?.abort()
      abortRef.current = new AbortController()
      const controller = abortRef.current

      const response = await fetch(`${backendBaseUrl}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          business_type: selectedBusiness,
          conversation_history: messages.slice(-6).map(m => ({ role: m.type, content: m.content }))
        }),
        signal: controller.signal
      })

      if (!response.ok || !response.body) {
        const errorText = await response.text()
        throw new Error(`Erreur ${response.status}: ${errorText}`)
      }

      // Placeholder assistant message to append chunks
      const assistantId = (Date.now() + 1).toString()
      setMessages(prev => [...prev, {
        id: assistantId,
        type: 'assistant',
        content: '',
        timestamp: new Date(),
        businessContext: `Expert ${selectedBusiness.replace('_', ' ')}`
      }])

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let done = false
      let buffer = ''
      while (!done) {
        const { value, done: doneRead } = await reader.read()
        done = doneRead
        if (value) {
          buffer += decoder.decode(value, { stream: true })
          // Split on [DONE] marker if present
          const parts = buffer.split('[DONE]')
          const text = parts[0]
          setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, content: text } : m))
          if (parts.length > 1) break
        }
      }

    } catch (error: any) {
      if (error?.name === 'AbortError') return
      console.error('Erreur chat:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '❌ Une erreur s\'est produite. Veuillez réessayer.',
        timestamp: new Date(),
        businessContext: 'Système'
      }
      setMessages(prev => [...prev, errorMessage])
      toast.error('Erreur de communication')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success('Message copié !')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card h-[70vh] flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-white">Expert IA</h3>
            <p className="text-sm text-gray-400">Intelligence Stratégique</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-axial-accent">●</span>
          <span className="text-xs text-gray-400">En ligne</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${message.type === 'user' ? 'message-user' : 'message-assistant'}`}>
                <div className="flex items-start gap-3">
                  {message.type === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  
                  <div className="flex-1">
                    {message.type === 'assistant' && message.businessContext && (
                      <div className="text-xs text-axial-accent mb-1 font-medium">
                        {message.businessContext}
                      </div>
                    )}
                    
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                    
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-gray-400">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      <button
                        onClick={() => copyMessage(message.content)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white/10 rounded"
                      >
                        <Copy className="w-3 h-3 text-gray-400" />
                      </button>
                    </div>
                  </div>
                  
                  {message.type === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-start"
          >
            <div className="message-assistant max-w-[80%]">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
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

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Posez votre question d'intelligence stratégique..."
              className="input-liquid w-full resize-none min-h-[50px] max-h-[120px]"
              rows={1}
              disabled={isLoading}
            />
            <div className="absolute bottom-2 right-2 text-xs text-gray-500">
              {input.length}/1000
            </div>
          </div>
          
          {isLoading ? (
            <motion.button
              onClick={stopStreaming}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="glass-button px-4 py-3 text-red-200 border-red-500 hover:bg-red-500/30 flex items-center gap-2"
            >
              <span>Stop</span>
            </motion.button>
          ) : (
            <motion.button
              onClick={sendMessage}
              disabled={!input.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-liquid px-4 py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span className="hidden sm:inline">Envoyer</span>
            </motion.button>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <Sparkles className="w-3 h-3" />
            <span>IA spécialisée {selectedBusiness.replace('_', ' ')}</span>
          </div>
          <span>Maj+Entrée pour nouvelle ligne</span>
        </div>
      </div>
    </motion.div>
  )
}

'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, X, Send, Bot, User, Sparkles, Copy, Minimize2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { toast } from 'react-hot-toast'
import MessageWithCitations from './MessageWithCitations'
import DocumentModal from './DocumentModal'

interface Source {
  id: number
  doc_id: number | string
  title?: string
  author?: string
  year?: number
  page?: number
  doc_type?: string
  text: string
  score?: number
  apa_citation?: string
  document_url?: string
}

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  businessContext?: string
  sources?: Source[]
}

export default function ChatWidget() {
  const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8006'
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: '👋 Bonjour ! Je suis votre expert en intelligence stratégique. Comment puis-je vous aider ?',
      timestamp: new Date(),
      businessContext: 'Expert IA',
      sources: []
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [hasUnread, setHasUnread] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Mark as read when opening
  useEffect(() => {
    if (isOpen) {
      setHasUnread(false)
    }
  }, [isOpen])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
      sources: []
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${backendBaseUrl}/chat`, {
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
        const errorText = await response.text()
        throw new Error(`Erreur ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response || '❌ Pas de réponse',
        timestamp: new Date(),
        businessContext: 'Expert IA',
        sources: data.sources || []
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Set unread badge if chat is closed
      if (!isOpen) {
        setHasUnread(true)
      }

    } catch (error: any) {
      console.error('Erreur chat:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '❌ Une erreur s\'est produite. Veuillez réessayer.',
        timestamp: new Date(),
        businessContext: 'Système',
        sources: []
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
    <>
      {/* Floating Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="chat-widget-button"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.5 }}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <X className="w-6 h-6 text-white" />
            </motion.div>
          ) : (
            <motion.div
              key="open"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <MessageCircle className="w-6 h-6 text-white" />
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Unread badge */}
        {hasUnread && !isOpen && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center"
          >
            <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
          </motion.span>
        )}
        
        {/* Pulse ring animation */}
        {!isOpen && (
          <span className="chat-widget-pulse" />
        )}
      </motion.button>

      {/* Chat Popup */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="chat-widget-popup"
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {/* Header */}
            <div className="chat-widget-header">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-white text-sm">Expert IA</h3>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-xs text-gray-400">En ligne</span>
                  </div>
                </div>
              </div>
              <motion.button
                onClick={() => setIsOpen(false)}
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <Minimize2 className="w-4 h-4 text-gray-400" />
              </motion.button>
            </div>

            {/* Messages */}
            <div className="chat-widget-messages">
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-3`}
                  >
                    <div className={`max-w-[85%] ${
                      message.type === 'user' 
                        ? 'chat-widget-message-user' 
                        : 'chat-widget-message-assistant'
                    }`}>
                      <div className="flex items-start gap-2">
                        {message.type === 'assistant' && (
                          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-axial-blue to-axial-accent flex items-center justify-center flex-shrink-0">
                            <Bot className="w-3 h-3 text-white" />
                          </div>
                        )}
                        
                        <div className="flex-1 min-w-0">
                          <div className="prose prose-invert prose-sm max-w-none text-sm">
                            {message.type === 'assistant' && message.sources && message.sources.length > 0 ? (
                              <MessageWithCitations
                                content={message.content}
                                sources={message.sources}
                                onViewDocument={(source) => {
                                  setSelectedSource(source)
                                  setIsModalOpen(true)
                                }}
                              />
                            ) : (
                              <ReactMarkdown>{message.content}</ReactMarkdown>
                            )}
                          </div>
                          
                          <span className="text-[10px] text-gray-500 mt-1 block">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        
                        {message.type === 'user' && (
                          <div className="w-6 h-6 rounded-full bg-gradient-to-r from-gray-600 to-gray-700 flex items-center justify-center flex-shrink-0">
                            <User className="w-3 h-3 text-white" />
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
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start mb-3"
                >
                  <div className="chat-widget-message-assistant">
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

            {/* Input */}
            <div className="chat-widget-input">
              <div className="flex gap-2">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Posez votre question..."
                  className="chat-widget-textarea"
                  rows={1}
                  disabled={isLoading}
                />
                
                <motion.button
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="chat-widget-send-btn"
                >
                  <Send className="w-4 h-4" />
                </motion.button>
              </div>
              
              <div className="flex items-center gap-1 mt-2 text-[10px] text-gray-500">
                <Sparkles className="w-3 h-3" />
                <span>Intelligence Stratégique</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document Modal */}
      <DocumentModal
        isOpen={isModalOpen}
        source={selectedSource}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedSource(null)
        }}
      />
    </>
  )
}


'use client'

import { useState, useRef, useEffect } from 'react'
import { 
  MessageSquare, 
  Send, 
  Bot, 
  User, 
  Loader2, 
  AlertCircle,
  Clock,
  Trash2,
  RefreshCw
} from 'lucide-react'
import clsx from 'clsx'
import { API_CONFIG } from '../lib/config'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources_referenced?: string[]
}

interface ChatInterfaceProps {
  analysisId: string
  companyName?: string
  className?: string
}

export function ChatInterface({ analysisId, companyName, className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Add welcome message
    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      content: `${API_CONFIG.chat.welcomeMessage} I have access to the complete analysis for ${companyName || 'your company'} and can answer any questions about the IPO readiness assessment, financial highlights, risks, recommendations, and more. What would you like to know?`,
      timestamp: new Date().toISOString(),
      sources_referenced: []
    }
    setMessages([welcomeMessage])
  }, [companyName])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          analysis_id: analysisId,
          conversation_id: conversationId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      const assistantMessage: Message = {
        id: data.message_id,
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp,
        sources_referenced: data.sources_referenced || []
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (err) {
      console.error('Chat error:', err)
      setError('Failed to send message. Please try again.')
      
      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
        sources_referenced: []
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const clearChat = () => {
    const welcomeMessage: Message = {
      id: 'welcome-new',
      role: 'assistant',
      content: `Chat cleared! I'm ready to help you with questions about ${companyName || 'the company'}'s IPO readiness analysis.`,
      timestamp: new Date().toISOString(),
      sources_referenced: []
    }
    setMessages([welcomeMessage])
    setConversationId(null)
    setError(null)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className={clsx(
      "flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <MessageSquare className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">IPO Analysis Chat</h3>
            <p className="text-sm text-slate-600">
              Ask questions about {companyName || 'the analysis'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={clearChat}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-white rounded-lg transition-colors"
            title="Clear chat"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[400px] max-h-[600px]">
        {messages.map((message) => (
          <div
            key={message.id}
            className={clsx(
              "flex items-start space-x-3",
              message.role === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
            )}
          >
            {/* Avatar */}
            <div className={clsx(
              "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
              message.role === 'user' 
                ? 'bg-blue-100 text-blue-600' 
                : 'bg-green-100 text-green-600'
            )}>
              {message.role === 'user' ? (
                <User className="h-4 w-4" />
              ) : (
                <Bot className="h-4 w-4" />
              )}
            </div>

            {/* Message Content */}
            <div className={clsx(
              "flex-1 max-w-[80%]",
              message.role === 'user' ? 'text-right' : 'text-left'
            )}>
              <div className={clsx(
                "inline-block px-4 py-3 rounded-2xl",
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-md'
                  : 'bg-slate-100 text-slate-900 rounded-bl-md'
              )}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
              
              {/* Message metadata */}
              <div className={clsx(
                "flex items-center mt-1 space-x-2 text-xs text-slate-500",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}>
                <Clock className="h-3 w-3" />
                <span>{formatTimestamp(message.timestamp)}</span>
                
                {/* Sources referenced for assistant messages */}
                {message.role === 'assistant' && message.sources_referenced && message.sources_referenced.length > 0 && (
                  <div className="flex items-center space-x-1">
                    <span>•</span>
                    <span className="text-blue-600">
                      Sources: {message.sources_referenced.join(', ')}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex-1">
              <div className="inline-block px-4 py-3 rounded-2xl rounded-bl-md bg-slate-100">
                <div className="flex items-center space-x-2 text-slate-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error display */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-700">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span className="text-sm">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-600"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-slate-200 p-4">
        <div className="flex items-center space-x-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about the IPO analysis..."
              maxLength={API_CONFIG.chat.maxMessageLength}
              className="w-full px-4 py-3 pr-12 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
              disabled={isLoading}
            />
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className={clsx(
              "p-3 rounded-xl transition-all duration-200",
              inputMessage.trim() && !isLoading
                ? "bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md"
                : "bg-slate-100 text-slate-400 cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </div>
        
        <div className="mt-2 text-xs text-slate-500 text-center">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}
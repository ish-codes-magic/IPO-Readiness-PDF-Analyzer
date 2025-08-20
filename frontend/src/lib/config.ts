// Configuration for the frontend application

export const API_CONFIG = {
  // Backend API base URL
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // API endpoints
  endpoints: {
    analyzePdf: '/analyze-pdf',
    chat: '/chat',
    conversations: '/chat/conversations',
    conversationHistory: '/chat/history',
    criteria: '/criteria',
    health: '/health'
  },
  
  // Request configuration
  timeout: 300000, // 5 minutes for PDF analysis
  maxFileSize: 20 * 1024 * 1024, // 20MB
  
  // Supported file types
  supportedFileTypes: ['.pdf'],
  
  // Chat configuration
  chat: {
    maxMessageLength: 2000,
    welcomeMessage: "Hello! I'm your IPO readiness advisor. I can answer questions about your company's analysis.",
    errorMessage: "I apologize, but I encountered an error. Please try again.",
    typingIndicator: "Thinking...",
    maxHistoryLength: 50 // Maximum number of messages to keep in memory
  }
}

export const endpoints = {
  analyzePdf: `${API_CONFIG.baseURL}/analyze-pdf`,
  health: `${API_CONFIG.baseURL}/health`,
  criteria: `${API_CONFIG.baseURL}/criteria`,
}

export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
}
'use client'

import { useState } from 'react'
import { Upload, FileText, BarChart3, MessageSquare, CheckCircle2, AlertCircle } from 'lucide-react'
import { PDFUploader } from '@/components/PDFUploader'
import { AnalysisResults } from '@/components/AnalysisResults'
import { LoadingSpinner } from '@/components/LoadingSpinner'

type AnalysisData = {
  overall_ipo_score: number
  readiness_level: string
  filename: string
  timestamp: string
  processing_time_seconds?: number
  confidence_score?: number
  company_metadata?: {
    company_name?: string
    industry?: string
  }
  criterion_scores?: Array<{
    name: string
    score: number
    rationale: string
    strengths?: string[]
    weaknesses?: string[]
  }>
  executive_summary?: {
    overall_assessment?: string
    key_highlights?: string[]
    recommendation?: string
  }
  risk_assessment?: {
    key_risks?: string[]
    information_gaps?: string[]
  }
  competitive_positioning?: string
  follow_up_questions?: {
    questions?: string[]
    priority_areas?: string[]
  }
}

export default function Home() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalysisComplete = (data: unknown) => {
    setAnalysisData(data as AnalysisData)
    setIsAnalyzing(false)
    setError(null)
  }

  const handleAnalysisStart = () => {
    setIsAnalyzing(true)
    setError(null)
    setAnalysisData(null)
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
    setIsAnalyzing(false)
  }

  const resetAnalysis = () => {
    setAnalysisData(null)
    setError(null)
    setIsAnalyzing(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">IPO Readiness Analyzer</h1>
                <p className="text-sm text-slate-600">AI-powered pitch deck evaluation</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="hidden sm:flex items-center space-x-6">
                <div className="flex items-center space-x-2 text-sm text-slate-600">
                  <FileText className="h-4 w-4" />
                  <span>PDF Analysis</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-slate-600">
                  <BarChart3 className="h-4 w-4" />
                  <span>IPO Scoring</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-slate-600">
                  <MessageSquare className="h-4 w-4" />
                  <span>Chat</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        {!analysisData && !isAnalyzing && !error && (
          <div className="text-center mb-12">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-2xl w-fit mx-auto mb-6">
              <Upload className="h-12 w-12 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Analyze Your Pitch Deck for IPO Readiness
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
              Upload your SME pitch deck PDF and get comprehensive AI-powered analysis with 
              detailed scoring across 8 key criteria for IPO readiness assessment.
            </p>
            
            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
              <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <div className="bg-blue-100 p-3 rounded-lg w-fit mx-auto mb-4">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">Smart PDF Extraction</h3>
                <p className="text-sm text-slate-600">Advanced content extraction from pitch decks with table and section recognition</p>
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <div className="bg-indigo-100 p-3 rounded-lg w-fit mx-auto mb-4">
                  <BarChart3 className="h-6 w-6 text-indigo-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">Comprehensive Scoring</h3>
                <p className="text-sm text-slate-600">8-criteria evaluation including financials, traction, and regulatory compliance</p>
              </div>
              
              <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
                <div className="bg-emerald-100 p-3 rounded-lg w-fit mx-auto mb-4">
                  <CheckCircle2 className="h-6 w-6 text-emerald-600" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">Actionable Insights</h3>
                <p className="text-sm text-slate-600">Detailed recommendations and follow-up questions for investment decisions</p>
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <div className="flex items-center space-x-3 mb-3">
                <AlertCircle className="h-6 w-6 text-red-600" />
                <h3 className="font-semibold text-red-900">Analysis Failed</h3>
              </div>
              <p className="text-red-700 mb-4">{error}</p>
              <button
                onClick={resetAnalysis}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isAnalyzing && (
          <div className="max-w-2xl mx-auto">
            <LoadingSpinner />
          </div>
        )}

        {/* Upload Component */}
        {!analysisData && !isAnalyzing && (
          <div className="max-w-2xl mx-auto">
            <PDFUploader
              onAnalysisStart={handleAnalysisStart}
              onAnalysisComplete={handleAnalysisComplete}
              onError={handleError}
            />
          </div>
        )}

        {/* Analysis Results */}
        {analysisData && !isAnalyzing && (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Analysis Results</h2>
                <p className="text-slate-600">Comprehensive IPO readiness assessment</p>
              </div>
              <button
                onClick={resetAnalysis}
                className="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 transition-colors"
              >
                Analyze Another Deck
              </button>
            </div>
            <AnalysisResults data={analysisData} />
          </div>
        )}


      </main>

      {/* Footer */}
      <footer className="mt-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-slate-600">
            <p>IPO Readiness PDF Analyzer - Powered by AI for Investment Decision Making</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
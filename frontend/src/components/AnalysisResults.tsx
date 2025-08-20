'use client'

import { useState } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  MessageSquare, 
  FileText,
  Target,
  Shield,
  Users,
  DollarSign,
  Award,
  Building,
  Calculator
} from 'lucide-react'
import { 
  RadialBarChart, 
  RadialBar, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip
} from 'recharts'
import * as Tabs from '@radix-ui/react-tabs'
import clsx from 'clsx'
import { ChatInterface } from './ChatInterface'

interface AnalysisResultsProps {
  data: {
    analysis_id?: string
    overall_ipo_score: number
    readiness_level?: string
    filename?: string
    timestamp: string
    processing_time_seconds?: number
    confidence_score?: number
    company_metadata?: {
      company_name?: string
      industry?: string
      founding_year?: number
      stage?: string
      employee_count?: number
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
      critical_gaps?: string[]
    }
    risk_assessment?: {
      key_risks?: string[]
      information_gaps?: string[]
      risk_level?: string
    }
    competitive_positioning?: string
    follow_up_questions?: {
      questions?: string[]
      priority_areas?: string[]
    }
    financial_highlights?: {
      revenue?: string
      profit?: string
      growth_rate?: string
      funding_raised?: string
      valuation?: string
      burn_rate?: string
      runway?: string
      other_metrics?: string
    }
  }
}

const criteriaIcons = {
  'Basic Company Info': Building,
  'Mission & Core Business': Target,
  'Defensibility / IP / MOAT': Shield,
  'Regulatory Approvals & Compliance': FileText,
  'Commercial Traction & Validation': TrendingUp,
  'Segment-level Unit Economics': DollarSign,
  'Equity Cap Table': Users,
  'Key Risks & Information Gaps': AlertTriangle
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316']

export function AnalysisResults({ data }: AnalysisResultsProps) {
  console.log("Gemini data", data)
  const [activeTab, setActiveTab] = useState('overview')

  const getReadinessColor = (score: number) => {
    if (score >= 86) return 'text-emerald-600 bg-emerald-50 border-emerald-200'
    if (score >= 66) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (score >= 41) return 'text-amber-600 bg-amber-50 border-amber-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getScoreColor = (score: number) => {
    if (score >= 8.5) return 'bg-emerald-500'
    if (score >= 7) return 'bg-blue-500'
    if (score >= 5) return 'bg-amber-500'
    return 'bg-red-500'
  }

  // Prepare chart data
  const overallScoreData = [
    {
      name: 'IPO Readiness',
      value: data.overall_ipo_score,
      fill: '#3B82F6'
    }
  ]

  const criteriaData = data.criterion_scores?.map((criterion, index: number) => ({
    name: criterion.name.replace(' / ', '/\n'),
    score: criterion.score,
    fullName: criterion.name,
    fill: COLORS[index % COLORS.length]
  })) || []

  return (
    <div className="space-y-8">
      {/* Header Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">{data.filename}</h3>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full border font-medium ${getReadinessColor(data.overall_ipo_score)}`}>
                {data.readiness_level}
              </div>
              <span className="text-sm text-slate-700">
                Analyzed on {new Date(data.timestamp).toLocaleDateString()}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-slate-900">{Math.round(data.overall_ipo_score)}</div>
            <div className="text-sm text-slate-800">/ 100</div>
          </div>
        </div>

        {/* Overall Score Visualization */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Overall IPO Readiness Score</h4>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={overallScoreData}>
                  <RadialBar dataKey="value" cornerRadius={10} fill="#3B82F6" />
                  <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="fill-slate-900 text-2xl font-bold">
                    {Math.round(data.overall_ipo_score)}%
                  </text>
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-slate-900 mb-3">Key Metrics</h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-slate-800">Processing Time</span>
                <span className="font-medium text-slate-900">{data.processing_time_seconds?.toFixed(1)}s</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-800">Company</span>
                <span className="font-medium text-slate-900">{data.company_metadata?.company_name || 'Not specified'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-800">Industry</span>
                <span className="font-medium text-slate-900">{data.company_metadata?.industry || 'Not specified'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabbed Content */}
      <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
        <Tabs.List className="flex space-x-1 bg-slate-100 p-1 rounded-lg">
          {[
            { value: 'overview', label: 'Overview', icon: BarChart3 },
            { value: 'criteria', label: 'Detailed Scores', icon: Award },
            { value: 'insights', label: 'Insights & Risks', icon: AlertTriangle },
            { value: 'financial', label: 'Key Financial Metrics', icon: Calculator },
            { value: 'recommendations', label: 'Recommendations', icon: CheckCircle2 },
            { value: 'chat', label: 'Ask Questions', icon: MessageSquare }
          ].map(tab => {
            const Icon = tab.icon
            return (
              <Tabs.Trigger
                key={tab.value}
                value={tab.value}
                className={clsx(
                  'flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-all',
                  activeTab === tab.value
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </Tabs.Trigger>
            )
          })}
        </Tabs.List>

        {/* Overview Tab */}
        <Tabs.Content value="overview" className="mt-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Criteria Scores Chart */}
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h4 className="font-semibold text-slate-900 mb-4">Criteria Breakdown</h4>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={criteriaData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      fontSize={12}
                    />
                    <YAxis domain={[0, 10]} />
                    <Tooltip 
                      formatter={(value: number, name: string, props: { payload?: { fullName: string } }) => [
                        `${value}/10`, 
                        props.payload?.fullName || name
                      ]}
                    />
                    <Bar dataKey="score" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h4 className="font-semibold text-slate-900 mb-4">Executive Summary</h4>
              <div className="space-y-4">
                <div>
                  <h5 className="font-medium text-slate-800 mb-2">Overall Assessment</h5>
                  <p className="text-slate-800 text-sm leading-relaxed">
                    {data.executive_summary?.overall_assessment || 'Assessment not available'}
                  </p>
                </div>
                
                <div>
                  <h5 className="font-medium text-slate-800 mb-2">Key Highlights</h5>
                  <ul className="space-y-1">
                    {data.executive_summary?.key_highlights?.slice(0, 3).map((highlight, index: number) => (
                      <li key={index} className="flex items-start space-x-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                        <span className="text-slate-800">{highlight}</span>
                      </li>
                    )) || []}
                  </ul>
                </div>

                <div>
                  <h5 className="font-medium text-slate-800 mb-2">Recommendation</h5>
                  <p className="text-slate-800 text-sm leading-relaxed">
                    {data.executive_summary?.recommendation || 'Recommendation not available'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Tabs.Content>

        {/* Detailed Criteria Tab */}
        <Tabs.Content value="criteria" className="mt-6">
          <div className="grid gap-6">
            {data.criterion_scores?.map((criterion, index: number) => {
              const Icon = criteriaIcons[criterion.name as keyof typeof criteriaIcons] || Award
              return (
                <div key={index} className="bg-white rounded-xl border border-slate-200 p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="bg-blue-100 p-2 rounded-lg">
                        <Icon className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-900">{criterion.name}</h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <div className={`h-2 w-16 rounded-full ${getScoreColor(criterion.score)}`}></div>
                          <span className="text-sm font-medium text-slate-700">
                            {criterion.score}/10
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-4">
                    <div>
                      <h5 className="font-medium text-slate-800 mb-2">Rationale</h5>
                      <p className="text-sm text-slate-800 leading-relaxed">
                        {criterion.rationale}
                      </p>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-slate-800 mb-2">Strengths</h5>
                      <ul className="space-y-1">
                        {criterion.strengths?.map((strength, idx: number) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm">
                            <CheckCircle2 className="h-3 w-3 text-green-600 mt-1 flex-shrink-0" />
                            <span className="text-slate-800">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-slate-800 mb-2">Areas for Improvement</h5>
                      <ul className="space-y-1">
                        {criterion.weaknesses?.map((weakness, idx: number) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm">
                            <AlertTriangle className="h-3 w-3 text-amber-600 mt-1 flex-shrink-0" />
                            <span className="text-slate-800">{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Tabs.Content>

        {/* Insights & Risks Tab */}
        <Tabs.Content value="insights" className="mt-6">
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h4 className="font-semibold text-slate-900 mb-4 flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                <span>Key Risks</span>
              </h4>
              <div className="space-y-3">
                {data.risk_assessment?.key_risks?.map((risk, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-red-800">{risk}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h4 className="font-semibold text-slate-900 mb-4 flex items-center space-x-2">
                <FileText className="h-5 w-5 text-amber-600" />
                <span>Information Gaps</span>
              </h4>
              <div className="space-y-3">
                {data.risk_assessment?.information_gaps?.map((gap, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-amber-50 rounded-lg">
                    <FileText className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-amber-800">{gap}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6 mt-6">
            <h4 className="font-semibold text-slate-900 mb-4">Competitive Positioning</h4>
            <p className="text-slate-800 leading-relaxed">
              {data.competitive_positioning}
            </p>
          </div>
        </Tabs.Content>

        {/* Financial Metrics Tab */}
        <Tabs.Content value="financial" className="mt-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h4 className="font-semibold text-slate-900 mb-6 flex items-center space-x-2">
              <Calculator className="h-5 w-5 text-blue-600" />
              <span>Key Financial Metrics</span>
            </h4>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Revenue */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <DollarSign className="h-5 w-5 text-blue-600" />
                  <h5 className="font-semibold text-blue-900">Revenue</h5>
                </div>
                <p className="text-blue-800 text-sm">{data.financial_highlights?.revenue || 'N/A'}</p>
              </div>

              {/* Profit */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <h5 className="font-semibold text-green-900">Profit/Loss</h5>
                </div>
                <p className="text-green-800 text-sm">{data.financial_highlights?.profit || 'N/A'}</p>
              </div>

              {/* Growth Rate */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                <div className="flex items-center space-x-2 mb-2">
                  <BarChart3 className="h-5 w-5 text-purple-600" />
                  <h5 className="font-semibold text-purple-900">Growth Rate</h5>
                </div>
                <p className="text-purple-800 text-sm">{data.financial_highlights?.growth_rate || 'N/A'}</p>
              </div>

              {/* Funding Raised */}
              <div className="bg-gradient-to-br from-amber-50 to-amber-100 p-4 rounded-lg border border-amber-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Building className="h-5 w-5 text-amber-600" />
                  <h5 className="font-semibold text-amber-900">Funding Raised</h5>
                </div>
                <p className="text-amber-800 text-sm">{data.financial_highlights?.funding_raised || 'N/A'}</p>
              </div>

              {/* Valuation */}
              <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-4 rounded-lg border border-indigo-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Award className="h-5 w-5 text-indigo-600" />
                  <h5 className="font-semibold text-indigo-900">Valuation</h5>
                </div>
                <p className="text-indigo-800 text-sm">{data.financial_highlights?.valuation || 'N/A'}</p>
              </div>

              {/* Burn Rate */}
              <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <h5 className="font-semibold text-red-900">Burn Rate</h5>
                </div>
                <p className="text-red-800 text-sm">{data.financial_highlights?.burn_rate || 'N/A'}</p>
              </div>

              {/* Runway */}
              <div className="bg-gradient-to-br from-teal-50 to-teal-100 p-4 rounded-lg border border-teal-200">
                <div className="flex items-center space-x-2 mb-2">
                  <Target className="h-5 w-5 text-teal-600" />
                  <h5 className="font-semibold text-teal-900">Financial Runway</h5>
                </div>
                <p className="text-teal-800 text-sm">{data.financial_highlights?.runway || 'N/A'}</p>
              </div>

              {/* Other Metrics */}
              {data.financial_highlights?.other_metrics && data.financial_highlights.other_metrics !== 'N/A' && (
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-lg border border-gray-200 md:col-span-2 lg:col-span-3">
                  <div className="flex items-center space-x-2 mb-2">
                    <Calculator className="h-5 w-5 text-gray-600" />
                    <h5 className="font-semibold text-gray-900">Other Financial Metrics</h5>
                  </div>
                  <p className="text-gray-800 text-sm">{data.financial_highlights.other_metrics}</p>
                </div>
              )}
            </div>
          </div>
        </Tabs.Content>

        {/* Recommendations Tab */}
        <Tabs.Content value="recommendations" className="mt-6">
          <div className="grid gap-6">
            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h4 className="font-semibold text-slate-900 mb-4 flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                <span>Questions for Next Meeting</span>
              </h4>
              <div className="space-y-3">
                {data.follow_up_questions?.questions?.map((question, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
                    <div className="bg-blue-100 text-blue-600 rounded-full p-1 mt-1 flex-shrink-0">
                      <span className="block w-2 h-2 rounded-full bg-current"></span>
                    </div>
                    <p className="text-sm text-blue-800 font-medium">{question}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6">
              <h4 className="font-semibold text-slate-900 mb-4 flex items-center space-x-2">
                <Target className="h-5 w-5 text-green-600" />
                <span>Priority Areas</span>
              </h4>
              <div className="space-y-3">
                {data.follow_up_questions?.priority_areas?.map((area, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
                    <Target className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-green-800">{area}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Tabs.Content>

        {/* Chat Tab */}
        <Tabs.Content value="chat" className="mt-6">
          <ChatInterface 
            analysisId={data.analysis_id || 'unknown'}
            companyName={data.company_metadata?.company_name}
            className="h-[700px]"
          />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
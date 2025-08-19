'use client'

import { BarChart3, FileText, Brain, CheckCircle } from 'lucide-react'
import { useState, useEffect } from 'react'

const loadingSteps = [
  {
    icon: FileText,
    title: 'Extracting Content',
    description: 'Analyzing PDF structure and extracting text, tables, and sections...',
    duration: 3000
  },
  {
    icon: Brain,
    title: 'AI Analysis',
    description: 'Evaluating content across 8 IPO readiness criteria...',
    duration: 5000
  },
  {
    icon: BarChart3,
    title: 'Generating Scores',
    description: 'Calculating scores and preparing detailed insights...',
    duration: 2000
  },
  {
    icon: CheckCircle,
    title: 'Finalizing Report',
    description: 'Compiling comprehensive analysis and recommendations...',
    duration: 1000
  }
]

export function LoadingSpinner() {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {

    let currentDuration = 0

    const totalTime = loadingSteps.reduce((sum, step) => sum + step.duration, 0)

    const updateProgress = () => {
      const interval = setInterval(() => {
        currentDuration += 100
        const newProgress = (currentDuration / totalTime) * 100
        setProgress(Math.min(newProgress, 100))

        // Update current step
        let stepIndex = 0
        let stepStartTime = 0
        
        for (let i = 0; i < loadingSteps.length; i++) {
          if (currentDuration >= stepStartTime && currentDuration < stepStartTime + loadingSteps[i].duration) {
            stepIndex = i
            break
          }
          stepStartTime += loadingSteps[i].duration
          if (i === loadingSteps.length - 1) stepIndex = i
        }
        
        setCurrentStep(stepIndex)

        if (currentDuration >= totalTime) {
          clearInterval(interval)
        }
      }, 100)

      return interval
    }

    const interval = updateProgress()
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-8 max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-2xl w-fit mx-auto mb-4">
          <div className="animate-spin">
            <BarChart3 className="h-8 w-8 text-white" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Analyzing Your Pitch Deck</h2>
        <p className="text-slate-600">This may take a few moments as we perform comprehensive AI analysis</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-slate-600 mb-2">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {loadingSteps.map((step, index) => {
          const Icon = step.icon
          const isActive = index === currentStep
          const isCompleted = index < currentStep


          return (
            <div
              key={index}
              className={`flex items-start space-x-4 p-4 rounded-lg transition-all duration-300 ${
                isActive
                  ? 'bg-blue-50 border border-blue-200'
                  : isCompleted
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-slate-50 border border-slate-200'
              }`}
            >
              <div
                className={`p-2 rounded-lg ${
                  isActive
                    ? 'bg-blue-100 text-blue-600'
                    : isCompleted
                    ? 'bg-green-100 text-green-600'
                    : 'bg-slate-100 text-slate-400'
                }`}
              >
                {isActive ? (
                  <div className="animate-pulse">
                    <Icon className="h-5 w-5" />
                  </div>
                ) : (
                  <Icon className="h-5 w-5" />
                )}
              </div>
              <div className="flex-1">
                <h3
                  className={`font-medium ${
                    isActive
                      ? 'text-blue-900'
                      : isCompleted
                      ? 'text-green-900'
                      : 'text-slate-500'
                  }`}
                >
                  {step.title}
                  {isActive && (
                    <span className="ml-2 text-blue-600">
                      <span className="animate-pulse">●</span>
                    </span>
                  )}
                  {isCompleted && (
                    <span className="ml-2 text-green-600">✓</span>
                  )}
                </h3>
                <p
                  className={`text-sm ${
                    isActive
                      ? 'text-blue-700'
                      : isCompleted
                      ? 'text-green-700'
                      : 'text-slate-400'
                  }`}
                >
                  {step.description}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Additional Info */}
      <div className="mt-8 p-4 bg-slate-50 rounded-lg">
        <p className="text-sm text-slate-600 text-center">
          Our AI is analyzing your pitch deck content, financial data, and business model 
          to provide comprehensive IPO readiness insights.
        </p>
      </div>
    </div>
  )
}
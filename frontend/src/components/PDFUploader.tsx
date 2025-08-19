'use client'

import { useCallback, useState } from 'react'
import { useDropzone, FileRejection } from 'react-dropzone'
import { Upload, FileText, X, AlertCircle } from 'lucide-react'
import clsx from 'clsx'
import { endpoints } from './../lib/config'

interface PDFUploaderProps {
  onAnalysisStart: () => void
  onAnalysisComplete: (data: unknown) => void
  onError: (error: string) => void
}

export function PDFUploader({ onAnalysisStart, onAnalysisComplete, onError }: PDFUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      if (rejection.errors.some((e) => e.code === 'file-invalid-type')) {
        onError('Please select a valid PDF file')
      } else if (rejection.errors.some((e) => e.code === 'file-too-large')) {
        onError('File size must be less than 20MB')
      } else {
        onError('File upload failed. Please try again.')
      }
      return
    }

    const file = acceptedFiles[0]
    if (file) {
      // Double check file type by extension as well
      const fileName = file.name.toLowerCase()
      if (file.type === 'application/pdf' || fileName.endsWith('.pdf')) {
        setSelectedFile(file)
      } else {
        onError('Please select a valid PDF file')
      }
    }
  }, [onError])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/x-pdf': ['.pdf'],
      'application/acrobat': ['.pdf'],
      'applications/vnd.pdf': ['.pdf'],
      'text/pdf': ['.pdf'],
      'text/x-pdf': ['.pdf']
    },
    maxFiles: 1,
    maxSize: 20 * 1024 * 1024, // 20MB
    multiple: false,
    noClick: false,
    noKeyboard: false
  })

  const removeFile = () => {
    setSelectedFile(null)
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      onError('Please select a PDF file first')
      return
    }

    setIsUploading(true)
    onAnalysisStart()

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      // Check if backend is accessible first
      try {
        console.log(endpoints)
        const healthResponse = await fetch(endpoints.health, { method: 'GET' })
        if (!healthResponse.ok) {
          throw new Error('Backend server is not responding. Please make sure the backend is running.')
        }
      } catch {
        throw new Error('Cannot connect to backend server. Please ensure the backend is running at http://localhost:8000')
      }

      const response = await fetch(endpoints.analyzePdf, {
        method: 'POST',
        body: formData,
        headers: {
          // Don't set Content-Type header - let the browser set it with boundary for FormData
        }
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          detail: `Server error (${response.status}): ${response.statusText}` 
        }))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      onAnalysisComplete(result)
    } catch (error) {
      console.error('Analysis error:', error)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        onError('Cannot connect to the analysis server. Please ensure the backend is running.')
      } else {
        onError(error instanceof Error ? error.message : 'Analysis failed. Please try again.')
      }
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
          {
            'border-blue-300 bg-blue-50': isDragActive && !isDragReject,
            'border-red-300 bg-red-50': isDragReject,
            'border-slate-300 bg-white hover:border-blue-400 hover:bg-blue-50/50': !isDragActive && !selectedFile,
            'border-green-300 bg-green-50': selectedFile
          }
        )}
      >
        <input {...getInputProps()} />
        
        {selectedFile ? (
          <div className="space-y-4">
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-green-600" />
                  <div className="text-left">
                    <p className="font-medium text-slate-900">{selectedFile.name}</p>
                    <p className="text-sm text-slate-600">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    removeFile()
                  }}
                  className="text-slate-400 hover:text-slate-600 p-1"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
            <p className="text-sm text-green-700">
              PDF ready for analysis. Click &quot;Analyze Deck&quot; to begin.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-xl w-fit mx-auto">
              <Upload className="h-8 w-8 text-white" />
            </div>
            
            {isDragActive ? (
              isDragReject ? (
                <div className="space-y-2">
                  <AlertCircle className="h-6 w-6 text-red-500 mx-auto" />
                  <p className="text-red-600 font-medium">Only PDF files are supported</p>
                </div>
              ) : (
                <p className="text-blue-600 font-medium">Drop your PDF here...</p>
              )
            ) : (
              <div className="space-y-2">
                            <p className="text-lg font-medium text-slate-900">
              Drag &amp; drop your pitch deck PDF here
            </p>
                <p className="text-slate-600">or click to browse files</p>
                <p className="text-sm text-slate-500">
                  Maximum file size: 20MB
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action Button */}
      {selectedFile && (
        <div className="flex justify-center">
          <button
            onClick={handleAnalyze}
            disabled={isUploading}
            className={clsx(
              'px-8 py-3 rounded-lg font-medium transition-all duration-200',
              'bg-gradient-to-r from-blue-600 to-indigo-600 text-white',
              'hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
            )}
          >
            {isUploading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>Analyzing...</span>
              </div>
            ) : (
              'Analyze Pitch Deck'
            )}
          </button>
        </div>
      )}

      {/* Upload Instructions */}
      <div className="bg-slate-50 rounded-lg p-6">
        <h3 className="font-medium text-slate-900 mb-3">What happens next?</h3>
        <div className="space-y-2 text-sm text-slate-600">
          <div className="flex items-start space-x-2">
            <div className="bg-blue-100 text-blue-600 rounded-full p-1 mt-0.5">
              <span className="block w-1.5 h-1.5 rounded-full bg-current"></span>
            </div>
            <p>Your PDF will be processed using advanced AI document analysis</p>
          </div>
          <div className="flex items-start space-x-2">
            <div className="bg-blue-100 text-blue-600 rounded-full p-1 mt-0.5">
              <span className="block w-1.5 h-1.5 rounded-full bg-current"></span>
            </div>
            <p>Content will be evaluated across 8 key IPO readiness criteria</p>
          </div>
          <div className="flex items-start space-x-2">
            <div className="bg-blue-100 text-blue-600 rounded-full p-1 mt-0.5">
              <span className="block w-1.5 h-1.5 rounded-full bg-current"></span>
            </div>
            <p>You&apos;ll receive detailed scores, insights, and actionable recommendations</p>
          </div>
        </div>
      </div>
    </div>
  )
}
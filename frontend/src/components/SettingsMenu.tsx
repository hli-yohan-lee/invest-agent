'use client'

import { useState, useEffect } from 'react'
import { Settings, X, Eye, EyeOff, Check, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SettingsMenuProps {
  isOpen: boolean
  onClose: () => void
}

export default function SettingsMenu({ isOpen, onClose }: SettingsMenuProps) {
  const [openaiApiKey, setOpenaiApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [testStatus, setTestStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [testMessage, setTestMessage] = useState('')

  // 저장된 설정 불러오기
  useEffect(() => {
    const savedApiKey = localStorage.getItem('openai_api_key')
    if (savedApiKey) {
      setOpenaiApiKey(savedApiKey)
    }
  }, [])

  const handleTest = async () => {
    setIsTesting(true)
    setTestStatus('idle')
    setTestMessage('')

    try {
      const response = await fetch('http://localhost:8000/api/planning/test-openai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: "API 연결 테스트",
          openai_api_key: openaiApiKey 
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.status === 'success') {
          setTestStatus('success')
          setTestMessage('OpenAI API 연결 성공!')
        } else {
          setTestStatus('error')
          setTestMessage(data.message || 'API 연결 실패')
        }
      } else {
        setTestStatus('error')
        setTestMessage('서버 연결 실패')
      }
    } catch (error) {
      setTestStatus('error')
      setTestMessage('네트워크 오류')
    } finally {
      setIsTesting(false)
      setTimeout(() => {
        setTestStatus('idle')
        setTestMessage('')
      }, 3000)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    setSaveStatus('idle')

    try {
      // API 키 검증 (백엔드에 요청)
      const response = await fetch('http://localhost:8000/api/settings/validate-openai-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 인증 헤더 제거 (테스트용)
        },
        body: JSON.stringify({ api_key: openaiApiKey })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.valid) {
          // 로컬 스토리지에 저장
          localStorage.setItem('openai_api_key', openaiApiKey)
          setSaveStatus('success')
          setErrorMessage('')
          setTimeout(() => setSaveStatus('idle'), 2000)
        } else {
          setSaveStatus('error')
          setErrorMessage(data.message || 'API 키 검증에 실패했습니다.')
          setTimeout(() => setSaveStatus('idle'), 3000)
        }
      } else {
        const errorData = await response.json().catch(() => ({ message: '서버 오류가 발생했습니다.' }))
        setSaveStatus('error')
        setErrorMessage(errorData.message || '서버 연결에 실패했습니다.')
        setTimeout(() => setSaveStatus('idle'), 3000)
      }
    } catch (error) {
      // 네트워크 오류 등
      setSaveStatus('error')
      setErrorMessage('네트워크 연결을 확인해주세요.')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } finally {
      setIsSaving(false)
    }
  }

  const handleClear = () => {
    setOpenaiApiKey('')
    localStorage.removeItem('openai_api_key')
    setSaveStatus('idle')
    setErrorMessage('')
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center">
            <Settings className="w-5 h-5 text-gray-600 mr-2" />
            <h2 className="text-lg font-semibold text-gray-900">API 설정</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* OpenAI API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              OpenAI API Key
            </label>
            <div className="relative">
              <input
                type={showApiKey ? 'text' : 'password'}
                value={openaiApiKey}
                onChange={(e) => setOpenaiApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              OpenAI API 키를 입력하세요. 이 정보는 브라우저에만 저장됩니다.
            </p>
          </div>

          {/* Status Messages */}
          {saveStatus === 'success' && (
            <div className="flex items-center text-green-600 text-sm">
              <Check className="w-4 h-4 mr-2" />
              설정이 저장되었습니다.
            </div>
          )}
          
          {saveStatus === 'error' && (
            <div className="flex items-center text-red-600 text-sm">
              <AlertCircle className="w-4 h-4 mr-2" />
              {errorMessage || 'API 키 검증에 실패했습니다.'}
            </div>
          )}

          {/* Test Status Messages */}
          {testStatus === 'success' && (
            <div className="flex items-center text-green-600 text-sm">
              <Check className="w-4 h-4 mr-2" />
              {testMessage}
            </div>
          )}
          
          {testStatus === 'error' && (
            <div className="flex items-center text-red-600 text-sm">
              <AlertCircle className="w-4 h-4 mr-2" />
              {testMessage}
            </div>
          )}

          {/* Test Button */}
          <div>
            <button
              onClick={handleTest}
              disabled={isTesting || !openaiApiKey}
              className={cn(
                "w-full px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50",
                isTesting 
                  ? "bg-green-400 text-white" 
                  : "bg-green-600 hover:bg-green-700 text-white"
              )}
            >
              {isTesting ? 'API 연결 테스트 중...' : 'OpenAI API 연결 테스트'}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
          <button
            onClick={handleClear}
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
          >
            초기화
          </button>
          <button
            onClick={onClose}
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            취소
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !openaiApiKey}
            className={cn(
              "px-4 py-2 text-sm font-medium text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50",
              isSaving ? "bg-blue-400" : "bg-blue-600 hover:bg-blue-700"
            )}
          >
            {isSaving ? '저장 중...' : '저장'}
          </button>
        </div>
      </div>
    </div>
  )
}

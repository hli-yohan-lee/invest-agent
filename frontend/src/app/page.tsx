'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { Settings } from 'lucide-react'
import TabNavigation from '@/components/TabNavigation'
import InputBar from '@/components/InputBar'
import ChatInterface from '@/components/ChatInterface'
import WorkflowCanvas from '@/components/WorkflowCanvas'
import SettingsMenu from '@/components/SettingsMenu'

export default function Home() {
  const { currentTab } = useAppStore()
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  const renderActiveTab = () => {
    switch (currentTab) {
      case 'planning':
        return <ChatInterface />
      case 'workflow':
        return <WorkflowCanvas />
      case 'result':
        return (
          <div className="flex-1 bg-gray-50 rounded-lg p-8 flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">분석 결과</h3>
              <p className="text-gray-600">아직 분석 결과가 없습니다. 워크플로우를 실행해보세요.</p>
            </div>
          </div>
        )
      default:
        return <ChatInterface />
    }
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-gray-900">
              투자 분석 AI Agent 플랫폼
            </h1>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              title="API 설정"
            >
              <Settings className="w-5 h-5" />
            </button>
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium text-sm">AI</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Tab Navigation */}
        <TabNavigation />

        {/* Content Area */}
        <div className="flex-1 flex flex-col p-6">
          {/* Active Tab Content */}
          {renderActiveTab()}

          {/* Input Bar - Only show on planning tab */}
          {currentTab === 'planning' && (
            <div className="mt-4">
              <InputBar />
            </div>
          )}
        </div>
      </div>

      {/* Settings Menu */}
      <SettingsMenu 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  )
}

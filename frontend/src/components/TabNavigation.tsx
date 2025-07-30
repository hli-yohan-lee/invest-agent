'use client'

import { useAppStore } from '@/lib/store'
import { MessageCircle, Workflow, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function TabNavigation() {
  const { currentTab, setCurrentTab } = useAppStore()

  const tabs = [
    { id: 'planning' as const, label: '1. 플래닝', icon: MessageCircle },
    { id: 'workflow' as const, label: '2. 워크플로우', icon: Workflow },
    { id: 'result' as const, label: '3. 결과', icon: BarChart3 },
  ]

  return (
    <div className="border-b border-gray-200 bg-white">
      <nav className="flex space-x-8 px-6" aria-label="Tabs">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setCurrentTab(id)}
            className={cn(
              'flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              currentTab === id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <Icon className="w-5 h-5 mr-2" />
            {label}
          </button>
        ))}
      </nav>
    </div>
  )
}

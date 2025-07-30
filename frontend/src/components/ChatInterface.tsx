'use client'

import { useAppStore } from '@/lib/store'
import { User, Bot, Copy, Edit, RotateCcw } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function ChatInterface() {
  const { chatHistory, currentPlan } = useAppStore()

  return (
    <div className="flex-1 overflow-y-auto p-6 pb-32">
      <div className="max-w-4xl mx-auto space-y-6">
        {chatHistory.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              AI 투자 분석가에게 질문해보세요
            </h3>
            <p className="text-gray-500">
              아래 입력창에 투자 관련 질문이나 요청을 입력하세요
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {[
                "PER이 높은 기업 분석해줘",
                "ESG 점수가 높은 배당주 추천",
                "반도체 업종 재무제표 분석",
                "포트폴리오 최적화 전략"
              ].map((example) => (
                <button
                  key={example}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {chatHistory.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-4',
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.type === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}
                
                <div
                  className={cn(
                    'max-w-3xl px-4 py-3 rounded-lg',
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  )}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {message.type === 'assistant' && (
                    <div className="mt-3 flex gap-2">
                      <button className="p-1 text-gray-500 hover:text-gray-700 rounded">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="p-1 text-gray-500 hover:text-gray-700 rounded">
                        <Copy className="w-4 h-4" />
                      </button>
                      <button className="p-1 text-gray-500 hover:text-gray-700 rounded">
                        <RotateCcw className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
                
                {message.type === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            
            {/* 실행 확인 프롬프트 */}
            {chatHistory.length > 0 && chatHistory[chatHistory.length - 1].type === 'assistant' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                    <span className="font-medium text-yellow-800">실행하시겠습니까?</span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => useAppStore.getState().setCurrentTab('workflow')}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      실행
                    </button>
                    <button className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors">
                      수정
                    </button>
                  </div>
                </div>
                <div className="mt-2 text-sm text-yellow-700">
                  Ctrl + Enter 또는 실행 버튼을 눌러 워크플로우를 생성합니다
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

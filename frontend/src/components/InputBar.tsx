'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { Send, Mic } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function InputBar() {
  const [input, setInput] = useState('')
  const { addMessage, isLoading } = useAppStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    // 사용자 메시지 추가
    addMessage({
      type: 'user',
      content: input.trim(),
    })

    setInput('')

    // TODO: AI 응답 처리
    // 임시로 모의 응답 추가
    setTimeout(() => {
      addMessage({
        type: 'assistant',
        content: `다음과 같은 투자 분석 전략을 제안합니다:

1. 시장 데이터 수집
   - 주요 지수 및 개별 종목 데이터 수집
   - 거래량 및 변동성 분석

2. 기술적 분석
   - 이동평균선 분석
   - RSI 및 MACD 지표 확인

3. 기본적 분석
   - 재무제표 분석
   - 업종별 비교 분석

4. 투자 권고 생성
   - 리스크 평가
   - 목표가 설정

실행하시겠습니까?`,
      })
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="flex items-end space-x-4">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="투자 관련 질문을 입력하세요... (예: PER이 높은 기업 분석해줘)"
              className="w-full min-h-[24px] max-h-32 px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={1}
              style={{ 
                height: 'auto',
                minHeight: '48px'
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = 'auto'
                target.style.height = Math.min(target.scrollHeight, 128) + 'px'
              }}
            />
            <button
              type="button"
              className="absolute right-3 bottom-3 p-1 text-gray-400 hover:text-gray-600"
            >
              <Mic className="w-4 h-4" />
            </button>
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              'px-4 py-3 rounded-lg font-medium transition-colors',
              input.trim() && !isLoading
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <div className="mt-2 text-xs text-gray-500 text-center">
          Ctrl + Enter로 전송 • 최대 2000자
        </div>
      </div>
    </div>
  )
}

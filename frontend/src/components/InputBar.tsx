'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { Send, Mic } from 'lucide-react'
import { cn } from '@/lib/utils'

// JSON 응답 포맷팅 함수
function formatJsonResponse(data: any): string {
  if (!data || typeof data !== 'object') {
    return JSON.stringify(data, null, 2)
  }

  let formatted = ''
  
  // 분석 결과
  if (data.analysis) {
    formatted += `📊 **분석 결과**\n${data.analysis}\n\n`
  }
  
  // 계획 제목
  if (data.plan_title) {
    formatted += `📋 **${data.plan_title}**\n\n`
  }
  
  // 작업 목록
  if (data.tasks && Array.isArray(data.tasks) && data.tasks.length > 0) {
    formatted += `🔧 **실행 계획**\n`
    data.tasks.forEach((task: any, index: number) => {
      formatted += `\n**${index + 1}. ${task.title || `작업 ${index + 1}`}**\n`
      formatted += `${task.description || '설명 없음'}\n`
      
      if (task.agent_allowed && task.agent_allowed.length > 0) {
        formatted += `👥 담당 에이전트: ${task.agent_allowed.join(', ')}\n`
      }
      
      if (task.mcp_tools && task.mcp_tools.length > 0) {
        formatted += `🛠️ 사용 도구: ${task.mcp_tools.join(', ')}\n`
      }
      
      if (task.estimated_time) {
        formatted += `⏱️ 예상 시간: ${task.estimated_time}\n`
      }
      
      if (task.dependencies && task.dependencies.length > 0) {
        formatted += `🔗 종속성: ${task.dependencies.join(', ')}\n`
      }
    })
    formatted += '\n'
  }
  
  // 추가 질문
  if (data.clarification_questions && Array.isArray(data.clarification_questions) && data.clarification_questions.length > 0) {
    formatted += `❓ **추가 정보가 필요합니다**\n`
    data.clarification_questions.forEach((q: any, index: number) => {
      formatted += `\n${index + 1}. ${q.question || '질문 없음'}\n`
      if (q.context) {
        formatted += `   💡 ${q.context}\n`
      }
    })
    formatted += '\n'
  }
  
  // 메타 정보
  const metaInfo = []
  if (data.priority) metaInfo.push(`우선순위: ${data.priority}`)
  if (data.complexity) metaInfo.push(`복잡도: ${data.complexity}`)
  if (data.move_to_canvas !== undefined) metaInfo.push(`캔버스 이동: ${data.move_to_canvas ? '예' : '아니오'}`)
  
  if (metaInfo.length > 0) {
    formatted += `📌 **계획 정보**: ${metaInfo.join(' | ')}\n`
  }
  
  return formatted.trim()
}

export default function InputBar() {
  const [input, setInput] = useState('')
  const { addMessage, updateMessage, isLoading } = useAppStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    // OpenAI API 키 확인
    const openaiApiKey = localStorage.getItem('openai_api_key')
    if (!openaiApiKey) {
      addMessage({
        type: 'assistant',
        content: '⚠️ OpenAI API 키가 설정되지 않았습니다. 우상단 설정 버튼(⚙️)을 클릭하여 API 키를 설정해주세요.',
      })
      return
    }

    // 사용자 메시지 추가
    addMessage({
      type: 'user',
      content: input.trim(),
    })

    const userMessage = input.trim()
    setInput('')

    try {
      // 스트리밍 응답을 위한 fetch 요청
      const response = await fetch('http://localhost:8000/api/planning/chat-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          openai_api_key: openaiApiKey
        })
      })

      if (!response.ok) {
        throw new Error('서버 응답 오류')
      }

      // 스트리밍 응답 처리
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      
      // 빈 어시스턴트 메시지 생성 및 추가
      const assistantMessage = {
        type: 'assistant' as const,
        content: '',
      }
      addMessage(assistantMessage)
      
      // 방금 추가한 메시지의 ID를 가져오기 위해 store에서 최신 메시지 찾기
      const { chatHistory } = useAppStore.getState()
      const lastMessageId = chatHistory[chatHistory.length - 1]?.id
      
      let accumulatedContent = ''
      let isJsonComplete = false
      
      if (reader && lastMessageId) {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break
            
            const chunk = decoder.decode(value)
            const lines = chunk.split('\n')
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  
                  if (data.type === 'content') {
                    accumulatedContent += data.content
                    // JSON이 완성되었는지 확인
                    if (accumulatedContent.includes('```json') && accumulatedContent.includes('```')) {
                      isJsonComplete = true
                    }
                    // 같은 메시지 박스에서 내용 업데이트 (실시간 표시)
                    updateMessage(lastMessageId, accumulatedContent)
                  } else if (data.type === 'done') {
                    // 완료 시 최종 응답 처리
                    if (data.full_response) {
                      try {
                        // JSON 응답 파싱 및 포맷팅
                        const parsedJson = JSON.parse(data.full_response)
                        const formattedResponse = formatJsonResponse(parsedJson)
                        updateMessage(lastMessageId, formattedResponse)
                      } catch (jsonError) {
                        // JSON 파싱 실패 시 원본 텍스트 사용
                        updateMessage(lastMessageId, accumulatedContent)
                      }
                    }
                    break
                  } else if (data.type === 'error') {
                    updateMessage(lastMessageId, `❌ ${data.content}`)
                    break
                  }
                } catch (parseError) {
                  console.log('JSON 파싱 오류:', parseError)
                }
              }
            }
          }
        } finally {
          reader.releaseLock()
        }
      }
    } catch (error) {
      // 네트워크 오류 등
      addMessage({
        type: 'assistant',
        content: '❌ 서버와의 연결에 실패했습니다. 네트워크 상태를 확인해주세요.',
      })
    }
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

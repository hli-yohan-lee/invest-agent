'use client'

import { useEffect } from 'react'
import { useAppStore } from '@/lib/store'
import { CheckCircle, XCircle, Clock, TrendingUp, BarChart3, FileText, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function ResultView() {
  const { 
    currentResult, 
    results, 
    executionStatus, 
    nodes, 
    error,
    setCurrentResult 
  } = useAppStore()

  // 최신 결과 자동 선택
  useEffect(() => {
    if (results.length > 0 && !currentResult) {
      setCurrentResult(results[results.length - 1])
    }
  }, [results, currentResult, setCurrentResult])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'running':
        return <Clock className="w-5 h-5 text-blue-600 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'error':
        return 'bg-red-100 text-red-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const renderWorkflowStatus = () => {
    if (executionStatus === 'running') {
      return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <div className="flex items-center">
            <Clock className="w-6 h-6 text-blue-600 animate-spin mr-3" />
            <div>
              <h3 className="text-lg font-medium text-blue-900">워크플로우 실행 중</h3>
              <p className="text-blue-700 mt-1">분석을 수행하고 있습니다. 잠시만 기다려주세요...</p>
            </div>
          </div>
        </div>
      )
    }

    if (executionStatus === 'error') {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
          <div className="flex items-center">
            <AlertCircle className="w-6 h-6 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-medium text-red-900">워크플로우 실행 오류</h3>
              <p className="text-red-700 mt-1">{error || '알 수 없는 오류가 발생했습니다.'}</p>
            </div>
          </div>
        </div>
      )
    }

    return null
  }

  const renderNodeResults = () => {
    const taskNodes = nodes.filter(node => node.type === 'task' || node.type === 'result')
    
    if (taskNodes.length === 0) {
      return null
    }

    return (
      <div className="bg-white rounded-lg border border-gray-200 mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            작업 실행 결과
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {taskNodes.map((node) => (
            <div key={node.id} className="px-6 py-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  {getStatusIcon(node.data.status || 'pending')}
                  <h4 className="ml-3 font-medium text-gray-900">{node.data.label}</h4>
                </div>
                <span className={cn(
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getStatusColor(node.data.status || 'pending')
                )}>
                  {node.data.status === 'completed' ? '완료' : 
                   node.data.status === 'error' ? '오류' :
                   node.data.status === 'running' ? '실행중' : '대기'}
                </span>
              </div>
              
              {node.data.prompt && (
                <p className="text-sm text-gray-600 mb-3">{node.data.prompt}</p>
              )}
              
              {node.data.tool_used && (
                <div className="text-xs text-gray-500 mb-2">
                  사용된 도구: <span className="font-medium">{node.data.tool_used}</span>
                </div>
              )}
              
              {node.data.result && (
                <div className="bg-gray-50 rounded-md p-3 mt-3">
                  <div className="text-sm font-medium text-gray-700 mb-2">실행 결과:</div>
                  <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-auto max-h-32">
                    {typeof node.data.result === 'object' 
                      ? JSON.stringify(node.data.result, null, 2)
                      : String(node.data.result)
                    }
                  </pre>
                </div>
              )}
              
              {node.data.error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3 mt-3">
                  <div className="text-sm font-medium text-red-700 mb-1">오류:</div>
                  <div className="text-sm text-red-600">{node.data.error}</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  const renderFinalResult = () => {
    if (!currentResult) {
      return null
    }

    return (
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            최종 분석 결과
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {new Date(currentResult.metadata.timestamp).toLocaleString('ko-KR')}
          </p>
        </div>
        
        <div className="px-6 py-4">
          {currentResult.data.summary && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-2">요약</h4>
              <p className="text-gray-700">{currentResult.data.summary}</p>
            </div>
          )}
          
          {currentResult.data.finalResult && (
            <div className="bg-blue-50 rounded-md p-4">
              <h4 className="font-medium text-blue-900 mb-2 flex items-center">
                <FileText className="w-4 h-4 mr-2" />
                최종 결과
              </h4>
              <pre className="text-sm text-blue-800 whitespace-pre-wrap overflow-auto max-h-64">
                {typeof currentResult.data.finalResult === 'object'
                  ? JSON.stringify(currentResult.data.finalResult, null, 2)
                  : String(currentResult.data.finalResult)
                }
              </pre>
            </div>
          )}
          
          {currentResult.metadata.modules.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="font-medium text-gray-900 mb-2">사용된 도구</h4>
              <div className="flex flex-wrap gap-2">
                {currentResult.metadata.modules.map((module, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                  >
                    {module}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 bg-gray-50 overflow-auto">
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">분석 결과</h2>
          <p className="text-gray-600">
            워크플로우 실행 결과와 최종 분석 내용을 확인할 수 있습니다.
          </p>
        </div>

        {renderWorkflowStatus()}
        
        {/* 아직 결과가 없는 경우 */}
        {nodes.length === 0 && !currentResult && executionStatus === 'idle' && (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
            <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">분석 결과가 없습니다</h3>
            <p className="text-gray-600">
              플래닝 탭에서 질문을 입력하고 워크플로우를 생성한 후 실행해보세요.
            </p>
          </div>
        )}

        {/* 노드 실행 결과 */}
        {renderNodeResults()}

        {/* 최종 결과 */}
        {renderFinalResult()}
      </div>
    </div>
  )
}

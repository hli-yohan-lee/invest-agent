'use client'

import { useAppStore } from '@/lib/store'
import { useState } from 'react'

export default function ReportView() {
  const { 
    currentReport, 
    reports, 
    reportGenerating,
    setCurrentReport 
  } = useAppStore()
  
  const [selectedSection, setSelectedSection] = useState<string>('all')

  if (reportGenerating) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">보고서를 생성하고 있습니다...</p>
        </div>
      </div>
    )
  }

  if (!currentReport && reports.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            생성된 보고서가 없습니다
          </h3>
          <p className="text-gray-600 mb-4">
            워크플로우를 실행한 후 결과 탭에서 보고서를 생성하세요.
          </p>
        </div>
      </div>
    )
  }

  const displayReport = currentReport || reports[reports.length - 1]

  if (!displayReport) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-600">보고서를 불러올 수 없습니다.</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* 헤더 */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {displayReport.title}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              생성일: {displayReport.generatedAt.toLocaleString()}
              {displayReport.metadata.stocksAnalyzed && (
                <span className="ml-4">
                  분석 종목: {displayReport.metadata.stocksAnalyzed}개
                </span>
              )}
            </p>
          </div>
          
          {/* 보고서 선택 드롭다운 */}
          {reports.length > 1 && (
            <select
              value={displayReport.id}
              onChange={(e) => {
                const selectedReport = reports.find(r => r.id === e.target.value)
                if (selectedReport) {
                  setCurrentReport(selectedReport)
                }
              }}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              {reports.map((report) => (
                <option key={report.id} value={report.id}>
                  {report.title}
                </option>
              ))}
            </select>
          )}
        </div>
        
        {/* 섹션 필터 */}
        {displayReport.sections.length > 1 && (
          <div className="flex space-x-2 mt-4">
            <button
              onClick={() => setSelectedSection('all')}
              className={`px-3 py-1 rounded-md text-sm ${
                selectedSection === 'all'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              전체
            </button>
            {displayReport.sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setSelectedSection(section.id)}
                className={`px-3 py-1 rounded-md text-sm ${
                  selectedSection === section.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {section.title}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 보고서 내용 */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {selectedSection === 'all' ? (
            <div className="prose prose-lg max-w-none">
              <div 
                className="text-gray-800 leading-relaxed"
                style={{ whiteSpace: 'pre-wrap' }}
                dangerouslySetInnerHTML={{
                  __html: formatReportContent(displayReport.content)
                }}
              />
            </div>
          ) : (
            displayReport.sections
              .filter(section => section.id === selectedSection)
              .map((section) => (
                <div key={section.id} className="prose prose-lg max-w-none">
                  <h2 className="text-2xl font-semibold mb-4 text-gray-800">{section.title}</h2>
                  <div 
                    className="text-gray-800 leading-relaxed"
                    style={{ whiteSpace: 'pre-wrap' }}
                    dangerouslySetInnerHTML={{
                      __html: formatReportContent(section.content)
                    }}
                  />
                </div>
              ))
          )}
        </div>
      </div>

      {/* 푸터 */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <div>
            상태: <span className="font-medium">{getStatusText(displayReport.status)}</span>
          </div>
          <div>
            데이터 소스: {displayReport.metadata.dataSource?.join(', ') || '없음'}
          </div>
        </div>
      </div>
    </div>
  )
}

function formatReportContent(content: string): string {
  if (!content) return ''
  
  // 더 확실한 줄바꿈 처리
  let result = content
    // HTML 특수문자 이스케이프
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    
    // 마크다운 헤더
    .replace(/^# (.*$)/gm, '<h1 style="font-size: 1.5rem; font-weight: bold; margin: 1rem 0; color: #1f2937;">$1</h1>')
    .replace(/^## (.*$)/gm, '<h2 style="font-size: 1.25rem; font-weight: 600; margin: 0.75rem 0; color: #374151;">$1</h2>')
    .replace(/^### (.*$)/gm, '<h3 style="font-size: 1.125rem; font-weight: 500; margin: 0.5rem 0; color: #4b5563;">$1</h3>')
    
    // 볼드, 이탤릭
    .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>')
    
    // 리스트 항목
    .replace(/^[\-\*\+] (.*)$/gm, '<div style="margin-left: 1rem; margin-bottom: 0.25rem;">• $1</div>')
    .replace(/^\d+\. (.*)$/gm, '<div style="margin-left: 1rem; margin-bottom: 0.25rem;">$1</div>')
  
  // 줄바꿈을 HTML로 변환 - 가장 중요!
  result = result
    .replace(/\n\n\n+/g, '<br><br><br>')  // 3개 이상
    .replace(/\n\n/g, '<br><br>')         // 이중 줄바꿈
    .replace(/\n/g, '<br>')               // 단일 줄바꿈
  
  // 각 줄을 div로 감싸서 확실히 줄바꿈되도록
  const lines = result.split('<br>')
  result = lines.map(line => line.trim() ? `<div style="margin-bottom: 0.5rem;">${line}</div>` : '<div style="height: 0.5rem;"></div>').join('')
  
  return result
}

function getStatusText(status: string): string {
  switch (status) {
    case 'generating':
      return '생성 중'
    case 'completed':
      return '생성 완료'
    case 'error':
      return '생성 실패'
    default:
      return '알 수 없음'
  }
}

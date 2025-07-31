import React, { useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Settings, TrendingUp, FileText, Database, ChevronDown, ChevronUp, Play } from 'lucide-react';

interface TaskNodeData {
  label: string;
  type?: 'analysis' | 'data' | 'report' | 'general';
  status?: 'pending' | 'running' | 'completed' | 'error';
  prompt?: string;
  result?: any;
  error?: string;
  tool_used?: string;
  parameters_used?: Record<string, any>;
}

interface TaskNodeProps {
  data: TaskNodeData;
  selected?: boolean;
  onDataChange?: (newData: TaskNodeData) => void;
}

const getTaskIcon = (type: string) => {
  switch (type) {
    case 'analysis':
      return TrendingUp;
    case 'data':
      return Database;
    case 'report':
      return FileText;
    default:
      return Settings;
  }
};

const getTaskColor = (type: string) => {
  switch (type) {
    case 'analysis':
      return 'bg-blue-50 border-blue-200';
    case 'data':
      return 'bg-purple-50 border-purple-200';
    case 'report':
      return 'bg-orange-50 border-orange-200';
    default:
      return 'bg-gray-50 border-gray-200';
  }
};

const getStatusColor = (status?: string) => {
  switch (status) {
    case 'running':
      return 'bg-yellow-400 animate-pulse';
    case 'completed':
      return 'bg-green-400';
    case 'error':
      return 'bg-red-400';
    default:
      return 'bg-gray-300';
  }
};

export default function TaskNode({ data, selected }: TaskNodeProps) {
  const [showDetails, setShowDetails] = useState(false);
  const Icon = getTaskIcon(data.type || 'general');
  
  // 실행 결과를 문자열로 포맷팅
  const formatResult = (result: any) => {
    if (typeof result === 'string') {
      return result;
    }
    if (typeof result === 'object') {
      return JSON.stringify(result, null, 2);
    }
    return String(result);
  };
  
  return (
    <div 
      className={`
        ${getTaskColor(data.type || 'general')} 
        border-2 rounded-lg p-3 shadow-sm min-w-[200px] max-w-[280px]
        ${selected ? 'ring-2 ring-blue-400' : ''}
        transition-all duration-200
      `}
    >
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon size={16} className="text-gray-600" />
          <span className="font-medium text-sm">{data.label}</span>
        </div>
        
        {/* 상태 표시기 */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${getStatusColor(data.status)}`} />
          {(data.result || data.error) && (
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-gray-500 hover:text-gray-700"
            >
              {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </div>
      </div>
      
      {/* 작업 유형 표시 */}
      <div className="text-xs text-gray-500 mb-2">
        {data.type === 'analysis' && '분석 작업'}
        {data.type === 'data' && '데이터 수집'}
        {data.type === 'report' && '보고서 생성'}
        {data.type === 'general' && '일반 작업'}
      </div>
      
      {/* 상태별 메시지 */}
      <div className="text-xs mb-2">
        {data.status === 'pending' && (
          <span className="text-gray-600 flex items-center gap-1">
            <Play size={12} />
            실행 대기 중
          </span>
        )}
        {data.status === 'running' && (
          <span className="text-yellow-700 flex items-center gap-1">
            <div className="w-3 h-3 border border-yellow-500 border-t-transparent rounded-full animate-spin" />
            실행 중...
          </span>
        )}
        {data.status === 'completed' && (
          <span className="text-green-700">✓ 실행 완료</span>
        )}
        {data.status === 'error' && (
          <span className="text-red-700">✗ 실행 실패</span>
        )}
      </div>
      
      {/* 사용된 도구 표시 */}
      {data.tool_used && (
        <div className="text-xs text-gray-600 mb-2">
          도구: {data.tool_used.replace('get_', '').replace(/_/g, ' ')}
        </div>
      )}
      
      {/* 세부 정보 (접을 수 있음) */}
      {showDetails && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          {/* 실행 결과 */}
          {data.result && (
            <div className="mb-3">
              <div className="text-xs font-medium text-gray-700 mb-1">실행 결과:</div>
              <div className="text-xs bg-white rounded p-2 border max-h-32 overflow-y-auto font-mono">
                {formatResult(data.result).substring(0, 500)}
                {formatResult(data.result).length > 500 && '...'}
              </div>
            </div>
          )}
          
          {/* 오류 메시지 */}
          {data.error && (
            <div className="mb-3">
              <div className="text-xs font-medium text-red-700 mb-1">오류:</div>
              <div className="text-xs bg-red-50 rounded p-2 border border-red-200 text-red-700">
                {data.error}
              </div>
            </div>
          )}
          
          {/* 사용된 매개변수 */}
          {data.parameters_used && Object.keys(data.parameters_used).length > 0 && (
            <div className="mb-3">
              <div className="text-xs font-medium text-gray-700 mb-1">매개변수:</div>
              <div className="text-xs bg-gray-50 rounded p-2 border font-mono">
                {JSON.stringify(data.parameters_used, null, 2)}
              </div>
            </div>
          )}
          
          {/* 프롬프트 */}
          {data.prompt && (
            <div>
              <div className="text-xs font-medium text-gray-700 mb-1">설명:</div>
              <div className="text-xs text-gray-600 bg-gray-50 rounded p-2 border">
                {data.prompt.length > 100 ? data.prompt.substring(0, 100) + '...' : data.prompt}
              </div>
            </div>
          )}
        </div>
      )}
      
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  );
}

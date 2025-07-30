import React, { useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Settings, TrendingUp, FileText, Database, ChevronDown } from 'lucide-react';

interface TaskNodeData {
  label: string;
  type: 'analysis' | 'data' | 'report' | 'general';
  status?: 'pending' | 'running' | 'completed' | 'error';
  prompt?: string;
  useAgent?: boolean;
  mcpModules?: string[];
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
      return 'bg-yellow-400';
    case 'completed':
      return 'bg-green-400';
    case 'error':
      return 'bg-red-400';
    default:
      return 'bg-gray-400';
  }
};

const availableModules = [
  { id: 'naver-securities', label: '네이버 증권' },
  { id: 'toss-securities', label: '토스 증권' },
  { id: 'kakao-securities', label: '카카오페이 증권' },
  { id: 'yahoo-finance', label: 'Yahoo Finance' },
  { id: 'korea-exchange', label: '한국거래소' },
  { id: 'financial-analysis', label: '재무분석 툴' },
  { id: 'market-data', label: '시장데이터' },
];

export default function TaskNode({ data, selected, onDataChange }: TaskNodeProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const Icon = getTaskIcon(data.type);
  const colorClass = getTaskColor(data.type);
  const statusColor = getStatusColor(data.status);

  const handlePromptChange = (newPrompt: string) => {
    if (onDataChange) {
      onDataChange({ ...data, prompt: newPrompt });
    }
  };

  const handleAgentToggle = () => {
    if (onDataChange) {
      onDataChange({ ...data, useAgent: !data.useAgent });
    }
  };

  const handleModuleToggle = (moduleId: string) => {
    if (onDataChange) {
      const currentModules = data.mcpModules || [];
      const newModules = currentModules.includes(moduleId)
        ? currentModules.filter(id => id !== moduleId)
        : [...currentModules, moduleId];
      onDataChange({ ...data, mcpModules: newModules });
    }
  };

  return (
    <div className={`shadow-lg rounded-lg ${colorClass} border-2 min-w-[350px] max-w-[400px] ${
      selected ? 'border-blue-400' : ''
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-blue-500 border-2 border-white"
      />
      
      {/* Header */}
      <div className="flex items-center space-x-3 p-4 pb-2">
        <div className="flex items-center justify-center w-8 h-8 bg-white rounded-full shadow-sm">
          <Icon className="w-4 h-4 text-gray-600" />
        </div>
        <div className="flex-1">
          <div className="text-gray-900 font-medium text-sm">{data.label}</div>
          <div className="text-gray-500 text-xs capitalize">{data.type} 작업</div>
        </div>
        {data.status && (
          <div className={`w-3 h-3 rounded-full ${statusColor}`} />
        )}
      </div>

      {/* Content */}
      <div className="px-4 pb-4 space-y-3">
        {/* Prompt Textarea */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            프롬프트
          </label>
          <textarea
            value={data.prompt || ''}
            onChange={(e) => handlePromptChange(e.target.value)}
            placeholder="작업 지시사항을 입력하세요..."
            className="w-full h-20 px-3 py-2 text-sm border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Agent Checkbox */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id={`agent-${data.label}`}
            checked={data.useAgent || false}
            onChange={handleAgentToggle}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor={`agent-${data.label}`} className="ml-2 text-xs font-medium text-gray-700">
            에이전트 툴 사용
          </label>
        </div>

        {/* MCP Modules Dropdown */}
        <div className="relative">
          <label className="block text-xs font-medium text-gray-700 mb-1">
            MCP 모듈
          </label>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-full flex items-center justify-between px-3 py-2 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <span className="text-gray-700">
              {(data.mcpModules?.length || 0) > 0 
                ? `${data.mcpModules?.length}개 선택됨`
                : '모듈 선택'}
            </span>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${
              isDropdownOpen ? 'rotate-180' : ''
            }`} />
          </button>
          
          {isDropdownOpen && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-48 overflow-y-auto">
              {availableModules.map((module) => (
                <div key={module.id} className="flex items-center px-3 py-2 hover:bg-gray-50">
                  <input
                    type="checkbox"
                    id={`module-${module.id}-${data.label}`}
                    checked={data.mcpModules?.includes(module.id) || false}
                    onChange={() => handleModuleToggle(module.id)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label 
                    htmlFor={`module-${module.id}-${data.label}`}
                    className="ml-2 text-xs text-gray-700 cursor-pointer flex-1"
                  >
                    {module.label}
                  </label>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected modules display */}
        {(data.mcpModules?.length || 0) > 0 && (
          <div className="flex flex-wrap gap-1">
            {data.mcpModules?.map((moduleId) => {
              const module = availableModules.find(m => m.id === moduleId);
              return module ? (
                <span
                  key={moduleId}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                >
                  {module.label}
                </span>
              ) : null;
            })}
          </div>
        )}
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-blue-500 border-2 border-white"
      />
    </div>
  );
}

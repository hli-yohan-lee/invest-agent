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
      return 'bg-gray-400';
  }
};

export default function TaskNode({ data, selected, onDataChange }: TaskNodeProps) {
  const Icon = getTaskIcon(data.type || 'general');
  const colorClass = getTaskColor(data.type || 'general');
  const statusColor = getStatusColor(data.status);

  const handlePromptChange = (newPrompt: string) => {
    if (onDataChange) {
      onDataChange({ ...data, prompt: newPrompt });
    }
  };

  return (
    <div className={`shadow-lg rounded-lg ${colorClass} border-2 min-w-[300px] max-w-[350px] ${
      selected ? 'border-blue-400' : ''
    }`}>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      
      {/* 헤더 */}
      <div className="flex items-center justify-between p-3 bg-white rounded-t-lg border-b">
        <div className="flex items-center gap-2">
          <Icon className="w-5 h-5 text-gray-700" />
          <span className="font-semibold text-gray-900">{data.label}</span>
        </div>
        <div className={`w-2 h-2 rounded-full ${statusColor}`}></div>
      </div>

      {/* 내용 */}
      <div className="p-4">
        {/* 작업 설명 입력 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            작업 설명
          </label>
          <textarea
            value={data.prompt || ''}
            onChange={(e) => handlePromptChange(e.target.value)}
            placeholder="이 작업에서 수행할 내용을 입력하세요..."
            className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={4}
          />
        </div>
      </div>

      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  );
}

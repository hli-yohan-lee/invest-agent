import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { CheckCircle, AlertCircle, FileText, BarChart3 } from 'lucide-react';

interface ResultNodeData {
  label: string;
  type?: 'report' | 'chart' | 'data' | 'analysis';
  status?: 'success' | 'warning' | 'error' | 'pending';
}

interface ResultNodeProps {
  data: ResultNodeData;
  selected?: boolean;
}

const getResultIcon = (type?: string) => {
  switch (type) {
    case 'report':
      return FileText;
    case 'chart':
      return BarChart3;
    case 'analysis':
      return CheckCircle;
    default:
      return CheckCircle;
  }
};

const getResultColor = (status?: string) => {
  switch (status) {
    case 'success':
      return 'from-green-400 to-green-500 border-green-300';
    case 'warning':
      return 'from-yellow-400 to-yellow-500 border-yellow-300';
    case 'error':
      return 'from-red-400 to-red-500 border-red-300';
    case 'pending':
      return 'from-gray-400 to-gray-500 border-gray-300';
    default:
      return 'from-emerald-400 to-emerald-500 border-emerald-300';
  }
};

const getStatusIcon = (status?: string) => {
  switch (status) {
    case 'warning':
      return AlertCircle;
    case 'error':
      return AlertCircle;
    default:
      return CheckCircle;
  }
};

export default function ResultNode({ data, selected }: ResultNodeProps) {
  const Icon = getResultIcon(data.type);
  const StatusIcon = getStatusIcon(data.status);
  const colorClass = getResultColor(data.status);

  return (
    <div className={`px-4 py-3 shadow-lg rounded-lg bg-gradient-to-r ${colorClass} border-2 min-w-[180px] ${
      selected ? 'border-opacity-100' : 'border-opacity-50'
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-white border-2 border-current"
      />
      
      <div className="flex items-center space-x-2">
        <div className="flex items-center justify-center w-8 h-8 bg-white rounded-full">
          <Icon className="w-4 h-4 text-current" />
        </div>
        <div className="flex-1">
          <div className="text-white font-medium text-sm">{data.label}</div>
          <div className="text-white text-opacity-80 text-xs">
            <span className="ml-1 capitalize">{data.type || 'general'} 결과</span>
          </div>
        </div>
        {data.status && (
          <StatusIcon className="w-4 h-4 text-white" />
        )}
      </div>
    </div>
  );
}

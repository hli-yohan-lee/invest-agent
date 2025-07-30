import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Play } from 'lucide-react';

interface StartNodeData {
  label: string;
}

interface StartNodeProps {
  data: StartNodeData;
  selected?: boolean;
}

export default function StartNode({ data, selected }: StartNodeProps) {
  return (
    <div className={`px-4 py-3 shadow-lg rounded-lg bg-gradient-to-r from-green-400 to-green-500 border-2 min-w-[180px] ${
      selected ? 'border-green-600' : 'border-green-300'
    }`}>
      <div className="flex items-center space-x-2">
        <div className="flex items-center justify-center w-8 h-8 bg-white rounded-full">
          <Play className="w-4 h-4 text-green-500" fill="currentColor" />
        </div>
        <div>
          <div className="text-white font-medium text-sm">시작</div>
          <div className="text-green-100 text-xs">{data.label}</div>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-white border-2 border-green-500"
      />
    </div>
  );
}

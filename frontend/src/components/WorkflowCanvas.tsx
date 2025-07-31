'use client'

import React, { useCallback, useEffect } from 'react'
import { 
  ReactFlow, 
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  useReactFlow,
  ReactFlowProvider
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useAppStore } from '@/lib/store'
import StartNode from './nodes/StartNode'
import TaskNode from './nodes/TaskNode' 
import ResultNode from './nodes/ResultNode'

// NodeTypes에 대한 context provider 생성
const NodeDataContext = React.createContext<{
  updateNodeData: (nodeId: string, newData: any) => void;
}>({
  updateNodeData: () => {},
});

// TaskNode wrapper with context
const TaskNodeWrapper = (props: any) => {
  const { updateNodeData } = React.useContext(NodeDataContext);
  
  const handleDataChange = (newData: any) => {
    updateNodeData(props.id, newData);
  };
  
  return <TaskNode {...props} onDataChange={handleDataChange} />;
};

const nodeTypes = {
  start: StartNode,
  task: TaskNodeWrapper,
  result: ResultNode,
}

const initialNodes: Node[] = [
  {
    id: 'start',
    type: 'start',
    position: { x: 100, y: 100 },
    data: { label: '투자 분석 시작' },
  },
  {
    id: 'task-1',
    type: 'task',
    position: { x: 350, y: 50 },
    data: { 
      label: '데이터 수집',
      type: 'data',
      prompt: '한국 주식 시장의 PER, PBR, ROE 데이터를 수집하고 최신 재무제표 정보를 가져와 주세요.',
      useAgent: true,
      mcpModules: ['naver-securities', 'toss-securities', 'korea-exchange']
    },
  },
  {
    id: 'task-2', 
    type: 'task',
    position: { x: 350, y: 250 },
    data: {
      label: '데이터 분석',
      type: 'analysis',
      prompt: '수집된 재무 데이터를 분석하여 PER 15 이하, ROE 10% 이상인 기업들을 필터링하고 상위 20개 종목을 선별해 주세요.',
      useAgent: true,
      mcpModules: ['financial-analysis', 'market-data']
    },
  },
  {
    id: 'result',
    type: 'result',
    position: { x: 700, y: 150 },
    data: { 
      label: '분석 결과',
      type: 'report',
      status: 'success'
    },
  },
]

const initialEdges: Edge[] = [
  { id: 'e1', source: 'start', target: 'task-1', type: 'default' },
  { id: 'e2', source: 'task-1', target: 'task-2', type: 'default' },
  { id: 'e3', source: 'task-2', target: 'result', type: 'default' },
]

function WorkflowCanvasContent() {
  // store에서 nodes와 edges 가져오기
  const { 
    nodes: storeNodes, 
    edges: storeEdges, 
    executionStatus, 
    setExecutionStatus, 
    setCurrentTab,
    updateNode,
    addEdge: addStoreEdge,
    deleteEdge,
    workflowGenerating  // 워크플로우 생성 중 상태 추가
  } = useAppStore()
  
  // store 상태를 React Flow 상태와 동기화
  const [nodes, setNodes, onNodesChange] = useNodesState(storeNodes.length > 0 ? storeNodes as any : initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges.length > 0 ? storeEdges as any : initialEdges)
  
  // React Flow 인스턴스 가져오기
  const reactFlowInstance = useReactFlow()
  
  // 노드가 업데이트될 때 뷰 맞추기
  useEffect(() => {
    if (storeNodes.length > 0) {
      setTimeout(() => {
        console.log('Fitting view to new nodes...')
        reactFlowInstance.fitView({ padding: 50 })
      }, 100)
    }
  }, [storeNodes, reactFlowInstance])
  
  // store 상태가 변경될 때 React Flow 상태 업데이트
  useEffect(() => {
    console.log('Store nodes changed:', storeNodes.length, storeNodes)
    if (storeNodes.length > 0) {
      console.log('Updating React Flow nodes...')
      setNodes(storeNodes as any)
    } else {
      console.log('No store nodes, using initial nodes')
      setNodes(initialNodes)
    }
  }, [storeNodes, setNodes])
  
  useEffect(() => {
    console.log('Store edges changed:', storeEdges.length, storeEdges) 
    if (storeEdges.length > 0) {
      console.log('Updating React Flow edges...')
      setEdges(storeEdges as any)
    } else {
      console.log('No store edges, using initial edges')
      setEdges(initialEdges)
    }
  }, [storeEdges, setEdges])

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge = {
        id: `edge-${Date.now()}`,
        source: params.source!,
        target: params.target!,
        type: 'default' as const
      }
      setEdges((eds) => addEdge(params, eds))
      addStoreEdge(newEdge)
    },
    [setEdges, addStoreEdge]
  )

  const handleNodeDataChange = useCallback((nodeId: string, newData: any) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: newData } : node
      )
    )
    // store도 업데이트
    updateNode(nodeId, { data: newData })
  }, [setNodes, updateNode])

  const handleExecute = useCallback(() => {
    setExecutionStatus('running')
    
    // 실행 시뮬레이션
    setTimeout(() => {
      setExecutionStatus('completed')
      setCurrentTab('result')
    }, 3000)
  }, [setExecutionStatus, setCurrentTab])

  const contextValue = {
    updateNodeData: handleNodeDataChange,
  };

  return (
    <NodeDataContext.Provider value={contextValue}>
      <div className="flex-1 bg-gray-50">
      {/* 툴바 */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">워크플로우 편집기</h2>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                executionStatus === 'idle' ? 'bg-gray-400' :
                executionStatus === 'running' ? 'bg-yellow-400' :
                executionStatus === 'completed' ? 'bg-green-400' :
                'bg-red-400'
              }`}></div>
              <span className="text-sm text-gray-600">
                {executionStatus === 'idle' ? '대기중' :
                 executionStatus === 'running' ? '실행중' :
                 executionStatus === 'completed' ? '완료' :
                 '오류'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleExecute}
              disabled={executionStatus === 'running'}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {executionStatus === 'running' ? '실행중...' : '워크플로우 실행'}
            </button>
          </div>
        </div>
      </div>

      {/* React Flow */}
      <div className="h-[calc(100vh-200px)] relative">
        {/* 워크플로우 생성 중 로딩 오버레이 */}
        {workflowGenerating && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-8 flex flex-col items-center space-y-4">
              <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
              <div className="text-lg font-medium text-gray-900">워크플로우 생성 중</div>
              <div className="text-sm text-gray-500">플래닝 결과를 워크플로우로 변환하고 있습니다...</div>
            </div>
          </div>
        )}
        
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-50"
        >
          <Background />
          <Controls />
          <MiniMap className="bg-white" />
        </ReactFlow>
      </div>
    </div>
    </NodeDataContext.Provider>
  )
}

export default function WorkflowCanvas() {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasContent />
    </ReactFlowProvider>
  )
}

import { create } from 'zustand'

export interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    planId?: string
    executionId?: string
  }
}

export interface Plan {
  id: string
  title: string
  description: string
  steps: PlanStep[]
  status: 'draft' | 'approved' | 'executing' | 'completed'
  createdAt: Date
  updatedAt: Date
}

export interface PlanStep {
  id: string
  title: string
  description: string
  order: number
  mcpModules: string[]
  parameters: Record<string, any>
}

export interface Node {
  id: string
  type: 'start' | 'task' | 'result'
  position: { x: number; y: number }
  data: {
    label: string
    prompt?: string
    useAgentTool?: boolean
    selectedModules?: string[]
    outputFormat?: 'table' | 'report'
    parameters?: Record<string, any>
  }
}

export interface Edge {
  id: string
  source: string
  target: string
  type: 'default'
}

export interface Result {
  id: string
  workflowId: string
  type: 'table' | 'report'
  data: any
  metadata: {
    executionTime: number
    timestamp: Date
    modules: string[]
  }
  editable: boolean
}

export interface MCPModule {
  id: string
  name: string
  description: string
  version: string
  category: 'data' | 'analysis' | 'report'
  parameters: MCPParameter[]
  status: 'online' | 'offline'
}

export interface MCPParameter {
  name: string
  type: 'string' | 'number' | 'boolean' | 'select'
  required: boolean
  description: string
  options?: string[]
  defaultValue?: any
}

interface AppState {
  // 전역 상태
  currentTab: 'planning' | 'workflow' | 'result'
  isLoading: boolean
  error: string | null
  
  // 플래닝 상태
  chatHistory: Message[]
  currentPlan: Plan | null
  
  // 워크플로우 상태
  nodes: Node[]
  edges: Edge[]
  selectedNode: string | null
  executionStatus: 'idle' | 'running' | 'completed' | 'error'
  
  // 결과 상태
  results: Result[]
  currentResult: Result | null
  viewMode: 'table' | 'report'
  
  // MCP 상태
  availableModules: MCPModule[]
  moduleStatus: Record<string, 'online' | 'offline'>
  
  // 액션들
  setCurrentTab: (tab: 'planning' | 'workflow' | 'result') => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  
  // 플래닝 액션
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  updatePlan: (plan: Plan) => void
  clearChatHistory: () => void
  
  // 워크플로우 액션
  addNode: (node: Node) => void
  updateNode: (id: string, updates: Partial<Node>) => void
  deleteNode: (id: string) => void
  addEdge: (edge: Edge) => void
  deleteEdge: (id: string) => void
  setSelectedNode: (nodeId: string | null) => void
  setExecutionStatus: (status: 'idle' | 'running' | 'completed' | 'error') => void
  
  // 결과 액션
  addResult: (result: Result) => void
  setCurrentResult: (result: Result | null) => void
  setViewMode: (mode: 'table' | 'report') => void
  
  // MCP 액션
  setAvailableModules: (modules: MCPModule[]) => void
  updateModuleStatus: (moduleId: string, status: 'online' | 'offline') => void
}

export const useAppStore = create<AppState>((set, get) => ({
  // 초기 상태
  currentTab: 'planning',
  isLoading: false,
  error: null,
  
  chatHistory: [],
  currentPlan: null,
  
  nodes: [],
  edges: [],
  selectedNode: null,
  executionStatus: 'idle',
  
  results: [],
  currentResult: null,
  viewMode: 'table',
  
  availableModules: [],
  moduleStatus: {},
  
  // 전역 액션
  setCurrentTab: (tab) => set({ currentTab: tab }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  
  // 플래닝 액션
  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    }
    set((state) => ({
      chatHistory: [...state.chatHistory, newMessage]
    }))
  },
  
  updatePlan: (plan) => set({ currentPlan: plan }),
  clearChatHistory: () => set({ chatHistory: [], currentPlan: null }),
  
  // 워크플로우 액션
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),
  
  updateNode: (id, updates) => set((state) => ({
    nodes: state.nodes.map(node => 
      node.id === id ? { ...node, ...updates } : node
    )
  })),
  
  deleteNode: (id) => set((state) => ({
    nodes: state.nodes.filter(node => node.id !== id),
    edges: state.edges.filter(edge => edge.source !== id && edge.target !== id)
  })),
  
  addEdge: (edge) => set((state) => ({
    edges: [...state.edges, edge]
  })),
  
  deleteEdge: (id) => set((state) => ({
    edges: state.edges.filter(edge => edge.id !== id)
  })),
  
  setSelectedNode: (nodeId) => set({ selectedNode: nodeId }),
  setExecutionStatus: (status) => set({ executionStatus: status }),
  
  // 결과 액션
  addResult: (result) => set((state) => ({
    results: [...state.results, result]
  })),
  
  setCurrentResult: (result) => set({ currentResult: result }),
  setViewMode: (mode) => set({ viewMode: mode }),
  
  // MCP 액션
  setAvailableModules: (modules) => set({ availableModules: modules }),
  updateModuleStatus: (moduleId, status) => set((state) => ({
    moduleStatus: { ...state.moduleStatus, [moduleId]: status }
  })),
}))

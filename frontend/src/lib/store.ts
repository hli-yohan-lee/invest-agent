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
  workflowGenerating: boolean  // 워크플로우 생성 중 상태
  
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
  updateMessage: (id: string, content: string) => void
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
  setWorkflowGenerating: (generating: boolean) => void
  
  // 결과 액션
  addResult: (result: Result) => void
  setCurrentResult: (result: Result | null) => void
  setViewMode: (mode: 'table' | 'report') => void
  
  // MCP 액션
  setAvailableModules: (modules: MCPModule[]) => void
  updateModuleStatus: (moduleId: string, status: 'online' | 'offline') => void
  
  // 워크플로우 생성 액션
  generateWorkflowFromPlanning: () => void
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
  workflowGenerating: false,
  
  results: [],
  currentResult: null,
  viewMode: 'table',
  
  availableModules: [],
  moduleStatus: {},
  
  // 전역 액션
  setCurrentTab: (tab) => {
    console.log('setCurrentTab called with:', tab)
    console.log('Previous tab:', get().currentTab)
    set({ currentTab: tab })
    console.log('New tab set to:', tab)
  },
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
  
  updateMessage: (id, content) => set((state) => ({
    chatHistory: state.chatHistory.map(message => 
      message.id === id ? { ...message, content } : message
    )
  })),
  
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
  setWorkflowGenerating: (generating) => set({ workflowGenerating: generating }),
  
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
    // 플래닝 결과를 워크플로우로 변환
  generateWorkflowFromPlanning: async () => {
    console.log('generateWorkflowFromPlanning called!')
    
    // 로딩 시작
    set({ workflowGenerating: true })
    
    const state = get()
    console.log('Current chat history length:', state.chatHistory.length)
    
    try {
      // OpenAI API 키 확인
      const openaiApiKey = localStorage.getItem('openai_api_key')
      if (!openaiApiKey) {
        console.log('No OpenAI API key found!')
        set({ workflowGenerating: false, error: 'OpenAI API 키가 설정되지 않았습니다.' })
        return
      }

      console.log('OpenAI API key found:', openaiApiKey.substring(0, 10) + '...')

      // 기존 대화 내용 수집
      const chatHistoryText = state.chatHistory
        .map(msg => `${msg.type === 'user' ? '사용자' : 'AI'}: ${msg.content}`)
        .join('\n\n')

      console.log('Sending workflow conversion request...')

      // 워크플로우 변환 API 호출
      const response = await fetch('http://localhost:8000/api/planning/chat-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: "위 대화 내용을 워크플로우로 변환해주세요",
          openai_api_key: openaiApiKey,
          mode: 'workflow',
          chat_history: chatHistoryText
        })
      })

      if (!response.ok) {
        throw new Error('서버 응답 오류')
      }

      // 스트리밍 응답 처리
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullResponse = ''
      
      if (reader) {
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
                    fullResponse += data.content
                  } else if (data.type === 'done' && data.full_response) {
                    fullResponse = data.full_response
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

      console.log('Received workflow response:', fullResponse)

      // 워크플로우 데이터 파싱
      let workflowData: any = null
      
      if (fullResponse) {
        // JSON 블록에서 데이터 추출 시도
        const jsonMatch = fullResponse.match(/```json\s*([\s\S]*?)\s*```/)
        if (jsonMatch) {
          console.log('Found JSON block, parsing...')
          try {
            workflowData = JSON.parse(jsonMatch[1])
            console.log('Parsed workflow data:', workflowData)
          } catch (jsonParseError) {
            console.log('JSON parsing failed:', jsonParseError)
            // 전체 응답을 JSON으로 파싱 시도
            try {
              workflowData = JSON.parse(fullResponse)
            } catch (fullParseError) {
              console.log('Full response JSON parsing failed:', fullParseError)
            }
          }
        } else {
          // JSON 블록이 없으면 전체 응답을 JSON으로 파싱 시도
          try {
            workflowData = JSON.parse(fullResponse)
          } catch (parseError) {
            console.log('Direct JSON parsing failed:', parseError)
          }
        }
      }
      
      if (!workflowData || !workflowData.tasks) {
        console.log('No valid workflow data found! Creating default workflow...')
        // 마지막 어시스턴트 메시지에서 워크플로우 생성 시도
        const lastAssistantMessage = state.chatHistory
          .filter(msg => msg.type === 'assistant')
          .pop()
        
        if (lastAssistantMessage) {
          const content = lastAssistantMessage.content
          // 기본 워크플로우 생성 (기존 로직)
          workflowData = {
            workflow_title: "투자 분석 워크플로우",
            tasks: [
              {
                id: "analysis_task",
                title: "투자 분석",
                description: content.substring(0, 200) + "...",
                agent_allowed: ["financial_analyst"],
                mcp_tools: ["stock_data_fetcher", "financial_analyzer"],
                output_type: "report"
              }
            ]
          }
        } else {
          // 기본 워크플로우
          workflowData = {
            workflow_title: "투자 분석 워크플로우",
            tasks: [
              {
                id: "analysis_task",
                title: "투자 분석",
                description: "투자 대상에 대한 종합적인 분석을 수행합니다",
                agent_allowed: ["financial_analyst"],
                mcp_tools: ["stock_data_fetcher", "financial_analyzer"],
                output_type: "report"
              }
            ]
          }
        }
      }
      
      console.log('Final workflow data:', workflowData)
      
      // 기존 노드와 엣지 클리어
      set({ nodes: [], edges: [] })
      
      // 새로운 노드들 생성 (기존 로직과 동일)
      const newNodes: Node[] = []
      const newEdges: Edge[] = []
      
      // 시작 노드
      newNodes.push({
        id: 'start',
        type: 'start',
        position: { x: 100, y: 200 },
        data: { 
          label: workflowData.workflow_title || '워크플로우 시작' 
        }
      })
      
      // 작업 노드들
      const tasks = workflowData.tasks || []
      tasks.forEach((task: any, index: number) => {
        const nodeId = task.id || `task-${index + 1}`
        const prevNodeId = index === 0 ? 'start' : (tasks[index - 1]?.id || `task-${index}`)
        
        // 노드 생성
        newNodes.push({
          id: nodeId,
          type: 'task',
          position: { 
            x: 350 + (index * 250), 
            y: 100 + (index % 2) * 200 
          },
          data: {
            label: task.title || `작업 ${index + 1}`,
            prompt: task.description || '',
            useAgentTool: task.agent_allowed && task.agent_allowed.length > 0,
            selectedModules: task.mcp_tools || [],
            outputFormat: task.output_type || 'table',
            parameters: {
              estimatedTime: task.estimated_time,
              agents: task.agent_allowed || []
            }
          }
        })
        
        // 엣지 생성 (이전 노드와 연결)
        newEdges.push({
          id: `edge-${index}`,
          source: prevNodeId,
          target: nodeId,
          type: 'default'
        })
      })
      
      // 결과 노드
      if (tasks.length > 0) {
        const lastTaskId = tasks[tasks.length - 1]?.id || `task-${tasks.length}`
        newNodes.push({
          id: 'result',
          type: 'result',
          position: { 
            x: 350 + (tasks.length * 250), 
            y: 200 
          },
          data: {
            label: workflowData.expected_outcome || '분석 결과',
            outputFormat: 'report'
          }
        })
        
        // 마지막 작업과 결과 노드 연결
        newEdges.push({
          id: `edge-final`,
          source: lastTaskId,
          target: 'result',
          type: 'default'
        })
      }
      
      // 상태 업데이트
      console.log('Setting new nodes and edges')
      console.log('New nodes:', newNodes.length, newNodes)
      console.log('New edges:', newEdges.length, newEdges)
      
      set({ 
        nodes: newNodes, 
        edges: newEdges,
        workflowGenerating: false // 로딩 종료
      })
      
      console.log('Workflow generation completed!')
      
    } catch (error) {
      console.error('워크플로우 생성 중 오류:', error)
      
      // 오류 발생 시 기본 워크플로우 생성
      const lastAssistantMessage = state.chatHistory
        .filter(msg => msg.type === 'assistant')
        .pop()
      
      const defaultWorkflow = {
        workflow_title: "투자 분석 워크플로우",
        tasks: [
          {
            id: "analysis_task",
            title: "투자 분석",
            description: lastAssistantMessage ? 
              lastAssistantMessage.content.substring(0, 200) + "..." : 
              "투자 대상에 대한 종합적인 분석을 수행합니다",
            agent_allowed: ["financial_analyst"],
            mcp_tools: ["stock_data_fetcher", "financial_analyzer"],
            output_type: "report"
          }
        ]
      }
      
      // 기본 워크플로우로 노드 생성
      const newNodes: Node[] = [
        {
          id: 'start',
          type: 'start',
          position: { x: 100, y: 200 },
          data: { label: defaultWorkflow.workflow_title }
        },
        {
          id: 'analysis_task',
          type: 'task',
          position: { x: 350, y: 100 },
          data: {
            label: defaultWorkflow.tasks[0].title,
            prompt: defaultWorkflow.tasks[0].description,
            useAgentTool: true,
            selectedModules: defaultWorkflow.tasks[0].mcp_tools,
            outputFormat: defaultWorkflow.tasks[0].output_type as 'table' | 'report'
          }
        },
        {
          id: 'result',
          type: 'result',
          position: { x: 600, y: 200 },
          data: { label: '분석 결과', outputFormat: 'report' }
        }
      ]
      
      const newEdges: Edge[] = [
        { id: 'edge-0', source: 'start', target: 'analysis_task', type: 'default' },
        { id: 'edge-final', source: 'analysis_task', target: 'result', type: 'default' }
      ]
      
      set({ 
        nodes: newNodes, 
        edges: newEdges,
        workflowGenerating: false, // 로딩 종료
        error: '워크플로우 생성에 실패했습니다. 기본 워크플로우를 생성했습니다.' 
      })
    }
  },
}))

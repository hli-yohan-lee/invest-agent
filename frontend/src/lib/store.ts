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
    type?: 'analysis' | 'data' | 'report' | 'general'
    status?: 'pending' | 'running' | 'completed' | 'error'
    result?: any
    error?: string
    tool_used?: string
    parameters_used?: Record<string, any>
    raw_data?: any
    mcp_result?: any
    analysis_result?: any
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

export interface MCPTool {
  name: string
  description: string
  inputSchema: any
}

export interface Report {
  id: string
  title: string
  content: string
  type: 'investment_analysis' | 'stock_analysis' | 'market_analysis'
  status: 'generating' | 'completed' | 'error'
  generatedAt: Date
  metadata: {
    workflowId?: string
    stocksAnalyzed?: number
    executionTime?: number
    dataSource?: string[]
  }
  sections: ReportSection[]
}

export interface ReportSection {
  id: string
  title: string
  content: string
  type: 'summary' | 'analysis' | 'table' | 'chart' | 'recommendation'
  order: number
}

interface AppState {
  // 전역 상태
  currentTab: 'planning' | 'workflow' | 'result' | 'report'
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
  availableTools: MCPTool[]
  
  // 보고서 상태
  reports: Report[]
  currentReport: Report | null
  reportGenerating: boolean
  
  // 액션들
  setCurrentTab: (tab: 'planning' | 'workflow' | 'result' | 'report') => void
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
  setAvailableTools: (tools: MCPTool[]) => void
  getAvailableMCPTools: () => Promise<void>
  
  // 보고서 액션
  addReport: (report: Report) => void
  setCurrentReport: (report: Report | null) => void
  setReportGenerating: (generating: boolean) => void
  generateReport: (workflowResults: any[]) => Promise<void>
  
  // 워크플로우 실행 액션
  executeWorkflowNode: (nodeId: string, toolName?: string, params?: Record<string, any>) => Promise<void>
  executeEntireWorkflow: () => Promise<void>
  
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
  availableTools: [],
  
  reports: [],
  currentReport: null,
  reportGenerating: false,
  
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
  setAvailableTools: (tools) => set({ availableTools: tools }),
  
  // MCP 도구 목록 조회
  getAvailableMCPTools: async () => {
    try {
      const response = await fetch('http://localhost:8000/api/mcp/tools')
      if (response.ok) {
        const tools = await response.json()
        set({ availableTools: tools })
        console.log('Available MCP tools:', tools)
      }
    } catch (error) {
      console.error('Failed to get MCP tools:', error)
    }
  },
  
  // 워크플로우 노드 실행 - 동적 도구 선택
  executeWorkflowNode: async (nodeId: string, toolName?: string, params?: Record<string, any>) => {
    console.log(`Executing node ${nodeId}`)
    
    const state = get()
    const node = state.nodes.find(n => n.id === nodeId)
    
    if (!node) {
      console.error(`Node ${nodeId} not found`)
      return
    }

    try {
      // 노드 상태를 실행 중으로 변경
      set((state) => ({
        nodes: state.nodes.map(node => 
          node.id === nodeId 
            ? { ...node, data: { ...node.data, status: 'running' } }
            : node
        )
      }))

      // OpenAI API 키 확인
      const openaiApiKey = localStorage.getItem('openai_api_key')
      if (!openaiApiKey) {
        throw new Error('OpenAI API 키가 설정되지 않았습니다.')
      }

      // 1단계: AI가 현재 노드에 적합한 MCP 도구를 선택하도록 요청
      console.log(`Step 1: Selecting appropriate tool for node: ${node.data.label}`)
      
      const toolSelectionResponse = await fetch('http://localhost:8000/api/workflow/select-tool', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          node_description: node.data.label,
          node_prompt: node.data.prompt || '',
          workflow_context: state.nodes.map(n => ({ id: n.id, label: n.data.label, status: n.data.status })),
          openai_api_key: openaiApiKey
        })
      })

      console.log('Tool selection response status:', toolSelectionResponse.status)
      if (!toolSelectionResponse.ok) {
        const errorText = await toolSelectionResponse.text()
        console.error('Tool selection API error:', errorText)
        throw new Error(`도구 선택 API 호출 실패: ${toolSelectionResponse.status} - ${errorText}`)
      }

      const toolSelection = await toolSelectionResponse.json()
      console.log('Selected tool:', toolSelection)

      // 2단계: 선택된 도구로 실제 작업 실행
      const selectedTool = toolSelection.tool_name
      const selectedParams = toolSelection.parameters

      console.log(`Step 2: Executing selected tool: ${selectedTool} with params:`, selectedParams)

      const mcpResponse = await fetch('http://localhost:8000/api/mcp/call-tool', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_name: selectedTool,
          parameters: selectedParams
        })
      })

      console.log('MCP response status:', mcpResponse.status)
      if (!mcpResponse.ok) {
        const errorText = await mcpResponse.text()
        console.error('MCP tool error:', errorText)
        throw new Error(`MCP 도구 실행 실패: ${mcpResponse.status} - ${errorText}`)
      }

      const mcpResult = await mcpResponse.json()
      console.log('MCP tool result:', mcpResult)
      
      // MCP 결과를 상세히 출력
      console.log('=== MCP 호출 결과 상세 ===')
      console.log('도구명:', selectedTool)
      console.log('매개변수:', selectedParams)
      console.log('결과 타입:', typeof mcpResult)
      console.log('결과 구조:', Object.keys(mcpResult))
      console.log('전체 결과:', JSON.stringify(mcpResult, null, 2))
      console.log('========================')

      // 3단계: AI가 결과를 분석하고 해석
      console.log('Step 3: Analyzing results with AI')
      
      const analysisResponse = await fetch('http://localhost:8000/api/workflow/analyze-result', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          node_description: node.data.label,
          tool_used: selectedTool,
          raw_result: mcpResult,
          openai_api_key: openaiApiKey
        })
      })

      console.log('Analysis response status:', analysisResponse.status)
      if (!analysisResponse.ok) {
        const errorText = await analysisResponse.text()
        console.error('Analysis API error:', errorText)
        throw new Error(`결과 분석 API 호출 실패: ${analysisResponse.status} - ${errorText}`)
      }

      const analysisResult = await analysisResponse.json()
      console.log('Analysis result:', analysisResult)
      
      // 분석 결과를 상세히 출력
      console.log('=== AI 분석 결과 상세 ===')
      console.log('분석 내용:', analysisResult.analysis)
      console.log('사용된 도구:', analysisResult.tool_used)
      console.log('데이터 요약:', analysisResult.data_summary)
      console.log('========================')

      // 노드 상태를 완료로 변경하고 결과 저장
      set((state) => ({
        nodes: state.nodes.map(node => 
          node.id === nodeId 
            ? { 
                ...node, 
                data: { 
                  ...node.data, 
                  status: 'completed',
                  result: analysisResult.analysis,
                  tool_used: selectedTool,
                  parameters_used: selectedParams,
                  raw_data: mcpResult,
                  // MCP 결과도 함께 저장
                  mcp_result: mcpResult,
                  analysis_result: analysisResult
                } 
              }
            : node
        )
      }))

      console.log(`Node ${nodeId} execution completed successfully`)

    } catch (error) {
      console.error(`Error executing node ${nodeId}:`, error)
      
      // 노드 상태를 에러로 변경
      set((state) => ({
        nodes: state.nodes.map(node => 
          node.id === nodeId 
            ? { 
                ...node, 
                data: { 
                  ...node.data, 
                  status: 'error',
                  error: error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'
                } 
              }
            : node
        )
      }))
    }
  },

  // 자동 워크플로우 실행
  executeEntireWorkflow: async () => {
    console.log('Executing entire workflow...')
    
    try {
      set({ executionStatus: 'running' })
      
      // 시작 노드를 제외한 실행 가능한 노드들을 순서대로 실행
      const initialState = get()
      const executableNodes = initialState.nodes.filter(node => 
        node.type !== 'start' && node.data.status !== 'completed'
      )
      
      console.log('Executable nodes:', executableNodes.map(n => n.id))
      
      // 기본 실행 매개변수 설정
      for (const node of executableNodes) {
        console.log(`Processing node: ${node.id} (${node.data.type})`)
        
        // 결과 노드인 경우 특별 처리
        if (node.type === 'result') {
          // 최신 상태에서 이전 노드들의 결과를 종합해서 최종 결과 생성
          const currentState = get()
          const taskNodes = currentState.nodes.filter(n => n.type === 'task' && n.data.status === 'completed')
          const summaryResults = taskNodes.map(n => ({
            title: n.data.label,
            result: n.data.result
          }))
          
          console.log(`Completed task nodes: ${taskNodes.length}`)
          
          // 결과 노드 업데이트
          set((state) => ({
            nodes: state.nodes.map(n => 
              n.id === node.id 
                ? { 
                    ...n, 
                    data: { 
                      ...n.data, 
                      status: 'completed',
                      result: {
                        summary: `총 ${taskNodes.length}개의 작업이 완료되었습니다.`,
                        details: summaryResults,
                        completedAt: new Date().toISOString()
                      }
                    } 
                  }
                : n
            )
          }))
        } else {
          // 일반 노드 실행 (자동 도구 선택)
          console.log(`Executing node ${node.id}...`)
          await get().executeWorkflowNode(node.id)
          console.log(`Node ${node.id} execution completed`)
        }
        
        // 노드 간 실행 간격
        await new Promise(resolve => setTimeout(resolve, 500))
      }
      
      set({ executionStatus: 'completed' })
      console.log('Entire workflow execution completed!')
      
      // 최신 상태 다시 가져오기 (노드 실행 후 업데이트된 상태)
      const updatedState = get()
      
      // 워크플로우 완료 후 결과 생성 및 결과 탭으로 이동
      const resultNode = updatedState.nodes.find(node => node.type === 'result')
      if (resultNode && resultNode.data.result) {
        const newResult: Result = {
          id: Math.random().toString(36).substr(2, 9),
          workflowId: 'workflow-' + Date.now(),
          type: 'report',
          data: {
            summary: '워크플로우 실행 완료',
            results: updatedState.nodes.filter(node => node.type === 'task').map(node => ({
              nodeId: node.id,
              title: node.data.label,
              status: node.data.status,
              result: node.data.result,
              tool_used: node.data.tool_used,
              parameters_used: node.data.parameters_used
            })),
            finalResult: resultNode.data.result
          },
          metadata: {
            executionTime: Date.now(),
            timestamp: new Date(),
            modules: updatedState.nodes.filter(node => node.data.tool_used).map(node => node.data.tool_used || '')
          },
          editable: false
        }
        
        // 결과 추가 및 결과 탭으로 이동
        set((state) => ({
          results: [...state.results, newResult],
          currentResult: newResult,
          currentTab: 'result' // 모든 실행 완료 후에만 결과 탭으로 이동
        }))
        
        console.log('All tasks completed! Moved to result tab with final results')
      } else {
        // 결과 노드가 없거나 결과가 없어도 모든 작업 완료 후 결과 탭으로 이동
        set({ currentTab: 'result' })
        console.log('All tasks completed! Moved to result tab')
      }
      
    } catch (error) {
      console.error('Workflow execution failed:', error)
      set({ 
        executionStatus: 'error',
        currentTab: 'result', // 오류 시에도 결과 탭으로 이동 (오류 확인용)
        error: error instanceof Error ? error.message : String(error)
      })
    }
  },
  
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
                task_type: "analysis"
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
                task_type: "analysis"
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
            type: task.task_type || 'general',
            status: 'pending'
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
            type: 'report',
            status: 'pending'
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
      
      // 워크플로우 생성 완료 후 탭 변경 (약간의 지연을 두어 렌더링 완료 보장)
      setTimeout(() => {
        set({ currentTab: 'workflow' })
      }, 100)
      
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
            task_type: "analysis"
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
            type: 'analysis',
            status: 'pending'
          }
        },
        {
          id: 'result',
          type: 'result',
          position: { x: 600, y: 200 },
          data: { 
            label: '분석 결과', 
            type: 'report',
            status: 'pending'
          }
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
      
      // 워크플로우 생성 완료 후 탭 변경 (약간의 지연을 두어 렌더링 완료 보장)
      setTimeout(() => {
        set({ currentTab: 'workflow' })
      }, 100)
    }
  },
  
  // 보고서 액션
  addReport: (report) => {
    set(state => ({
      reports: [...state.reports, report]
    }))
  },
  
  setCurrentReport: (report) => {
    set({ currentReport: report })
  },
  
  setReportGenerating: (generating) => {
    set({ reportGenerating: generating })
  },
  
  generateReport: async (workflowResults) => {
    const { setReportGenerating, addReport, setCurrentReport, setCurrentTab } = get()
    
    try {
      setReportGenerating(true)
      
      // 워크플로우 결과 데이터 준비
      const reportData = {
        workflowResults,
        timestamp: new Date().toISOString(),
        totalStocks: workflowResults.reduce((total, result) => {
          if (result.tool_used === 'get_all_tickers' && result.result) {
            try {
              const data = JSON.parse(result.result)
              return data.total_count || 0
            } catch {
              return 0
            }
          }
          return total
        }, 0),
        filteredStocks: workflowResults.reduce((total, result) => {
          if (result.tool_used === 'filter_stocks_by_fundamentals' && result.result) {
            try {
              const data = JSON.parse(result.result)
              return data.filtered_stocks?.length || 0
            } catch {
              return 0
            }
          }
          return total
        }, 0)
      }
      
      // GPT API 호출하여 보고서 생성
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData)
      })
      
      if (!response.ok) {
        throw new Error('보고서 생성 실패')
      }
      
      const reportContent = await response.text()
      
      // 보고서 객체 생성
      const newReport: Report = {
        id: `report_${Date.now()}`,
        title: `투자 분석 보고서 - ${new Date().toLocaleDateString()}`,
        content: reportContent,
        type: 'investment_analysis',
        status: 'completed',
        generatedAt: new Date(),
        metadata: {
          stocksAnalyzed: reportData.filteredStocks,
          executionTime: Date.now(),
          dataSource: workflowResults.map(r => r.tool_used).filter(Boolean)
        },
        sections: [
          {
            id: 'summary',
            title: '요약',
            content: reportContent.split('\n\n')[0] || '요약 정보 없음',
            type: 'summary',
            order: 1
          },
          {
            id: 'analysis',
            title: '분석 결과',
            content: reportContent,
            type: 'analysis',
            order: 2
          }
        ]
      }
      
      addReport(newReport)
      setCurrentReport(newReport)
      setCurrentTab('report')
      
    } catch (error) {
      console.error('보고서 생성 실패:', error)
      
      // 에러 시 샘플 보고서 생성
      const fallbackReport: Report = {
        id: `report_${Date.now()}`,
        title: `투자 분석 보고서 - ${new Date().toLocaleDateString()}`,
        content: `# 투자 분석 보고서

## 요약
워크플로우 실행 결과를 바탕으로 한 투자 분석 보고서입니다.

## 분석 결과
${workflowResults.map((result, index) => `
### ${index + 1}. ${result.tool_used || '분석 단계'}
${result.result ? JSON.stringify(JSON.parse(result.result), null, 2) : '결과 없음'}
`).join('\n')}

## 투자 제안
분석된 데이터를 바탕으로 한 투자 제안사항입니다.

*이 보고서는 자동 생성되었으며, 실제 투자 결정 시 추가적인 분석이 필요합니다.*`,
        type: 'investment_analysis',
        status: 'completed',
        generatedAt: new Date(),
        metadata: {
          stocksAnalyzed: workflowResults.length,
          executionTime: Date.now(),
          dataSource: workflowResults.map(r => r.tool_used).filter(Boolean)
        },
        sections: [
          {
            id: 'summary',
            title: '요약',
            content: '워크플로우 실행 결과를 바탕으로 한 투자 분석 보고서입니다.',
            type: 'summary',
            order: 1
          }
        ]
      }
      
      addReport(fallbackReport)
      setCurrentReport(fallbackReport)
      setCurrentTab('report')
      
    } finally {
      setReportGenerating(false)
    }
  }
}))

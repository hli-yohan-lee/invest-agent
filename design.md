# AI Agent Workflow Platform - Design Document

## 1. 시스템 아키텍처

### 1.1 전체 아키텍처 개요
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   MCP Server    │
│   (Next.js)     │    │   (Node.js)     │    │   (Python)      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Chat UI       │◄──►│ • API Gateway   │◄──►│ • Finance APIs  │
│ • Canvas Editor │    │ • Planner Model │    │ • Data Modules  │
│ • Result Viewer │    │ • Workflow Exec │    │ • AI Agents     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   Database      │
                    │ (PostgreSQL +   │
                    │  Redis Cache)   │
                    └─────────────────┘
```

### 1.2 마이크로서비스 구조
- **Frontend Service**: Next.js 기반 사용자 인터페이스
- **API Gateway**: 라우팅 및 인증 처리
- **Planner Service**: AI 플래닝 및 전략 수립
- **Workflow Engine**: 워크플로우 실행 및 관리
- **MCP Connector**: MCP 서버와의 통신 인터페이스
- **Data Service**: 사용자 데이터 및 결과 저장

## 2. 사용자 인터페이스 설계

### 2.1 전체 레이아웃 구조
```
┌──────────────────────────────────────────────────────────────┐
│                        Header                                 │
│  [Logo] [프로젝트명]                    [설정] [사용자메뉴]    │
├──────────────────────────────────────────────────────────────┤
│                     Tab Navigation                           │
│    [1. 플래닝] [2. 워크플로우] [3. 결과]                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    Main Content Area                         │
│                  (탭별 콘텐츠 영역)                           │
│                                                              │
│                                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                    Input Bar (Fixed)                        │
│  [💬] [사용자 입력창________________________] [전송] [🎤]    │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 탭별 상세 설계

#### 2.2.1 플래닝 탭 (1번 탭)
```
┌──────────────────────────────────────────────────────────────┐
│                      Chat Interface                         │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 사용자: PER이 높은 기업 분석해줘                          │ │
│ │ ──────────────────────────────────────────────────────── │ │
│ │ AI: 다음과 같은 분석 전략을 제안합니다:                   │ │
│ │                                                          │ │
│ │ 1. 코스피/코스닥 전체 종목 PER 데이터 수집               │ │
│ │ 2. 업종별 PER 상위 20% 기업 필터링                      │ │
│ │ 3. 재무건전성 지표 추가 분석                            │ │
│ │ 4. 최종 투자 추천 리포트 생성                           │ │
│ │                                                          │ │
│ │ [✏️ 편집] [📋 복사] [🔄 재생성]                        │ │
│ │                                                          │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │    실행하시겠습니까?                                 │ │ │
│ │ │                 [실행] [수정]                       │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

#### 2.2.2 워크플로우 탭 (2번 탭)
```
┌──────────────────────────────────────────────────────────────┐
│  [🎯] [📊] [⚙️] [💾] [▶️]     Canvas Controls                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│    ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●        │
│   시작    ┌─────────────────────┐    ┌─────────────────────┐  │
│          │      데이터 수집     │    │     데이터 분석     │  │
│          │ ┌─────────────────┐ │    │ ┌─────────────────┐ │  │
│          │ │PER 데이터 수집   │ │    │ │상위 20% 필터링  │ │  │
│          │ └─────────────────┘ │    │ └─────────────────┘ │  │
│          │ ☑ 에이전트 툴 사용  │    │ ☑ 에이전트 툴 사용  │  │
│          │ ▼ MCP 모듈 선택     │    │ ▼ MCP 모듈 선택     │  │
│          │ ☑ naver-finance     │    │ ☑ data-analyzer     │  │
│          │ ☑ kakao-finance     │    │ ☐ esg-analyzer      │  │
│          └─────────────────────┘    └─────────────────────┘  │
│                     │                        │               │
│                     ●━━━━━━━━━━━━━━━━━━━━━━━━●               │
│                                              │               │
│              ┌─────────────────────┐    ┌─────────────────┐  │
│              │    재무분석 추가    │    │   결과 보고     │  │
│              │ ┌─────────────────┐ │    │ ▼ 출력 형식     │  │
│              │ │재무건전성 분석  │ │    │ ◉ 테이블        │  │
│              │ └─────────────────┘ │    │ ○ 보고서        │  │
│              │ ☑ 에이전트 툴 사용  │    └─────────────────┘  │
│              │ ▼ MCP 모듈 선택     │                        │
│              │ ☑ financial-analyze │                        │
│              └─────────────────────┘                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

#### 2.2.3 결과 탭 (3번 탭)
```
┌──────────────────────────────────────────────────────────────┐
│ [📊 테이블] [📝 보고서] [📤 내보내기] [📜 히스토리]         │
├──────────────────────────────────────────────────────────────┤
│                     실행 결과                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 회사명    │ 종목코드 │  PER  │ 업종      │ 투자등급       │ │
│ │──────────┼─────────┼───────┼──────────┼──────────────  │ │
│ │ 삼성전자  │ 005930  │ 24.5  │ 반도체    │ 매수           │ │
│ │ SK하이닉스│ 000660  │ 22.1  │ 반도체    │ 매수           │ │
│ │ LG화학    │ 051910  │ 19.8  │ 화학      │ 보유           │ │
│ │ 포스코홀딩스│373220  │ 18.2  │ 철강      │ 보유           │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│                      분석 보고서                            │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ ## PER 기반 투자 분석 결과                               │ │
│ │                                                          │ │
│ │ ### 주요 발견사항                                        │ │
│ │ - 반도체 업종이 높은 PER 구간에서 강세를 보임           │ │
│ │ - 삼성전자와 SK하이닉스는 성장성 대비 적정 밸류에이션    │ │
│ │                                                          │ │
│ │ ### 투자 권고                                            │ │
│ │ 1. 단기적으로는 반도체 업종 중심의 포트폴리오 구성       │ │
│ │ 2. 중장기적으로는 업종 다변화 필요                      │ │
│ │                                                          │ │
│ │ [✏️ 편집모드]                                           │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 3. 컴포넌트 설계

### 3.1 React 컴포넌트 구조
```
App
├── Header
│   ├── Logo
│   ├── UserMenu
│   └── Settings
├── TabNavigation
│   ├── PlanningTab
│   ├── WorkflowTab
│   └── ResultTab
├── MainContent
│   ├── PlanningView
│   │   ├── ChatInterface
│   │   ├── MessageBubble
│   │   ├── ActionButtons
│   │   └── ExecutionPrompt
│   ├── WorkflowView
│   │   ├── CanvasToolbar
│   │   ├── FlowCanvas
│   │   ├── NodeEditor
│   │   │   ├── StartNode
│   │   │   ├── TaskNode
│   │   │   │   ├── PromptInput
│   │   │   │   ├── AgentToolCheckbox
│   │   │   │   └── MCPModuleSelector
│   │   │   └── ResultNode
│   │   └── ExecutionPanel
│   └── ResultView
│       ├── ResultToolbar
│       ├── TableView
│       ├── ReportEditor
│       └── ExportPanel
└── InputBar
    ├── InputField
    ├── SendButton
    └── VoiceInput
```

### 3.2 상태 관리 구조 (Zustand)
```typescript
interface AppState {
  // 전역 상태
  currentTab: 'planning' | 'workflow' | 'result';
  isLoading: boolean;
  error: string | null;
  
  // 플래닝 상태
  chatHistory: Message[];
  currentPlan: Plan | null;
  
  // 워크플로우 상태
  nodes: Node[];
  edges: Edge[];
  selectedNode: string | null;
  executionStatus: 'idle' | 'running' | 'completed' | 'error';
  
  // 결과 상태
  results: Result[];
  currentResult: Result | null;
  viewMode: 'table' | 'report';
  
  // MCP 상태
  availableModules: MCPModule[];
  moduleStatus: Record<string, 'online' | 'offline'>;
  
  // 액션들
  actions: {
    // 플래닝 액션
    sendMessage: (message: string) => Promise<void>;
    updatePlan: (plan: Plan) => void;
    executePlan: () => Promise<void>;
    
    // 워크플로우 액션
    addNode: (node: Node) => void;
    updateNode: (id: string, updates: Partial<Node>) => void;
    deleteNode: (id: string) => void;
    addEdge: (edge: Edge) => void;
    executeWorkflow: () => Promise<void>;
    
    // 결과 액션
    updateResult: (result: Result) => void;
    exportResult: (format: 'csv' | 'pdf' | 'excel') => Promise<void>;
    
    // MCP 액션
    loadModules: () => Promise<void>;
    toggleModule: (moduleId: string, enabled: boolean) => void;
  };
}
```

## 4. 데이터 모델

### 4.1 핵심 데이터 구조
```typescript
// 메시지 구조
interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    planId?: string;
    executionId?: string;
  };
}

// 플랜 구조
interface Plan {
  id: string;
  title: string;
  description: string;
  steps: PlanStep[];
  status: 'draft' | 'approved' | 'executing' | 'completed';
  createdAt: Date;
  updatedAt: Date;
}

interface PlanStep {
  id: string;
  title: string;
  description: string;
  order: number;
  mcpModules: string[];
  parameters: Record<string, any>;
}

// 워크플로우 노드 구조
interface Node {
  id: string;
  type: 'start' | 'task' | 'result';
  position: { x: number; y: number };
  data: {
    label: string;
    prompt?: string;
    useAgentTool?: boolean;
    selectedModules?: string[];
    outputFormat?: 'table' | 'report';
    parameters?: Record<string, any>;
  };
}

interface Edge {
  id: string;
  source: string;
  target: string;
  type: 'default';
}

// 결과 구조
interface Result {
  id: string;
  workflowId: string;
  type: 'table' | 'report';
  data: any;
  metadata: {
    executionTime: number;
    timestamp: Date;
    modules: string[];
  };
  editable: boolean;
}

// MCP 모듈 구조
interface MCPModule {
  id: string;
  name: string;
  description: string;
  version: string;
  category: 'data' | 'analysis' | 'report';
  parameters: MCPParameter[];
  status: 'online' | 'offline';
}

interface MCPParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select';
  required: boolean;
  description: string;
  options?: string[];
  defaultValue?: any;
}
```

## 5. API 설계

### 5.1 REST API 엔드포인트
```
# 인증
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me

# 플래닝
POST /api/planning/chat        # 메시지 전송
GET  /api/planning/history     # 채팅 히스토리
POST /api/planning/plan        # 플랜 생성
PUT  /api/planning/plan/:id    # 플랜 수정

# 워크플로우
GET  /api/workflows           # 워크플로우 목록
POST /api/workflows           # 워크플로우 생성
PUT  /api/workflows/:id       # 워크플로우 수정
DELETE /api/workflows/:id     # 워크플로우 삭제
POST /api/workflows/:id/execute # 워크플로우 실행

# 결과
GET  /api/results             # 결과 목록
GET  /api/results/:id         # 결과 상세
PUT  /api/results/:id         # 결과 수정
POST /api/results/:id/export  # 결과 내보내기

# MCP
GET  /api/mcp/modules         # 사용 가능한 모듈 목록
GET  /api/mcp/modules/:id     # 모듈 상세 정보
POST /api/mcp/modules/:id/execute # 모듈 실행
```

### 5.2 WebSocket 이벤트
```typescript
// 클라이언트 → 서버
interface ClientEvents {
  'chat:message': { content: string };
  'workflow:execute': { workflowId: string };
  'workflow:stop': { executionId: string };
}

// 서버 → 클라이언트  
interface ServerEvents {
  'chat:response': { message: Message };
  'workflow:progress': { 
    executionId: string; 
    progress: number; 
    currentStep: string 
  };
  'workflow:complete': { 
    executionId: string; 
    result: Result 
  };
  'workflow:error': { 
    executionId: string; 
    error: string 
  };
  'mcp:status': { 
    moduleId: string; 
    status: 'online' | 'offline' 
  };
}
```

## 6. 데이터베이스 설계

### 6.1 테이블 구조 (PostgreSQL)
```sql
-- 사용자 테이블
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 대화 세션 테이블
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id INTEGER REFERENCES users(id),
  title VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 메시지 테이블
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES chat_sessions(id),
  type VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 플랜 테이블
CREATE TABLE plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES chat_sessions(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  steps JSONB NOT NULL,
  status VARCHAR(20) DEFAULT 'draft',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 워크플로우 테이블
CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id UUID REFERENCES plans(id),
  user_id INTEGER REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  nodes JSONB NOT NULL,
  edges JSONB NOT NULL,
  status VARCHAR(20) DEFAULT 'draft',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 실행 결과 테이블
CREATE TABLE execution_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID REFERENCES workflows(id),
  type VARCHAR(20) NOT NULL, -- 'table', 'report'
  data JSONB NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- MCP 모듈 상태 테이블
CREATE TABLE mcp_modules (
  id VARCHAR(100) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  version VARCHAR(50),
  category VARCHAR(50),
  parameters JSONB,
  status VARCHAR(20) DEFAULT 'offline',
  last_heartbeat TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Redis 캐시 구조
```
# 세션 캐시
session:{sessionId} -> { userId, metadata }

# MCP 모듈 상태 캐시
mcp:status:{moduleId} -> { status, lastSeen }

# 실행 진행상황 캐시
execution:{executionId} -> { 
  progress, 
  currentStep, 
  startTime, 
  estimatedCompletion 
}

# 사용자별 최근 결과 캐시
user:recent:{userId} -> [resultId1, resultId2, ...]
```

## 7. 보안 및 성능

### 7.1 보안 설계
```typescript
// JWT 토큰 구조
interface JWTPayload {
  userId: number;
  email: string;
  role: 'user' | 'admin';
  iat: number;
  exp: number;
}

// API 키 관리
interface APIKeyConfig {
  openai: string;
  claude: string;
  mcpServers: Record<string, string>;
}

// 권한 체크 미들웨어
const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET) as JWTPayload;
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

### 7.2 성능 최적화
```typescript
// React Query 설정
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5분
      cacheTime: 10 * 60 * 1000, // 10분
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

// 가상화된 큰 리스트 렌더링
const VirtualizedResultTable = ({ data }: { data: Result[] }) => {
  const Row = ({ index, style }: { index: number; style: any }) => (
    <div style={style}>
      <ResultRow data={data[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={data.length}
      itemSize={50}
    >
      {Row}
    </FixedSizeList>
  );
};

// 캔버스 최적화 (React Flow)
const optimizedNodeTypes = {
  start: memo(StartNode),
  task: memo(TaskNode),
  result: memo(ResultNode),
};
```

## 8. 배포 및 모니터링

### 8.1 Docker 구성
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend Dockerfile  
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 8000
CMD ["npm", "start"]
```

### 8.2 Kubernetes 배포
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-workflow-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-workflow-frontend
  template:
    metadata:
      labels:
        app: ai-workflow-frontend
    spec:
      containers:
      - name: frontend
        image: ai-workflow-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.aiworkflow.com"
```

### 8.3 모니터링 설정
```typescript
// 성능 메트릭 수집
const performanceMonitor = {
  trackAPIResponse: (endpoint: string, responseTime: number) => {
    prometheus.histogram
      .labels({ endpoint })
      .observe(responseTime);
  },
  
  trackUserAction: (action: string, userId: number) => {
    prometheus.counter
      .labels({ action, userId })
      .inc();
  },
  
  trackError: (error: Error, context: string) => {
    logger.error(`Error in ${context}:`, error);
    prometheus.counter
      .labels({ error: error.name, context })
      .inc();
  },
};
```

## 9. 테스트 전략

### 9.1 단위 테스트
```typescript
// 컴포넌트 테스트 예시
describe('ChatInterface', () => {
  it('should send message when enter is pressed', async () => {
    const mockSendMessage = jest.fn();
    render(<ChatInterface onSendMessage={mockSendMessage} />);
    
    const input = screen.getByPlaceholderText('메시지를 입력하세요');
    fireEvent.change(input, { target: { value: 'test message' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 13 });
    
    expect(mockSendMessage).toHaveBeenCalledWith('test message');
  });
});

// API 테스트 예시
describe('Planning API', () => {
  it('should create plan from chat message', async () => {
    const response = await request(app)
      .post('/api/planning/chat')
      .send({ content: 'PER 높은 기업 분석해줘' })
      .expect(200);
      
    expect(response.body.plan).toBeDefined();
    expect(response.body.plan.steps).toHaveLength(4);
  });
});
```

### 9.2 E2E 테스트
```typescript
// Playwright E2E 테스트
test('complete workflow execution', async ({ page }) => {
  await page.goto('/');
  
  // 1. 플래닝 단계
  await page.fill('[data-testid=chat-input]', 'PER 높은 기업 분석해줘');
  await page.click('[data-testid=send-button]');
  await page.waitForSelector('[data-testid=execution-prompt]');
  await page.click('[data-testid=execute-button]');
  
  // 2. 워크플로우 단계
  await page.waitForSelector('[data-testid=workflow-canvas]');
  await page.click('[data-testid=start-node]');
  
  // 3. 결과 확인
  await page.waitForSelector('[data-testid=result-table]');
  const resultRows = await page.locator('[data-testid=result-row]').count();
  expect(resultRows).toBeGreaterThan(0);
});
```

## 10. 결론

본 설계 문서는 AI Agent Workflow Platform의 전체적인 아키텍처와 구현 방향을 제시합니다. 모듈화된 설계와 확장 가능한 아키텍처를 통해 향후 기능 추가와 성능 개선이 용이하도록 구성되었습니다.

주요 설계 원칙:
- **사용자 중심**: 직관적이고 반응적인 UI/UX
- **확장성**: 마이크로서비스와 플러그인 아키텍처
- **성능**: 최적화된 렌더링과 캐싱 전략
- **보안**: 강력한 인증과 데이터 보호
- **모니터링**: 포괄적인 로깅과 메트릭 수집

// 기본 타입 정의
export interface User {
  id: string;
  email: string;
  username: string;
  passwordHash: string;
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
  isActive: boolean;
  role: 'user' | 'admin';
}

export interface Plan {
  id: string;
  userId: string;
  title: string;
  description: string;
  steps: PlanStep[];
  status: 'draft' | 'approved' | 'executing' | 'completed' | 'failed';
  createdAt: Date;
  updatedAt: Date;
  executionStartAt?: Date;
  executionEndAt?: Date;
  metadata?: Record<string, any>;
}

export interface PlanStep {
  id: string;
  planId: string;
  title: string;
  description: string;
  order: number;
  type: 'data_collection' | 'analysis' | 'report_generation';
  mcpModules: string[];
  parameters: Record<string, any>;
  prompt?: string;
  useAgent?: boolean;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  startedAt?: Date;
  completedAt?: Date;
}

export interface ChatMessage {
  id: string;
  userId: string;
  planId?: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    executionId?: string;
    stepId?: string;
    tokens?: number;
  };
}

export interface WorkflowExecution {
  id: string;
  planId: string;
  userId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  currentStepIndex: number;
  results: Record<string, any>;
  errors: string[];
  startedAt: Date;
  completedAt?: Date;
  metadata?: Record<string, any>;
}

// MCP 모듈 관련 타입
export interface MCPModule {
  id: string;
  name: string;
  displayName: string;
  type: 'securities' | 'data' | 'analysis' | 'report';
  description: string;
  version: string;
  isActive: boolean;
  capabilities: string[];
  config: Record<string, any>;
}

export interface MCPRequest {
  moduleId: string;
  method: string;
  parameters: Record<string, any>;
  timeout?: number;
}

export interface MCPResponse {
  success: boolean;
  data?: any;
  error?: string;
  executionTime: number;
  timestamp: Date;
}

// 증권 데이터 관련 타입
export interface StockInfo {
  symbol: string;
  name: string;
  market: 'KOSPI' | 'KOSDAQ' | 'NASDAQ' | 'NYSE';
  sector: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
  updatedAt: Date;
}

export interface StockPrice {
  symbol: string;
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjustedClose?: number;
}

export interface FinancialStatement {
  symbol: string;
  period: string;
  type: 'quarterly' | 'annual';
  revenue: number;
  netIncome: number;
  totalAssets: number;
  totalLiabilities: number;
  shareholderEquity: number;
  operatingCashFlow: number;
  updatedAt: Date;
}

// API 응답 타입
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// 요청 타입
export interface CreatePlanRequest {
  title: string;
  description: string;
  steps: Omit<PlanStep, 'id' | 'planId' | 'status' | 'startedAt' | 'completedAt'>[];
}

export interface UpdatePlanRequest {
  title?: string;
  description?: string;
  steps?: Partial<PlanStep>[];
}

export interface ExecutePlanRequest {
  planId: string;
  overrideParameters?: Record<string, any>;
}

export interface SendMessageRequest {
  content: string;
  planId?: string;
  type?: 'user';
}

// 에러 타입
export interface AppError extends Error {
  statusCode: number;
  isOperational: boolean;
}

// 환경 변수 타입
export interface EnvConfig {
  NODE_ENV: string;
  PORT: number;
  MONGODB_URI: string;
  REDIS_URL: string;
  JWT_SECRET: string;
  JWT_EXPIRES_IN: string;
  OPENAI_API_KEY: string;
  NAVER_API_KEY: string;
  TOSS_API_KEY: string;
  KAKAO_API_KEY: string;
  YAHOO_FINANCE_API_KEY: string;
  KRX_API_KEY: string;
  SOCKET_CORS_ORIGIN: string;
  LOG_LEVEL: string;
}

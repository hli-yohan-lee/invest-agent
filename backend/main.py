"""
AI Agent Workflow Platform - FastAPI 백엔드 서버
투자 분석 워크플로우 플랫폼의 메인 애플리케이션
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import verify_token
from app.api import auth, planning, workflow, results, mcp, users
from app.api import settings as settings_api
from app.utils.logger import setup_logger

# 로거 설정
logger = setup_logger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="AI Agent Workflow Platform",
    description="투자 분석 AI Agent 워크플로우 플랫폼 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host 미들웨어
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", settings.HOST]
)

# API 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(planning.router, prefix="/api/planning", tags=["Planning"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP"])

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    logger.info("🚀 AI Agent Workflow Platform 시작")
    
    # 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ 데이터베이스 초기화 완료")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 정리"""
    logger.info("🛑 AI Agent Workflow Platform 종료")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "AI Agent Workflow Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": "2025-07-30T00:00:00Z"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

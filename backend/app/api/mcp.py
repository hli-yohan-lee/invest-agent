"""
MCP 서버 연동 API 라우터
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/modules")
async def get_mcp_modules(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """사용 가능한 MCP 모듈 목록 조회"""
    # 임시 데이터 (실제로는 MCP 서버에서 동적 로딩)
    modules = [
        {
            "id": "naver-finance-agent",
            "name": "네이버 증권 에이전트",
            "description": "네이버 증권에서 주식 데이터를 수집합니다",
            "category": "data_collection",
            "version": "1.0.0",
            "is_active": True
        },
        {
            "id": "kakao-finance-agent", 
            "name": "카카오페이 증권 에이전트",
            "description": "카카오페이 증권 데이터를 연동합니다",
            "category": "data_collection",
            "version": "1.0.0",
            "is_active": True
        },
        {
            "id": "esg-analyzer",
            "name": "ESG 분석기",
            "description": "기업의 ESG 점수를 분석합니다",
            "category": "analysis",
            "version": "1.0.0",
            "is_active": True
        },
        {
            "id": "portfolio-optimizer",
            "name": "포트폴리오 최적화",
            "description": "포트폴리오를 최적화합니다",
            "category": "optimization",
            "version": "1.0.0",
            "is_active": True
        }
    ]
    
    return {"modules": modules}

@router.get("/modules/{module_id}")
async def get_mcp_module(
    module_id: str,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """특정 MCP 모듈 정보 조회"""
    return {
        "id": module_id,
        "name": f"모듈 {module_id}",
        "description": f"{module_id} 모듈의 상세 정보",
        "category": "data_collection",
        "version": "1.0.0",
        "is_active": True,
        "config_schema": {
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
                "timeout": {"type": "integer", "default": 30}
            }
        }
    }

@router.post("/modules/{module_id}/execute")
async def execute_mcp_module(
    module_id: str,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """MCP 모듈 실행"""
    user_id = token_data.get("user_id")
    return {
        "message": f"MCP 모듈 {module_id} 실행",
        "user_id": user_id,
        "status": "success"
    }

@router.get("/status")
async def get_mcp_status():
    """MCP 서버 상태 확인"""
    return {
        "status": "connected",
        "server_url": "localhost:3001",
        "available_modules": 4,
        "last_update": "2025-07-30T00:00:00Z"
    }

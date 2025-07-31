"""
워크플로우 관련 API 라우터  
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
async def get_workflows(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 목록 조회"""
    user_id = token_data.get("user_id")
    return {"message": "워크플로우 목록", "user_id": user_id}

@router.post("/")
async def create_workflow(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """새 워크플로우 생성"""
    user_id = token_data.get("user_id")
    return {"message": "워크플로우 생성", "user_id": user_id}

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 상세 조회"""
    user_id = token_data.get("user_id")
    return {"message": f"워크플로우 {workflow_id} 조회", "user_id": user_id}

@router.put("/{workflow_id}")
async def update_workflow(
    workflow_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 업데이트"""
    user_id = token_data.get("user_id")
    return {"message": f"워크플로우 {workflow_id} 업데이트", "user_id": user_id}

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 실행"""
    user_id = token_data.get("user_id")
    return {"message": f"워크플로우 {workflow_id} 실행", "user_id": user_id}

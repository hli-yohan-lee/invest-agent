"""
결과 관련 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
async def get_results(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """결과 목록 조회"""
    user_id = token_data.get("user_id")
    return {"message": "결과 목록", "user_id": user_id}

@router.get("/{result_id}")
async def get_result(
    result_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """결과 상세 조회"""
    user_id = token_data.get("user_id")
    return {"message": f"결과 {result_id} 조회", "user_id": user_id}

@router.get("/reports")
async def get_reports(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """보고서 목록 조회"""
    user_id = token_data.get("user_id")
    return {"message": "보고서 목록", "user_id": user_id}

@router.post("/reports")
async def create_report(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """새 보고서 생성"""
    user_id = token_data.get("user_id")
    return {"message": "보고서 생성", "user_id": user_id}

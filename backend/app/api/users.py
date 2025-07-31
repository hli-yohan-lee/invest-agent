"""
사용자 관련 API 라우터
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token, get_password_hash, verify_password
from app.schemas.user import User, UserUpdate, PasswordChange, UserProfile
from app.crud.user import user_crud
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/profile", response_model=UserProfile)
async def get_profile(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """사용자 프로필 조회"""
    user_id = token_data.get("user_id")
    
    user_stats = await user_crud.get_user_with_stats(db, user_id)
    
    if not user_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    user = user_stats["user"]
    return UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        conversation_count=user_stats["conversation_count"],
        workflow_count=user_stats["workflow_count"],
        report_count=user_stats["report_count"]
    )

@router.put("/profile", response_model=User)
async def update_profile(
    user_update: UserUpdate,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """사용자 프로필 업데이트"""
    user_id = token_data.get("user_id")
    
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # 이메일 중복 확인
    if user_update.email and user_update.email != user.email:
        existing_user = await user_crud.get_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다"
            )
    
    # 사용자명 중복 확인
    if user_update.username and user_update.username != user.username:
        existing_user = await user_crud.get_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 사용자명입니다"
            )
    
    # 프로필 업데이트
    updated_user = await user_crud.update(
        db, user,
        email=user_update.email,
        username=user_update.username,
        full_name=user_update.full_name,
        is_active=user_update.is_active
    )
    
    return updated_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """비밀번호 변경"""
    user_id = token_data.get("user_id")
    
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # 현재 비밀번호 확인
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다"
        )
    
    # 새 비밀번호 해싱 및 업데이트
    new_hashed_password = get_password_hash(password_data.new_password)
    await user_crud.update(db, user, hashed_password=new_hashed_password)
    
    return {"message": "비밀번호가 성공적으로 변경되었습니다"}

@router.delete("/account")
async def delete_account(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """계정 삭제"""
    user_id = token_data.get("user_id")
    
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    await user_crud.delete(db, user)
    
    return {"message": "계정이 성공적으로 삭제되었습니다"}

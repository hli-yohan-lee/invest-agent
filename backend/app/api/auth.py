"""
인증 관련 API 라우터
"""

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    verify_token
)
from app.schemas.user import UserCreate, User, Token, UserLogin
from app.crud.user import user_crud
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """사용자 회원가입"""
    logger.info("새 사용자 회원가입 시도", email=user_data.email)
    
    # 이메일 중복 확인
    existing_user = await user_crud.get_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 사용자명 중복 확인
    existing_username = await user_crud.get_by_username(db, username=user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다"
        )
    
    # 비밀번호 해싱
    hashed_password = get_password_hash(user_data.password)
    
    # 사용자 생성
    user = await user_crud.create(
        db,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    logger.info("사용자 회원가입 완료", user_id=user.id, email=user.email)
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """사용자 로그인 (OAuth2 호환)"""
    logger.info("사용자 로그인 시도", username=form_data.username)
    
    # 사용자 조회 (이메일 또는 사용자명으로)
    user = await user_crud.get_by_email(db, email=form_data.username)
    if not user:
        user = await user_crud.get_by_username(db, username=form_data.username)
    
    # 사용자 검증
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 인증 정보입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다"
        )
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    logger.info("사용자 로그인 성공", user_id=user.id, username=user.username)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/login/email", response_model=Token)
async def login_with_email(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """이메일로 로그인"""
    logger.info("이메일 로그인 시도", email=login_data.email)
    
    # 사용자 조회
    user = await user_crud.get_by_email(db, email=login_data.email)
    
    # 사용자 검증
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다"
        )
    
    # JWT 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    logger.info("이메일 로그인 성공", user_id=user.id, email=user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer", 
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.get("/me", response_model=User)
async def get_current_user(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """현재 로그인한 사용자 정보 조회"""
    username = token_data.get("sub")
    user = await user_crud.get_by_username(db, username=username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """토큰 갱신"""
    username = token_data.get("sub")
    user_id = token_data.get("user_id")
    
    # 새 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "user_id": user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

"""
사용자 관련 스키마
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# 기본 스키마
class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

# 요청 스키마
class UserCreate(UserBase):
    """사용자 생성 요청 스키마"""
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    """사용자 업데이트 요청 스키마"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    """사용자 로그인 요청 스키마"""
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    """비밀번호 변경 요청 스키마"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

# 응답 스키마
class User(UserBase):
    """사용자 응답 스키마"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserProfile(User):
    """사용자 프로필 응답 스키마"""
    conversation_count: int = 0
    workflow_count: int = 0
    report_count: int = 0

# 토큰 스키마
class Token(BaseModel):
    """JWT 토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """토큰 데이터 스키마"""
    username: Optional[str] = None

"""
사용자 CRUD 작업
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User

class UserCRUD:
    """사용자 CRUD 클래스"""
    
    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(
        self, 
        db: AsyncSession, 
        email: str, 
        username: str, 
        hashed_password: str,
        full_name: Optional[str] = None
    ) -> User:
        """새 사용자 생성"""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def update(
        self, 
        db: AsyncSession, 
        user: User, 
        **kwargs
    ) -> User:
        """사용자 정보 업데이트"""
        for field, value in kwargs.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def delete(self, db: AsyncSession, user: User) -> bool:
        """사용자 삭제"""
        await db.delete(user)
        await db.commit()
        return True
    
    async def get_user_with_stats(self, db: AsyncSession, user_id: int) -> Optional[dict]:
        """사용자 정보와 통계 조회"""
        stmt = select(User).options(
            selectinload(User.conversations),
            selectinload(User.workflows),
            selectinload(User.reports)
        ).where(User.id == user_id)
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        return {
            "user": user,
            "conversation_count": len(user.conversations),
            "workflow_count": len(user.workflows),
            "report_count": len(user.reports)
        }

# 글로벌 인스턴스
user_crud = UserCRUD()

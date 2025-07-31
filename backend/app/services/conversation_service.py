"""
대화 및 플랜 관리 서비스
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message, Plan
from app.schemas.conversation import PlanCreate
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ConversationService:
    """대화 및 플랜 관리 서비스"""
    
    async def get_or_create_conversation(
        self, 
        db: AsyncSession, 
        user_id: int, 
        conversation_id: Optional[int] = None
    ) -> Conversation:
        """대화 조회 또는 새로 생성"""
        
        if conversation_id:
            # 기존 대화 조회
            stmt = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()
            
            if conversation:
                return conversation
        
        # 새 대화 생성
        conversation = Conversation(
            user_id=user_id,
            title="새 대화",
            status="active"
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        return conversation
    
    async def create_conversation(
        self, 
        db: AsyncSession, 
        user_id: int, 
        title: str
    ) -> Conversation:
        """새 대화 생성"""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            status="active"
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        return conversation
    
    async def add_message(
        self, 
        db: AsyncSession, 
        conversation_id: int, 
        role: str, 
        content: str,
        extra_data: Optional[dict] = None
    ) -> Message:
        """대화에 메시지 추가"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            extra_data=extra_data
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        return message
    
    async def get_user_conversations(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Conversation]:
        """사용자의 대화 목록 조회"""
        stmt = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def get_conversation_with_messages(
        self, 
        db: AsyncSession, 
        conversation_id: int, 
        user_id: int
    ) -> Optional[Conversation]:
        """메시지와 함께 대화 조회"""
        stmt = select(Conversation).options(
            selectinload(Conversation.messages)
        ).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_plan(self, db: AsyncSession, plan_data: PlanCreate) -> Plan:
        """새 플랜 생성"""
        plan = Plan(
            conversation_id=plan_data.conversation_id,
            user_query=plan_data.user_query,
            plan_content=plan_data.plan_content,
            execution_steps=plan_data.execution_steps,
            estimated_time=plan_data.estimated_time,
            status="pending"
        )
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        
        return plan
    
    async def approve_plan(
        self, 
        db: AsyncSession, 
        plan_id: int, 
        user_id: int
    ) -> Optional[Plan]:
        """플랜 승인"""
        # 플랜 조회 및 권한 확인
        stmt = select(Plan).join(Conversation).where(
            Plan.id == plan_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()
        
        if plan:
            plan.status = "approved"
            await db.commit()
            await db.refresh(plan)
        
        return plan
    
    async def get_plan(
        self, 
        db: AsyncSession, 
        plan_id: int, 
        user_id: int
    ) -> Optional[Plan]:
        """플랜 조회"""
        stmt = select(Plan).join(Conversation).where(
            Plan.id == plan_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_conversation_title(
        self, 
        db: AsyncSession, 
        conversation_id: int, 
        title: str
    ) -> bool:
        """대화 제목 업데이트"""
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if conversation:
            conversation.title = title
            await db.commit()
            return True
        
        return False

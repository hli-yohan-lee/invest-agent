"""
대화 및 플래닝 관련 스키마
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# 메시지 스키마
class MessageBase(BaseModel):
    """메시지 기본 스키마"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)

class MessageCreate(MessageBase):
    """메시지 생성 요청 스키마"""
    conversation_id: int
    extra_data: Optional[Dict[str, Any]] = None

class Message(MessageBase):
    """메시지 응답 스키마"""
    id: int
    conversation_id: int
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 대화 스키마
class ConversationBase(BaseModel):
    """대화 기본 스키마"""
    title: str = Field(..., max_length=200)

class ConversationCreate(ConversationBase):
    """대화 생성 요청 스키마"""
    pass

class ConversationUpdate(BaseModel):
    """대화 업데이트 요청 스키마"""
    title: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(active|completed|archived)$")

class Conversation(ConversationBase):
    """대화 응답 스키마"""
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

# 플래닝 스키마
class PlanBase(BaseModel):
    """플랜 기본 스키마"""
    user_query: str = Field(..., min_length=1)
    plan_content: str = Field(..., min_length=1)

class PlanCreate(PlanBase):
    """플랜 생성 요청 스키마"""
    conversation_id: int
    execution_steps: Optional[List[Dict[str, Any]]] = None
    estimated_time: Optional[int] = None

class PlanUpdate(BaseModel):
    """플랜 업데이트 요청 스키마"""
    plan_content: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|approved|executed|rejected)$")
    execution_steps: Optional[List[Dict[str, Any]]] = None

class Plan(PlanBase):
    """플랜 응답 스키마"""
    id: int
    conversation_id: int
    status: str
    execution_steps: Optional[List[Dict[str, Any]]] = None
    estimated_time: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 채팅 요청/응답 스키마
class ChatRequest(BaseModel):
    """채팅 요청 스키마"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None
    openai_api_key: Optional[str] = None

class ChatResponse(BaseModel):
    """채팅 응답 스키마"""
    message: Message
    conversation_id: int
    plan: Optional[Plan] = None
    suggestions: List[str] = []

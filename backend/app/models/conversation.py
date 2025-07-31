"""
대화 및 플래닝 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Conversation(Base):
    """대화 세션 테이블"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(String(50), default="active")  # active, completed, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """메시지 테이블"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    extra_data = Column(JSON, nullable=True)  # 추가 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    conversation = relationship("Conversation", back_populates="messages")

class Plan(Base):
    """AI 플래닝 결과 테이블"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_query = Column(Text, nullable=False)
    plan_content = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, executed, rejected
    execution_steps = Column(JSON, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # 예상 소요 시간 (분)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    conversation = relationship("Conversation")
    workflows = relationship("Workflow", back_populates="plan")

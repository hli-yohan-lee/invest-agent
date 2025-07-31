"""
워크플로우 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Workflow(Base):
    """워크플로우 테이블"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    canvas_data = Column(JSON, nullable=False)  # 캔버스 노드 및 연결 정보
    status = Column(String(50), default="draft")  # draft, ready, running, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="workflows")
    plan = relationship("Plan", back_populates="workflows")
    nodes = relationship("WorkflowNode", back_populates="workflow")
    executions = relationship("WorkflowExecution", back_populates="workflow")

class WorkflowNode(Base):
    """워크플로우 노드 테이블"""
    __tablename__ = "workflow_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    node_id = Column(String(100), nullable=False)  # 캔버스에서의 고유 ID
    node_type = Column(String(50), nullable=False)  # start, task, result
    title = Column(String(200), nullable=True)
    prompt = Column(Text, nullable=True)
    use_agent_tools = Column(Boolean, default=False)
    mcp_modules = Column(JSON, nullable=True)  # 선택된 MCP 모듈 리스트
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    config = Column(JSON, nullable=True)  # 추가 노드 설정
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    workflow = relationship("Workflow", back_populates="nodes")

class WorkflowExecution(Base):
    """워크플로우 실행 이력 테이블"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), default="running")  # running, completed, failed, cancelled
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    execution_log = Column(JSON, nullable=True)  # 실행 로그 및 결과
    error_message = Column(Text, nullable=True)
    
    # 관계 설정
    workflow = relationship("Workflow", back_populates="executions")
    results = relationship("ExecutionResult", back_populates="execution")

class ExecutionResult(Base):
    """실행 결과 테이블"""
    __tablename__ = "execution_results"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    node_id = Column(String(100), nullable=False)
    result_type = Column(String(50), nullable=False)  # table, report, chart, error
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    execution = relationship("WorkflowExecution", back_populates="results")

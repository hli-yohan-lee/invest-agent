"""
보고서 및 결과 모델
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Report(Base):
    """보고서 테이블"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # 마크다운 형식의 보고서 내용
    report_type = Column(String(50), nullable=False)  # investment_analysis, portfolio_report, etc.
    extra_data = Column(JSON, nullable=True)  # 차트, 이미지 등 메타데이터
    is_public = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="reports")
    execution = relationship("WorkflowExecution")

class DataTable(Base):
    """데이터 테이블 결과"""
    __tablename__ = "data_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    table_name = Column(String(200), nullable=False)
    columns = Column(JSON, nullable=False)  # 컬럼 정보
    data = Column(JSON, nullable=False)  # 테이블 데이터
    row_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    execution = relationship("WorkflowExecution")

class MCPModule(Base):
    """MCP 모듈 정보 테이블"""
    __tablename__ = "mcp_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # finance, analysis, data_collection, etc.
    version = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    config_schema = Column(JSON, nullable=True)  # 모듈 설정 스키마
    capabilities = Column(JSON, nullable=True)  # 모듈 기능 목록
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

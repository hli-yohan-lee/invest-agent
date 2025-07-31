"""
애플리케이션 설정 관리
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 데이터베이스 설정
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./invest_platform.db",
        env="DATABASE_URL"
    )
    
    # Redis 설정
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # JWT 설정
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # AI API 키
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # MCP 서버 설정
    MCP_SERVER_HOST: str = Field(default="localhost", env="MCP_SERVER_HOST")
    MCP_SERVER_PORT: int = Field(default=3001, env="MCP_SERVER_PORT")
    
    # 외부 API 설정
    NAVER_FINANCE_API_KEY: Optional[str] = Field(default=None, env="NAVER_FINANCE_API_KEY")
    KAKAO_FINANCE_API_KEY: Optional[str] = Field(default=None, env="KAKAO_FINANCE_API_KEY")
    
    # CORS 설정
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 글로벌 설정 인스턴스
settings = Settings()

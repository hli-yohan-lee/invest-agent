"""
데이터베이스 연결 및 세션 관리
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 베이스 모델 클래스
Base = declarative_base()

# 데이터베이스 세션 의존성
async def get_db() -> AsyncSession:
    """데이터베이스 세션 생성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

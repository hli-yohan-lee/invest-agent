"""
설정 관련 API 라우터
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from openai import AsyncOpenAI
import openai
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

class OpenAIKeyValidation(BaseModel):
    api_key: str

class ValidationResponse(BaseModel):
    valid: bool
    message: str

@router.post("/validate-openai-key", response_model=ValidationResponse)
async def validate_openai_key(request: OpenAIKeyValidation):
    """OpenAI API 키 유효성 검증 (인증 없음)"""
    logger.info("OpenAI API 키 검증 요청")
    
    try:
        # 비동기 OpenAI 클라이언트로 간단한 요청 테스트
        client = AsyncOpenAI(api_key=request.api_key)
        
        # 간단한 completions 요청으로 API 키 유효성 확인
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=1
        )
        
        logger.info("OpenAI API 키 검증 성공")
        return ValidationResponse(
            valid=True,
            message="API 키가 유효합니다."
        )
        
    except openai.AuthenticationError as e:
        logger.warning("OpenAI API 키 인증 실패", error=str(e))
        return ValidationResponse(
            valid=False,
            message="유효하지 않은 API 키입니다."
        )
    except openai.RateLimitError as e:
        logger.warning("OpenAI API 요청 한도 초과", error=str(e))
        return ValidationResponse(
            valid=True,  # 키는 유효하지만 한도 초과
            message="API 키는 유효하지만 요청 한도를 초과했습니다."
        )
    except Exception as e:
        logger.error("OpenAI API 키 검증 오류", error=str(e))
        return ValidationResponse(
            valid=False,
            message=f"API 키 검증 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/openai-status")
async def get_openai_status():
    """OpenAI API 상태 확인 (인증 없음)"""
    logger.info("OpenAI API 상태 확인")
    
    return {
        "configured": True,  # 클라이언트에서 키 관리
        "message": "클라이언트에서 API 키를 관리합니다."
    }

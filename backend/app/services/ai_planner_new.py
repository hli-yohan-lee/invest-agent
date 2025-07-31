"""
AI 플래너 서비스
투자 관련 사용자 요청을 분석하고 실행 가능한 플랜을 생성
"""

import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class AIPlanner:
    """AI 플래너 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = None
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI API 키가 설정되지 않았습니다")
        
    async def generate_plan_stream(self, user_query: str):
        """사용자 쿼리를 분석하여 투자 분석 플랜 생성 (스트리밍)"""
        logger.info("AI 플랜 생성 시작 (스트리밍)", query_length=len(user_query))
        
        # OpenAI 클라이언트가 없는 경우 기본 응답 반환
        if not self.client:
            yield {
                "type": "content",
                "content": f"'{user_query}'에 대한 투자 분석을 도와드리겠습니다. 현재 AI 플래닝 기능이 설정되지 않아 기본 응답을 제공합니다.",
            }
            return
        
        try:
            # 투자 분석 전문 프롬프트
            system_prompt = """당신은 투자 분석 전문가입니다. PER(주가수익률), PBR(주가순자산비율), ROE(자기자본이익률) 등 재무지표를 활용하여 투자 분석을 제공합니다.

사용자의 질문에 대해 전문적이고 실용적인 투자 분석 조언을 제공하세요. 구체적인 분석 방법, 주의사항, 실행 가능한 투자 전략을 포함하여 답변해주세요."""
            
            # OpenAI API 스트리밍 호출
            stream = await self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o 모델 사용
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            # 스트리밍 응답 처리
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield {
                        "type": "content",
                        "content": content
                    }
            
            # 완료 신호
            yield {
                "type": "done",
                "full_response": full_response
            }
            
            logger.info("AI 플랜 생성 완료 (스트리밍)")
            
        except Exception as e:
            logger.error("AI 플랜 생성 중 오류 (스트리밍)", error=str(e))
            yield {
                "type": "error",
                "content": "죄송합니다. 현재 플랜을 생성할 수 없습니다. 잠시 후 다시 시도해주세요."
            }
    
    async def generate_plan(self, user_query: str) -> Dict[str, Any]:
        """사용자 쿼리를 분석하여 투자 분석 플랜 생성 (기존 방식)"""
        logger.info("AI 플랜 생성 시작", query_length=len(user_query))
        
        # OpenAI 클라이언트가 없는 경우 기본 응답 반환
        if not self.client:
            return {
                "response": f"'{user_query}'에 대한 투자 분석을 도와드리겠습니다. 현재 AI 플래닝 기능이 설정되지 않아 기본 응답을 제공합니다.",
                "plan": "1. 데이터 수집\n2. 분석 실행\n3. 결과 정리\n4. 보고서 생성",
                "steps": [
                    {
                        "step": 1,
                        "title": "데이터 수집",
                        "description": "필요한 투자 데이터를 수집합니다",
                        "tools": ["data-collector"],
                        "estimated_time": 5
                    }
                ],
                "estimated_time": 15,
                "suggestions": ["추가 분석 옵션을 확인해보세요"]
            }
        
        try:
            # 투자 분석 전문 프롬프트
            system_prompt = """당신은 투자 분석 전문가입니다. PER(주가수익률), PBR(주가순자산비율), ROE(자기자본이익률) 등 재무지표를 활용하여 투자 분석을 제공합니다.

사용자의 질문에 대해 전문적이고 실용적인 투자 분석 조언을 제공하세요. 구체적인 분석 방법, 주의사항, 실행 가능한 투자 전략을 포함하여 답변해주세요."""
            
            # OpenAI API 호출
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o 모델 사용
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 응답 반환
            ai_response = response.choices[0].message.content
            
            logger.info("AI 플랜 생성 완료")
            return {
                "response": ai_response,
                "plan": None,
                "steps": [],
                "suggestions": []
            }
            
        except Exception as e:
            logger.error("AI 플랜 생성 중 오류", error=str(e))
            return {
                "response": "죄송합니다. 현재 플랜을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.",
                "plan": None,
                "steps": [],
                "suggestions": []
            }

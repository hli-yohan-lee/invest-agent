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
        """사용자 쿼리를 분석하여 투자 분석 플랜 생성"""
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
            # AI 플래닝 프롬프트
            system_prompt = self._get_planning_prompt()
            
            # OpenAI API 호출
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o 모델로 변경
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 응답 파싱
            ai_response = response.choices[0].message.content
            parsed_result = self._parse_ai_response(ai_response)
            
            logger.info("AI 플랜 생성 완료", has_plan=bool(parsed_result.get("plan")))
            return parsed_result
            
        except Exception as e:
            logger.error("AI 플랜 생성 중 오류", error=str(e))
            return {
                "response": "죄송합니다. 현재 플랜을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.",
                "plan": None,
                "steps": [],
                "suggestions": []
            }
                "suggestions": ["추가 분석 옵션을 확인해보세요"]
            }
        
        try:
            # AI 플래닝 프롬프트
            system_prompt = self._get_planning_prompt()
            
            # OpenAI API 호출
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # GPT-4o 모델로 변경
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 응답 파싱
            ai_response = response.choices[0].message.content
            parsed_result = self._parse_ai_response(ai_response)
            
            logger.info("AI 플랜 생성 완료", has_plan=bool(parsed_result.get("plan")))
            return parsed_result
            
        except Exception as e:
            logger.error("AI 플랜 생성 중 오류", error=str(e))
            return {
                "response": "죄송합니다. 현재 플랜을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.",
                "plan": None,
                "steps": [],
                "suggestions": []
            }
    
    def _get_planning_prompt(self) -> str:
        """AI 플래닝을 위한 시스템 프롬프트"""
        return """
당신은 투자 분석 전문가입니다. 사용자의 투자 관련 요청을 분석하고 실행 가능한 워크플로우 계획을 수립합니다.

## 역할:
- 투자 분석 요청 이해 및 분석
- 단계별 실행 계획 수립
- 필요한 데이터 소스 및 도구 식별
- 예상 소요 시간 제공

## 응답 형식:
다음 JSON 형식으로 응답하세요:

```json
{
    "response": "사용자에게 보여줄 친근한 응답 메시지",
    "plan": "상세한 실행 계획 (실행 가능한 경우에만)",
    "steps": [
        {
            "step": 1,
            "title": "단계 제목",
            "description": "단계 설명",
            "tools": ["필요한 도구/모듈"],
            "estimated_time": 5
        }
    ],
    "estimated_time": 30,
    "suggestions": ["추가 분석 제안사항"]
}
```

## 지원하는 분석 유형:
- 종목 분석 (PER, PBR, ROE 등 재무지표)
- 업종 분석
- 포트폴리오 분석
- ESG 점수 분석
- 배당주 분석
- 기술적 분석
- 시장 동향 분석

## 사용 가능한 MCP 모듈:
- naver-finance-agent: 네이버 증권 데이터
- kakao-finance-agent: 카카오페이 증권 데이터  
- esg-analyzer: ESG 점수 분석
- portfolio-optimizer: 포트폴리오 최적화
- technical-analyzer: 기술적 분석
- market-data-collector: 시장 데이터 수집

사용자의 요청이 투자와 관련이 없거나 불분명한 경우, 친절하게 안내하고 plan은 null로 설정하세요.
"""
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """AI 응답을 파싱하여 구조화된 데이터 반환"""
        try:
            # JSON 부분 추출
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # JSON이 없는 경우 기본 형식으로 반환
                return {
                    "response": ai_response,
                    "plan": None,
                    "steps": [],
                    "suggestions": []
                }
                
        except json.JSONDecodeError:
            logger.warning("AI 응답 JSON 파싱 실패")
            return {
                "response": ai_response,
                "plan": None,
                "steps": [],
                "suggestions": []
            }
    
    async def refine_plan(self, original_plan: str, user_feedback: str) -> Dict[str, Any]:
        """사용자 피드백을 바탕으로 플랜 개선"""
        try:
            prompt = f"""
원래 계획:
{original_plan}

사용자 피드백:
{user_feedback}

위 피드백을 반영하여 개선된 계획을 다시 작성해주세요.
같은 JSON 형식으로 응답해주세요.
"""
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_planning_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error("플랜 개선 중 오류", error=str(e))
            raise

"""
AI 플래너 서비스
투자 관련 사용자 요청을 분석하고 실행 가능한 플랜을 생성
"""

import json
import re
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
            default_response = self._get_default_plan_response(user_query)
            yield {
                "type": "content",
                "content": json.dumps(default_response, ensure_ascii=False, indent=2),
            }
            return
        
        try:
            # 구조화된 투자 분석 전문 프롬프트
            system_prompt = self._get_structured_system_prompt()
            
            # OpenAI API 스트리밍 호출
            stream = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,  # 일관성을 위해 낮은 온도
                max_tokens=3000,
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
            
            # JSON 파싱 시도 및 검증
            try:
                parsed_response = self._parse_and_validate_response(full_response)
                yield {
                    "type": "done",
                    "full_response": json.dumps(parsed_response, ensure_ascii=False, indent=2)
                }
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 응답으로 fallback
                logger.warning("JSON 파싱 실패, 기본 응답으로 fallback")
                default_response = self._get_default_plan_response(user_query)
                yield {
                    "type": "done",
                    "full_response": json.dumps(default_response, ensure_ascii=False, indent=2)
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
            return self._get_default_plan_response(user_query)
        
        try:
            # 구조화된 투자 분석 전문 프롬프트
            system_prompt = self._get_structured_system_prompt()
            
            # OpenAI API 호출
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            # 응답 파싱 및 검증
            ai_response = response.choices[0].message.content
            parsed_response = self._parse_and_validate_response(ai_response)
            
            logger.info("AI 플랜 생성 완료")
            return parsed_response
            
        except Exception as e:
            logger.error("AI 플랜 생성 중 오류", error=str(e))
            return self._get_default_plan_response(user_query)
    
    def _get_structured_system_prompt(self) -> str:
        """구조화된 응답을 위한 시스템 프롬프트"""
        return """당신은 투자 분석 전문가이자 AI Agent Workflow 플래너입니다. 
사용자의 투자 관련 요청을 분석하여 구체적인 실행 계획을 수립하고, 필요한 MCP 툴들을 호출하여 단계별로 작업을 진행합니다.

다음 규칙에 따라 응답하세요:

1. **반드시 JSON 형식으로 응답**해야 합니다.
2. 다음 구조를 정확히 따라야 합니다:

```json
{
  "analysis": "사용자 요청에 대한 간단한 분석",
  "plan_title": "계획 제목",
  "tasks": [
    {
      "id": "unique_task_id",
      "title": "작업 제목",
      "description": "작업 설명",
      "agent_allowed": ["agent1", "agent2"],
      "mcp_tools": ["tool1", "tool2"],
      "dependencies": ["prerequisite_task_id"],
      "estimated_time": "예상 소요 시간"
    }
  ],
  "clarification_questions": [
    {
      "question": "추가로 필요한 정보에 대한 질문",
      "context": "왜 이 정보가 필요한지 설명"
    }
  ],
  "move_to_canvas": true/false,
  "priority": "high/medium/low",
  "complexity": "simple/medium/complex"
}
```

3. **사용 가능한 MCP 툴들**:
   - "stock_data_fetcher": 주식 데이터 수집
   - "financial_analyzer": 재무제표 분석
   - "market_scanner": 시장 스캔
   - "risk_calculator": 리스크 분석
   - "portfolio_optimizer": 포트폴리오 최적화
   - "news_analyzer": 뉴스 분석
   - "technical_analyzer": 기술적 분석
   - "valuation_calculator": 기업가치 평가

4. **사용 가능한 Agent들**:
   - "data_collector": 데이터 수집 전문
   - "financial_analyst": 재무 분석 전문
   - "market_researcher": 시장 조사 전문
   - "risk_manager": 리스크 관리 전문
   - "portfolio_manager": 포트폴리오 관리 전문

5. **응답 규칙**:
   - 복잡한 요청일수록 더 세분화된 tasks를 생성
   - 각 task는 구체적이고 실행 가능해야 함
   - dependencies를 통해 작업 순서 명시
   - 불분명한 요청의 경우 clarification_questions 포함
   - 워크플로우 캔버스에 표시가 필요하면 move_to_canvas: true

투자 분석에 필요한 PER, PBR, ROE 등 재무지표와 기술적 분석을 활용하여 실용적인 계획을 수립하세요."""
    
    def _get_default_plan_response(self, user_query: str) -> Dict[str, Any]:
        """기본 플랜 응답 생성"""
        return {
            "analysis": f"'{user_query}'에 대한 투자 분석 요청을 받았습니다. OpenAI API가 설정되지 않아 기본 계획을 제공합니다.",
            "plan_title": "기본 투자 분석 계획",
            "tasks": [
                {
                    "id": "data_collection",
                    "title": "데이터 수집",
                    "description": "필요한 투자 데이터를 수집합니다",
                    "agent_allowed": ["data_collector"],
                    "mcp_tools": ["stock_data_fetcher"],
                    "dependencies": [],
                    "estimated_time": "5분"
                },
                {
                    "id": "analysis",
                    "title": "분석 실행",
                    "description": "수집된 데이터를 바탕으로 투자 분석을 실행합니다",
                    "agent_allowed": ["financial_analyst"],
                    "mcp_tools": ["financial_analyzer", "technical_analyzer"],
                    "dependencies": ["data_collection"],
                    "estimated_time": "10분"
                },
                {
                    "id": "report_generation",
                    "title": "보고서 생성",
                    "description": "분석 결과를 종합하여 보고서를 생성합니다",
                    "agent_allowed": ["financial_analyst"],
                    "mcp_tools": [],
                    "dependencies": ["analysis"],
                    "estimated_time": "5분"
                }
            ],
            "clarification_questions": [
                {
                    "question": "분석하고자 하는 특정 종목이나 섹터가 있나요?",
                    "context": "더 정확한 분석을 위해 구체적인 대상이 필요합니다"
                },
                {
                    "question": "투자 기간과 목표 수익률은 어느 정도인가요?",
                    "context": "투자 전략 수립에 필요한 정보입니다"
                }
            ],
            "move_to_canvas": True,
            "priority": "medium",
            "complexity": "medium"
        }
    
    def _parse_and_validate_response(self, response: str) -> Dict[str, Any]:
        """AI 응답을 파싱하고 검증"""
        try:
            # JSON 블록 추출 (```json...``` 형태 처리)
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSON 블록이 없으면 전체 응답에서 JSON 파싱 시도
                json_str = response
            
            # JSON 파싱
            parsed = json.loads(json_str)
            
            # 필수 필드 검증 및 기본값 설정
            required_fields = {
                "analysis": "투자 분석 요청이 접수되었습니다.",
                "plan_title": "투자 분석 계획",
                "tasks": [],
                "clarification_questions": [],
                "move_to_canvas": True,
                "priority": "medium",
                "complexity": "medium"
            }
            
            for field, default_value in required_fields.items():
                if field not in parsed:
                    parsed[field] = default_value
            
            # tasks 배열 검증
            if not isinstance(parsed["tasks"], list):
                parsed["tasks"] = []
            
            # 각 task 검증
            for i, task in enumerate(parsed["tasks"]):
                if not isinstance(task, dict):
                    continue
                    
                # task 필수 필드 검증
                task_defaults = {
                    "id": f"task_{i+1}",
                    "title": f"작업 {i+1}",
                    "description": "작업 설명",
                    "agent_allowed": [],
                    "mcp_tools": [],
                    "dependencies": [],
                    "estimated_time": "예상 시간 미정"
                }
                
                for field, default_value in task_defaults.items():
                    if field not in task:
                        task[field] = default_value
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error("JSON 파싱 오류", error=str(e))
            raise
        except Exception as e:
            logger.error("응답 검증 오류", error=str(e))
            raise json.JSONDecodeError("응답 검증 실패", response, 0)

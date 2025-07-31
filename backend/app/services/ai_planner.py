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
            logger.info(f"OpenAI 클라이언트 초기화 완료. API 키: {self.api_key[:10]}...")
        else:
            logger.warning("OpenAI API 키가 설정되지 않았습니다")
        
    async def generate_plan_stream(self, user_query: str, mode: str = "conversation"):
        """사용자 쿼리를 분석하여 투자 분석 플랜 생성 (스트리밍)
        
        Args:
            user_query: 사용자 질문
            mode: "conversation" (대화식) 또는 "workflow" (워크플로우 변환)
        """
        logger.info("AI 플랜 생성 시작 (스트리밍)", query_length=len(user_query), mode=mode)
        
        # OpenAI 클라이언트가 없는 경우 기본 응답 반환
        if not self.client:
            logger.warning(f"OpenAI 클라이언트가 없음. API 키: {self.api_key}")
            default_response = self._get_default_plan_response(user_query, mode)
            yield {
                "type": "content",
                "content": json.dumps(default_response, ensure_ascii=False, indent=2),
            }
            return
        
        try:
            # 모드에 따른 시스템 프롬프트 선택
            if mode == "workflow":
                system_prompt = self._get_workflow_conversion_prompt()
            else:
                system_prompt = self._get_conversation_system_prompt()
            
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
            
            # JSON 파싱 시도 및 검증 (워크플로우 모드에서만)
            if mode == "workflow":
                try:
                    parsed_response = self._parse_and_validate_response(full_response)
                    logger.info(f"워크플로우 변환 성공: {parsed_response.get('workflow_title', 'Unknown')}")
                    yield {
                        "type": "done",
                        "full_response": json.dumps(parsed_response, ensure_ascii=False, indent=2)
                    }
                except json.JSONDecodeError as e:
                    # JSON 파싱 실패 시 원본 응답 로깅 후 기본 응답으로 fallback
                    logger.warning(f"JSON 파싱 실패: {str(e)}")
                    logger.warning(f"원본 응답 (처음 500자): {full_response[:500]}")
                    
                    # 사용자 요청 기반 맞춤형 기본 응답 생성
                    default_response = self._create_smart_default_workflow(user_query, mode)
                    yield {
                        "type": "done",
                        "full_response": json.dumps(default_response, ensure_ascii=False, indent=2)
                    }
            else:
                # 대화 모드에서는 JSON 파싱 없이 원본 응답 그대로 전달
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
    
    def _get_conversation_system_prompt(self) -> str:
        """대화식 플래닝용 시스템 프롬프트"""
        return """당신은 친근하고 전문적인 투자 분석 전문가입니다. 사용자의 투자 질문에 대해 구체적인 분석 태스크들을 제시해주세요.

**응답 방식**:
사용자의 질문을 분석한 후, 다음과 같은 형태로 답변해주세요:

"네, [사용자 요청 내용]에 대해 분석해드리겠습니다. 다음과 같은 태스크들을 진행하겠습니다:

1) [구체적인 태스크명] - [간단한 설명]
   - 에이전트: [사용할 에이전트]
   - 도구: [사용할 MCP 도구들]
   
2) [다음 태스크명] - [간단한 설명]
   - 에이전트: [사용할 에이전트]
   - 도구: [사용할 MCP 도구들]

... (필요한 만큼 계속)

이러한 분석을 통해 [최종 목표/결과물]을 제공해드리겠습니다."

**사용 가능한 에이전트들**:
- data_collector: 데이터 수집 전문
- financial_analyst: 재무 분석 전문  
- market_researcher: 시장 조사 전문
- risk_manager: 리스크 관리 전문
- portfolio_manager: 포트폴리오 관리 전문

**사용 가능한 MCP 도구들**:
- stock_data_fetcher: 주식 데이터 수집
- financial_analyzer: 재무제표 분석
- market_scanner: 시장 스캔
- risk_calculator: 리스크 분석
- portfolio_optimizer: 포트폴리오 최적화
- news_analyzer: 뉴스 분석
- technical_analyzer: 기술적 분석
- valuation_calculator: 기업가치 평가

**주의사항**:
- JSON이나 구조화된 코드 형태로 응답하지 마세요
- 자연스러운 텍스트로 태스크 리스트를 제시하세요
- 사용자의 구체적인 요청에 맞는 적절한 태스크들을 선별하세요
- 각 태스크마다 왜 필요한지 간단히 설명해주세요"""

    def _get_workflow_conversion_prompt(self) -> str:
        """워크플로우 변환용 시스템 프롬프트"""
        return """당신은 투자 분석 대화 내용을 워크플로우로 변환하는 전문가입니다.

**반드시 JSON 형식으로만 응답하세요. 다른 설명이나 텍스트는 포함하지 마세요.**

대화 내용을 분석하여 다음 JSON 형식으로 워크플로우를 생성하세요:

```json
{
  "workflow_title": "구체적인 워크플로우 제목",
  "description": "워크플로우 설명",
  "tasks": [
    {
      "id": "unique_task_id_1",
      "title": "작업 제목 (간단하게)",
      "description": "구체적인 작업 내용과 분석 방법",
      "agent_allowed": ["data_collector", "financial_analyst", "market_researcher"],
      "mcp_tools": ["stock_data_fetcher", "financial_analyzer"],
      "dependencies": [],
      "estimated_time": "5분",
      "output_type": "table"
    },
    {
      "id": "unique_task_id_2", 
      "title": "두 번째 작업",
      "description": "이전 작업 결과를 바탕으로 한 분석",
      "agent_allowed": ["financial_analyst"],
      "mcp_tools": ["technical_analyzer", "risk_calculator"],
      "dependencies": ["unique_task_id_1"],
      "estimated_time": "10분",
      "output_type": "report"
    }
  ],
  "expected_outcome": "최종 결과물 설명"
}
```

**사용 가능한 MCP 도구들**:
- "stock_data_fetcher": 주식 데이터 수집
- "financial_analyzer": 재무제표 분석  
- "market_scanner": 시장 스캔
- "risk_calculator": 리스크 분석
- "portfolio_optimizer": 포트폴리오 최적화
- "news_analyzer": 뉴스 분석
- "technical_analyzer": 기술적 분석
- "valuation_calculator": 기업가치 평가

**사용 가능한 Agent들**:
- "data_collector": 데이터 수집 전문
- "financial_analyst": 재무 분석 전문
- "market_researcher": 시장 조사 전문
- "risk_manager": 리스크 관리 전문
- "portfolio_manager": 포트폴리오 관리 전문

**중요**: 대화 내용에서 사용자가 구체적으로 요청한 분석 내용에 따라 적절한 작업들을 생성하세요. 
예시:
- 종목 분석 요청 → 데이터 수집 + 재무분석 + 기술적 분석
- 포트폴리오 구성 → 시장 스캔 + 리스크 분석 + 포트폴리오 최적화
- 섹터 분석 → 시장 조사 + 뉴스 분석 + 비교 분석

반드시 유효한 JSON만 응답하세요."""

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
    
    def _create_smart_default_workflow(self, user_query: str, mode: str = "workflow") -> Dict[str, Any]:
        """사용자 쿼리를 분석하여 스마트한 기본 워크플로우 생성"""
        query_lower = user_query.lower()
        
        # 키워드 기반 워크플로우 결정
        if any(keyword in query_lower for keyword in ['삼성', '애플', '테슬라', '네이버', '카카오', '종목', '주식', '기업']):
            # 개별 종목 분석 워크플로우
            return {
                "workflow_title": "개별 종목 투자 분석",
                "description": "특정 종목에 대한 종합적인 투자 분석을 수행합니다",
                "tasks": [
                    {
                        "id": "stock_data_collection",
                        "title": "종목 데이터 수집",
                        "description": "해당 종목의 주가, 재무제표, 거래량 등 기본 데이터를 수집합니다",
                        "agent_allowed": ["data_collector"],
                        "mcp_tools": ["stock_data_fetcher"],
                        "dependencies": [],
                        "estimated_time": "3분",
                        "output_type": "table"
                    },
                    {
                        "id": "fundamental_analysis",
                        "title": "기본적 분석",
                        "description": "PER, PBR, ROE 등 재무지표를 분석하고 기업 가치를 평가합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["financial_analyzer", "valuation_calculator"],
                        "dependencies": ["stock_data_collection"],
                        "estimated_time": "7분",
                        "output_type": "report"
                    },
                    {
                        "id": "technical_analysis",
                        "title": "기술적 분석",
                        "description": "차트 패턴, 이동평균, 거래량 등을 분석하여 매매 시점을 판단합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["technical_analyzer"],
                        "dependencies": ["stock_data_collection"],
                        "estimated_time": "5분",
                        "output_type": "chart"
                    },
                    {
                        "id": "investment_recommendation",
                        "title": "투자 의견 도출",
                        "description": "기본적 분석과 기술적 분석 결과를 종합하여 투자 의견을 제시합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["risk_calculator"],
                        "dependencies": ["fundamental_analysis", "technical_analysis"],
                        "estimated_time": "5분",
                        "output_type": "report"
                    }
                ],
                "expected_outcome": "종목별 투자 의견 및 목표가 제시"
            }
        
        elif any(keyword in query_lower for keyword in ['포트폴리오', '분산투자', '자산배분', '리밸런싱']):
            # 포트폴리오 분석 워크플로우
            return {
                "workflow_title": "포트폴리오 최적화 분석",
                "description": "투자 포트폴리오의 구성과 리스크를 분석하여 최적화 방안을 제시합니다",
                "tasks": [
                    {
                        "id": "market_scan",
                        "title": "시장 스캔",
                        "description": "투자 가능한 자산군과 종목들을 스캔하고 선별합니다",
                        "agent_allowed": ["market_researcher"],
                        "mcp_tools": ["market_scanner"],
                        "dependencies": [],
                        "estimated_time": "5분",
                        "output_type": "table"
                    },
                    {
                        "id": "risk_analysis",
                        "title": "리스크 분석",
                        "description": "각 자산의 변동성, 상관관계, VaR 등을 분석합니다",
                        "agent_allowed": ["risk_manager"],
                        "mcp_tools": ["risk_calculator"],
                        "dependencies": ["market_scan"],
                        "estimated_time": "8분",
                        "output_type": "report"
                    },
                    {
                        "id": "portfolio_optimization",
                        "title": "포트폴리오 최적화",
                        "description": "현대 포트폴리오 이론을 적용하여 최적 자산배분을 계산합니다",
                        "agent_allowed": ["portfolio_manager"],
                        "mcp_tools": ["portfolio_optimizer"],
                        "dependencies": ["risk_analysis"],
                        "estimated_time": "10분",
                        "output_type": "chart"
                    }
                ],
                "expected_outcome": "최적 포트폴리오 구성안 및 예상 수익률/리스크"
            }
        
        elif any(keyword in query_lower for keyword in ['섹터', '업종', '산업', '테마']):
            # 섹터/업종 분석 워크플로우
            return {
                "workflow_title": "섹터 및 업종 분석",
                "description": "특정 섹터나 업종의 투자 전망과 유망 종목을 분석합니다",
                "tasks": [
                    {
                        "id": "sector_research",
                        "title": "섹터 리서치",
                        "description": "해당 섹터의 시장 동향, 성장성, 경쟁 구조를 조사합니다",
                        "agent_allowed": ["market_researcher"],
                        "mcp_tools": ["market_scanner", "news_analyzer"],
                        "dependencies": [],
                        "estimated_time": "7분",
                        "output_type": "report"
                    },
                    {
                        "id": "sector_comparison",
                        "title": "섹터 내 기업 비교",
                        "description": "섹터 내 주요 기업들의 재무지표와 경쟁력을 비교 분석합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["financial_analyzer", "valuation_calculator"],
                        "dependencies": ["sector_research"],
                        "estimated_time": "10분",
                        "output_type": "table"
                    },
                    {
                        "id": "investment_ranking",
                        "title": "투자 매력도 순위",
                        "description": "분석 결과를 바탕으로 투자 매력도 순위를 매기고 추천 종목을 선별합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["risk_calculator"],
                        "dependencies": ["sector_comparison"],
                        "estimated_time": "5분",
                        "output_type": "report"
                    }
                ],
                "expected_outcome": "섹터 전망 및 추천 종목 리스트"
            }
        
        else:
            # 일반적인 투자 분석 워크플로우
            return {
                "workflow_title": "종합 투자 분석",
                "description": "투자 요청에 대한 종합적인 분석을 수행합니다",
                "tasks": [
                    {
                        "id": "data_collection",
                        "title": "데이터 수집",
                        "description": "투자 분석에 필요한 시장 데이터와 재무 정보를 수집합니다",
                        "agent_allowed": ["data_collector"],
                        "mcp_tools": ["stock_data_fetcher", "market_scanner"],
                        "dependencies": [],
                        "estimated_time": "5분",
                        "output_type": "table"
                    },
                    {
                        "id": "comprehensive_analysis",
                        "title": "종합 분석",
                        "description": "수집된 데이터를 바탕으로 기본적 분석과 기술적 분석을 수행합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["financial_analyzer", "technical_analyzer"],
                        "dependencies": ["data_collection"],
                        "estimated_time": "12분",
                        "output_type": "report"
                    },
                    {
                        "id": "risk_assessment",
                        "title": "리스크 평가",
                        "description": "투자 리스크를 평가하고 리스크 관리 방안을 제시합니다",
                        "agent_allowed": ["risk_manager"],
                        "mcp_tools": ["risk_calculator"],
                        "dependencies": ["comprehensive_analysis"],
                        "estimated_time": "6분",
                        "output_type": "report"
                    },
                    {
                        "id": "final_recommendation",
                        "title": "최종 투자 의견",
                        "description": "분석 결과를 종합하여 최종 투자 의견과 전략을 제시합니다",
                        "agent_allowed": ["portfolio_manager"],
                        "mcp_tools": [],
                        "dependencies": ["risk_assessment"],
                        "estimated_time": "5분",
                        "output_type": "report"
                    }
                ],
                "expected_outcome": "투자 의견 및 전략 제안서"
            }

    def _get_default_plan_response(self, user_query: str, mode: str = "conversation") -> Dict[str, Any]:
        """기본 플랜 응답 생성"""
        if mode == "workflow":
            return {
                "workflow_title": "기본 투자 분석 워크플로우",
                "description": f"'{user_query}'에 대한 투자 분석 워크플로우입니다.",
                "tasks": [
                    {
                        "id": "data_collection",
                        "title": "데이터 수집",
                        "description": "필요한 투자 데이터를 수집합니다",
                        "agent_allowed": ["data_collector"],
                        "mcp_tools": ["stock_data_fetcher"],
                        "dependencies": [],
                        "estimated_time": "5분",
                        "output_type": "table"
                    },
                    {
                        "id": "analysis",
                        "title": "데이터 분석",
                        "description": "수집된 데이터를 분석합니다",
                        "agent_allowed": ["financial_analyst"],
                        "mcp_tools": ["financial_analyzer"],
                        "dependencies": ["data_collection"],
                        "estimated_time": "10분",
                        "output_type": "report"
                    }
                ],
                "expected_outcome": "투자 분석 결과 보고서"
            }
        else:
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
            # 1. JSON 블록 추출 (```json...``` 형태 처리)
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                logger.info("JSON 블록을 찾았습니다")
            else:
                # 2. 중괄호로 둘러싸인 JSON 찾기
                brace_match = re.search(r'\{.*\}', response, re.DOTALL)
                if brace_match:
                    json_str = brace_match.group(0).strip()
                    logger.info("중괄호 JSON을 찾았습니다")
                else:
                    # 3. 전체 응답에서 JSON 파싱 시도
                    json_str = response.strip()
                    logger.info("전체 응답을 JSON으로 파싱 시도")
            
            # JSON 파싱
            parsed = json.loads(json_str)
            logger.info("JSON 파싱 성공")
            
            # 워크플로우 형식인지 확인
            if "workflow_title" in parsed or "tasks" in parsed:
                # 워크플로우 응답 검증
                return self._validate_workflow_response(parsed)
            else:
                # 일반 계획 응답 검증
                return self._validate_plan_response(parsed)
            
        except json.JSONDecodeError as e:
            logger.error("JSON 파싱 오류", error=str(e))
            logger.error(f"파싱 시도한 문자열 (처음 200자): {response[:200]}")
            raise
        except Exception as e:
            logger.error("응답 검증 오류", error=str(e))
            raise json.JSONDecodeError("응답 검증 실패", response, 0)

    def _validate_workflow_response(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 응답 검증 및 기본값 설정"""
        # 워크플로우 필수 필드 검증
        workflow_defaults = {
            "workflow_title": "투자 분석 워크플로우",
            "description": "투자 분석을 위한 워크플로우입니다",
            "tasks": [],
            "expected_outcome": "투자 분석 결과"
        }
        
        for field, default_value in workflow_defaults.items():
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
                "agent_allowed": ["financial_analyst"],
                "mcp_tools": ["stock_data_fetcher"],
                "dependencies": [],
                "estimated_time": "5분",
                "output_type": "table"
            }
            
            for field, default_value in task_defaults.items():
                if field not in task:
                    task[field] = default_value
        
        return parsed

    def _validate_plan_response(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """일반 계획 응답 검증 및 기본값 설정"""
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
        
        # tasks 배열 검증 (기존 로직과 동일)
        if not isinstance(parsed["tasks"], list):
            parsed["tasks"] = []
        
        for i, task in enumerate(parsed["tasks"]):
            if not isinstance(task, dict):
                continue
                
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

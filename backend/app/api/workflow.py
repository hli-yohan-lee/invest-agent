"""
워크플로우 관련 API 라우터  
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json
import openai

from app.core.database import get_db
from app.core.security import verify_token
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

class ToolSelectionRequest(BaseModel):
    node_description: str
    node_prompt: Optional[str] = ""
    workflow_context: List[Dict[str, Any]] = []
    openai_api_key: str

class AnalysisRequest(BaseModel):
    node_description: str
    tool_used: str
    raw_result: Dict[str, Any]
    openai_api_key: str

# 사용 가능한 MCP 도구 목록과 설명
AVAILABLE_TOOLS = {
    "get_all_tickers": {
        "description": "전체 종목 목록을 조회합니다. PER, PBR 등 기본 재무지표와 함께 정렬된 결과를 제공합니다.",
        "use_cases": ["종목 탐색", "시장 전체 현황", "재무지표 기반 초기 스크리닝"],
        "parameters": ["market (KOSPI/KOSDAQ/ALL)"]
    },
    "get_stock_fundamentals": {
        "description": "특정 종목의 상세 재무지표를 조회합니다.",
        "use_cases": ["개별 종목 분석", "재무 건전성 평가", "투자 가치 분석"],
        "parameters": ["ticker (종목코드)"]
    },
    "filter_stocks_by_fundamentals": {
        "description": "재무지표 조건으로 종목을 필터링합니다.",
        "use_cases": ["가치주 발굴", "성장주 탐색", "조건부 스크리닝"],
        "parameters": ["tickers", "per_max", "pbr_max", "roe_min", "market_cap_min", "limit"]
    },
    "get_market_news": {
        "description": "특정 종목이나 섹터의 최신 뉴스를 조회합니다.",
        "use_cases": ["뉴스 분석", "시장 동향 파악", "리스크 요인 분석"],
        "parameters": ["tickers", "sector", "days"]
    },
    "get_sector_performance": {
        "description": "특정 섹터의 성과를 분석합니다.",
        "use_cases": ["섹터 분석", "업종별 투자 전략", "상대적 성과 비교"],
        "parameters": ["sector", "period"]
    },
    "get_foreign_investment": {
        "description": "외국인 투자 동향을 조회합니다.",
        "use_cases": ["외국인 자금 흐름 분석", "시장 심리 파악"],
        "parameters": ["market"]
    },
    "get_market_cap": {
        "description": "시가총액 관련 정보를 조회합니다.",
        "use_cases": ["시장 규모 분석", "대형주/중형주/소형주 분류"],
        "parameters": ["market"]
    }
}

@router.get("/")
async def get_workflows(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 목록 조회"""
    user_id = token_data.get("user_id")
    return {"message": "워크플로우 목록", "user_id": user_id}

@router.post("/")
async def create_workflow(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """새 워크플로우 생성"""
    user_id = token_data.get("user_id")
    return {"message": "워크플로우 생성", "user_id": user_id}

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 상세 조회"""
    user_id = token_data.get("user_id")
    return {"message": f"워크플로우 {workflow_id} 조회", "user_id": user_id}

@router.put("/{workflow_id}")
async def update_workflow(
    workflow_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 업데이트"""
    user_id = token_data.get("user_id")
    return {"message": f"워크플로우 {workflow_id} 업데이트", "user_id": user_id}

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """워크플로우 실행"""
    user_id = token_data.get("user_id")
    return {"message": f"워크플로우 {workflow_id} 실행", "user_id": user_id}

@router.post("/tool-selection")
async def select_tool(
    request: ToolSelectionRequest,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """동적 도구 선택"""
    user_id = token_data.get("user_id")
    logger.info(f"사용자 {user_id}에 의해 도구 선택 요청됨: {request.json()}")
    
    # OpenAI API를 사용한 도구 선택 로직 추가 필요
    selected_tool = "get_all_tickers"  # 예시: 기본 도구로 전체 종목 조회
    tool_description = AVAILABLE_TOOLS.get(selected_tool, {}).get("description", "설명 없음")
    
    return {
        "message": "도구 선택 완료",
        "user_id": user_id,
        "selected_tool": selected_tool,
        "tool_description": tool_description
    }

@router.post("/select-tool")
async def select_appropriate_tool(request: ToolSelectionRequest):
    """
    노드 설명과 워크플로우 컨텍스트를 바탕으로 적절한 MCP 도구를 선택합니다.
    """
    try:
        # OpenAI API 키 설정
        openai.api_key = request.openai_api_key
        
        # 워크플로우 컨텍스트 분석
        workflow_context_str = "\n".join([
            f"- {node['label']} (상태: {node.get('status', 'pending')})"
            for node in request.workflow_context
        ])
        
        # 도구 선택을 위한 프롬프트
        tool_selection_prompt = f"""
당신은 투자 분석 워크플로우의 AI 어시스턴트입니다.
현재 실행해야 할 노드와 전체 워크플로우 컨텍스트를 바탕으로 가장 적절한 MCP 도구를 선택해주세요.

**현재 노드:**
- 설명: {request.node_description}
- 프롬프트: {request.node_prompt}

**전체 워크플로우 컨텍스트:**
{workflow_context_str}

**사용 가능한 도구들:**
{json.dumps(AVAILABLE_TOOLS, ensure_ascii=False, indent=2)}

**응답 형식 (JSON):**
{{
    "tool_name": "선택한_도구명",
    "reasoning": "선택 이유 설명",
    "parameters": {{
        "parameter1": "value1",
        "parameter2": "value2"
    }}
}}

주의사항:
1. 노드의 목적에 가장 적합한 도구를 선택하세요
2. 워크플로우의 순서와 이전 단계 결과를 고려하세요
3. 매개변수는 노드의 컨텍스트에 맞게 설정하세요
4. 뉴스 분석이 필요하면 get_market_news를, 재무 분석이 필요하면 get_stock_fundamentals나 filter_stocks_by_fundamentals를 사용하세요
"""

        # OpenAI 클라이언트 생성
        client = openai.OpenAI(api_key=request.openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 투자 분석 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": tool_selection_prompt}
            ],
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON 추출 시도
        try:
            # JSON 블록에서 추출
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            result = json.loads(result_text)
            
            # 도구명 검증
            if result.get("tool_name") not in AVAILABLE_TOOLS:
                logger.warning(f"Unknown tool selected: {result.get('tool_name')}")
                # 기본 도구로 fallback
                result["tool_name"] = "get_all_tickers"
                result["parameters"] = {"market": "ALL"}
                result["reasoning"] = "알 수 없는 도구가 선택되어 기본 도구로 fallback"
            
            logger.info(f"Selected tool: {result['tool_name']} for node: {request.node_description}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            # 기본 도구로 fallback
            return {
                "tool_name": "get_all_tickers",
                "parameters": {"market": "ALL"},
                "reasoning": "JSON 파싱 실패로 기본 도구 선택"
            }
        
    except Exception as e:
        logger.error(f"Tool selection failed: {e}")
        raise HTTPException(status_code=500, detail=f"도구 선택 실패: {str(e)}")

@router.post("/analysis")
async def analyze_result(
    request: AnalysisRequest,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """결과 분석"""
    user_id = token_data.get("user_id")
    logger.info(f"사용자 {user_id}에 의해 결과 분석 요청됨: {request.json()}")
    
    # OpenAI API를 사용한 결과 분석 로직 추가 필요
    analysis_result = {"summary": "분석 결과 요약", "details": "자세한 분석 내용"}
    
    return {
        "message": "결과 분석 완료",
        "user_id": user_id,
        "analysis_result": analysis_result
    }

@router.post("/analyze-result")
async def analyze_tool_result(request: AnalysisRequest):
    """
    MCP 도구 실행 결과를 AI가 분석하고 해석합니다.
    """
    try:
        # OpenAI API 키 설정
        openai.api_key = request.openai_api_key
        
        # 결과 분석을 위한 프롬프트
        analysis_prompt = f"""
당신은 투자 분석 전문가입니다.
다음 MCP 도구 실행 결과를 분석하고 투자자가 이해하기 쉽게 해석해주세요.

**노드 목적:** {request.node_description}
**사용된 도구:** {request.tool_used}
**원시 데이터:** {json.dumps(request.raw_result, ensure_ascii=False, indent=2)}

**분석 요청사항:**
1. 데이터의 핵심 인사이트 추출
2. 투자 관점에서의 해석
3. 주목할 만한 종목이나 패턴 식별
4. 다음 분석 단계 제안

**응답 형식:**
명확하고 구조화된 한국어로 작성해주세요.
- 핵심 요약 (2-3문장)
- 주요 발견사항 (불릿 포인트)
- 투자 시사점
- 추천 후속 조치

길이는 200-500자 정도로 간결하게 작성해주세요.
"""

        # OpenAI 클라이언트 생성
        client = openai.OpenAI(api_key=request.openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 투자 분석 전문가입니다. 데이터를 명확하고 실용적으로 해석하세요."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content.strip()
        
        logger.info(f"Analysis completed for tool: {request.tool_used}")
        
        return {
            "analysis": analysis,
            "tool_used": request.tool_used,
            "data_summary": f"{request.tool_used} 도구로 {len(str(request.raw_result))} 바이트의 데이터 처리"
        }
        
    except Exception as e:
        logger.error(f"Result analysis failed: {e}")
        
        # 기본 분석 제공
        return {
            "analysis": f"""
**{request.node_description} 분석 결과**

{request.tool_used} 도구를 사용하여 데이터를 수집했습니다.

• 데이터 크기: {len(str(request.raw_result))} 바이트
• 처리 상태: 완료
• 다음 단계: 추가 분석이나 다른 도구를 활용한 심화 분석을 권장합니다.

*자동 생성된 기본 분석입니다. 상세한 분석을 위해 AI 분석을 다시 시도해보세요.*
            """,
            "tool_used": request.tool_used,
            "data_summary": "기본 분석 모드"
        }

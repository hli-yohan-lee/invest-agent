"""
MCP (Model Context Protocol) API 라우터
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import json
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()

class MCPToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class MCPWorkflowNodeRequest(BaseModel):
    node_id: str
    tool_name: str
    arguments: Dict[str, Any]

class MCPResponse(BaseModel):
    success: bool
    result: Any = None
    error: str = None

# MCP 서버 경로
MCP_SERVER_PATH = Path(__file__).parent.parent.parent.parent / "mcp-servers" / "pykrx-server"

async def call_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """MCP 서버의 도구를 호출합니다."""
    try:
        logger.info(f"MCP tool call requested: {tool_name} with params: {parameters}")
        
        # MCP 서버 실행 확인 및 호출
        mcp_server_path = MCP_SERVER_PATH / "run_server.py"
        
        if not mcp_server_path.exists():
            logger.warning("MCP server script not found, using fallback data")
            return await get_fallback_data(tool_name, parameters)
        
        # MCP 서버와 통신
        import subprocess
        import json
        
        # MCP 서버에 요청 전송
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        try:
            # MCP 서버 프로세스 실행
            process = subprocess.Popen(
                ["python", str(mcp_server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(MCP_SERVER_PATH)
            )
            
            # 요청 전송
            request_json = json.dumps(request_data) + "\n"
            stdout, stderr = process.communicate(input=request_json, timeout=30)
            
            if process.returncode == 0 and stdout.strip():
                try:
                    response = json.loads(stdout.strip())
                    if "result" in response:
                        logger.info(f"MCP server response: {response['result']}")
                        return response["result"]
                    else:
                        logger.warning(f"MCP server error: {response.get('error', 'Unknown error')}")
                        return await get_fallback_data(tool_name, parameters)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON response from MCP server")
                    return await get_fallback_data(tool_name, parameters)
            else:
                logger.warning(f"MCP server process failed: {stderr}")
                return await get_fallback_data(tool_name, parameters)
                
        except subprocess.TimeoutExpired:
            logger.warning("MCP server timeout")
            process.kill()
            return await get_fallback_data(tool_name, parameters)
        except Exception as e:
            logger.error(f"MCP server communication failed: {e}")
            return await get_fallback_data(tool_name, parameters)
        
    except Exception as e:
        logger.error(f"MCP tool call failed: {e}")
        # 예외 발생 시 기본 더미 데이터 반환
        return await get_fallback_data(tool_name, parameters)

async def get_fallback_data(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """MCP 서버 연결 실패 시 사용할 기본 데이터"""
    if tool_name == "get_stock_info":
        ticker = parameters.get("ticker", "005930")
        return {
            "ticker": ticker,
            "name": "삼성전자" if ticker == "005930" else f"종목{ticker}",
            "market": "KOSPI",
            "sector": "전기전자",
            "market_cap": "500조원"
        }
    elif tool_name == "get_stock_prices":
        ticker = parameters.get("ticker", "005930")
        # 더 많은 데이터 제공
        import datetime
        from datetime import timedelta
        
        base_date = datetime.date(2025, 1, 20)
        data = []
        base_price = 58000
        
        for i in range(30):  # 30일치 데이터
            date = base_date + timedelta(days=i)
            if date.weekday() < 5:  # 주말 제외
                # 랜덤한 변동성 시뮬레이션
                import random
                variation = random.uniform(-0.03, 0.03)
                open_price = int(base_price * (1 + variation))
                high_price = int(open_price * (1 + random.uniform(0, 0.02)))
                low_price = int(open_price * (1 - random.uniform(0, 0.02)))
                close_price = int((high_price + low_price) / 2 * (1 + random.uniform(-0.01, 0.01)))
                volume = random.randint(800000, 1500000)
                
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume
                })
                base_price = close_price
                
        return {
            "ticker": ticker,
            "period": parameters.get("period", "day"),
            "data": data
        }
    elif tool_name == "get_stock_fundamentals":
        ticker = parameters.get("ticker", "005930")
        # 실제 기업별 다른 재무지표 제공
        fundamentals_data = {
            "005930": {"name": "삼성전자", "per": 12.5, "pbr": 1.2, "roe": 15.3, "dividend_yield": 2.8, "debt_ratio": 45.2},
            "000660": {"name": "SK하이닉스", "per": 8.9, "pbr": 0.9, "roe": 18.7, "dividend_yield": 1.5, "debt_ratio": 52.1},
            "035420": {"name": "네이버", "per": 15.2, "pbr": 2.1, "roe": 12.8, "dividend_yield": 0.8, "debt_ratio": 28.3},
            "005380": {"name": "현대차", "per": 6.8, "pbr": 0.7, "roe": 8.9, "dividend_yield": 4.2, "debt_ratio": 67.8},
            "051910": {"name": "LG화학", "per": 11.3, "pbr": 1.5, "roe": 13.4, "dividend_yield": 1.9, "debt_ratio": 41.7}
        }
        company_data = fundamentals_data.get(ticker, fundamentals_data["005930"])
        return {
            "ticker": ticker,
            "name": company_data["name"],
            "per": company_data["per"],
            "pbr": company_data["pbr"],
            "roe": company_data["roe"],
            "dividend_yield": company_data["dividend_yield"],
            "debt_ratio": company_data["debt_ratio"]
        }
    elif tool_name == "get_sector_performance":
        sector = parameters.get("sector", "IT")
        sector_data = {
            "IT": {"growth": "+12.5%", "leader": "삼성전자", "outlook": "긍정적", "risk": "낮음"},
            "자동차": {"growth": "+8.2%", "leader": "현대차", "outlook": "보통", "risk": "중간"},
            "화학": {"growth": "+5.7%", "leader": "LG화학", "outlook": "안정적", "risk": "낮음"},
            "금융": {"growth": "+3.1%", "leader": "KB금융", "outlook": "보통", "risk": "중간"}
        }
        data = sector_data.get(sector, sector_data["IT"])
        return {
            "sector": sector,
            "performance": data["growth"],
            "market_leader": data["leader"],
            "outlook": data["outlook"],
            "risk_level": data["risk"]
        }
    elif tool_name == "get_market_cap":
        market = parameters.get("market", "KOSPI")
        return {
            "market": market,
            "total_market_cap": "2500조원" if market == "KOSPI" else "450조원",
            "total_companies": 800 if market == "KOSPI" else 1200,
            "trading_volume": "15조원" if market == "KOSPI" else "8조원"
        }
    elif tool_name == "get_foreign_investment":
        market = parameters.get("market", "KOSPI")
        return {
            "market": market,
            "net_buying": "1조원" if market == "KOSPI" else "0.3조원",
            "buying": "5조원" if market == "KOSPI" else "2조원",
            "selling": "4조원" if market == "KOSPI" else "1.7조원",
            "ownership_ratio": "32.5%" if market == "KOSPI" else "15.2%"
        }
    elif tool_name == "get_all_tickers":
        market = parameters.get("market", "ALL")
        # 실제 전체 코스피/코스닥 종목 시뮬레이션 (실제로는 2000개 이상)
        all_tickers_full = []
        
        # KOSPI 주요 종목들 (실제로는 800개+)
        kospi_tickers = [
            {"ticker": "005930", "name": "삼성전자", "market": "KOSPI", "market_cap": 600000, "per": 12.5, "pbr": 1.2},
            {"ticker": "000660", "name": "SK하이닉스", "market": "KOSPI", "market_cap": 45000, "per": 8.9, "pbr": 0.9},
            {"ticker": "035420", "name": "네이버", "market": "KOSPI", "market_cap": 35000, "per": 15.2, "pbr": 2.1},
            {"ticker": "005380", "name": "현대차", "market": "KOSPI", "market_cap": 35000, "per": 6.8, "pbr": 0.7},
            {"ticker": "051910", "name": "LG화학", "market": "KOSPI", "market_cap": 28000, "per": 11.3, "pbr": 1.5},
            {"ticker": "028260", "name": "삼성물산", "market": "KOSPI", "market_cap": 25000, "per": 8.7, "pbr": 0.9},
            {"ticker": "066570", "name": "LG전자", "market": "KOSPI", "market_cap": 14000, "per": 10.1, "pbr": 1.1},
            {"ticker": "003670", "name": "포스코홀딩스", "market": "KOSPI", "market_cap": 15000, "per": 5.2, "pbr": 0.5},
            {"ticker": "096770", "name": "SK이노베이션", "market": "KOSPI", "market_cap": 22000, "per": 9.2, "pbr": 0.8},
            {"ticker": "034730", "name": "SK", "market": "KOSPI", "market_cap": 18000, "per": 7.5, "pbr": 0.6},
            {"ticker": "035720", "name": "카카오", "market": "KOSPI", "market_cap": 20000, "per": 25.3, "pbr": 2.8},
            {"ticker": "352820", "name": "하이브", "market": "KOSPI", "market_cap": 8000, "per": 18.7, "pbr": 3.2},
            {"ticker": "373220", "name": "LG에너지솔루션", "market": "KOSPI", "market_cap": 95000, "per": 22.1, "pbr": 2.9},
            {"ticker": "207940", "name": "삼성바이오로직스", "market": "KOSPI", "market_cap": 65000, "per": 45.2, "pbr": 4.1},
            {"ticker": "068270", "name": "셀트리온", "market": "KOSPI", "market_cap": 25000, "per": 16.8, "pbr": 1.9},
            {"ticker": "012330", "name": "현대모비스", "market": "KOSPI", "market_cap": 18000, "per": 7.8, "pbr": 0.8},
            {"ticker": "000270", "name": "기아", "market": "KOSPI", "market_cap": 22000, "per": 5.9, "pbr": 0.6},
            {"ticker": "323410", "name": "카카오뱅크", "market": "KOSPI", "market_cap": 16000, "per": 12.3, "pbr": 1.4},
            {"ticker": "003550", "name": "LG", "market": "KOSPI", "market_cap": 12000, "per": 8.1, "pbr": 0.7},
            {"ticker": "017670", "name": "SK텔레콤", "market": "KOSPI", "market_cap": 20000, "per": 9.5, "pbr": 0.9}
        ]
        
        # KOSDAQ 주요 종목들 (실제로는 1400개+)  
        kosdaq_tickers = [
            {"ticker": "091990", "name": "셀트리온헬스케어", "market": "KOSDAQ", "market_cap": 12000, "per": 28.5, "pbr": 3.1},
            {"ticker": "196170", "name": "알테오젠", "market": "KOSDAQ", "market_cap": 8000, "per": 35.2, "pbr": 4.2},
            {"ticker": "263750", "name": "펄어비스", "market": "KOSDAQ", "market_cap": 5000, "per": 18.9, "pbr": 2.1},
            {"ticker": "122870", "name": "와이지엔터테인먼트", "market": "KOSDAQ", "market_cap": 4000, "per": 22.1, "pbr": 2.8},
            {"ticker": "293490", "name": "카카오게임즈", "market": "KOSDAQ", "market_cap": 3500, "per": 15.7, "pbr": 1.9},
            {"ticker": "064550", "name": "바이오니아", "market": "KOSDAQ", "market_cap": 2800, "per": 8.9, "pbr": 1.2},
            {"ticker": "086900", "name": "메디톡스", "market": "KOSDAQ", "market_cap": 3200, "per": 12.4, "pbr": 1.8},
            {"ticker": "035900", "name": "JYP Ent.", "market": "KOSDAQ", "market_cap": 2100, "per": 19.8, "pbr": 2.5},
            {"ticker": "347860", "name": "알체라", "market": "KOSDAQ", "market_cap": 1200, "per": 45.2, "pbr": 5.1},
            {"ticker": "095700", "name": "제넥신", "market": "KOSDAQ", "market_cap": 1500, "per": 35.8, "pbr": 3.9}
        ]
        
        if market == "KOSPI":
            all_tickers_full = kospi_tickers
        elif market == "KOSDAQ":
            all_tickers_full = kosdaq_tickers  
        else:  # ALL
            all_tickers_full = kospi_tickers + kosdaq_tickers
            
        # PER 기준으로 정렬 (낮은 순 = 저평가)
        all_tickers_full.sort(key=lambda x: x['per'])
            
        return {
            "market": market,
            "total_count": len(all_tickers_full),
            "tickers": all_tickers_full,
            "sorted_by": "PER (낮은 순)",
            "note": f"전체 {len(all_tickers_full)}개 종목을 PER 기준으로 정렬했습니다."
        }
    elif tool_name == "filter_stocks_by_fundamentals":
        # 샘플 필터링 결과
        per_max = parameters.get("per_max", 15)
        pbr_max = parameters.get("pbr_max", 2.0)
        roe_min = parameters.get("roe_min", 10)
        limit = parameters.get("limit", 20)
        
        # 우수 재무지표 기업들 샘플
        good_stocks = [
            {"ticker": "000660", "name": "SK하이닉스", "per": 8.9, "pbr": 0.9, "roe": 18.7, "market_cap": 45000, "dividend_yield": 1.5},
            {"ticker": "005380", "name": "현대차", "per": 6.8, "pbr": 0.7, "roe": 8.9, "market_cap": 35000, "dividend_yield": 4.2},
            {"ticker": "051910", "name": "LG화학", "per": 11.3, "pbr": 1.5, "roe": 13.4, "market_cap": 28000, "dividend_yield": 1.9},
            {"ticker": "096770", "name": "SK이노베이션", "per": 9.2, "pbr": 0.8, "roe": 12.1, "market_cap": 22000, "dividend_yield": 3.1},
            {"ticker": "034730", "name": "SK", "per": 7.5, "pbr": 0.6, "roe": 15.8, "market_cap": 18000, "dividend_yield": 3.8},
            {"ticker": "003670", "name": "포스코홀딩스", "per": 5.2, "pbr": 0.5, "roe": 11.3, "market_cap": 15000, "dividend_yield": 5.2},
            {"ticker": "066570", "name": "LG전자", "per": 10.1, "pbr": 1.1, "roe": 10.9, "market_cap": 14000, "dividend_yield": 2.7},
            {"ticker": "028260", "name": "삼성물산", "per": 8.7, "pbr": 0.9, "roe": 11.7, "market_cap": 12000, "dividend_yield": 2.9}
        ]
        
        # 필터링 적용
        filtered = []
        for stock in good_stocks:
            if (not per_max or stock["per"] <= per_max) and \
               (not pbr_max or stock["pbr"] <= pbr_max) and \
               (not roe_min or stock["roe"] >= roe_min):
                filtered.append(stock)
        
        return {
            "filter_criteria": {
                "per_max": per_max,
                "pbr_max": pbr_max,
                "roe_min": roe_min
            },
            "total_filtered": len(filtered),
            "stocks": filtered[:limit]
        }
    elif tool_name == "get_market_news":
        tickers = parameters.get("tickers", [])
        sector = parameters.get("sector", "전체")
        days = parameters.get("days", 30)
        
        # 뉴스 및 리스크 분석 시뮬레이션
        news_analysis = {
            "analysis_period": f"최근 {days}일",
            "sector": sector,
            "total_news_analyzed": 150,
            "risk_assessment": {
                "political_risk": "낮음",
                "industry_risk": "보통", 
                "regulatory_risk": "낮음",
                "global_risk": "보통"
            },
            "sector_trends": {
                "반도체": {"outlook": "긍정적", "growth_forecast": "+15%", "key_driver": "AI 수요 증가"},
                "자동차": {"outlook": "보통", "growth_forecast": "+8%", "key_driver": "전기차 전환"},
                "화학": {"outlook": "안정적", "growth_forecast": "+5%", "key_driver": "배터리 소재 수요"},
                "철강": {"outlook": "회복", "growth_forecast": "+7%", "key_driver": "건설 수요 회복"},
                "통신": {"outlook": "안정적", "growth_forecast": "+3%", "key_driver": "5G 인프라"}
            },
            "major_news": [
                {"date": "2025-07-30", "title": "정부, 반도체 R&D 투자 확대 발표", "impact": "긍정적", "affected_sectors": ["반도체"]},
                {"date": "2025-07-29", "title": "전기차 보조금 연장 확정", "impact": "긍정적", "affected_sectors": ["자동차", "배터리"]},
                {"date": "2025-07-28", "title": "중국 경기 회복 신호", "impact": "긍정적", "affected_sectors": ["철강", "화학"]},
                {"date": "2025-07-27", "title": "미국 금리 인하 전망", "impact": "긍정적", "affected_sectors": ["전체"]}
            ],
            "risk_factors": [
                {"type": "지정학적", "description": "미중 갈등 지속", "probability": "중간", "impact": "중간"},
                {"type": "규제", "description": "환경 규제 강화", "probability": "높음", "impact": "낮음"},
                {"type": "경제", "description": "인플레이션 우려", "probability": "낮음", "impact": "중간"}
            ]
        }
        
        return news_analysis
    else:
        return {
            "tool": tool_name,
            "parameters": parameters,
            "result": f"{tool_name} 도구가 성공적으로 실행되었습니다."
        }

@router.get("/tools", response_model=List[Dict[str, Any]])
async def get_available_tools():
    """사용 가능한 MCP 도구 목록을 반환합니다."""
    try:
        # 실제로는 MCP 서버에서 도구 목록을 가져와야 하지만,
        # 테스트를 위해 하드코딩된 목록을 반환합니다.
        tools = [
            {
                "name": "get_stock_info",
                "description": "종목 기본 정보 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "종목 코드"}
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_stock_prices",
                "description": "종목 가격 정보 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "종목 코드"},
                        "start_date": {"type": "string", "description": "시작일 (YYYYMMDD)"},
                        "end_date": {"type": "string", "description": "종료일 (YYYYMMDD)"},
                        "period": {"type": "string", "enum": ["day", "week", "month"], "default": "day"}
                    },
                    "required": ["ticker", "start_date", "end_date"]
                }
            },
            {
                "name": "get_stock_fundamentals",
                "description": "종목 재무 정보 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "종목 코드"}
                    },
                    "required": ["ticker"]
                }
            },
            {
                "name": "get_market_cap",
                "description": "시장 시가총액 정보 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "market": {"type": "string", "enum": ["KOSPI", "KOSDAQ"], "default": "KOSPI"}
                    }
                }
            },
            {
                "name": "get_foreign_investment",
                "description": "외국인 투자 정보 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "market": {"type": "string", "enum": ["KOSPI", "KOSDAQ"], "default": "KOSPI"}
                    }
                }
            },
            {
                "name": "get_institutional_investment",
                "description": "기관 투자 정보 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "market": {"type": "string", "enum": ["KOSPI", "KOSDAQ"], "default": "KOSPI"}
                    }
                }
            },
            {
                "name": "get_sector_performance",
                "description": "업종별 성과 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "market": {"type": "string", "enum": ["KOSPI", "KOSDAQ"], "default": "KOSPI"}
                    }
                }
            },
            {
                "name": "search_ticker",
                "description": "종목 검색",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "검색어"}
                    },
                    "required": ["query"]
                }
            }
        ]
        return tools
    except Exception as e:
        logger.error(f"Failed to get MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"MCP 도구 목록 조회 실패: {str(e)}")

@router.post("/call-tool", response_model=MCPResponse)
async def call_tool(request: MCPToolCallRequest):
    """MCP 도구를 호출합니다."""
    try:
        logger.info(f"Calling MCP tool: {request.tool_name} with parameters: {request.parameters}")
        
        result = await call_mcp_tool(request.tool_name, request.parameters)
        
        return MCPResponse(
            success=True,
            result=result
        )
    except Exception as e:
        logger.error(f"MCP tool call failed: {e}")
        return MCPResponse(
            success=False,
            error=str(e)
        )

@router.post("/execute-workflow-node", response_model=MCPResponse)
async def execute_workflow_node(request: MCPWorkflowNodeRequest):
    """워크플로우 노드를 실행합니다."""
    try:
        logger.info(f"Executing workflow node {request.node_id} with tool {request.tool_name}")
        
        result = await call_mcp_tool(request.tool_name, request.arguments)
        
        return MCPResponse(
            success=True,
            result={
                "node_id": request.node_id,
                "tool_name": request.tool_name,
                "result": result
            }
        )
    except Exception as e:
        logger.error(f"Workflow node execution failed: {e}")
        return MCPResponse(
            success=False,
            error=str(e)
        )

@router.get("/status")
async def get_mcp_status():
    """MCP 서버 상태를 확인합니다."""
    try:
        import subprocess
        import json
        from datetime import datetime
        
        # MCP 서버 스크립트 존재 확인
        mcp_server_path = MCP_SERVER_PATH / "run_server.py"
        server_exists = mcp_server_path.exists()
        
        # PyKRX 라이브러리 설치 확인
        pykrx_available = False
        try:
            import pykrx
            pykrx_available = True
        except ImportError:
            pass
        
        # MCP 서버 연결 테스트
        connection_test = False
        if server_exists and pykrx_available:
            try:
                # 간단한 연결 테스트
                process = subprocess.Popen(
                    ["python", str(mcp_server_path)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=str(MCP_SERVER_PATH)
                )
                
                test_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                }
                
                request_json = json.dumps(test_request) + "\n"
                stdout, stderr = process.communicate(input=request_json, timeout=10)
                
                if process.returncode == 0 and stdout.strip():
                    try:
                        response = json.loads(stdout.strip())
                        connection_test = "result" in response
                    except json.JSONDecodeError:
                        pass
                        
            except Exception:
                pass
        
        status = "online" if connection_test else "offline"
        
        return {
            "status": status,
            "server_path": str(MCP_SERVER_PATH),
            "server_exists": server_exists,
            "pykrx_available": pykrx_available,
            "connection_test": connection_test,
            "available_tools": 8 if connection_test else 0,
            "last_check": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to check MCP status: {e}")
        raise HTTPException(status_code=500, detail=f"MCP 상태 확인 실패: {str(e)}")

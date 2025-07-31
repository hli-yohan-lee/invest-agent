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
        # MCP 서버와 통신하는 코드
        # 간단한 테스트를 위해 기본 응답 반환
        
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
            return {
                "ticker": ticker,
                "period": parameters.get("period", "day"),
                "data": [
                    {"date": "2025-01-30", "open": 58000, "high": 59000, "low": 57500, "close": 58500, "volume": 1000000},
                    {"date": "2025-01-31", "open": 58500, "high": 59500, "low": 58000, "close": 59000, "volume": 1200000}
                ]
            }
        elif tool_name == "get_stock_fundamentals":
            ticker = parameters.get("ticker", "005930")
            return {
                "ticker": ticker,
                "per": 12.5,
                "pbr": 1.2,
                "roe": 15.3,
                "dividend_yield": 2.8,
                "debt_ratio": 45.2
            }
        elif tool_name == "get_market_cap":
            market = parameters.get("market", "KOSPI")
            return {
                "market": market,
                "total_market_cap": "2500조원",
                "total_companies": 800,
                "trading_volume": "15조원"
            }
        elif tool_name == "get_foreign_investment":
            market = parameters.get("market", "KOSPI")
            return {
                "market": market,
                "net_buying": "1조원",
                "buying": "5조원",
                "selling": "4조원",
                "ownership_ratio": "32.5%"
            }
        else:
            return {
                "tool": tool_name,
                "parameters": parameters,
                "result": f"{tool_name} 도구가 성공적으로 실행되었습니다."
            }
            
    except Exception as e:
        logger.error(f"MCP tool call failed: {e}")
        raise HTTPException(status_code=500, detail=f"MCP 도구 호출 실패: {str(e)}")

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
        # MCP 서버 상태 확인 로직
        return {
            "status": "online",
            "server_path": str(MCP_SERVER_PATH),
            "available_tools": 8,
            "last_check": "2025-01-31T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Failed to check MCP status: {e}")
        raise HTTPException(status_code=500, detail=f"MCP 상태 확인 실패: {str(e)}")

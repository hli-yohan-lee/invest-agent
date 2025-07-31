#!/usr/bin/env python3
"""
간단한 PyKRX MCP 서버
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, List
import traceback
import pandas as pd

# pykrx import
try:
    import pykrx.stock as stock
    PYKRX_AVAILABLE = True
except ImportError:
    PYKRX_AVAILABLE = False

import pandas as pd

# MCP 라이브러리 
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 서버 초기화
app = Server("pykrx-server")

def format_date(date_str: str) -> str:
    """날짜를 YYYYMMDD 형식으로 변환"""
    if not date_str:
        return datetime.now().strftime("%Y%m%d")
    return date_str.replace("-", "").replace("/", "")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """사용 가능한 도구 목록"""
    return [
        Tool(
            name="get_market_tickers",
            description="특정 시장의 모든 종목 코드를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "description": "시장 구분: KOSPI, KOSDAQ, KONEX",
                        "enum": ["KOSPI", "KOSDAQ", "KONEX"]
                    },
                    "date": {
                        "type": "string", 
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)",
                        "default": ""
                    }
                },
                "required": ["market"]
            }
        ),
        Tool(
            name="get_ticker_name",
            description="종목 코드로 종목명을 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "종목 코드 (예: 005930)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_stock_ohlcv",
            description="종목의 OHLCV 데이터를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "종목 코드"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "시작일 (YYYYMMDD 형식)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "종료일 (YYYYMMDD 형식, 기본값: 오늘)",
                        "default": ""
                    }
                },
                "required": ["ticker", "start_date"]
            }
        ),
        Tool(
            name="search_stocks",
            description="종목명으로 종목을 검색합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "검색할 종목명 키워드"
                    },
                    "market": {
                        "type": "string",
                        "description": "시장 구분 (ALL, KOSPI, KOSDAQ, KONEX)",
                        "enum": ["ALL", "KOSPI", "KOSDAQ", "KONEX"],
                        "default": "ALL"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_market_fundamental",
            description="특정 날짜의 시장 전체 기본적 분석 데이터 (PER, PBR, 배당수익률 등)를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)"
                    },
                    "market": {
                        "type": "string",
                        "description": "시장 구분",
                        "enum": ["KOSPI", "KOSDAQ"],
                        "default": "KOSPI"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_market_cap",
            description="특정 날짜의 시가총액 정보를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)"
                    },
                    "market": {
                        "type": "string",
                        "description": "시장 구분",
                        "enum": ["KOSPI", "KOSDAQ"],
                        "default": "KOSPI"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_foreign_investment",
            description="외국인 투자자의 매매 현황을 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)"
                    },
                    "market": {
                        "type": "string",
                        "description": "시장 구분",
                        "enum": ["KOSPI", "KOSDAQ"],
                        "default": "KOSPI"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_institutional_investment", 
            description="기관투자자의 매매 현황을 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)"
                    },
                    "market": {
                        "type": "string",
                        "description": "시장 구분",
                        "enum": ["KOSPI", "KOSDAQ"],
                        "default": "KOSPI"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_index_ohlcv",
            description="지수의 OHLCV 데이터를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "index_code": {
                        "type": "string", 
                        "description": "지수 코드 (1001=코스피, 2001=코스닥, 1028=코스피200 등)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "시작일 (YYYYMMDD 형식)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "종료일 (YYYYMMDD 형식, 기본값: 오늘)",
                        "default": ""
                    }
                },
                "required": ["index_code", "start_date"]
            }
        ),
        Tool(
            name="get_sector_performance",
            description="업종별 성과를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)"
                    },
                    "market": {
                        "type": "string",
                        "description": "시장 구분",
                        "enum": ["KOSPI", "KOSDAQ"],
                        "default": "KOSPI"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_short_selling",
            description="공매도 현황을 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)"
                    },
                    "market": {
                        "type": "string", 
                        "description": "시장 구분",
                        "enum": ["KOSPI", "KOSDAQ"],
                        "default": "KOSPI"
                    }
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """도구 호출 처리"""
    
    if not PYKRX_AVAILABLE:
        return [TextContent(
            type="text", 
            text="Error: pykrx is not available. Please install it with: pip install pykrx"
        )]
    
    try:
        if name == "get_market_tickers":
            market = arguments["market"]
            date = format_date(arguments.get("date", ""))
            
            tickers = stock.get_market_ticker_list(date=date, market=market)
            
            result = {
                "success": True,
                "market": market,
                "date": date,
                "count": len(tickers),
                "tickers": tickers[:20]  # 처음 20개만 반환
            }
            
        elif name == "get_ticker_name":
            ticker = arguments["ticker"]
            name = stock.get_market_ticker_name(ticker)
            
            result = {
                "success": True,
                "ticker": ticker,
                "name": name
            }
            
        elif name == "get_stock_ohlcv":
            ticker = arguments["ticker"]
            start_date = format_date(arguments["start_date"])
            end_date = format_date(arguments.get("end_date", ""))
            
            # 종목명도 함께 조회
            ticker_name = stock.get_market_ticker_name(ticker)
            
            # OHLCV 데이터 조회
            df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
            
            if df.empty:
                data = []
            else:
                # DataFrame을 딕셔너리 리스트로 변환
                data = []
                for date, row in df.iterrows():
                    data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": int(row["시가"]),
                        "high": int(row["고가"]),
                        "low": int(row["저가"]),
                        "close": int(row["종가"]),
                        "volume": int(row["거래량"])
                    })
            
            result = {
                "success": True,
                "ticker": ticker,
                "ticker_name": ticker_name,
                "start_date": start_date,
                "end_date": end_date,
                "data_count": len(data),
                "data": data
            }
            
        elif name == "search_stocks":
            keyword = arguments["keyword"]
            market_filter = arguments.get("market", "ALL")
            
            # 검색할 시장 목록
            markets = ["KOSPI", "KOSDAQ", "KONEX"] if market_filter == "ALL" else [market_filter]
            
            found_stocks = []
            
            for market in markets:
                try:
                    tickers = stock.get_market_ticker_list(market=market)
                    
                    for ticker in tickers:
                        name = stock.get_market_ticker_name(ticker)
                        if keyword.lower() in name.lower():
                            found_stocks.append({
                                "ticker": ticker,
                                "name": name,
                                "market": market
                            })
                except:
                    continue
                    
                # 최대 10개까지만
                if len(found_stocks) >= 10:
                    break
            
            result = {
                "success": True,
                "keyword": keyword,
                "market_filter": market_filter,
                "found_count": len(found_stocks),
                "stocks": found_stocks
            }
            
        elif name == "get_market_fundamental":
            date = format_date(arguments.get("date", ""))
            market = arguments.get("market", "KOSPI")
            
            df = stock.get_market_fundamental_by_date(date, date, market=market)
            
            if df.empty:
                data = []
            else:
                # 상위 10개 종목만 반환
                data = []
                for ticker, row in df.head(10).iterrows():
                    ticker_name = stock.get_market_ticker_name(ticker)
                    data.append({
                        "ticker": ticker,
                        "name": ticker_name,
                        "bps": float(row.get("BPS", 0)) if pd.notna(row.get("BPS")) else 0,
                        "per": float(row.get("PER", 0)) if pd.notna(row.get("PER")) else 0,
                        "pbr": float(row.get("PBR", 0)) if pd.notna(row.get("PBR")) else 0,
                        "eps": float(row.get("EPS", 0)) if pd.notna(row.get("EPS")) else 0,
                        "div": float(row.get("DIV", 0)) if pd.notna(row.get("DIV")) else 0,
                        "dps": float(row.get("DPS", 0)) if pd.notna(row.get("DPS")) else 0
                    })
            
            result = {
                "success": True,
                "date": date,
                "market": market,
                "data_count": len(data),
                "data": data
            }
            
        elif name == "get_market_cap":
            date = format_date(arguments.get("date", ""))
            market = arguments.get("market", "KOSPI")
            
            df = stock.get_market_cap(date, market=market)
            
            if df.empty:
                data = []
            else:
                # 상위 20개 종목만 반환 (시가총액 기준 정렬)
                df_sorted = df.sort_values('시가총액', ascending=False)
                data = []
                for idx, (ticker, row) in enumerate(df_sorted.head(20).iterrows(), 1):
                    ticker_name = stock.get_market_ticker_name(ticker)
                    data.append({
                        "rank": idx,
                        "ticker": ticker,
                        "name": ticker_name,
                        "market_cap": int(row.get("시가총액", 0)),
                        "shares": int(row.get("상장주식수", 0))
                    })
            
            result = {
                "success": True,
                "date": date,
                "market": market,
                "data_count": len(data),
                "data": data
            }
            
        elif name == "get_foreign_investment":
            date = format_date(arguments.get("date", ""))
            market = arguments.get("market", "KOSPI")
            
            try:
                df = stock.get_market_trading_volume_by_investor(date, date, market)
                
                if df.empty:
                    data = {}
                else:
                    # 외국인 데이터 찾기
                    foreign_data = None
                    if "외국인" in df.index:
                        foreign_data = df.loc["외국인"]
                    
                    if foreign_data is not None:
                        data = {
                            "date": date,
                            "market": market,
                            "foreign_sell": int(foreign_data.get("매도", 0)),
                            "foreign_buy": int(foreign_data.get("매수", 0)),
                            "foreign_net": int(foreign_data.get("순매수", 0))
                        }
                    else:
                        data = {}
                
                result = {
                    "success": True,
                    "data": data
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": f"외국인 투자 데이터 조회 실패: {str(e)}"
                }
            
        elif name == "get_institutional_investment":
            date = format_date(arguments.get("date", ""))
            market = arguments.get("market", "KOSPI")
            
            try:
                df = stock.get_market_trading_volume_by_investor(date, date, market)
                
                if df.empty:
                    data = {}
                else:
                    # 기관투자자 데이터들 합계 계산
                    institution_categories = ["금융투자", "보험", "투신", "사모", "은행", "기타금융", "연기금등"]
                    
                    total_sell = 0
                    total_buy = 0
                    total_net = 0
                    
                    for category in institution_categories:
                        if category in df.index:
                            row = df.loc[category]
                            total_sell += int(row.get("매도", 0))
                            total_buy += int(row.get("매수", 0))
                            total_net += int(row.get("순매수", 0))
                    
                    data = {
                        "date": date,
                        "market": market,
                        "institution_sell": total_sell,
                        "institution_buy": total_buy,
                        "institution_net": total_net
                    }
                
                result = {
                    "success": True,
                    "data": data
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": f"기관 투자 데이터 조회 실패: {str(e)}"
                }
            
        elif name == "get_index_ohlcv":
            index_code = arguments["index_code"]
            start_date = format_date(arguments["start_date"])
            end_date = format_date(arguments.get("end_date", ""))
            
            df = stock.get_index_ohlcv_by_date(start_date, end_date, index_code)
            
            if df.empty:
                data = []
            else:
                data = []
                for date, row in df.iterrows():
                    data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": float(row["시가"]),
                        "high": float(row["고가"]),
                        "low": float(row["저가"]),
                        "close": float(row["종가"]),
                        "volume": int(row["거래량"])
                    })
            
            # 지수명 매핑
            index_names = {
                "1001": "코스피",
                "2001": "코스닥",
                "1028": "코스피200",
                "1024": "코스피100", 
                "1003": "코스피50"
            }
            
            result = {
                "success": True,
                "index_code": index_code,
                "index_name": index_names.get(index_code, f"지수{index_code}"),
                "start_date": start_date,
                "end_date": end_date,
                "data_count": len(data),
                "data": data
            }
            
        elif name == "get_sector_performance":
            date = format_date(arguments.get("date", ""))
            market = arguments.get("market", "KOSPI")
            
            try:
                # 업종 분류 정보 조회
                sector_df = stock.get_market_sector_classifications(market)
                
                if sector_df.empty:
                    data = []
                else:
                    # 업종별 현재 지수 조회
                    data = []
                    for idx, row in sector_df.head(10).iterrows():  # 상위 10개 업종만
                        sector_code = row.get("업종코드", "")
                        sector_name = row.get("업종명", "")
                        
                        try:
                            # 업종 지수 데이터 조회 시도
                            index_data = stock.get_index_ohlcv_by_date(date, date, sector_code)
                            if not index_data.empty:
                                latest = index_data.iloc[-1]
                                close_price = float(latest.get("종가", 0))
                            else:
                                close_price = 0
                        except:
                            close_price = 0
                        
                        data.append({
                            "sector_code": sector_code,
                            "sector_name": sector_name,
                            "close_price": close_price
                        })
                
                result = {
                    "success": True,
                    "date": date,
                    "market": market,
                    "data_count": len(data),
                    "data": data
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": f"업종 성과 조회 실패: {str(e)}"
                }
            
        elif name == "get_short_selling":
            date = format_date(arguments.get("date", ""))
            market = arguments.get("market", "KOSPI")
            
            try:
                # 공매도 잔고 조회
                short_df = stock.get_shorting_balance_by_date(date, date, market=market)
                
                if short_df.empty:
                    data = []
                else:
                    # 상위 20개 종목만 반환 (공매도 잔고 기준)
                    data = []
                    for ticker, row in short_df.head(20).iterrows():
                        ticker_name = stock.get_market_ticker_name(ticker)
                        data.append({
                            "rank": len(data) + 1,
                            "ticker": ticker,
                            "name": ticker_name,
                            "short_balance": int(row.get("공매도잔고", 0)),
                            "short_ratio": float(row.get("공매도비중", 0))
                        })
                
                result = {
                    "success": True,
                    "date": date,
                    "market": market,
                    "data_count": len(data),
                    "data": data
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": f"공매도 데이터 조회 실패: {str(e)}"
                }
            
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}"
            }
            
    except Exception as e:
        result = {
            "success": False,
            "error": f"Error in {name}: {str(e)}",
            "traceback": traceback.format_exc()
        }
    
    # 결과를 JSON으로 반환
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2, default=str)
    )]

async def main():
    """서버 실행"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

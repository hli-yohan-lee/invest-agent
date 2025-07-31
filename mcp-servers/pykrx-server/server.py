"""
PyKRX MCP Server
한국거래소 데이터를 제공하는 MCP 서버
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import traceback

try:
    import pykrx.stock as stock
    import pykrx.bond as bond
    PYKRX_AVAILABLE = True
except ImportError as e:
    PYKRX_AVAILABLE = False
    print(f"Warning: pykrx import failed: {e}")
    print("Install it with: pip install pykrx")

import pandas as pd
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types
from mcp.server.session import ServerSession
from mcp.server.stdio import stdio_server


class PyKRXMCPServer:
    def __init__(self):
        self.server = Server("pykrx-server")
        self.setup_handlers()
    
    def setup_handlers(self):
        """MCP 핸들러 설정"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """사용 가능한 도구 목록 반환"""
            return [
                Tool(
                    name="get_stock_info",
                    description="종목 기본 정보 조회 (종목명, 업종, 시가총액 등)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "종목 코드 (예: '005930' for 삼성전자)"
                            }
                        },
                        "required": ["ticker"]
                    }
                ),
                Tool(
                    name="get_stock_prices",
                    description="종목 가격 정보 조회 (일별, 주별, 월별)",
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
                                "description": "종료일 (YYYYMMDD 형식)"
                            },
                            "period": {
                                "type": "string",
                                "enum": ["day", "week", "month"],
                                "description": "조회 기간 단위",
                                "default": "day"
                            }
                        },
                        "required": ["ticker", "start_date", "end_date"]
                    }
                ),
                Tool(
                    name="get_stock_fundamentals",
                    description="종목 재무 정보 조회 (PER, PBR, ROE, 배당률 등)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "종목 코드"
                            },
                            "date": {
                                "type": "string",
                                "description": "조회일 (YYYYMMDD 형식, 선택사항)"
                            }
                        },
                        "required": ["ticker"]
                    }
                ),
                Tool(
                    name="get_market_cap",
                    description="시가총액 정보 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "조회일 (YYYYMMDD 형식)"
                            },
                            "market": {
                                "type": "string",
                                "enum": ["KOSPI", "KOSDAQ", "ALL"],
                                "description": "시장 구분",
                                "default": "ALL"
                            }
                        },
                        "required": ["date"]
                    }
                ),
                Tool(
                    name="get_sector_performance",
                    description="업종별 성과 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "조회일 (YYYYMMDD 형식)"
                            },
                            "market": {
                                "type": "string",
                                "enum": ["KOSPI", "KOSDAQ"],
                                "description": "시장 구분",
                                "default": "KOSPI"
                            }
                        },
                        "required": ["date"]
                    }
                ),
                Tool(
                    name="get_index_data",
                    description="지수 데이터 조회 (KOSPI, KOSDAQ, KRX 등)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "index_name": {
                                "type": "string",
                                "description": "지수명 (KOSPI, KOSDAQ, KRX100 등)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "시작일 (YYYYMMDD 형식)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "종료일 (YYYYMMDD 형식)"
                            }
                        },
                        "required": ["index_name", "start_date", "end_date"]
                    }
                ),
                Tool(
                    name="get_foreign_investment",
                    description="외국인 투자 현황 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "종목 코드 (선택사항)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "시작일 (YYYYMMDD 형식)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "종료일 (YYYYMMDD 형식)"
                            }
                        },
                        "required": ["start_date", "end_date"]
                    }
                ),
                Tool(
                    name="get_institutional_investment",
                    description="기관 투자 현황 조회",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "종목 코드 (선택사항)"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "시작일 (YYYYMMDD 형식)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "종료일 (YYYYMMDD 형식)"
                            }
                        },
                        "required": ["start_date", "end_date"]
                    }
                ),
                Tool(
                    name="get_short_selling",
                    description="공매도 현황 조회",
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
                                "description": "종료일 (YYYYMMDD 형식)"
                            }
                        },
                        "required": ["ticker", "start_date", "end_date"]
                    }
                ),
                Tool(
                    name="search_ticker",
                    description="종목명으로 종목 코드 검색",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "검색할 종목명 (예: '삼성전자')"
                            },
                            "market": {
                                "type": "string",
                                "enum": ["KOSPI", "KOSDAQ", "ALL"],
                                "description": "시장 구분",
                                "default": "ALL"
                            }
                        },
                        "required": ["name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """도구 호출 처리"""
            
            if not PYKRX_AVAILABLE:
                return [types.TextContent(
                    type="text",
                    text="Error: pykrx is not installed. Please install it with: pip install pykrx"
                )]
            
            try:
                if name == "get_stock_info":
                    return await self.get_stock_info(arguments)
                elif name == "get_stock_prices":
                    return await self.get_stock_prices(arguments)
                elif name == "get_stock_fundamentals":
                    return await self.get_stock_fundamentals(arguments)
                elif name == "get_market_cap":
                    return await self.get_market_cap(arguments)
                elif name == "get_sector_performance":
                    return await self.get_sector_performance(arguments)
                elif name == "get_index_data":
                    return await self.get_index_data(arguments)
                elif name == "get_foreign_investment":
                    return await self.get_foreign_investment(arguments)
                elif name == "get_institutional_investment":
                    return await self.get_institutional_investment(arguments)
                elif name == "get_short_selling":
                    return await self.get_short_selling(arguments)
                elif name == "search_ticker":
                    return await self.search_ticker(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                error_msg = f"Error in {name}: {str(e)}\n{traceback.format_exc()}"
                return [types.TextContent(
                    type="text",
                    text=error_msg
                )]

    async def get_stock_info(self, arguments: dict) -> list[types.TextContent]:
        """종목 기본 정보 조회"""
        ticker = arguments["ticker"]
        
        try:
            # 종목명 조회
            ticker_list = stock.get_market_ticker_list()
            ticker_name = stock.get_market_ticker_name(ticker)
            
            if not ticker_name:
                return [types.TextContent(
                    type="text",
                    text=f"종목 코드 '{ticker}'를 찾을 수 없습니다."
                )]
            
            # 기본 정보 수집
            today = datetime.now().strftime("%Y%m%d")
            
            # 최근 가격 정보
            try:
                recent_ohlcv = stock.get_market_ohlcv_by_date(today, today, ticker)
                if recent_ohlcv.empty:
                    # 오늘 데이터가 없으면 어제 데이터 조회
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
                    recent_ohlcv = stock.get_market_ohlcv_by_date(yesterday, yesterday, ticker)
            except:
                recent_ohlcv = pd.DataFrame()
            
            # 시가총액 정보
            try:
                market_cap = stock.get_market_cap_by_date(today, today, ticker)
                if market_cap.empty:
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
                    market_cap = stock.get_market_cap_by_date(yesterday, yesterday, ticker)
            except:
                market_cap = pd.DataFrame()
            
            # 결과 정리
            result = {
                "종목코드": ticker,
                "종목명": ticker_name,
                "조회일": today
            }
            
            if not recent_ohlcv.empty:
                latest_data = recent_ohlcv.iloc[-1]
                result.update({
                    "종가": f"{latest_data['종가']:,}원",
                    "시가": f"{latest_data['시가']:,}원",
                    "고가": f"{latest_data['고가']:,}원",
                    "저가": f"{latest_data['저가']:,}원",
                    "거래량": f"{latest_data['거래량']:,}주"
                })
            
            if not market_cap.empty:
                cap_data = market_cap.iloc[-1]
                result.update({
                    "시가총액": f"{cap_data['시가총액']:,}원",
                    "상장주식수": f"{cap_data['상장주식수']:,}주"
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"종목 정보 조회 실패: {str(e)}"
            )]

    async def get_stock_prices(self, arguments: dict) -> list[types.TextContent]:
        """종목 가격 정보 조회"""
        ticker = arguments["ticker"]
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        period = arguments.get("period", "day")
        
        try:
            if period == "day":
                df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
            elif period == "week":
                df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker, freq='w')
            elif period == "month":
                df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker, freq='m')
            else:
                return [types.TextContent(
                    type="text",
                    text="잘못된 period 값입니다. 'day', 'week', 'month' 중 하나를 선택하세요."
                )]
            
            if df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당 기간({start_date}~{end_date})에 대한 {ticker} 데이터가 없습니다."
                )]
            
            # 데이터 포맷팅
            df_formatted = df.copy()
            for col in ['시가', '고가', '저가', '종가']:
                df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:,}")
            df_formatted['거래량'] = df_formatted['거래량'].apply(lambda x: f"{x:,}")
            
            result = {
                "종목코드": ticker,
                "종목명": stock.get_market_ticker_name(ticker),
                "조회기간": f"{start_date} ~ {end_date}",
                "기간단위": period,
                "데이터": df_formatted.to_dict('index')
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2, default=str)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"가격 정보 조회 실패: {str(e)}"
            )]

    async def get_stock_fundamentals(self, arguments: dict) -> list[types.TextContent]:
        """종목 재무 정보 조회"""
        ticker = arguments["ticker"]
        date = arguments.get("date", datetime.now().strftime("%Y%m%d"))
        
        try:
            # 기본 재무 정보
            fundamental_df = stock.get_market_fundamental_by_date(date, date, ticker)
            
            if fundamental_df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당일({date})에 대한 {ticker} 재무 데이터가 없습니다."
                )]
            
            fundamental_data = fundamental_df.iloc[-1]
            
            result = {
                "종목코드": ticker,
                "종목명": stock.get_market_ticker_name(ticker),
                "조회일": date,
                "PER": round(fundamental_data.get('PER', 0), 2),
                "PBR": round(fundamental_data.get('PBR', 0), 2),
                "EPS": f"{fundamental_data.get('EPS', 0):,}원",
                "BPS": f"{fundamental_data.get('BPS', 0):,}원",
                "DIV": f"{fundamental_data.get('DIV', 0)}%",
                "DPS": f"{fundamental_data.get('DPS', 0):,}원"
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"재무 정보 조회 실패: {str(e)}"
            )]

    async def get_market_cap(self, arguments: dict) -> list[types.TextContent]:
        """시가총액 정보 조회"""
        date = arguments["date"]
        market = arguments.get("market", "ALL")
        
        try:
            if market == "KOSPI":
                market_list = ["KOSPI"]
            elif market == "KOSDAQ":
                market_list = ["KOSDAQ"]
            else:
                market_list = ["KOSPI", "KOSDAQ"]
            
            all_data = []
            
            for mkt in market_list:
                ticker_list = stock.get_market_ticker_list(date, market=mkt)
                if ticker_list:
                    cap_df = stock.get_market_cap_by_date(date, date, ticker_list[0])
                    for ticker in ticker_list[:10]:  # 상위 10개만
                        try:
                            ticker_cap = stock.get_market_cap_by_date(date, date, ticker)
                            if not ticker_cap.empty:
                                ticker_data = ticker_cap.iloc[-1]
                                all_data.append({
                                    "시장": mkt,
                                    "종목코드": ticker,
                                    "종목명": stock.get_market_ticker_name(ticker),
                                    "시가총액": ticker_data['시가총액'],
                                    "상장주식수": ticker_data['상장주식수']
                                })
                        except:
                            continue
            
            # 시가총액 기준 정렬
            all_data.sort(key=lambda x: x['시가총액'], reverse=True)
            
            # 포맷팅
            for item in all_data:
                item['시가총액'] = f"{item['시가총액']:,}원"
                item['상장주식수'] = f"{item['상장주식수']:,}주"
            
            result = {
                "조회일": date,
                "시장구분": market,
                "데이터": all_data[:20]  # 상위 20개
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"시가총액 조회 실패: {str(e)}"
            )]

    async def get_sector_performance(self, arguments: dict) -> list[types.TextContent]:
        """업종별 성과 조회"""
        date = arguments["date"]
        market = arguments.get("market", "KOSPI")
        
        try:
            if market == "KOSPI":
                df = stock.get_market_sector_index_by_date(date, date, "KOSPI")
            else:
                df = stock.get_market_sector_index_by_date(date, date, "KOSDAQ")
            
            if df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당일({date})에 대한 {market} 업종 데이터가 없습니다."
                )]
            
            # 등락률 계산 및 정렬
            df_result = df.copy()
            df_result = df_result.sort_values('등락률', ascending=False)
            
            sectors_data = []
            for idx, row in df_result.iterrows():
                sectors_data.append({
                    "업종명": idx,
                    "지수": f"{row['지수']:.2f}",
                    "등락률": f"{row['등락률']:.2f}%",
                    "거래량": f"{row['거래량']:,}" if '거래량' in row else "N/A",
                    "거래대금": f"{row['거래대금']:,}원" if '거래대금' in row else "N/A"
                })
            
            result = {
                "조회일": date,
                "시장": market,
                "업종별_성과": sectors_data
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"업종별 성과 조회 실패: {str(e)}"
            )]

    async def get_index_data(self, arguments: dict) -> list[types.TextContent]:
        """지수 데이터 조회"""
        index_name = arguments["index_name"]
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        
        try:
            # 지수명 매핑
            index_mapping = {
                "KOSPI": "1001",
                "KOSDAQ": "2001", 
                "KRX100": "1028"
            }
            
            index_code = index_mapping.get(index_name.upper(), index_name)
            
            df = stock.get_index_ohlcv_by_date(start_date, end_date, index_code)
            
            if df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당 기간({start_date}~{end_date})에 대한 {index_name} 지수 데이터가 없습니다."
                )]
            
            # 데이터 포맷팅
            df_formatted = df.copy()
            for col in ['시가', '고가', '저가', '종가']:
                if col in df_formatted.columns:
                    df_formatted[col] = df_formatted[col].apply(lambda x: f"{x:.2f}")
            
            if '거래량' in df_formatted.columns:
                df_formatted['거래량'] = df_formatted['거래량'].apply(lambda x: f"{x:,}")
            
            result = {
                "지수명": index_name,
                "지수코드": index_code,
                "조회기간": f"{start_date} ~ {end_date}",
                "데이터": df_formatted.to_dict('index')
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2, default=str)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"지수 데이터 조회 실패: {str(e)}"
            )]

    async def get_foreign_investment(self, arguments: dict) -> list[types.TextContent]:
        """외국인 투자 현황 조회"""
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        ticker = arguments.get("ticker")
        
        try:
            if ticker:
                # 특정 종목의 외국인 투자 현황
                df = stock.get_market_trading_value_by_date(start_date, end_date, ticker, detail=True)
                df = df[df['투자자'] == '외국인']
            else:
                # 전체 시장 외국인 투자 현황
                df = stock.get_market_trading_value_by_investor(start_date, end_date, "KOSPI", detail=True)
                df = df[df['투자자'] == '외국인']
            
            if df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당 기간({start_date}~{end_date})에 대한 외국인 투자 데이터가 없습니다."
                )]
            
            # 데이터 포맷팅
            result_data = []
            for idx, row in df.iterrows():
                result_data.append({
                    "날짜": str(idx) if isinstance(idx, str) else idx.strftime("%Y-%m-%d"),
                    "매수금액": f"{row.get('매수', 0):,}원",
                    "매도금액": f"{row.get('매도', 0):,}원", 
                    "순매수금액": f"{row.get('순매수', 0):,}원"
                })
            
            result = {
                "조회기간": f"{start_date} ~ {end_date}",
                "종목": stock.get_market_ticker_name(ticker) if ticker else "전체시장",
                "외국인_투자현황": result_data
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"외국인 투자 현황 조회 실패: {str(e)}"
            )]

    async def get_institutional_investment(self, arguments: dict) -> list[types.TextContent]:
        """기관 투자 현황 조회"""
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        ticker = arguments.get("ticker")
        
        try:
            if ticker:
                # 특정 종목의 기관 투자 현황
                df = stock.get_market_trading_value_by_date(start_date, end_date, ticker, detail=True)
                df = df[df['투자자'].str.contains('기관')]
            else:
                # 전체 시장 기관 투자 현황
                df = stock.get_market_trading_value_by_investor(start_date, end_date, "KOSPI", detail=True)
                df = df[df['투자자'].str.contains('기관')]
            
            if df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당 기간({start_date}~{end_date})에 대한 기관 투자 데이터가 없습니다."
                )]
            
            # 데이터 포맷팅
            result_data = []
            for idx, row in df.iterrows():
                result_data.append({
                    "날짜": str(idx) if isinstance(idx, str) else idx.strftime("%Y-%m-%d"),
                    "투자자구분": row.get('투자자', ''),
                    "매수금액": f"{row.get('매수', 0):,}원",
                    "매도금액": f"{row.get('매도', 0):,}원",
                    "순매수금액": f"{row.get('순매수', 0):,}원"
                })
            
            result = {
                "조회기간": f"{start_date} ~ {end_date}",
                "종목": stock.get_market_ticker_name(ticker) if ticker else "전체시장",
                "기관_투자현황": result_data
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"기관 투자 현황 조회 실패: {str(e)}"
            )]

    async def get_short_selling(self, arguments: dict) -> list[types.TextContent]:
        """공매도 현황 조회"""
        ticker = arguments["ticker"]
        start_date = arguments["start_date"]
        end_date = arguments["end_date"]
        
        try:
            df = stock.get_shorting_status_by_date(start_date, end_date, ticker)
            
            if df.empty:
                return [types.TextContent(
                    type="text",
                    text=f"해당 기간({start_date}~{end_date})에 대한 {ticker} 공매도 데이터가 없습니다."
                )]
            
            # 데이터 포맷팅
            result_data = []
            for idx, row in df.iterrows():
                result_data.append({
                    "날짜": str(idx) if isinstance(idx, str) else idx.strftime("%Y-%m-%d"),
                    "공매도거래량": f"{row.get('공매도거래량', 0):,}주",
                    "공매도거래대금": f"{row.get('공매도거래대금', 0):,}원",
                    "공매도비중": f"{row.get('공매도비중', 0):.2f}%"
                })
            
            result = {
                "종목코드": ticker,
                "종목명": stock.get_market_ticker_name(ticker),
                "조회기간": f"{start_date} ~ {end_date}",
                "공매도_현황": result_data
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"공매도 현황 조회 실패: {str(e)}"
            )]

    async def search_ticker(self, arguments: dict) -> list[types.TextContent]:
        """종목명으로 종목 코드 검색"""
        name = arguments["name"]
        market = arguments.get("market", "ALL")
        
        try:
            markets_to_search = []
            if market == "ALL":
                markets_to_search = ["KOSPI", "KOSDAQ"]
            else:
                markets_to_search = [market]
            
            results = []
            
            for mkt in markets_to_search:
                ticker_list = stock.get_market_ticker_list(market=mkt)
                
                for ticker in ticker_list:
                    ticker_name = stock.get_market_ticker_name(ticker)
                    if name in ticker_name:
                        results.append({
                            "종목코드": ticker,
                            "종목명": ticker_name,
                            "시장": mkt
                        })
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"'{name}'을 포함하는 종목을 찾을 수 없습니다."
                )]
            
            result = {
                "검색어": name,
                "검색결과": results[:20]  # 상위 20개 결과만
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"종목 검색 실패: {str(e)}"
            )]

    async def run(self):
        """서버 실행"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="pykrx-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """메인 함수"""
    server = PyKRXMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())

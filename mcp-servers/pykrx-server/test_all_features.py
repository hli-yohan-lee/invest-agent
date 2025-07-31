#!/usr/bin/env python3
"""
PyKRX MCP 서버 전체 기능 테스트
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_all_features():
    """모든 기능 테스트"""
    print("=== PyKRX MCP 서버 전체 기능 테스트 ===\n")
    
    server_params = StdioServerParameters(
        command="python",
        args=["simple_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                await session.initialize()
                
                # 1. 삼성전자 주가 데이터 조회
                print("1. 삼성전자 주가 데이터 조회 (최근 1주일):")
                
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
                
                result = await session.call_tool(
                    name="get_stock_ohlcv",
                    arguments={
                        "ticker": "005930",
                        "start_date": start_date,
                        "end_date": end_date
                    }
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success']:
                            print(f"  종목: {data['ticker_name']} ({data['ticker']})")
                            print(f"  기간: {data['start_date']} ~ {data['end_date']}")
                            print(f"  데이터 수: {data['data_count']}개")
                            
                            if data['data']:
                                print("  최근 데이터:")
                                for item in data['data'][-3:]:  # 최근 3일
                                    print(f"    {item['date']}: 종가 {item['close']:,}원, 거래량 {item['volume']:,}주")
                        else:
                            print(f"  오류: {data.get('error', 'Unknown error')}")
                print()
                
                # 2. KOSDAQ 종목 목록 조회
                print("2. KOSDAQ 종목 목록 조회:")
                result = await session.call_tool(
                    name="get_market_tickers",
                    arguments={"market": "KOSDAQ"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success']:
                            print(f"  KOSDAQ 총 종목 수: {data['count']}")
                            print(f"  처음 10개: {data['tickers'][:10]}")
                        else:
                            print(f"  오류: {data.get('error', 'Unknown error')}")
                print()
                
                # 3. 다양한 키워드로 종목 검색
                keywords = ["현대", "LG", "SK", "포스코"]
                for keyword in keywords:
                    print(f"3-{keywords.index(keyword)+1}. '{keyword}' 키워드 검색:")
                    
                    result = await session.call_tool(
                        name="search_stocks",
                        arguments={"keyword": keyword, "market": "ALL"}
                    )
                    
                    for content in result.content:
                        if hasattr(content, 'text'):
                            data = json.loads(content.text)
                            if data['success']:
                                print(f"  검색 결과: {data['found_count']}개")
                                for stock in data['stocks'][:3]:  # 처음 3개만
                                    print(f"    {stock['ticker']}: {stock['name']} ({stock['market']})")
                            else:
                                print(f"  오류: {data.get('error', 'Unknown error')}")
                    print()
                
                print("✅ 전체 기능 테스트 완료!")
                
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_all_features())

#!/usr/bin/env python3
"""
간단한 MCP 클라이언트 테스트
"""

import asyncio
import json
import subprocess
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_simple_server():
    """간단한 MCP 서버 테스트"""
    print("=== 간단한 PyKRX MCP 서버 테스트 ===\n")
    
    server_params = StdioServerParameters(
        command="python",
        args=["simple_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # 초기화
                await session.initialize()
                
                # 도구 목록 조회
                print("1. 사용 가능한 도구 목록:")
                tools = await session.list_tools()
                
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
                
                # 삼성전자 종목명 조회
                print("2. 삼성전자(005930) 종목명 조회:")
                result = await session.call_tool(
                    name="get_ticker_name",
                    arguments={"ticker": "005930"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        print(f"  종목명: {data.get('name', 'N/A')}")
                print()
                
                # KOSPI 종목 목록 일부 조회
                print("3. KOSPI 종목 목록 (처음 20개):")
                result = await session.call_tool(
                    name="get_market_tickers",
                    arguments={"market": "KOSPI"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success']:
                            print(f"  총 종목 수: {data['count']}")
                            print(f"  처음 5개: {data['tickers'][:5]}")
                        else:
                            print(f"  오류: {data.get('error', 'Unknown error')}")
                print()
                
                # 삼성 키워드로 종목 검색
                print("4. '삼성' 키워드로 종목 검색:")
                result = await session.call_tool(
                    name="search_stocks",
                    arguments={"keyword": "삼성", "market": "KOSPI"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success']:
                            print(f"  검색 결과: {data['found_count']}개")
                            for stock in data['stocks'][:5]:
                                print(f"    {stock['ticker']}: {stock['name']}")
                        else:
                            print(f"  오류: {data.get('error', 'Unknown error')}")
                print()
                
                print("✅ 테스트 완료!")
                
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_server())

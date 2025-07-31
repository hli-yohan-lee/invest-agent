#!/usr/bin/env python3
"""
PyKRX MCP 서버 테스트 클라이언트
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_tools():
    """MCP 서버의 도구들을 테스트"""
    print("=== PyKRX MCP 서버 테스트 ===\n")
    
    # MCP 서버 매개변수 설정
    server_params = StdioServerParameters(
        command="python",
        args=["run_server.py"],
        cwd="."
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 1. 사용 가능한 도구 목록 조회
                print("1. 사용 가능한 도구 목록 조회")
                tools = await session.list_tools()
                
                print(f"사용 가능한 도구 수: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                print()
                
                # 2. 삼성전자 기본 정보 조회
                print("2. 삼성전자 기본 정보 조회")
                try:
                    result = await session.call_tool(
                        name="get_stock_info",
                        arguments={"ticker": "005930"}
                    )
                    print("결과:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                except Exception as e:
                    print(f"오류: {e}")
                print()
                
                # 3. 삼성전자 주가 정보 조회
                print("3. 삼성전자 주가 정보 조회")
                try:
                    result = await session.call_tool(
                        name="get_stock_prices",
                        arguments={
                            "ticker": "005930",
                            "start_date": "20250720",
                            "end_date": "20250731"
                        }
                    )
                    print("결과:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                except Exception as e:
                    print(f"오류: {e}")
                print()
                
                # 4. 종목 검색 테스트
                print("4. 종목 검색 테스트 (삼성)")
                try:
                    result = await session.call_tool(
                        name="search_ticker",
                        arguments={"name": "삼성"}
                    )
                    print("결과:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                except Exception as e:
                    print(f"오류: {e}")
                print()
                
    except Exception as e:
        print(f"서버 연결 오류: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())

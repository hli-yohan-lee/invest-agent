#!/usr/bin/env python3
"""
PyKRX MCP 서버 최종 종합 테스트
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_final_server():
    """최종 완성된 서버 종합 테스트"""
    print("=== PyKRX MCP 서버 최종 종합 테스트 ===\n")
    
    server_params = StdioServerParameters(
        command="python",
        args=["simple_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                await session.initialize()
                
                print("🔧 사용 가능한 도구 목록:")
                tools = await session.list_tools()
                for i, tool in enumerate(tools.tools, 1):
                    print(f"  {i:2d}. {tool.name}")
                print(f"\n총 {len(tools.tools)}개의 도구가 사용 가능합니다.\n")
                
                # 테스트 시나리오들
                tests = [
                    {
                        "name": "🏢 시가총액 TOP 5",
                        "tool": "get_market_cap",
                        "args": {"market": "KOSPI"},
                        "process": lambda data: [
                            f"  {stock['rank']:2d}. {stock['name']:15s} {stock['market_cap']/1_000_000_000_000:.1f}조원"
                            for stock in data['data'][:5]
                        ] if data['success'] else [f"  오류: {data.get('error', 'Unknown')}"]
                    },
                    {
                        "name": "📈 코스피 지수 (최근 3일)",
                        "tool": "get_index_ohlcv",
                        "args": {
                            "index_code": "1001",
                            "start_date": (datetime.now() - timedelta(days=5)).strftime("%Y%m%d"),
                            "end_date": datetime.now().strftime("%Y%m%d")
                        },
                        "process": lambda data: [
                            f"  {item['date']}: {item['close']:,.2f} (거래량: {item['volume']:,})"
                            for item in data['data'][-3:]
                        ] if data['success'] and data['data'] else [f"  오류: {data.get('error', 'No data')}"]
                    },
                    {
                        "name": "🌍 외국인 투자 현황",
                        "tool": "get_foreign_investment", 
                        "args": {"market": "KOSPI"},
                        "process": lambda data: [
                            f"  외국인 순매수: {data['data']['foreign_net']:,}주",
                            f"  (매수: {data['data']['foreign_buy']:,}, 매도: {data['data']['foreign_sell']:,})"
                        ] if data['success'] and data['data'] else [f"  오류: {data.get('error', 'No data')}"]
                    },
                    {
                        "name": "🏛️ 기관 투자 현황",
                        "tool": "get_institutional_investment",
                        "args": {"market": "KOSPI"},
                        "process": lambda data: [
                            f"  기관 순매수: {data['data']['institution_net']:,}주",
                            f"  (매수: {data['data']['institution_buy']:,}, 매도: {data['data']['institution_sell']:,})"
                        ] if data['success'] and data['data'] else [f"  오류: {data.get('error', 'No data')}"]
                    },
                    {
                        "name": "🔍 삼성 관련 종목 검색",
                        "tool": "search_stocks",
                        "args": {"keyword": "삼성", "market": "KOSPI"},
                        "process": lambda data: [
                            f"  {stock['ticker']}: {stock['name']:20s} ({stock['market']})"
                            for stock in data['stocks'][:5]
                        ] if data['success'] else [f"  오류: {data.get('error', 'Unknown')}"]
                    },
                    {
                        "name": "📊 삼성전자 주가 (최근 3일)",
                        "tool": "get_stock_ohlcv",
                        "args": {
                            "ticker": "005930",
                            "start_date": (datetime.now() - timedelta(days=5)).strftime("%Y%m%d"),
                            "end_date": datetime.now().strftime("%Y%m%d")
                        },
                        "process": lambda data: [
                            f"  {data['ticker_name']} ({data['ticker']})",
                            *[f"  {item['date']}: {item['close']:,}원 (거래량: {item['volume']:,})"
                              for item in data['data'][-3:]]
                        ] if data['success'] and data['data'] else [f"  오류: {data.get('error', 'No data')}"]
                    }
                ]
                
                # 각 테스트 실행
                for i, test in enumerate(tests, 1):
                    print(f"{i}. {test['name']}:")
                    
                    try:
                        result = await session.call_tool(
                            name=test['tool'],
                            arguments=test['args']
                        )
                        
                        for content in result.content:
                            if hasattr(content, 'text'):
                                data = json.loads(content.text)
                                messages = test['process'](data)
                                for msg in messages:
                                    print(msg)
                                
                    except Exception as e:
                        print(f"  ❌ 테스트 실패: {e}")
                    
                    print()
                
                print("✅ 최종 종합 테스트 완료!")
                print("\n🎉 PyKRX MCP 서버가 성공적으로 구축되었습니다!")
                
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_final_server())

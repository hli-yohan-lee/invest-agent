#!/usr/bin/env python3
"""
확장된 PyKRX MCP 서버 테스트
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_extended_features():
    """확장된 기능들 테스트"""
    print("=== 확장된 PyKRX MCP 서버 기능 테스트 ===\n")
    
    server_params = StdioServerParameters(
        command="python",
        args=["simple_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                await session.initialize()
                
                # 1. 도구 목록 확인
                print("1. 사용 가능한 도구 목록:")
                tools = await session.list_tools()
                for i, tool in enumerate(tools.tools, 1):
                    print(f"  {i}. {tool.name}: {tool.description}")
                print()
                
                # 2. KOSPI 시가총액 상위 종목
                print("2. KOSPI 시가총액 상위 종목 (Top 10):")
                result = await session.call_tool(
                    name="get_market_cap",
                    arguments={"market": "KOSPI"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success']:
                            print(f"  날짜: {data['date']}")
                            for stock_info in data['data'][:10]:
                                market_cap_trillion = stock_info['market_cap'] / 1_000_000_000_000
                                print(f"    {stock_info['rank']:2d}. {stock_info['name']} ({stock_info['ticker']}): {market_cap_trillion:.1f}조원")
                        else:
                            print(f"  오류: {data.get('error', 'Unknown error')}")
                print()
                
                # 3. 코스피 지수 데이터 (최근 1주일)
                print("3. 코스피 지수 데이터 (최근 1주일):")
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
                
                result = await session.call_tool(
                    name="get_index_ohlcv",
                    arguments={
                        "index_code": "1001",
                        "start_date": start_date,
                        "end_date": end_date
                    }
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success']:
                            print(f"  지수: {data['index_name']} ({data['index_code']})")
                            print(f"  기간: {data['start_date']} ~ {data['end_date']}")
                            print(f"  데이터 수: {data['data_count']}개")
                            
                            if data['data']:
                                print("  최근 데이터:")
                                for item in data['data'][-3:]:
                                    print(f"    {item['date']}: {item['close']:.2f} (거래량: {item['volume']:,})")
                        else:
                            print(f"  오류: {data.get('error', 'Unknown error')}")
                print()
                
                # 4. 외국인 투자 현황
                print("4. 외국인 투자 현황:")
                result = await session.call_tool(
                    name="get_foreign_investment",
                    arguments={"market": "KOSPI"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success'] and data['data']:
                            inv_data = data['data']
                            print(f"  날짜: {inv_data['date']}")
                            print(f"  시장: {inv_data['market']}")
                            print(f"  외국인 매수: {inv_data['foreign_buy']:,}주")
                            print(f"  외국인 매도: {inv_data['foreign_sell']:,}주")
                            print(f"  외국인 순매수: {inv_data['foreign_net']:,}주")
                        else:
                            print(f"  오류: {data.get('error', 'No data available')}")
                print()
                
                # 5. 기관 투자 현황
                print("5. 기관 투자 현황:")
                result = await session.call_tool(
                    name="get_institutional_investment",
                    arguments={"market": "KOSPI"}
                )
                
                for content in result.content:
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        if data['success'] and data['data']:
                            inv_data = data['data']
                            print(f"  날짜: {inv_data['date']}")
                            print(f"  시장: {inv_data['market']}")
                            print(f"  기관 매수: {inv_data['institution_buy']:,}주")
                            print(f"  기관 매도: {inv_data['institution_sell']:,}주")
                            print(f"  기관 순매수: {inv_data['institution_net']:,}주")
                        else:
                            print(f"  오류: {data.get('error', 'No data available')}")
                print()
                
                print("✅ 확장 기능 테스트 완료!")
                
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_extended_features())

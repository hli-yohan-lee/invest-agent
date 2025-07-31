"""
PyKRX MCP 서버 테스트 스크립트
"""

import asyncio
import json
from pykrx import stock
from datetime import datetime, timedelta

async def test_pykrx_functions():
    """pykrx 기능 테스트"""
    print("=== PyKRX 기능 테스트 ===\n")
    
    try:
        # 1. 종목 리스트 조회
        print("1. 종목 리스트 조회")
        ticker_list = stock.get_market_ticker_list()
        print(f"전체 종목 수: {len(ticker_list)}")
        print(f"첫 5개 종목: {ticker_list[:5]}")
        print()
        
        # 2. 삼성전자 정보 조회
        samsung = "005930"
        print(f"2. 삼성전자({samsung}) 정보")
        ticker_name = stock.get_market_ticker_name(samsung)
        print(f"종목명: {ticker_name}")
        
        # 3. 최근 주가 데이터
        today = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        
        print(f"3. 주가 데이터 ({start_date} ~ {today})")
        try:
            price_df = stock.get_market_ohlcv_by_date(start_date, today, samsung)
            if not price_df.empty:
                print("최근 주가 데이터:")
                print(price_df.tail())
            else:
                print("주가 데이터 없음 (주말/휴일)")
        except Exception as e:
            print(f"주가 데이터 조회 오류: {e}")
        print()
        
        # 4. 재무 정보
        print("4. 재무 정보")
        try:
            fundamental_df = stock.get_market_fundamental_by_date(start_date, today, samsung)
            if not fundamental_df.empty:
                print("재무 정보:")
                print(fundamental_df.tail())
            else:
                print("재무 정보 없음")
        except Exception as e:
            print(f"재무 정보 조회 오류: {e}")
        print()
        
        # 5. 종목 검색
        print("5. 종목 검색 (삼성)")
        search_results = []
        for ticker in ticker_list[:100]:  # 처음 100개만 검색
            try:
                name = stock.get_market_ticker_name(ticker)
                if "삼성" in name:
                    search_results.append({"ticker": ticker, "name": name})
            except:
                continue
        
        print("삼성 관련 종목:")
        for result in search_results[:5]:
            print(f"  {result['ticker']}: {result['name']}")
        print()
        
        print("✅ PyKRX 기본 기능 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pykrx_functions())

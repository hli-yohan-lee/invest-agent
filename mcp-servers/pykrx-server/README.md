# PyKRX MCP Server

한국거래소 데이터를 제공하는 MCP (Model Context Protocol) 서버입니다.

## ✨ 기능

이 MCP 서버는 pykrx 라이브러리를 사용하여 다음과 같은 한국 주식 시장 데이터를 제공합니다:

### 🔧 제공 도구 (11개)

1. **get_market_tickers** - 특정 시장의 모든 종목 코드 조회
   - KOSPI, KOSDAQ, KONEX 시장별 종목 리스트

2. **get_ticker_name** - 종목 코드로 종목명 조회
   - 종목 코드를 입력하면 해당 종목의 정식 명칭 반환

3. **get_stock_ohlcv** - 종목의 OHLCV 데이터 조회
   - 일별 시가, 고가, 저가, 종가, 거래량 데이터

4. **search_stocks** - 종목명으로 종목 검색
   - 키워드로 종목명 검색, 시장별 필터링 가능

5. **get_market_fundamental** - 시장 기본적 분석 데이터 조회
   - PER, PBR, EPS, BPS, 배당률 등 재무 지표

6. **get_market_cap** - 시가총액 정보 조회
   - 시가총액 기준 순위별 종목 정보

7. **get_foreign_investment** - 외국인 투자 현황 조회
   - 외국인 매수/매도/순매수 거래량

8. **get_institutional_investment** - 기관 투자 현황 조회
   - 기관투자자 매수/매도/순매수 거래량

9. **get_index_ohlcv** - 지수 데이터 조회
   - 코스피, 코스닥, 코스피200 등 주요 지수 OHLCV

10. **get_sector_performance** - 업종별 성과 조회
    - 업종 분류 및 업종별 지수 정보

11. **get_short_selling** - 공매도 현황 조회
    - 공매도 잔고 및 비중 정보

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 서버 실행

#### 직접 실행
```bash
python simple_server.py
```

#### 실행 스크립트 사용
```bash
python run_server.py
```

### 3. 테스트

#### 기본 기능 테스트
```bash
python test_simple_client.py
```

#### 전체 기능 테스트
```bash
python test_all_features.py
```

#### 확장 기능 테스트
```bash
python test_extended.py
```

#### 최종 종합 테스트
```bash
python test_final.py
```

#### pykrx 라이브러리 직접 테스트
```bash
python test_pykrx.py
```

## 📊 사용 예시

### MCP 클라이언트에서 사용

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["simple_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # 삼성전자 정보 조회
        result = await session.call_tool(
            name="get_ticker_name",
            arguments={"ticker": "005930"}
        )
        
        # 시가총액 TOP 10 조회
        result = await session.call_tool(
            name="get_market_cap",
            arguments={"market": "KOSPI"}
        )
```

### 응답 데이터 형식

모든 도구는 다음과 같은 JSON 형식으로 응답합니다:

```json
{
  "success": true,
  "data": {
    // 요청한 데이터
  },
  // 추가 메타데이터
}
```

오류 발생 시:

```json
{
  "success": false,
  "error": "오류 메시지",
  "traceback": "상세 오류 정보"
}
```

## 🛠️ 개발 정보

### 주요 의존성
- `pykrx>=1.0.46` - 한국 주식 데이터 라이브러리
- `mcp>=1.0.0` - Model Context Protocol 서버 프레임워크
- `pandas>=2.0.0` - 데이터 처리
- `numpy>=1.24.0` - 수치 계산

### 파일 구조
```
pykrx-server/
├── simple_server.py          # 메인 MCP 서버
├── server.py                 # 원본 상세 서버 (참고용)
├── run_server.py             # 서버 실행 스크립트
├── requirements.txt          # 의존성 패키지
├── mcp.json                  # MCP 서버 설정
├── README.md                # 이 파일
├── test_simple_client.py     # 기본 테스트
├── test_all_features.py      # 전체 기능 테스트
├── test_extended.py          # 확장 기능 테스트
├── test_final.py             # 최종 종합 테스트
├── test_pykrx.py            # pykrx 라이브러리 테스트
└── test_mcp_client.py       # MCP 클라이언트 테스트
```

## 📝 참고사항

- 한국거래소의 거래일 기준으로 데이터가 제공됩니다
- 일부 데이터는 실시간이 아닌 지연된 데이터일 수 있습니다
- pykrx 라이브러리의 제약사항이 적용됩니다
- 네트워크 연결이 필요합니다

## 🤝 기여

이슈나 개선사항이 있으면 언제든 연락주세요!

---

💡 **Tip**: `test_final.py`를 실행하면 모든 기능을 한 번에 테스트할 수 있습니다!

```bash
python run_server.py
```

또는

```bash
python server.py
```

## 사용 예시

### 종목 정보 조회
```json
{
  "tool": "get_stock_info",
  "arguments": {
    "ticker": "005930"
  }
}
```

### 주가 데이터 조회
```json
{
  "tool": "get_stock_prices", 
  "arguments": {
    "ticker": "005930",
    "start_date": "20240101",
    "end_date": "20240131",
    "period": "day"
  }
}
```

### 종목 검색
```json
{
  "tool": "search_ticker",
  "arguments": {
    "name": "삼성",
    "market": "ALL"
  }
}
```

## 주의사항

- pykrx는 한국거래소의 공개 데이터를 사용합니다
- 실시간 데이터가 아닌 과거 데이터를 제공합니다
- 거래일 기준으로 데이터가 제공됩니다
- 일부 데이터는 해당일 다음 거래일에 업데이트됩니다

## 에러 처리

- 잘못된 종목 코드: "종목 코드를 찾을 수 없습니다" 메시지 반환
- 데이터 없음: "해당 기간에 대한 데이터가 없습니다" 메시지 반환
- pykrx 미설치: 설치 안내 메시지 반환

## 개발자 정보

- **라이브러리**: pykrx
- **프로토콜**: MCP (Model Context Protocol)
- **데이터 소스**: 한국거래소 (KRX)

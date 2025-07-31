import { Router, Request, Response, NextFunction } from 'express';
import { AppError } from '../middleware/errorHandler';
import { ApiResponse, StockInfo, StockPrice } from '../types';
import { getCache, setCache } from '../services/redis';

const router = Router();

// 임시 주식 데이터
const stocksData: StockInfo[] = [
  {
    symbol: 'AAPL',
    name: '애플',
    market: 'NASDAQ',
    sector: 'Technology',
    price: 185.25,
    change: 2.35,
    changePercent: 1.29,
    volume: 45123456,
    marketCap: 2890000000000,
    updatedAt: new Date(),
  },
  {
    symbol: 'TSLA',
    name: '테슬라',
    market: 'NASDAQ',
    sector: 'Automotive',
    price: 245.67,
    change: -5.23,
    changePercent: -2.08,
    volume: 32456789,
    marketCap: 780000000000,
    updatedAt: new Date(),
  },
  {
    symbol: '005930',
    name: '삼성전자',
    market: 'KOSPI',
    sector: 'Technology',
    price: 68500,
    change: 1500,
    changePercent: 2.24,
    volume: 12345678,
    marketCap: 408000000000000,
    updatedAt: new Date(),
  },
];

// 주식 목록 조회
router.get('/', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { market, sector, search, limit = 20, offset = 0 } = req.query;

    let filteredStocks = [...stocksData];

    // 필터링
    if (market) {
      filteredStocks = filteredStocks.filter(stock => stock.market === market);
    }

    if (sector) {
      filteredStocks = filteredStocks.filter(stock => stock.sector === sector);
    }

    if (search) {
      const searchTerm = (search as string).toLowerCase();
      filteredStocks = filteredStocks.filter(stock => 
        stock.name.toLowerCase().includes(searchTerm) ||
        stock.symbol.toLowerCase().includes(searchTerm)
      );
    }

    // 페이지네이션
    const paginatedStocks = filteredStocks.slice(
      Number(offset),
      Number(offset) + Number(limit)
    );

    const response: ApiResponse<StockInfo[]> = {
      success: true,
      data: paginatedStocks,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 특정 주식 정보 조회
router.get('/:symbol', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { symbol } = req.params;
    
    // 캐시에서 먼저 확인
    const cacheKey = `stock:${symbol}`;
    let stockInfo = await getCache(cacheKey);

    if (!stockInfo) {
      // 데이터베이스나 외부 API에서 조회
      stockInfo = stocksData.find(stock => 
        stock.symbol.toLowerCase() === symbol.toLowerCase()
      );

      if (!stockInfo) {
        throw new AppError('주식 정보를 찾을 수 없습니다', 404);
      }

      // 캐시에 저장 (5분)
      await setCache(cacheKey, stockInfo, 300);
    }

    const response: ApiResponse<StockInfo> = {
      success: true,
      data: stockInfo,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 주식 가격 히스토리 조회
router.get('/:symbol/history', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { symbol } = req.params;
    const { period = '1M', interval = '1d' } = req.query;

    // 모크 히스토리 데이터 생성
    const historyData: StockPrice[] = generateMockHistory(symbol, period as string);

    const response: ApiResponse<StockPrice[]> = {
      success: true,
      data: historyData,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 실시간 주식 가격 조회
router.get('/:symbol/realtime', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { symbol } = req.params;

    const stock = stocksData.find(s => s.symbol.toLowerCase() === symbol.toLowerCase());
    if (!stock) {
      throw new AppError('주식 정보를 찾을 수 없습니다', 404);
    }

    // 실시간 가격 시뮬레이션 (랜덤 변동)
    const priceVariation = (Math.random() - 0.5) * 2; // -1% ~ +1%
    const currentPrice = stock.price * (1 + priceVariation / 100);
    const change = currentPrice - stock.price;
    const changePercent = (change / stock.price) * 100;

    const realtimeData = {
      symbol: stock.symbol,
      price: Number(currentPrice.toFixed(2)),
      change: Number(change.toFixed(2)),
      changePercent: Number(changePercent.toFixed(2)),
      volume: stock.volume + Math.floor(Math.random() * 100000),
      timestamp: new Date(),
      bid: currentPrice - 0.01,
      ask: currentPrice + 0.01,
      high: stock.price * 1.02,
      low: stock.price * 0.98,
    };

    const response: ApiResponse = {
      success: true,
      data: realtimeData,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 시장 요약 정보
router.get('/market/summary', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const marketSummary = {
      kospi: {
        index: 2485.67,
        change: 15.23,
        changePercent: 0.62,
        volume: 456789123,
      },
      kosdaq: {
        index: 845.32,
        change: -8.45,
        changePercent: -0.99,
        volume: 234567890,
      },
      nasdaq: {
        index: 14256.78,
        change: 125.45,
        changePercent: 0.89,
        volume: 3456789012,
      },
      sp500: {
        index: 4523.12,
        change: 23.67,
        changePercent: 0.53,
        volume: 2345678901,
      },
      updatedAt: new Date(),
    };

    const response: ApiResponse = {
      success: true,
      data: marketSummary,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 모크 히스토리 데이터 생성 함수
function generateMockHistory(symbol: string, period: string): StockPrice[] {
  const stock = stocksData.find(s => s.symbol === symbol);
  if (!stock) return [];

  const basePrice = stock.price;
  const data: StockPrice[] = [];
  
  let days = 30; // 기본 1개월
  if (period === '1W') days = 7;
  else if (period === '3M') days = 90;
  else if (period === '1Y') days = 365;

  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);

    const randomVariation = (Math.random() - 0.5) * 0.1; // -5% ~ +5%
    const price = basePrice * (1 + randomVariation);
    
    data.push({
      symbol,
      timestamp: date,
      open: price * (1 + (Math.random() - 0.5) * 0.02),
      high: price * (1 + Math.random() * 0.03),
      low: price * (1 - Math.random() * 0.03),
      close: price,
      volume: Math.floor(Math.random() * 50000000) + 10000000,
    });
  }

  return data;
}

export default router;

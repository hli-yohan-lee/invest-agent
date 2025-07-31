import rateLimit from 'express-rate-limit';

export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15분
  max: 100, // 15분당 최대 100 요청
  message: {
    success: false,
    message: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.',
    timestamp: new Date(),
  },
  standardHeaders: true,
  legacyHeaders: false,
});

export const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15분
  max: 5, // 15분당 최대 5 로그인 시도
  message: {
    success: false,
    message: '로그인 시도가 너무 많습니다. 15분 후 다시 시도해주세요.',
    timestamp: new Date(),
  },
  standardHeaders: true,
  legacyHeaders: false,
});

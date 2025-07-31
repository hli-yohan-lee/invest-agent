import { Router, Request, Response, NextFunction } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { AppError } from '../middleware/errorHandler';
import { authRateLimiter } from '../middleware/rateLimiter';
import { ApiResponse } from '../types';

const router = Router();

// 임시 사용자 데이터 (실제로는 MongoDB 모델 사용)
const users: any[] = [];

// 스키마 검증
const registerSchema = z.object({
  email: z.string().email('유효한 이메일을 입력해주세요'),
  username: z.string().min(2, '사용자명은 최소 2자 이상이어야 합니다'),
  password: z.string().min(6, '비밀번호는 최소 6자 이상이어야 합니다'),
});

const loginSchema = z.object({
  email: z.string().email('유효한 이메일을 입력해주세요'),
  password: z.string().min(1, '비밀번호를 입력해주세요'),
});

// 회원가입
router.post('/register', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const validation = registerSchema.safeParse(req.body);
    if (!validation.success) {
      throw new AppError(validation.error.errors[0].message, 400);
    }

    const { email, username, password } = validation.data;

    // 이메일 중복 체크
    const existingUser = users.find(user => user.email === email);
    if (existingUser) {
      throw new AppError('이미 존재하는 이메일입니다', 400);
    }

    // 비밀번호 해시화
    const saltRounds = 12;
    const passwordHash = await bcrypt.hash(password, saltRounds);

    // 사용자 생성
    const newUser = {
      id: (users.length + 1).toString(),
      email,
      username,
      passwordHash,
      createdAt: new Date(),
      updatedAt: new Date(),
      isActive: true,
      role: 'user',
    };

    users.push(newUser);

    // JWT 토큰 생성
    const jwtSecret = process.env.JWT_SECRET || 'default-secret-key';
    const expiresIn = process.env.JWT_EXPIRES_IN || '7d';
    const token = jwt.sign(
      { id: newUser.id, email: newUser.email, role: newUser.role },
      jwtSecret,
      { expiresIn }
    );

    const response: ApiResponse = {
      success: true,
      data: {
        user: {
          id: newUser.id,
          email: newUser.email,
          username: newUser.username,
          role: newUser.role,
        },
        token,
      },
      message: '회원가입이 완료되었습니다',
      timestamp: new Date(),
    };

    res.status(201).json(response);
  } catch (error) {
    next(error);
  }
});

// 로그인
router.post('/login', authRateLimiter, async (req: Request, res: Response, next: NextFunction) => {
  try {
    const validation = loginSchema.safeParse(req.body);
    if (!validation.success) {
      throw new AppError(validation.error.errors[0].message, 400);
    }

    const { email, password } = validation.data;

    // 사용자 조회
    const user = users.find(u => u.email === email);
    if (!user) {
      throw new AppError('이메일 또는 비밀번호가 잘못되었습니다', 401);
    }

    // 비밀번호 확인
    const isPasswordValid = await bcrypt.compare(password, user.passwordHash);
    if (!isPasswordValid) {
      throw new AppError('이메일 또는 비밀번호가 잘못되었습니다', 401);
    }

    // 활성 사용자 체크
    if (!user.isActive) {
      throw new AppError('비활성화된 계정입니다', 401);
    }

    // 로그인 시간 업데이트
    user.lastLoginAt = new Date();

    // JWT 토큰 생성
    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET as string,
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    const response: ApiResponse = {
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          role: user.role,
        },
        token,
      },
      message: '로그인이 완료되었습니다',
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 토큰 검증
router.get('/verify', async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      throw new AppError('토큰이 필요합니다', 401);
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET as string) as any;
    const user = users.find(u => u.id === decoded.id);

    if (!user || !user.isActive) {
      throw new AppError('유효하지 않은 토큰입니다', 401);
    }

    const response: ApiResponse = {
      success: true,
      data: {
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          role: user.role,
        },
      },
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

export default router;

import { Request, Response, NextFunction } from 'express';
import { ApiResponse } from '../types';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  let err = error as AppError;

  // 기본 에러 설정
  if (!err.statusCode) {
    err.statusCode = 500;
  }

  // MongoDB validation error
  if (error.name === 'ValidationError') {
    const message = Object.values((error as any).errors)
      .map((val: any) => val.message)
      .join(', ');
    err = new AppError(message, 400);
  }

  // MongoDB duplicate field error
  if ((error as any).code === 11000) {
    const field = Object.keys((error as any).keyValue)[0];
    const message = `${field}가 이미 존재합니다.`;
    err = new AppError(message, 400);
  }

  // JWT error
  if (error.name === 'JsonWebTokenError') {
    err = new AppError('유효하지 않은 토큰입니다.', 401);
  }

  // JWT expired error
  if (error.name === 'TokenExpiredError') {
    err = new AppError('토큰이 만료되었습니다.', 401);
  }

  const response: ApiResponse = {
    success: false,
    message: err.message || '서버 오류가 발생했습니다.',
    error: process.env.NODE_ENV === 'development' ? err.stack : undefined,
    timestamp: new Date(),
  };

  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    statusCode: err.statusCode,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
  });

  res.status(err.statusCode).json(response);
};

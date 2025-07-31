import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { AppError } from '../middleware/errorHandler';
import { ApiResponse, ChatMessage } from '../types';

interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

const router = Router();

// 임시 메시지 저장소
const messages: ChatMessage[] = [];

// 스키마 검증
const sendMessageSchema = z.object({
  content: z.string().min(1, '메시지 내용을 입력해주세요'),
  planId: z.string().optional(),
  type: z.enum(['user']).default('user'),
});

// 메시지 목록 조회
router.get('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const { planId, limit = 50, offset = 0 } = req.query;

    let userMessages = messages.filter(msg => msg.userId === req.user!.id);

    if (planId) {
      userMessages = userMessages.filter(msg => msg.planId === planId);
    }

    // 최신 메시지부터 정렬
    userMessages.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

    // 페이지네이션
    const paginatedMessages = userMessages.slice(
      Number(offset),
      Number(offset) + Number(limit)
    );

    const response: ApiResponse<ChatMessage[]> = {
      success: true,
      data: paginatedMessages,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 메시지 전송
router.post('/send', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const validation = sendMessageSchema.safeParse(req.body);
    if (!validation.success) {
      throw new AppError(validation.error.errors[0].message, 400);
    }

    const { content, planId, type } = validation.data;

    // 사용자 메시지 생성
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      userId: req.user!.id,
      planId,
      type,
      content,
      timestamp: new Date(),
    };

    messages.push(userMessage);

    // AI 응답 시뮬레이션
    const aiResponse: ChatMessage = {
      id: `msg-${Date.now() + 1}-${Math.random().toString(36).substr(2, 9)}`,
      userId: req.user!.id,
      planId,
      type: 'assistant',
      content: generateAIResponse(content),
      timestamp: new Date(Date.now() + 1000), // 1초 후
      metadata: {
        tokens: Math.floor(Math.random() * 100) + 50,
      },
    };

    // 1초 후 AI 응답 추가
    setTimeout(() => {
      messages.push(aiResponse);
      
      // 소켓으로 AI 응답 전송
      if ((global as any).socketBroadcast) {
        (global as any).socketBroadcast.message(req.user!.id, aiResponse);
      }
    }, 1000);

    const response: ApiResponse<ChatMessage> = {
      success: true,
      data: userMessage,
      message: '메시지가 전송되었습니다',
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 메시지 삭제
router.delete('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const messageIndex = messages.findIndex(
      msg => msg.id === req.params.id && msg.userId === req.user!.id
    );

    if (messageIndex === -1) {
      throw new AppError('메시지를 찾을 수 없습니다', 404);
    }

    messages.splice(messageIndex, 1);

    const response: ApiResponse = {
      success: true,
      message: '메시지가 삭제되었습니다',
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// AI 응답 생성 함수 (임시)
function generateAIResponse(userMessage: string): string {
  const responses = [
    `"${userMessage}"에 대해 분석해보겠습니다. 투자 관련 정보를 수집하고 있습니다...`,
    `요청하신 "${userMessage}" 관련해서 다음과 같은 분석을 진행하겠습니다: 1) 시장 데이터 수집 2) 기술적 분석 3) 기본적 분석`,
    `네, "${userMessage}"에 대한 투자 분석을 시작하겠습니다. 워크플로우 탭에서 진행 상황을 확인하실 수 있습니다.`,
    `"${userMessage}" 관련 정보를 네이버증권, 토스증권 등에서 수집하여 종합적인 분석 보고서를 작성해드리겠습니다.`,
    `투자 분석 요청을 받았습니다. "${userMessage}"에 대한 데이터 수집부터 보고서 생성까지 자동으로 진행하겠습니다.`,
  ];

  return responses[Math.floor(Math.random() * responses.length)];
}

export default router;

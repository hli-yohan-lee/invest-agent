import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { AppError } from '../middleware/errorHandler';
import { ApiResponse, Plan, PlanStep } from '../types';

interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

const router = Router();

// 임시 데이터 저장소
const plans: Plan[] = [];

// 스키마 검증
const createPlanSchema = z.object({
  title: z.string().min(1, '제목을 입력해주세요'),
  description: z.string().min(1, '설명을 입력해주세요'),
  steps: z.array(z.object({
    title: z.string().min(1, '단계 제목을 입력해주세요'),
    description: z.string().min(1, '단계 설명을 입력해주세요'),
    order: z.number().min(0),
    type: z.enum(['data_collection', 'analysis', 'report_generation']),
    mcpModules: z.array(z.string()),
    parameters: z.record(z.any()),
    prompt: z.string().optional(),
    useAgent: z.boolean().optional(),
  })),
});

// 계획 목록 조회
router.get('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const userPlans = plans.filter(plan => plan.userId === req.user!.id);

    const response: ApiResponse<Plan[]> = {
      success: true,
      data: userPlans,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 계획 상세 조회
router.get('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const plan = plans.find(p => p.id === req.params.id && p.userId === req.user!.id);

    if (!plan) {
      throw new AppError('계획을 찾을 수 없습니다', 404);
    }

    const response: ApiResponse<Plan> = {
      success: true,
      data: plan,
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 계획 생성
router.post('/', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const validation = createPlanSchema.safeParse(req.body);
    if (!validation.success) {
      throw new AppError(validation.error.errors[0].message, 400);
    }

    const { title, description, steps } = validation.data;

    const planId = (plans.length + 1).toString();
    
    const planSteps: PlanStep[] = steps.map((step, index) => ({
      id: `${planId}-step-${index + 1}`,
      planId,
      title: step.title,
      description: step.description,
      order: step.order,
      type: step.type,
      mcpModules: step.mcpModules,
      parameters: step.parameters,
      prompt: step.prompt,
      useAgent: step.useAgent || false,
      status: 'pending',
    }));

    const newPlan: Plan = {
      id: planId,
      userId: req.user!.id,
      title,
      description,
      steps: planSteps,
      status: 'draft',
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    plans.push(newPlan);

    const response: ApiResponse<Plan> = {
      success: true,
      data: newPlan,
      message: '계획이 생성되었습니다',
      timestamp: new Date(),
    };

    res.status(201).json(response);
  } catch (error) {
    next(error);
  }
});

// 계획 수정
router.put('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const planIndex = plans.findIndex(p => p.id === req.params.id && p.userId === req.user!.id);

    if (planIndex === -1) {
      throw new AppError('계획을 찾을 수 없습니다', 404);
    }

    const plan = plans[planIndex];

    if (plan.status === 'executing') {
      throw new AppError('실행 중인 계획은 수정할 수 없습니다', 400);
    }

    const { title, description, steps } = req.body;

    if (title) plan.title = title;
    if (description) plan.description = description;
    if (steps) {
      plan.steps = steps.map((step: any, index: number) => ({
        ...step,
        id: step.id || `${plan.id}-step-${index + 1}`,
        planId: plan.id,
        status: step.status || 'pending',
      }));
    }

    plan.updatedAt = new Date();

    const response: ApiResponse<Plan> = {
      success: true,
      data: plan,
      message: '계획이 수정되었습니다',
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 계획 삭제
router.delete('/:id', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const planIndex = plans.findIndex(p => p.id === req.params.id && p.userId === req.user!.id);

    if (planIndex === -1) {
      throw new AppError('계획을 찾을 수 없습니다', 404);
    }

    const plan = plans[planIndex];

    if (plan.status === 'executing') {
      throw new AppError('실행 중인 계획은 삭제할 수 없습니다', 400);
    }

    plans.splice(planIndex, 1);

    const response: ApiResponse = {
      success: true,
      message: '계획이 삭제되었습니다',
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

// 계획 실행
router.post('/:id/execute', async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const plan = plans.find(p => p.id === req.params.id && p.userId === req.user!.id);

    if (!plan) {
      throw new AppError('계획을 찾을 수 없습니다', 404);
    }

    if (plan.status === 'executing') {
      throw new AppError('이미 실행 중인 계획입니다', 400);
    }

    // 계획 상태 업데이트
    plan.status = 'executing';
    plan.executionStartAt = new Date();
    plan.updatedAt = new Date();

    // 실제 실행 로직은 백그라운드 작업으로 처리
    // 여기서는 워크플로우 실행 서비스를 호출
    setTimeout(() => {
      plan.status = 'completed';
      plan.executionEndAt = new Date();
      
      // 소켓으로 실행 완료 알림
      if ((global as any).socketBroadcast) {
        (global as any).socketBroadcast.workflowStatus(plan.id, {
          status: 'completed',
          planId: plan.id,
          completedAt: plan.executionEndAt,
        });
      }
    }, 5000); // 5초 후 완료로 시뮬레이션

    const response: ApiResponse = {
      success: true,
      data: { planId: plan.id, status: plan.status },
      message: '계획 실행이 시작되었습니다',
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    next(error);
  }
});

export default router;

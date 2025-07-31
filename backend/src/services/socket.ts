import { Server as SocketIOServer, Socket } from 'socket.io';
import jwt from 'jsonwebtoken';

interface AuthenticatedSocket extends Socket {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export const setupSocketIO = (io: SocketIOServer): void => {
  // 인증 미들웨어
  io.use((socket: AuthenticatedSocket, next) => {
    try {
      const token = socket.handshake.auth.token;
      if (!token) {
        return next(new Error('Authentication token required'));
      }

      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
      socket.user = {
        id: decoded.id,
        email: decoded.email,
        role: decoded.role,
      };

      next();
    } catch (error) {
      next(new Error('Invalid token'));
    }
  });

  io.on('connection', (socket: AuthenticatedSocket) => {
    console.log(`User connected: ${socket.user?.id}`);

    // 사용자별 룸 참가
    if (socket.user?.id) {
      socket.join(`user:${socket.user.id}`);
    }

    // 채팅 메시지 수신
    socket.on('send_message', (data) => {
      console.log('Message received:', data);
      // 메시지 처리 로직
      socket.emit('message_received', {
        id: Date.now().toString(),
        ...data,
        timestamp: new Date(),
      });
    });

    // 워크플로우 실행 상태 구독
    socket.on('subscribe_workflow', (planId: string) => {
      socket.join(`workflow:${planId}`);
      console.log(`User ${socket.user?.id} subscribed to workflow ${planId}`);
    });

    // 워크플로우 실행 상태 구독 해제
    socket.on('unsubscribe_workflow', (planId: string) => {
      socket.leave(`workflow:${planId}`);
      console.log(`User ${socket.user?.id} unsubscribed from workflow ${planId}`);
    });

    // 연결 해제
    socket.on('disconnect', () => {
      console.log(`User disconnected: ${socket.user?.id}`);
    });
  });

  // 워크플로우 실행 상태 브로드캐스트 함수들
  const broadcastWorkflowStatus = (planId: string, status: any) => {
    io.to(`workflow:${planId}`).emit('workflow_status', status);
  };

  const broadcastStepStatus = (planId: string, stepId: string, status: any) => {
    io.to(`workflow:${planId}`).emit('step_status', { stepId, status });
  };

  const broadcastMessage = (userId: string, message: any) => {
    io.to(`user:${userId}`).emit('new_message', message);
  };

  // 전역 함수로 export
  (global as any).socketBroadcast = {
    workflowStatus: broadcastWorkflowStatus,
    stepStatus: broadcastStepStatus,
    message: broadcastMessage,
  };
};

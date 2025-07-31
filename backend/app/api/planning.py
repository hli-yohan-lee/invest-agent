"""
플래닝 관련 API 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.conversation import (
    ChatRequest, 
    ChatResponse, 
    Conversation, 
    ConversationCreate,
    Plan,
    PlanCreate
)
from app.services.ai_planner import AIPlanner
from app.services.conversation_service import ConversationService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# 서비스 인스턴스
# ai_planner는 각 요청마다 새로 생성
conversation_service = ConversationService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """채팅 메시지 처리 및 AI 플래닝"""
    user_id = token_data.get("user_id")
    logger.info("채팅 요청 처리", user_id=user_id, message_length=len(request.message))
    
    try:
        # 대화 세션 처리
        conversation = await conversation_service.get_or_create_conversation(
            db, user_id, request.conversation_id
        )
        
        # 사용자 메시지 저장
        user_message = await conversation_service.add_message(
            db, conversation.id, "user", request.message
        )
        
        # AI 플래닝 실행 (클라이언트 API 키 사용)
        ai_planner = AIPlanner(api_key=request.openai_api_key)
        planning_result = await ai_planner.generate_plan(request.message)
        
        # AI 응답 메시지 저장
        ai_message = await conversation_service.add_message(
            db, conversation.id, "assistant", planning_result["response"]
        )
        
        # 플랜 생성 (실행 가능한 계획이 있는 경우)
        plan = None
        if planning_result.get("plan"):
            plan_data = PlanCreate(
                conversation_id=conversation.id,
                user_query=request.message,
                plan_content=planning_result["plan"],
                execution_steps=planning_result.get("steps", []),
                estimated_time=planning_result.get("estimated_time")
            )
            plan = await conversation_service.create_plan(db, plan_data)
        
        return ChatResponse(
            message=ai_message,
            conversation_id=conversation.id,
            plan=plan,
            suggestions=planning_result.get("suggestions", [])
        )
        
    except Exception as e:
        logger.error("채팅 처리 중 오류", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="채팅 처리 중 오류가 발생했습니다"
        )

@router.post("/chat-test", response_model=ChatResponse)
async def chat_test(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """채팅 메시지 처리 및 AI 플래닝 (인증 없는 테스트용)"""
    logger.info("테스트 채팅 요청 처리", message_length=len(request.message))
    
    try:
        # 임시 사용자 ID 사용
        user_id = 1
        
        # 대화 세션 처리
        conversation = await conversation_service.get_or_create_conversation(
            db, user_id, request.conversation_id
        )
        
        # 사용자 메시지 저장
        user_message = await conversation_service.add_message(
            db, conversation.id, "user", request.message
        )
        
        # AI 플래닝 실행 (클라이언트 API 키 사용)
        ai_planner = AIPlanner(api_key=request.openai_api_key)
        planning_result = await ai_planner.generate_plan(request.message)
        
        # AI 응답 메시지 저장
        ai_message = await conversation_service.add_message(
            db, conversation.id, "assistant", planning_result["response"]
        )
        
        # 응답 반환
        return ChatResponse(
            message=ai_message,
            conversation_id=conversation.id,
            plan=None,
            suggestions=planning_result.get("suggestions", [])
        )
        
    except Exception as e:
        logger.error("테스트 채팅 처리 오류", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/chat-test")
async def chat_test(request: ChatRequest):
    """테스트용 채팅 엔드포인트 (인증 없음)"""
    logger.info("테스트 채팅 요청", message_length=len(request.message))
    
    try:
        # AI 플래닝 실행 (클라이언트 API 키 사용)
        ai_planner = AIPlanner(api_key=request.openai_api_key)
        planning_result = await ai_planner.generate_plan(request.message)
        
        # 간단한 응답 반환
        return {
            "message": {
                "id": 1,
                "role": "assistant",
                "content": planning_result["response"],
                "created_at": "2024-01-01T00:00:00"
            },
            "conversation_id": 1,
            "plan": None,
            "suggestions": planning_result.get("suggestions", [])
        }
        
    except Exception as e:
        logger.error("테스트 채팅 오류", error=str(e))
        return {
            "message": {
                "id": 1,
                "role": "assistant", 
                "content": f"죄송합니다. 오류가 발생했습니다: {str(e)}",
                "created_at": "2024-01-01T00:00:00"
            },
            "conversation_id": 1,
            "plan": None,
            "suggestions": []
        }

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """사용자 대화 목록 조회"""
    user_id = token_data.get("user_id")
    
    conversations = await conversation_service.get_user_conversations(
        db, user_id, skip, limit
    )
    
    return conversations

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """특정 대화 조회"""
    user_id = token_data.get("user_id")
    
    conversation = await conversation_service.get_conversation_with_messages(
        db, conversation_id, user_id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화를 찾을 수 없습니다"
        )
    
    return conversation

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    request: ConversationCreate,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """새 대화 생성"""
    user_id = token_data.get("user_id")
    
    conversation = await conversation_service.create_conversation(
        db, user_id, request.title
    )
    
    return conversation

@router.put("/plans/{plan_id}/approve")
async def approve_plan(
    plan_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """플랜 승인"""
    user_id = token_data.get("user_id")
    
    plan = await conversation_service.approve_plan(db, plan_id, user_id)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플랜을 찾을 수 없습니다"
        )
    
    return {"message": "플랜이 승인되었습니다", "plan_id": plan_id}

@router.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(
    plan_id: int,
    token_data: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """플랜 상세 조회"""
    user_id = token_data.get("user_id")
    
    plan = await conversation_service.get_plan(db, plan_id, user_id)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="플랜을 찾을 수 없습니다"
        )
    
    return plan

@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):
    """스트리밍 채팅 엔드포인트 (인증 없음)"""
    logger.info("스트리밍 채팅 요청", message_length=len(request.message), mode=request.mode)
    
    # API 키 로깅 (보안상 일부만)
    api_key_preview = request.openai_api_key[:10] + "..." if request.openai_api_key else "None"
    logger.info(f"API 키 상태: {api_key_preview}")
    
    async def generate_stream():
        try:
            # AI 플래너로 스트리밍 응답 생성
            ai_planner = AIPlanner(api_key=request.openai_api_key)
            
            # 워크플로우 모드인 경우 대화 내용과 함께 전달
            if request.mode == "workflow" and request.chat_history:
                query = f"다음 대화 내용을 워크플로우로 변환해주세요:\n\n{request.chat_history}\n\n사용자 추가 요청: {request.message}"
                logger.info(f"워크플로우 변환 쿼리 길이: {len(query)}")
            else:
                query = request.message
            
            async for chunk in ai_planner.generate_plan_stream(query, request.mode):
                # SSE 형식으로 데이터 전송
                yield f"data: {json.dumps(chunk)}\n\n"
                
        except Exception as e:
            logger.error("스트리밍 채팅 오류", error=str(e))
            error_chunk = {
                "type": "error",
                "content": f"오류가 발생했습니다: {str(e)}"
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

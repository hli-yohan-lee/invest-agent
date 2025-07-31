# AI Agent Workflow Platform - Backend

투자 분석 AI Agent 워크플로우 플랫폼의 FastAPI 백엔드 서버입니다.

## 기술 스택

- **FastAPI**: 고성능 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **PostgreSQL**: 메인 데이터베이스 (asyncpg 드라이버)
- **Redis**: 캐싱 및 세션 관리
- **OpenAI**: AI 플래닝 서비스
- **Alembic**: 데이터베이스 마이그레이션
- **Pydantic**: 데이터 검증 및 설정 관리

## 주요 기능

### 1. 인증 시스템
- JWT 기반 사용자 인증
- 회원가입, 로그인, 비밀번호 변경
- 사용자 프로필 관리

### 2. AI 플래닝 시스템
- OpenAI GPT-4 기반 투자 분석 플랜 생성
- 사용자 요청 분석 및 구조화된 실행 계획 수립
- 대화형 인터페이스

### 3. 워크플로우 엔진
- 시각적 워크플로우 편집 및 실행
- 노드 기반 작업 정의
- MCP 모듈 연동

### 4. MCP 서버 연동
- Model Context Protocol 서버와의 통신
- 동적 모듈 로딩 및 실행
- 투자 데이터 수집 및 분석 도구

### 5. 결과 관리
- 테이블 및 보고서 형태의 결과 출력
- 편집 가능한 마크다운 보고서
- 데이터 내보내기 기능

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env.example` 파일을 참고하여 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.

```bash
cp .env.example .env
```

필수 환경 변수:
- `DATABASE_URL`: PostgreSQL 연결 URL
- `SECRET_KEY`: JWT 토큰 시크릿 키
- `OPENAI_API_KEY`: OpenAI API 키 (선택사항)

### 3. 데이터베이스 마이그레이션
```bash
alembic upgrade head
```

### 4. 서버 실행
```bash
# 개발 모드
python main.py

# 또는
python start_server.py

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 URL에서 접근할 수 있습니다:
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 헬스 체크: http://localhost:8000/health

## API 엔드포인트

### 인증 (Authentication)
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인 (OAuth2 호환)
- `POST /api/auth/login/email` - 이메일 로그인
- `GET /api/auth/me` - 현재 사용자 정보
- `POST /api/auth/refresh` - 토큰 갱신

### 사용자 (Users)
- `GET /api/users/profile` - 프로필 조회
- `PUT /api/users/profile` - 프로필 업데이트
- `POST /api/users/change-password` - 비밀번호 변경
- `DELETE /api/users/account` - 계정 삭제

### 플래닝 (Planning)
- `POST /api/planning/chat` - 채팅 및 AI 플래닝
- `GET /api/planning/conversations` - 대화 목록
- `POST /api/planning/conversations` - 새 대화 생성
- `GET /api/planning/conversations/{id}` - 대화 상세
- `PUT /api/planning/plans/{id}/approve` - 플랜 승인

### 워크플로우 (Workflow)
- `GET /api/workflow/` - 워크플로우 목록
- `POST /api/workflow/` - 워크플로우 생성
- `GET /api/workflow/{id}` - 워크플로우 상세
- `PUT /api/workflow/{id}` - 워크플로우 업데이트
- `POST /api/workflow/{id}/execute` - 워크플로우 실행

### 결과 (Results)
- `GET /api/results/` - 결과 목록
- `GET /api/results/{id}` - 결과 상세
- `GET /api/results/reports` - 보고서 목록
- `POST /api/results/reports` - 보고서 생성

### MCP (Model Context Protocol)
- `GET /api/mcp/modules` - MCP 모듈 목록
- `GET /api/mcp/modules/{id}` - MCP 모듈 상세
- `POST /api/mcp/modules/{id}/execute` - MCP 모듈 실행
- `GET /api/mcp/status` - MCP 서버 상태

## 데이터베이스 구조

### 주요 테이블
- `users` - 사용자 정보
- `conversations` - 대화 세션
- `messages` - 채팅 메시지
- `plans` - AI 생성 플랜
- `workflows` - 워크플로우 정의
- `workflow_nodes` - 워크플로우 노드
- `workflow_executions` - 실행 이력
- `execution_results` - 실행 결과
- `reports` - 보고서
- `data_tables` - 테이블 데이터
- `mcp_modules` - MCP 모듈 정보

## 개발 가이드

### 코드 구조
```
app/
├── api/           # API 라우터
├── core/          # 핵심 설정 (데이터베이스, 보안, 설정)
├── models/        # SQLAlchemy 모델
├── schemas/       # Pydantic 스키마
├── crud/          # 데이터베이스 CRUD 작업
├── services/      # 비즈니스 로직
└── utils/         # 유틸리티 함수
```

### 새로운 API 추가
1. `app/models/`에 데이터 모델 정의
2. `app/schemas/`에 Pydantic 스키마 정의
3. `app/crud/`에 CRUD 작업 구현
4. `app/services/`에 비즈니스 로직 구현
5. `app/api/`에 API 엔드포인트 추가
6. `main.py`에 라우터 등록

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Add new table"

# 마이그레이션 실행
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

## 배포

### Docker (예정)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 환경별 설정
- 개발: `DEBUG=True`, SQLite 또는 로컬 PostgreSQL
- 스테이징: `DEBUG=False`, 외부 PostgreSQL, Redis
- 프로덕션: `DEBUG=False`, 클러스터 환경, 모니터링

## 라이선스

MIT License

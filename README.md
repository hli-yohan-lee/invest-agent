# 🚀 AI Agent Workflow Platform

투자 분석을 위한 AI Agent 워크플로우 플랫폼입니다. Next.js 프론트엔드, FastAPI 백엔드, MCP(Model Context Protocol) 서버를 통합한 시스템입니다.

## ⚡ 빠른 시작

### 🎯 원클릭 실행 (권장)

루트 디렉토리에서 다음 배치 파일 중 하나를 실행하세요:

```bash
# 상세한 로그와 함께 모든 서버 시작
start-all-servers.bat

## 🚀 빠른 시작

### 방법 1: 원클릭 실행 (배치 파일)
```cmd
# 모든 의존성 설치 및 서버 시작
quick-start.bat

# 또는 직접 서버 시작 (의존성이 이미 설치된 경우)
start-all-servers.bat
```

### 방법 2: PowerShell 스크립트 실행
```powershell
# PowerShell 실행 정책 설정 (최초 1회만)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 모든 의존성 설치 및 서버 시작
.\quick-start.ps1

# 또는 직접 서버 시작 (의존성이 이미 설치된 경우)
.\start-all-servers.ps1
```

### 🛑 서버 종료

```cmd
# 배치 파일로 종료
stop-all-servers.bat
```

```powershell
# PowerShell로 종료
.\stop-all-servers.ps1
```

### ⚠️ 중요 사항

- **PowerShell 환경**: 
  - 명령어 연결 시 `&&` 대신 **반드시** `;`를 사용해야 합니다
  - 예: `cd backend && npm install` ❌ → `cd backend; npm install` ✅
  - 배치 파일(.bat)은 PowerShell에서도 정상 동작합니다
- **실행 정책**: PowerShell 스크립트(.ps1) 실행 시 실행 정책 설정이 필요할 수 있습니다
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **포트 충돌**: 3000, 8000 포트가 사용 중이면 서버 시작이 실패할 수 있습니다
- **권장사항**: Windows 환경에서는 `.bat` 파일 사용을 권장합니다

## 🏗️ 시스템 구성

- **프론트엔드**: Next.js 14 + TypeScript + Tailwind CSS
- **백엔드**: FastAPI + SQLAlchemy + SQLite
- **MCP 서버**: pykrx 기반 한국 주식 데이터 제공
- **AI**: OpenAI GPT-4 기반 투자 분석

## 📱 사용 방법

1. **서버 시작**: `start-all-servers.bat` 실행
2. **브라우저 접속**: http://localhost:3000 자동 열림
3. **API 키 설정**: 우상단 설정 버튼(⚙️)에서 OpenAI API 키 입력
4. **투자 분석**: 
   - 플래닝 탭에서 투자 질문 입력
   - `Ctrl + Enter`로 워크플로우 생성 및 이동
   - 워크플로우 탭에서 실행 버튼 클릭
   - 결과 탭에서 분석 결과 확인

## 🌐 서비스 주소

- **웹 애플리케이션**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **관리자 문서**: http://localhost:8000/redoc

## 📋 기능

### ✨ 주요 기능
- 🤖 AI 기반 투자 분석 플래닝
- 🔄 시각적 워크플로우 편집기
- 📊 실시간 한국 주식 데이터 연동
- 📈 종합 분석 결과 리포트
- ⚙️ 직관적인 설정 관리

### 🛠️ 기술 특징
- **실시간 스트리밍**: AI 응답 실시간 표시
- **MCP 연동**: 표준화된 데이터 소스 연결
- **상태 관리**: Zustand 기반 효율적 상태 관리
- **반응형 UI**: 모든 화면 크기 지원

## 🔧 개발자 가이드

### 수동 서버 실행

개발 중에는 각 서버를 개별적으로 실행할 수 있습니다:

**배치 파일 사용 (권장):**
```cmd
# 백엔드 서버
cd backend
python -m uvicorn main:app --reload --port 8000

# 프론트엔드 서버  
cd frontend
npm run dev

# MCP 서버
cd mcp-servers\pykrx-server
python server.py
```

**PowerShell 사용 시:**
```powershell
# 백엔드 서버
cd backend; python -m uvicorn main:app --reload --port 8000

# 프론트엔드 서버  
cd frontend; npm run dev

# MCP 서버
cd mcp-servers\pykrx-server; python server.py
```

**주의**: PowerShell에서는 `&&` 대신 `;`를 사용해야 합니다!

### 요구사항

- **Node.js** 18+ 
- **Python** 3.9+
- **npm** 또는 **yarn**
- **OpenAI API 키**

### 설치

```bash
# 프론트엔드 의존성
cd frontend && npm install

# 백엔드 의존성
cd backend && pip install -r requirements.txt

# MCP 서버 의존성
cd mcp-servers/pykrx-server && pip install -r requirements.txt
```

## 🔐 환경 설정

### OpenAI API 키
웹 애플리케이션에서 우상단 설정 버튼을 통해 API 키를 설정하세요.

### 데이터베이스
SQLite 파일이 자동으로 생성되며, 별도 설치가 필요하지 않습니다.

## 🚨 문제 해결

### 서버 시작 실패
1. `stop-all-servers.bat`으로 모든 프로세스 종료
2. `start-all-servers.bat`으로 재시작
3. 포트 충돌 시 다른 애플리케이션 종료

### API 연결 오류
1. 설정 메뉴에서 "OpenAI API 연결 테스트" 버튼 클릭
2. API 키 유효성 확인
3. 네트워크 연결 상태 확인

### 종속성 오류
```bash
# 프론트엔드 재설치
cd frontend && rm -rf node_modules package-lock.json && npm install

# 백엔드 재설치  
cd backend && pip install -r requirements.txt --force-reinstall
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 모든 배치 파일이 관리자 권한으로 실행되는지 확인
2. 방화벽이 포트 3000, 8000을 차단하지 않는지 확인
3. Node.js와 Python이 올바르게 설치되었는지 확인

---

💡 **빠른 시작**: `start-all-servers.bat` 실행 → 브라우저 자동 열림 → 설정에서 API 키 입력 → 투자 분석 시작!

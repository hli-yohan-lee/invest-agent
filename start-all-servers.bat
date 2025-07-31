@echo off
chcp 65001 >nul
echo ================================================================
echo    🚀 AI Agent Workflow Platform 서버 시작
echo ================================================================
echo.

REM 현재 디렉토리 확인
echo 📂 작업 디렉토리: %cd%
echo.

REM 기존 프로세스 종료 (오류 무시)
echo 🛑 기존 서버 프로세스 종료 중...
taskkill /f /im node.exe 2>nul
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul
echo    ✅ 기존 프로세스 정리 완료
echo.

REM 백엔드 서버 시작 (Python FastAPI)
echo 🐍 백엔드 서버 시작 중...
start "Backend Server" cmd /k "cd /d backend && python -m uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
echo    ✅ 백엔드 서버 시작됨 (http://localhost:8000)
echo.

REM 프론트엔드 서버 시작 (Next.js)
echo ⚛️  프론트엔드 서버 시작 중...
start "Frontend Server" cmd /k "cd /d frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo    ✅ 프론트엔드 서버 시작됨 (http://localhost:3000)
echo.

REM MCP 서버 시작 (pykrx)
echo 📊 MCP 서버 시작 중...
start "MCP Server" cmd /k "cd /d mcp-servers\pykrx-server && python server.py"
timeout /t 2 /nobreak >nul
echo    ✅ MCP 서버 시작됨
echo.

echo ================================================================
echo    🎉 모든 서버가 성공적으로 시작되었습니다!
echo ================================================================
echo.
echo 📱 서비스 접속 주소:
echo    • 프론트엔드: http://localhost:3000
echo    • 백엔드 API: http://localhost:8000
echo    • API 문서:   http://localhost:8000/docs
echo.
echo 💡 사용 방법:
echo    1. 브라우저에서 http://localhost:3000 접속
echo    2. 우상단 설정 버튼으로 OpenAI API 키 설정
echo    3. 플래닝 탭에서 투자 질문 입력
echo    4. Ctrl+Enter로 워크플로우 생성 및 실행
echo.
echo ⚠️  서버 종료 시: 각 터미널 창에서 Ctrl+C 누르기
echo.
echo 🔄 브라우저 자동 열기 중...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo 계속하려면 아무 키나 누르세요...
pause >nul

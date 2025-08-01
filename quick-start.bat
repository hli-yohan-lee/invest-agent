@echo off
chcp 65001 >nul
title AI Agent Platform - Quick Start

echo 🚀 AI Agent Workflow Platform 빠른 시작
echo.

REM 기존 프로세스 정리
taskkill /f /im node.exe 2>nul
taskkill /f /im python.exe 2>nul

echo 서버 시작 중...

REM 백그라운드에서 서버들 실행
start /min cmd /c "cd /d backend && python -m uvicorn main:app --reload --port 8000"
start /min cmd /c "cd /d frontend && npm run dev"
start /min cmd /c "cd /d mcp-servers\pykrx-server && python server.py"

echo.
echo ⏳ 서버 초기화 대기 중...
timeout /t 8 /nobreak >nul

echo.
echo ✅ 서버 시작 완료!
echo 🌐 브라우저가 자동으로 열립니다...

REM 브라우저 열기
start http://localhost:3000

echo.
echo 💡 서버 종료: stop-all-servers.bat 실행
echo.
echo ✅ 서버가 백그라운드에서 실행 중입니다.
echo 📝 로그 확인: 각 서버 창을 확인하세요.

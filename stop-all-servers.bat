@echo off
chcp 65001 >nul
echo ================================================================
echo    🛑 AI Agent Workflow Platform 서버 종료
echo ================================================================
echo.

echo 🔍 실행 중인 서버 프로세스 확인...

REM Node.js 프로세스 확인 및 종료
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq node.exe" ^| find "node.exe"') do (
    echo    • Node.js 프로세스 발견: %%i
)

REM Python 프로세스 확인 및 종료  
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" ^| find "python.exe"') do (
    echo    • Python 프로세스 발견: %%i
)

echo.
echo 🛑 모든 서버 프로세스 종료 중...

REM 프론트엔드 서버 종료 (Node.js)
taskkill /f /im node.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✅ 프론트엔드 서버 종료됨
) else (
    echo    ⚠️  프론트엔드 서버가 실행되지 않았음
)

REM 백엔드 서버 종료 (Python)
taskkill /f /im python.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✅ 백엔드 및 MCP 서버 종료됨
) else (
    echo    ⚠️  백엔드 서버가 실행되지 않았음
)

REM 특정 포트의 프로세스 종료 (추가 안전장치)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
    echo    ✅ 포트 3000 프로세스 종료됨
)

for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
    echo    ✅ 포트 8000 프로세스 종료됨
)

echo.
echo ================================================================
echo    ✅ 모든 서버가 성공적으로 종료되었습니다!
echo ================================================================
echo.
echo 🚀 다시 시작하려면: quick-start.bat 또는 start-all-servers.bat 실행

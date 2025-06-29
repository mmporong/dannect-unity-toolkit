@echo off
chcp 65001 > nul
setlocal

echo 🎮 Unity Rebuild Button CLI Runner (Windows)
echo ==================================================

REM 현재 스크립트의 디렉토리로 이동
cd /d "%~dp0"

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo 💡 Python 3.6 이상을 설치해주세요.
    pause
    exit /b 1
)

echo 📋 사용 가능한 액션:
echo    1. all_test         - 전체 테스트 실행
echo    2. create_button    - Rebuild 버튼 생성
echo    3. test_click       - 버튼 클릭 테스트
echo    4. debug_success_pop - Success_Pop 디버그
echo    5. check_events     - 이벤트 연결 상태 확인
echo.

set /p choice="실행할 액션 번호를 선택하세요 (1-5): "

if "%choice%"=="1" set action=all_test
if "%choice%"=="2" set action=create_button
if "%choice%"=="3" set action=test_click
if "%choice%"=="4" set action=debug_success_pop
if "%choice%"=="5" set action=check_events

if not defined action (
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

echo.
echo 🚀 Unity CLI 실행 중: %action%
echo ==================================================

python unity_cli_runner.py --action %action%

if %errorlevel% equ 0 (
    echo.
    echo 🎉 작업이 성공적으로 완료되었습니다!
) else (
    echo.
    echo ❌ 작업 실행 중 오류가 발생했습니다.
)

echo.
pause 
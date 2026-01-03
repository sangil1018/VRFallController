@echo off
chcp 65001 >nul
echo ====================================
echo VR 추락 시뮬레이터 컨트롤러 시작
echo ====================================
echo.

REM 가상환경 확인 및 활성화
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 의존성 설치 여부 확인
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo 의존성 설치 중...
    pip install -r requirements.txt
    echo.
)

REM 서버 시작
echo 서버를 시작합니다...
echo 웹 인터페이스: http://localhost:8000
echo 중지하려면 Ctrl+C를 누르세요
echo.

python main.py

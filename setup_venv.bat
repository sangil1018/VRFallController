@echo off
chcp 65001 >nul
echo ====================================
echo 가상환경 설정
echo ====================================
echo.

REM 가상환경이 이미 있는지 확인
if exist "venv\" (
    echo 가상환경이 이미 존재합니다.
) else (
    echo 가상환경 생성 중...
    python -m venv venv
    echo 가상환경이 생성되었습니다.
)

echo.
echo 가상환경 활성화 중...
call venv\Scripts\activate.bat

echo.
echo 의존성 설치 중...
pip install -r requirements.txt

echo.
echo ====================================
echo 설정 완료!
echo ====================================
echo.
echo 서버를 시작하려면:
echo   venv\Scripts\activate
echo   python main.py
echo.
echo 또는 간단하게:
echo   start.bat (일반 모드)
echo   start_test.bat (테스트 모드)
echo.
pause

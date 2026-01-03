@echo off
chcp 65001 >nul
echo ========================================
echo VRFallController EXE 빌드 시작
echo ========================================

rem 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: 가상환경을 찾을 수 없습니다. setup_venv.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

rem PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller를 설치합니다...
    pip install pyinstaller
)

rem 이전 빌드 정리
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

rem PyInstaller로 exe 빌드
echo.
echo 빌드 중...
pyinstaller VRFallController.spec

rem 빌드 결과 확인
if exist dist\VRFallController\VRFallController.exe (
    echo.
    echo ========================================
    echo 빌드 성공!
    echo 실행 파일 위치: dist\VRFallController\
    echo ========================================
    echo.
    echo 배포 방법:
    echo 1. dist\VRFallController 폴더 전체를 복사하여 배포
    echo 2. VRFallController.exe를 실행
    echo.
) else (
    echo.
    echo ========================================
    echo 빌드 실패! 오류를 확인하세요.
    echo ========================================
)

pause

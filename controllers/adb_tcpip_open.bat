@echo off
chcp 65001 >nul
echo ====================================
echo ADB TCP/IP 모드 활성화 중...
echo ====================================
echo.

adb devices

REM 연결된 모든 기기에 대해 5555 포트 개방
for /f "tokens=1" %%i in ('adb devices ^| findstr "device$"') do (
    echo Setting TCP/IP for %%i
    adb -s %%i tcpip 5555
)

echo 완료! 이제 USB를 뽑고 adb connect [IP] 명령을 사용하세요.
echo.

pause

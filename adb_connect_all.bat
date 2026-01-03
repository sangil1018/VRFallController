@echo off
chcp 65001 >nul
echo ====================================
echo 피코 디바이스 ADB 연결
echo ====================================
echo.

echo 피코4 디바이스 연결 중...
echo.

adb connect 192.168.1.101
adb connect 192.168.1.102
adb connect 192.168.1.103

echo.
echo ====================================
echo 연결 상태 확인
echo ====================================
adb devices

echo.
pause

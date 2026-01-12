@echo off
chcp 65001 >nul
echo ====================================
echo 피코 디바이스 ADB 연결
echo 디바이스의 IP 값을 체크해서 주소 수정
echo 3대 모두 실행
echo ====================================
echo.

echo 피코4 디바이스 연결 중...
echo.

adb connect 192.168.0.41:5555

echo.
echo ====================================
echo 연결 상태 확인
echo ====================================
adb devices

echo.
pause
"""
VR 추락 시뮬레이터 컨트롤러 설정
"""
import os
from typing import List

# 테스트 모드 설정
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# 네트워크 설정
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
WEBSOCKET_PORT = 8001

# 피코 디바이스 기본 IP
DEFAULT_PICO_IPS: List[str] = [
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103"
]

# 시뮬레이터 설정
SIMULATOR_HOST = "192.168.1.200"  # 기본값, 사용자가 UI에서 변경 가능
SIMULATOR_PORT = 9000

# 유니티 클라이언트 통신 포트
UNITY_SERVER_PORT = 9100

# ADB 설정
ADB_PATH = "adb"  # PATH에 있다고 가정, 필요시 전체 경로로 변경

# 기본 APK 패키지 이름
DEFAULT_PACKAGE_NAME = "com.safety.vrfall"

# 로그 설정
LOG_FILE = "vr_controller.log"
MAX_LOG_LINES = 1000

# UI 테마 색상
THEME = {
    "primary": "#6366f1",      # Indigo
    "success": "#10b981",      # Green
    "warning": "#f59e0b",      # Amber
    "danger": "#ef4444",       # Red
    "info": "#3b82f6",         # Blue
    "dark": "#0f172a",         # Slate 900
    "darker": "#020617",       # Slate 950
}

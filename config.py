"""
VR 추락 시뮬레이터 컨트롤러 설정
"""
import os
import sys
from pathlib import Path
from typing import List
import configparser


def get_exe_directory() -> Path:
    """실행 파일 또는 스크립트가 위치한 디렉토리 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일
        return Path(sys.executable).parent
    else:
        # 개발 환경 (소스 코드에서 직접 실행)
        return Path(__file__).parent


# 설정 파일 경로
EXE_DIR = get_exe_directory()
CONFIG_FILE_PATH = EXE_DIR / "config.ini"


def create_default_config() -> configparser.ConfigParser:
    """기본 설정 생성"""
    config = configparser.ConfigParser()
    
    config['Server'] = {
        'host': '0.0.0.0',
        'port': '8000',
        'websocket_port': '8001',
        'unity_server_port': '9100'
    }
    
    config['Devices'] = {
        'pico_ips': '192.168.1.101,192.168.1.102,192.168.1.103'
    }
    
    config['Simulator'] = {
        'host': '192.168.1.200',
        'port': '9000'
    }
    
    config['APK'] = {
        'package_name': 'com.mc.gintotal.vrfall'
    }
    
    config['ADB'] = {
        'path': r'C:\platform-tools\adb.exe'
    }
    
    config['Logging'] = {
        'log_file': 'vr_controller.log',
        'max_log_lines': '1000'
    }
    
    return config


def load_config() -> configparser.ConfigParser:
    """설정 파일 로드 또는 생성"""
    config = configparser.ConfigParser()
    
    if CONFIG_FILE_PATH.exists():
        # 기존 설정 파일 로드
        config.read(CONFIG_FILE_PATH, encoding='utf-8')
    else:
        # 기본 설정 생성 및 저장
        config = create_default_config()
        save_config(config)
    
    return config


def save_config(config: configparser.ConfigParser = None):
    """설정 파일 저장"""
    if config is None:
        config = _config
    
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        config.write(f)


# 설정 로드
_config = load_config()

# 테스트 모드 설정
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# 네트워크 설정
SERVER_HOST = _config.get('Server', 'host', fallback='0.0.0.0')
SERVER_PORT = _config.getint('Server', 'port', fallback=8000)
WEBSOCKET_PORT = _config.getint('Server', 'websocket_port', fallback=8001)
UNITY_SERVER_PORT = _config.getint('Server', 'unity_server_port', fallback=9100)

# 피코 디바이스 IP 리스트
pico_ips_str = _config.get('Devices', 'pico_ips', fallback='192.168.1.101,192.168.1.102,192.168.1.103')
DEFAULT_PICO_IPS: List[str] = [ip.strip() for ip in pico_ips_str.split(',') if ip.strip()]

# 시뮬레이터 설정
SIMULATOR_HOST = _config.get('Simulator', 'host', fallback='192.168.1.200')
SIMULATOR_PORT = _config.getint('Simulator', 'port', fallback=9000)

# ADB 설정
ADB_PATH = _config.get('ADB', 'path', fallback=r'C:\platform-tools\adb.exe')

# 기본 APK 패키지 이름
DEFAULT_PACKAGE_NAME = _config.get('APK', 'package_name', fallback='com.safety.vrfall')

# 로그 설정
LOG_FILE = _config.get('Logging', 'log_file', fallback='vr_controller.log')
MAX_LOG_LINES = _config.getint('Logging', 'max_log_lines', fallback=1000)

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


def update_pico_ips(ips: List[str]):
    """Pico IP 리스트 업데이트 및 저장"""
    _config.set('Devices', 'pico_ips', ','.join(ips))
    save_config()
    global DEFAULT_PICO_IPS
    DEFAULT_PICO_IPS = ips


def update_simulator_host(host: str):
    """시뮬레이터 호스트 업데이트 및 저장"""
    _config.set('Simulator', 'host', host)
    save_config()
    global SIMULATOR_HOST
    SIMULATOR_HOST = host


def update_package_name(package_name: str):
    """APK 패키지 이름 업데이트 및 저장"""
    _config.set('APK', 'package_name', package_name)
    save_config()
    global DEFAULT_PACKAGE_NAME
    DEFAULT_PACKAGE_NAME = package_name


"""
FastAPI 백엔드 서버
VR 추락 시뮬레이터 컨트롤러 웹 앱
"""
# UTF-8 인코딩 설정 (한글 에러 메시지 처리를 위해)
import sys
import os

# 환경 변수를 가장 먼저 설정 (uvicorn 로깅에도 적용되도록)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
    
    # Windows에서 UTF-8 인코딩 강제 설정
    import io
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import asyncio
import uvicorn
import json
import webbrowser
import threading
import time
from pathlib import Path
import signal
import atexit
import subprocess

from config import *
from controllers.simulator_controller import SimulatorController
from controllers.experience_controller import ExperienceController
from controllers.adb_controller import ADBController
from utils.logger import Logger


def safe_print(*args, **kwargs):
    """UTF-8 인코딩 에러를 방지하는 안전한 print 함수"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # UTF-8로 인코딩 후 출력
        try:
            message = ' '.join(str(arg) for arg in args)
            if sys.stdout and hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(message.encode('utf-8'))
                sys.stdout.buffer.write(b'\n')
                sys.stdout.buffer.flush()
        except:
            # 최후의 수단: 모든 한글을 제거하고 출력
            pass


def cleanup_port(port=8000):
    """프로그램 종료 시 포트를 사용 중인 프로세스 종료"""
    try:
        # Windows에서 포트를 사용하는 프로세스 찾기
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            # PID 추출 및 프로세스 종료
            lines = result.stdout.strip().split('\n')
            pids = set()
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
            
            # 각 PID 종료
            for pid in pids:
                try:
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                    safe_print(f"Port {port} process (PID: {pid}) terminated")
                except:
                    pass
    except Exception as e:
        safe_print(f"Port cleanup error: {e}")


def signal_handler(signum, frame):
    """시그널 핸들러 - 프로세스 완전 종료"""
    safe_print("\nShutting down...")
    cleanup_port(SERVER_PORT)
    # 프로세스 강제 종료 (확실한 종료 보장)
    os._exit(0)


# 프로그램 종료 시 자동으로 포트 정리
atexit.register(cleanup_port, SERVER_PORT)
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # 종료 시그널

# Windows에서 추가 시그널 처리
if sys.platform == 'win32':
    try:
        signal.signal(signal.SIGBREAK, signal_handler)  # Ctrl+Break
    except AttributeError:
        pass  # SIGBREAK가 없는 경우 무시


def get_base_path():
    """PyInstaller 실행 파일 또는 개발 환경에서의 기본 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일
        return Path(sys._MEIPASS)
    else:
        # 개발 환경 (소스 코드에서 직접 실행)
        return Path(__file__).parent


def setup_console_for_frozen():
    """PyInstaller 실행 파일에서 콘솔 출력 설정 (console=False 모드 대응)"""
    if getattr(sys, 'frozen', False):
        # stdout/stderr가 None인 경우 더미 스트림으로 대체
        if sys.stdout is None:
            sys.stdout = open(os.devnull, 'w')
        if sys.stderr is None:
            sys.stderr = open(os.devnull, 'w')
        if sys.stdin is None:
            sys.stdin = open(os.devnull, 'r')


# PyInstaller frozen 모드 설정
setup_console_for_frozen()


# 기본 경로 설정
BASE_PATH = get_base_path()
STATIC_PATH = BASE_PATH / "static"

# FastAPI 앱 초기화
app = FastAPI(title="VR Fall Simulator Controller")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory=str(STATIC_PATH)), name="static")

# 컨트롤러 초기화
logger = Logger()
simulator_ctrl = SimulatorController(logger)
experience_ctrl = ExperienceController(logger, simulator_ctrl)
adb_ctrl = ADBController(logger)

# WebSocket 연결 관리
active_connections: List[WebSocket] = []


@app.get("/")
async def root():
    """메인 페이지 제공"""
    return FileResponse(str(STATIC_PATH / "index.html"))


@app.get("/api/test_mode")
async def get_test_mode():
    """테스트 모드 상태 확인"""
    return {"enabled": TEST_MODE}


@app.get("/api/config")
async def get_config():
    """설정 값 가져오기"""
    return {
        "package_name": DEFAULT_PACKAGE_NAME,
        "simulator_host": SIMULATOR_HOST,
        "simulator_port": SIMULATOR_PORT,
        "server_port": SERVER_PORT
    }


# ==================== 시뮬레이터 API ====================

@app.post("/api/simulator/connect")
async def connect_simulator(data: dict):
    """시뮬레이터 연결"""
    try:
        ip = data.get("ip", SIMULATOR_HOST)
        port = data.get("port", SIMULATOR_PORT)
        
        success = await simulator_ctrl.connect(ip, port)
        
        if success:
            await broadcast({
                "type": "simulator_status",
                "status": "connected"
            })
            await broadcast_log("success", f"시뮬레이터 연결 성공: {ip}:{port}")
        else:
            await broadcast_log("error", "시뮬레이터 연결 실패")
        
        return {"success": success}
    except Exception as e:
        await broadcast_log("error", f"연결 오류: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/api/simulator/disconnect")
async def disconnect_simulator():
    """시뮬레이터 연결 해제"""
    try:
        simulator_ctrl.disconnect()
        await broadcast({
            "type": "simulator_status",
            "status": "disconnected"
        })
        await broadcast_log("info", "시뮬레이터 연결 해제됨")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/simulator/scan")
async def scan_simulator():
    """시뮬레이터 스캔"""
    try:
        await broadcast_log("info", "시뮬레이터 스캔 중...")
        found = await simulator_ctrl.scan()
        
        if found:
            await broadcast_log("success", f"시뮬레이터 발견: {found}")
        else:
            await broadcast_log("warning", "시뮬레이터를 찾을 수 없습니다")
        
        return {"success": bool(found), "address": found}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/simulator/elevator_up")
async def elevator_up(data: dict):
    """엘리베이터 상승 신호"""
    try:
        duration = data.get("duration", 5)
        success = await simulator_ctrl.send_elevator_up(duration)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/simulator/fall")
async def fall(data: dict):
    """추락 신호"""
    try:
        duration = data.get("duration", 3)
        success = await simulator_ctrl.send_fall(duration)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 체험 제어 API ====================

@app.post("/api/experience/start")
async def start_experience():
    """체험 시작"""
    try:
        success = await experience_ctrl.start()
        if success:
            await broadcast_log("success", "모든 피코 디바이스에 시작 신호 전송됨")
        return {"success": success}
    except Exception as e:
        await broadcast_log("error", f"체험 시작 오류: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/api/experience/pause")
async def pause_experience():
    """체험 일시정지"""
    try:
        success = await experience_ctrl.pause()
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/experience/resume")
async def resume_experience():
    """체험 재개"""
    try:
        success = await experience_ctrl.resume()
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/experience/stop")
async def stop_experience():
    """체험 종료"""
    try:
        success = await experience_ctrl.stop()
        if success:
            await broadcast_log("success", "모든 피코 디바이스에 종료 신호 전송됨")
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/experience/mode")
async def set_experience_mode(data: dict):
    """제어 모드 설정 (auto/manual)"""
    try:
        mode = data.get("mode", "auto")
        experience_ctrl.set_mode(mode)
        return {"success": True, "mode": mode}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== ADB 디바이스 API ====================

@app.post("/api/devices/scan")
async def scan_devices():
    """피코 디바이스 스캔"""
    try:
        devices = await adb_ctrl.scan_devices()
        await broadcast({
            "type": "devices",
            "devices": devices
        })
        return {"success": True, "devices": devices}
    except Exception as e:
        await broadcast_log("error", f"디바이스 스캔 오류: {str(e)}")
        return {"success": False, "error": str(e), "devices": []}


@app.post("/api/devices/install")
async def install_apk(data: dict):
    """APK 설치"""
    try:
        apk_path = data.get("apk_path")
        devices = data.get("devices", "all")
        
        success = await adb_ctrl.install_apk(apk_path, devices)
        return {"success": success}
    except Exception as e:
        await broadcast_log("error", f"APK 설치 오류: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/api/devices/uninstall")
async def uninstall_apk(data: dict):
    """APK 삭제"""
    try:
        package_name = data.get("package_name")
        devices = data.get("devices", "all")
        
        success = await adb_ctrl.uninstall_apk(package_name, devices)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/devices/launch")
async def launch_app(data: dict):
    """앱 실행"""
    try:
        package_name = data.get("package_name")
        devices = data.get("devices", "all")
        
        success = await adb_ctrl.launch_app(package_name, devices)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/devices/stop")
async def stop_app(data: dict):
    """앱 종료"""
    try:
        package_name = data.get("package_name")
        devices = data.get("devices", "all")
        
        success = await adb_ctrl.stop_app(package_name, devices)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/devices/reboot")
async def reboot_devices(data: dict):
    """디바이스 재부팅"""
    try:
        devices = data.get("devices", "all")
        
        success = await adb_ctrl.reboot_devices(devices)
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== WebSocket ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 연결 처리"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # 초기 상태 전송
        await websocket.send_json({
            "type": "test_mode",
            "enabled": TEST_MODE
        })
        
        # 메시지 수신 대기
        while True:
            data = await websocket.receive_text()
            # 필요시 클라이언트로부터의 메시지 처리
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)



async def broadcast(message: dict):
    """모든 WebSocket 클라이언트에 메시지 브로드캐스트"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass


async def broadcast_log(level: str, message: str):
    """로그 메시지 브로드캐스트"""
    logger.log(level, message)
    await broadcast({
        "type": "log",
        "level": level,
        "message": message
    })


# ==================== 서버 시작 ====================

def open_browser():
    """서버 시작 후 브라우저 자동 실행"""
    time.sleep(1.5)  # 서버 시작 대기
    webbrowser.open(f'http://localhost:{SERVER_PORT}')

if __name__ == "__main__":
    # 시작 전 포트 정리 (이전 실행이 비정상 종료된 경우 대비)
    safe_print("Cleaning up port...")
    cleanup_port(SERVER_PORT)
    time.sleep(0.5)  # 포트 해제 대기
    
    # 시작 배너 출력 (콘솔이 있는 경우만)
    try:
        safe_print(f"""
╔══════════════════════════════════════════════════════════╗
║  VR Fall Simulator Controller                           ║
║  Web Interface: http://localhost:{SERVER_PORT}                    ║
║  Test Mode: {'Enabled' if TEST_MODE else 'Disabled'}                                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    except (UnicodeEncodeError, OSError):
        # PyInstaller 윈도우 모드에서는 콘솔 출력 무시
        pass
    
    # 브라우저 자동 실행 (별도 스레드)
    threading.Thread(target=open_browser, daemon=True).start()
    
    # uvicorn 로깅 설정 (UTF-8 지원)
    import logging
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # WebSocket 서버 실행
    try:
        uvicorn.run(
            app,
            host=SERVER_HOST,
            port=SERVER_PORT,
            log_level="info",
            access_log=False  # 한글 에러 방지를 위해 액세스 로그 비활성화
        )
    except KeyboardInterrupt:
        # Ctrl+C로 종료
        safe_print("\nServer stopped by user")
    except Exception as e:
        safe_print(f"Server start error: {e}")
    finally:
        # 종료 시 포트 정리 및 프로세스 완전 종료
        safe_print("Cleaning up and exiting...")
        cleanup_port(SERVER_PORT)
        # 프로세스 강제 종료
        os._exit(0)


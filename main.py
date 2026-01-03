"""
FastAPI 백엔드 서버
VR 추락 시뮬레이터 컨트롤러 웹 앱
"""
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

from config import *
from controllers.simulator_controller import SimulatorController
from controllers.experience_controller import ExperienceController
from controllers.adb_controller import ADBController
from utils.logger import Logger

# FastAPI 앱 초기화
app = FastAPI(title="VR Fall Simulator Controller")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return FileResponse("static/index.html")


@app.get("/api/test_mode")
async def get_test_mode():
    """테스트 모드 상태 확인"""
    return {"enabled": TEST_MODE}


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
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  VR 추락 시뮬레이터 컨트롤러                             ║
║  웹 인터페이스: http://localhost:{SERVER_PORT}                    ║
║  테스트 모드: {'활성화' if TEST_MODE else '비활성화'}                                     ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 브라우저 자동 실행 (별도 스레드)
    threading.Thread(target=open_browser, daemon=True).start()
    
    # WebSocket 서버는 별도 포트에서 실행
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )


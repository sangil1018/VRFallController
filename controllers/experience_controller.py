"""
체험 제어 모듈
피코 디바이스와 통신하여 VR 체험 제어
"""
import asyncio
import socket
import json
from typing import Literal
from utils.logger import Logger
from controllers.simulator_controller import SimulatorController
from config import UNITY_SERVER_PORT, DEFAULT_PICO_IPS, TEST_MODE

ControlMode = Literal["auto", "manual"]


class ExperienceController:
    def __init__(self, logger: Logger, simulator_ctrl: SimulatorController):
        self.logger = logger
        self.simulator_ctrl = simulator_ctrl
        self.mode: ControlMode = "auto"
        self.unity_server = None
        self.devices = DEFAULT_PICO_IPS.copy()
    
    def set_mode(self, mode: ControlMode):
        """제어 모드 설정"""
        self.mode = mode
        self.logger.info(f"제어 모드 변경: {mode}")
    
    async def send_to_devices(self, command: str, data: dict = None) -> bool:
        """모든 피코 디바이스에 명령 전송"""
        try:
            message = {
                "command": command,
                "data": data or {}
            }
            
            if TEST_MODE:
                self.logger.info(f"[테스트] 디바이스 명령 전송: {command} -> {len(self.devices)}개 디바이스")
                return True
            
            # 실제 구현: 각 디바이스로 TCP 연결하여 메시지 전송
            tasks = []
            for device_ip in self.devices:
                task = self._send_to_device(device_ip, message)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if r is True)
            self.logger.info(f"{success_count}/{len(self.devices)} 디바이스에 명령 전송 완료")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"디바이스 명령 전송 오류: {str(e)}")
            return False
    
    async def _send_to_device(self, device_ip: str, message: dict) -> bool:
        """개별 디바이스에 명령 전송"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            await asyncio.get_event_loop().run_in_executor(
                None, sock.connect, (device_ip, UNITY_SERVER_PORT)
            )
            
            message_str = json.dumps(message) + "\n"
            await asyncio.get_event_loop().run_in_executor(
                None, sock.sendall, message_str.encode('utf-8')
            )
            
            sock.close()
            return True
            
        except Exception as e:
            self.logger.warning(f"디바이스 {device_ip} 전송 실패: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """체험 시작"""
        self.logger.info("체험 시작 신호 전송 중...")
        
        # 모든 디바이스에 PLAY 신호 전송
        success = await self.send_to_devices("PLAY")
        
        if success and self.mode == "auto":
            self.logger.info("자동 모드: 피코 #1로부터 신호 대기 중...")
            # 자동 모드에서는 첫 번째 피코 디바이스로부터 신호를 받아 시뮬레이터 제어
            # 실제 구현에서는 별도 서버 스레드에서 리스닝
        
        return success
    
    async def pause(self) -> bool:
        """체험 일시정지"""
        self.logger.info("체험 일시정지 신호 전송 중...")
        return await self.send_to_devices("PAUSE")
    
    async def resume(self) -> bool:
        """체험 재개"""
        self.logger.info("체험 재개 신호 전송 중...")
        return await self.send_to_devices("RESUME")
    
    async def stop(self) -> bool:
        """체험 종료"""
        self.logger.info("체험 종료 신호 전송 중...")
        success = await self.send_to_devices("STOP")
        
        # 시뮬레이터도 리셋
        if self.simulator_ctrl.connected:
            await self.simulator_ctrl.send_reset()
        
        return success
    
    async def handle_unity_signal(self, signal: str, data: dict = None):
        """Unity 클라이언트로부터 받은 신호 처리 (자동 모드)"""
        if self.mode != "auto":
            return
        
        self.logger.info(f"Unity 신호 수신: {signal}")
        
        # 시뮬레이터로 신호 전달
        if signal == "ELEVATOR_UP":
            duration = data.get("duration", 5) if data else 5
            await self.simulator_ctrl.send_elevator_up(duration)
        
        elif signal == "FALL":
            duration = data.get("duration", 3) if data else 3
            await self.simulator_ctrl.send_fall(duration)
        
        elif signal == "STOP":
            await self.simulator_ctrl.send_elevator_stop()

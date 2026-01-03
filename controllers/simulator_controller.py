"""
시뮬레이터 제어 모듈
"""
import asyncio
import socket
import json
from typing import Optional, Dict, Any
from utils.logger import Logger
from config import TEST_MODE


class SimulatorController:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.connected = False
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.socket: Optional[socket.socket] = None
    
    async def connect(self, host: str, port: int) -> bool:
        """시뮬레이터 연결"""
        try:
            self.host = host
            self.port = port
            
            if TEST_MODE:
                # 테스트 모드에서는 자동 연결 성공
                self.logger.success(f"[테스트] 시뮬레이터 연결: {host}:{port}")
                self.connected = True
                return True
            
            # 실제 연결 시도
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (host, port)
            )
            
            self.connected = True
            self.logger.success(f"시뮬레이터 연결 성공: {host}:{port}")
            return True
            
        except Exception as e:
            self.logger.error(f"시뮬레이터 연결 실패: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """시뮬레이터 연결 해제"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        self.socket = None
        self.logger.info("시뮬레이터 연결 해제됨")
    
    async def scan(self) -> Optional[str]:
        """네트워크에서 시뮬레이터 스캔"""
        # 간단한 스캔 구현 - 기본 IP 확인
        try:
            if TEST_MODE:
                await asyncio.sleep(1)  # 스캔 시뮬레이션
                return "192.168.1.100:9000"
            
            # 실제 구현에서는 브로드캐스트나 특정 IP 범위 스캔
            # 여기서는 기본 주소만 확인
            test_host = "192.168.1.100"
            test_port = 9000
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, sock.connect_ex, (test_host, test_port)
            )
            
            sock.close()
            
            if result == 0:
                return f"{test_host}:{test_port}"
            
            return None
            
        except Exception as e:
            self.logger.error(f"스캔 오류: {str(e)}")
            return None
    
    async def send_command(self, command: str, data: Dict[str, Any] = None) -> bool:
        """시뮬레이터에 명령 전송"""
        if not self.connected and not TEST_MODE:
            self.logger.error("시뮬레이터가 연결되지 않았습니다")
            return False
        
        try:
            message = {
                "command": command,
                "data": data or {}
            }
            
            if TEST_MODE:
                self.logger.info(f"[테스트] 시뮬레이터 명령 전송: {command}")
                return True
            
            # 실제 전송
            message_str = json.dumps(message) + "\n"
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.sendall, message_str.encode('utf-8')
            )
            
            self.logger.success(f"시뮬레이터 명령 전송: {command}")
            return True
            
        except Exception as e:
            self.logger.error(f"명령 전송 실패: {str(e)}")
            return False
    
    async def send_elevator_up(self, duration: int) -> bool:
        """엘리베이터 상승 신호"""
        return await self.send_command("ELEVATOR_UP", {"duration": duration})
    
    async def send_elevator_stop(self) -> bool:
        """엘리베이터 정지 신호"""
        return await self.send_command("ELEVATOR_STOP")
    
    async def send_fall(self, duration: int) -> bool:
        """추락 신호"""
        return await self.send_command("FALL", {"duration": duration})
    
    async def send_reset(self) -> bool:
        """리셋 신호"""
        return await self.send_command("RESET")

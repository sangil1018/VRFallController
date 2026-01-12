"""
ADB 컨트롤러
피코 디바이스 관리 및 ADB 명령 실행
"""
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Union
from utils.logger import Logger
from config import ADB_PATH, DEFAULT_PICO_IPS, TEST_MODE, EXE_DIR


class ADBController:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.devices: List[Dict[str, str]] = []
        self.default_ips = DEFAULT_PICO_IPS.copy()
        self.first_scan_done = False  # 첫 스캔 여부 추적
        
        # 일반 모드에서 배치 파일 복사
        if not TEST_MODE:
            self.copy_batch_file_to_exe()
    
    async def run_adb_command(self, command: List[str], device_ip: str = None) -> tuple[bool, str]:
        """ADB 명령 실행"""
        try:
            cmd = [ADB_PATH]
            
            if device_ip:
                cmd.extend(["-s", device_ip])
            
            cmd.extend(command)
            
            if TEST_MODE:
                # 테스트 모드에서는 가상 응답 반환
                cmd_str = " ".join(command)
                self.logger.info(f"[테스트] ADB 명령: {cmd_str}")
                
                if "devices" in cmd_str:
                    return True, "\n".join([f"{ip}\tdevice" for ip in self.default_ips])
                elif "install" in cmd_str:
                    await asyncio.sleep(0.5)
                    return True, "Success"
                else:
                    return True, "OK"
            
            # 실제 ADB 명령 실행 (CMD 창 숨김)
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=creationflags
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return True, stdout.decode('utf-8', errors='ignore')
            else:
                error = stderr.decode('utf-8', errors='ignore')
                self.logger.error(f"ADB 명령 실패: {error}")
                return False, error
                
        except Exception as e:
            self.logger.error(f"ADB 명령 실행 오류: {str(e)}")
            return False, str(e)
    
    def copy_batch_file_to_exe(self):
        """배치 파일들을 exe 디렉토리에 복사"""
        try:
            batch_files = [
                "adb_connect_all.bat",      # 네트워크 연결용
                "adb_tcpip_open.bat"        # USB로 TCPIP 포트 열기용 (초기 설정)
            ]
            
            for bat_file in batch_files:
                # 소스 파일 경로 (controllers 폴더 내)
                source_bat = Path(__file__).parent / bat_file
                # 목적지 경로 (exe 디렉토리)
                dest_bat = EXE_DIR / bat_file
                
                # 소스 파일이 존재하고, 목적지에 없으면 복사
                if source_bat.exists() and not dest_bat.exists():
                    shutil.copy2(source_bat, dest_bat)
                    self.logger.info(f"배치 파일 복사됨: {dest_bat}")
                elif dest_bat.exists():
                    self.logger.info(f"배치 파일이 이미 존재함: {dest_bat}")
        except Exception as e:
            self.logger.error(f"배치 파일 복사 오류: {str(e)}")
    
    async def execute_adb_connect_batch(self):
        """adb_connect_all.bat 실행 (일반 모드 첫 스캔시에만)"""
        try:
            bat_path = EXE_DIR / "adb_connect_all.bat"
            
            if not bat_path.exists():
                self.logger.warning(f"배치 파일을 찾을 수 없습니다: {bat_path}")
                return False
            
            self.logger.info("ADB 연결 배치 파일 실행 중...")
            
            # 배치 파일 실행 (백그라운드에서)
            process = await asyncio.create_subprocess_exec(
                str(bat_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # 배치 파일 완료 대기 (최대 10초)
            try:
                await asyncio.wait_for(process.communicate(), timeout=10.0)
                self.logger.success("ADB 연결 배치 파일 실행 완료")
                # 연결 안정화를 위해 잠시 대기
                await asyncio.sleep(1.0)
                return True
            except asyncio.TimeoutError:
                self.logger.warning("배치 파일 실행 시간 초과 (백그라운드 계속 실행 중)")
                return True  # 백그라운드로 계속 실행되므로 성공으로 간주
                
        except Exception as e:
            self.logger.error(f"배치 파일 실행 오류: {str(e)}")
            return False
    
    async def scan_devices(self) -> List[Dict[str, str]]:
        """피코 디바이스 스캔"""
        try:
            self.logger.info("피코 디바이스 스캔 중...")
            
            # 일반 모드에서 첫 스캔일 때만 배치 파일 실행
            if not TEST_MODE and not self.first_scan_done:
                self.logger.info("첫 스캔: ADB 연결 배치 파일 실행")
                await self.execute_adb_connect_batch()
                self.first_scan_done = True
            
            # ADB devices 명령 실행
            success, output = await self.run_adb_command(["devices"])
            
            if not success:
                return []
            
            # 출력 파싱
            devices = []
            lines = output.strip().split('\n')[1:]  # 첫 줄 "List of devices" 제외
            
            for line in lines:
                if '\t' in line:
                    device_id, status = line.split('\t')
                    devices.append({
                        "ip": device_id,
                        "status": status
                    })
            
            # 테스트 모드에서만 기본 IP 추가
            if TEST_MODE:
                for ip in self.default_ips:
                    if not any(d["ip"] == ip for d in devices):
                        devices.append({
                            "ip": ip,
                            "status": "device"
                        })
            
            # 일반 모드에서는 스캔된 디바이스만 표시 (기본 IP 추가 안함)
            
            self.devices = devices
            self.logger.success(f"{len(devices)}개 디바이스 발견됨")
            return devices
            
        except Exception as e:
            self.logger.error(f"디바이스 스캔 오류: {str(e)}")
            return []
    
    async def _execute_on_devices(self, devices: Union[str, List[str]], command: List[str]) -> bool:
        """선택된 디바이스에서 명령 실행"""
        target_devices = []
        
        if devices == "all":
            target_devices = [d["ip"] for d in self.devices]
        else:
            target_devices = devices if isinstance(devices, list) else [devices]
        
        if not target_devices:
            self.logger.warning("대상 디바이스가 없습니다")
            return False
        
        # 동시 실행 (오차 최소화)
        tasks = []
        for device_ip in target_devices:
            task = self.run_adb_command(command, device_ip)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, tuple) and r[0])
        self.logger.info(f"{success_count}/{len(target_devices)} 디바이스에서 성공")
        
        return success_count > 0
    
    async def install_apk(self, apk_path: str, devices: Union[str, List[str]] = "all") -> bool:
        """APK 설치"""
        self.logger.info(f"APK 설치 중: {apk_path}")
        return await self._execute_on_devices(devices, ["install", "-r", apk_path])
    
    async def uninstall_apk(self, package_name: str, devices: Union[str, List[str]] = "all") -> bool:
        """APK 삭제"""
        self.logger.info(f"APK 삭제 중: {package_name}")
        return await self._execute_on_devices(devices, ["uninstall", package_name])
    
    async def launch_app(self, package_name: str, devices: Union[str, List[str]] = "all") -> bool:
        """앱 실행"""
        self.logger.info(f"앱 실행 중: {package_name}")
        
        # Unity VR 앱의 일반적인 액티비티 이름
        activity = f"{package_name}/com.unity3d.player.UnityPlayerActivity"
        
        command = ["shell", "am", "start", "-n", activity]
        return await self._execute_on_devices(devices, command)
    
    async def stop_app(self, package_name: str, devices: Union[str, List[str]] = "all") -> bool:
        """앱 종료"""
        self.logger.info(f"앱 종료 중: {package_name}")
        command = ["shell", "am", "force-stop", package_name]
        return await self._execute_on_devices(devices, command)
    
    async def reboot_devices(self, devices: Union[str, List[str]] = "all") -> bool:
        """디바이스 재부팅"""
        self.logger.warning("디바이스 재부팅 중...")
        return await self._execute_on_devices(devices, ["reboot"])

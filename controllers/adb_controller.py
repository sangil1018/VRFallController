"""
ADB 컨트롤러
피코 디바이스 관리 및 ADB 명령 실행
"""
import asyncio
import subprocess
from typing import List, Dict, Union
from utils.logger import Logger
from config import ADB_PATH, DEFAULT_PICO_IPS, TEST_MODE


class ADBController:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.devices: List[Dict[str, str]] = []
        self.default_ips = DEFAULT_PICO_IPS.copy()
    
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
            
            # 실제 ADB 명령 실행
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
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
    
    async def scan_devices(self) -> List[Dict[str, str]]:
        """피코 디바이스 스캔"""
        try:
            self.logger.info("피코 디바이스 스캔 중...")
            
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
            
            # 기본 IP도 추가 (연결 안된 경우)
            for ip in self.default_ips:
                if not any(d["ip"] == ip for d in devices):
                    # 네트워크 연결 시도
                    if not TEST_MODE:
                        await self.run_adb_command(["connect", ip])
                        await asyncio.sleep(0.5)
                    
                    devices.append({
                        "ip": ip,
                        "status": "연결 시도 중" if not TEST_MODE else "device"
                    })
            
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

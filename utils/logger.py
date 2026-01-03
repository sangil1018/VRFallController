"""
로거 유틸리티
색상별 로그 레벨 지원
"""
import logging
import sys
from datetime import datetime
from typing import Literal

LogLevel = Literal["info", "success", "warning", "error"]


class Logger:
    def __init__(self, log_file: str = "vr_controller.log"):
        self.log_file = log_file
        
        # 파일 로거 설정
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        
        self.logger = logging.getLogger(__name__)
    
    def safe_print(self, message: str):
        """UTF-8 인코딩 에러를 방지하는 안전한 print"""
        try:
            print(message)
        except UnicodeEncodeError:
            # UTF-8로 직접 인코딩하여 출력
            try:
                if sys.stdout and hasattr(sys.stdout, 'buffer'):
                    sys.stdout.buffer.write(message.encode('utf-8'))
                    sys.stdout.buffer.write(b'\n')
                    sys.stdout.buffer.flush()
            except:
                # 최후의 수단: 이모지와 한글 제거
                safe_message = message.encode('ascii', errors='ignore').decode('ascii')
                print(safe_message)
    
    def log(self, level: LogLevel, message: str):
        """로그 메시지 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            self.logger.error(message)
            self.safe_print(f"[{timestamp}] ERROR: {message}")
        elif level == "warning":
            self.logger.warning(message)
            self.safe_print(f"[{timestamp}] WARNING: {message}")
        elif level == "success":
            self.logger.info(f"SUCCESS: {message}")
            self.safe_print(f"[{timestamp}] SUCCESS: {message}")
        else:  # info
            self.logger.info(message)
            self.safe_print(f"[{timestamp}] INFO: {message}")
    
    def info(self, message: str):
        self.log("info", message)
    
    def success(self, message: str):
        self.log("success", message)
    
    def warning(self, message: str):
        self.log("warning", message)
    
    def error(self, message: str):
        self.log("error", message)

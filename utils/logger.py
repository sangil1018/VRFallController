"""
로거 유틸리티
색상별 로그 레벨 지원
"""
import logging
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
    
    def log(self, level: LogLevel, message: str):
        """로그 메시지 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            self.logger.error(message)
            print(f"[{timestamp}] ❌ {message}")
        elif level == "warning":
            self.logger.warning(message)
            print(f"[{timestamp}] ⚠️  {message}")
        elif level == "success":
            self.logger.info(f"SUCCESS: {message}")
            print(f"[{timestamp}] ✅ {message}")
        else:  # info
            self.logger.info(message)
            print(f"[{timestamp}] ℹ️  {message}")
    
    def info(self, message: str):
        self.log("info", message)
    
    def success(self, message: str):
        self.log("success", message)
    
    def warning(self, message: str):
        self.log("warning", message)
    
    def error(self, message: str):
        self.log("error", message)

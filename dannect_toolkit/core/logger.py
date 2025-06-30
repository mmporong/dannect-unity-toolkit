#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Logger
색상 코딩과 다양한 로그 레벨을 지원하는 로깅 시스템
"""

import logging
import datetime
from typing import Optional


class DannectLogger:
    """Dannect Toolkit 전용 로거 - Unity DannectLogger와 호환"""
    
    def __init__(self, name: str = "DannectToolkit", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 핸들러가 이미 있으면 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 파일 핸들러
        log_filename = f"dannect_toolkit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """정보 로그 (Unity DannectLogger.Log와 동일)"""
        self.logger.info(f"✅ {message}")
    
    def log(self, message: str):
        """일반 로그 (info의 별칭)"""
        self.info(message)
    
    def warning(self, message: str):
        """경고 로그 (Unity DannectLogger.LogWarning과 동일)"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        """에러 로그 (Unity DannectLogger.LogError와 동일)"""
        self.logger.error(f"❌ {message}")
    
    def debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(f"🐛 {message}")
    
    def start(self, message: str):
        """시작 로그 (Unity DannectLogger.LogStart와 동일)"""
        self.logger.info(f"🚀 {message}")
    
    def complete(self, message: str):
        """완료 로그 (Unity DannectLogger.LogComplete와 동일)"""
        self.logger.info(f"🎯 {message}")
    
    def progress(self, message: str):
        """진행 로그 (Unity DannectLogger.LogProgress와 동일)"""
        self.logger.info(f"🔄 {message}")
    
    def success(self, message: str):
        """성공 로그 (Unity DannectLogger.LogSuccess와 동일)"""
        self.logger.info(f"🎉 {message}")
    
    def exception(self, message: str, exception: Exception):
        """예외 로그"""
        self.logger.error(f"❌ {message}: {str(exception)}")
        self.logger.debug(f"스택 트레이스: {exception}")
    
    def verbose(self, message: str):
        """상세 로그 (Unity DannectLogger.LogVerbose와 동일)"""
        self.logger.debug(f"📝 {message}")
    
    # Unity 스타일 호환성을 위한 별칭들
    def LogInfo(self, message: str):
        """Unity 스타일 호환성"""
        self.info(message)
    
    def LogWarning(self, message: str):
        """Unity 스타일 호환성"""
        self.warning(message)
    
    def LogError(self, message: str):
        """Unity 스타일 호환성"""
        self.error(message)
    
    def LogStart(self, message: str):
        """Unity 스타일 호환성"""
        self.start(message)
    
    def LogComplete(self, message: str):
        """Unity 스타일 호환성"""
        self.complete(message)
    
    def LogProgress(self, message: str):
        """Unity 스타일 호환성"""
        self.progress(message)
    
    def LogSuccess(self, message: str):
        """Unity 스타일 호환성"""
        self.success(message)
    
    def LogVerbose(self, message: str):
        """Unity 스타일 호환성"""
        self.verbose(message)


# 전역 로거 인스턴스 (기존 코드와의 호환성)
logger = DannectLogger()

# Unity 패키지와의 호환성을 위한 함수들
def get_unity_compatible_logger() -> DannectLogger:
    """Unity 패키지와 호환되는 로거를 반환합니다."""
    return logger

def set_log_level(level: str):
    """로그 레벨을 설정합니다."""
    global logger
    logger.logger.setLevel(getattr(logging, level.upper())) 
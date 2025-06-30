#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Development Toolkit
범용 Unity 개발 자동화 도구

Author: Dannect
Version: 2.0.0
License: MIT
"""

from .core.toolkit import DannectUnityToolkit
from .core.config import ToolkitConfig, UnityProjectConfig
from .core.logger import DannectLogger
from .core.enums import ActionType

# 버전 정보
__version__ = "2.0.0"
__author__ = "Dannect"
__license__ = "MIT"

# 메인 클래스들을 패키지 레벨에서 접근 가능하도록 export
__all__ = [
    'DannectUnityToolkit',
    'ToolkitConfig', 
    'UnityProjectConfig',
    'DannectLogger',
    'ActionType',
    '__version__',
    '__author__',
    '__license__'
]

# 패키지 초기화
def get_version():
    """패키지 버전을 반환합니다."""
    return __version__

def get_logger(name: str = "DannectToolkit", level: str = "INFO"):
    """설정된 로거 인스턴스를 반환합니다."""
    return DannectLogger(name, level) 
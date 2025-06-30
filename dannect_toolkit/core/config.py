#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Configuration
설정 관리 시스템 - Unity DannectToolkitConfig와 호환
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
# from .logger import logger  # 순환 임포트 방지


@dataclass
class UnityProjectConfig:
    """Unity 프로젝트 설정 - Unity DannectToolkitConfig와 호환"""
    path: str
    name: str
    unity_version: str = "2022.3"
    target_platform: str = "WebGL"
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}
        
        # 프로젝트 이름이 없으면 경로에서 추출
        if not self.name:
            self.name = os.path.basename(self.path.rstrip(os.sep))
    
    def is_valid(self) -> bool:
        """프로젝트 설정이 유효한지 확인합니다."""
        return (
            os.path.exists(self.path) and
            os.path.exists(os.path.join(self.path, "Assets")) and
            os.path.exists(os.path.join(self.path, "ProjectSettings"))
        )
    
    def get_packages_manifest_path(self) -> str:
        """Packages/manifest.json 경로를 반환합니다."""
        return os.path.join(self.path, "Packages", "manifest.json")
    
    def get_project_settings_path(self) -> str:
        """ProjectSettings 폴더 경로를 반환합니다."""
        return os.path.join(self.path, "ProjectSettings")


@dataclass
class ToolkitConfig:
    """Toolkit 전체 설정 - Unity DannectToolkitConfig와 호환"""
    unity_editor_path: str = ""
    default_timeout: int = 300
    max_parallel_workers: int = 3
    enable_logging: bool = True
    log_level: str = "INFO"
    git_packages: Dict[str, str] = field(default_factory=dict)
    project_directories: List[str] = field(default_factory=list)
    
    # Unity 패키지와의 호환성을 위한 추가 설정들
    button_settings: Optional[Dict[str, Any]] = field(default_factory=dict)
    webgl_settings: Optional[Dict[str, Any]] = field(default_factory=dict)
    scene_settings: Optional[Dict[str, Any]] = field(default_factory=dict)
    debug_settings: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.git_packages is None:
            self.git_packages = {}
        
        # 기본 Git 패키지 설정
        if not self.git_packages:
            self.git_packages = {
                "com.dannect.toolkit": "https://github.com/mmporong/unity-toolkit.git"
            }
        
        if self.project_directories is None:
            self.project_directories = []
        
        # Unity 패키지 호환성을 위한 기본 설정들
        if self.button_settings is None:
            self.button_settings = {
                "sourceButtonName": "Next_Btn",
                "newButtonName": "Rebuild_Btn",
                "buttonText": "다시하기",
                "buttonOffset": {"x": -140.0, "y": 0.0},
                "targetClassName": "SystemManager",
                "targetMethodName": "OnRebuildButtonClicked"
            }
        
        if self.webgl_settings is None:
            self.webgl_settings = {
                "defaultWidth": 1655,
                "defaultHeight": 892,
                "initialMemorySize": 32,
                "maximumMemorySize": 2048,
                "compressionFormat": "Disabled",
                "template": "APPLICATION:Minimal"
            }
        
        if self.scene_settings is None:
            self.scene_settings = {
                "popupObjectNames": ["Success_Pop", "Warning_Pop", "Error_Pop"],
                "searchRootObjects": ["Canvas", "UI", "Popup"],
                "autoSaveScene": True
            }
        
        if self.debug_settings is None:
            self.debug_settings = {
                "enableVerboseLogging": True,
                "enableUnityEditorOnlyLogs": True,
                "enableFileLogging": False,
                "maxRetryAttempts": 3,
                "enableDebugMode": False
            }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ToolkitConfig':
        """설정 파일에서 ToolkitConfig를 로드합니다."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return cls(
                unity_editor_path=config_data.get("unity_editor_path", ""),
                default_timeout=config_data.get("default_timeout", 300),
                max_parallel_workers=config_data.get("max_parallel_workers", 3),
                enable_logging=config_data.get("enable_logging", True),
                log_level=config_data.get("log_level", "INFO"),
                git_packages=config_data.get("git_packages", {}),
                project_directories=config_data.get("project_directories", []),
                button_settings=config_data.get("button_settings", {}),
                webgl_settings=config_data.get("webgl_settings", {}),
                scene_settings=config_data.get("scene_settings", {}),
                debug_settings=config_data.get("debug_settings", {})
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"설정 파일 JSON 파싱 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"설정 파일 로드 오류: {e}")
    
    def save_to_file(self, config_path: str) -> bool:
        """설정을 파일로 저장합니다."""
        try:
            config_data = {
                "unity_editor_path": self.unity_editor_path,
                "default_timeout": self.default_timeout,
                "max_parallel_workers": self.max_parallel_workers,
                "enable_logging": self.enable_logging,
                "log_level": self.log_level,
                "git_packages": self.git_packages,
                "project_directories": self.project_directories,
                "button_settings": self.button_settings,
                "webgl_settings": self.webgl_settings,
                "scene_settings": self.scene_settings,
                "debug_settings": self.debug_settings
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ 설정 파일 저장 완료: {config_path}")
            return True
        except Exception as e:
            print(f"❌ 설정 파일 저장 오류: {e}")
            return False
    
    def validate(self) -> tuple[bool, List[str]]:
        """설정의 유효성을 검사합니다."""
        errors = []
        
        # Unity 경로 검증
        if self.unity_editor_path and not os.path.exists(self.unity_editor_path):
            errors.append(f"Unity Editor 경로가 존재하지 않습니다: {self.unity_editor_path}")
        
        # 프로젝트 디렉토리 검증
        for proj_dir in self.project_directories:
            if not os.path.exists(proj_dir):
                errors.append(f"프로젝트 디렉토리가 존재하지 않습니다: {proj_dir}")
        
        # 타임아웃 범위 검증
        if not (10 <= self.default_timeout <= 3600):
            errors.append(f"타임아웃 값이 범위를 벗어났습니다 (10-3600초): {self.default_timeout}")
        
        # 워커 수 검증
        if not (1 <= self.max_parallel_workers <= 10):
            errors.append(f"최대 워커 수가 범위를 벗어났습니다 (1-10개): {self.max_parallel_workers}")
        
        return len(errors) == 0, errors
    
    def get_unity_compatible_dict(self) -> Dict[str, Any]:
        """Unity 패키지와 호환되는 딕셔너리 형태로 반환합니다."""
        return {
            "ProjectName": os.path.basename(os.getcwd()) if self.project_directories else "Unknown",
            "CompanyName": "Dannect",
            "Version": "2.0.0",
            "ButtonSettings": self.button_settings,
            "WebGLSettings": self.webgl_settings,
            "SceneSettings": self.scene_settings,
            "DebugSettings": self.debug_settings
        }
    
    def merge_with_unity_config(self, unity_config_data: Dict[str, Any]):
        """Unity DannectToolkitConfig에서 가져온 설정과 병합합니다."""
        if "ButtonSettings" in unity_config_data:
            self.button_settings.update(unity_config_data["ButtonSettings"])
        
        if "WebGLSettings" in unity_config_data:
            self.webgl_settings.update(unity_config_data["WebGLSettings"])
        
        if "SceneSettings" in unity_config_data:
            self.scene_settings.update(unity_config_data["SceneSettings"])
        
        if "DebugSettings" in unity_config_data:
            self.debug_settings.update(unity_config_data["DebugSettings"])
        
        print("📝 Unity 설정과 병합 완료")


def create_sample_config(file_path: str = "dannect_toolkit_config.json") -> bool:
    """샘플 설정 파일을 생성합니다."""
    sample_config = ToolkitConfig()
    sample_config.project_directories = [
        "C:/UnityProjects/Project1",
        "C:/UnityProjects/Project2", 
        "E:/SimGround_Package_v2/5.1.3.2_SolubilityObservation"
    ]
    
    success = sample_config.save_to_file(file_path)
    if success:
        print(f"✅ 샘플 설정 파일 생성 완료: {file_path}")
        print("📄 설정 파일을 수정한 후 --config 옵션으로 사용하세요.")
    
    return success


def load_config_with_fallback(config_path: Optional[str] = None) -> ToolkitConfig:
    """설정 파일을 로드하거나 기본 설정을 반환합니다."""
    if config_path and os.path.exists(config_path):
        try:
            return ToolkitConfig.from_file(config_path)
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패, 기본 설정 사용: {e}")
    
    return ToolkitConfig() 
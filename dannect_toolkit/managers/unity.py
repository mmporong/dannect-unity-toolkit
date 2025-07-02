#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Unity Managers
Unity 경로, 프로젝트, CLI 실행 관련 관리자들
"""

import os
import subprocess
from typing import List, Optional
from ..core.config import ToolkitConfig, UnityProjectConfig
from ..core.logger import logger
from ..core.enums import ActionType, UNITY_CLI_METHODS, DEFAULT_UNITY_PATHS


class UnityPathManager:
    """Unity Editor 경로 관리"""
    
    @staticmethod
    def find_unity_editor_path() -> Optional[str]:
        """Unity Editor 경로를 자동으로 찾습니다."""
        logger.progress("Unity Editor 경로 검색 중...")
        
        for base_path in DEFAULT_UNITY_PATHS:
            logger.debug(f"검색 중인 기본 경로: {base_path}")
            
            if not os.path.exists(base_path):
                logger.debug(f"경로가 존재하지 않음: {base_path}")
                continue
            
            logger.debug(f"경로 확인됨: {base_path}")
            
            try:
                # 버전 폴더들 검색
                items = os.listdir(base_path)
                logger.debug(f"발견된 항목들: {items}")
                
                for item in items:
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        unity_exe = os.path.join(item_path, "Editor", "Unity.exe")
                        logger.debug(f"Unity.exe 확인 중: {unity_exe}")
                        
                        if os.path.exists(unity_exe):
                            logger.info(f"Unity Editor 발견: {unity_exe}")
                            return unity_exe
                        else:
                            logger.debug(f"Unity.exe 없음: {unity_exe}")
            except Exception as e:
                logger.debug(f"경로 검색 중 오류: {base_path} - {e}")
        
        logger.error("Unity Editor를 찾을 수 없습니다.")
        return None
    
    @staticmethod
    def validate_unity_path(unity_path: str) -> bool:
        """Unity 경로가 유효한지 확인합니다."""
        if not unity_path:
            return False
        
        if not os.path.exists(unity_path):
            return False
        
        # Unity.exe 파일인지 확인
        if os.path.basename(unity_path).lower() != "unity.exe":
            return False
        
        return True
    
    @staticmethod
    def get_unity_version(unity_path: str) -> Optional[str]:
        """Unity 버전을 가져옵니다."""
        try:
            result = subprocess.run(
                [unity_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # 버전 정보 파싱
                version_line = result.stdout.strip().split('\n')[0]
                return version_line
            return None
        except Exception:
            return None


class UnityProjectManager:
    """Unity 프로젝트 관리"""
    
    @staticmethod
    def find_unity_projects(base_dir: str) -> List[UnityProjectConfig]:
        """지정된 디렉토리에서 Unity 프로젝트들을 자동으로 찾습니다."""
        unity_projects = []
        
        if not os.path.exists(base_dir):
            logger.error(f"기본 디렉토리가 존재하지 않습니다: {base_dir}")
            return unity_projects
        
        logger.progress(f"Unity 프로젝트 검색 중: {base_dir}")
        
        try:
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path):
                    if UnityProjectManager.is_unity_project(item_path):
                        config = UnityProjectConfig(
                            path=item_path,
                            name=item
                        )
                        unity_projects.append(config)
                        logger.debug(f"Unity 프로젝트 발견: {item}")
        
        except Exception as e:
            logger.error(f"디렉토리 스캔 오류: {e}")
        
        logger.info(f"총 {len(unity_projects)}개의 Unity 프로젝트를 찾았습니다.")
        return unity_projects
    
    @staticmethod
    def is_unity_project(project_path: str) -> bool:
        """해당 경로가 Unity 프로젝트인지 확인합니다."""
        project_settings = os.path.join(project_path, "ProjectSettings")
        assets_folder = os.path.join(project_path, "Assets")
        
        return os.path.exists(project_settings) and os.path.exists(assets_folder)
    
    @staticmethod
    def get_project_unity_version(project_path: str) -> Optional[str]:
        """프로젝트의 Unity 버전을 가져옵니다."""
        version_file = os.path.join(project_path, "ProjectSettings", "ProjectVersion.txt")
        
        if not os.path.exists(version_file):
            return None
        
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('m_EditorVersion:'):
                        return line.split(':', 1)[1].strip()
            return None
        except Exception as e:
            logger.debug(f"프로젝트 버전 읽기 오류: {e}")
            return None
    
    @staticmethod
    def has_dannect_toolkit_package(project_path: str) -> bool:
        """프로젝트에 Dannect Toolkit 패키지가 설치되어 있는지 확인합니다."""
        manifest_path = os.path.join(project_path, "Packages", "manifest.json")
        
        if not os.path.exists(manifest_path):
            return False
        
        try:
            import json
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                dependencies = manifest.get("dependencies", {})
                return "com.dannect.unity.toolkit" in dependencies
        except Exception:
            return False


class UnityCliExecutor:
    """Unity CLI 명령어 실행기 - Unity 패키지와 연동"""
    
    def __init__(self, toolkit_config: ToolkitConfig):
        self.config = toolkit_config
        self.unity_path = self._resolve_unity_path()
    
    def _resolve_unity_path(self) -> str:
        """Unity 경로를 결정합니다."""
        if self.config.unity_editor_path and UnityPathManager.validate_unity_path(self.config.unity_editor_path):
            return self.config.unity_editor_path
        
        # 자동 검색
        found_path = UnityPathManager.find_unity_editor_path()
        if found_path:
            self.config.unity_editor_path = found_path
            return found_path
        
        raise RuntimeError("Unity Editor 경로를 찾을 수 없습니다.")
    
    def execute_unity_method(self, project: UnityProjectConfig, method_name: str, timeout: Optional[int] = None) -> bool:
        """Unity 메소드를 실행합니다."""
        if timeout is None:
            timeout = self.config.default_timeout
        
        logger.start(f"Unity 메소드 실행: {project.name} - {method_name}")
        
        cmd = [
            self.unity_path,
            "-batchmode",
            "-quit",
            "-projectPath", project.path,
            "-executeMethod", method_name,
            "-logFile", "-"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                timeout=timeout,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 로그 출력
            if result.stdout:
                logger.debug("Unity 출력:")
                for line in result.stdout.split('\n')[:50]:  # 처음 50줄만
                    if line.strip():
                        logger.debug(f"  {line}")
            
            success = result.returncode == 0
            if success:
                logger.complete(f"Unity 메소드 실행 완료: {project.name}")
            else:
                logger.error(f"Unity 메소드 실행 실패: {project.name} (코드: {result.returncode})")
                if result.stderr:
                    logger.error(f"에러 출력: {result.stderr[:500]}")
            
            return success
            
        except subprocess.TimeoutExpired:
            logger.error(f"Unity 실행 타임아웃: {project.name} ({timeout}초)")
            return False
        except Exception as e:
            logger.error(f"Unity 실행 오류: {project.name} - {e}")
            return False
    
    def execute_action(self, project: UnityProjectConfig, action: ActionType) -> bool:
        """특정 액션을 실행합니다 (Unity 패키지 메소드와 연동)."""
        if action not in UNITY_CLI_METHODS:
            logger.error(f"지원하지 않는 액션: {action}")
            return False
        
        method_name = UNITY_CLI_METHODS[action]
        return self.execute_unity_method(project, method_name)
    
    def check_unity_package_integration(self, project: UnityProjectConfig) -> bool:
        """Unity 패키지와의 연동 상태를 확인합니다."""
        logger.progress(f"{project.name} Unity 패키지 연동 확인 중...")
        
        # 1. Dannect Toolkit 패키지 설치 확인
        has_package = UnityProjectManager.has_dannect_toolkit_package(project.path)
        if not has_package:
            logger.warning(f"{project.name}: Dannect Toolkit 패키지가 설치되지 않았습니다.")
            return False
        
        # 2. 테스트 메소드 실행으로 연동 확인
        test_success = self.execute_action(project, ActionType.PROJECT_INFO)
        if test_success:
            logger.success(f"{project.name}: Unity 패키지 연동 정상")
        else:
            logger.error(f"{project.name}: Unity 패키지 연동 실패")
        
        return test_success
    
    def get_project_info(self, project: UnityProjectConfig) -> dict:
        """프로젝트 정보를 가져옵니다."""
        info = {
            "name": project.name,
            "path": project.path,
            "unity_version": UnityProjectManager.get_project_unity_version(project.path),
            "has_toolkit": UnityProjectManager.has_dannect_toolkit_package(project.path),
            "is_valid": project.is_valid()
        }
        
        return info 
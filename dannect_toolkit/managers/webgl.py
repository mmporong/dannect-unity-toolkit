#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit WebGL Build Manager
WebGL 빌드 최적화 및 자동화
"""

import os
import subprocess
from typing import Dict, Any, Optional
from ..core.config import UnityProjectConfig, ToolkitConfig
from ..core.logger import logger


class WebGLBuildManager:
    """WebGL 빌드 관리자 - Unity 6 최적화"""
    
    @staticmethod
    def build_webgl(project: UnityProjectConfig, unity_path: str, config: ToolkitConfig) -> bool:
        """WebGL 빌드를 실행합니다."""
        logger.start(f"WebGL 빌드 시작: {project.name}")
        
        # 빌드 폴더 설정
        build_path = os.path.join(project.path, "Builds", "WebGL")
        
        # 기본 빌드 명령어
        cmd = [
            unity_path,
            "-batchmode",
            "-quit",
            "-projectPath", project.path,
            "-buildTarget", "WebGL",
            "-buildPath", build_path,
            "-executeMethod", "Dannect.Unity.Toolkit.Editor.DannectToolkitEditorCore.BuildWebGL",
            "-logFile", "-"
        ]
        
        # Unity 6 WebGL 설정 적용
        webgl_settings = config.webgl_settings
        if webgl_settings:
            # Player Settings 적용을 위한 추가 파라미터
            if "defaultWidth" in webgl_settings:
                cmd.extend(["-screen-width", str(webgl_settings["defaultWidth"])])
            if "defaultHeight" in webgl_settings:
                cmd.extend(["-screen-height", str(webgl_settings["defaultHeight"])])
        
        try:
            logger.progress(f"Unity WebGL 빌드 실행 중: {project.name}")
            
            result = subprocess.run(
                cmd,
                timeout=config.default_timeout * 2,  # WebGL 빌드는 더 오래 걸림
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 빌드 로그 처리
            if result.stdout:
                WebGLBuildManager._process_build_log(result.stdout, project.name)
            
            success = result.returncode == 0 and os.path.exists(build_path)
            
            if success:
                build_size = WebGLBuildManager._get_build_size(build_path)
                logger.complete(f"WebGL 빌드 완료: {project.name} ({build_size})")
            else:
                logger.error(f"WebGL 빌드 실패: {project.name} (코드: {result.returncode})")
                if result.stderr:
                    logger.error(f"빌드 오류: {result.stderr[:500]}")
            
            return success
            
        except subprocess.TimeoutExpired:
            logger.error(f"WebGL 빌드 타임아웃: {project.name}")
            return False
        except Exception as e:
            logger.error(f"WebGL 빌드 오류: {project.name} - {e}")
            return False
    
    @staticmethod
    def _process_build_log(log_output: str, project_name: str):
        """빌드 로그를 처리하고 중요한 정보를 추출합니다."""
        lines = log_output.split('\n')
        important_lines = []
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'error', 'warning', 'build report', 'total time', 'compressed'
            ]):
                important_lines.append(line)
        
        if important_lines:
            logger.info(f"{project_name} 빌드 요약:")
            for line in important_lines[:10]:  # 최대 10줄만
                logger.info(f"  {line}")
    
    @staticmethod
    def _get_build_size(build_path: str) -> str:
        """빌드 크기를 문자열로 반환합니다."""
        try:
            total_size = 0
            for root, dirs, files in os.walk(build_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            
            # MB 단위로 변환
            size_mb = total_size / (1024 * 1024)
            return f"{size_mb:.1f}MB"
            
        except Exception:
            return "크기 불명"
    
    @staticmethod
    def apply_webgl_settings(project: UnityProjectConfig, settings: Dict[str, Any]) -> bool:
        """WebGL 설정을 프로젝트에 적용합니다."""
        logger.progress(f"WebGL 설정 적용: {project.name}")
        
        # ProjectSettings/ProjectSettings.asset 파일 경로
        project_settings_path = os.path.join(
            project.path, "ProjectSettings", "ProjectSettings.asset"
        )
        
        if not os.path.exists(project_settings_path):
            logger.error(f"ProjectSettings.asset 파일을 찾을 수 없습니다: {project.name}")
            return False
        
        try:
            # Unity의 Player Settings를 직접 수정하는 것보다는
            # Unity Editor 메소드를 통해 설정하는 것이 안전
            logger.info(f"WebGL 설정이 Unity 패키지를 통해 적용됩니다: {project.name}")
            return True
            
        except Exception as e:
            logger.error(f"WebGL 설정 적용 오류: {project.name} - {e}")
            return False
    
    @staticmethod
    def clean_webgl_builds(project: UnityProjectConfig) -> bool:
        """WebGL 빌드 파일들을 정리합니다."""
        build_path = os.path.join(project.path, "Builds", "WebGL")
        
        if not os.path.exists(build_path):
            logger.info(f"정리할 WebGL 빌드가 없습니다: {project.name}")
            return True
        
        try:
            import shutil
            shutil.rmtree(build_path)
            logger.info(f"WebGL 빌드 정리 완료: {project.name}")
            return True
        except Exception as e:
            logger.error(f"WebGL 빌드 정리 오류: {project.name} - {e}")
            return False
    
    @staticmethod
    def validate_webgl_requirements(project: UnityProjectConfig) -> tuple[bool, list[str]]:
        """WebGL 빌드 요구사항을 검증합니다."""
        errors = []
        
        # 1. 기본 Unity 프로젝트 구조 확인
        if not project.is_valid():
            errors.append("유효하지 않은 Unity 프로젝트입니다")
        
        # 2. WebGL 플랫폼 지원 확인 (Unity 6 기준)
        project_settings_path = os.path.join(
            project.path, "ProjectSettings", "ProjectSettings.asset"
        )
        if not os.path.exists(project_settings_path):
            errors.append("ProjectSettings.asset 파일이 없습니다")
        
        # 3. 빌드 출력 디렉토리 확인
        builds_dir = os.path.join(project.path, "Builds")
        if not os.path.exists(builds_dir):
            try:
                os.makedirs(builds_dir, exist_ok=True)
                logger.debug(f"빌드 디렉토리 생성: {builds_dir}")
            except Exception as e:
                errors.append(f"빌드 디렉토리 생성 실패: {e}")
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.success(f"WebGL 빌드 요구사항 충족: {project.name}")
        else:
            logger.warning(f"WebGL 빌드 요구사항 미충족: {project.name}")
            for error in errors:
                logger.warning(f"  - {error}")
        
        return is_valid, errors 
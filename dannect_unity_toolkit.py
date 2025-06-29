#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Development Toolkit
범용 Unity 개발 자동화 도구

Author: Dannect
Version: 2.0.0
License: MIT
"""

import os
import json
import subprocess
import sys
import time
import argparse
import logging
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# =========================
# #region 설정 및 상수
# =========================

class ActionType(Enum):
    """실행 가능한 액션 타입들"""
    ALL_TEST = "all_test"
    CREATE_BUTTON = "create_button"
    TEST_BUTTON = "test_button"
    DEBUG_POPUP = "debug_popup"
    CHECK_EVENTS = "check_events"
    BUILD_WEBGL = "build_webgl"
    CLEAN_BUILDS = "clean_builds"
    PACKAGE_UPDATE = "package_update"
    GIT_COMMIT = "git_commit"
    PROJECT_INFO = "project_info"

@dataclass
class UnityProjectConfig:
    """Unity 프로젝트 설정"""
    path: str
    name: str
    unity_version: str = "2022.3"
    target_platform: str = "WebGL"
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}
        
        # 프로젝트 이름이 없으면 경로에서 추출
        if not self.name:
            self.name = os.path.basename(self.path.rstrip(os.sep))

@dataclass
class ToolkitConfig:
    """Toolkit 전체 설정"""
    unity_editor_path: str = ""
    default_timeout: int = 300
    max_parallel_workers: int = 3
    enable_logging: bool = True
    log_level: str = "INFO"
    git_packages: Dict[str, str] = None
    
    def __post_init__(self):
        if self.git_packages is None:
            self.git_packages = {
                "com.dannect.toolkit": "https://github.com/dannect/unity-toolkit.git"
            }

# 기본 설정값들
DEFAULT_UNITY_PATHS = [
    r"C:\Program Files\Unity\Hub\Editor",
    r"C:\Program Files (x86)\Unity\Hub\Editor",
    r"D:\Unity",
    r"C:\Unity"
]

UNITY_CLI_METHODS = {
    ActionType.ALL_TEST: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_AllInOneRebuildButtonTest",
    ActionType.CREATE_BUTTON: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_CreateRebuildButton",
    ActionType.TEST_BUTTON: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_TestRebuildButtonClick",
    ActionType.DEBUG_POPUP: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_DebugFindSuccessPop",
    ActionType.CHECK_EVENTS: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_CheckRebuildButtonEvents",
    ActionType.PROJECT_INFO: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_TestCLIMode"
}

# endregion

# =========================
# #region 로깅 시스템
# =========================

class DannectLogger:
    """Dannect Toolkit 전용 로거"""
    
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
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        self.logger.error(f"❌ {message}")
    
    def debug(self, message: str):
        self.logger.debug(f"🐛 {message}")
    
    def start(self, message: str):
        self.logger.info(f"🚀 {message}")
    
    def complete(self, message: str):
        self.logger.info(f"🎯 {message}")
    
    def progress(self, message: str):
        self.logger.info(f"🔄 {message}")

# 전역 로거 인스턴스
logger = DannectLogger()

# endregion

# =========================
# #region Unity 경로 및 프로젝트 관리
# =========================

class UnityPathManager:
    """Unity Editor 경로 관리"""
    
    @staticmethod
    def find_unity_editor_path() -> Optional[str]:
        """Unity Editor 경로를 자동으로 찾습니다."""
        logger.progress("Unity Editor 경로 검색 중...")
        
        for base_path in DEFAULT_UNITY_PATHS:
            if not os.path.exists(base_path):
                continue
            
            try:
                # 버전 폴더들 검색
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        unity_exe = os.path.join(item_path, "Editor", "Unity.exe")
                        if os.path.exists(unity_exe):
                            logger.info(f"Unity Editor 발견: {unity_exe}")
                            return unity_exe
            except Exception as e:
                logger.debug(f"경로 검색 중 오류: {base_path} - {e}")
        
        logger.error("Unity Editor를 찾을 수 없습니다.")
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

# endregion

# =========================
# #region Unity CLI 실행기
# =========================

class UnityCliExecutor:
    """Unity CLI 명령어 실행기"""
    
    def __init__(self, toolkit_config: ToolkitConfig):
        self.config = toolkit_config
        self.unity_path = self._resolve_unity_path()
    
    def _resolve_unity_path(self) -> str:
        """Unity 경로를 결정합니다."""
        if self.config.unity_editor_path and os.path.exists(self.config.unity_editor_path):
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
            
            return success
            
        except subprocess.TimeoutExpired:
            logger.error(f"Unity 실행 타임아웃: {project.name} ({timeout}초)")
            return False
        except Exception as e:
            logger.error(f"Unity 실행 오류: {project.name} - {e}")
            return False
    
    def execute_action(self, project: UnityProjectConfig, action: ActionType) -> bool:
        """특정 액션을 실행합니다."""
        if action not in UNITY_CLI_METHODS:
            logger.error(f"지원하지 않는 액션: {action}")
            return False
        
        method_name = UNITY_CLI_METHODS[action]
        return self.execute_unity_method(project, method_name)

# endregion

# =========================
# #region 메인 Toolkit 클래스
# =========================

class DannectUnityToolkit:
    """Dannect Unity Toolkit 메인 클래스"""
    
    def __init__(self, config: Optional[ToolkitConfig] = None):
        self.config = config or ToolkitConfig()
        self.unity_executor = UnityCliExecutor(self.config)
    
    def discover_projects(self, base_directories: List[str]) -> List[UnityProjectConfig]:
        """여러 디렉토리에서 Unity 프로젝트들을 발견합니다."""
        all_projects = []
        
        for base_dir in base_directories:
            projects = UnityProjectManager.find_unity_projects(base_dir)
            all_projects.extend(projects)
        
        return all_projects
    
    def execute_single_project(self, project_path: str, action: ActionType) -> bool:
        """단일 프로젝트에서 액션을 실행합니다."""
        if not UnityProjectManager.is_unity_project(project_path):
            logger.error(f"Unity 프로젝트가 아닙니다: {project_path}")
            return False
        
        project = UnityProjectConfig(
            path=project_path,
            name=os.path.basename(project_path)
        )
        
        return self.unity_executor.execute_action(project, action)

# endregion

# =========================
# #region CLI 인터페이스
# =========================

def create_argument_parser() -> argparse.ArgumentParser:
    """명령행 인수 파서를 생성합니다."""
    parser = argparse.ArgumentParser(
        description="Dannect Unity Development Toolkit - 범용 Unity 개발 자동화 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  # 단일 프로젝트에서 전체 테스트 실행
  python dannect_unity_toolkit.py --project "C:/MyUnityProject" --action all_test
  
  # 여러 프로젝트에서 버튼 생성
  python dannect_unity_toolkit.py --projects-dir "C:/UnityProjects" --action create_button
  
액션 타입:
  all_test      - 전체 테스트 (버튼 생성 + 테스트 + 디버그)
  create_button - Rebuild 버튼 생성
  test_button   - 버튼 클릭 테스트
  debug_popup   - 팝업 오브젝트 디버그
  check_events  - 버튼 이벤트 확인
  project_info  - 프로젝트 정보 출력
        """
    )
    
    # 프로젝트 선택 옵션
    project_group = parser.add_mutually_exclusive_group(required=True)
    project_group.add_argument(
        "--project", 
        type=str,
        help="단일 Unity 프로젝트 경로"
    )
    project_group.add_argument(
        "--projects-dir", 
        type=str,
        help="Unity 프로젝트들이 있는 기본 디렉토리"
    )
    
    # 액션 설정
    parser.add_argument(
        "--action", 
        type=str,
        choices=[action.value for action in ActionType],
        required=True,
        help="실행할 액션 타입"
    )
    
    # Unity 설정
    parser.add_argument(
        "--unity-path", 
        type=str,
        help="Unity Editor 경로"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=300,
        help="Unity 실행 타임아웃 (초)"
    )
    
    # 로그 설정
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="로그 레벨"
    )
    
    return parser

def main():
    """메인 실행 함수"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 로거 설정
    global logger
    logger = DannectLogger(level=args.log_level)
    
    logger.start("=== Dannect Unity Toolkit v2.0 시작 ===")
    
    try:
        # Toolkit 설정
        toolkit_config = ToolkitConfig(
            unity_editor_path=args.unity_path or "",
            default_timeout=args.timeout,
            enable_logging=True,
            log_level=args.log_level
        )
        
        # Toolkit 인스턴스 생성
        toolkit = DannectUnityToolkit(toolkit_config)
        
        # 프로젝트 목록 결정
        projects = []
        
        if args.project:
            # 단일 프로젝트
            if not UnityProjectManager.is_unity_project(args.project):
                logger.error(f"Unity 프로젝트가 아닙니다: {args.project}")
                return 1
            
            projects = [UnityProjectConfig(path=args.project, name=os.path.basename(args.project))]
            
        elif args.projects_dir:
            # 디렉토리에서 프로젝트 자동 검색
            projects = toolkit.discover_projects([args.projects_dir])
        
        if not projects:
            logger.error("처리할 Unity 프로젝트를 찾을 수 없습니다.")
            return 1
        
        # 프로젝트 요약 표시
        logger.info("=== 프로젝트 요약 ===")
        logger.info(f"총 프로젝트 수: {len(projects)}")
        for i, project in enumerate(projects, 1):
            logger.info(f"{i:2d}. {project.name}")
        logger.info("====================")
        
        # 액션 실행
        action = ActionType(args.action)
        
        if len(projects) == 1:
            # 단일 프로젝트
            success = toolkit.execute_single_project(projects[0].path, action)
            result_code = 0 if success else 1
        else:
            # 다중 프로젝트 (순차 실행)
            success_count = 0
            for i, project in enumerate(projects, 1):
                logger.progress(f"[{i}/{len(projects)}] {project.name} 처리 중...")
                if toolkit.unity_executor.execute_action(project, action):
                    success_count += 1
            
            logger.complete(f"=== 최종 결과: {success_count}/{len(projects)} 성공 ===")
            result_code = 0 if success_count == len(projects) else 1
        
        logger.complete("=== Dannect Unity Toolkit 완료 ===")
        return result_code
        
    except KeyboardInterrupt:
        logger.warning("사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
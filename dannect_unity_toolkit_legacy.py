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
    BUILD_WEBGL_PARALLEL = "build_webgl_parallel"
    CLEAN_BUILDS = "clean_builds"
    PACKAGE_UPDATE = "package_update"
    PACKAGE_FORCE_UPDATE = "package_force_update"
    GIT_COMMIT = "git_commit"
    GIT_AUTO_BRANCH = "git_auto_branch"
    PROJECT_INFO = "project_info"
    UNITY_BATCH = "unity_batch"
    UNITY_BATCH_PARALLEL = "unity_batch_parallel"
    ADD_SYSTEM_METHODS = "add_system_methods"
    
    # 설정 관리 액션
    CREATE_CONFIG = "create_config"                        # 샘플 설정 파일 생성
    CREATE_PROJECTS_FILE = "create_projects_file"          # 샘플 프로젝트 목록 파일 생성
    SAVE_PROJECT_LIST = "save_project_list"               # 현재 프로젝트 목록을 파일로 저장

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
    project_directories: List[str] = None
    
    def __post_init__(self):
        if self.git_packages is None:
            self.git_packages = {
                "com.dannect.toolkit": "https://github.com/mmporong/unity-toolkit.git"
            }
        if self.project_directories is None:
            self.project_directories = []
    
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
                project_directories=config_data.get("project_directories", [])
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
                "project_directories": self.project_directories
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"설정 파일 저장 오류: {e}")
            return False

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
# #region 다중 프로젝트 관리 시스템
# =========================

class MultiProjectManager:
    """다중 프로젝트 관리자"""
    
    @staticmethod
    def load_projects_from_file(file_path: str) -> List[str]:
        """텍스트 파일에서 프로젝트 목록을 로드합니다."""
        if not os.path.exists(file_path):
            logger.error(f"프로젝트 목록 파일을 찾을 수 없습니다: {file_path}")
            return []
        
        projects = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # 빈 줄이나 주석(#로 시작) 건너뛰기
                    if not line or line.startswith('#'):
                        continue
                    
                    # 경로가 존재하는지 확인
                    if os.path.exists(line):
                        if UnityProjectManager.is_unity_project(line):
                            projects.append(line)
                            logger.debug(f"프로젝트 로드: {line}")
                        else:
                            logger.warning(f"Unity 프로젝트가 아님 (라인 {line_num}): {line}")
                    else:
                        logger.warning(f"경로가 존재하지 않음 (라인 {line_num}): {line}")
            
            logger.info(f"총 {len(projects)}개의 프로젝트를 파일에서 로드했습니다: {file_path}")
            return projects
            
        except Exception as e:
            logger.error(f"프로젝트 목록 파일 읽기 오류: {e}")
            return []
    
    @staticmethod
    def save_projects_to_file(projects: List[str], file_path: str) -> bool:
        """프로젝트 목록을 텍스트 파일로 저장합니다."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Dannect Unity Toolkit - 프로젝트 목록 파일\n")
                f.write("# 각 줄에 Unity 프로젝트 경로를 입력하세요\n")
                f.write("# '#'으로 시작하는 줄은 주석으로 처리됩니다\n\n")
                
                for project in projects:
                    f.write(f"{project}\n")
            
            logger.info(f"프로젝트 목록 저장 완료: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"프로젝트 목록 파일 저장 오류: {e}")
            return False
    
    @staticmethod
    def validate_projects(project_paths: List[str]) -> List[str]:
        """프로젝트 경로들을 검증하고 유효한 것들만 반환합니다."""
        valid_projects = []
        
        for path in project_paths:
            if not path.strip():
                continue
                
            if os.path.exists(path):
                if UnityProjectManager.is_unity_project(path):
                    valid_projects.append(path)
                    logger.debug(f"✅ 유효한 Unity 프로젝트: {path}")
                else:
                    logger.warning(f"⚠️ Unity 프로젝트가 아님: {path}")
            else:
                logger.warning(f"⚠️ 경로가 존재하지 않음: {path}")
        
        logger.info(f"총 {len(valid_projects)}개의 유효한 프로젝트 발견")
        return valid_projects
    
    @staticmethod
    def create_sample_config(file_path: str = "dannect_toolkit_config.json") -> bool:
        """샘플 설정 파일을 생성합니다."""
        sample_config = {
            "unity_editor_path": "",
            "default_timeout": 300,
            "max_parallel_workers": 3,
            "enable_logging": True,
            "log_level": "INFO",
            "git_packages": {
                "com.dannect.toolkit": "https://github.com/mmporong/SimGround_Package.git"
            },
            "project_directories": [
                "C:/UnityProjects/Project1",
                "C:/UnityProjects/Project2",
                "E:/SimGround_Package_v2/5.1.3.2_SolubilityObservation"
            ]
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"샘플 설정 파일 생성 완료: {file_path}")
            logger.info("설정 파일을 수정한 후 --config 옵션으로 사용하세요.")
            return True
            
        except Exception as e:
            logger.error(f"샘플 설정 파일 생성 오류: {e}")
            return False
    
    @staticmethod
    def create_sample_projects_file(file_path: str = "unity_projects.txt") -> bool:
        """샘플 프로젝트 목록 파일을 생성합니다."""
        sample_content = """# Dannect Unity Toolkit - 프로젝트 목록 파일
# 각 줄에 Unity 프로젝트 경로를 입력하세요
# '#'으로 시작하는 줄은 주석으로 처리됩니다

# 예시 프로젝트들
C:/UnityProjects/ScienceExperiment1
C:/UnityProjects/ScienceExperiment2
E:/SimGround_Package_v2/5.1.3.2_SolubilityObservation

# 필요한 만큼 프로젝트 경로를 추가하세요
"""
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            
            logger.info(f"샘플 프로젝트 목록 파일 생성 완료: {file_path}")
            logger.info("프로젝트 목록을 수정한 후 --projects-file 옵션으로 사용하세요.")
            return True
            
        except Exception as e:
            logger.error(f"샘플 프로젝트 목록 파일 생성 오류: {e}")
            return False

# endregion

# =========================
# #region Git 자동화 시스템
# =========================

class GitAutomationManager:
    """Git 자동화 관리자"""
    
    DEFAULT_BRANCH = "main"
    DEV_BRANCH = "dev"
    
    @staticmethod
    def run_git_command(command: str, cwd: str) -> Tuple[bool, str, str]:
        """Git 명령어를 실행하고 결과를 반환합니다."""
        try:
            result = subprocess.run(
                command, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                shell=True,
                encoding='utf-8',
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    @staticmethod
    def is_git_repository(project_path: str) -> bool:
        """해당 경로가 Git 리포지토리인지 확인합니다."""
        git_dir = os.path.join(project_path, ".git")
        return os.path.exists(git_dir)
    
    @staticmethod
    def initialize_git_repository(project_path: str, repo_url: str = None) -> bool:
        """Git 리포지토리를 초기화하고 원격 저장소를 설정합니다."""
        logger.progress(f"Git 리포지토리 초기화 중: {project_path}")
        
        # Git 초기화
        success, stdout, stderr = GitAutomationManager.run_git_command("git init", project_path)
        if not success:
            logger.error(f"Git 초기화 실패: {stderr}")
            return False
        
        # 원격 저장소 추가 (repo_url이 제공된 경우)
        if repo_url:
            success, stdout, stderr = GitAutomationManager.run_git_command(
                f"git remote add origin {repo_url}", project_path
            )
            if not success and "already exists" not in stderr:
                logger.warning(f"원격 저장소 추가 실패: {stderr}")
        
        logger.info(f"Git 리포지토리 초기화 완료")
        return True
    
    @staticmethod
    def get_current_branch(project_path: str) -> Optional[str]:
        """현재 브랜치명을 가져옵니다."""
        success, stdout, stderr = GitAutomationManager.run_git_command(
            "git branch --show-current", project_path
        )
        if success:
            return stdout.strip()
        return None
    
    @staticmethod
    def get_all_branches(project_path: str) -> List[str]:
        """모든 브랜치 목록을 가져옵니다."""
        success, stdout, stderr = GitAutomationManager.run_git_command(
            "git branch -a", project_path
        )
        if success:
            branches = []
            for line in stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('*'):
                    # 원격 브랜치 정보 제거
                    branch = line.replace('remotes/origin/', '').strip()
                    if branch and branch not in branches and not branch.startswith('HEAD'):
                        branches.append(branch)
            return branches
        return []
    
    @staticmethod
    def get_branch_hierarchy_info(project_path: str, branch_name: str) -> Tuple[int, int]:
        """브랜치의 계층 정보를 가져옵니다 (커밋 수와 최근 커밋 시간)."""
        # 브랜치의 커밋 수 가져오기
        success, commit_count, stderr = GitAutomationManager.run_git_command(
            f"git rev-list --count {branch_name}", project_path
        )
        if not success:
            return 0, 0
        
        # 브랜치의 최근 커밋 시간 가져오기 (Unix timestamp) 
        success, last_commit_time, stderr = GitAutomationManager.run_git_command(
            f"git log -1 --format=%ct {branch_name}", project_path
        )
        if not success:
            return int(commit_count) if commit_count.isdigit() else 0, 0
        
        return (
            int(commit_count) if commit_count.isdigit() else 0,
            int(last_commit_time) if last_commit_time.isdigit() else 0
        )
    
    @staticmethod
    def find_deepest_branch(project_path: str, branches: List[str]) -> Optional[str]:
        """브랜치 계층구조에서 가장 깊은(아래) 브랜치를 찾습니다."""
        if not branches:
            return None
        
        # main 브랜치 제외
        filtered_branches = [b for b in branches if b != GitAutomationManager.DEFAULT_BRANCH]
        if not filtered_branches:
            return None
        
        deepest_branch = None
        max_commits = 0
        latest_time = 0
        
        logger.debug("브랜치 계층 분석 중...")
        
        for branch in filtered_branches:
            commit_count, last_commit_time = GitAutomationManager.get_branch_hierarchy_info(
                project_path, branch
            )
            logger.debug(f"  {branch}: {commit_count}개 커밋, 최근 커밋: {last_commit_time}")
            
            # 커밋 수가 더 많거나, 커밋 수가 같으면 더 최근 브랜치 선택
            if (commit_count > max_commits or 
                (commit_count == max_commits and last_commit_time > latest_time)):
                max_commits = commit_count
                latest_time = last_commit_time
                deepest_branch = branch
        
        return deepest_branch
    
    @staticmethod
    def get_target_branch(project_path: str) -> str:
        """커밋할 대상 브랜치를 결정합니다."""
        branches = GitAutomationManager.get_all_branches(project_path)
        
        # 1. 브랜치 계층구조에서 가장 깊은(아래) 브랜치 찾기
        deepest_branch = GitAutomationManager.find_deepest_branch(project_path, branches)
        if deepest_branch:
            logger.info(f"계층구조에서 가장 깊은 브랜치 사용: {deepest_branch}")
            return deepest_branch
        
        # 2. 다른 브랜치가 없으면 dev 브랜치 확인
        if GitAutomationManager.DEV_BRANCH in branches:
            logger.info(f"dev 브랜치 사용")
            return GitAutomationManager.DEV_BRANCH
        
        # 3. dev 브랜치도 없으면 dev 브랜치 생성
        logger.info(f"적절한 브랜치가 없어 dev 브랜치를 새로 생성합니다")
        return GitAutomationManager.DEV_BRANCH
    
    @staticmethod
    def clean_git_status(project_path: str) -> bool:
        """Git 상태를 정리합니다."""
        logger.progress("Git 상태 정리 중...")
        
        # Untracked 파일들 정리
        success, stdout, stderr = GitAutomationManager.run_git_command("git clean -fd", project_path)
        if success:
            logger.debug("Untracked 파일 정리 완료")
        
        # 인덱스 리셋
        success, stdout, stderr = GitAutomationManager.run_git_command("git reset", project_path)
        if success:
            logger.debug("Git 인덱스 리셋 완료")
            return True
        else:
            logger.warning(f"Git 인덱스 리셋 실패: {stderr}")
            # 강제 리셋 시도
            success, stdout, stderr = GitAutomationManager.run_git_command(
                "git reset --hard HEAD", project_path
            )
            if success:
                logger.info("강제 리셋 완료")
                return True
            else:
                logger.error(f"강제 리셋도 실패: {stderr}")
                return False
    
    @staticmethod
    def checkout_or_create_branch(project_path: str, branch_name: str) -> bool:
        """브랜치로 체크아웃하거나 새로 생성합니다."""
        # 기존 브랜치로 체크아웃 시도
        success, stdout, stderr = GitAutomationManager.run_git_command(
            f"git checkout {branch_name}", project_path
        )
        
        if success:
            logger.info(f"브랜치 '{branch_name}' 체크아웃 완료")
            return True
        
        # 체크아웃 실패 시 브랜치 생성 시도
        if "did not match any file" in stderr or "pathspec" in stderr:
            logger.info(f"브랜치 '{branch_name}' 생성 및 체크아웃 시도")
            success, stdout, stderr = GitAutomationManager.run_git_command(
                f"git checkout -b {branch_name}", project_path
            )
            
            if success:
                logger.info(f"브랜치 '{branch_name}' 생성 완료")
                return True
            else:
                logger.error(f"브랜치 생성 실패: {stderr}")
                return False
        
        # 기타 Git 상태 문제로 인한 실패
        logger.warning(f"브랜치 체크아웃 실패, Git 상태 정리 후 재시도: {stderr}")
        if GitAutomationManager.clean_git_status(project_path):
            success, stdout, stderr = GitAutomationManager.run_git_command(
                f"git checkout {branch_name}", project_path
            )
            if success:
                logger.info(f"브랜치 '{branch_name}' 체크아웃 완료 (재시도)")
                return True
        
        logger.error(f"브랜치 체크아웃 최종 실패: {branch_name}")
        return False
    
    @staticmethod
    def commit_and_push_changes(project_path: str, commit_message: str = "Auto commit: Unity project updates") -> bool:
        """변경사항을 커밋하고 푸시합니다."""
        project_name = os.path.basename(project_path.rstrip(os.sep))
        logger.start(f"{project_name} Git 작업 시작")
        
        # Git 리포지토리 확인
        if not GitAutomationManager.is_git_repository(project_path):
            logger.warning(f"Git 리포지토리가 아닙니다. 초기화를 시도합니다: {project_path}")
            if not GitAutomationManager.initialize_git_repository(project_path):
                logger.error(f"Git 리포지토리 초기화 실패: {project_path}")
                return False
        
        # Git 상태 확인
        success, stdout, stderr = GitAutomationManager.run_git_command("git status --porcelain", project_path)
        if not success:
            logger.error(f"Git 상태 확인 실패: {stderr}")
            return False
        
        if not stdout.strip():
            logger.info(f"변경사항 없음: {project_name}")
            return True
        
        logger.info(f"변경사항 발견: {project_name}")
        
        # 대상 브랜치 결정
        target_branch = GitAutomationManager.get_target_branch(project_path)
        
        # 브랜치 체크아웃
        if not GitAutomationManager.checkout_or_create_branch(project_path, target_branch):
            return False
        
        # 변경사항 스테이징
        success, stdout, stderr = GitAutomationManager.run_git_command("git add .", project_path)
        if not success:
            logger.error(f"Git add 실패: {stderr}")
            return False
        
        # 커밋
        success, stdout, stderr = GitAutomationManager.run_git_command(
            f'git commit -m "{commit_message}"', project_path
        )
        if not success:
            logger.error(f"Git commit 실패: {stderr}")
            return False
        
        logger.info(f"커밋 완료: {project_name}")
        
        # 푸시
        success, stdout, stderr = GitAutomationManager.run_git_command(
            f"git push -u origin {target_branch}", project_path
        )
        if not success:
            logger.warning(f"Git push 실패 (원격 저장소 없음 가능): {stderr}")
            # push 실패해도 커밋은 성공했으므로 True 반환
        else:
            logger.info(f"푸시 완료: {project_name} -> {target_branch}")
        
        logger.complete(f"{project_name} Git 작업 완료")
        return True

# endregion

# =========================
# #region 패키지 관리 시스템
# =========================

class PackageManager:
    """Unity 패키지 관리자"""
    
    @staticmethod
    def add_git_packages_to_manifest(project_path: str, git_packages: Dict[str, str], 
                                   force_update: bool = True) -> bool:
        """Git 패키지를 manifest.json에 추가하거나 업데이트합니다."""
        manifest_path = os.path.join(project_path, "Packages", "manifest.json")
        if not os.path.exists(manifest_path):
            logger.error(f"manifest.json 파일이 없습니다: {manifest_path}")
            return False

        project_name = os.path.basename(project_path.rstrip(os.sep))
        logger.progress(f"{project_name} 패키지 처리 중")

        try:
            # manifest.json 파일 읽기
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            changed = False
            force_updated_packages = []

            # 모든 Git 패키지 추가/수정
            for name, url in git_packages.items():
                package_exists = name in manifest["dependencies"]
                
                if package_exists:
                    current_url = manifest["dependencies"][name]
                    
                    # com.dannect.toolkit 패키지는 항상 강제 업데이트
                    if name == "com.dannect.toolkit" and force_update:
                        logger.info(f"🔄 {name} 강제 업데이트 진행")
                        logger.debug(f"  기존: {current_url}")
                        logger.debug(f"  새버전: {url}")
                        
                        # 패키지를 임시로 제거한 후 다시 추가 (강제 업데이트)
                        del manifest["dependencies"][name]
                        manifest["dependencies"][name] = url
                        force_updated_packages.append(name)
                        changed = True
                        
                    elif current_url == url:
                        logger.debug(f"⚪ {name} 이미 최신 버전 설치됨")
                        continue
                    else:
                        logger.info(f"🔄 {name} 업데이트: {current_url} -> {url}")
                        manifest["dependencies"][name] = url
                        changed = True
                else:
                    logger.info(f"➕ {name} 새로 추가")
                    manifest["dependencies"][name] = url
                    changed = True

            # 변경된 경우에만 저장
            if changed:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=4, ensure_ascii=False)
                
                if force_updated_packages:
                    logger.complete(f"{project_name} 강제 업데이트 완료: {', '.join(force_updated_packages)}")
                else:
                    logger.complete(f"{project_name} 패키지 업데이트 완료")
                return True
            else:
                logger.info(f"⚪ {project_name} 변경 없음 (모든 패키지 최신 상태)")
                return True
                
        except Exception as e:
            logger.error(f"{project_name} 패키지 처리 실패: {e}")
            return False
    
    @staticmethod
    def create_package_refresh_script(project_path: str) -> bool:
        """패키지 새로고침 스크립트를 생성합니다."""
        editor_dir = os.path.join(project_path, "Assets", "Editor")
        os.makedirs(editor_dir, exist_ok=True)
        
        script_path = os.path.join(editor_dir, "PackageRefreshScript.cs")
        
        script_content = '''using UnityEngine;
using UnityEditor;
using UnityEditor.PackageManager;

public class PackageRefreshScript
{
    [MenuItem("Tools/Force Refresh Packages")]
    public static void ForceRefreshPackages()
    {
        Debug.Log("=== 패키지 강제 새로고침 시작 ===");
        
        // Package Manager 캐시 정리
        Client.Resolve();
        
        // Asset Database 갱신
        AssetDatabase.Refresh();
        AssetDatabase.SaveAssets();
        
        Debug.Log("=== 패키지 강제 새로고침 완료 ===");
    }
}
'''
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.debug(f"패키지 새로고침 스크립트 생성 완료: {script_path}")
            return True
        except Exception as e:
            logger.error(f"패키지 새로고침 스크립트 생성 실패: {e}")
            return False

# endregion

# =========================
# #region WebGL 빌드 자동화 시스템
# =========================

class WebGLBuildManager:
    """WebGL 빌드 자동화 관리자"""
    
    BUILD_TIMEOUT = 1800  # 30분
    BUILD_OUTPUT_DIR = "Builds"
    
    @staticmethod
    def create_webgl_build_script(project_path: str, output_path: str = None) -> bool:
        """Unity WebGL 빌드를 위한 Editor 스크립트를 생성합니다. (Unity 6 호환, Player Settings 완전 반영)"""
        editor_dir = os.path.join(project_path, "Assets", "Editor")
        os.makedirs(editor_dir, exist_ok=True)
        
        script_path = os.path.join(editor_dir, "AutoWebGLBuildScript.cs")
        
        if output_path is None:
            output_path = os.path.join(project_path, WebGLBuildManager.BUILD_OUTPUT_DIR, "WebGL")
        
        output_path_formatted = output_path.replace(os.sep, '/')
        
        # Unity 6 호환 WebGL 빌드 스크립트 (SimGround 버전과 동일)
        script_content = f'''using UnityEngine;
using UnityEditor;
using UnityEditor.Build;
using System.IO;

public class AutoWebGLBuildScript
{{
    [MenuItem("Build/Auto Build WebGL (Player Settings)")]
    public static void BuildWebGLWithPlayerSettings()
    {{
        Debug.Log("=== WebGL Player Settings 자동 설정 및 빌드 시작 ===");
        
        // WebGL Player Settings 자동 설정
        ConfigureWebGLPlayerSettings();
        
        // 설정된 Player Settings 정보 출력
        LogCurrentPlayerSettings();
        
        // 빌드 출력 경로 설정 (Product Name 기반)
        string buildPath = @"{output_path_formatted}";
        
        // Product Name이 설정되어 있다면 경로에 반영
        if (!string.IsNullOrEmpty(PlayerSettings.productName))
        {{
            string safeName = PlayerSettings.productName.Replace(" ", "_");
            // 특수문자 제거
            safeName = System.Text.RegularExpressions.Regex.Replace(safeName, @"[^\\w\\-_]", "");
            buildPath = Path.Combine(Path.GetDirectoryName(buildPath), safeName);
        }}
        
        // 출력 디렉토리 생성
        if (!Directory.Exists(buildPath))
        {{
            Directory.CreateDirectory(buildPath);
            Debug.Log($"빌드 출력 디렉토리 생성: {{buildPath}}");
        }}
        
        // 빌드할 씬들 가져오기 (Build Settings에서 활성화된 씬만)
        string[] scenes = GetBuildScenes();
        if (scenes.Length == 0)
        {{
            Debug.LogError("빌드할 씬이 없습니다. Build Settings에서 씬을 추가하세요.");
            return;
        }}
        
        // WebGL 빌드 옵션 설정 (Player Settings 완전 반영)
        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
        buildPlayerOptions.scenes = scenes;
        buildPlayerOptions.locationPathName = buildPath;
        buildPlayerOptions.target = BuildTarget.WebGL;
        
        // 빌드 옵션을 Player Settings에 따라 설정
        buildPlayerOptions.options = GetBuildOptionsFromPlayerSettings();
        
        // WebGL 특수 설정 적용
        ApplyWebGLSettings();
        
        Debug.Log($"🌐 WebGL 빌드 시작");
        Debug.Log($"📁 빌드 경로: {{buildPlayerOptions.locationPathName}}");
        Debug.Log($"🎮 제품명: {{PlayerSettings.productName}}");
        Debug.Log($"🏢 회사명: {{PlayerSettings.companyName}}");
        Debug.Log($"📋 버전: {{PlayerSettings.bundleVersion}}");
        
        // WebGL 빌드 실행
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);
        
        // 빌드 결과 확인
        if (report.summary.result == UnityEditor.Build.Reporting.BuildResult.Succeeded)
        {{
            Debug.Log($"✅ WebGL 빌드 성공!");
            Debug.Log($"📦 빌드 크기: {{FormatBytes(report.summary.totalSize)}}");
            Debug.Log($"⏱️ 빌드 시간: {{report.summary.totalTime}}");
            Debug.Log($"📁 빌드 경로: {{buildPath}}");
            Debug.Log($"🌐 WebGL 빌드 완료!");
        }}
        else
        {{
            Debug.LogError($"❌ WebGL 빌드 실패: {{report.summary.result}}");
            if (report.summary.totalErrors > 0)
            {{
                Debug.LogError($"에러 수: {{report.summary.totalErrors}}");
            }}
            if (report.summary.totalWarnings > 0)
            {{
                Debug.LogWarning($"경고 수: {{report.summary.totalWarnings}}");
            }}
        }}
        
        Debug.Log("=== WebGL Player Settings 반영 빌드 완료 ===");
    }}
    
    private static void ConfigureWebGLPlayerSettings()
    {{
        Debug.Log("🔧 WebGL Player Settings 이미지 기반 고정 설정 적용 중...");
        
        // 기본 제품 정보 설정 (비어있는 경우에만)
        if (string.IsNullOrEmpty(PlayerSettings.productName))
        {{
            PlayerSettings.productName = "Science Experiment Simulation";
            Debug.Log("✅ 제품명 설정: Science Experiment Simulation");
        }}
        
        if (string.IsNullOrEmpty(PlayerSettings.companyName))
        {{
            PlayerSettings.companyName = "Educational Software";
            Debug.Log("✅ 회사명 설정: Educational Software");
        }}
        
        if (string.IsNullOrEmpty(PlayerSettings.bundleVersion))
        {{
            PlayerSettings.bundleVersion = "1.0.0";
            Debug.Log("✅ 버전 설정: 1.0.0");
        }}
        
        // === 이미지 기반 고정 설정 적용 ===
        
        // Resolution and Presentation 설정 (이미지 기반)
        PlayerSettings.defaultWebScreenWidth = 1655;
        PlayerSettings.defaultWebScreenHeight = 892;
        PlayerSettings.runInBackground = true;
        Debug.Log("✅ 해상도 설정: 1655x892, Run In Background 활성화");
        
        // WebGL Template 설정 (이미지 기반: Minimal)
        PlayerSettings.WebGL.template = "APPLICATION:Minimal";
        Debug.Log("✅ WebGL 템플릿 설정: Minimal");
        
        // Publishing Settings (이미지 기반)
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Disabled;
        PlayerSettings.WebGL.nameFilesAsHashes = true;
        PlayerSettings.WebGL.dataCaching = true;
        // Unity 6에서 debugSymbols -> debugSymbolMode로 변경
        PlayerSettings.WebGL.debugSymbolMode = WebGLDebugSymbolMode.Off;
        PlayerSettings.WebGL.showDiagnostics = false;
        PlayerSettings.WebGL.decompressionFallback = false;
        Debug.Log("✅ Publishing Settings: 압축 비활성화, 파일명 해시화, 데이터 캐싱 활성화");
        
        // WebAssembly Language Features (이미지 기반)
        PlayerSettings.WebGL.exceptionSupport = WebGLExceptionSupport.ExplicitlyThrownExceptionsOnly;
        PlayerSettings.WebGL.threadsSupport = false;
        // Unity 6에서 wasmStreaming 제거됨 (decompressionFallback에 따라 자동 결정)
        Debug.Log("✅ WebAssembly 설정: 명시적 예외만, 멀티스레딩 비활성화, 스트리밍 자동");
        
        // Memory Settings (이미지 기반)
        PlayerSettings.WebGL.memorySize = 32;  // Initial Memory Size
        PlayerSettings.WebGL.memoryGrowthMode = WebGLMemoryGrowthMode.Geometric;
        PlayerSettings.WebGL.maximumMemorySize = 2048;
        Debug.Log("✅ 메모리 설정: 초기 32MB, 최대 2048MB, Geometric 증가");
        
        // Splash Screen 설정 (이미지 기반)
        PlayerSettings.SplashScreen.show = true;
        PlayerSettings.SplashScreen.showUnityLogo = false;
        PlayerSettings.SplashScreen.animationMode = PlayerSettings.SplashScreen.AnimationMode.Dolly;
        // Unity 6에서 logoAnimationMode 제거됨
        PlayerSettings.SplashScreen.overlayOpacity = 0.0f;
        PlayerSettings.SplashScreen.blurBackgroundImage = true;
        Debug.Log("✅ 스플래시 화면: Unity 로고 숨김, Dolly 애니메이션, 오버레이 투명");
        
        // WebGL 링커 타겟 설정 (Unity 6 최적화)
        PlayerSettings.WebGL.linkerTarget = WebGLLinkerTarget.Wasm;
        Debug.Log("✅ WebGL 링커 타겟 설정: WebAssembly (Unity 6 최적화)");
        
        Debug.Log("🔧 WebGL Player Settings 이미지 기반 고정 설정 완료");
    }}
    
    private static void LogCurrentPlayerSettings()
    {{
        Debug.Log("=== 현재 WebGL Player Settings ===");
        Debug.Log($"🎮 제품명: {{PlayerSettings.productName}}");
        Debug.Log($"🏢 회사명: {{PlayerSettings.companyName}}");
        Debug.Log($"📋 버전: {{PlayerSettings.bundleVersion}}");
        
        // Unity 6 호환성: 아이콘 API 확인 (Unity 버전에 따라 다름)
        try
        {{
            // Unity 6에서는 NamedBuildTarget과 IconKind 사용
            var icons = PlayerSettings.GetIcons(NamedBuildTarget.WebGL, IconKind.Application);
            Debug.Log($"🖼️ 기본 아이콘: {{(icons != null && icons.Length > 0 ? "설정됨" : "없음")}}");
        }}
        catch
        {{
            Debug.Log($"🖼️ 기본 아이콘: 확인 불가 (Unity 버전 호환성 문제)");
        }}
        
        // WebGL 전용 설정들
        Debug.Log($"🌐 WebGL 템플릿: {{PlayerSettings.WebGL.template}}");
        Debug.Log($"💾 WebGL 메모리 크기: {{PlayerSettings.WebGL.memorySize}}MB");
        Debug.Log($"📦 WebGL 압축 포맷: {{PlayerSettings.WebGL.compressionFormat}}");
        Debug.Log($"⚠️ WebGL 예외 지원: {{PlayerSettings.WebGL.exceptionSupport}}");
        Debug.Log($"💽 WebGL 데이터 캐싱: {{PlayerSettings.WebGL.dataCaching}}");
        Debug.Log($"🔧 WebGL 링커 타겟: {{PlayerSettings.WebGL.linkerTarget}}");
        Debug.Log($"🎯 WebGL 최적화: Unity 6에서 자동 관리");
        Debug.Log("=====================================");
    }}
    
    private static BuildOptions GetBuildOptionsFromPlayerSettings()
    {{
        BuildOptions options = BuildOptions.None;
        
        // Development Build 설정 확인
        if (EditorUserBuildSettings.development)
        {{
            options |= BuildOptions.Development;
            Debug.Log("✅ Development Build 모드 활성화");
        }}
        
        // Script Debugging 설정 확인
        if (EditorUserBuildSettings.allowDebugging)
        {{
            options |= BuildOptions.AllowDebugging;
            Debug.Log("✅ Script Debugging 활성화");
        }}
        
        // Profiler 설정 확인
        if (EditorUserBuildSettings.connectProfiler)
        {{
            options |= BuildOptions.ConnectWithProfiler;
            Debug.Log("✅ Profiler 연결 활성화");
        }}
        
        // Deep Profiling 설정 확인
        if (EditorUserBuildSettings.buildWithDeepProfilingSupport)
        {{
            options |= BuildOptions.EnableDeepProfilingSupport;
            Debug.Log("✅ Deep Profiling 지원 활성화");
        }}
        
        // Unity 6에서 autoRunPlayer 제거됨
        // WebGL은 브라우저에서 실행되므로 AutoRunPlayer 옵션 불필요
        Debug.Log("ℹ️ WebGL 빌드는 브라우저에서 수동 실행");
        
        return options;
    }}
    
    private static void ApplyWebGLSettings()
    {{
        Debug.Log("🌐 WebGL 특수 설정 적용 및 검증 중...");
        
        Debug.Log($"🌐 WebGL 템플릿 사용: {{PlayerSettings.WebGL.template}}");
        Debug.Log($"💾 WebGL 메모리 크기: {{PlayerSettings.WebGL.memorySize}}MB");
        Debug.Log($"📦 WebGL 압축 포맷: {{PlayerSettings.WebGL.compressionFormat}}");
        Debug.Log($"⚠️ WebGL 예외 지원: {{PlayerSettings.WebGL.exceptionSupport}}");
        Debug.Log($"💽 WebGL 데이터 캐싱: {{PlayerSettings.WebGL.dataCaching}}");
        
        // WebGL 최적화 설정 확인 및 권장사항
        if (PlayerSettings.WebGL.memorySize < 256)
        {{
            Debug.LogWarning("⚠️ WebGL 메모리 크기가 256MB 미만입니다. 과학실험 시뮬레이션에는 512MB 이상 권장합니다.");
        }}
        else if (PlayerSettings.WebGL.memorySize >= 512)
        {{
            Debug.Log("✅ WebGL 메모리 크기가 적절합니다 (512MB 이상).");
        }}
        
        if (string.IsNullOrEmpty(PlayerSettings.WebGL.template) || PlayerSettings.WebGL.template == "APPLICATION:Default")
        {{
            Debug.LogWarning("⚠️ WebGL 템플릿이 기본값입니다. 교육용 템플릿 사용을 권장합니다.");
        }}
        else
        {{
            Debug.Log($"✅ WebGL 템플릿 설정됨: {{PlayerSettings.WebGL.template}}");
        }}
        
        // WebGL 압축 설정 확인
        if (PlayerSettings.WebGL.compressionFormat == WebGLCompressionFormat.Disabled)
        {{
            Debug.LogWarning("⚠️ WebGL 압축이 비활성화되어 있습니다. 파일 크기가 클 수 있습니다.");
        }}
        else
        {{
            Debug.Log($"✅ WebGL 압축 활성화: {{PlayerSettings.WebGL.compressionFormat}}");
        }}
        
        // 과학실험 시뮬레이션에 최적화된 설정 권장사항
        Debug.Log("📚 과학실험 시뮬레이션 최적화 권장사항:");
        Debug.Log("  - 메모리: 512MB 이상");
        Debug.Log("  - 압축: Gzip 또는 Brotli");
        Debug.Log("  - 예외 지원: ExplicitlyThrownExceptionsOnly");
        Debug.Log("  - 데이터 캐싱: 활성화");
    }}
    
    private static string[] GetBuildScenes()
    {{
        // Build Settings에서 활성화된 씬들만 가져오기
        var enabledScenes = new System.Collections.Generic.List<string>();
        
        foreach (var scene in EditorBuildSettings.scenes)
        {{
            if (scene.enabled)
            {{
                enabledScenes.Add(scene.path);
            }}
        }}
        
        Debug.Log($"📋 빌드할 씬 수: {{enabledScenes.Count}}");
        foreach (var scene in enabledScenes)
        {{
            Debug.Log($"  - {{scene}}");
        }}
        
        return enabledScenes.ToArray();
    }}
    
    private static string FormatBytes(ulong bytes)
    {{
        string[] sizes = {{ "B", "KB", "MB", "GB", "TB" }};
        double len = bytes;
        int order = 0;
        while (len >= 1024 && order < sizes.Length - 1)
        {{
            order++;
            len = len / 1024;
        }}
        return $"{{len:0.##}} {{sizes[order]}}";
    }}
}}
'''
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.info(f"WebGL 빌드 스크립트 생성 완료: {script_path}")
            return True
        except Exception as e:
            logger.error(f"WebGL 빌드 스크립트 생성 실패: {e}")
            return False
    
    @staticmethod
    def run_webgl_build(project: UnityProjectConfig, unity_executor: 'UnityCliExecutor') -> bool:
        """Unity WebGL 빌드를 실행합니다."""
        logger.start(f"WebGL 빌드 시작: {project.name}")
        
        # WebGL 빌드 스크립트 생성
        if not WebGLBuildManager.create_webgl_build_script(project.path):
            return False
        
        # Unity CLI로 빌드 실행
        success = unity_executor.execute_unity_method(
            project, 
            "AutoWebGLBuildScript.BuildWebGLWithPlayerSettings",
            timeout=WebGLBuildManager.BUILD_TIMEOUT
        )
        
        if success:
            logger.complete(f"WebGL 빌드 성공: {project.name}")
        else:
            logger.error(f"WebGL 빌드 실패: {project.name}")
        
        return success
    
    @staticmethod
    def clean_build_outputs(project_path: str) -> bool:
        """빌드 출력물을 정리합니다."""
        build_dir = os.path.join(project_path, WebGLBuildManager.BUILD_OUTPUT_DIR)
        
        if os.path.exists(build_dir):
            try:
                import shutil
                shutil.rmtree(build_dir)
                logger.info(f"빌드 출력물 정리 완료: {build_dir}")
                return True
            except Exception as e:
                logger.error(f"빌드 출력물 정리 실패: {e}")
                return False
        else:
            logger.debug(f"빌드 출력물 없음: {build_dir}")
            return True

# endregion

# =========================
# #region SystemManager 메소드 추가 시스템
# =========================

class SystemManagerEditor:
    """SystemManager 메소드 자동 추가 관리자"""
    
    @staticmethod
    def find_system_manager_files(projects: List[UnityProjectConfig]) -> List[Tuple[str, str]]:
        """모든 프로젝트에서 SystemManager.cs 파일을 찾습니다."""
        system_manager_files = []
        
        for project in projects:
            assets_dir = os.path.join(project.path, "Assets")
            
            if not os.path.exists(assets_dir):
                logger.debug(f"Assets 폴더 없음: {project.path}")
                continue
            
            # Assets 폴더에서 SystemManager.cs 파일 찾기
            for root, dirs, files in os.walk(assets_dir):
                # 불필요한 폴더 제외
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['Library', 'Temp', 'Logs']]
                
                for file in files:
                    if file == "SystemManager.cs":
                        file_path = os.path.join(root, file)
                        system_manager_files.append((project.name, file_path))
                        logger.debug(f"SystemManager 발견: {project.name} -> {file_path}")
        
        return system_manager_files
    
    @staticmethod
    def check_method_exists_in_file(file_path: str, method_name: str) -> bool:
        """파일에서 특정 메소드가 이미 존재하는지 확인합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            pattern = rf'(public|private|protected|internal)\s+(static\s+)?(void|bool|int|float|string|[A-Z]\w*)\s+{re.escape(method_name)}\s*\('
            return bool(re.search(pattern, content))
            
        except Exception as e:
            logger.error(f"파일 읽기 오류 ({file_path}): {e}")
            return False
    
    @staticmethod
    def add_method_to_system_manager(file_path: str, method_code: str, class_name: str = "SystemManager") -> bool:
        """SystemManager 클래스에 새로운 메소드를 추가합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # SystemManager 클래스 찾기
            class_pattern = rf'public\s+class\s+{re.escape(class_name)}\s*[:\s\w,]*\s*\{{'
            class_match = re.search(class_pattern, content)
            
            if not class_match:
                logger.error(f"클래스 '{class_name}'를 찾을 수 없습니다: {file_path}")
                return False
            
            # 클래스 시작 위치
            class_start = class_match.end()
            
            # 중괄호 매칭으로 클래스 끝 찾기
            brace_count = 1
            pos = class_start
            
            while pos < len(content) and brace_count > 0:
                if content[pos] == '{{':
                    brace_count += 1
                elif content[pos] == '}}':
                    brace_count -= 1
                pos += 1
            
            if brace_count != 0:
                logger.error(f"클래스 끝을 찾을 수 없습니다: {file_path}")
                return False
            
            # 메소드 추가 위치 결정 (클래스 끝 직전)
            insertion_point = pos - 1
            
            # 들여쓰기 설정
            indent = "    "
            
            # 메소드 코드에 적절한 들여쓰기 적용
            indented_method = '\\n'.join([
                '',
                f'{indent}// 자동 추가된 메소드',
            ] + [f'{indent}{line}' if line.strip() else line for line in method_code.split('\\n')] + [''])
            
            # 새로운 내용 생성
            new_content = content[:insertion_point] + indented_method + content[insertion_point:]
            
            # 파일 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            logger.error(f"메소드 추가 실패 ({file_path}): {e}")
            return False
    
    @staticmethod
    def get_sample_methods() -> Dict[str, str]:
        """샘플 메소드들을 반환합니다."""
        return {{
            "ShowSuccessPopup": '''public void ShowSuccessPopup(string message = "실험 성공!")
{{
    // SuccessPopup 프리팹을 찾아서 활성화
    GameObject popup = GameObject.Find("SuccessPopup");
    if (popup != null)
    {{
        popup.SetActive(true);
        
        // 메시지 텍스트 설정
        var messageText = popup.GetComponentInChildren<UnityEngine.UI.Text>();
        if (messageText != null)
        {{
            messageText.text = message;
        }}
        
        Debug.Log($"성공 팝업 표시: {{message}}");
    }}
    else
    {{
        Debug.LogWarning("SuccessPopup을 찾을 수 없습니다.");
    }}
}}''',
            "HideSuccessPopup": '''public void HideSuccessPopup()
{{
    GameObject popup = GameObject.Find("SuccessPopup");
    if (popup != null)
    {{
        popup.SetActive(false);
        Debug.Log("성공 팝업 숨김");
    }}
}}''',
            "ResetExperiment": '''public void ResetExperiment()
{{
    Debug.Log("실험 리셋 시작");
    
    // 팝업들 모두 숨기기
    HideSuccessPopup();
    
    // 실험 상태 초기화
    // TODO: 실험별 리셋 로직 구현
    
    Debug.Log("실험 리셋 완료");
}}'''
        }}
    
    @staticmethod
    def add_methods_to_all_system_managers(projects: List[UnityProjectConfig], 
                                         methods_to_add: Dict[str, str] = None) -> bool:
        """모든 프로젝트의 SystemManager에 메소드들을 일괄 추가합니다."""
        if methods_to_add is None:
            methods_to_add = SystemManagerEditor.get_sample_methods()
        
        logger.start("SystemManager 메소드 일괄 추가 시작")
        
        # SystemManager 파일들 찾기
        system_manager_files = SystemManagerEditor.find_system_manager_files(projects)
        
        if not system_manager_files:
            logger.error("SystemManager.cs 파일을 찾을 수 없습니다.")
            return False
        
        logger.info(f"총 {len(system_manager_files)}개의 SystemManager 파일 발견")
        
        # 각 메소드별 결과 추적
        method_results = {{method_name: {{'added': 0, 'skipped': 0, 'failed': 0}} 
                         for method_name in methods_to_add.keys()}}
        
        # 각 SystemManager 파일 처리
        for project_name, file_path in system_manager_files:
            logger.progress(f"{project_name} SystemManager 처리 중")
            
            file_modified = False
            
            for method_name, method_code in methods_to_add.items():
                # 메소드가 이미 존재하는지 확인
                if SystemManagerEditor.check_method_exists_in_file(file_path, method_name):
                    logger.debug(f"  {method_name}: 이미 존재함")
                    method_results[method_name]['skipped'] += 1
                    continue
                
                # 메소드 추가
                if SystemManagerEditor.add_method_to_system_manager(file_path, method_code):
                    logger.info(f"  {method_name}: 추가 완료")
                    method_results[method_name]['added'] += 1
                    file_modified = True
                else:
                    logger.error(f"  {method_name}: 추가 실패")
                    method_results[method_name]['failed'] += 1
            
            if file_modified:
                logger.complete(f"{project_name} SystemManager 수정 완료")
        
        # 결과 요약
        logger.info("=== SystemManager 메소드 추가 결과 ===")
        for method_name, results in method_results.items():
            total = results['added'] + results['skipped'] + results['failed']
            logger.info(f"{method_name}: ✅{results['added']} ⚪{results['skipped']} ❌{results['failed']} (총 {total}개)")
        
        logger.complete("SystemManager 메소드 일괄 추가 완료")
        return True

# endregion

# =========================
# #region 메인 Toolkit 클래스
# =========================

class DannectUnityToolkit:
    """Dannect Unity Toolkit 메인 클래스"""
    
    def __init__(self, config: Optional[ToolkitConfig] = None):
        self.config = config or ToolkitConfig()
        self.unity_executor = UnityCliExecutor(self.config)
        self.git_manager = GitAutomationManager()
        self.package_manager = PackageManager()
        self.webgl_manager = WebGLBuildManager()
        self.system_editor = SystemManagerEditor()
    
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
        
        return self._execute_action_on_project(project, action)
    
    def execute_multiple_projects(self, projects: List[UnityProjectConfig], action: ActionType, 
                                 parallel: bool = False) -> List[Tuple[str, bool]]:
        """여러 프로젝트에서 액션을 실행합니다."""
        if parallel and action in [ActionType.BUILD_WEBGL, ActionType.UNITY_BATCH]:
            return self._execute_projects_parallel(projects, action)
        else:
            return self._execute_projects_sequential(projects, action)
    
    def _execute_projects_sequential(self, projects: List[UnityProjectConfig], action: ActionType) -> List[Tuple[str, bool]]:
        """순차적으로 프로젝트들을 처리합니다."""
        results = []
        success_count = 0
        
        for i, project in enumerate(projects, 1):
            logger.progress(f"[{i}/{len(projects)}] {project.name} 처리 중...")
            
            success = self._execute_action_on_project(project, action)
            results.append((project.name, success))
            
            if success:
                success_count += 1
                logger.info(f"✅ {project.name} 완료")
            else:
                logger.error(f"❌ {project.name} 실패")
        
        logger.complete(f"순차 처리 결과: {success_count}/{len(projects)} 성공")
        return results
    
    def _execute_projects_parallel(self, projects: List[UnityProjectConfig], action: ActionType) -> List[Tuple[str, bool]]:
        """병렬로 프로젝트들을 처리합니다."""
        max_workers = min(self.config.max_parallel_workers, len(projects))
        logger.start(f"병렬 처리 시작 (최대 {max_workers}개 동시 실행)")
        
        results = []
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 모든 프로젝트를 병렬로 제출
            future_to_project = {
                executor.submit(self._execute_action_on_project, project, action): project 
                for project in projects
            }
            
            # 완료된 작업들을 처리
            for future in as_completed(future_to_project):
                project = future_to_project[future]
                
                try:
                    success = future.result()
                    results.append((project.name, success))
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ {project.name} 병렬 처리 완료")
                    else:
                        logger.error(f"❌ {project.name} 병렬 처리 실패")
                except Exception as e:
                    logger.error(f"❌ {project.name} 병렬 처리 예외: {e}")
                    results.append((project.name, False))
        
        logger.complete(f"병렬 처리 결과: {success_count}/{len(projects)} 성공")
        return results
    
    def _execute_action_on_project(self, project: UnityProjectConfig, action: ActionType) -> bool:
        """단일 프로젝트에서 특정 액션을 실행합니다."""
        try:
            if action in UNITY_CLI_METHODS:
                # 기본 Unity CLI 액션
                return self.unity_executor.execute_action(project, action)
            
            elif action == ActionType.BUILD_WEBGL:
                # WebGL 빌드
                return self.webgl_manager.run_webgl_build(project, self.unity_executor)
            
            elif action == ActionType.CLEAN_BUILDS:
                # 빌드 출력물 정리
                return self.webgl_manager.clean_build_outputs(project.path)
            
            elif action == ActionType.PACKAGE_FORCE_UPDATE:
                # 패키지 강제 업데이트
                success = self.package_manager.add_git_packages_to_manifest(
                    project.path, self.config.git_packages, force_update=True
                )
                if success:
                    self.package_manager.create_package_refresh_script(project.path)
                return success
            
            elif action == ActionType.GIT_COMMIT:
                # Git 커밋 및 푸시
                return self.git_manager.commit_and_push_changes(project.path)
            
            elif action == ActionType.GIT_AUTO_BRANCH:
                # Git 자동 브랜치 관리
                target_branch = self.git_manager.get_target_branch(project.path)
                return self.git_manager.checkout_or_create_branch(project.path, target_branch)
            
            elif action == ActionType.ADD_SYSTEM_METHODS:
                # SystemManager 메소드 추가 (단일 프로젝트용)
                return self.system_editor.add_methods_to_all_system_managers([project])
            
            elif action == ActionType.UNITY_BATCH:
                # Unity 배치 스크립트 생성 및 실행
                return self._create_and_run_unity_batch_script(project)
            
            else:
                logger.error(f"지원하지 않는 액션: {action}")
                return False
                
        except Exception as e:
            logger.error(f"액션 실행 중 오류 발생: {project.name} - {action} - {e}")
            return False
    
    def _create_and_run_unity_batch_script(self, project: UnityProjectConfig) -> bool:
        """Unity 배치 스크립트를 생성하고 실행합니다."""
        editor_dir = os.path.join(project.path, "Assets", "Editor")
        os.makedirs(editor_dir, exist_ok=True)
        
        script_path = os.path.join(editor_dir, "AutoBatchProcessor.cs")
        
        script_content = '''using UnityEngine;
using UnityEditor;

public class AutoBatchProcessor
{
    [MenuItem("Tools/Process Batch")]
    public static void ProcessBatch()
    {
        Debug.Log("=== 배치 처리 시작 ===");
        
        // 패키지 임포트 대기
        AssetDatabase.Refresh();
        
        // PackageAssetCopier가 있다면 실행
        var copierType = System.Type.GetType("PackageAssetCopier");
        if (copierType != null)
        {
            var method = copierType.GetMethod("CopyFilesFromPackage", 
                System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
            if (method != null)
            {
                Debug.Log("PackageAssetCopier.CopyFilesFromPackage 실행");
                method.Invoke(null, null);
            }
        }
        
        // 최종 Asset Database 갱신
        AssetDatabase.Refresh();
        AssetDatabase.SaveAssets();
        
        Debug.Log("=== 배치 처리 완료 ===");
    }
}
'''
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            logger.debug(f"배치 스크립트 생성 완료: {script_path}")
            
            # Unity 배치 모드로 스크립트 실행
            return self.unity_executor.execute_unity_method(
                project, "AutoBatchProcessor.ProcessBatch"
            )
            
        except Exception as e:
            logger.error(f"배치 스크립트 생성/실행 실패: {e}")
            return False
    
    def process_package_updates(self, projects: List[UnityProjectConfig], force_update: bool = True) -> bool:
        """모든 프로젝트에 패키지 업데이트를 적용합니다."""
        logger.start("패키지 업데이트 처리 시작")
        
        success_count = 0
        for project in projects:
            logger.progress(f"{project.name} 패키지 업데이트 중")
            
            success = self.package_manager.add_git_packages_to_manifest(
                project.path, self.config.git_packages, force_update
            )
            
            if success:
                self.package_manager.create_package_refresh_script(project.path)
                success_count += 1
            
        logger.complete(f"패키지 업데이트 완료: {success_count}/{len(projects)} 성공")
        return success_count == len(projects)
    
    def process_git_operations(self, projects: List[UnityProjectConfig], 
                             commit_message: str = "Auto commit: Unity project updates") -> bool:
        """모든 프로젝트에 Git 작업을 적용합니다."""
        logger.start("Git 작업 처리 시작")
        
        success_count = 0
        for project in projects:
            if self.git_manager.commit_and_push_changes(project.path, commit_message):
                success_count += 1
        
        logger.complete(f"Git 작업 완료: {success_count}/{len(projects)} 성공")
        return success_count == len(projects)
    
    def process_system_manager_methods(self, projects: List[UnityProjectConfig], 
                                     custom_methods: Dict[str, str] = None) -> bool:
        """모든 프로젝트의 SystemManager에 메소드를 추가합니다."""
        return self.system_editor.add_methods_to_all_system_managers(projects, custom_methods)

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
  
  # 여러 프로젝트에서 WebGL 빌드 (병렬 처리) - 디렉토리에서 자동 검색
  python dannect_unity_toolkit.py --projects-dir "C:/UnityProjects" --action build_webgl --parallel
  
  # 다중 프로젝트 직접 지정
  python dannect_unity_toolkit.py --projects "C:/Project1" "D:/Project2" "E:/Project3" --action all_test
  
  # 프로젝트 목록 파일 사용
  python dannect_unity_toolkit.py --projects-file "my_projects.txt" --action build_webgl
  
  # 설정 파일 사용 (프로젝트 목록 포함)
  python dannect_unity_toolkit.py --config "toolkit_config.json" --full-workflow
  
  # 샘플 설정 파일 생성
  python dannect_unity_toolkit.py --action create_config --output "my_config.json"
  
  # 샘플 프로젝트 목록 파일 생성
  python dannect_unity_toolkit.py --action create_projects_file --output "my_projects.txt"
  
  # 현재 검색된 프로젝트 목록을 파일로 저장
  python dannect_unity_toolkit.py --projects-dir "C:/UnityProjects" --action save_project_list --output "found_projects.txt"

기본 액션 타입:
  all_test              - 전체 테스트 (버튼 생성 + 테스트 + 디버그)
  create_button         - Rebuild 버튼 생성
  test_button           - 버튼 클릭 테스트
  debug_popup           - 팝업 오브젝트 디버그
  check_events          - 버튼 이벤트 확인
  project_info          - 프로젝트 정보 출력

고급 액션 타입:
  build_webgl           - WebGL 빌드 자동화
  build_webgl_parallel  - WebGL 병렬 빌드
  clean_builds          - 빌드 출력물 정리
  package_force_update  - 패키지 강제 업데이트
  git_commit            - Git 커밋 및 푸시
  git_auto_branch       - Git 자동 브랜치 관리
  unity_batch           - Unity 배치 스크립트 실행
  unity_batch_parallel  - Unity 배치 병렬 실행
  add_system_methods    - SystemManager 메소드 추가

설정 관리 액션:
  create_config         - 샘플 설정 파일 생성
  create_projects_file  - 샘플 프로젝트 목록 파일 생성
  save_project_list     - 현재 프로젝트 목록을 파일로 저장

워크플로우 옵션:
  --full-workflow       - 패키지 업데이트 + Git 커밋 전체 워크플로우
  --package-git         - 패키지 업데이트 + Git 커밋
  --build-workflow      - WebGL 빌드 + 정리 워크플로우
        """
    )
    
    # 프로젝트 선택 옵션
    project_group = parser.add_mutually_exclusive_group()
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
    project_group.add_argument(
        "--projects", 
        nargs="+",
        help="다중 Unity 프로젝트 경로들 (공백으로 구분)"
    )
    project_group.add_argument(
        "--projects-file", 
        type=str,
        help="Unity 프로젝트 목록이 담긴 텍스트 파일"
    )
    project_group.add_argument(
        "--config", 
        type=str,
        help="설정 파일 경로 (project_directories 포함)"
    )
    
    # 액션 설정
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--action", 
        type=str,
        choices=[action.value for action in ActionType],
        help="실행할 액션 타입"
    )
    
    # 워크플로우 옵션
    action_group.add_argument(
        "--full-workflow",
        action="store_true",
        help="전체 워크플로우 실행 (패키지 업데이트 + Git 커밋)"
    )
    action_group.add_argument(
        "--package-git",
        action="store_true", 
        help="패키지 업데이트 + Git 커밋 워크플로우"
    )
    action_group.add_argument(
        "--build-workflow",
        action="store_true",
        help="WebGL 빌드 + 정리 워크플로우"
    )
    
    # 실행 옵션
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="병렬 처리 활성화 (WebGL 빌드, Unity 배치 등)"
    )
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="패키지 강제 업데이트 (기본값: True)"
    )
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Git 작업 건너뛰기"
    )
    parser.add_argument(
        "--skip-packages",
        action="store_true", 
        help="패키지 업데이트 건너뛰기"
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
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="병렬 처리 최대 워커 수"
    )
    
    # Git 설정
    parser.add_argument(
        "--commit-message",
        type=str,
        default="Auto commit: Unity project updates",
        help="Git 커밋 메시지"
    )
    
    # 로그 설정
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="로그 레벨"
    )
    
    # 출력 파일 설정
    parser.add_argument(
        "--output", 
        type=str,
        help="출력 파일 경로 (프로젝트 목록 저장, 설정 파일 생성 등에 사용)"
    )
    
    return parser

def main():
    """메인 실행 함수"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 로거 설정
    global logger
    logger = DannectLogger(level=args.log_level)
    
    logger.start("=== Dannect Unity Toolkit v2.0 Enhanced 시작 ===")
    
    try:
        # 설정 관리 액션 먼저 처리 (프로젝트 없이 실행 가능)
        if args.action == ActionType.CREATE_CONFIG.value:
            config_file = args.output or "dannect_toolkit_config.json"
            if MultiProjectManager.create_sample_config(config_file):
                return 0
            else:
                return 1
        
        if args.action == ActionType.CREATE_PROJECTS_FILE.value:
            projects_file = args.output or "unity_projects.txt"
            if MultiProjectManager.create_sample_projects_file(projects_file):
                return 0
            else:
                return 1
        
        # 프로젝트 경로 확인
        if not any([args.project, args.projects_dir, args.projects, args.projects_file, args.config]):
            logger.error("다음 중 하나를 지정해주세요: --project, --projects-dir, --projects, --projects-file, --config")
            return 1
        
        # 액션/워크플로우 확인
        if not any([args.action, args.full_workflow, args.package_git, args.build_workflow]):
            logger.error("실행할 액션 또는 워크플로우를 지정해주세요.")
            return 1
        
        # Toolkit 설정 - 설정 파일이 있으면 로드, 없으면 기본값
        if args.config:
            try:
                toolkit_config = ToolkitConfig.from_file(args.config)
                logger.info(f"설정 파일에서 로드: {args.config}")
                
                # CLI 옵션으로 덮어쓰기
                if args.unity_path:
                    toolkit_config.unity_editor_path = args.unity_path
                if args.timeout != 300:  # 기본값이 아니면
                    toolkit_config.default_timeout = args.timeout
                if args.max_workers != 3:  # 기본값이 아니면
                    toolkit_config.max_parallel_workers = args.max_workers
                toolkit_config.log_level = args.log_level
                
            except Exception as e:
                logger.error(f"설정 파일 로드 실패: {e}")
                return 1
        else:
            toolkit_config = ToolkitConfig(
                unity_editor_path=args.unity_path or "",
                default_timeout=args.timeout,
                max_parallel_workers=args.max_workers,
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
            
        elif args.projects:
            # 다중 프로젝트 직접 지정
            logger.info(f"다중 프로젝트 직접 지정: {len(args.projects)}개")
            valid_paths = MultiProjectManager.validate_projects(args.projects)
            projects = [UnityProjectConfig(path=path, name=os.path.basename(path)) for path in valid_paths]
            
        elif args.projects_file:
            # 프로젝트 목록 파일에서 로드
            logger.info(f"프로젝트 목록 파일에서 로드: {args.projects_file}")
            project_paths = MultiProjectManager.load_projects_from_file(args.projects_file)
            projects = [UnityProjectConfig(path=path, name=os.path.basename(path)) for path in project_paths]
            
        elif args.config:
            # 설정 파일의 project_directories에서 로드
            logger.info(f"설정 파일의 프로젝트 목록 사용: {len(toolkit_config.project_directories)}개")
            if toolkit_config.project_directories:
                valid_paths = MultiProjectManager.validate_projects(toolkit_config.project_directories)
                projects = [UnityProjectConfig(path=path, name=os.path.basename(path)) for path in valid_paths]
            else:
                logger.warning("설정 파일에 project_directories가 비어있습니다.")
        
        if not projects:
            logger.error("처리할 Unity 프로젝트를 찾을 수 없습니다.")
            return 1
        
        # 프로젝트 요약 표시
        logger.info("=== 프로젝트 요약 ===")
        logger.info(f"총 프로젝트 수: {len(projects)}")
        for i, project in enumerate(projects, 1):
            logger.info(f"{i:2d}. {project.name}")
        logger.info("====================")
        
        # 워크플로우 실행
        if args.full_workflow:
            return execute_full_workflow(toolkit, projects, args)
        elif args.package_git:
            return execute_package_git_workflow(toolkit, projects, args)
        elif args.build_workflow:
            return execute_build_workflow(toolkit, projects, args)
        elif args.action:
            return execute_single_action(toolkit, projects, args)
        
        logger.complete("=== Dannect Unity Toolkit 완료 ===")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return 1

def execute_full_workflow(toolkit: DannectUnityToolkit, projects: List[UnityProjectConfig], args) -> int:
    """전체 워크플로우를 실행합니다."""
    logger.start("=== 전체 워크플로우 실행 ===")
    
    success = True
    
    # 1. 패키지 업데이트
    if not args.skip_packages:
        logger.info("1️⃣ 패키지 업데이트 단계")
        if not toolkit.process_package_updates(projects, force_update=True):
            logger.error("패키지 업데이트 실패")
            success = False
    
    # 2. Unity 배치 실행 (옵션)
    if args.parallel:
        logger.info("2️⃣ Unity 배치 처리 단계 (병렬)")
        results = toolkit.execute_multiple_projects(projects, ActionType.UNITY_BATCH, parallel=True)
        if not all(result[1] for result in results):
            logger.warning("일부 Unity 배치 처리 실패")
    
    # 3. Git 커밋 및 푸시
    if not args.skip_git:
        logger.info("3️⃣ Git 커밋 및 푸시 단계")
        if not toolkit.process_git_operations(projects, args.commit_message):
            logger.error("Git 작업 실패")
            success = False
    
    if success:
        logger.complete("=== 전체 워크플로우 성공 ===")
        return 0
    else:
        logger.error("=== 전체 워크플로우 일부 실패 ===")
        return 1

def execute_package_git_workflow(toolkit: DannectUnityToolkit, projects: List[UnityProjectConfig], args) -> int:
    """패키지 + Git 워크플로우를 실행합니다."""
    logger.start("=== 패키지-Git 워크플로우 실행 ===")
    
    success = True
    
    # 1. 패키지 업데이트
    if not args.skip_packages:
        if not toolkit.process_package_updates(projects, force_update=True):
            success = False
    
    # 2. Git 커밋 및 푸시
    if not args.skip_git:
        if not toolkit.process_git_operations(projects, args.commit_message):
            success = False
    
    return 0 if success else 1

def execute_build_workflow(toolkit: DannectUnityToolkit, projects: List[UnityProjectConfig], args) -> int:
    """빌드 워크플로우를 실행합니다."""
    logger.start("=== 빌드 워크플로우 실행 ===")
    
    # 1. 빌드 출력물 정리
    logger.info("1️⃣ 빌드 출력물 정리")
    for project in projects:
        toolkit.webgl_manager.clean_build_outputs(project.path)
    
    # 2. WebGL 빌드
    logger.info("2️⃣ WebGL 빌드 실행")
    results = toolkit.execute_multiple_projects(projects, ActionType.BUILD_WEBGL, parallel=args.parallel)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    logger.complete(f"빌드 워크플로우 완료: {success_count}/{total_count} 성공")
    return 0 if success_count == total_count else 1

def execute_single_action(toolkit: DannectUnityToolkit, projects: List[UnityProjectConfig], args) -> int:
    """단일 액션을 실행합니다."""
    action = ActionType(args.action)
    logger.start(f"=== 액션 실행: {action.value} ===")
    
    # 특별한 처리가 필요한 액션들
    if action == ActionType.ADD_SYSTEM_METHODS:
        success = toolkit.process_system_manager_methods(projects)
        return 0 if success else 1
    
    elif action == ActionType.SAVE_PROJECT_LIST:
        # 현재 프로젝트 목록을 파일로 저장
        project_paths = [project.path for project in projects]
        output_file = getattr(args, 'output', None) or "current_projects.txt"
        
        logger.info(f"현재 프로젝트 목록을 파일로 저장: {output_file}")
        logger.info(f"저장할 프로젝트 수: {len(project_paths)}개")
        
        success = MultiProjectManager.save_projects_to_file(project_paths, output_file)
        if success:
            logger.complete(f"프로젝트 목록 저장 완료: {output_file}")
            logger.info("이 파일을 --projects-file 옵션으로 사용할 수 있습니다.")
        return 0 if success else 1
    
    # 단일 프로젝트 vs 다중 프로젝트
    if len(projects) == 1:
        success = toolkit.execute_single_project(projects[0].path, action)
        return 0 if success else 1
    else:
        # 병렬 처리 가능한 액션들
        parallel_actions = [
            ActionType.BUILD_WEBGL, 
            ActionType.UNITY_BATCH,
            ActionType.BUILD_WEBGL_PARALLEL,
            ActionType.UNITY_BATCH_PARALLEL
        ]
        
        use_parallel = args.parallel and action in parallel_actions
        results = toolkit.execute_multiple_projects(projects, action, parallel=use_parallel)
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        logger.complete(f"=== 최종 결과: {success_count}/{total_count} 성공 ===")
        return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main()) 
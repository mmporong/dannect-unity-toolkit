#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Main Class
모든 기능을 통합하는 메인 툴킷 클래스
"""

import os
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import ToolkitConfig, UnityProjectConfig
from .logger import logger
from .enums import ActionType, WorkflowType
from ..managers.unity import UnityProjectManager, UnityCliExecutor
from ..managers.git import GitAutomationManager
from ..managers.webgl import WebGLBuildManager
from ..managers.package import PackageManager
from ..managers.project import MultiProjectManager
from ..managers.system import SystemManagerEditor


class DannectUnityToolkit:
    """Dannect Unity Development Toolkit - 메인 클래스"""
    
    def __init__(self, config: Optional[ToolkitConfig] = None):
        self.config = config or ToolkitConfig()
        self.cli_executor = UnityCliExecutor(self.config)
        
        logger.info("🚀 Dannect Unity Toolkit 초기화 완료")
        logger.info(f"Unity Path: {self.config.unity_editor_path}")
        logger.info(f"Max Workers: {self.config.max_parallel_workers}")
    
    def execute_action(self, projects: List[str], action: ActionType, parallel: bool = False) -> bool:
        """프로젝트들에 대해 액션을 실행합니다."""
        if not projects:
            logger.error("실행할 프로젝트가 없습니다.")
            return False
        
        # 프로젝트 설정 생성
        project_configs = []
        for project_path in projects:
            config = UnityProjectConfig(path=project_path, name=os.path.basename(project_path))
            if config.is_valid():
                project_configs.append(config)
            else:
                logger.warning(f"유효하지 않은 프로젝트: {project_path}")
        
        if not project_configs:
            logger.error("유효한 프로젝트가 없습니다.")
            return False
        
        logger.start(f"액션 실행: {action.value} ({len(project_configs)}개 프로젝트)")
        
        if parallel and len(project_configs) > 1:
            return self._execute_parallel(project_configs, action)
        else:
            return self._execute_sequential(project_configs, action)
    
    def execute_workflow(self, projects: List[str], workflow: WorkflowType, parallel: bool = False) -> bool:
        """워크플로우를 실행합니다."""
        logger.start(f"워크플로우 실행: {workflow.value}")
        
        if workflow == WorkflowType.FULL_AUTOMATION:
            return self._execute_full_automation_workflow(projects, parallel)
        elif workflow == WorkflowType.WEBGL_BUILD_WORKFLOW:
            return self._execute_webgl_workflow(projects, parallel)
        elif workflow == WorkflowType.GIT_AUTOMATION_WORKFLOW:
            return self._execute_git_workflow(projects, parallel)
        else:
            logger.error(f"지원하지 않는 워크플로우: {workflow}")
            return False
    
    def _execute_sequential(self, projects: List[UnityProjectConfig], action: ActionType) -> bool:
        """순차적으로 액션을 실행합니다."""
        success_count = 0
        
        for project in projects:
            if self._execute_single_action(project, action):
                success_count += 1
        
        logger.complete(f"액션 실행 완료: {success_count}/{len(projects)} 성공")
        return success_count == len(projects)
    
    def _execute_parallel(self, projects: List[UnityProjectConfig], action: ActionType) -> bool:
        """병렬로 액션을 실행합니다."""
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=self.config.max_parallel_workers) as executor:
            future_to_project = {
                executor.submit(self._execute_single_action, project, action): project
                for project in projects
            }
            
            for future in as_completed(future_to_project):
                project = future_to_project[future]
                try:
                    if future.result():
                        success_count += 1
                except Exception as e:
                    logger.error(f"병렬 실행 오류: {project.name} - {e}")
        
        logger.complete(f"병렬 액션 실행 완료: {success_count}/{len(projects)} 성공")
        return success_count == len(projects)
    
    def _execute_single_action(self, project: UnityProjectConfig, action: ActionType) -> bool:
        """단일 프로젝트에 대해 액션을 실행합니다."""
        try:
            if action == ActionType.BUILD_WEBGL:
                return WebGLBuildManager.build_webgl(project, self.cli_executor.unity_path, self.config)
            elif action == ActionType.PACKAGE_UPDATE:
                return PackageManager.update_packages(project, self.config, force=False)
            elif action == ActionType.PACKAGE_FORCE_UPDATE:
                return PackageManager.update_packages(project, self.config, force=True)
            elif action == ActionType.GIT_COMMIT:
                return GitAutomationManager.commit_and_push_changes(project.path)
            elif action == ActionType.ADD_SYSTEM_METHOD:
                return SystemManagerEditor.add_rebuild_method(project)
            elif action == ActionType.CLEAN_BUILDS:
                return WebGLBuildManager.clean_webgl_builds(project)
            elif action == ActionType.CREATE_BUTTON:
                # 패키지가 설치되어 있다면 업데이트 후 버튼 생성
                PackageManager.update_packages(project, self.config, force=False)
                return self.cli_executor.execute_action(project, action)
            else:
                # 기본 Unity CLI 액션들
                return self.cli_executor.execute_action(project, action)
                
        except Exception as e:
            logger.error(f"액션 실행 오류: {project.name} - {action.value} - {e}")
            return False
    
    def _execute_full_automation_workflow(self, projects: List[str], parallel: bool) -> bool:
        """전체 자동화 워크플로우"""
        workflow_actions = [
            ActionType.PACKAGE_UPDATE,
            ActionType.ALL_TEST,
            ActionType.ADD_SYSTEM_METHOD,
            ActionType.CREATE_BUTTON,
            ActionType.BUILD_WEBGL,
            ActionType.GIT_COMMIT
        ]
        
        for action in workflow_actions:
            logger.info(f"워크플로우 단계: {action.value}")
            if not self.execute_action(projects, action, parallel):
                logger.error(f"워크플로우 실패: {action.value}")
                return False
        
        logger.success("전체 자동화 워크플로우 완료")
        return True
    
    def _execute_webgl_workflow(self, projects: List[str], parallel: bool) -> bool:
        """WebGL 빌드 워크플로우"""
        workflow_actions = [
            ActionType.CLEAN_BUILDS,
            ActionType.PACKAGE_UPDATE,
            ActionType.BUILD_WEBGL
        ]
        
        for action in workflow_actions:
            if not self.execute_action(projects, action, parallel):
                return False
        
        logger.success("WebGL 빌드 워크플로우 완료")
        return True
    
    def _execute_git_workflow(self, projects: List[str], parallel: bool) -> bool:
        """Git 자동화 워크플로우"""
        workflow_actions = [
            ActionType.ALL_TEST,
            ActionType.GIT_COMMIT
        ]
        
        for action in workflow_actions:
            if not self.execute_action(projects, action, parallel):
                return False
        
        logger.success("Git 자동화 워크플로우 완료")
        return True
    
    def discover_projects(self, base_dirs: Optional[List[str]] = None) -> List[str]:
        """프로젝트를 자동으로 발견합니다."""
        if not base_dirs:
            base_dirs = self.config.project_directories
        
        if not base_dirs:
            logger.warning("프로젝트 검색 디렉토리가 설정되지 않았습니다.")
            return []
        
        all_projects = []
        for base_dir in base_dirs:
            projects = UnityProjectManager.find_unity_projects(base_dir)
            all_projects.extend([p.path for p in projects])
        
        return list(set(all_projects))  # 중복 제거
    
    def validate_projects(self, project_paths: List[str]) -> tuple[List[str], List[str]]:
        """프로젝트들을 검증하고 유효한 것과 무효한 것을 분리합니다."""
        valid_projects = []
        invalid_projects = []
        
        for path in project_paths:
            config = UnityProjectConfig(path=path, name=os.path.basename(path))
            if config.is_valid():
                valid_projects.append(path)
            else:
                invalid_projects.append(path)
        
        return valid_projects, invalid_projects
    
    def get_status_report(self, project_paths: List[str]) -> dict:
        """프로젝트들의 상태를 리포트합니다."""
        report = {
            "total_projects": len(project_paths),
            "valid_projects": 0,
            "projects_with_toolkit": 0,
            "git_repositories": 0,
            "details": []
        }
        
        for path in project_paths:
            config = UnityProjectConfig(path=path, name=os.path.basename(path))
            
            project_info = {
                "name": config.name,
                "path": path,
                "is_valid": config.is_valid(),
                "has_toolkit": UnityProjectManager.has_dannect_toolkit_package(path),
                "is_git_repo": GitAutomationManager.is_git_repository(path),
                "unity_version": UnityProjectManager.get_project_unity_version(path)
            }
            
            if project_info["is_valid"]:
                report["valid_projects"] += 1
            if project_info["has_toolkit"]:
                report["projects_with_toolkit"] += 1
            if project_info["is_git_repo"]:
                report["git_repositories"] += 1
            
            report["details"].append(project_info)
        
        return report 
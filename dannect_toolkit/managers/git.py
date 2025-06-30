#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Git Manager
Git 자동화 시스템
"""

import os
import subprocess
from typing import Tuple, List, Optional
from ..core.logger import logger


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
    def get_current_branch(project_path: str) -> Optional[str]:
        """현재 브랜치명을 가져옵니다."""
        success, stdout, stderr = GitAutomationManager.run_git_command(
            "git branch --show-current", project_path
        )
        if success:
            return stdout.strip()
        return None
    
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
    def commit_and_push_changes(project_path: str, commit_message: str = "Auto commit: Unity project updates") -> bool:
        """변경사항을 커밋하고 푸시합니다."""
        project_name = os.path.basename(project_path.rstrip(os.sep))
        logger.start(f"{project_name} Git 작업 시작")
        
        # Git 리포지토리 확인
        if not GitAutomationManager.is_git_repository(project_path):
            logger.warning(f"Git 리포지토리가 아닙니다: {project_path}")
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
        
        logger.error(f"브랜치 체크아웃 최종 실패: {branch_name}")
        return False 
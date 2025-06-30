#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Project Manager
다중 프로젝트 관리 시스템
"""

import os
from typing import List
from .unity import UnityProjectManager
from ..core.logger import logger


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
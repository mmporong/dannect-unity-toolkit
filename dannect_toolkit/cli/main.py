#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit CLI Main
명령행 인터페이스 메인 모듈
"""

import argparse
import sys
from typing import List, Optional

from ..core.config import ToolkitConfig, load_config_with_fallback, create_sample_config
from ..core.enums import ActionType, WorkflowType
from ..core.logger import logger
from ..managers.project import MultiProjectManager
from .commands import execute_command


def create_argument_parser() -> argparse.ArgumentParser:
    """명령행 인수 파서를 생성합니다."""
    parser = argparse.ArgumentParser(
        description="Dannect Unity Development Toolkit - 범용 Unity 개발 자동화 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 단일 프로젝트에서 모든 테스트 실행
  python -m dannect_toolkit --project "C:/MyUnityProject" --action all_test
  
  # 다중 프로젝트에서 WebGL 빌드 (병렬)
  python -m dannect_toolkit --projects-dir "C:/Projects" --action build_webgl --parallel
  
  # 설정 파일 사용하여 전체 자동화 워크플로우 실행
  python -m dannect_toolkit --config toolkit_config.json --workflow full_automation
  
  # 프로젝트 목록 파일 사용
  python -m dannect_toolkit --projects-file projects.txt --action create_button
        """)
    
    # 프로젝트 지정 방식들 (5가지)
    project_group = parser.add_mutually_exclusive_group()
    project_group.add_argument(
        "--project", 
        help="단일 Unity 프로젝트 경로"
    )
    project_group.add_argument(
        "--projects-dir", 
        help="Unity 프로젝트들이 있는 디렉토리 (자동 검색)"
    )
    project_group.add_argument(
        "--projects", 
        nargs="+", 
        help="여러 Unity 프로젝트 경로들 (공백으로 구분)"
    )
    project_group.add_argument(
        "--projects-file", 
        help="Unity 프로젝트 목록이 담긴 텍스트 파일"
    )
    project_group.add_argument(
        "--config", 
        help="툴킷 설정 파일 (JSON 형식)"
    )
    
    # 액션 및 워크플로우
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--action", 
        choices=[action.value for action in ActionType],
        help="실행할 액션"
    )
    action_group.add_argument(
        "--workflow", 
        choices=[workflow.value for workflow in WorkflowType],
        help="실행할 워크플로우"
    )
    
    # 실행 옵션들
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="병렬 처리 사용 (다중 프로젝트 시)"
    )
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=3, 
        help="병렬 처리 시 최대 워커 수 (기본값: 3)"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=300, 
        help="Unity 명령어 타임아웃 (초, 기본값: 300)"
    )
    
    # 출력 및 로깅
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        default="INFO", 
        help="로그 레벨 (기본값: INFO)"
    )
    parser.add_argument(
        "--output", 
        help="결과를 저장할 파일 경로"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true", 
        help="최소한의 출력만 표시"
    )
    
    # 유틸리티 명령어들
    parser.add_argument(
        "--create-config", 
        action="store_true", 
        help="샘플 설정 파일 생성"
    )
    parser.add_argument(
        "--create-projects-file", 
        action="store_true", 
        help="샘플 프로젝트 목록 파일 생성"
    )
    parser.add_argument(
        "--validate-projects", 
        action="store_true", 
        help="프로젝트들의 유효성 검사"
    )
    parser.add_argument(
        "--status-report", 
        action="store_true", 
        help="프로젝트들의 상태 리포트 생성"
    )
    
    # 버전 정보
    parser.add_argument(
        "--version", 
        action="version", 
        version="Dannect Unity Toolkit v2.0.0"
    )
    
    return parser


def resolve_projects(args: argparse.Namespace) -> List[str]:
    """명령행 인수에서 프로젝트 목록을 결정합니다."""
    projects = []
    
    if args.project:
        projects = [args.project]
    elif args.projects:
        projects = args.projects
    elif args.projects_dir:
        from ..managers.unity import UnityProjectManager
        project_configs = UnityProjectManager.find_unity_projects(args.projects_dir)
        projects = [config.path for config in project_configs]
    elif args.projects_file:
        projects = MultiProjectManager.load_projects_from_file(args.projects_file)
    elif args.config:
        config = load_config_with_fallback(args.config)
        projects = config.project_directories
    
    # 프로젝트 유효성 검사
    valid_projects = MultiProjectManager.validate_projects(projects)
    
    return valid_projects


def main():
    """메인 실행 함수"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 로거 설정
    if args.quiet:
        logger.set_level("ERROR")
    else:
        logger.set_level(args.log_level)
    
    logger.info("🚀 Dannect Unity Toolkit 시작")
    
    # 유틸리티 명령어들 처리
    if args.create_config:
        create_sample_config()
        return 0
    
    if args.create_projects_file:
        MultiProjectManager.create_sample_projects_file()
        return 0
    
    # 프로젝트 목록 결정
    projects = resolve_projects(args)
    
    if not projects:
        logger.error("실행할 프로젝트를 찾을 수 없습니다.")
        logger.info("다음 옵션 중 하나를 사용하세요:")
        logger.info("  --project <경로>")
        logger.info("  --projects-dir <디렉토리>")
        logger.info("  --projects <경로1> <경로2> ...")
        logger.info("  --projects-file <파일>")
        logger.info("  --config <설정파일>")
        return 1
    
    # 유효성 검사 및 상태 리포트
    if args.validate_projects or args.status_report:
        from ..core.toolkit import DannectUnityToolkit
        toolkit = DannectUnityToolkit()
        
        if args.validate_projects:
            valid, invalid = toolkit.validate_projects(projects)
            logger.info(f"유효한 프로젝트: {len(valid)}개")
            logger.info(f"무효한 프로젝트: {len(invalid)}개")
            
            if invalid:
                logger.warning("무효한 프로젝트들:")
                for project in invalid:
                    logger.warning(f"  - {project}")
            
            return 0 if not invalid else 1
        
        if args.status_report:
            report = toolkit.get_status_report(projects)
            logger.info("=== 프로젝트 상태 리포트 ===")
            logger.info(f"총 프로젝트: {report['total_projects']}개")
            logger.info(f"유효한 프로젝트: {report['valid_projects']}개")
            logger.info(f"Toolkit 설치됨: {report['projects_with_toolkit']}개")
            logger.info(f"Git 리포지토리: {report['git_repositories']}개")
            
            for detail in report['details']:
                status = "✅" if detail['is_valid'] else "❌"
                toolkit_status = "📦" if detail['has_toolkit'] else "⚪"
                git_status = "🔄" if detail['is_git_repo'] else "⚪"
                
                logger.info(f"{status} {toolkit_status} {git_status} {detail['name']}")
                if detail['unity_version']:
                    logger.info(f"    Unity: {detail['unity_version']}")
            
            return 0
    
    # 설정 로드
    config = load_config_with_fallback(args.config)
    config.max_parallel_workers = args.max_workers
    config.default_timeout = args.timeout
    config.log_level = args.log_level
    
    # 명령어 실행
    try:
        success = execute_command(args, projects, config)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.warning("사용자에 의해 중단되었습니다.")
        return 130
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return 1
    finally:
        logger.info("Dannect Unity Toolkit 종료")


if __name__ == "__main__":
    sys.exit(main()) 
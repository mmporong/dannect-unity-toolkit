#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit CLI Commands
CLI 명령어 실행 로직
"""

import argparse
from typing import List

from ..core.config import ToolkitConfig
from ..core.enums import ActionType, WorkflowType
from ..core.logger import logger
from ..core.toolkit import DannectUnityToolkit


def execute_command(args: argparse.Namespace, projects: List[str], config: ToolkitConfig) -> bool:
    """CLI 명령어를 실행합니다."""
    toolkit = DannectUnityToolkit(config)
    
    logger.info(f"대상 프로젝트: {len(projects)}개")
    for i, project in enumerate(projects, 1):
        logger.info(f"  {i}. {project}")
    
    # 액션 실행
    if args.action:
        action = ActionType(args.action)
        logger.info(f"실행 액션: {action.value}")
        
        if args.parallel:
            logger.info("병렬 처리 모드")
        
        return toolkit.execute_action(projects, action, args.parallel)
    
    # 워크플로우 실행
    elif args.workflow:
        workflow = WorkflowType(args.workflow)
        logger.info(f"실행 워크플로우: {workflow.value}")
        
        if args.parallel:
            logger.info("병렬 처리 모드")
        
        return toolkit.execute_workflow(projects, workflow, args.parallel)
    
    else:
        logger.error("액션 또는 워크플로우를 지정해야 합니다.")
        return False 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Package Manager
Unity 패키지 관리 시스템
"""

import os
import json
from typing import Dict, List
from ..core.config import UnityProjectConfig, ToolkitConfig
from ..core.logger import logger


class PackageManager:
    """Unity 패키지 관리자"""
    
    @staticmethod
    def update_packages(project: UnityProjectConfig, config: ToolkitConfig, force: bool = False) -> bool:
        """패키지를 업데이트합니다."""
        manifest_path = project.get_packages_manifest_path()
        
        if not os.path.exists(manifest_path):
            logger.error(f"manifest.json 파일을 찾을 수 없습니다: {project.name}")
            return False
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            updated = False
            dependencies = manifest.get("dependencies", {})
            
            # Git 패키지 업데이트
            for package_name, package_url in config.git_packages.items():
                if package_name in dependencies:
                    old_url = dependencies[package_name]
                    if force or old_url != package_url:
                        dependencies[package_name] = package_url
                        updated = True
                        logger.info(f"패키지 업데이트: {package_name}")
                else:
                    dependencies[package_name] = package_url
                    updated = True
                    logger.info(f"패키지 추가: {package_name}")
            
            if updated:
                manifest["dependencies"] = dependencies
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)
                
                logger.success(f"패키지 업데이트 완료: {project.name}")
            else:
                logger.info(f"패키지 업데이트 불필요: {project.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"패키지 업데이트 오류: {project.name} - {e}")
            return False 
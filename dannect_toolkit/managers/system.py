#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit System Manager Editor
SystemManager 클래스에 메소드를 자동으로 추가하는 시스템
"""

import os
import re
from typing import List, Optional
from ..core.config import UnityProjectConfig
from ..core.logger import logger


class SystemManagerEditor:
    """SystemManager 자동 편집기"""
    
    SAMPLE_METHOD = '''
    /// <summary>
    /// Dannect Toolkit에서 자동 생성된 메소드
    /// 리빌드 버튼 클릭 시 호출됩니다
    /// </summary>
    public void OnRebuildButtonClicked()
    {
        // 리빌드 로직을 여기에 구현하세요
        Debug.Log("리빌드 버튼이 클릭되었습니다!");
        
        // 예시: 씬 재시작
        // SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        
        // 예시: 특정 초기화 메소드 호출
        // ResetExperiment();
    }
    
    /// <summary>
    /// 실험 초기화 메소드 (예시)
    /// </summary>
    private void ResetExperiment()
    {
        // 실험 상태 초기화 로직
        Debug.Log("실험이 초기화되었습니다.");
    }'''
    
    @staticmethod
    def find_system_manager_files(project: UnityProjectConfig) -> List[str]:
        """프로젝트에서 SystemManager 파일들을 찾습니다."""
        system_manager_files = []
        assets_path = os.path.join(project.path, "Assets")
        
        if not os.path.exists(assets_path):
            return system_manager_files
        
        # Assets 폴더에서 SystemManager.cs 파일들 찾기
        for root, dirs, files in os.walk(assets_path):
            for file in files:
                if file == "SystemManager.cs":
                    file_path = os.path.join(root, file)
                    system_manager_files.append(file_path)
                    logger.debug(f"SystemManager 파일 발견: {file_path}")
        
        return system_manager_files
    
    @staticmethod
    def add_rebuild_method(project: UnityProjectConfig, method_name: str = "OnRebuildButtonClicked") -> bool:
        """SystemManager에 리빌드 메소드를 추가합니다."""
        system_files = SystemManagerEditor.find_system_manager_files(project)
        
        if not system_files:
            logger.warning(f"SystemManager.cs 파일을 찾을 수 없습니다: {project.name}")
            return False
        
        success_count = 0
        
        for file_path in system_files:
            if SystemManagerEditor._add_method_to_file(file_path, method_name):
                success_count += 1
        
        if success_count > 0:
            logger.success(f"SystemManager 메소드 추가 완료: {project.name} ({success_count}개 파일)")
            return True
        else:
            logger.error(f"SystemManager 메소드 추가 실패: {project.name}")
            return False
    
    @staticmethod
    def _add_method_to_file(file_path: str, method_name: str) -> bool:
        """파일에 메소드를 추가합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 이미 메소드가 있는지 확인
            if method_name in content:
                logger.debug(f"메소드가 이미 존재합니다: {method_name}")
                return True
            
            # 클래스의 마지막 부분 (마지막 }) 찾기
            class_pattern = r'(public\s+class\s+SystemManager.*?{.*?)(\s*}\s*$)'
            match = re.search(class_pattern, content, re.DOTALL | re.MULTILINE)
            
            if not match:
                logger.warning(f"SystemManager 클래스를 찾을 수 없습니다: {file_path}")
                return False
            
            # 메소드 추가
            class_content = match.group(1)
            closing_brace = match.group(2)
            
            new_content = content.replace(
                match.group(0),
                class_content + SystemManagerEditor.SAMPLE_METHOD + "\n" + closing_brace
            )
            
            # 파일 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"메소드 추가 완료: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"메소드 추가 오류: {file_path} - {e}")
            return False
    
    @staticmethod
    def validate_system_manager(project: UnityProjectConfig) -> tuple[bool, List[str]]:
        """SystemManager 파일의 유효성을 검사합니다."""
        messages = []
        system_files = SystemManagerEditor.find_system_manager_files(project)
        
        if not system_files:
            messages.append("SystemManager.cs 파일이 없습니다")
            return False, messages
        
        valid_files = 0
        
        for file_path in system_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 기본 검증
                if "class SystemManager" in content:
                    valid_files += 1
                    messages.append(f"✅ 유효한 SystemManager: {os.path.basename(file_path)}")
                    
                    # 리빌드 메소드 확인
                    if "OnRebuildButtonClicked" in content:
                        messages.append(f"  - 리빌드 메소드 존재")
                    else:
                        messages.append(f"  - 리빌드 메소드 없음 (자동 추가 가능)")
                else:
                    messages.append(f"⚠️ SystemManager 클래스를 찾을 수 없음: {file_path}")
                    
            except Exception as e:
                messages.append(f"❌ 파일 읽기 오류: {file_path} - {e}")
        
        is_valid = valid_files > 0
        return is_valid, messages 
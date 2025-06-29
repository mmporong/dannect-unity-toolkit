#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unity CLI Runner for Rebuild Button Functions
유니티 Rebuild 버튼 기능을 CLI로 실행하는 파이썬 스크립트

Usage:
    python unity_cli_runner.py --action all_test
    python unity_cli_runner.py --action create_button
    python unity_cli_runner.py --action test_click
    python unity_cli_runner.py --action debug_success_pop
    python unity_cli_runner.py --action check_events
"""

import subprocess
import os
import sys
import argparse
import time
from pathlib import Path
import json
from datetime import datetime


class UnityCliRunner:
    def __init__(self, project_path=None, unity_path=None):
        """
        Unity CLI Runner 초기화
        
        Args:
            project_path (str): Unity 프로젝트 경로 (현재 디렉토리 기본값)
            unity_path (str): Unity 실행 파일 경로 (자동 감지 시도)
        """
        self.project_path = project_path or os.getcwd()
        self.unity_path = unity_path or self._find_unity_path()
        self.log_file = os.path.join(self.project_path, "Logs", "Editor.log")
        
        print(f"🎯 Unity CLI Runner 초기화")
        print(f"📁 프로젝트 경로: {self.project_path}")
        print(f"🎮 Unity 경로: {self.unity_path}")
        print(f"📝 로그 파일: {self.log_file}")

    def _find_unity_path(self):
        """Unity 실행 파일 경로를 자동으로 찾습니다."""
        possible_paths = [
            # Windows
            "C:\\Program Files\\Unity\\Hub\\Editor\\*\\Editor\\Unity.exe",
            "C:\\Program Files\\Unity\\Editor\\Unity.exe",
            "D:\\Unity\\6000.0.30f1\\Editor\\Unity.exe",
            # 환경 변수에서 찾기
            os.environ.get("UNITY_EDITOR_PATH", ""),
        ]
        
        for path_pattern in possible_paths:
            if "*" in path_pattern:
                # 와일드카드가 있는 경우 glob로 찾기
                import glob
                matches = glob.glob(path_pattern)
                if matches:
                    # 가장 최신 버전 선택
                    return max(matches, key=os.path.getctime)
            elif os.path.exists(path_pattern):
                return path_pattern
        
        # Unity가 PATH에 있는지 확인
        try:
            result = subprocess.run(["unity", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return "unity"
        except:
            pass
        
        print("⚠️  Unity 경로를 자동으로 찾을 수 없습니다.")
        print("💡 --unity-path 옵션으로 Unity 경로를 직접 지정해주세요.")
        return None

    def run_unity_method(self, method_name, timeout=60):
        """
        Unity CLI로 지정된 메소드를 실행합니다.
        
        Args:
            method_name (str): 실행할 메소드명 (CreateTestButton.CLI_메소드명)
            timeout (int): 타임아웃 시간 (초)
            
        Returns:
            tuple: (성공여부, 로그내용)
        """
        if not self.unity_path:
            return False, "Unity 경로를 찾을 수 없습니다."
        
        full_method_name = f"CreateTestButton.{method_name}"
        
        print(f"\n🚀 Unity CLI 실행 중...")
        print(f"📋 메소드: {full_method_name}")
        print(f"⏱️  타임아웃: {timeout}초")
        
        # Unity CLI 명령어 구성
        cmd = [
            self.unity_path,
            "-batchmode",
            "-quit",
            "-projectPath", self.project_path,
            "-executeMethod", full_method_name,
            "-logFile", "-"  # 표준 출력으로 로그 출력
        ]
        
        print(f"💻 실행 명령어: {' '.join(cmd)}")
        
        try:
            # 시작 시간 기록
            start_time = time.time()
            
            # Unity 프로세스 실행
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.project_path
            )
            
            # 타임아웃과 함께 프로세스 대기
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                
                # 실행 시간 계산
                execution_time = time.time() - start_time
                
                print(f"✅ Unity 프로세스 완료")
                print(f"🏁 반환 코드: {return_code}")
                print(f"⏱️  실행 시간: {execution_time:.2f}초")
                
                # 로그 내용 준비
                log_content = f"=== Unity CLI 실행 결과 ===\n"
                log_content += f"메소드: {full_method_name}\n"
                log_content += f"실행 시간: {execution_time:.2f}초\n"
                log_content += f"반환 코드: {return_code}\n\n"
                
                if stdout:
                    log_content += "=== 표준 출력 ===\n"
                    log_content += stdout + "\n"
                
                if stderr:
                    log_content += "=== 표준 에러 ===\n"
                    log_content += stderr + "\n"
                
                # 성공 여부 판단 (반환 코드 0이면 성공)
                success = return_code == 0
                
                if success:
                    print("🎉 Unity CLI 실행 성공!")
                else:
                    print(f"❌ Unity CLI 실행 실패 (코드: {return_code})")
                
                return success, log_content
                
            except subprocess.TimeoutExpired:
                print(f"⏰ 타임아웃 ({timeout}초) - Unity 프로세스를 강제 종료합니다.")
                process.kill()
                stdout, stderr = process.communicate()
                
                log_content = f"=== Unity CLI 타임아웃 ===\n"
                log_content += f"메소드: {full_method_name}\n"
                log_content += f"타임아웃: {timeout}초\n\n"
                
                return False, log_content
                
        except Exception as e:
            error_msg = f"Unity CLI 실행 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def save_log(self, content, action_name):
        """실행 결과를 로그 파일로 저장합니다."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"unity_cli_{action_name}_{timestamp}.log"
        log_path = os.path.join(self.project_path, log_filename)
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📝 로그 저장: {log_path}")
            return log_path
        except Exception as e:
            print(f"⚠️  로그 저장 실패: {e}")
            return None

    def run_action(self, action, save_log=True):
        """
        지정된 액션을 실행합니다.
        
        Args:
            action (str): 실행할 액션
            save_log (bool): 로그 파일 저장 여부
            
        Returns:
            bool: 성공 여부
        """
        action_map = {
            "all_test": "CLI_AllInOneRebuildButtonTest",
            "create_button": "CLI_CreateRebuildButton", 
            "test_click": "CLI_TestRebuildButtonClick",
            "debug_success_pop": "CLI_DebugFindSuccessPop",
            "check_events": "CLI_CheckRebuildButtonEvents"
        }
        
        if action not in action_map:
            print(f"❌ 알 수 없는 액션: {action}")
            print(f"💡 사용 가능한 액션: {', '.join(action_map.keys())}")
            return False
        
        method_name = action_map[action]
        print(f"🎯 액션 실행: {action} -> {method_name}")
        
        success, log_content = self.run_unity_method(method_name)
        
        # 로그 출력
        print("\n" + "="*50)
        print("📋 Unity 실행 결과")
        print("="*50)
        print(log_content)
        print("="*50)
        
        # 로그 파일 저장
        if save_log:
            self.save_log(log_content, action)
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description="Unity Rebuild Button CLI Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python unity_cli_runner.py --action all_test
  python unity_cli_runner.py --action create_button --project-path "C:/MyProject"
  python unity_cli_runner.py --action test_click --unity-path "C:/Unity/Editor/Unity.exe"
        """
    )
    
    parser.add_argument(
        "--action", "-a",
        required=True,
        choices=["all_test", "create_button", "test_click", "debug_success_pop", "check_events"],
        help="실행할 액션 선택"
    )
    
    parser.add_argument(
        "--project-path", "-p",
        help="Unity 프로젝트 경로 (기본값: 현재 디렉토리)"
    )
    
    parser.add_argument(
        "--unity-path", "-u",
        help="Unity 실행 파일 경로 (기본값: 자동 감지)"
    )
    
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=60,
        help="타임아웃 시간 (초, 기본값: 60)"
    )
    
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="로그 파일 저장하지 않기"
    )
    
    args = parser.parse_args()
    
    print("🎮 Unity Rebuild Button CLI Runner")
    print("="*50)
    
    # Unity CLI Runner 초기화
    runner = UnityCliRunner(
        project_path=args.project_path,
        unity_path=args.unity_path
    )
    
    # 액션 실행
    success = runner.run_action(args.action, save_log=not args.no_log)
    
    # 최종 결과
    if success:
        print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 작업 실행 중 오류가 발생했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main() 
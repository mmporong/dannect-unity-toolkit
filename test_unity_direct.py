#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unity 직접 실행 테스트 스크립트
"""

import subprocess
import os
import sys

def test_unity_direct():
    """Unity를 직접 실행해서 오류를 확인합니다."""
    
    unity_path = r"D:\Unity\6000.0.30f1\Editor\Unity.exe"
    project_path = r"E:\5.1.1.7_HeatFlowInFluid"
    method_name = "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_TestCLIMode"
    
    print("=== Unity 직접 실행 테스트 ===")
    print(f"Unity 경로: {unity_path}")
    print(f"프로젝트 경로: {project_path}")
    print(f"메소드: {method_name}")
    print()
    
    cmd = [
        unity_path,
        "-batchmode",
        "-quit",
        "-projectPath", project_path,
        "-executeMethod", method_name,
        "-logFile", "-"  # 표준 출력으로 로그 출력
    ]
    
    print(f"실행 명령어: {' '.join(cmd)}")
    print()
    print("=== Unity 실행 중... ===")
    
    try:
        result = subprocess.run(
            cmd,
            timeout=60,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"반환 코드: {result.returncode}")
        print()
        
        if result.stdout:
            print("=== 표준 출력 ===")
            print(result.stdout)
            print()
        
        if result.stderr:
            print("=== 표준 에러 ===")
            print(result.stderr)
            print()
        
        # 성공/실패 판단
        if result.returncode == 0:
            print("✅ Unity 실행 성공!")
        else:
            print(f"❌ Unity 실행 실패 (코드: {result.returncode})")
            
            # 일반적인 오류 코드들
            error_codes = {
                1: "일반적인 실행 오류 (스크립트 컴파일 오류, 메소드 찾을 수 없음 등)",
                2: "라이선스 오류",
                3: "프로젝트 열기 실패",
                4: "잘못된 명령행 인수",
                125: "메소드 실행 실패"
            }
            
            if result.returncode in error_codes:
                print(f"가능한 원인: {error_codes[result.returncode]}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ 타임아웃 발생")
        return False
    except Exception as e:
        print(f"❌ 실행 중 예외 발생: {e}")
        return False

if __name__ == "__main__":
    test_unity_direct() 
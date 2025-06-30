#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Development Toolkit
범용 Unity 개발 자동화 도구

Author: Dannect
Version: 2.0.0 (Refactored)
License: MIT

이 파일은 기존 사용자와의 호환성을 위해 유지되며,
새로운 모듈형 구조(dannect_toolkit)를 래핑합니다.

기존 사용법 (호환성 유지):
    python dannect_unity_toolkit.py --project "경로" --action all_test

권장 사용법 (새로운 모듈 방식):
    python -m dannect_toolkit --project "경로" --action all_test

주요 변경사항:
- 모듈화: 기능별로 분리된 managers 시스템
- Unity 패키지 완전 연동
- 향상된 로깅 시스템  
- 더 나은 오류 처리
- 타입 힌트 완전 지원
"""

import sys
import os

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

try:
    # 새로운 모듈 구조 사용
    from dannect_toolkit.cli.main import main
    
    if __name__ == "__main__":
        print("🔄 Dannect Unity Toolkit v2.0.0 (리팩토링 버전)")
        print("💡 권장: python -m dannect_toolkit 명령어 사용")
        print("📄 레거시 버전: dannect_unity_toolkit_legacy.py 참조")
        print("-" * 60)
        
        # 새로운 모듈의 메인 함수 실행
        sys.exit(main())
        
except ImportError as e:
    print(f"❌ 새로운 모듈을 불러올 수 없습니다: {e}")
    print("📄 레거시 버전 사용: python dannect_unity_toolkit_legacy.py")
    sys.exit(1) 
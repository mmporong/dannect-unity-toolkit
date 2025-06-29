# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-29

### Added
- 🎯 **Dannect Unity Toolkit** - 완전히 새로운 패키지 구조로 재설계
- **DannectLogger**: 색상 코딩과 다양한 로그 레벨을 지원하는 강력한 로깅 시스템
- **ButtonUtility**: 버튼 복사, 이벤트 연결, 이미지 변경 등의 종합 버튼 관리 도구
- **SceneUtility**: GameObject 검색, Scene 분석, 계층구조 시각화 기능
- **DannectToolkitConfig**: ScriptableObject 기반 설정 시스템
- **Unity Editor 메뉴 통합**: 15개 카테고리별 메뉴 항목 제공
- **Assembly Definition 파일**: 모듈화된 패키지 구조
- **Python CLI 연동**: Unity Editor 원격 제어 및 자동화

### Changed
- **네임스페이스**: `SimGround.Unity.Toolkit` → `Dannect.Unity.Toolkit`으로 변경
- **패키지 이름**: `com.simground.unity.toolkit` → `com.dannect.unity.toolkit`으로 변경
- **구조 개선**: Runtime/Editor 폴더 분리로 모듈화
- **설정 시스템**: 보다 직관적인 Inspector 기반 설정 관리

### Fixed
- **오브젝트 검색**: 비활성화된 오브젝트도 포함하는 강력한 검색 알고리즘
- **버튼 이벤트**: Persistent Listener와 Runtime Listener 이중 연결로 안정성 향상
- **에러 처리**: 포괄적인 try-catch와 상세한 오류 메시지 제공
- **Scene 저장**: 자동 변경사항 감지 및 저장 기능

### Documentation
- **README.md**: 종합적인 사용 가이드 및 API 문서
- **CHANGELOG.md**: 버전별 변경사항 상세 기록
- **LICENSE.md**: MIT 라이선스 적용
- **코드 주석**: 모든 public 메소드에 XML 문서 주석 추가

## [1.0.0] - 2024-06-29

### Added
- **초기 DannectToolkit 버전**
- 기본 버튼 복사 기능
- SystemManager 연동
- 간단한 Python CLI 스크립트
- Unity Editor 기본 메뉴 항목

### Features
- Success_Pop의 Next_Btn 복사하여 Rebuild_Btn 생성
- "Hello World!" 로그 출력 기능
- 기본적인 CLI 자동화

---

## 버전 관리 규칙

### 버전 번호 체계 (Semantic Versioning)
- **MAJOR.MINOR.PATCH** (예: 2.1.0)
- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 하위 호환성을 유지하면서 기능 추가
- **PATCH**: 하위 호환성을 유지하는 버그 수정

### 변경사항 카테고리
- **Added**: 새로운 기능
- **Changed**: 기존 기능의 변경
- **Deprecated**: 곧 제거될 기능
- **Removed**: 제거된 기능
- **Fixed**: 버그 수정
- **Security**: 보안 관련 수정

### 아이콘 가이드
- 🎯 새로운 주요 기능
- 🚀 성능 개선
- 🐛 버그 수정
- 📋 문서 개선
- ⚙️ 설정 변경
- 🔧 개발 도구
- 📂 파일 구조 변경
- 🌐 다국어 지원

---

## 로드맵

### 🚀 계획된 기능 (v2.1.0)
- **Samples 패키지**: 실제 사용 예제 및 튜토리얼
- **다국어 지원**: 영어/한국어 UI 지원
- **성능 모니터링**: WebGL 메모리 사용량 실시간 추적
- **템플릿 시스템**: 프로젝트 템플릿 자동 생성

### 🎯 장기 계획 (v3.0.0)
- **Visual Scripting 연동**: Unity Visual Scripting 노드 제공
- **CI/CD 통합**: GitHub Actions 자동 빌드 지원
- **Asset Store 배포**: Unity Asset Store 패키지 버전
- **플러그인 시스템**: 서드파티 확장 지원

---

## 기여자

### v2.0.0 개발팀
- **Lead Developer**: Dannect Team
- **QA Testing**: Dannect Community
- **Documentation**: Technical Writing Team

### 특별 감사
- Unity Technologies - Unity Engine 제공
- 모든 피드백을 제공해주신 개발자 커뮤니티
- Beta 테스터분들의 소중한 의견

---

**릴리스 정보**: [GitHub Releases](https://github.com/Dannect/unity-toolkit/releases)
**이슈 리포트**: [GitHub Issues](https://github.com/Dannect/unity-toolkit/issues) 
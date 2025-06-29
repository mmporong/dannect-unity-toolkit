# 📦 Dannect Rebuild Toolkit 설치 가이드

이 가이드는 Dannect Rebuild Toolkit을 Unity 프로젝트에 설치하고 설정하는 방법을 자세히 설명합니다.

## 🚀 설치 방법

### 방법 1: Unity Package Manager (권장)

#### 1-1. Local Package 설치
```bash
1. Unity Editor 열기
2. Window > Package Manager 선택
3. 좌상단 '+' 버튼 클릭
4. "Add package from disk..." 선택
5. DannectUnityToolkit/package.json 파일 선택
6. "Open" 클릭하여 설치 완료
```

#### 1-2. Git URL을 통한 설치 (추후 지원 예정)
```bash
1. Unity Editor에서 Window > Package Manager 열기
2. '+' 버튼 클릭 > "Add package from git URL..." 선택
3. 다음 URL 입력: https://github.com/dannect/unity-rebuild-toolkit.git
4. "Add" 버튼 클릭
```

### 방법 2: 수동 설치

#### 2-1. Packages 폴더에 복사
```bash
1. Unity 프로젝트 루트 폴더 열기
2. Packages 폴더 찾기 (없으면 생성)
3. DannectUnityToolkit 폴더를 Packages 폴더에 복사
4. Unity Editor에서 자동으로 패키지 인식
```

#### 2-2. Assets 폴더에 설치 (비권장)
```bash
1. DannectUnityToolkit/Runtime 폴더 내용을 Assets/Scripts/DannectToolkit/로 복사
2. DannectUnityToolkit/Editor 폴더 내용을 Assets/Editor/DannectToolkit/로 복사
3. Unity Editor에서 컴파일 대기
```

## ⚙️ 설치 후 설정

### 1. 메뉴 확인
설치가 완료되면 다음 메뉴가 나타납니다:
```
Tools/Dannect Rebuild Toolkit/
├── 🚀 All-in-One Rebuild Button Test
├── Create Rebuild Button
├── Test Rebuild Button Click
└── Debug/
```

### 2. Scene 설정

#### 2-1. RebuildButtonManager 추가
```csharp
// 방법 1: 기존 SystemManager에 추가 (권장)
GameObject systemManagerObj = GameObject.Find("SystemManager");
if (systemManagerObj != null)
{
    systemManagerObj.AddComponent<RebuildButtonManager>();
}

// 방법 2: 새로운 GameObject 생성
GameObject rebuildManagerObj = new GameObject("RebuildButtonManager");
rebuildManagerObj.AddComponent<RebuildButtonManager>();
```

#### 2-2. Success_Pop 확인
```csharp
// Success_Pop이 Scene에 존재하는지 확인
GameObject successPop = GameObject.Find("Success_Pop");
if (successPop == null)
{
    Debug.LogWarning("Success_Pop을 찾을 수 없습니다. Rebuild 버튼 생성이 제한될 수 있습니다.");
}
```

### 3. 설정 파일 생성 (선택사항)

#### 3-1. DannectToolkitConfig 생성
```bash
1. Assets/Resources 폴더 생성 (없는 경우)
2. Resources 폴더에서 우클릭
3. Create > Dannect > Toolkit Config 선택
4. 파일명을 "DannectToolkitConfig"로 설정
```

#### 3-2. 설정 값 조정
```csharp
// Inspector에서 다음 값들을 조정
- Project Name: "Your Project Name"
- Version: "1.0.0"
- Button Settings:
  - Source Button Name: "Next_Btn"
  - New Button Name: "Rebuild_Btn"
  - Button Text: "다시하기"
  - Position Offset: (-140, 0)
```

## 🧪 설치 확인 테스트

### 테스트 1: 메뉴 접근성
```bash
1. Tools > Dannect Rebuild Toolkit > 🚀 All-in-One Rebuild Button Test 실행
2. Console에서 로그 메시지 확인
3. "Hello World!" 메시지가 출력되면 설치 성공
```

### 테스트 2: CLI 도구
```bash
1. 프로젝트 루트에서 터미널 열기
2. cd DannectUnityToolkit/CLI
3. python unity_cli_runner.py --action all_test
4. 정상 실행되면 CLI 설정 완료
```

### 테스트 3: Rebuild 버튼 생성
```bash
1. Scene에 Success_Pop 활성화
2. Tools > Dannect Rebuild Toolkit > Create Rebuild Button
3. Success_Pop 하위에 Rebuild_Btn이 생성되면 성공
```

## 🔧 의존성 요구사항

### Unity 버전
- **최소 요구사항**: Unity 2022.3 LTS
- **권장 버전**: Unity 2022.3.12f1 이상
- **테스트된 버전**: Unity 2022.3 LTS, Unity 2023.2

### .NET 프레임워크
- **.NET Standard 2.1** 지원
- **C# 9.0** 이상 권장

### Unity Packages
자동으로 설치되는 필수 패키지:
```json
{
  "com.unity.ugui": "1.0.0",
  "com.unity.textmeshpro": "3.0.6" // 선택사항
}
```

### Python (CLI 사용 시)
- **Python 버전**: 3.6 이상
- **필수 모듈**: subprocess, argparse, json, datetime

## 🚨 문제 해결

### 설치 관련 문제

#### 문제 1: Package Manager에서 패키지가 인식되지 않음
```bash
해결책:
1. package.json 파일 경로 확인
2. Unity Editor 재시작
3. Packages/manifest.json에서 패키지 직접 추가:
   "com.dannect.rebuild-toolkit": "file:../DannectUnityToolkit"
```

#### 문제 2: 컴파일 에러 발생
```bash
해결책:
1. Unity 버전 확인 (2022.3 LTS 이상)
2. .NET Standard 2.1 설정 확인
3. 기존 DannectToolkit 관련 스크립트 삭제 후 재설치
```

#### 문제 3: 메뉴가 나타나지 않음
```bash
해결책:
1. Editor 폴더 구조 확인
2. Assembly Definition 파일 확인
3. Unity Editor 재시작
4. Assets > Reimport All 실행
```

### Runtime 관련 문제

#### 문제 4: RebuildButtonManager 인스턴스를 찾을 수 없음
```csharp
해결책:
// Scene에 수동으로 추가
GameObject managerObj = new GameObject("RebuildButtonManager");
RebuildButtonManager manager = managerObj.AddComponent<RebuildButtonManager>();
manager.Initialize();
```

#### 문제 5: Success_Pop을 찾을 수 없음
```csharp
해결책:
// 비활성화된 오브젝트도 검색
GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
foreach (GameObject obj in allObjects)
{
    if (obj.scene.IsValid() && obj.name == "Success_Pop")
    {
        // 찾음
        return obj;
    }
}
```

### CLI 관련 문제

#### 문제 6: Python CLI 실행 실패
```bash
해결책:
1. Python 설치 확인: python --version
2. Unity 경로 설정: 환경변수 또는 스크립트 수정
3. 권한 설정: 관리자 권한으로 실행
```

## 📞 추가 지원

설치 중 문제가 발생하면:

1. **GitHub Issues**: [Issues Page](https://github.com/dannect/unity-rebuild-toolkit/issues)
2. **Documentation**: [문서 폴더](Documentation/)
3. **Samples**: [샘플 코드](Samples~/)

## ✅ 설치 완료 체크리스트

- [ ] Unity Package Manager에 패키지 표시됨
- [ ] Tools 메뉴에 Dannect Rebuild Toolkit 항목 존재
- [ ] All-in-One Test 정상 실행
- [ ] Console에 "Hello World!" 메시지 출력
- [ ] CLI 도구 정상 작동 (선택사항)
- [ ] Rebuild 버튼 생성 성공
- [ ] 버튼 클릭 이벤트 정상 작동

모든 항목이 체크되면 설치가 완료된 것입니다! 🎉

---

**설치가 완료되었습니다! 이제 [README.md](../README.md)를 참조하여 사용법을 익혀보세요.** 
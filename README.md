# 🔧 Dannect Rebuild Toolkit

**Unity WebGL 과학실험 시뮬레이션용 Rebuild 버튼 자동화 툴킷**

Unity WebGL 환경에서 Success_Pop의 Next_Btn을 복사하여 Rebuild_Btn을 자동 생성하고 "Hello World!" 로그를 출력하는 완전한 시스템입니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **자동 Rebuild 버튼 생성**: Success_Pop의 Next_Btn을 복사하여 Rebuild_Btn 생성
- **Hello World! 로그 출력**: 버튼 클릭 시 콘솔에 로그 메시지 출력
- **SOLID 원칙 적용**: Single Responsibility Principle 기반 코드 구조
- **SystemManager 분리**: 실험 관리와 툴킷 기능의 완전한 분리
- **Unity Editor 통합**: 메뉴 항목을 통한 쉬운 접근
- **CLI 자동화**: Python 스크립트를 통한 원격 실행

### 🛠️ 기술적 특징
- **Unity 2022.3 LTS** 지원
- **WebGL 최적화**: 초저사양 환경 지원
- **비활성화 오브젝트 처리**: Resources.FindObjectsOfTypeAll 활용
- **안전한 이벤트 연결**: UnityEditor.Events API 사용
- **메모리 효율성**: Object Pooling 및 리소스 관리

## 🚀 설치 방법

### Unity Package Manager를 통한 설치
1. Unity Editor를 열고 `Window` > `Package Manager`를 선택
2. `+` 버튼 클릭 > `Add package from disk...` 선택
3. `DannectUnityToolkit/package.json` 파일 선택
4. 설치 완료 후 `Tools` > `Dannect Rebuild Toolkit` 메뉴 확인

### 수동 설치
1. `DannectUnityToolkit` 폴더를 Unity 프로젝트의 `Packages` 폴더에 복사
2. Unity Editor에서 자동으로 패키지를 인식하고 로드

## 📋 사용 방법

### 1. Unity Editor에서 사용

#### 🎯 메뉴 항목
```
Tools/Dannect Rebuild Toolkit/
├── 🚀 All-in-One Rebuild Button Test  (전체 테스트 실행)
├── Create Rebuild Button              (Rebuild 버튼 생성)
├── Test Rebuild Button Click          (버튼 클릭 테스트)
└── Debug/
    ├── Find Success_Pop               (Success_Pop 디버그)
    └── Check Rebuild Button Events    (이벤트 연결 상태 확인)
```

#### 🔧 기본 사용법
1. **RebuildButtonManager 설정**:
   ```csharp
   // Scene에 RebuildButtonManager 컴포넌트 추가
   // 또는 SystemManager와 같은 GameObject에 자동 추가
   ```

2. **Rebuild 버튼 생성**:
   ```
   Tools > Dannect Rebuild Toolkit > Create Rebuild Button
   ```

3. **테스트 실행**:
   ```
   Tools > Dannect Rebuild Toolkit > 🚀 All-in-One Rebuild Button Test
   ```

### 2. CLI를 통한 사용

#### 🐍 Python CLI 실행
```bash
# 전체 테스트 실행
python CLI/unity_cli_runner.py --action all_test

# Rebuild 버튼 생성
python CLI/unity_cli_runner.py --action create_button

# 버튼 클릭 테스트
python CLI/unity_cli_runner.py --action test_click
```

#### 🪟 Windows 배치 파일
```batch
# 대화형 메뉴 실행
CLI/run_unity_tests.bat
```

### 3. 코드에서 직접 사용

#### 🔧 RebuildButtonManager 사용
```csharp
// RebuildButtonManager 인스턴스 가져오기
RebuildButtonManager rebuildManager = RebuildButtonManager.Instance;

// Rebuild 버튼 생성
GameObject rebuildButton = rebuildManager.CreateRebuildButton();

// 버튼 클릭 이벤트 실행
rebuildManager.OnRebuildButtonClicked();
```

#### 🎯 SystemManager 연동
```csharp
public class YourExperimentManager : MonoBehaviour
{
    [SerializeField] private RebuildButtonManager m_rebuildButtonManager;
    
    private void Start()
    {
        // RebuildButtonManager 초기화
        if (m_rebuildButtonManager != null)
        {
            m_rebuildButtonManager.Initialize();
        }
    }
}
```

## 🏗️ 아키텍처

### 📦 패키지 구조
```
DannectUnityToolkit/
├── package.json                    # Unity Package 매니페스트
├── README.md                       # 메인 문서
├── CHANGELOG.md                    # 변경 사항 기록
├── LICENSE.md                      # 라이선스
├── Runtime/                        # Runtime 스크립트
│   └── Scripts/
│       └── Core/
│           ├── RebuildButtonManager.cs
│           ├── DannectLogger.cs
│           └── ...
├── Editor/                         # Editor 스크립트
│   └── Scripts/
│       ├── Core/
│       │   └── DannectToolkitEditorCore.cs
│       └── MenuItems/
│           └── CreateRebuildButtonEditor.cs
├── CLI/                           # CLI 자동화 도구
│   ├── unity_cli_runner.py
│   ├── run_unity_tests.bat
│   └── dannect_unity_toolkit.py
├── Documentation/                  # 추가 문서
│   └── ...
└── Samples~/                      # 샘플 코드
    └── RebuildButtonSample/
        └── ...
```

### 🔧 클래스 다이어그램
```
RebuildButtonManager
├── Initialize()
├── CreateRebuildButton()
├── OnRebuildButtonClicked()
├── RemoveRebuildButton()
└── FindSuccessPop()

SystemManager (선택적 연동)
├── ResetExperimentState()
├── StartExperiment()
└── StopExperiment()
```

## ⚙️ 설정

### 🔧 RebuildButtonManager 설정
```csharp
[Header("🔧 Dannect Toolkit 연동")]
[SerializeField] private DannectToolkitConfig m_toolkitConfig;
[SerializeField] private bool m_enableToolkitIntegration = true;

[Header("🎯 Rebuild 설정")]
[SerializeField] private bool m_enableDebugMode = true;
[SerializeField] private bool m_autoInitialize = true;

[Header("🔗 시스템 연동 (선택사항)")]
[SerializeField] private SystemManager m_systemManager;
[SerializeField] private bool m_resetExperimentOnRebuild = true;
```

### 📁 Resources 설정
```
Assets/Resources/
└── DannectToolkitConfig.asset    # 툴킷 설정 파일
```

## 🔍 디버깅

### 🐛 일반적인 문제 해결

#### 1. Success_Pop을 찾을 수 없음
```csharp
// 해결책: 비활성화된 오브젝트도 검색
GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
```

#### 2. 버튼 이벤트가 연결되지 않음
```csharp
// 해결책: 기존 Button 컴포넌트 제거 후 재생성
DestroyImmediate(oldButton);
Button newButton = gameObject.AddComponent<Button>();
```

#### 3. CLI 실행 실패
```bash
# Unity 경로 확인
unity_cli_runner.py --debug

# Python 버전 확인 (3.6 이상 필요)
python --version
```

### 🔧 Context Menu 디버깅
```csharp
// RebuildButtonManager 컴포넌트 우클릭 메뉴
[ContextMenu("설정 검증")]        // 설정 상태 확인
[ContextMenu("강제 초기화")]       // 강제 재초기화
[ContextMenu("매니저 정보 출력")]   // 상세 정보 출력
[ContextMenu("Rebuild 테스트")]    // 기능 테스트
```

## 📝 API 문서

### RebuildButtonManager
```csharp
public class RebuildButtonManager : MonoBehaviour
{
    // 프로퍼티
    public static RebuildButtonManager Instance { get; }
    public bool IsInitialized { get; }
    public bool IsRebuildInProgress { get; }
    public GameObject CurrentRebuildButton { get; }
    
    // 메소드
    public void Initialize();
    public void OnRebuildButtonClicked();
    public GameObject CreateRebuildButton();
    public void RemoveRebuildButton();
    public void LogRebuildManagerInfo();
    public GameObject FindSuccessPop();
}
```

## 🤝 기여하기

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE.md](LICENSE.md) 파일을 참조하세요.

## 💬 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/dannect/unity-rebuild-toolkit/issues)
- **문서**: [Documentation](Documentation/)
- **샘플**: [Samples~](Samples~/)

## 📈 로드맵

### v1.1.0 (예정)
- [ ] 다중 버튼 생성 지원
- [ ] 커스텀 이미지 설정
- [ ] 버튼 위치 자동 조정

### v1.2.0 (예정)  
- [ ] 실시간 실험 상태 모니터링
- [ ] 웹 인터페이스 제공
- [ ] 클라우드 로깅 지원

---

**Made with ❤️ by Dannect** 
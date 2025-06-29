# 🔧 Dannect Unity Development Toolkit

**범용 Unity 개발 자동화 도구 패키지**

## 📋 개요

Dannect Unity Toolkit은 Unity 프로젝트 개발을 자동화하고 효율성을 높이기 위한 종합적인 도구 패키지입니다. 버튼 복사, 이벤트 연결, Scene 관리, CLI 자동화 등의 기능을 제공합니다.

## ✨ 주요 기능

### 🎯 Button Utilities
- **버튼 복사 및 생성**: 기존 버튼을 복사하여 새로운 버튼 생성
- **이벤트 자동 연결**: 설정 기반 자동 메소드 연결
- **이미지 및 텍스트 변경**: 버튼 외관 자동 커스터마이징
- **비활성화 오브젝트 검색**: setActive(false) 상태의 오브젝트도 찾기

### 📂 Scene Utilities
- **Scene 자동 로드**: CLI 모드에서 Scene 자동 감지 및 로드
- **계층구조 분석**: Scene의 GameObject 구조 분석 및 로깅
- **오브젝트 검색**: 이름 및 컴포넌트 기반 고급 검색

### 🚀 CLI Automation
- **Python 통합**: Python 스크립트를 통한 Unity 원격 제어
- **병렬 처리**: 여러 프로젝트 동시 작업
- **배치 작업**: 대량 프로젝트 일괄 처리

### 🐛 Debug & Logging
- **색상 코딩 로그**: 가독성 높은 컬러 로그 시스템
- **조건부 로깅**: Editor/Development 빌드 전용 로그
- **파일 로깅**: 로그 파일 자동 저장 및 관리

## 🚀 빠른 시작

### 1. 패키지 설치

#### Unity Package Manager 사용
```
Window > Package Manager > + > Add package from git URL
https://github.com/dannect/unity-toolkit.git
```

#### Manual 설치
1. `Assets/DannectToolkit` 폴더를 Unity 프로젝트에 복사
2. Unity에서 프로젝트 새로고침

### 2. 설정 파일 생성

Unity 메뉴에서:
```
Tools > Dannect Toolkit > 📋 Settings > Open Config
```

### 3. 기본 사용법

#### Editor에서 버튼 생성
```
Tools > Dannect Toolkit > 🎯 Button Utilities > Create Rebuild Button
```

#### 코드에서 사용
```csharp
using Dannect.Unity.Toolkit;

public class MyScript : MonoBehaviour
{
    [SerializeField] private DannectToolkitConfig config;
    
    void Start()
    {
        // 자동 Rebuild 버튼 생성
        GameObject button = ButtonUtility.CreateRebuildButtonAuto(config);
        
        // 로깅
        DannectLogger.LogSuccess("버튼 생성 완료!");
    }
}
```

## 🔧 설정 가이드

### DannectToolkitConfig 설정

```csharp
[CreateAssetMenu(fileName = "DannectToolkitConfig", menuName = "Dannect/Toolkit Config")]
public class DannectToolkitConfig : ScriptableObject
{
    [Header("🔧 일반 설정")]
    public string projectName = "My Unity Project";
    public string version = "1.0.0";
    
    [Header("🎯 버튼 유틸리티 설정")]
    public ButtonSettings buttonSettings;
    
    [Header("🌐 WebGL 빌드 설정")]
    public WebGLSettings webglSettings;
}
```

### 버튼 설정 예제

```csharp
[System.Serializable]
public class ButtonSettings
{
    [Header("🔍 검색 설정")]
    public string sourceButtonName = "Next_Btn";
    public string newButtonName = "Rebuild_Btn";
    
    [Header("📍 위치 및 외관")]
    public Vector2 buttonOffset = new Vector2(-140, 0);
    public string buttonText = "재구성";
    public string buttonImagePath = "Assets/05.Textures, Images, Materials/GuideUI/버튼-다음.png";
    
    [Header("🔗 이벤트 연결")]
    public string targetClassName = "SystemManager";
    public string targetMethodName = "OnRebuildButtonClicked";
}
```

## 🐍 Python CLI 사용법

### 기본 사용법

```bash
# 단일 프로젝트에서 전체 테스트
python dannect_unity_toolkit.py --project "C:/MyUnityProject" --action all_test

# 여러 프로젝트에서 버튼 생성
python dannect_unity_toolkit.py --projects-dir "C:/UnityProjects" --action create_button

# 특정 Unity 경로 지정
python dannect_unity_toolkit.py --project "C:/MyProject" --action test_button --unity-path "C:/Unity/2022.3.0f1/Editor/Unity.exe"
```

### 사용 가능한 액션

| 액션 | 설명 |
|------|------|
| `all_test` | 전체 테스트 (버튼 생성 + 테스트 + 디버그) |
| `create_button` | Rebuild 버튼 생성 |
| `test_button` | 버튼 클릭 테스트 |
| `debug_popup` | 팝업 오브젝트 디버그 |
| `check_events` | 버튼 이벤트 확인 |
| `project_info` | 프로젝트 정보 출력 |

### 고급 옵션

```bash
# 로그 레벨 설정
python dannect_unity_toolkit.py --project "C:/MyProject" --action all_test --log-level DEBUG

# 타임아웃 설정 (초)
python dannect_unity_toolkit.py --project "C:/MyProject" --action create_button --timeout 600

# 여러 프로젝트 순차 처리
python dannect_unity_toolkit.py --projects-dir "C:/UnityProjects" --action all_test
```

## 🏗️ 아키텍처

### 핵심 컴포넌트

```
Dannect.Unity.Toolkit/
├── Runtime/
│   ├── Scripts/
│   │   ├── Core/
│   │   │   ├── DannectToolkitConfig.cs
│   │   │   └── DannectLogger.cs
│   │   └── Utilities/
│   │       ├── ButtonUtility.cs
│   │       └── SceneUtility.cs
│   └── Resources/
│       └── DannectToolkitConfig.asset
├── Editor/
│   ├── Scripts/
│   │   ├── Core/
│   │   │   └── DannectToolkitEditorCore.cs
│   │   └── MenuItems/
│   │       └── DannectToolkitMenuItems.cs
└── Python/
    └── dannect_unity_toolkit.py
```

### 설계 원칙

- **모듈화**: 각 기능을 독립적인 유틸리티 클래스로 분리
- **설정 기반**: ScriptableObject를 통한 유연한 설정 관리
- **로깅 시스템**: 개발 및 디버깅을 위한 포괄적인 로깅
- **CLI 통합**: Python을 통한 외부 자동화 지원

## 🔄 통합 가이드

### 기존 SystemManager와 연동

```csharp
using Dannect.Unity.Toolkit;

public class SystemManager : MonoBehaviour
{
    [Header("🔧 Dannect Toolkit 연동")]
    [SerializeField] private DannectToolkitConfig toolkitConfig;
    [SerializeField] private bool enableToolkitIntegration = true;
    
    public void OnRebuildButtonClicked()
    {
        DannectLogger.LogStart("Rebuild 버튼 클릭됨!");
        
        if (enableToolkitIntegration && toolkitConfig != null)
        {
            // Toolkit을 통한 재구성
            StartCoroutine(RebuildExperimentWithToolkit());
        }
        else
        {
            // 기존 방식으로 재구성
            RebuildExperiment();
        }
    }
    
    public GameObject CreateRebuildButton()
    {
        return ButtonUtility.CreateRebuildButtonAuto(toolkitConfig);
    }
}
```

### Assembly Definition 설정

기존 Scripts 폴더에 `Scripts.asmdef` 추가:

```json
{
    "name": "Scripts",
    "references": [
        "Dannect.Unity.Toolkit"
    ],
    "autoReferenced": true
}
```

## 🐛 문제 해결

### 자주 발생하는 문제

#### 1. "Unity Editor를 찾을 수 없습니다"
```bash
# Unity 경로 직접 지정
python dannect_unity_toolkit.py --unity-path "C:/Program Files/Unity/Hub/Editor/2022.3.0f1/Editor/Unity.exe"
```

#### 2. "Success_Pop을 찾을 수 없습니다"
- `DannectToolkitConfig`에서 `popupObjectNames` 설정 확인
- Scene에서 해당 오브젝트가 존재하는지 확인

#### 3. "Assembly 참조 오류"
- Unity를 재시작하여 Assembly Definition 새로고침
- `Window > Package Manager`에서 패키지 재설치

### 로그 분석

```csharp
// 로그 레벨 설정
DannectLogger.UpdateSettings(
    enableVerbose: true,
    enableEditorOnly: true,
    enableFileLogging: true
);

// 시스템 정보 출력
SystemManager.Instance.LogSystemInfo();
```

## 📚 API 참조

### ButtonUtility

| 메소드 | 설명 |
|--------|------|
| `CopyButton()` | 버튼 복사 |
| `ConnectButtonMethod()` | 메소드 연결 |
| `ChangeButtonText()` | 텍스트 변경 |
| `ChangeButtonImage()` | 이미지 변경 |
| `CreateRebuildButtonAuto()` | 완전 자동 생성 |

### SceneUtility

| 메소드 | 설명 |
|--------|------|
| `FindGameObjectByName()` | 이름으로 오브젝트 찾기 |
| `FindComponentInScene()` | 컴포넌트 검색 |
| `LogSceneHierarchy()` | 계층구조 로깅 |
| `GetHierarchyPath()` | 계층 경로 반환 |

### DannectLogger

| 메소드 | 설명 |
|--------|------|
| `Log()` | 일반 로그 |
| `LogWarning()` | 경고 로그 |
| `LogError()` | 오류 로그 |
| `LogSuccess()` | 성공 로그 |
| `LogStart()` | 시작 로그 |
| `LogComplete()` | 완료 로그 |

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙋‍♂️ 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discussions**: 질문 및 커뮤니티 논의
- **Wiki**: 상세한 가이드 및 예제

---

**Dannect Unity Toolkit** - Unity 개발을 더 스마트하게! 🚀 
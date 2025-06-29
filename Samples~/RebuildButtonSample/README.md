# 🔧 Rebuild Button Sample

이 샘플은 Dannect Rebuild Toolkit을 사용하여 Rebuild 버튼을 생성하고 테스트하는 방법을 보여줍니다.

## 📋 포함된 내용

- **SampleScene.unity**: 테스트용 Scene
- **SampleSystemManager.cs**: 예제 SystemManager 스크립트
- **SampleRebuildTest.cs**: Rebuild 기능 테스트 스크립트

## 🚀 사용 방법

### 1. 샘플 임포트
1. Unity Package Manager에서 Dannect Rebuild Toolkit 선택
2. Samples 탭에서 "Rebuild Button Sample" 임포트

### 2. Scene 실행
1. SampleScene.unity 열기
2. Play Mode 진입
3. UI에서 Success_Pop 활성화
4. Tools 메뉴에서 Rebuild 버튼 생성 테스트

### 3. 코드 예제

```csharp
using UnityEngine;
using Dannect.Unity.Toolkit;

public class SampleRebuildTest : MonoBehaviour
{
    private RebuildButtonManager rebuildManager;
    
    void Start()
    {
        // RebuildButtonManager 인스턴스 가져오기
        rebuildManager = RebuildButtonManager.Instance;
        
        if (rebuildManager == null)
        {
            // 없으면 생성
            GameObject managerObj = new GameObject("RebuildButtonManager");
            rebuildManager = managerObj.AddComponent<RebuildButtonManager>();
        }
        
        // 초기화
        rebuildManager.Initialize();
        
        // 2초 후 Rebuild 버튼 자동 생성
        Invoke("CreateRebuildButton", 2f);
    }
    
    void CreateRebuildButton()
    {
        GameObject rebuildButton = rebuildManager.CreateRebuildButton();
        
        if (rebuildButton != null)
        {
            Debug.Log("✅ Rebuild 버튼이 성공적으로 생성되었습니다!");
        }
        else
        {
            Debug.LogError("❌ Rebuild 버튼 생성에 실패했습니다!");
        }
    }
    
    // 테스트용 메소드
    [ContextMenu("테스트 Rebuild 실행")]
    void TestRebuild()
    {
        if (rebuildManager != null)
        {
            rebuildManager.OnRebuildButtonClicked();
        }
    }
}
```

## 🎯 학습 목표

이 샘플을 통해 다음을 학습할 수 있습니다:

1. **RebuildButtonManager 사용법**
2. **Success_Pop 찾기 및 처리**
3. **버튼 생성 및 이벤트 연결**
4. **SystemManager와의 연동**
5. **CLI 도구 활용법**

## 🔧 커스터마이징

### 버튼 텍스트 변경
```csharp
// 생성된 버튼의 텍스트 변경
Text buttonText = rebuildButton.GetComponentInChildren<Text>();
if (buttonText != null)
{
    buttonText.text = "다시 시작";
}
```

### 버튼 위치 조정
```csharp
// 버튼 위치 조정
RectTransform rectTransform = rebuildButton.GetComponent<RectTransform>();
rectTransform.anchoredPosition = new Vector2(-200f, 0f);
```

### 커스텀 이벤트 연결
```csharp
// 커스텀 메소드 연결
Button button = rebuildButton.GetComponent<Button>();
button.onClick.AddListener(() => {
    Debug.Log("커스텀 Rebuild 실행!");
    // 여기에 커스텀 로직 추가
});
```

## 🚀 다음 단계

1. **CLI 도구 실행**: `CLI/run_unity_tests.bat` 실행
2. **커스텀 버튼 생성**: 다른 팝업에서 버튼 생성 시도
3. **SystemManager 연동**: 실제 실험과 연결
4. **WebGL 빌드**: 브라우저에서 테스트

## 💡 팁

- Inspector에서 RebuildButtonManager의 Context Menu 활용
- 디버그 모드를 활성화하여 상세한 로그 확인
- Scene 저장을 잊지 마세요!

---

**Happy Coding! 🎉** 
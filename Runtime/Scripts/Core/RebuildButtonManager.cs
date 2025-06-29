using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using Dannect;
using Dannect.Unity.Toolkit;
#if UNITY_EDITOR
using UnityEditor.Events;
#endif

/// <summary>
/// Rebuild 버튼 전용 관리자 - SOLID 원칙의 SRP(Single Responsibility Principle) 적용
/// SystemManager와 완전히 분리된 독립적인 툴킷 관리자
/// </summary>
public class RebuildButtonManager : MonoBehaviour
{
    #region Serialized Fields
    [Header("🔧 Dannect Toolkit 연동")]
    [SerializeField] private DannectToolkitConfig m_toolkitConfig;
    [SerializeField] private bool m_enableToolkitIntegration = true;
    
    [Header("🎯 Rebuild 설정")]
    [SerializeField] private bool m_enableDebugMode = true;
    [SerializeField] private bool m_autoInitialize = true;
    
    [Header("🔗 시스템 연동 (선택사항)")]
    [SerializeField] private SystemManager m_systemManager;
    [SerializeField] private bool m_resetExperimentOnRebuild = true;
    #endregion

    #region Private Fields
    private bool m_isInitialized = false;
    private static RebuildButtonManager s_instance;
    
    // Rebuild 버튼 관련 상태
    private GameObject m_currentRebuildButton;
    private bool m_isRebuildInProgress = false;
    #endregion

    #region Properties
    public static RebuildButtonManager Instance
    {
        get
        {
            if (s_instance == null)
            {
                s_instance = FindFirstObjectByType<RebuildButtonManager>();
                if (s_instance == null)
                {
                    DannectLogger.LogWarning("RebuildButtonManager 인스턴스를 찾을 수 없습니다.");
                }
            }
            return s_instance;
        }
    }

    public DannectToolkitConfig ToolkitConfig => m_toolkitConfig;
    public bool IsInitialized => m_isInitialized;
    public bool IsRebuildInProgress => m_isRebuildInProgress;
    public GameObject CurrentRebuildButton => m_currentRebuildButton;
    #endregion

    #region Unity Lifecycle
    private void Awake()
    {
        // 싱글톤 패턴 구현
        if (s_instance == null)
        {
            s_instance = this;
        }
        else if (s_instance != this)
        {
            DannectLogger.LogWarning("중복된 RebuildButtonManager가 발견되어 제거합니다.");
            Destroy(gameObject);
            return;
        }

        if (m_autoInitialize)
        {
            Initialize();
        }
    }

    private void Start()
    {
        if (m_isInitialized)
        {
            DannectLogger.LogSuccess("RebuildButtonManager 초기화 완료 - Rebuild 기능 준비됨");
        }
    }
    #endregion

    #region 초기화
    /// <summary>
    /// RebuildButtonManager 초기화
    /// </summary>
    public void Initialize()
    {
        if (m_isInitialized)
            return;

        DannectLogger.LogStart("RebuildButtonManager 초기화 시작...");

        try
        {
            // 1. Toolkit 설정 로드
            InitializeToolkitConfig();

            // 2. 시스템 매니저 참조 설정
            InitializeSystemManagerReference();

            // 3. 기존 Rebuild 버튼 찾기
            FindExistingRebuildButton();

            m_isInitialized = true;
            DannectLogger.LogComplete("RebuildButtonManager 초기화 완료");
        }
        catch (Exception e)
        {
            DannectLogger.LogException("RebuildButtonManager 초기화 실패", e);
        }
    }

    /// <summary>
    /// Toolkit 설정 초기화
    /// </summary>
    private void InitializeToolkitConfig()
    {
        if (!m_enableToolkitIntegration)
        {
            DannectLogger.Log("Toolkit 연동이 비활성화되어 있습니다.");
            return;
        }

        if (m_toolkitConfig == null)
        {
            // Resources 폴더에서 설정 파일 찾기
            m_toolkitConfig = Resources.Load<DannectToolkitConfig>("DannectToolkitConfig");
            
            if (m_toolkitConfig == null)
            {
                DannectLogger.LogWarning("DannectToolkitConfig를 찾을 수 없습니다. 기본 설정을 사용합니다.");
            }
            else
            {
                DannectLogger.Log("Toolkit 설정 파일을 로드했습니다.");
            }
        }

        // 로거 설정 업데이트
        if (m_toolkitConfig != null)
        {
            DannectLogger.UpdateSettingsFromConfig(m_toolkitConfig);
        }
    }

    /// <summary>
    /// SystemManager 참조 설정
    /// </summary>
    private void InitializeSystemManagerReference()
    {
        if (m_systemManager == null)
        {
            m_systemManager = SystemManager.Instance;
            if (m_systemManager != null)
            {
                DannectLogger.Log("SystemManager 참조를 자동으로 설정했습니다.");
            }
            else
            {
                DannectLogger.LogWarning("SystemManager를 찾을 수 없습니다. Rebuild 시 실험 상태 초기화가 비활성화됩니다.");
            }
        }
    }

    /// <summary>
    /// 기존 Rebuild 버튼 찾기
    /// </summary>
    private void FindExistingRebuildButton()
    {
        if (m_toolkitConfig != null)
        {
            m_currentRebuildButton = ButtonUtility.FindButton(m_toolkitConfig.ButtonSettings.newButtonName);
            if (m_currentRebuildButton != null)
            {
                DannectLogger.Log($"기존 Rebuild 버튼을 찾았습니다: {m_currentRebuildButton.name}");
            }
        }
    }
    #endregion

    #region Rebuild 버튼 관련 기능
    /// <summary>
    /// Rebuild 버튼 클릭 이벤트 - "Hello World!" 출력 및 실험 재구성
    /// </summary>
    public void OnRebuildButtonClicked()
    {
        DannectLogger.LogStart("🔧 Rebuild 버튼 클릭됨 - Hello World!");
        
        if (m_isRebuildInProgress)
        {
            DannectLogger.LogWarning("Rebuild가 이미 진행 중입니다.");
            return;
        }

        try
        {
            if (m_enableToolkitIntegration && m_toolkitConfig != null)
            {
                // Toolkit을 통한 재구성
                StartCoroutine(RebuildExperimentWithToolkit());
            }
            else
            {
                // 기본 방식으로 재구성
                RebuildExperiment();
            }
        }
        catch (Exception e)
        {
            DannectLogger.LogException("Rebuild 버튼 처리 중 오류", e);
        }
    }

    /// <summary>
    /// Toolkit을 사용한 실험 재구성 (코루틴)
    /// </summary>
    private IEnumerator RebuildExperimentWithToolkit()
    {
        m_isRebuildInProgress = true;
        DannectLogger.LogProgress("Toolkit을 사용하여 실험 재구성 중...");
        
        try
        {
            // 1. 실험 상태 초기화
            if (m_resetExperimentOnRebuild && m_systemManager != null)
            {
                m_systemManager.ResetExperimentState();
                yield return new WaitForSeconds(0.1f);
            }

            // 2. Toolkit 설정 기반 재구성
            if (m_toolkitConfig != null)
            {
                DannectLogger.Log($"프로젝트: {m_toolkitConfig.ProjectName}");
                DannectLogger.Log($"버전: {m_toolkitConfig.Version}");
                yield return new WaitForSeconds(0.1f);
            }

            // 3. 추가 재구성 로직 (필요시)
            yield return PerformAdditionalRebuildTasks();

            // 4. 완료 처리
            DannectLogger.LogComplete("Toolkit 기반 실험 재구성 완료");
        }
        finally
        {
            m_isRebuildInProgress = false;
        }
    }

    /// <summary>
    /// 기본 방식의 실험 재구성
    /// </summary>
    private void RebuildExperiment()
    {
        m_isRebuildInProgress = true;
        DannectLogger.LogProgress("기본 방식으로 실험 재구성 중...");
        
        try
        {
            // 1. 실험 상태 초기화
            if (m_resetExperimentOnRebuild && m_systemManager != null)
            {
                m_systemManager.ResetExperimentState();
            }

            // 2. 기본 재구성 로직
            PerformBasicRebuildTasks();

            DannectLogger.LogComplete("기본 방식 실험 재구성 완료");
        }
        finally
        {
            m_isRebuildInProgress = false;
        }
    }

    /// <summary>
    /// 추가 재구성 작업 (코루틴)
    /// </summary>
    private IEnumerator PerformAdditionalRebuildTasks()
    {
        // 여기에 필요한 추가 재구성 로직 구현
        // 예: 오브젝트 위치 초기화, UI 상태 리셋 등
        
        DannectLogger.Log("추가 재구성 작업 수행 중...");
        yield return new WaitForSeconds(0.1f);
        DannectLogger.Log("추가 재구성 작업 완료");
    }

    /// <summary>
    /// 기본 재구성 작업
    /// </summary>
    private void PerformBasicRebuildTasks()
    {
        // 여기에 기본 재구성 로직 구현
        DannectLogger.Log("기본 재구성 작업 수행 중...");
        // 실제 재구성 로직은 프로젝트 요구사항에 따라 구현
        DannectLogger.Log("기본 재구성 작업 완료");
    }

    /// <summary>
    /// 자동 Rebuild 버튼 생성 (Editor 및 CLI에서 호출)
    /// </summary>
    public GameObject CreateRebuildButton()
    {
        if (!m_enableToolkitIntegration || m_toolkitConfig == null)
        {
            DannectLogger.LogError("Toolkit 연동이 비활성화되어 있거나 설정이 없습니다.");
            return null;
        }

        try
        {
            DannectLogger.LogStart("Rebuild 버튼 생성 시작...");
            
            // 기존 버튼 제거
            if (m_currentRebuildButton != null)
            {
                DannectLogger.Log("기존 Rebuild 버튼을 제거합니다.");
#if UNITY_EDITOR
                DestroyImmediate(m_currentRebuildButton);
#else
                Destroy(m_currentRebuildButton);
#endif
                m_currentRebuildButton = null;
            }

            // 새 버튼 생성
            m_currentRebuildButton = ButtonUtility.CreateRebuildButtonAuto(m_toolkitConfig);
            
            if (m_currentRebuildButton != null)
            {
                DannectLogger.LogComplete($"Rebuild 버튼 생성 완료: {m_currentRebuildButton.name}");
            }
            else
            {
                DannectLogger.LogError("Rebuild 버튼 생성 실패");
            }

            return m_currentRebuildButton;
        }
        catch (Exception e)
        {
            DannectLogger.LogException("Rebuild 버튼 생성 실패", e);
            return null;
        }
    }

    /// <summary>
    /// Rebuild 버튼 제거
    /// </summary>
    public void RemoveRebuildButton()
    {
        if (m_currentRebuildButton != null)
        {
            DannectLogger.Log($"Rebuild 버튼을 제거합니다: {m_currentRebuildButton.name}");
#if UNITY_EDITOR
            DestroyImmediate(m_currentRebuildButton);
#else
            Destroy(m_currentRebuildButton);
#endif
            m_currentRebuildButton = null;
        }
        else
        {
            DannectLogger.LogWarning("제거할 Rebuild 버튼이 없습니다.");
        }
    }
    #endregion

    #region 유틸리티 메소드
    /// <summary>
    /// Toolkit 설정을 Runtime에서 업데이트
    /// </summary>
    /// <param name="newConfig">새로운 설정</param>
    public void UpdateToolkitConfig(DannectToolkitConfig newConfig)
    {
        if (newConfig == null)
        {
            DannectLogger.LogError("새로운 설정이 null입니다.");
            return;
        }

        m_toolkitConfig = newConfig;
        DannectLogger.UpdateSettingsFromConfig(m_toolkitConfig);
        DannectLogger.LogSuccess("Toolkit 설정이 업데이트되었습니다.");
    }

    /// <summary>
    /// 디버그 정보 출력
    /// </summary>
    public void LogRebuildManagerInfo()
    {
        if (!m_enableDebugMode)
            return;

        DannectLogger.Log("=== RebuildButtonManager 정보 ===");
        DannectLogger.Log($"초기화됨: {m_isInitialized}");
        DannectLogger.Log($"Toolkit 연동: {m_enableToolkitIntegration}");
        DannectLogger.Log($"Toolkit 설정: {(m_toolkitConfig != null ? "로드됨" : "없음")}");
        DannectLogger.Log($"SystemManager 연결: {(m_systemManager != null ? "연결됨" : "없음")}");
        DannectLogger.Log($"현재 Rebuild 버튼: {(m_currentRebuildButton != null ? m_currentRebuildButton.name : "없음")}");
        DannectLogger.Log($"Rebuild 진행 중: {m_isRebuildInProgress}");
        
        if (m_toolkitConfig != null)
        {
            DannectLogger.Log($"프로젝트명: {m_toolkitConfig.ProjectName}");
            DannectLogger.Log($"버전: {m_toolkitConfig.Version}");
        }
        
        DannectLogger.Log("====================================");
    }

    /// <summary>
    /// Success_Pop 찾기 (디버그용)
    /// </summary>
    public GameObject FindSuccessPop()
    {
        if (m_toolkitConfig == null)
        {
            DannectLogger.LogError("Toolkit 설정이 없습니다.");
            return null;
        }

        var popupObjects = SceneUtility.FindPopupObjects(m_toolkitConfig);
        
        foreach (var popup in popupObjects)
        {
            if (popup.name.Contains("Success"))
            {
                DannectLogger.Log($"Success_Pop 발견: {popup.name}");
                return popup;
            }
        }

        DannectLogger.LogWarning("Success_Pop을 찾을 수 없습니다.");
        return null;
    }
    #endregion

    #region 이벤트 처리
    /// <summary>
    /// 애플리케이션 종료 시 정리 작업
    /// </summary>
    private void OnApplicationQuit()
    {
        DannectLogger.Log("RebuildButtonManager 정리 작업 수행 중...");
        
        // Rebuild 진행 중이면 중단
        if (m_isRebuildInProgress)
        {
            StopAllCoroutines();
            m_isRebuildInProgress = false;
        }
        
        DannectLogger.Log("RebuildButtonManager 정리 완료");
    }
    #endregion

    #region 에디터 전용 메소드
#if UNITY_EDITOR
    /// <summary>
    /// 에디터에서 설정 검증
    /// </summary>
    [ContextMenu("설정 검증")]
    private void ValidateSettings()
    {
        DannectLogger.LogStart("RebuildButtonManager 설정 검증 시작...");
        
        if (m_toolkitConfig == null)
        {
            DannectLogger.LogWarning("Toolkit 설정이 할당되지 않았습니다.");
        }
        else
        {
            DannectLogger.LogSuccess("Toolkit 설정이 올바르게 할당되었습니다.");
        }

        if (m_systemManager == null)
        {
            DannectLogger.LogWarning("SystemManager 참조가 없습니다.");
        }
        else
        {
            DannectLogger.LogSuccess("SystemManager가 연결되었습니다.");
        }

        DannectLogger.LogComplete("설정 검증 완료");
    }

    /// <summary>
    /// 에디터에서 강제 초기화
    /// </summary>
    [ContextMenu("강제 초기화")]
    private void ForceInitialize()
    {
        m_isInitialized = false;
        Initialize();
    }

    /// <summary>
    /// 에디터에서 매니저 정보 출력
    /// </summary>
    [ContextMenu("매니저 정보 출력")]
    private void EditorLogRebuildManagerInfo()
    {
        LogRebuildManagerInfo();
    }

    /// <summary>
    /// 에디터에서 Rebuild 테스트
    /// </summary>
    [ContextMenu("Rebuild 테스트")]
    private void EditorTestRebuild()
    {
        OnRebuildButtonClicked();
    }

    /// <summary>
    /// 에디터에서 Rebuild 버튼 생성 테스트
    /// </summary>
    [ContextMenu("Rebuild 버튼 생성")]
    private void EditorCreateRebuildButton()
    {
        CreateRebuildButton();
    }

    /// <summary>
    /// 에디터에서 Rebuild 버튼 제거 테스트
    /// </summary>
    [ContextMenu("Rebuild 버튼 제거")]
    private void EditorRemoveRebuildButton()
    {
        RemoveRebuildButton();
    }
#endif
    #endregion
} 
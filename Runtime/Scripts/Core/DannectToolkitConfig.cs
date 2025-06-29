using UnityEngine;
using System;
using System.Collections.Generic;

namespace Dannect.Unity.Toolkit
{
    [CreateAssetMenu(fileName = "DannectToolkitConfig", menuName = "Dannect/Toolkit Config")]
    public class DannectToolkitConfig : ScriptableObject
    {
        [Header("🔧 일반 설정")]
        [SerializeField] private string m_projectName = "Dannect Unity Project";
        [SerializeField] private string m_companyName = "Dannect";
        [SerializeField] private string m_version = "2.0.0";
        
        [Header("🎯 버튼 유틸리티 설정")]
        [SerializeField] private ButtonSettings m_buttonSettings = new ButtonSettings();
        
        [Header("🌐 WebGL 빌드 설정")]
        [SerializeField] private WebGLSettings m_webglSettings = new WebGLSettings();
        
        [Header("📂 씬 및 오브젝트 설정")]
        [SerializeField] private SceneSettings m_sceneSettings = new SceneSettings();
        
        [Header("🐛 디버그 설정")]
        [SerializeField] private DebugSettings m_debugSettings = new DebugSettings();

        #region 프로퍼티
        public string ProjectName => m_projectName;
        public string CompanyName => m_companyName;
        public string Version => m_version;
        public ButtonSettings ButtonSettings => m_buttonSettings;
        public WebGLSettings WebGLSettings => m_webglSettings;
        public SceneSettings SceneSettings => m_sceneSettings;
        public DebugSettings DebugSettings => m_debugSettings;
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// 기본 설정값으로 초기화
        /// </summary>
        [ContextMenu("기본값으로 초기화")]
        public void ResetToDefaults()
        {
            m_projectName = "Dannect Unity Project";
            m_companyName = "Dannect";
            m_version = "2.0.0";
            
            m_buttonSettings = new ButtonSettings();
            m_webglSettings = new WebGLSettings();
            m_sceneSettings = new SceneSettings();
            m_debugSettings = new DebugSettings();
            
            Debug.Log("DannectToolkitConfig가 기본값으로 초기화되었습니다.");
        }

        /// <summary>
        /// 설정 유효성 검증
        /// </summary>
        public bool ValidateSettings(out string errorMessage)
        {
            errorMessage = "";
            
            if (string.IsNullOrEmpty(m_projectName))
            {
                errorMessage = "프로젝트 이름이 설정되지 않았습니다.";
                return false;
            }
            
            if (m_webglSettings.initialMemorySize <= 0)
            {
                errorMessage = "WebGL 초기 메모리 크기가 올바르지 않습니다.";
                return false;
            }
            
            if (m_webglSettings.maximumMemorySize < m_webglSettings.initialMemorySize)
            {
                errorMessage = "WebGL 최대 메모리 크기가 초기 메모리 크기보다 작습니다.";
                return false;
            }
            
            return true;
        }

        /// <summary>
        /// 현재 설정을 JSON으로 내보내기
        /// </summary>
        public string ExportToJson()
        {
            return JsonUtility.ToJson(this, true);
        }

        /// <summary>
        /// JSON에서 설정 가져오기
        /// </summary>
        public void ImportFromJson(string json)
        {
            JsonUtility.FromJsonOverwrite(json, this);
        }
        #endregion

        #region Unity 이벤트
        private void OnValidate()
        {
            // Inspector에서 값이 변경될 때 자동 검증
            if (m_webglSettings.maximumMemorySize < m_webglSettings.initialMemorySize)
            {
                m_webglSettings.maximumMemorySize = m_webglSettings.initialMemorySize;
            }
        }
        #endregion
    }

    #region 설정 클래스들
    [System.Serializable]
    public class ButtonSettings
    {
        [Header("기본 버튼 설정")]
        public string sourceButtonName = "Next_Btn";
        public string newButtonName = "Rebuild_Btn";
        public string buttonText = "다시하기";
        public Vector2 buttonOffset = new Vector2(-140f, 0f);
        
        [Header("이미지 설정")]
        public string buttonImagePath = "Assets/05.Textures, Images, Materials/GuideUI/버튼-다음.png";
        
        [Header("이벤트 설정")]
        public string targetMethodName = "OnRebuildButtonClicked";
        public string targetClassName = "SystemManager";
    }

    [System.Serializable]
    public class WebGLSettings
    {
        [Header("해상도 설정")]
        public int defaultWidth = 1655;
        public int defaultHeight = 892;
        
        [Header("메모리 설정")]
        public int initialMemorySize = 32;
        public int maximumMemorySize = 2048;
        
        [Header("압축 설정")]
        public bool enableCompression = false;
        public bool enableDataCaching = true;
        
        [Header("템플릿 설정")]
        public string webglTemplate = "APPLICATION:Minimal";
    }

    [System.Serializable]
    public class SceneSettings
    {
        [Header("대상 오브젝트들")]
        public List<string> popupObjectNames = new List<string> { "Success_Pop", "Warning_Pop" };
        public List<string> searchRootObjects = new List<string> { "Canvas", "UI", "Popup" };
        
        [Header("씬 관리")]
        public bool autoLoadScene = true;
        public bool autoSaveScene = true;
        public string defaultScenePath = "";
    }

    [System.Serializable]
    public class DebugSettings
    {
        [Header("로깅 설정")]
        public bool enableVerboseLogging = true;
        public bool enableUnityEditorOnlyLogs = true;
        public bool enableFileLogging = false;
        
        [Header("에러 처리")]
        public bool continueOnError = true;
        public int maxRetryAttempts = 3;
    }
    #endregion
} 
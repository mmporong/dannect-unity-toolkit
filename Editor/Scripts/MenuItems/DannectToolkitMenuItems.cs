using UnityEngine;
using UnityEditor;
using System;

namespace Dannect.Unity.Toolkit.Editor
{
    /// <summary>
    /// Dannect Toolkit Unity Editor 메뉴 항목들을 제공합니다.
    /// </summary>
    public static class DannectToolkitMenuItems
    {
        #region 메뉴 상수
        private const string MENU_ROOT = "Tools/Dannect Toolkit/";
        private const int MENU_PRIORITY_START = 1000;
        #endregion

        #region 설정 및 정보
        [MenuItem(MENU_ROOT + "📋 Settings/Open Config", priority = MENU_PRIORITY_START)]
        public static void OpenConfig()
        {
            DannectToolkitConfig config = DannectToolkitEditorCore.GetOrCreateConfig();
            Selection.activeObject = config;
            EditorGUIUtility.PingObject(config);
            DannectLogger.Log("설정 파일을 열었습니다.");
        }

        [MenuItem(MENU_ROOT + "📋 Settings/Create New Config", priority = MENU_PRIORITY_START + 1)]
        public static void CreateNewConfig()
        {
            // 새 설정 파일 생성 (기존 것이 있어도)
            string newPath = EditorUtility.SaveFilePanelInProject(
                "새 설정 파일 생성",
                "DannectToolkitConfig_New",
                "asset",
                "새 설정 파일을 저장할 위치를 선택하세요."
            );

            if (!string.IsNullOrEmpty(newPath))
            {
                DannectToolkitConfig newConfig = ScriptableObject.CreateInstance<DannectToolkitConfig>();
                AssetDatabase.CreateAsset(newConfig, newPath);
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh();

                Selection.activeObject = newConfig;
                EditorGUIUtility.PingObject(newConfig);
                DannectLogger.LogSuccess($"새 설정 파일이 생성되었습니다: {newPath}");
            }
        }

        [MenuItem(MENU_ROOT + "📋 Settings/Project Info", priority = MENU_PRIORITY_START + 2)]
        public static void ShowProjectInfo()
        {
            DannectToolkitEditorCore.LogProjectInfo();
        }
        #endregion

        #region 버튼 유틸리티
        [MenuItem(MENU_ROOT + "🎯 Button Utilities/Create Rebuild Button", priority = MENU_PRIORITY_START + 10)]
        public static void CreateRebuildButton()
        {
            var success = DannectToolkitEditorCore.ExecuteWithProgress(
                "Rebuild 버튼 생성",
                () => CreateRebuildButtonInternal(),
                "설정 로드 중...",
                "Scene 확인 중...",
                "원본 버튼 찾기...",
                "버튼 복사 중...",
                "이벤트 연결 중...",
                "완료"
            );

            if (success)
            {
                DannectLogger.LogComplete("Rebuild 버튼 생성이 완료되었습니다.");
            }
            else
            {
                DannectLogger.LogError("Rebuild 버튼 생성에 실패했습니다.");
            }
        }

        [MenuItem(MENU_ROOT + "🎯 Button Utilities/Test Rebuild Button", priority = MENU_PRIORITY_START + 11)]
        public static void TestRebuildButton()
        {
            DannectToolkitConfig config = DannectToolkitEditorCore.GetOrCreateConfig();
            GameObject rebuildButton = ButtonUtility.FindButton(config.ButtonSettings.newButtonName);
            
            if (rebuildButton != null)
            {
                // 버튼 클릭 시뮬레이션
                var button = rebuildButton.GetComponent<UnityEngine.UI.Button>();
                if (button != null)
                {
                    button.onClick.Invoke();
                    DannectLogger.LogSuccess("Rebuild 버튼 테스트 완료");
                }
                else
                {
                    DannectLogger.LogError("Button 컴포넌트를 찾을 수 없습니다.");
                }
            }
            else
            {
                DannectLogger.LogError($"Rebuild 버튼을 찾을 수 없습니다: {config.ButtonSettings.newButtonName}");
            }
        }

        [MenuItem(MENU_ROOT + "🎯 Button Utilities/Find All Buttons", priority = MENU_PRIORITY_START + 12)]
        public static void FindAllButtons()
        {
            DannectLogger.LogStart("Scene의 모든 Button 컴포넌트 검색 중...");
            
            var buttons = UnityEngine.Object.FindObjectsOfType<UnityEngine.UI.Button>(true);
            DannectLogger.Log($"총 {buttons.Length}개의 Button 발견:");
            
            foreach (var button in buttons)
            {
                string path = SceneUtility.GetHierarchyPath(button.gameObject);
                string activeStatus = button.gameObject.activeInHierarchy ? "[Active]" : "[Inactive]";
                DannectLogger.Log($"  - {path} {activeStatus}");
            }
            
            DannectLogger.LogComplete("Button 검색 완료");
        }
        #endregion

        #region Scene 유틸리티
        [MenuItem(MENU_ROOT + "📂 Scene Utilities/Log Scene Hierarchy", priority = MENU_PRIORITY_START + 20)]
        public static void LogSceneHierarchy()
        {
            SceneUtility.LogSceneHierarchy(maxDepth: 4);
        }

        [MenuItem(MENU_ROOT + "📂 Scene Utilities/Ensure Scene Loaded", priority = MENU_PRIORITY_START + 21)]
        public static void EnsureSceneLoaded()
        {
            bool success = DannectToolkitEditorCore.EnsureSceneLoaded();
            if (success)
            {
                DannectLogger.LogSuccess("Scene 로드 확인 완료");
            }
            else
            {
                DannectLogger.LogError("Scene 로드 실패");
            }
        }

        [MenuItem(MENU_ROOT + "📂 Scene Utilities/Save Scene", priority = MENU_PRIORITY_START + 22)]
        public static void SaveScene()
        {
            bool success = DannectToolkitEditorCore.SaveSceneIfNeeded();
            if (success)
            {
                DannectLogger.LogSuccess("Scene 저장 완료");
            }
            else
            {
                DannectLogger.LogError("Scene 저장 실패");
            }
        }
        #endregion

        #region CLI 통합 기능
        [MenuItem(MENU_ROOT + "🚀 CLI Integration/All-in-One Rebuild Button", priority = MENU_PRIORITY_START + 30)]
        public static void AllInOneRebuildButton()
        {
            CLI_AllInOneRebuildButtonTest();
        }

        [MenuItem(MENU_ROOT + "🚀 CLI Integration/Test CLI Mode", priority = MENU_PRIORITY_START + 31)]
        public static void TestCLIMode()
        {
            CLI_TestCLIMode();
        }

        [MenuItem(MENU_ROOT + "🚀 CLI Integration/Initialize CLI", priority = MENU_PRIORITY_START + 32)]
        public static void InitializeCLI()
        {
            CLI_Initialize();
        }
        #endregion

        #region 디버그 및 로깅
        [MenuItem(MENU_ROOT + "🐛 Debug/Clear Console", priority = MENU_PRIORITY_START + 40)]
        public static void ClearConsole()
        {
            DannectLogger.ClearConsole();
        }

        [MenuItem(MENU_ROOT + "🐛 Debug/Clear Log File", priority = MENU_PRIORITY_START + 41)]
        public static void ClearLogFile()
        {
            DannectLogger.ClearLogFile();
        }

        [MenuItem(MENU_ROOT + "🐛 Debug/Open Log File", priority = MENU_PRIORITY_START + 42)]
        public static void OpenLogFile()
        {
            string logPath = DannectLogger.GetLogFilePath();
            if (System.IO.File.Exists(logPath))
            {
                Application.OpenURL(logPath);
                DannectLogger.Log($"로그 파일을 열었습니다: {logPath}");
            }
            else
            {
                DannectLogger.LogWarning("로그 파일이 존재하지 않습니다.");
            }
        }

        [MenuItem(MENU_ROOT + "🐛 Debug/Refresh Asset Database", priority = MENU_PRIORITY_START + 43)]
        public static void RefreshAssetDatabase()
        {
            DannectToolkitEditorCore.RefreshAssetDatabase();
        }
        #endregion

        #region 내부 메소드들
        /// <summary>
        /// Rebuild 버튼 생성 내부 로직
        /// </summary>
        private static void CreateRebuildButtonInternal()
        {
            try
            {
                // CLI 모드 초기화
                if (!DannectToolkitEditorCore.InitializeForCLI())
                {
                    throw new Exception("CLI 모드 초기화 실패");
                }

                // 설정 로드
                DannectToolkitConfig config = DannectToolkitEditorCore.GetOrCreateConfig();

                // Rebuild 버튼 생성
                GameObject newButton = ButtonUtility.CreateRebuildButtonAuto(config);
                if (newButton == null)
                {
                    throw new Exception("Rebuild 버튼 생성 실패");
                }

                // 정리 작업
                DannectToolkitEditorCore.CleanupForCLI();

                DannectLogger.LogSuccess($"Rebuild 버튼 생성 완료: {newButton.name}");
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Rebuild 버튼 생성 중 오류 발생", e);
                throw;
            }
        }
        #endregion

        #region CLI 전용 메소드들 (Python에서 호출)
        /// <summary>
        /// CLI용 전체 테스트 (Python에서 호출)
        /// </summary>
        public static void CLI_AllInOneRebuildButtonTest()
        {
            DannectLogger.LogStart("=== All-in-One Rebuild Button Test ===");

            try
            {
                // 1. CLI 초기화
                if (!DannectToolkitEditorCore.InitializeForCLI())
                {
                    DannectLogger.LogError("CLI 초기화 실패");
                    return;
                }

                // 2. Rebuild 버튼 생성
                CreateRebuildButtonInternal();

                // 3. 버튼 테스트
                TestRebuildButton();

                // 4. Scene 계층구조 로그
                SceneUtility.LogSceneHierarchy(2);

                // 5. 정리 작업
                DannectToolkitEditorCore.CleanupForCLI();

                DannectLogger.LogComplete("=== All-in-One Test 완료 ===");
            }
            catch (Exception e)
            {
                DannectLogger.LogException("All-in-One Test 실패", e);
            }
        }

        /// <summary>
        /// CLI 모드 테스트 (Python에서 호출)
        /// </summary>
        public static void CLI_TestCLIMode()
        {
            DannectLogger.LogStart("=== CLI 모드 테스트 ===");
            DannectLogger.Log($"Batch Mode: {Application.isBatchMode}");
            DannectLogger.Log($"Editor Mode: {Application.isEditor}");
            DannectLogger.Log($"Platform: {Application.platform}");
            DannectToolkitEditorCore.LogProjectInfo();
            DannectLogger.LogComplete("=== CLI 모드 테스트 완료 ===");
        }

        /// <summary>
        /// CLI 초기화 (Python에서 호출)
        /// </summary>
        public static void CLI_Initialize()
        {
            DannectLogger.LogStart("=== CLI 초기화 ===");
            bool success = DannectToolkitEditorCore.InitializeForCLI();
            if (success)
            {
                DannectLogger.LogComplete("=== CLI 초기화 완료 ===");
            }
            else
            {
                DannectLogger.LogError("=== CLI 초기화 실패 ===");
            }
        }

        /// <summary>
        /// CLI용 Rebuild 버튼 생성 (Python에서 호출)
        /// </summary>
        public static void CLI_CreateRebuildButton()
        {
            DannectLogger.LogStart("=== CLI Rebuild 버튼 생성 ===");
            try
            {
                CreateRebuildButtonInternal();
                DannectLogger.LogComplete("=== CLI Rebuild 버튼 생성 완료 ===");
            }
            catch (Exception e)
            {
                DannectLogger.LogException("CLI Rebuild 버튼 생성 실패", e);
            }
        }

        /// <summary>
        /// CLI용 버튼 테스트 (Python에서 호출)
        /// </summary>
        public static void CLI_TestRebuildButtonClick()
        {
            DannectLogger.LogStart("=== CLI 버튼 테스트 ===");
            TestRebuildButton();
            DannectLogger.LogComplete("=== CLI 버튼 테스트 완료 ===");
        }

        /// <summary>
        /// CLI용 디버그 (Python에서 호출)
        /// </summary>
        public static void CLI_DebugFindSuccessPop()
        {
            DannectLogger.LogStart("=== Success_Pop 디버그 ===");
            
            DannectToolkitConfig config = DannectToolkitEditorCore.GetOrCreateConfig();
            var popupObjects = SceneUtility.FindPopupObjects(config);
            
            DannectLogger.Log($"설정된 팝업 오브젝트들: {string.Join(", ", config.SceneSettings.popupObjectNames)}");
            DannectLogger.Log($"발견된 팝업 오브젝트 수: {popupObjects.Count}");
            
            foreach (var popup in popupObjects)
            {
                DannectLogger.Log($"  - {popup.name} (활성화: {popup.activeInHierarchy})");
                
                // 자식 버튼들 찾기
                var buttons = popup.GetComponentsInChildren<UnityEngine.UI.Button>(true);
                foreach (var button in buttons)
                {
                    DannectLogger.Log($"    └ 버튼: {button.name} (활성화: {button.gameObject.activeInHierarchy})");
                }
            }
            
            DannectLogger.LogComplete("=== Success_Pop 디버그 완료 ===");
        }

        /// <summary>
        /// CLI용 버튼 이벤트 확인 (Python에서 호출)
        /// </summary>
        public static void CLI_CheckRebuildButtonEvents()
        {
            DannectLogger.LogStart("=== Rebuild 버튼 이벤트 확인 ===");
            
            DannectToolkitConfig config = DannectToolkitEditorCore.GetOrCreateConfig();
            GameObject rebuildButton = ButtonUtility.FindButton(config.ButtonSettings.newButtonName);
            
            if (rebuildButton != null)
            {
                var button = rebuildButton.GetComponent<UnityEngine.UI.Button>();
                if (button != null)
                {
                    int listenerCount = button.onClick.GetPersistentEventCount();
                    DannectLogger.Log($"Rebuild 버튼 이벤트 수: {listenerCount}");
                    
                    for (int i = 0; i < listenerCount; i++)
                    {
                        var target = button.onClick.GetPersistentTarget(i);
                        var methodName = button.onClick.GetPersistentMethodName(i);
                        DannectLogger.Log($"  이벤트 {i}: {target?.GetType().Name}.{methodName}");
                    }
                }
                else
                {
                    DannectLogger.LogError("Button 컴포넌트를 찾을 수 없습니다.");
                }
            }
            else
            {
                DannectLogger.LogError($"Rebuild 버튼을 찾을 수 없습니다: {config.ButtonSettings.newButtonName}");
            }
            
            DannectLogger.LogComplete("=== Rebuild 버튼 이벤트 확인 완료 ===");
        }
        #endregion
    }
} 
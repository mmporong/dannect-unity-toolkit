using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using System;
using System.Diagnostics;

namespace Dannect.Unity.Toolkit.Editor
{
    /// <summary>
    /// Dannect Unity Toolkit의 Unity Editor 메뉴 항목들을 제공합니다.
    /// </summary>
    public static class DannectToolkitMenuItems
    {
        #region 메뉴 우선순위 상수
        private const int MENU_PRIORITY_BASE = 1000;
        private const int MENU_PRIORITY_SETTINGS = MENU_PRIORITY_BASE;
        private const int MENU_PRIORITY_BUTTON = MENU_PRIORITY_BASE + 50;
        private const int MENU_PRIORITY_SCENE = MENU_PRIORITY_BASE + 100;
        private const int MENU_PRIORITY_CLI = MENU_PRIORITY_BASE + 150;
        private const int MENU_PRIORITY_DEBUG = MENU_PRIORITY_BASE + 200;
        #endregion

        #region 📋 설정 관리
        [MenuItem("Tools/Dannect Toolkit/📋 Settings/Open Config File", priority = MENU_PRIORITY_SETTINGS)]
        public static void OpenConfigFile()
        {
            DannectToolkitEditorCore.SelectConfigInInspector();
        }

        [MenuItem("Tools/Dannect Toolkit/📋 Settings/Reset Config to Defaults", priority = MENU_PRIORITY_SETTINGS + 1)]
        public static void ResetConfigToDefaults()
        {
            var config = DannectToolkitEditorCore.LoadOrCreateConfig();
            if (config != null)
            {
                config.ResetToDefaults();
                EditorUtility.SetDirty(config);
                AssetDatabase.SaveAssets();
                DannectLogger.LogSuccess("설정이 기본값으로 초기화되었습니다.");
            }
        }

        [MenuItem("Tools/Dannect Toolkit/📋 Settings/Show Project Info", priority = MENU_PRIORITY_SETTINGS + 2)]
        public static void ShowProjectInfo()
        {
            string info = DannectToolkitEditorCore.GetProjectInfo();
            DannectLogger.Log(info);
        }
        #endregion

        #region 🎯 버튼 유틸리티
        [MenuItem("Tools/Dannect Toolkit/🎯 Button Utilities/Create Rebuild Button", priority = MENU_PRIORITY_BUTTON)]
        public static void CreateRebuildButton()
        {
            ExecuteWithProgressBar("Rebuild 버튼 생성", () => {
                if (!DannectToolkitEditorCore.EnsureSceneLoaded())
                {
                    DannectLogger.LogError("Scene 로드에 실패했습니다.");
                    return false;
                }

                var config = DannectToolkitEditorCore.LoadOrCreateConfig();
                if (config == null)
                {
                    DannectLogger.LogError("설정 파일을 로드할 수 없습니다.");
                    return false;
                }

                GameObject rebuildButton = ButtonUtility.CreateRebuildButtonAuto(config);
                if (rebuildButton != null)
                {
                    DannectToolkitEditorCore.SaveSceneIfNeeded();
                    DannectLogger.LogComplete("Rebuild 버튼 생성이 완료되었습니다!");
                    return true;
                }
                else
                {
                    DannectLogger.LogError("Rebuild 버튼 생성에 실패했습니다.");
                    return false;
                }
            });
        }

        [MenuItem("Tools/Dannect Toolkit/🎯 Button Utilities/Test Rebuild Button", priority = MENU_PRIORITY_BUTTON + 1)]
        public static void TestRebuildButton()
        {
            ExecuteWithProgressBar("Rebuild 버튼 테스트", () => {
                var config = DannectToolkitEditorCore.LoadOrCreateConfig();
                if (config == null) return false;

                GameObject rebuildButton = ButtonUtility.FindButton(config.ButtonSettings.newButtonName);
                if (rebuildButton == null)
                {
                    DannectLogger.LogError($"Rebuild 버튼을 찾을 수 없습니다: {config.ButtonSettings.newButtonName}");
                    return false;
                }

                Button buttonComponent = rebuildButton.GetComponent<Button>();
                if (buttonComponent == null)
                {
                    DannectLogger.LogError("Button 컴포넌트가 없습니다.");
                    return false;
                }

                // 버튼 상태 로그
                ButtonUtility.LogButtonState(buttonComponent);

                // 버튼 클릭 시뮬레이션
                DannectLogger.LogStart("버튼 클릭 시뮬레이션 실행...");
                buttonComponent.onClick.Invoke();
                
                return true;
            });
        }

        [MenuItem("Tools/Dannect Toolkit/🎯 Button Utilities/Find Source Button", priority = MENU_PRIORITY_BUTTON + 2)]
        public static void FindSourceButton()
        {
            var config = DannectToolkitEditorCore.LoadOrCreateConfig();
            if (config == null) return;

            GameObject sourceButton = ButtonUtility.FindButton(config.ButtonSettings.sourceButtonName);
            if (sourceButton != null)
            {
                Selection.activeGameObject = sourceButton;
                EditorGUIUtility.PingObject(sourceButton);
                DannectLogger.LogSuccess($"원본 버튼을 찾았습니다: {sourceButton.name}");
            }
            else
            {
                DannectLogger.LogError($"원본 버튼을 찾을 수 없습니다: {config.ButtonSettings.sourceButtonName}");
            }
        }
        #endregion

        #region 📂 Scene 유틸리티
        [MenuItem("Tools/Dannect Toolkit/📂 Scene Utilities/Show Scene Hierarchy", priority = MENU_PRIORITY_SCENE)]
        public static void ShowSceneHierarchy()
        {
            SceneUtility.LogSceneHierarchy(5);
        }

        [MenuItem("Tools/Dannect Toolkit/📂 Scene Utilities/Show Scene Statistics", priority = MENU_PRIORITY_SCENE + 1)]
        public static void ShowSceneStatistics()
        {
            string stats = SceneUtility.GetSceneStatistics();
            DannectLogger.Log(stats);
        }

        [MenuItem("Tools/Dannect Toolkit/📂 Scene Utilities/Find All Popup Objects", priority = MENU_PRIORITY_SCENE + 2)]
        public static void FindAllPopupObjects()
        {
            var config = DannectToolkitEditorCore.LoadOrCreateConfig();
            if (config == null) return;

            DannectLogger.Log("=== 팝업 오브젝트 검색 ===");
            foreach (string popupName in config.SceneSettings.popupObjectNames)
            {
                GameObject popup = SceneUtility.FindGameObjectByName(popupName);
                if (popup != null)
                {
                    DannectLogger.LogSuccess($"✓ {popupName}: 발견됨 (활성: {popup.activeInHierarchy})");
                    string info = SceneUtility.GetGameObjectInfo(popup);
                    DannectLogger.LogVerbose(info);
                }
                else
                {
                    DannectLogger.LogWarning($"✗ {popupName}: 찾을 수 없음");
                }
            }
            DannectLogger.Log("=======================");
        }

        [MenuItem("Tools/Dannect Toolkit/📂 Scene Utilities/Save Scene", priority = MENU_PRIORITY_SCENE + 3)]
        public static void SaveScene()
        {
            DannectToolkitEditorCore.SaveSceneIfNeeded();
        }
        #endregion

        #region 🚀 CLI 통합
        [MenuItem("Tools/Dannect Toolkit/🚀 CLI Integration/🎯 All-in-One Test", priority = MENU_PRIORITY_CLI)]
        public static void RunAllInOneTest()
        {
            ExecuteWithProgressBar("All-in-One 테스트", () => {
                DannectLogger.LogStart("🚀 All-in-One Rebuild Button Test 시작!");

                // 1. Scene 확인
                if (!DannectToolkitEditorCore.EnsureSceneLoaded())
                {
                    return false;
                }

                // 2. 설정 로드
                var config = DannectToolkitEditorCore.LoadOrCreateConfig();
                if (config == null)
                {
                    return false;
                }

                // 3. 버튼 생성
                GameObject rebuildButton = ButtonUtility.CreateRebuildButtonAuto(config);
                if (rebuildButton == null)
                {
                    return false;
                }

                // 4. 버튼 테스트
                Button buttonComponent = rebuildButton.GetComponent<Button>();
                if (buttonComponent != null)
                {
                    ButtonUtility.LogButtonState(buttonComponent);
                    buttonComponent.onClick.Invoke();
                }

                // 5. Scene 저장
                DannectToolkitEditorCore.SaveSceneIfNeeded();

                DannectLogger.LogComplete("🎯 All-in-One 테스트가 성공적으로 완료되었습니다!");
                return true;
            });
        }

        [MenuItem("Tools/Dannect Toolkit/🚀 CLI Integration/Run Python CLI", priority = MENU_PRIORITY_CLI + 1)]
        public static void RunPythonCLI()
        {
            try
            {
                string pythonScript = "dannect_unity_toolkit.py";
                if (System.IO.File.Exists(pythonScript))
                {
                    ProcessStartInfo startInfo = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"{pythonScript} --project \".\" --action all_test",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };

                    using (Process process = Process.Start(startInfo))
                    {
                        string output = process.StandardOutput.ReadToEnd();
                        string error = process.StandardError.ReadToEnd();
                        
                        process.WaitForExit();

                        if (!string.IsNullOrEmpty(output))
                        {
                            DannectLogger.Log($"Python 출력:\n{output}");
                        }

                        if (!string.IsNullOrEmpty(error))
                        {
                            DannectLogger.LogError($"Python 오류:\n{error}");
                        }

                        if (process.ExitCode == 0)
                        {
                            DannectLogger.LogSuccess("Python CLI 실행이 완료되었습니다.");
                        }
                        else
                        {
                            DannectLogger.LogError($"Python CLI 실행 실패 (종료 코드: {process.ExitCode})");
                        }
                    }
                }
                else
                {
                    DannectLogger.LogError($"Python 스크립트를 찾을 수 없습니다: {pythonScript}");
                }
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Python CLI 실행 중 오류 발생", e);
            }
        }
        #endregion

        #region 🐛 디버그 도구
        [MenuItem("Tools/Dannect Toolkit/🐛 Debug/Clear Console", priority = MENU_PRIORITY_DEBUG)]
        public static void ClearConsole()
        {
            DannectToolkitEditorCore.ClearUnityConsole();
        }

        [MenuItem("Tools/Dannect Toolkit/🐛 Debug/Test Logger", priority = MENU_PRIORITY_DEBUG + 1)]
        public static void TestLogger()
        {
            DannectLogger.Log("일반 로그 테스트");
            DannectLogger.LogWarning("경고 로그 테스트");
            DannectLogger.LogError("에러 로그 테스트");
            DannectLogger.LogSuccess("성공 로그 테스트");
            DannectLogger.LogStart("시작 로그 테스트");
            DannectLogger.LogComplete("완료 로그 테스트");
            DannectLogger.LogProgress("진행 로그 테스트");
            DannectLogger.LogVerbose("상세 로그 테스트");
            DannectLogger.LogEditor("에디터 로그 테스트");
        }

        [MenuItem("Tools/Dannect Toolkit/🐛 Debug/Show Config Contents", priority = MENU_PRIORITY_DEBUG + 2)]
        public static void ShowConfigContents()
        {
            var config = DannectToolkitEditorCore.LoadOrCreateConfig();
            if (config != null)
            {
                string json = config.ExportToJson();
                DannectLogger.Log($"현재 설정 내용:\n{json}");
            }
        }

        [MenuItem("Tools/Dannect Toolkit/🐛 Debug/Force Asset Refresh", priority = MENU_PRIORITY_DEBUG + 3)]
        public static void ForceAssetRefresh()
        {
            DannectToolkitEditorCore.ForceAssetRefresh();
        }

        [MenuItem("Tools/Dannect Toolkit/🐛 Debug/Find Success_Pop (Debug)", priority = MENU_PRIORITY_DEBUG + 4)]
        public static void FindSuccessPopDebug()
        {
            GameObject successPop = SceneUtility.FindGameObjectByName("Success_Pop");
            if (successPop != null)
            {
                Selection.activeGameObject = successPop;
                EditorGUIUtility.PingObject(successPop);
                
                string info = SceneUtility.GetGameObjectInfo(successPop);
                DannectLogger.LogSuccess($"Success_Pop을 찾았습니다!\n{info}");
                
                // 자식 오브젝트들도 확인
                DannectLogger.Log("=== Success_Pop 자식 오브젝트들 ===");
                for (int i = 0; i < successPop.transform.childCount; i++)
                {
                    Transform child = successPop.transform.GetChild(i);
                    DannectLogger.Log($"  [{i}] {child.name} (활성: {child.gameObject.activeInHierarchy})");
                    
                    if (child.name.Contains("Btn") || child.name.Contains("Button"))
                    {
                        Button btnComponent = child.GetComponent<Button>();
                        if (btnComponent != null)
                        {
                            DannectLogger.LogVerbose($"    Button 컴포넌트 발견! 이벤트 수: {btnComponent.onClick.GetPersistentEventCount()}");
                        }
                    }
                }
                DannectLogger.Log("=================================");
            }
            else
            {
                DannectLogger.LogError("Success_Pop을 찾을 수 없습니다.");
                
                // 대체 검색
                DannectLogger.LogWarning("대체 검색을 시도합니다...");
                GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
                foreach (GameObject obj in allObjects)
                {
                    if (obj.name.Contains("Success") && obj.hideFlags == HideFlags.None)
                    {
                        DannectLogger.LogVerbose($"발견된 Success 관련 오브젝트: {obj.name} (활성: {obj.activeInHierarchy})");
                    }
                }
            }
        }
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// Progress Bar와 함께 작업을 실행합니다.
        /// </summary>
        /// <param name="title">작업 제목</param>
        /// <param name="operation">실행할 작업</param>
        private static void ExecuteWithProgressBar(string title, System.Func<bool> operation)
        {
            try
            {
                DannectToolkitEditorCore.ShowProgressBar(title, "처리 중...", 0.5f);
                
                bool success = operation();
                
                if (success)
                {
                    DannectLogger.LogComplete($"{title} 완료!");
                }
                else
                {
                    DannectLogger.LogError($"{title} 실패!");
                }
            }
            catch (Exception e)
            {
                DannectLogger.LogException($"{title} 중 오류 발생", e);
            }
            finally
            {
                DannectToolkitEditorCore.CloseProgressBar();
            }
        }
        #endregion
    }
} 
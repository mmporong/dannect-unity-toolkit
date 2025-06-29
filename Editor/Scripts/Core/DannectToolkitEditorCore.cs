using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using System;
using System.IO;

namespace Dannect.Unity.Toolkit.Editor
{
    /// <summary>
    /// Dannect Unity Toolkit의 Editor 핵심 기능을 제공합니다.
    /// </summary>
    public static class DannectToolkitEditorCore
    {
        #region 상수
        private const string CONFIG_ASSET_PATH = "Assets/Resources/DannectToolkitConfig.asset";
        private const string CONFIG_RESOURCES_PATH = "DannectToolkitConfig";
        #endregion

        #region 설정 관리
        /// <summary>
        /// DannectToolkitConfig를 로드하거나 생성합니다.
        /// </summary>
        /// <returns>DannectToolkitConfig 인스턴스</returns>
        public static DannectToolkitConfig LoadOrCreateConfig()
        {
            // 1. Resources에서 로드 시도
            DannectToolkitConfig config = Resources.Load<DannectToolkitConfig>(CONFIG_RESOURCES_PATH);
            if (config != null)
            {
                DannectLogger.LogVerbose("기존 설정 파일을 로드했습니다.");
                return config;
            }

            // 2. AssetDatabase에서 로드 시도
            config = AssetDatabase.LoadAssetAtPath<DannectToolkitConfig>(CONFIG_ASSET_PATH);
            if (config != null)
            {
                DannectLogger.LogVerbose("AssetDatabase에서 설정 파일을 로드했습니다.");
                return config;
            }

            // 3. 새로 생성
            config = CreateNewConfig();
            DannectLogger.LogSuccess("새로운 설정 파일을 생성했습니다.");
            return config;
        }

        /// <summary>
        /// 새로운 설정 파일을 생성합니다.
        /// </summary>
        /// <returns>생성된 설정 파일</returns>
        private static DannectToolkitConfig CreateNewConfig()
        {
            try
            {
                // Resources 폴더 확인 및 생성
                string resourcesPath = "Assets/Resources";
                if (!Directory.Exists(resourcesPath))
                {
                    Directory.CreateDirectory(resourcesPath);
                    AssetDatabase.Refresh();
                }

                // 설정 파일 생성
                DannectToolkitConfig config = ScriptableObject.CreateInstance<DannectToolkitConfig>();
                
                // 기본값으로 초기화
                config.ResetToDefaults();

                // 파일로 저장
                AssetDatabase.CreateAsset(config, CONFIG_ASSET_PATH);
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh();

                DannectLogger.LogSuccess($"설정 파일이 생성되었습니다: {CONFIG_ASSET_PATH}");
                return config;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("설정 파일 생성 중 오류 발생", e);
                return null;
            }
        }

        /// <summary>
        /// 설정 파일을 Inspector에서 선택합니다.
        /// </summary>
        public static void SelectConfigInInspector()
        {
            DannectToolkitConfig config = LoadOrCreateConfig();
            if (config != null)
            {
                Selection.activeObject = config;
                EditorGUIUtility.PingObject(config);
                DannectLogger.LogVerbose("설정 파일이 Inspector에서 선택되었습니다.");
            }
        }
        #endregion

        #region Scene 관리
        /// <summary>
        /// CLI 모드에서 Scene이 로드되었는지 확인하고 필요시 로드합니다.
        /// </summary>
        /// <returns>Scene 로드 성공 여부</returns>
        public static bool EnsureSceneLoaded()
        {
            try
            {
                Scene currentScene = SceneManager.GetActiveScene();
                
                if (!currentScene.IsValid() || string.IsNullOrEmpty(currentScene.path))
                {
                    DannectLogger.LogWarning("현재 Scene이 유효하지 않습니다. 첫 번째 Scene을 로드합니다.");
                    return LoadFirstAvailableScene();
                }

                if (!currentScene.isLoaded)
                {
                    DannectLogger.LogWarning("Scene이 로드되지 않았습니다. 다시 로드합니다.");
                    EditorSceneManager.OpenScene(currentScene.path);
                }

                DannectLogger.LogVerbose($"현재 Scene: {currentScene.name} ({currentScene.path})");
                return true;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Scene 로드 확인 중 오류 발생", e);
                return false;
            }
        }

        /// <summary>
        /// 첫 번째 사용 가능한 Scene을 로드합니다.
        /// </summary>
        /// <returns>로드 성공 여부</returns>
        private static bool LoadFirstAvailableScene()
        {
            try
            {
                // Build Settings에서 첫 번째 Scene 가져오기
                EditorBuildSettingsScene[] buildScenes = EditorBuildSettings.scenes;
                if (buildScenes.Length > 0 && buildScenes[0].enabled)
                {
                    string scenePath = buildScenes[0].path;
                    EditorSceneManager.OpenScene(scenePath);
                    DannectLogger.LogSuccess($"첫 번째 Scene을 로드했습니다: {scenePath}");
                    return true;
                }

                // Assets 폴더에서 .unity 파일 찾기
                string[] sceneGuids = AssetDatabase.FindAssets("t:Scene");
                if (sceneGuids.Length > 0)
                {
                    string scenePath = AssetDatabase.GUIDToAssetPath(sceneGuids[0]);
                    EditorSceneManager.OpenScene(scenePath);
                    DannectLogger.LogSuccess($"Scene을 로드했습니다: {scenePath}");
                    return true;
                }

                DannectLogger.LogError("로드할 수 있는 Scene을 찾을 수 없습니다.");
                return false;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Scene 로드 중 오류 발생", e);
                return false;
            }
        }

        /// <summary>
        /// Scene에 변경사항이 있으면 저장합니다.
        /// </summary>
        /// <returns>저장 성공 여부</returns>
        public static bool SaveSceneIfNeeded()
        {
            try
            {
                Scene currentScene = SceneManager.GetActiveScene();
                
                if (currentScene.isDirty)
                {
                    bool saved = EditorSceneManager.SaveScene(currentScene);
                    if (saved)
                    {
                        DannectLogger.LogSuccess($"Scene이 저장되었습니다: {currentScene.name}");
                    }
                    else
                    {
                        DannectLogger.LogWarning("Scene 저장에 실패했습니다.");
                    }
                    return saved;
                }
                else
                {
                    SimGroundLogger.LogVerbose("Scene에 변경사항이 없습니다.");
                    return true;
                }
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("Scene 저장 중 오류 발생", e);
                return false;
            }
        }
        #endregion

        #region 프로젝트 정보
        /// <summary>
        /// 현재 프로젝트의 정보를 반환합니다.
        /// </summary>
        /// <returns>프로젝트 정보 문자열</returns>
        public static string GetProjectInfo()
        {
            try
            {
                string info = "=== SimGround 프로젝트 정보 ===\n";
                info += $"프로젝트 이름: {PlayerSettings.productName}\n";
                info += $"회사명: {PlayerSettings.companyName}\n";
                info += $"버전: {PlayerSettings.bundleVersion}\n";
                info += $"Unity 버전: {Application.unityVersion}\n";
                info += $"플랫폼: {EditorUserBuildSettings.activeBuildTarget}\n";
                
                Scene currentScene = SceneManager.GetActiveScene();
                info += $"현재 Scene: {currentScene.name}\n";
                info += $"Scene 경로: {currentScene.path}\n";
                info += $"Scene 로드됨: {currentScene.isLoaded}\n";
                info += $"Scene 수정됨: {currentScene.isDirty}\n";

                // 설정 파일 정보
                SimGroundToolkitConfig config = LoadOrCreateConfig();
                if (config != null)
                {
                    info += $"\n=== Toolkit 설정 ===\n";
                    info += $"Toolkit 버전: {config.Version}\n";
                    info += $"상세 로그: {config.DebugSettings.enableVerboseLogging}\n";
                    info += $"버튼 소스: {config.ButtonSettings.sourceButtonName}\n";
                    info += $"버튼 타겟: {config.ButtonSettings.newButtonName}\n";
                }

                info += "==============================";
                return info;
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("프로젝트 정보 수집 중 오류 발생", e);
                return "프로젝트 정보를 수집할 수 없습니다.";
            }
        }
        #endregion

        #region Unity Console 관리
        /// <summary>
        /// Unity Console을 지웁니다.
        /// </summary>
        public static void ClearUnityConsole()
        {
            try
            {
                var assembly = System.Reflection.Assembly.GetAssembly(typeof(UnityEditor.Editor));
                var type = assembly.GetType("UnityEditor.LogEntries");
                var method = type.GetMethod("Clear");
                method.Invoke(new object(), null);
                
                SimGroundLogger.LogVerbose("Unity Console이 정리되었습니다.");
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("Unity Console 정리 중 오류 발생", e);
            }
        }
        #endregion

        #region 에디터 유틸리티
        /// <summary>
        /// Editor에서 실행 중인지 확인합니다.
        /// </summary>
        /// <returns>Editor 실행 여부</returns>
        public static bool IsRunningInEditor()
        {
            return Application.isEditor && !Application.isPlaying;
        }

        /// <summary>
        /// 현재 시간으로 백업 파일명을 생성합니다.
        /// </summary>
        /// <param name="baseName">기본 파일명</param>
        /// <param name="extension">파일 확장자</param>
        /// <returns>백업 파일명</returns>
        public static string GenerateBackupFileName(string baseName, string extension = ".backup")
        {
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            return $"{baseName}_{timestamp}{extension}";
        }

        /// <summary>
        /// 에셋을 강제로 새로고침합니다.
        /// </summary>
        public static void ForceAssetRefresh()
        {
            try
            {
                AssetDatabase.SaveAssets();
                AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
                SimGroundLogger.LogVerbose("에셋 데이터베이스가 새로고침되었습니다.");
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("에셋 새로고침 중 오류 발생", e);
            }
        }

        /// <summary>
        /// Progress Bar를 표시합니다.
        /// </summary>
        /// <param name="title">진행 상황 제목</param>
        /// <param name="info">진행 상황 정보</param>
        /// <param name="progress">진행률 (0.0 ~ 1.0)</param>
        public static void ShowProgressBar(string title, string info, float progress)
        {
            EditorUtility.DisplayProgressBar(title, info, progress);
        }

        /// <summary>
        /// Progress Bar를 닫습니다.
        /// </summary>
        public static void CloseProgressBar()
        {
            EditorUtility.ClearProgressBar();
        }
        #endregion

        #region 로깅 연동
        /// <summary>
        /// Editor Core를 초기화합니다.
        /// </summary>
        [InitializeOnLoadMethod]
        public static void Initialize()
        {
            // 설정 파일 로드 및 로거 설정
            try
            {
                SimGroundToolkitConfig config = LoadOrCreateConfig();
                if (config != null)
                {
                    SimGroundLogger.UpdateSettingsFromConfig(config);
                    SimGroundLogger.LogVerbose("SimGround Toolkit Editor Core가 초기화되었습니다.");
                }
            }
            catch (Exception e)
            {
                Debug.LogException(e);
            }
        }
        #endregion
    }
} 
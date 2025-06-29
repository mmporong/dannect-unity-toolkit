using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using System;
using System.IO;

namespace Dannect.Unity.Toolkit.Editor
{
    /// <summary>
    /// Dannect Toolkit Editor 핵심 기능을 제공합니다.
    /// </summary>
    public static class DannectToolkitEditorCore
    {
        #region 상수
        private const string CONFIG_ASSET_PATH = "Assets/DannectToolkit/Resources/DannectToolkitConfig.asset";
        private const string RESOURCES_FOLDER_PATH = "Assets/DannectToolkit/Resources";
        private const string MENU_ROOT = "Tools/Dannect Toolkit/";
        #endregion

        #region 설정 관리
        /// <summary>
        /// 현재 프로젝트의 Toolkit 설정을 가져옵니다.
        /// </summary>
        /// <returns>설정 파일 (없으면 기본값 생성)</returns>
        public static DannectToolkitConfig GetOrCreateConfig()
        {
            // Resources 폴더에서 찾기
            DannectToolkitConfig config = Resources.Load<DannectToolkitConfig>("DannectToolkitConfig");
            
            if (config == null)
            {
                // 설정 파일이 없으면 생성
                config = CreateDefaultConfig();
                DannectLogger.Log("기본 설정 파일이 생성되었습니다.");
            }
            
            // 로거 설정 업데이트
            DannectLogger.UpdateSettingsFromConfig(config);
            
            return config;
        }

        /// <summary>
        /// 기본 설정 파일을 생성합니다.
        /// </summary>
        /// <returns>생성된 설정 파일</returns>
        private static DannectToolkitConfig CreateDefaultConfig()
        {
            // Resources 폴더가 없으면 생성
            if (!Directory.Exists(RESOURCES_FOLDER_PATH))
            {
                Directory.CreateDirectory(RESOURCES_FOLDER_PATH);
                AssetDatabase.Refresh();
            }

            // 설정 파일 생성
            DannectToolkitConfig config = ScriptableObject.CreateInstance<DannectToolkitConfig>();
            
            // 프로젝트별 기본값 설정
            string projectName = PlayerSettings.productName;
            if (string.IsNullOrEmpty(projectName))
            {
                projectName = Application.productName;
            }
            if (string.IsNullOrEmpty(projectName))
            {
                projectName = "Unity Project";
            }
            
            // 설정 파일 저장
            AssetDatabase.CreateAsset(config, CONFIG_ASSET_PATH);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            
            return config;
        }
        #endregion

        #region Scene 관리
        /// <summary>
        /// CLI 모드에서 Scene을 자동으로 로드합니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>로드 성공 여부</returns>
        public static bool EnsureSceneLoaded(DannectToolkitConfig config = null)
        {
            if (config == null)
                config = GetOrCreateConfig();

            Scene currentScene = SceneManager.GetActiveScene();
            
            // 이미 Scene이 로드되어 있고 유효하면 그대로 사용
            if (currentScene.isLoaded && currentScene.rootCount > 0)
            {
                DannectLogger.Log($"현재 Scene 사용: {currentScene.name}");
                return true;
            }

            DannectLogger.LogStart("Scene 자동 로드 시작...");

            try
            {
                // 1. 설정 파일에 지정된 Scene 경로 확인
                if (!string.IsNullOrEmpty(config.SceneSettings.defaultScenePath))
                {
                    if (LoadSceneByPath(config.SceneSettings.defaultScenePath))
                        return true;
                }

                // 2. Build Settings에서 활성화된 첫 번째 Scene 로드
                EditorBuildSettingsScene[] buildScenes = EditorBuildSettings.scenes;
                foreach (var buildScene in buildScenes)
                {
                    if (buildScene.enabled && !string.IsNullOrEmpty(buildScene.path))
                    {
                        if (LoadSceneByPath(buildScene.path))
                            return true;
                    }
                }

                // 3. Assets 폴더에서 Scene 파일 찾기
                string[] sceneGuids = AssetDatabase.FindAssets("t:Scene");
                foreach (string guid in sceneGuids)
                {
                    string scenePath = AssetDatabase.GUIDToAssetPath(guid);
                    if (scenePath.StartsWith("Assets/") && scenePath.EndsWith(".unity"))
                    {
                        if (LoadSceneByPath(scenePath))
                            return true;
                    }
                }

                DannectLogger.LogWarning("로드할 Scene을 찾을 수 없습니다.");
                return false;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Scene 로드 실패", e);
                return false;
            }
        }

        /// <summary>
        /// 지정된 경로의 Scene을 로드합니다.
        /// </summary>
        /// <param name="scenePath">Scene 경로</param>
        /// <returns>로드 성공 여부</returns>
        private static bool LoadSceneByPath(string scenePath)
        {
            try
            {
                if (File.Exists(scenePath))
                {
                    Scene scene = EditorSceneManager.OpenScene(scenePath);
                    if (scene.IsValid() && scene.isLoaded)
                    {
                        DannectLogger.LogSuccess($"Scene 로드 성공: {scene.name} (경로: {scenePath})");
                        DannectLogger.Log($"Scene 루트 오브젝트 수: {scene.rootCount}");
                        return true;
                    }
                }
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"Scene 로드 실패 ({scenePath}): {e.Message}");
            }
            
            return false;
        }

        /// <summary>
        /// 현재 Scene의 변경사항을 저장합니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>저장 성공 여부</returns>
        public static bool SaveSceneIfNeeded(DannectToolkitConfig config = null)
        {
            if (config == null)
                config = GetOrCreateConfig();

            if (!config.SceneSettings.autoSaveScene)
            {
                DannectLogger.Log("자동 Scene 저장이 비활성화되어 있습니다.");
                return true;
            }

            try
            {
                bool saved = EditorSceneManager.SaveOpenScenes();
                if (saved)
                {
                    DannectLogger.LogSuccess("Scene 저장 완료");
                }
                else
                {
                    DannectLogger.LogWarning("Scene 저장 실패 또는 저장할 변경사항 없음");
                }
                return saved;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Scene 저장 실패", e);
                return false;
            }
        }
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// Editor에서 진행률을 표시하면서 작업을 실행합니다.
        /// </summary>
        /// <param name="title">진행률 바 제목</param>
        /// <param name="action">실행할 작업</param>
        /// <param name="steps">작업 단계들</param>
        /// <returns>작업 성공 여부</returns>
        public static bool ExecuteWithProgress(string title, System.Action action, params string[] steps)
        {
            try
            {
                if (steps.Length == 0)
                {
                    steps = new[] { "작업 진행 중..." };
                }

                for (int i = 0; i < steps.Length; i++)
                {
                    float progress = (float)i / steps.Length;
                    EditorUtility.DisplayProgressBar(title, steps[i], progress);
                    
                    // 짧은 지연으로 UI 업데이트
                    System.Threading.Thread.Sleep(100);
                }

                // 실제 작업 실행
                action?.Invoke();

                EditorUtility.DisplayProgressBar(title, "완료", 1.0f);
                System.Threading.Thread.Sleep(500);

                return true;
            }
            catch (Exception e)
            {
                DannectLogger.LogException($"{title} 실행 실패", e);
                return false;
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }
        }

        /// <summary>
        /// 에셋 데이터베이스를 새로고침합니다.
        /// </summary>
        public static void RefreshAssetDatabase()
        {
            DannectLogger.LogProgress("Asset Database 새로고침 중...");
            AssetDatabase.Refresh();
            AssetDatabase.SaveAssets();
            DannectLogger.LogComplete("Asset Database 새로고침 완료");
        }

        /// <summary>
        /// 현재 프로젝트의 정보를 로그로 출력합니다.
        /// </summary>
        public static void LogProjectInfo()
        {
            DannectLogger.Log("=== 프로젝트 정보 ===");
            DannectLogger.Log($"프로젝트 이름: {Application.productName}");
            DannectLogger.Log($"Unity 버전: {Application.unityVersion}");
            DannectLogger.Log($"플랫폼: {Application.platform}");
            DannectLogger.Log($"빌드 타겟: {EditorUserBuildSettings.activeBuildTarget}");
            
            Scene activeScene = SceneManager.GetActiveScene();
            DannectLogger.Log($"활성 Scene: {activeScene.name} (로드됨: {activeScene.isLoaded})");
            DannectLogger.Log("==================");
        }
        #endregion

        #region CLI 지원 메소드
        /// <summary>
        /// CLI 환경인지 확인합니다.
        /// </summary>
        /// <returns>CLI 환경 여부</returns>
        public static bool IsInCLIMode()
        {
            return Application.isBatchMode;
        }

        /// <summary>
        /// CLI 모드에서 필요한 초기화를 수행합니다.
        /// </summary>
        /// <returns>초기화 성공 여부</returns>
        public static bool InitializeForCLI()
        {
            if (!IsInCLIMode())
            {
                DannectLogger.Log("GUI 모드에서 실행 중입니다.");
                return true;
            }

            DannectLogger.LogStart("CLI 모드 초기화 시작...");

            try
            {
                // 1. 설정 로드
                DannectToolkitConfig config = GetOrCreateConfig();
                
                // 2. Scene 로드
                if (config.SceneSettings.autoLoadScene)
                {
                    if (!EnsureSceneLoaded(config))
                    {
                        DannectLogger.LogWarning("Scene 로드 실패, 계속 진행합니다.");
                    }
                }

                // 3. 프로젝트 정보 출력
                LogProjectInfo();

                DannectLogger.LogComplete("CLI 모드 초기화 완료");
                return true;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("CLI 모드 초기화 실패", e);
                return false;
            }
        }

        /// <summary>
        /// CLI 모드에서 정리 작업을 수행합니다.
        /// </summary>
        /// <returns>정리 성공 여부</returns>
        public static bool CleanupForCLI()
        {
            if (!IsInCLIMode())
                return true;

            DannectLogger.LogStart("CLI 모드 정리 작업 시작...");

            try
            {
                // 1. Scene 저장
                SaveSceneIfNeeded();

                // 2. Asset Database 저장
                RefreshAssetDatabase();

                DannectLogger.LogComplete("CLI 모드 정리 작업 완료");
                return true;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("CLI 모드 정리 작업 실패", e);
                return false;
            }
        }
        #endregion
    }
} 
using UnityEngine;
using UnityEngine.SceneManagement;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Dannect.Unity.Toolkit
{
    /// <summary>
    /// Scene 관리, GameObject 검색 등의 유틸리티 기능을 제공합니다.
    /// </summary>
    public static class SceneUtility
    {
        #region GameObject 찾기
        /// <summary>
        /// 이름으로 GameObject를 찾습니다 (비활성화된 오브젝트 포함).
        /// </summary>
        /// <param name="objectName">찾을 오브젝트 이름</param>
        /// <param name="exactMatch">정확한 이름 매칭 여부</param>
        /// <returns>찾은 GameObject</returns>
        public static GameObject FindGameObjectByName(string objectName, bool exactMatch = true)
        {
            if (string.IsNullOrEmpty(objectName))
            {
                DannectLogger.LogError("objectName이 비어있습니다.");
                return null;
            }

            try
            {
                // 1. 활성화된 오브젝트에서 먼저 찾기
                GameObject activeObj = GameObject.Find(objectName);
                if (activeObj != null)
                {
                    DannectLogger.Log($"활성화된 오브젝트에서 발견: {objectName}");
                    return activeObj;
                }

                // 2. 모든 오브젝트에서 찾기 (비활성화 포함)
                GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
                foreach (GameObject obj in allObjects)
                {
                    // Scene에 있는 오브젝트만 검색 (Prefab 제외)
                    if (obj.scene.isLoaded)
                    {
                        if (exactMatch)
                        {
                            if (obj.name == objectName)
                            {
                                DannectLogger.Log($"비활성화 오브젝트에서 발견: {objectName}");
                                return obj;
                            }
                        }
                        else
                        {
                            if (obj.name.Contains(objectName))
                            {
                                DannectLogger.Log($"부분 매칭으로 발견: {obj.name} (검색어: {objectName})");
                                return obj;
                            }
                        }
                    }
                }

                DannectLogger.LogWarning($"오브젝트를 찾을 수 없습니다: {objectName}");
                return null;
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"GameObject 찾기 실패: {e.Message}");
                return null;
            }
        }

        /// <summary>
        /// 특정 타입의 컴포넌트를 가진 오브젝트를 찾습니다.
        /// </summary>
        /// <typeparam name="T">찾을 컴포넌트 타입</typeparam>
        /// <param name="objectName">오브젝트 이름 (선택사항)</param>
        /// <returns>찾은 컴포넌트</returns>
        public static T FindComponentInScene<T>(string objectName = null) where T : Component
        {
            try
            {
                if (!string.IsNullOrEmpty(objectName))
                {
                    // 특정 이름의 오브젝트에서 컴포넌트 찾기
                    GameObject targetObj = FindGameObjectByName(objectName);
                    if (targetObj != null)
                    {
                        T component = targetObj.GetComponent<T>();
                        if (component != null)
                        {
                            DannectLogger.Log($"컴포넌트 발견: {typeof(T).Name} in {objectName}");
                            return component;
                        }
                    }
                }

                // Scene의 모든 오브젝트에서 컴포넌트 찾기
                T[] components = UnityEngine.Object.FindObjectsOfType<T>(true);
                if (components.Length > 0)
                {
                    DannectLogger.Log($"컴포넌트 발견: {typeof(T).Name} in {components[0].gameObject.name}");
                    return components[0];
                }

                DannectLogger.LogWarning($"컴포넌트를 찾을 수 없습니다: {typeof(T).Name}");
                return null;
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"컴포넌트 찾기 실패: {e.Message}");
                return null;
            }
        }

        /// <summary>
        /// 여러 이름으로 GameObject를 찾습니다.
        /// </summary>
        /// <param name="objectNames">찾을 오브젝트 이름들</param>
        /// <returns>찾은 GameObject들의 리스트</returns>
        public static List<GameObject> FindGameObjectsByNames(params string[] objectNames)
        {
            List<GameObject> foundObjects = new List<GameObject>();

            foreach (string name in objectNames)
            {
                GameObject obj = FindGameObjectByName(name);
                if (obj != null)
                {
                    foundObjects.Add(obj);
                }
            }

            DannectLogger.Log($"총 {foundObjects.Count}개의 오브젝트를 찾았습니다.");
            return foundObjects;
        }
        #endregion

        #region Scene 관리
        /// <summary>
        /// 현재 활성 Scene 정보를 가져옵니다.
        /// </summary>
        /// <returns>활성 Scene</returns>
        public static Scene GetActiveScene()
        {
            return SceneManager.GetActiveScene();
        }

        /// <summary>
        /// Scene이 로드되어 있는지 확인합니다.
        /// </summary>
        /// <param name="sceneName">Scene 이름</param>
        /// <returns>로드 여부</returns>
        public static bool IsSceneLoaded(string sceneName)
        {
            if (string.IsNullOrEmpty(sceneName))
                return false;

            Scene scene = SceneManager.GetSceneByName(sceneName);
            return scene.isLoaded;
        }

        /// <summary>
        /// 로드된 모든 Scene의 정보를 가져옵니다.
        /// </summary>
        /// <returns>Scene 정보 리스트</returns>
        public static List<string> GetLoadedSceneNames()
        {
            List<string> sceneNames = new List<string>();
            
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                Scene scene = SceneManager.GetSceneAt(i);
                if (scene.isLoaded)
                {
                    sceneNames.Add(scene.name);
                }
            }

            return sceneNames;
        }

        /// <summary>
        /// Scene의 루트 오브젝트들을 가져옵니다.
        /// </summary>
        /// <param name="scene">대상 Scene (null이면 활성 Scene)</param>
        /// <returns>루트 오브젝트들</returns>
        public static GameObject[] GetRootGameObjects(Scene? scene = null)
        {
            Scene targetScene = scene ?? GetActiveScene();
            
            if (!targetScene.isLoaded)
            {
                DannectLogger.LogWarning($"Scene이 로드되지 않았습니다: {targetScene.name}");
                return new GameObject[0];
            }

            return targetScene.GetRootGameObjects();
        }
        #endregion

        #region 설정 기반 검색
        /// <summary>
        /// 설정을 기반으로 팝업 오브젝트들을 찾습니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>찾은 팝업 오브젝트들</returns>
        public static List<GameObject> FindPopupObjects(DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("config가 null입니다.");
                return new List<GameObject>();
            }

            var sceneSettings = config.SceneSettings;
            return FindGameObjectsByNames(sceneSettings.popupObjectNames.ToArray());
        }

        /// <summary>
        /// 설정을 기반으로 루트 검색 오브젝트들을 찾습니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>찾은 루트 오브젝트들</returns>
        public static List<GameObject> FindSearchRootObjects(DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("config가 null입니다.");
                return new List<GameObject>();
            }

            var sceneSettings = config.SceneSettings;
            return FindGameObjectsByNames(sceneSettings.searchRootObjects.ToArray());
        }
        #endregion

        #region 계층구조 유틸리티
        /// <summary>
        /// GameObject의 전체 계층 경로를 가져옵니다.
        /// </summary>
        /// <param name="obj">대상 GameObject</param>
        /// <returns>계층 경로 문자열</returns>
        public static string GetHierarchyPath(GameObject obj)
        {
            if (obj == null)
                return "null";

            string path = obj.name;
            Transform parent = obj.transform.parent;

            while (parent != null)
            {
                path = parent.name + "/" + path;
                parent = parent.parent;
            }

            return path;
        }

        /// <summary>
        /// 자식 오브젝트들을 재귀적으로 검색합니다.
        /// </summary>
        /// <param name="parent">부모 오브젝트</param>
        /// <param name="searchName">찾을 이름</param>
        /// <param name="exactMatch">정확한 매칭 여부</param>
        /// <returns>찾은 자식 오브젝트</returns>
        public static GameObject FindChildRecursive(GameObject parent, string searchName, bool exactMatch = true)
        {
            if (parent == null || string.IsNullOrEmpty(searchName))
                return null;

            // 직접 자식들에서 먼저 찾기
            for (int i = 0; i < parent.transform.childCount; i++)
            {
                Transform child = parent.transform.GetChild(i);
                
                bool isMatch = exactMatch ? 
                    child.name == searchName : 
                    child.name.Contains(searchName);

                if (isMatch)
                {
                    return child.gameObject;
                }
            }

            // 재귀적으로 자식들의 자식에서 찾기
            for (int i = 0; i < parent.transform.childCount; i++)
            {
                Transform child = parent.transform.GetChild(i);
                GameObject found = FindChildRecursive(child.gameObject, searchName, exactMatch);
                if (found != null)
                {
                    return found;
                }
            }

            return null;
        }
        #endregion

        #region 디버그 유틸리티
        /// <summary>
        /// Scene의 모든 오브젝트 계층구조를 로그로 출력합니다.
        /// </summary>
        /// <param name="maxDepth">최대 깊이 (기본값: 3)</param>
        public static void LogSceneHierarchy(int maxDepth = 3)
        {
            Scene activeScene = GetActiveScene();
            DannectLogger.Log($"=== Scene Hierarchy: {activeScene.name} ===");

            GameObject[] rootObjects = GetRootGameObjects();
            foreach (GameObject root in rootObjects)
            {
                LogObjectHierarchy(root, 0, maxDepth);
            }

            DannectLogger.Log("=== End of Scene Hierarchy ===");
        }

        /// <summary>
        /// 특정 오브젝트의 계층구조를 로그로 출력합니다.
        /// </summary>
        /// <param name="obj">대상 오브젝트</param>
        /// <param name="currentDepth">현재 깊이</param>
        /// <param name="maxDepth">최대 깊이</param>
        private static void LogObjectHierarchy(GameObject obj, int currentDepth, int maxDepth)
        {
            if (obj == null || currentDepth > maxDepth)
                return;

            string indent = new string(' ', currentDepth * 2);
            string activeStatus = obj.activeInHierarchy ? "[Active]" : "[Inactive]";
            
            DannectLogger.Log($"{indent}{obj.name} {activeStatus}");

            // 자식 오브젝트들 출력
            for (int i = 0; i < obj.transform.childCount; i++)
            {
                Transform child = obj.transform.GetChild(i);
                LogObjectHierarchy(child.gameObject, currentDepth + 1, maxDepth);
            }
        }
        #endregion
    }
} 
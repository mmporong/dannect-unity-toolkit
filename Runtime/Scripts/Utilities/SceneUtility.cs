using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections.Generic;
using System.Linq;
using System;

namespace Dannect.Unity.Toolkit
{
    /// <summary>
    /// Scene 관리, GameObject 검색, 계층구조 분석 등의 유틸리티 기능을 제공합니다.
    /// </summary>
    public static class SceneUtility
    {
        #region GameObject 검색
        /// <summary>
        /// 이름으로 GameObject를 찾습니다. (비활성화된 오브젝트 포함)
        /// </summary>
        /// <param name="objectName">찾을 오브젝트 이름</param>
        /// <returns>찾은 GameObject (찾지 못한 경우 null)</returns>
        public static GameObject FindGameObjectByName(string objectName)
        {
            if (string.IsNullOrEmpty(objectName))
            {
                DannectLogger.LogError("오브젝트 이름이 null 또는 비어있습니다.");
                return null;
            }

            try
            {
                // 1. 활성화된 오브젝트에서 먼저 찾기
                GameObject activeObject = GameObject.Find(objectName);
                if (activeObject != null)
                {
                    DannectLogger.LogVerbose($"활성화된 오브젝트에서 찾음: {objectName}");
                    return activeObject;
                }

                // 2. 비활성화된 오브젝트 포함하여 모든 Transform 검색
                Transform[] allTransforms = Resources.FindObjectsOfTypeAll<Transform>();
                foreach (Transform transform in allTransforms)
                {
                    if (transform.name == objectName && transform.hideFlags == HideFlags.None)
                    {
                        DannectLogger.LogVerbose($"비활성화된 오브젝트에서 찾음: {objectName}");
                        return transform.gameObject;
                    }
                }

                // 3. 씬의 루트 오브젝트들을 직접 검색
                Scene currentScene = SceneManager.GetActiveScene();
                GameObject[] rootObjects = currentScene.GetRootGameObjects();
                
                foreach (GameObject rootObject in rootObjects)
                {
                    GameObject found = FindGameObjectRecursive(rootObject.transform, objectName);
                    if (found != null)
                    {
                        DannectLogger.LogVerbose($"재귀 검색에서 찾음: {objectName}");
                        return found;
                    }
                }

                DannectLogger.LogWarning($"오브젝트를 찾을 수 없습니다: {objectName}");
                return null;
            }
            catch (Exception e)
            {
                DannectLogger.LogException($"오브젝트 검색 중 오류 발생: {objectName}", e);
                return null;
            }
        }

        /// <summary>
        /// 재귀적으로 GameObject를 검색합니다.
        /// </summary>
        /// <param name="parent">검색할 부모 Transform</param>
        /// <param name="targetName">찾을 오브젝트 이름</param>
        /// <returns>찾은 GameObject (찾지 못한 경우 null)</returns>
        private static GameObject FindGameObjectRecursive(Transform parent, string targetName)
        {
            if (parent.name == targetName)
            {
                return parent.gameObject;
            }

            for (int i = 0; i < parent.childCount; i++)
            {
                GameObject result = FindGameObjectRecursive(parent.GetChild(i), targetName);
                if (result != null)
                {
                    return result;
                }
            }

            return null;
        }

        /// <summary>
        /// 특정 컴포넌트를 가진 오브젝트를 Scene에서 찾습니다.
        /// </summary>
        /// <param name="componentName">컴포넌트 이름</param>
        /// <returns>컴포넌트를 가진 GameObject</returns>
        public static GameObject FindComponentInScene(string componentName)
        {
            if (string.IsNullOrEmpty(componentName))
            {
                DannectLogger.LogError("컴포넌트 이름이 null 또는 비어있습니다.");
                return null;
            }

            try
            {
                // 모든 MonoBehaviour 검색
                MonoBehaviour[] allComponents = Resources.FindObjectsOfTypeAll<MonoBehaviour>();
                
                foreach (MonoBehaviour component in allComponents)
                {
                    if (component != null && 
                        component.GetType().Name == componentName && 
                        component.hideFlags == HideFlags.None)
                    {
                        DannectLogger.LogVerbose($"컴포넌트를 가진 오브젝트 찾음: {componentName} in {component.gameObject.name}");
                        return component.gameObject;
                    }
                }

                DannectLogger.LogWarning($"컴포넌트를 가진 오브젝트를 찾을 수 없습니다: {componentName}");
                return null;
            }
            catch (Exception e)
            {
                DannectLogger.LogException($"컴포넌트 검색 중 오류 발생: {componentName}", e);
                return null;
            }
        }

        /// <summary>
        /// 여러 이름 중 하나라도 일치하는 GameObject를 찾습니다.
        /// </summary>
        /// <param name="objectNames">찾을 오브젝트 이름들</param>
        /// <returns>찾은 GameObject (찾지 못한 경우 null)</returns>
        public static GameObject FindAnyGameObject(params string[] objectNames)
        {
            if (objectNames == null || objectNames.Length == 0)
            {
                DannectLogger.LogError("오브젝트 이름 목록이 비어있습니다.");
                return null;
            }

            foreach (string objectName in objectNames)
            {
                GameObject found = FindGameObjectByName(objectName);
                if (found != null)
                {
                    return found;
                }
            }

            string nameList = string.Join(", ", objectNames);
            DannectLogger.LogWarning($"다음 오브젝트들을 찾을 수 없습니다: {nameList}");
            return null;
        }
        #endregion

        #region Scene 관리
        /// <summary>
        /// 현재 Scene의 정보를 반환합니다.
        /// </summary>
        /// <returns>Scene 정보 문자열</returns>
        public static string GetCurrentSceneInfo()
        {
            try
            {
                Scene currentScene = SceneManager.GetActiveScene();
                string info = $"Scene 이름: {currentScene.name}\n";
                info += $"Scene 경로: {currentScene.path}\n";
                info += $"빌드 인덱스: {currentScene.buildIndex}\n";
                info += $"로드 여부: {currentScene.isLoaded}\n";
                info += $"유효성: {currentScene.IsValid()}\n";
                info += $"루트 오브젝트 수: {currentScene.rootCount}\n";

                return info;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Scene 정보 가져오기 중 오류 발생", e);
                return "Scene 정보를 가져올 수 없습니다.";
            }
        }

        /// <summary>
        /// 현재 Scene의 모든 루트 GameObject를 반환합니다.
        /// </summary>
        /// <returns>루트 GameObject 배열</returns>
        public static GameObject[] GetRootGameObjects()
        {
            try
            {
                Scene currentScene = SceneManager.GetActiveScene();
                return currentScene.GetRootGameObjects();
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("루트 오브젝트 가져오기 중 오류 발생", e);
                return new GameObject[0];
            }
        }

        /// <summary>
        /// Scene의 계층구조를 로그로 출력합니다.
        /// </summary>
        /// <param name="maxDepth">최대 출력 깊이 (기본: 3)</param>
        public static void LogSceneHierarchy(int maxDepth = 3)
        {
            try
            {
                SimGroundLogger.Log("=== Scene 계층구조 ===");
                
                GameObject[] rootObjects = GetRootGameObjects();
                foreach (GameObject rootObject in rootObjects)
                {
                    LogObjectHierarchy(rootObject.transform, 0, maxDepth);
                }
                
                SimGroundLogger.Log("=====================");
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("Scene 계층구조 출력 중 오류 발생", e);
            }
        }

        /// <summary>
        /// 특정 오브젝트의 계층구조를 재귀적으로 로그 출력합니다.
        /// </summary>
        /// <param name="transform">출력할 Transform</param>
        /// <param name="depth">현재 깊이</param>
        /// <param name="maxDepth">최대 깊이</param>
        private static void LogObjectHierarchy(Transform transform, int depth, int maxDepth)
        {
            if (depth > maxDepth)
                return;

            string indent = new string(' ', depth * 2);
            string status = transform.gameObject.activeInHierarchy ? "✓" : "✗";
            SimGroundLogger.Log($"{indent}{status} {transform.name}");

            for (int i = 0; i < transform.childCount; i++)
            {
                LogObjectHierarchy(transform.GetChild(i), depth + 1, maxDepth);
            }
        }
        #endregion

        #region GameObject 분석
        /// <summary>
        /// GameObject의 컴포넌트 정보를 반환합니다.
        /// </summary>
        /// <param name="gameObject">분석할 GameObject</param>
        /// <returns>컴포넌트 정보 문자열</returns>
        public static string GetGameObjectInfo(GameObject gameObject)
        {
            if (gameObject == null)
            {
                return "GameObject가 null입니다.";
            }

            try
            {
                string info = $"GameObject: {gameObject.name}\n";
                info += $"활성화: {gameObject.activeInHierarchy}\n";
                info += $"태그: {gameObject.tag}\n";
                info += $"레이어: {LayerMask.LayerToName(gameObject.layer)}\n";
                info += $"자식 수: {gameObject.transform.childCount}\n";

                Component[] components = gameObject.GetComponents<Component>();
                info += $"컴포넌트 수: {components.Length}\n";
                info += "컴포넌트 목록:\n";

                foreach (Component component in components)
                {
                    if (component != null)
                    {
                        info += $"  - {component.GetType().Name}\n";
                    }
                }

                return info;
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("GameObject 정보 분석 중 오류 발생", e);
                return "GameObject 정보를 분석할 수 없습니다.";
            }
        }

        /// <summary>
        /// GameObject의 위치 정보를 반환합니다.
        /// </summary>
        /// <param name="gameObject">분석할 GameObject</param>
        /// <returns>위치 정보 문자열</returns>
        public static string GetTransformInfo(GameObject gameObject)
        {
            if (gameObject == null)
            {
                return "GameObject가 null입니다.";
            }

            try
            {
                Transform transform = gameObject.transform;
                string info = $"Transform 정보: {gameObject.name}\n";
                info += $"위치: {transform.position}\n";
                info += $"회전: {transform.rotation.eulerAngles}\n";
                info += $"크기: {transform.localScale}\n";

                RectTransform rectTransform = gameObject.GetComponent<RectTransform>();
                if (rectTransform != null)
                {
                    info += $"앵커 위치: {rectTransform.anchoredPosition}\n";
                    info += $"크기 델타: {rectTransform.sizeDelta}\n";
                    info += $"앵커 최소: {rectTransform.anchorMin}\n";
                    info += $"앵커 최대: {rectTransform.anchorMax}\n";
                }

                return info;
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("Transform 정보 분석 중 오류 발생", e);
                return "Transform 정보를 분석할 수 없습니다.";
            }
        }
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// 지정된 이름들의 오브젝트가 Scene에 존재하는지 확인합니다.
        /// </summary>
        /// <param name="objectNames">확인할 오브젝트 이름들</param>
        /// <returns>존재하는 오브젝트들의 Dictionary</returns>
        public static Dictionary<string, bool> CheckObjectsExist(params string[] objectNames)
        {
            Dictionary<string, bool> results = new Dictionary<string, bool>();

            if (objectNames == null)
            {
                SimGroundLogger.LogWarning("오브젝트 이름 목록이 null입니다.");
                return results;
            }

            foreach (string objectName in objectNames)
            {
                GameObject obj = FindGameObjectByName(objectName);
                results[objectName] = obj != null;
            }

            return results;
        }

        /// <summary>
        /// Scene에서 특정 조건을 만족하는 모든 GameObject를 찾습니다.
        /// </summary>
        /// <param name="predicate">조건 함수</param>
        /// <returns>조건을 만족하는 GameObject 목록</returns>
        public static List<GameObject> FindGameObjectsWhere(System.Func<GameObject, bool> predicate)
        {
            List<GameObject> results = new List<GameObject>();

            if (predicate == null)
            {
                SimGroundLogger.LogError("조건 함수가 null입니다.");
                return results;
            }

            try
            {
                GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
                
                foreach (GameObject obj in allObjects)
                {
                    if (obj.hideFlags == HideFlags.None && predicate(obj))
                    {
                        results.Add(obj);
                    }
                }

                SimGroundLogger.LogVerbose($"조건을 만족하는 오브젝트 {results.Count}개를 찾았습니다.");
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("조건부 오브젝트 검색 중 오류 발생", e);
            }

            return results;
        }

        /// <summary>
        /// Scene 통계 정보를 반환합니다.
        /// </summary>
        /// <returns>Scene 통계 정보</returns>
        public static string GetSceneStatistics()
        {
            try
            {
                GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
                var sceneObjects = allObjects.Where(obj => obj.hideFlags == HideFlags.None).ToArray();
                
                int activeObjects = sceneObjects.Count(obj => obj.activeInHierarchy);
                int inactiveObjects = sceneObjects.Length - activeObjects;
                
                var componentCounts = new Dictionary<string, int>();
                foreach (GameObject obj in sceneObjects)
                {
                    Component[] components = obj.GetComponents<Component>();
                    foreach (Component comp in components)
                    {
                        if (comp != null)
                        {
                            string typeName = comp.GetType().Name;
                            componentCounts[typeName] = componentCounts.GetValueOrDefault(typeName, 0) + 1;
                        }
                    }
                }

                string stats = "=== Scene 통계 ===\n";
                stats += $"전체 오브젝트: {sceneObjects.Length}\n";
                stats += $"활성화된 오브젝트: {activeObjects}\n";
                stats += $"비활성화된 오브젝트: {inactiveObjects}\n";
                stats += $"고유 컴포넌트 타입: {componentCounts.Count}\n";
                stats += "\n주요 컴포넌트:\n";

                var topComponents = componentCounts.OrderByDescending(kvp => kvp.Value).Take(10);
                foreach (var kvp in topComponents)
                {
                    stats += $"  {kvp.Key}: {kvp.Value}개\n";
                }

                return stats;
            }
            catch (Exception e)
            {
                SimGroundLogger.LogException("Scene 통계 수집 중 오류 발생", e);
                return "Scene 통계를 수집할 수 없습니다.";
            }
        }
        #endregion
    }
} 
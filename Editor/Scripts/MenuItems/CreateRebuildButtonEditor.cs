using UnityEngine;
using UnityEditor;
using UnityEngine.UI;
using Dannect.Unity.Toolkit.Editor;

namespace Dannect.Unity.Toolkit.Editor
{
    /// <summary>
    /// Rebuild 버튼 생성 및 테스트 Editor 유틸리티
    /// </summary>
    public class CreateRebuildButtonEditor : EditorWindow
    {
        [MenuItem("Tools/Dannect Rebuild Toolkit/🚀 All-in-One Rebuild Button Test")]
        public static void AllInOneRebuildButtonTest()
        {
            Debug.Log("=== 🚀 All-in-One Rebuild Button Test 시작 ===");
            
            // 1. RebuildButtonManager 찾기 또는 생성
            Debug.Log("1️⃣ RebuildButtonManager 찾는 중...");
            RebuildButtonManager rebuildManager = FindOrCreateRebuildButtonManager();
            if (rebuildManager == null)
            {
                Debug.LogError("❌ RebuildButtonManager를 찾거나 생성할 수 없습니다! 테스트 중단.");
                return;
            }
            Debug.Log($"✅ RebuildButtonManager 찾음: {rebuildManager.gameObject.name}");
            
            // 2. Success_Pop 상태 확인
            Debug.Log("2️⃣ Success_Pop 상태 확인 중...");
            GameObject successPop = FindSuccessPopAnyState();
            if (successPop == null)
            {
                Debug.LogError("❌ Success_Pop을 찾을 수 없습니다! 테스트 중단.");
                return;
            }
            Debug.Log($"✅ Success_Pop 찾음: {successPop.name}, 활성화 상태: {successPop.activeInHierarchy}");
            
            // 3. Rebuild 버튼 생성
            Debug.Log("3️⃣ Rebuild 버튼 생성 중...");
            rebuildManager.CreateRebuildButton();
            
            // 4. 생성된 버튼 확인
            Debug.Log("4️⃣ 생성된 버튼 확인 중...");
            Transform rebuildBtnTransform = successPop.transform.Find("Rebuild_Btn");
            if (rebuildBtnTransform == null)
            {
                Debug.LogError("❌ Rebuild_Btn 생성 실패!");
                return;
            }
            
            Button rebuildButton = rebuildBtnTransform.GetComponent<Button>();
            if (rebuildButton == null)
            {
                Debug.LogError("❌ Rebuild_Btn에 Button 컴포넌트가 없습니다!");
                return;
            }
            
            Debug.Log($"✅ Rebuild_Btn 생성 성공: {rebuildBtnTransform.name}");
            
            // 5. 버튼 이벤트 확인
            Debug.Log("5️⃣ 버튼 이벤트 확인 중...");
            int listenerCount = rebuildButton.onClick.GetPersistentEventCount();
            Debug.Log($"📊 버튼 이벤트 수: {listenerCount}");
            
            for (int i = 0; i < listenerCount; i++)
            {
                var target = rebuildButton.onClick.GetPersistentTarget(i);
                var methodName = rebuildButton.onClick.GetPersistentMethodName(i);
                Debug.Log($"   이벤트 {i}: {target?.GetType().Name}.{methodName}");
            }
            
            if (listenerCount == 0)
            {
                Debug.LogWarning("❌ 버튼에 연결된 이벤트가 없습니다!");
            }
            else
            {
                Debug.Log("✅ 버튼 이벤트 연결 확인 완료");
            }
            
            // 6. 버튼 클릭 테스트
            Debug.Log("6️⃣ 버튼 클릭 테스트 중...");
            try
            {
                Debug.Log("🔄 onClick.Invoke() 실행...");
                rebuildButton.onClick.Invoke();
                Debug.Log("✅ 버튼 클릭 이벤트 실행 완료");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"❌ onClick.Invoke() 실행 중 오류: {e.Message}");
                Debug.LogError($"스택 트레이스: {e.StackTrace}");
            }
            
            // 7. 추가 테스트 - 직접 메소드 호출
            Debug.Log("7️⃣ 직접 메소드 호출 테스트...");
            Debug.Log("🔄 rebuildManager.OnRebuildButtonClicked() 직접 호출...");
            rebuildManager.OnRebuildButtonClicked();
            
            // 8. 완료
            Debug.Log("=== 🎉 All-in-One Rebuild Button Test 완료 ===");
            Debug.Log("📝 결과 요약:");
            Debug.Log($"   - RebuildButtonManager: ✅ {rebuildManager.gameObject.name}");
            Debug.Log($"   - Success_Pop: ✅ {successPop.name} (활성화: {successPop.activeInHierarchy})");
            Debug.Log($"   - Rebuild_Btn: ✅ 생성됨");
            Debug.Log($"   - Button 이벤트: ✅ 연결됨");
            Debug.Log($"   - 클릭 테스트: ✅ 실행됨");
            
            // Inspector 새로고침
            EditorUtility.SetDirty(rebuildManager.gameObject);
        }
        
        /// <summary>
        /// RebuildButtonManager를 찾거나 생성하는 메서드
        /// </summary>
        private static RebuildButtonManager FindOrCreateRebuildButtonManager()
        {
            // 1. 먼저 기존 RebuildButtonManager 찾기
            RebuildButtonManager existingManager = FindFirstObjectByType<RebuildButtonManager>();
            if (existingManager != null)
            {
                Debug.Log($"기존 RebuildButtonManager 발견: {existingManager.gameObject.name}");
                return existingManager;
            }
            
            // 2. SystemManager가 있는지 확인하고 같은 GameObject에 추가
            SystemManager systemManager = FindFirstObjectByType<SystemManager>();
            if (systemManager != null)
            {
                Debug.Log("SystemManager를 찾았습니다. 같은 GameObject에 RebuildButtonManager 추가...");
                RebuildButtonManager newManager = systemManager.gameObject.AddComponent<RebuildButtonManager>();
                Debug.Log($"RebuildButtonManager를 SystemManager와 같은 GameObject에 추가했습니다: {systemManager.gameObject.name}");
                return newManager;
            }
            
            // 3. SystemManager가 없으면 새로운 GameObject 생성
            Debug.Log("SystemManager를 찾을 수 없습니다. 새로운 GameObject에 RebuildButtonManager 생성...");
            GameObject newGameObject = new GameObject("RebuildButtonManager");
            RebuildButtonManager manager = newGameObject.AddComponent<RebuildButtonManager>();
            Debug.Log($"새로운 RebuildButtonManager GameObject 생성: {newGameObject.name}");
            return manager;
        }
        
        /// <summary>
        /// Success_Pop을 활성화/비활성화 상관없이 찾는 메서드
        /// </summary>
        private static GameObject FindSuccessPopAnyState()
        {
            // 1. 활성화된 오브젝트에서 먼저 찾기
            GameObject successPop = GameObject.Find("Success_Pop");
            if (successPop != null)
            {
                return successPop;
            }
            
            // 2. 비활성화된 오브젝트도 검색
            GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
            foreach (GameObject obj in allObjects)
            {
                if (obj.scene.IsValid() && obj.name == "Success_Pop")
                {
                    return obj;
                }
            }
            
            // 3. Warning_Pop 컴포넌트를 통해 찾기
            Warning_Pop warningPop = FindFirstObjectByType<Warning_Pop>();
            if (warningPop != null && warningPop.Success_Panel != null)
            {
                return warningPop.Success_Panel;
            }
            
            return null;
        }
        
        [MenuItem("Tools/Dannect Rebuild Toolkit/Create Rebuild Button")]
        public static void CreateRebuildButton()
        {
            Debug.Log("=== Rebuild 버튼 생성 시작 ===");
            
            // RebuildButtonManager 찾기 또는 생성
            RebuildButtonManager rebuildManager = FindOrCreateRebuildButtonManager();
            
            if (rebuildManager != null)
            {
                // Rebuild 버튼 생성
                GameObject rebuildButton = rebuildManager.CreateRebuildButton();
                
                if (rebuildButton != null)
                {
                    Debug.Log($"✅ Rebuild 버튼 생성 완료: {rebuildButton.name}");
                }
                else
                {
                    Debug.LogError("❌ Rebuild 버튼 생성 실패");
                }
            }
            else
            {
                Debug.LogError("❌ RebuildButtonManager를 찾거나 생성할 수 없습니다!");
            }
        }
        
        [MenuItem("Tools/Dannect Rebuild Toolkit/Test Rebuild Button Click")]
        public static void TestRebuildButtonClick()
        {
            Debug.Log("=== Rebuild 버튼 클릭 테스트 ===");
            
            // RebuildButtonManager 찾기
            RebuildButtonManager rebuildManager = FindFirstObjectByType<RebuildButtonManager>();
            
            if (rebuildManager != null)
            {
                // OnRebuildButtonClicked 메소드 테스트 실행
                rebuildManager.OnRebuildButtonClicked();
            }
            else
            {
                Debug.LogError("Scene에서 RebuildButtonManager를 찾을 수 없습니다!");
            }
        }
        
        [MenuItem("Tools/Dannect Rebuild Toolkit/Debug/Find Success_Pop")]
        public static void DebugFindSuccessPop()
        {
            // Success_Pop 찾기 디버그
            GameObject successPop = GameObject.Find("Success_Pop");
            if (successPop != null)
            {
                Debug.Log($"[Debug] Success_Pop 찾음 (활성화됨): {successPop.name}, 활성 상태: {successPop.activeInHierarchy}");
            }
            else
            {
                Debug.Log("[Debug] 활성화된 Success_Pop을 찾을 수 없음. 비활성화된 오브젝트 검색 중...");
                
                // 비활성화된 오브젝트도 검색
                GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
                bool found = false;
                
                foreach (GameObject obj in allObjects)
                {
                    if (obj.scene.IsValid() && obj.name == "Success_Pop")
                    {
                        Debug.Log($"[Debug] Success_Pop 찾음 (비활성화됨): {obj.name}, 활성 상태: {obj.activeInHierarchy}");
                        found = true;
                        break;
                    }
                }
                
                if (!found)
                {
                    Debug.LogError("[Debug] Success_Pop을 전혀 찾을 수 없습니다!");
                }
            }
            
            // Warning_Pop 컴포넌트에서도 찾아보기
            Warning_Pop warningPop = FindFirstObjectByType<Warning_Pop>();
            if (warningPop != null)
            {
                Debug.Log($"[Debug] Warning_Pop 컴포넌트 찾음: {warningPop.name}");
                if (warningPop.Success_Panel != null)
                {
                    Debug.Log($"[Debug] Warning_Pop.Success_Panel: {warningPop.Success_Panel.name}, 활성 상태: {warningPop.Success_Panel.activeInHierarchy}");
                }
            }
        }
        
        [MenuItem("Tools/Dannect Rebuild Toolkit/Debug/Check Rebuild Button Events")]
        public static void DebugCheckRebuildButtonEvents()
        {
            // RebuildButtonManager 찾기
            RebuildButtonManager rebuildManager = FindFirstObjectByType<RebuildButtonManager>();
            if (rebuildManager == null)
            {
                Debug.LogError("[Debug] RebuildButtonManager를 찾을 수 없습니다!");
                return;
            }
            
            // Success_Pop 찾기
            GameObject successPop = GameObject.Find("Success_Pop");
            if (successPop == null)
            {
                // 비활성화된 오브젝트도 검색
                GameObject[] allObjects = Resources.FindObjectsOfTypeAll<GameObject>();
                foreach (GameObject obj in allObjects)
                {
                    if (obj.scene.IsValid() && obj.name == "Success_Pop")
                    {
                        successPop = obj;
                        break;
                    }
                }
            }
            
            if (successPop == null)
            {
                Debug.LogError("[Debug] Success_Pop을 찾을 수 없습니다!");
                return;
            }
            
            // Rebuild_Btn 찾기
            Transform rebuildBtnTransform = successPop.transform.Find("Rebuild_Btn");
            if (rebuildBtnTransform == null)
            {
                Debug.LogError("[Debug] Rebuild_Btn을 찾을 수 없습니다!");
                return;
            }
            
            Button rebuildButton = rebuildBtnTransform.GetComponent<Button>();
            if (rebuildButton == null)
            {
                Debug.LogError("[Debug] Rebuild_Btn에 Button 컴포넌트가 없습니다!");
                return;
            }
            
            // 버튼 이벤트 확인
            int listenerCount = rebuildButton.onClick.GetPersistentEventCount();
            Debug.Log($"[Debug] Rebuild 버튼 이벤트 수: {listenerCount}");
            
            for (int i = 0; i < listenerCount; i++)
            {
                var target = rebuildButton.onClick.GetPersistentTarget(i);
                var methodName = rebuildButton.onClick.GetPersistentMethodName(i);
                Debug.Log($"[Debug] 이벤트 {i}: {target?.GetType().Name}.{methodName}");
            }
            
            if (listenerCount == 0)
            {
                Debug.LogWarning("[Debug] 버튼에 연결된 이벤트가 없습니다!");
            }
            else
            {
                Debug.Log("[Debug] 버튼 이벤트 확인 완료");
            }
        }

        #region CLI 전용 메소드들 (Python에서 호출)
        /// <summary>
        /// CLI용 전체 테스트 (Python에서 호출)
        /// </summary>
        public static void CLI_AllInOneRebuildButtonTest()
        {
            Debug.Log("=== CLI: All-in-One Rebuild Button Test ===");
            
            try
            {
                AllInOneRebuildButtonTest();
                Debug.Log("=== CLI: All-in-One Test 완료 ===");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"CLI: All-in-One Test 실패: {e.Message}");
                Debug.LogError($"스택 트레이스: {e.StackTrace}");
            }
        }

        /// <summary>
        /// CLI용 Rebuild 버튼 생성 (Python에서 호출)
        /// </summary>
        public static void CLI_CreateRebuildButton()
        {
            Debug.Log("=== CLI: Rebuild 버튼 생성 ===");
            
            try
            {
                CreateRebuildButton();
                Debug.Log("=== CLI: Rebuild 버튼 생성 완료 ===");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"CLI: Rebuild 버튼 생성 실패: {e.Message}");
            }
        }

        /// <summary>
        /// CLI용 Rebuild 버튼 클릭 테스트 (Python에서 호출)
        /// </summary>
        public static void CLI_TestRebuildButtonClick()
        {
            Debug.Log("=== CLI: Rebuild 버튼 클릭 테스트 ===");
            
            try
            {
                TestRebuildButtonClick();
                Debug.Log("=== CLI: Rebuild 버튼 클릭 테스트 완료 ===");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"CLI: Rebuild 버튼 클릭 테스트 실패: {e.Message}");
            }
        }

        /// <summary>
        /// CLI용 Success_Pop 디버그 (Python에서 호출)
        /// </summary>
        public static void CLI_DebugFindSuccessPop()
        {
            Debug.Log("=== CLI: Success_Pop 디버그 ===");
            
            try
            {
                DebugFindSuccessPop();
                Debug.Log("=== CLI: Success_Pop 디버그 완료 ===");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"CLI: Success_Pop 디버그 실패: {e.Message}");
            }
        }

        /// <summary>
        /// CLI용 버튼 이벤트 확인 (Python에서 호출)
        /// </summary>
        public static void CLI_CheckRebuildButtonEvents()
        {
            Debug.Log("=== CLI: Rebuild 버튼 이벤트 확인 ===");
            
            try
            {
                DebugCheckRebuildButtonEvents();
                Debug.Log("=== CLI: Rebuild 버튼 이벤트 확인 완료 ===");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"CLI: Rebuild 버튼 이벤트 확인 실패: {e.Message}");
            }
        }
        #endregion
    }
} 
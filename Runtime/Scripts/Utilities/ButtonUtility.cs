using UnityEngine;
using UnityEngine.UI;
using System;
using System.Reflection;
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Events;
#endif

namespace Dannect.Unity.Toolkit
{
    /// <summary>
    /// 버튼 복사, 이벤트 연결, 이미지 변경 등의 유틸리티 기능을 제공합니다.
    /// </summary>
    public static class ButtonUtility
    {
        #region 버튼 복사 및 생성
        /// <summary>
        /// 기존 버튼을 복사하여 새로운 버튼을 생성합니다.
        /// </summary>
        /// <param name="sourceButton">복사할 원본 버튼</param>
        /// <param name="newButtonName">새 버튼의 이름</param>
        /// <param name="positionOffset">새 버튼의 위치 오프셋</param>
        /// <returns>생성된 새 버튼의 GameObject</returns>
        public static GameObject CopyButton(GameObject sourceButton, string newButtonName, Vector2 positionOffset = default)
        {
            if (sourceButton == null)
            {
                DannectLogger.LogError("복사할 원본 버튼이 null입니다.");
                return null;
            }

            try
            {
                // 기존 버튼이 있는지 확인하고 제거
                Transform parent = sourceButton.transform.parent;
                Transform existingButton = parent.Find(newButtonName);
                if (existingButton != null)
                {
                    DannectLogger.LogWarning($"{newButtonName}이 이미 존재합니다. 기존 버튼을 제거합니다.");
#if UNITY_EDITOR
                    UnityEngine.Object.DestroyImmediate(existingButton.gameObject);
#else
                    UnityEngine.Object.Destroy(existingButton.gameObject);
#endif
                }

                // 버튼 복사
                GameObject newButton = UnityEngine.Object.Instantiate(sourceButton, parent);
                newButton.name = newButtonName;

                // 위치 조정
                RectTransform newRectTransform = newButton.GetComponent<RectTransform>();
                RectTransform sourceRectTransform = sourceButton.GetComponent<RectTransform>();
                
                if (newRectTransform != null && sourceRectTransform != null)
                {
                    newRectTransform.anchoredPosition = sourceRectTransform.anchoredPosition + positionOffset;
                }

                DannectLogger.LogSuccess($"버튼 복사 완료: {newButtonName}");
                return newButton;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("버튼 복사 중 오류 발생", e);
                return null;
            }
        }

        /// <summary>
        /// 설정을 기반으로 자동으로 Rebuild 버튼을 생성합니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>생성된 버튼 GameObject</returns>
        public static GameObject CreateRebuildButtonAuto(DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("설정 파일이 null입니다.");
                return null;
            }

            DannectLogger.LogStart("자동 Rebuild 버튼 생성 시작...");

            try
            {
                // 1. 원본 버튼 찾기
                GameObject sourceButton = FindButton(config.ButtonSettings.sourceButtonName);
                if (sourceButton == null)
                {
                    DannectLogger.LogError($"원본 버튼을 찾을 수 없습니다: {config.ButtonSettings.sourceButtonName}");
                    return null;
                }

                // 2. 버튼 복사
                GameObject newButton = CopyButton(sourceButton, config.ButtonSettings.newButtonName, config.ButtonSettings.buttonOffset);
                if (newButton == null)
                {
                    return null;
                }

                // 3. 버튼 컴포넌트 재설정
                Button buttonComponent = ResetButtonComponent(newButton);
                if (buttonComponent == null)
                {
                    return null;
                }

                // 4. 메소드 연결
                if (!ConnectButtonMethod(buttonComponent, config.ButtonSettings.targetClassName, config.ButtonSettings.targetMethodName))
                {
                    DannectLogger.LogError("메소드 연결에 실패했습니다.");
                    return null;
                }

                // 5. 텍스트 변경
                ChangeButtonText(newButton, config.ButtonSettings.buttonText);

                // 6. 이미지 변경
                ChangeButtonImage(newButton, config.ButtonSettings.buttonImagePath);

                DannectLogger.LogComplete($"자동 Rebuild 버튼 생성 완료: {newButton.name}");
                return newButton;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("자동 Rebuild 버튼 생성 중 오류 발생", e);
                return null;
            }
        }
        #endregion

        #region 버튼 검색
        /// <summary>
        /// 이름으로 버튼을 찾습니다.
        /// </summary>
        /// <param name="buttonName">찾을 버튼 이름</param>
        /// <returns>찾은 버튼 GameObject</returns>
        public static GameObject FindButton(string buttonName)
        {
            return SceneUtility.FindGameObjectByName(buttonName);
        }
        #endregion

        #region 버튼 컴포넌트 관리
        /// <summary>
        /// 버튼 컴포넌트를 완전히 재설정합니다.
        /// </summary>
        /// <param name="buttonObject">버튼 GameObject</param>
        /// <returns>새로 생성된 Button 컴포넌트</returns>
        public static Button ResetButtonComponent(GameObject buttonObject)
        {
            if (buttonObject == null)
            {
                DannectLogger.LogError("버튼 GameObject가 null입니다.");
                return null;
            }

            try
            {
                // 기존 Button 컴포넌트 제거
                Button existingButton = buttonObject.GetComponent<Button>();
                if (existingButton != null)
                {
                    DannectLogger.LogVerbose("기존 Button 컴포넌트를 제거합니다.");
#if UNITY_EDITOR
                    UnityEngine.Object.DestroyImmediate(existingButton);
#else
                    UnityEngine.Object.Destroy(existingButton);
#endif
                }

                // 새 Button 컴포넌트 추가
                Button newButton = buttonObject.AddComponent<Button>();
                
                // TargetGraphic 설정
                Image buttonImage = buttonObject.GetComponent<Image>();
                if (buttonImage != null)
                {
                    newButton.targetGraphic = buttonImage;
                }

                // Interactable 설정
                newButton.interactable = true;

                DannectLogger.LogVerbose("Button 컴포넌트 재설정 완료");
                return newButton;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Button 컴포넌트 재설정 중 오류 발생", e);
                return null;
            }
        }

        /// <summary>
        /// 버튼에 메소드를 연결합니다.
        /// </summary>
        /// <param name="button">Button 컴포넌트</param>
        /// <param name="className">대상 클래스 이름</param>
        /// <param name="methodName">대상 메소드 이름</param>
        /// <returns>연결 성공 여부</returns>
        public static bool ConnectButtonMethod(Button button, string className, string methodName)
        {
            if (button == null)
            {
                DannectLogger.LogError("Button 컴포넌트가 null입니다.");
                return false;
            }

            try
            {
                // 1. 대상 오브젝트 찾기 (다중 방법 시도)
                GameObject targetObject = null;
                
                // 방법 1: SceneUtility 사용
                try
                {
                    targetObject = SceneUtility.FindComponentInScene(className);
                    if (targetObject != null)
                    {
                        DannectLogger.LogVerbose($"SceneUtility로 오브젝트 찾기 성공: {targetObject.name}");
                    }
                }
                catch (Exception sceneUtilException)
                {
                    DannectLogger.LogWarning($"SceneUtility 실패: {sceneUtilException.Message}");
                }
                
                // 방법 2: GameObject.Find (이름으로 직접 찾기)
                if (targetObject == null)
                {
                    targetObject = GameObject.Find(className);
                    if (targetObject != null)
                    {
                        DannectLogger.LogVerbose($"GameObject.Find로 오브젝트 찾기 성공: {targetObject.name}");
                    }
                }
                
                // 방법 3: FindFirstObjectByType 사용 (다양한 네임스페이스 시도)
                if (targetObject == null)
                {
                    string[] possibleTypeNames = {
                        className,
                        $"HeatFlowInFluid.{className}",
                        $"global::{className}",
                        $"UnityEngine.{className}"
                    };
                    
                    foreach (string typeName in possibleTypeNames)
                    {
                        try
                        {
                            System.Type componentType = System.Type.GetType(typeName);
                            if (componentType != null && typeof(Component).IsAssignableFrom(componentType))
                            {
                                Component foundComponent = UnityEngine.Object.FindFirstObjectByType(componentType) as Component;
                                if (foundComponent != null)
                                {
                                    targetObject = foundComponent.gameObject;
                                    DannectLogger.LogVerbose($"FindFirstObjectByType로 오브젝트 찾기 성공: {targetObject.name} (타입: {typeName})");
                                    break;
                                }
                            }
                        }
                        catch (Exception findObjectException)
                        {
                            DannectLogger.LogVerbose($"FindFirstObjectByType 실패 ({typeName}): {findObjectException.Message}");
                        }
                    }
                }
                
                if (targetObject == null)
                {
                    DannectLogger.LogError($"{className} 컴포넌트를 가진 오브젝트를 찾을 수 없습니다. 씬에 '{className}' GameObject가 있고 해당 스크립트가 붙어있는지 확인하세요.");
                    return false;
                }

                // 2. 컴포넌트 가져오기
                MonoBehaviour targetComponent = targetObject.GetComponent(className) as MonoBehaviour;
                if (targetComponent == null)
                {
                    DannectLogger.LogError($"{className} 컴포넌트를 찾을 수 없습니다.");
                    return false;
                }

                // 3. 메서드 존재 여부 확인
                MethodInfo targetMethod = targetComponent.GetType().GetMethod(methodName, BindingFlags.Public | BindingFlags.Instance);
                if (targetMethod == null)
                {
                    DannectLogger.LogError($"메소드를 찾을 수 없습니다: {className}.{methodName}");
                    return false;
                }

                // 4. onClick 이벤트 초기화
                button.onClick = new Button.ButtonClickedEvent();

#if UNITY_EDITOR
                // 5. SerializedObject를 사용한 Persistent Listener 연결 (Editor 전용)
                try
                {
                    // SerializedObject로 Button의 onClick 이벤트에 접근
                    SerializedObject serializedButton = new SerializedObject(button);
                    SerializedProperty onClickProperty = serializedButton.FindProperty("m_OnClick");
                    
                    if (onClickProperty != null)
                    {
                        // Persistent Calls 배열에 접근
                        SerializedProperty persistentCallsProperty = onClickProperty.FindPropertyRelative("m_PersistentCalls");
                        SerializedProperty callsProperty = persistentCallsProperty.FindPropertyRelative("m_Calls");
                        
                        // 새 Persistent Call 추가
                        int newIndex = callsProperty.arraySize;
                        callsProperty.InsertArrayElementAtIndex(newIndex);
                        
                        SerializedProperty newCall = callsProperty.GetArrayElementAtIndex(newIndex);
                        
                        // 대상 오브젝트 설정
                        SerializedProperty targetProperty = newCall.FindPropertyRelative("m_Target");
                        targetProperty.objectReferenceValue = targetComponent;
                        
                        // 메서드 이름 설정
                        SerializedProperty methodNameProperty = newCall.FindPropertyRelative("m_MethodName");
                        methodNameProperty.stringValue = methodName;
                        
                        // 호출 상태 설정 (Runtime And Editor)
                        SerializedProperty callStateProperty = newCall.FindPropertyRelative("m_CallState");
                        callStateProperty.enumValueIndex = (int)UnityEngine.Events.UnityEventCallState.RuntimeOnly;
                        
                        // Mode 설정 (Void - 매개변수 없음)
                        SerializedProperty modeProperty = newCall.FindPropertyRelative("m_Mode");
                        modeProperty.enumValueIndex = (int)UnityEngine.Events.PersistentListenerMode.Void;
                        
                        // 변경사항 적용
                        serializedButton.ApplyModifiedProperties();
                        EditorUtility.SetDirty(button);
                        
                        DannectLogger.LogSuccess($"Persistent Listener 연결 완료: {className}.{methodName}");
                    }
                    else
                    {
                        DannectLogger.LogWarning("onClick 프로퍼티를 찾을 수 없습니다.");
                    }
                }
                catch (Exception persistentException)
                {
                    DannectLogger.LogWarning($"Persistent Listener 연결 실패: {persistentException.Message}");
                    DannectLogger.LogVerbose($"스택 트레이스: {persistentException.StackTrace}");
                }
#endif

                // 6. Runtime Listener 추가 (항상 실행, 백업용)
                button.onClick.AddListener(() => {
                    try
                    {
                        targetMethod.Invoke(targetComponent, null);
                        DannectLogger.LogVerbose($"Runtime 메소드 호출 성공: {className}.{methodName}");
                    }
                    catch (Exception runtimeException)
                    {
                        DannectLogger.LogError($"Runtime 메소드 호출 실패: {runtimeException.Message}");
                    }
                });

                DannectLogger.LogSuccess($"버튼 이벤트 연결 완료: {className}.{methodName}");
                return true;
            }
            catch (Exception e)
            {
                DannectLogger.LogException("메소드 연결 중 오류 발생", e);
                return false;
            }
        }
        #endregion

        #region 버튼 외관 변경
        /// <summary>
        /// 버튼의 텍스트를 변경합니다.
        /// </summary>
        /// <param name="buttonObject">버튼 GameObject</param>
        /// <param name="newText">새로운 텍스트</param>
        public static void ChangeButtonText(GameObject buttonObject, string newText)
        {
            if (buttonObject == null || string.IsNullOrEmpty(newText))
            {
                return;
            }

            try
            {
                // Text 컴포넌트 찾기
                Text textComponent = buttonObject.GetComponentInChildren<Text>();
                if (textComponent != null)
                {
                    textComponent.text = newText;
                    DannectLogger.LogVerbose($"버튼 텍스트 변경: {newText}");
                    return;
                }

                // TextMeshPro 컴포넌트 찾기
                TMPro.TextMeshProUGUI tmpComponent = buttonObject.GetComponentInChildren<TMPro.TextMeshProUGUI>();
                if (tmpComponent != null)
                {
                    tmpComponent.text = newText;
                    DannectLogger.LogVerbose($"버튼 TextMeshPro 변경: {newText}");
                    return;
                }

                DannectLogger.LogWarning("버튼에서 Text 또는 TextMeshPro 컴포넌트를 찾을 수 없습니다.");
            }
            catch (Exception e)
            {
                DannectLogger.LogException("버튼 텍스트 변경 중 오류 발생", e);
            }
        }

        /// <summary>
        /// 버튼의 이미지를 변경합니다.
        /// </summary>
        /// <param name="buttonObject">버튼 GameObject</param>
        /// <param name="imagePath">이미지 경로</param>
        public static void ChangeButtonImage(GameObject buttonObject, string imagePath)
        {
            if (buttonObject == null || string.IsNullOrEmpty(imagePath))
            {
                return;
            }

            try
            {
                Image buttonImage = buttonObject.GetComponent<Image>();
                if (buttonImage == null)
                {
                    DannectLogger.LogWarning("버튼에서 Image 컴포넌트를 찾을 수 없습니다.");
                    return;
                }

                Sprite newSprite = LoadSprite(imagePath);
                if (newSprite != null)
                {
                    buttonImage.sprite = newSprite;
                    DannectLogger.LogVerbose($"버튼 이미지 변경 완료: {imagePath}");

#if UNITY_EDITOR
                    EditorUtility.SetDirty(buttonImage);
#endif
                }
                else
                {
                    DannectLogger.LogWarning($"이미지를 로드할 수 없습니다: {imagePath}");
                }
            }
            catch (Exception e)
            {
                DannectLogger.LogException("버튼 이미지 변경 중 오류 발생", e);
            }
        }

        /// <summary>
        /// 이미지 경로에서 Sprite를 로드합니다.
        /// </summary>
        /// <param name="imagePath">이미지 경로</param>
        /// <returns>로드된 Sprite</returns>
        private static Sprite LoadSprite(string imagePath)
        {
            try
            {
#if UNITY_EDITOR
                // Editor에서 AssetDatabase 사용
                Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(imagePath);
                if (sprite != null)
                {
                    return sprite;
                }
#endif

                // Resources 폴더에서 로드 시도
                string resourcePath = imagePath.Replace("Assets/", "").Replace(".png", "").Replace(".jpg", "");
                return Resources.Load<Sprite>(resourcePath);
            }
            catch (Exception e)
            {
                DannectLogger.LogException("Sprite 로드 중 오류 발생", e);
                return null;
            }
        }
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// 버튼의 상태를 로그로 출력합니다.
        /// </summary>
        /// <param name="button">Button 컴포넌트</param>
        public static void LogButtonState(Button button)
        {
            if (button == null)
            {
                DannectLogger.LogError("Button이 null입니다.");
                return;
            }

            DannectLogger.Log("=== 버튼 상태 정보 ===");
            DannectLogger.Log($"이름: {button.name}");
            DannectLogger.Log($"활성화: {button.gameObject.activeInHierarchy}");
            DannectLogger.Log($"상호작용 가능: {button.interactable}");
            DannectLogger.Log($"이벤트 수: {button.onClick.GetPersistentEventCount()}");
            
            for (int i = 0; i < button.onClick.GetPersistentEventCount(); i++)
            {
                var target = button.onClick.GetPersistentTarget(i);
                var methodName = button.onClick.GetPersistentMethodName(i);
                DannectLogger.Log($"  이벤트 {i}: {target?.GetType().Name}.{methodName}");
            }
            
            DannectLogger.Log("===================");
        }
        #endregion
    }
} 
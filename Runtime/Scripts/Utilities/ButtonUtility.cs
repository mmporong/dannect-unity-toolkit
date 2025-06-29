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
                    Object.DestroyImmediate(existingButton.gameObject);
#else
                    Object.Destroy(existingButton.gameObject);
#endif
                }

                // 버튼 복사
                GameObject newButton = Object.Instantiate(sourceButton, parent);
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
                    Object.DestroyImmediate(existingButton);
#else
                    Object.Destroy(existingButton);
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
                // 1. 대상 오브젝트 찾기
                GameObject targetObject = SceneUtility.FindComponentInScene(className);
                if (targetObject == null)
                {
                    DannectLogger.LogError($"{className} 컴포넌트를 가진 오브젝트를 찾을 수 없습니다.");
                    return false;
                }

                // 2. 컴포넌트 가져오기
                MonoBehaviour targetComponent = targetObject.GetComponent(className) as MonoBehaviour;
                if (targetComponent == null)
                {
                    DannectLogger.LogError($"{className} 컴포넌트를 찾을 수 없습니다.");
                    return false;
                }

                // 3. onClick 이벤트 초기화
                button.onClick = new Button.ButtonClickedEvent();

#if UNITY_EDITOR
                // 4. Persistent Listener 추가 (Editor에서만)
                UnityEventTools.AddPersistentListener(button.onClick, () => {
                    MethodInfo method = targetComponent.GetType().GetMethod(methodName);
                    if (method != null)
                    {
                        method.Invoke(targetComponent, null);
                    }
                });

                // Inspector 업데이트
                EditorUtility.SetDirty(button);
                DannectLogger.LogVerbose("Persistent Listener 추가 완료");
#endif

                // 5. Runtime Listener 추가 (백업용)
                button.onClick.AddListener(() => {
                    MethodInfo method = targetComponent.GetType().GetMethod(methodName);
                    if (method != null)
                    {
                        method.Invoke(targetComponent, null);
                    }
                    else
                    {
                        DannectLogger.LogError($"메소드를 찾을 수 없습니다: {methodName}");
                    }
                });

                DannectLogger.LogSuccess($"메소드 연결 완료: {className}.{methodName}");
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
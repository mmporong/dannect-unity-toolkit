using UnityEngine;
using UnityEngine.UI;
using System;
using System.Reflection;

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
                DannectLogger.LogError("sourceButton이 null입니다.");
                return null;
            }

            try
            {
                // 버튼 복제
                GameObject newButton = UnityEngine.Object.Instantiate(sourceButton, sourceButton.transform.parent);
                newButton.name = newButtonName;

                // 위치 조정
                if (newButton.TryGetComponent<RectTransform>(out var rectTransform))
                {
                    Vector3 currentPos = rectTransform.anchoredPosition;
                    rectTransform.anchoredPosition = new Vector2(currentPos.x + positionOffset.x, currentPos.y + positionOffset.y);
                }

                DannectLogger.Log($"버튼 복사 완료: {sourceButton.name} -> {newButtonName}");
                return newButton;
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"버튼 복사 실패: {e.Message}");
                return null;
            }
        }

        /// <summary>
        /// 설정 파일을 기반으로 버튼을 복사합니다.
        /// </summary>
        /// <param name="sourceButton">복사할 원본 버튼</param>
        /// <param name="config">설정 파일</param>
        /// <returns>생성된 새 버튼의 GameObject</returns>
        public static GameObject CopyButtonWithConfig(GameObject sourceButton, DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("config가 null입니다.");
                return null;
            }

            var buttonSettings = config.ButtonSettings;
            GameObject newButton = CopyButton(sourceButton, buttonSettings.newButtonName, buttonSettings.buttonOffset);

            if (newButton != null)
            {
                // 버튼 텍스트 변경
                ChangeButtonText(newButton, buttonSettings.buttonText);

                // 버튼 이미지 변경
                if (!string.IsNullOrEmpty(buttonSettings.buttonImagePath))
                {
                    ChangeButtonImage(newButton, buttonSettings.buttonImagePath);
                }
            }

            return newButton;
        }
        #endregion

        #region 버튼 이벤트 연결
        /// <summary>
        /// 버튼에 메소드를 연결합니다.
        /// </summary>
        /// <param name="button">대상 버튼</param>
        /// <param name="target">메소드가 있는 객체</param>
        /// <param name="methodName">연결할 메소드 이름</param>
        /// <returns>연결 성공 여부</returns>
        public static bool ConnectButtonMethod(GameObject button, MonoBehaviour target, string methodName)
        {
            if (button == null || target == null || string.IsNullOrEmpty(methodName))
            {
                DannectLogger.LogError("버튼 메소드 연결: 잘못된 매개변수");
                return false;
            }

            if (!button.TryGetComponent<Button>(out var buttonComponent))
            {
                DannectLogger.LogError($"Button 컴포넌트를 찾을 수 없습니다: {button.name}");
                return false;
            }

            try
            {
                // 기존 이벤트 모두 제거
                buttonComponent.onClick.RemoveAllListeners();

                // 메소드 찾기
                MethodInfo method = target.GetType().GetMethod(methodName, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                if (method == null)
                {
                    DannectLogger.LogError($"메소드를 찾을 수 없습니다: {methodName} in {target.GetType().Name}");
                    return false;
                }

                // 메소드 연결
                buttonComponent.onClick.AddListener(() => method.Invoke(target, null));

                DannectLogger.Log($"버튼 메소드 연결 완료: {button.name} -> {target.GetType().Name}.{methodName}");
                return true;
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"버튼 메소드 연결 실패: {e.Message}");
                return false;
            }
        }

        /// <summary>
        /// 설정을 기반으로 버튼에 메소드를 연결합니다.
        /// </summary>
        /// <param name="button">대상 버튼</param>
        /// <param name="config">설정 파일</param>
        /// <returns>연결 성공 여부</returns>
        public static bool ConnectButtonMethodWithConfig(GameObject button, DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("config가 null입니다.");
                return false;
            }

            var buttonSettings = config.ButtonSettings;

            // SystemManager 찾기
            MonoBehaviour target = SceneUtility.FindComponentInScene<MonoBehaviour>(buttonSettings.targetClassName);
            if (target == null)
            {
                DannectLogger.LogError($"{buttonSettings.targetClassName}를 찾을 수 없습니다.");
                return false;
            }

            return ConnectButtonMethod(button, target, buttonSettings.targetMethodName);
        }
        #endregion

        #region 버튼 외관 변경
        /// <summary>
        /// 버튼의 텍스트를 변경합니다.
        /// </summary>
        /// <param name="button">대상 버튼</param>
        /// <param name="text">새로운 텍스트</param>
        /// <returns>변경 성공 여부</returns>
        public static bool ChangeButtonText(GameObject button, string text)
        {
            if (button == null || string.IsNullOrEmpty(text))
            {
                DannectLogger.LogError("ChangeButtonText: 잘못된 매개변수");
                return false;
            }

            try
            {
                // Text 컴포넌트 찾기 (버튼 자체 또는 자식 오브젝트에서)
                Text textComponent = button.GetComponentInChildren<Text>();
                if (textComponent != null)
                {
                    textComponent.text = text;
                    DannectLogger.Log($"버튼 텍스트 변경 완료: {button.name} -> '{text}'");
                    return true;
                }

                // TextMeshPro 컴포넌트 찾기
                var tmpComponent = button.GetComponentInChildren<TMPro.TextMeshProUGUI>();
                if (tmpComponent != null)
                {
                    tmpComponent.text = text;
                    DannectLogger.Log($"버튼 TextMeshPro 텍스트 변경 완료: {button.name} -> '{text}'");
                    return true;
                }

                DannectLogger.LogWarning($"텍스트 컴포넌트를 찾을 수 없습니다: {button.name}");
                return false;
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"버튼 텍스트 변경 실패: {e.Message}");
                return false;
            }
        }

        /// <summary>
        /// 버튼의 이미지를 변경합니다.
        /// </summary>
        /// <param name="button">대상 버튼</param>
        /// <param name="imagePath">새로운 이미지 경로</param>
        /// <returns>변경 성공 여부</returns>
        public static bool ChangeButtonImage(GameObject button, string imagePath)
        {
            if (button == null || string.IsNullOrEmpty(imagePath))
            {
                DannectLogger.LogError("ChangeButtonImage: 잘못된 매개변수");
                return false;
            }

            try
            {
                // Assets 경로에서 이미지 로드
                Sprite newSprite = Resources.Load<Sprite>(imagePath.Replace("Assets/Resources/", "").Replace(".png", ""));
                
                // Resources 폴더에 없으면 AssetDatabase 사용 (Editor Only)
                if (newSprite == null)
                {
#if UNITY_EDITOR
                    newSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(imagePath);
#endif
                }

                if (newSprite == null)
                {
                    DannectLogger.LogWarning($"이미지를 찾을 수 없습니다: {imagePath}");
                    return false;
                }

                // Image 컴포넌트 찾기
                Image imageComponent = button.GetComponent<Image>();
                if (imageComponent != null)
                {
                    imageComponent.sprite = newSprite;
                    DannectLogger.Log($"버튼 이미지 변경 완료: {button.name} -> {imagePath}");
                    return true;
                }

                DannectLogger.LogWarning($"Image 컴포넌트를 찾을 수 없습니다: {button.name}");
                return false;
            }
            catch (Exception e)
            {
                DannectLogger.LogError($"버튼 이미지 변경 실패: {e.Message}");
                return false;
            }
        }
        #endregion

        #region 버튼 검색
        /// <summary>
        /// 이름으로 버튼을 찾습니다 (비활성화된 오브젝트 포함).
        /// </summary>
        /// <param name="buttonName">찾을 버튼 이름</param>
        /// <param name="searchInactive">비활성화된 오브젝트도 검색할지 여부</param>
        /// <returns>찾은 버튼 GameObject</returns>
        public static GameObject FindButton(string buttonName, bool searchInactive = true)
        {
            if (string.IsNullOrEmpty(buttonName))
            {
                DannectLogger.LogError("buttonName이 비어있습니다.");
                return null;
            }

            if (searchInactive)
            {
                return SceneUtility.FindGameObjectByName(buttonName);
            }
            else
            {
                return GameObject.Find(buttonName);
            }
        }

        /// <summary>
        /// 설정을 기반으로 원본 버튼을 찾습니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>찾은 버튼 GameObject</returns>
        public static GameObject FindSourceButton(DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("config가 null입니다.");
                return null;
            }

            return FindButton(config.ButtonSettings.sourceButtonName);
        }
        #endregion

        #region 완전 자동화 메소드
        /// <summary>
        /// 설정 파일을 기반으로 버튼을 완전 자동으로 생성합니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        /// <returns>생성된 버튼 GameObject</returns>
        public static GameObject CreateRebuildButtonAuto(DannectToolkitConfig config)
        {
            if (config == null)
            {
                DannectLogger.LogError("config가 null입니다.");
                return null;
            }

            DannectLogger.Log("🔧 자동 Rebuild 버튼 생성 시작...");

            // 1. 원본 버튼 찾기
            GameObject sourceButton = FindSourceButton(config);
            if (sourceButton == null)
            {
                DannectLogger.LogError($"원본 버튼을 찾을 수 없습니다: {config.ButtonSettings.sourceButtonName}");
                return null;
            }

            // 2. 기존 Rebuild 버튼이 있는지 확인
            GameObject existingButton = FindButton(config.ButtonSettings.newButtonName);
            if (existingButton != null)
            {
                DannectLogger.LogWarning($"이미 {config.ButtonSettings.newButtonName} 버튼이 존재합니다. 제거 후 재생성합니다.");
                UnityEngine.Object.DestroyImmediate(existingButton);
            }

            // 3. 버튼 복사
            GameObject newButton = CopyButtonWithConfig(sourceButton, config);
            if (newButton == null)
            {
                DannectLogger.LogError("버튼 복사 실패");
                return null;
            }

            // 4. 메소드 연결
            if (!ConnectButtonMethodWithConfig(newButton, config))
            {
                DannectLogger.LogError("버튼 메소드 연결 실패");
                // 연결 실패해도 버튼은 생성되었으므로 계속 진행
            }

            DannectLogger.Log($"✅ 자동 Rebuild 버튼 생성 완료: {newButton.name}");
            return newButton;
        }
        #endregion
    }
} 
using UnityEngine;
using System;
using System.IO;
using System.Diagnostics;

namespace Dannect.Unity.Toolkit
{
    /// <summary>
    /// Dannect Unity Toolkit 전용 로깅 시스템
    /// </summary>
    public static class DannectLogger
    {
        #region 상수 및 설정
        private const string LOG_PREFIX = "[DannectToolkit]";
        private static readonly string LOG_FILE_PATH = Path.Combine(Application.persistentDataPath, "DannectToolkit_Log.txt");
        
        // 설정 (Inspector나 Config에서 변경 가능)
        private static bool s_enableVerboseLogging = true;
        private static bool s_enableUnityEditorOnlyLogs = true;
        private static bool s_enableFileLogging = false;
        
        // 색상 코드 (Rich Text 지원)
        private const string COLOR_INFO = "#00FF00";      // 초록색
        private const string COLOR_WARNING = "#FFAA00";   // 주황색
        private const string COLOR_ERROR = "#FF0000";     // 빨간색
        private const string COLOR_SUCCESS = "#00FFFF";   // 시안색
        private const string COLOR_START = "#FF00FF";     // 마젠타색
        private const string COLOR_COMPLETE = "#FFFF00";  // 노란색
        private const string COLOR_PROGRESS = "#00AAFF";  // 하늘색
        #endregion

        #region 기본 로그 메소드
        /// <summary>
        /// 일반 정보 로그
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void Log(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage(message.ToString(), COLOR_INFO);
            UnityEngine.Debug.Log(formattedMessage, context);
            WriteToFile($"INFO: {message}");
        }

        /// <summary>
        /// 경고 로그
        /// </summary>
        /// <param name="message">경고 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogWarning(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage(message.ToString(), COLOR_WARNING);
            UnityEngine.Debug.LogWarning(formattedMessage, context);
            WriteToFile($"WARNING: {message}");
        }

        /// <summary>
        /// 에러 로그
        /// </summary>
        /// <param name="message">에러 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogError(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage(message.ToString(), COLOR_ERROR);
            UnityEngine.Debug.LogError(formattedMessage, context);
            WriteToFile($"ERROR: {message}");
        }
        #endregion

        #region 확장 로그 메소드
        /// <summary>
        /// 성공 로그 (초록색)
        /// </summary>
        /// <param name="message">성공 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogSuccess(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage($"✅ {message}", COLOR_SUCCESS);
            UnityEngine.Debug.Log(formattedMessage, context);
            WriteToFile($"SUCCESS: {message}");
        }

        /// <summary>
        /// 시작 로그 (마젠타색)
        /// </summary>
        /// <param name="message">시작 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogStart(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage($"🚀 {message}", COLOR_START);
            UnityEngine.Debug.Log(formattedMessage, context);
            WriteToFile($"START: {message}");
        }

        /// <summary>
        /// 완료 로그 (노란색)
        /// </summary>
        /// <param name="message">완료 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogComplete(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage($"🎯 {message}", COLOR_COMPLETE);
            UnityEngine.Debug.Log(formattedMessage, context);
            WriteToFile($"COMPLETE: {message}");
        }

        /// <summary>
        /// 진행 상황 로그 (하늘색)
        /// </summary>
        /// <param name="message">진행 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogProgress(object message, UnityEngine.Object context = null)
        {
            string formattedMessage = FormatMessage($"🔄 {message}", COLOR_PROGRESS);
            UnityEngine.Debug.Log(formattedMessage, context);
            WriteToFile($"PROGRESS: {message}");
        }

        /// <summary>
        /// 예외 로그 (상세한 스택 트레이스 포함)
        /// </summary>
        /// <param name="message">예외 메시지</param>
        /// <param name="exception">예외 객체</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogException(string message, Exception exception, UnityEngine.Object context = null)
        {
            string fullMessage = $"{message}\n예외: {exception.Message}\n스택 트레이스:\n{exception.StackTrace}";
            string formattedMessage = FormatMessage($"💥 {fullMessage}", COLOR_ERROR);
            UnityEngine.Debug.LogError(formattedMessage, context);
            WriteToFile($"EXCEPTION: {fullMessage}");
        }
        #endregion

        #region 조건부 로그 메소드
        /// <summary>
        /// 에디터에서만 출력되는 로그
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        [Conditional("UNITY_EDITOR")]
        public static void LogEditor(object message, UnityEngine.Object context = null)
        {
            if (s_enableUnityEditorOnlyLogs)
            {
                Log($"[Editor Only] {message}", context);
            }
        }

        /// <summary>
        /// 상세 로그 (Verbose 모드에서만 출력)
        /// </summary>
        /// <param name="message">상세 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        public static void LogVerbose(object message, UnityEngine.Object context = null)
        {
            if (s_enableVerboseLogging)
            {
                Log($"[Verbose] {message}", context);
            }
        }

        /// <summary>
        /// 개발 빌드에서만 출력되는 로그
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="context">컨텍스트 오브젝트 (optional)</param>
        [Conditional("DEVELOPMENT_BUILD")]
        [Conditional("UNITY_EDITOR")]
        public static void LogDevelopment(object message, UnityEngine.Object context = null)
        {
            Log($"[Development] {message}", context);
        }
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// 로그 설정을 업데이트합니다
        /// </summary>
        /// <param name="enableVerbose">상세 로그 활성화</param>
        /// <param name="enableEditorOnly">에디터 전용 로그 활성화</param>
        /// <param name="enableFileLogging">파일 로깅 활성화</param>
        public static void UpdateSettings(bool enableVerbose = true, bool enableEditorOnly = true, bool enableFileLogging = false)
        {
            s_enableVerboseLogging = enableVerbose;
            s_enableUnityEditorOnlyLogs = enableEditorOnly;
            s_enableFileLogging = enableFileLogging;
            
            Log($"로거 설정 업데이트됨 - Verbose: {enableVerbose}, EditorOnly: {enableEditorOnly}, FileLogging: {enableFileLogging}");
        }

        /// <summary>
        /// Config 파일에서 설정을 업데이트합니다
        /// </summary>
        /// <param name="config">설정 파일</param>
        public static void UpdateSettingsFromConfig(DannectToolkitConfig config)
        {
            if (config?.DebugSettings != null)
            {
                UpdateSettings(
                    config.DebugSettings.enableVerboseLogging,
                    config.DebugSettings.enableUnityEditorOnlyLogs,
                    config.DebugSettings.enableFileLogging
                );
            }
        }

        /// <summary>
        /// Unity Console을 지웁니다
        /// </summary>
        public static void ClearConsole()
        {
#if UNITY_EDITOR
            var assembly = System.Reflection.Assembly.GetAssembly(typeof(UnityEditor.Editor));
            var type = assembly.GetType("UnityEditor.LogEntries");
            var method = type.GetMethod("Clear");
            method.Invoke(new object(), null);
            Log("Unity Console이 정리되었습니다.");
#endif
        }

        /// <summary>
        /// 로그 파일을 지웁니다
        /// </summary>
        public static void ClearLogFile()
        {
            try
            {
                if (File.Exists(LOG_FILE_PATH))
                {
                    File.Delete(LOG_FILE_PATH);
                    Log("로그 파일이 삭제되었습니다.");
                }
            }
            catch (Exception e)
            {
                LogError($"로그 파일 삭제 실패: {e.Message}");
            }
        }

        /// <summary>
        /// 로그 파일 경로를 반환합니다
        /// </summary>
        /// <returns>로그 파일 경로</returns>
        public static string GetLogFilePath()
        {
            return LOG_FILE_PATH;
        }
        #endregion

        #region 내부 메소드
        /// <summary>
        /// 메시지를 포맷팅합니다
        /// </summary>
        /// <param name="message">원본 메시지</param>
        /// <param name="color">색상 코드</param>
        /// <returns>포맷팅된 메시지</returns>
        private static string FormatMessage(string message, string color)
        {
            string timestamp = DateTime.Now.ToString("HH:mm:ss");
            return $"{LOG_PREFIX} <color={color}>[{timestamp}] {message}</color>";
        }

        /// <summary>
        /// 파일에 로그를 작성합니다
        /// </summary>
        /// <param name="message">파일에 작성할 메시지</param>
        private static void WriteToFile(string message)
        {
            if (!s_enableFileLogging)
                return;

            try
            {
                string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
                string logEntry = $"[{timestamp}] {message}\n";
                File.AppendAllText(LOG_FILE_PATH, logEntry);
            }
            catch (Exception e)
            {
                // 파일 쓰기 실패해도 Unity Console에는 출력하지 않음 (무한 루프 방지)
                UnityEngine.Debug.LogWarning($"로그 파일 쓰기 실패: {e.Message}");
            }
        }
        #endregion
    }
} 
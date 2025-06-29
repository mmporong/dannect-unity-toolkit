using UnityEngine;
using System;
using System.IO;
using System.Diagnostics;

namespace Dannect.Unity.Toolkit
{
    /// <summary>
    /// Dannect Toolkit 전용 로깅 시스템
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
        private const string COLOR_WARNING = "#FFFF00";   // 노란색
        private const string COLOR_ERROR = "#FF0000";     // 빨간색
        private const string COLOR_DEBUG = "#00FFFF";     // 시안색
        #endregion

        #region 설정 메소드
        /// <summary>
        /// 로거 설정을 업데이트합니다.
        /// </summary>
        /// <param name="enableVerbose">상세 로깅 활성화</param>
        /// <param name="enableEditorOnly">Editor 전용 로그 활성화</param>
        /// <param name="enableFileLogging">파일 로깅 활성화</param>
        public static void UpdateSettings(bool enableVerbose, bool enableEditorOnly, bool enableFileLogging)
        {
            s_enableVerboseLogging = enableVerbose;
            s_enableUnityEditorOnlyLogs = enableEditorOnly;
            s_enableFileLogging = enableFileLogging;
            
            Log($"로거 설정 업데이트: Verbose={enableVerbose}, EditorOnly={enableEditorOnly}, FileLogging={enableFileLogging}");
        }

        /// <summary>
        /// Config 파일을 기반으로 로거 설정을 업데이트합니다.
        /// </summary>
        /// <param name="config">설정 파일</param>
        public static void UpdateSettingsFromConfig(DannectToolkitConfig config)
        {
            if (config == null)
            {
                LogError("config가 null입니다.");
                return;
            }

            var debugSettings = config.DebugSettings;
            UpdateSettings(
                debugSettings.enableVerboseLogging,
                debugSettings.enableUnityEditorOnlyLogs,
                debugSettings.enableFileLogging
            );
        }
        #endregion

        #region 기본 로깅 메소드
        /// <summary>
        /// 일반 정보 로그를 출력합니다.
        /// </summary>
        /// <param name="message">로그 메시지</param>
        [Conditional("UNITY_EDITOR")]
        [Conditional("DEVELOPMENT_BUILD")]
        public static void Log(string message)
        {
            if (!s_enableVerboseLogging)
                return;

            string formattedMessage = FormatMessage(message, LogType.Log);
            
            UnityEngine.Debug.Log($"<color={COLOR_INFO}>{formattedMessage}</color>");
            
            if (s_enableFileLogging)
                WriteToFile(formattedMessage, LogType.Log);
        }

        /// <summary>
        /// 경고 로그를 출력합니다.
        /// </summary>
        /// <param name="message">경고 메시지</param>
        public static void LogWarning(string message)
        {
            string formattedMessage = FormatMessage(message, LogType.Warning);
            
            UnityEngine.Debug.LogWarning($"<color={COLOR_WARNING}>{formattedMessage}</color>");
            
            if (s_enableFileLogging)
                WriteToFile(formattedMessage, LogType.Warning);
        }

        /// <summary>
        /// 에러 로그를 출력합니다.
        /// </summary>
        /// <param name="message">에러 메시지</param>
        public static void LogError(string message)
        {
            string formattedMessage = FormatMessage(message, LogType.Error);
            
            UnityEngine.Debug.LogError($"<color={COLOR_ERROR}>{formattedMessage}</color>");
            
            if (s_enableFileLogging)
                WriteToFile(formattedMessage, LogType.Error);
        }

        /// <summary>
        /// 디버그 로그를 출력합니다 (Editor 전용).
        /// </summary>
        /// <param name="message">디버그 메시지</param>
        [Conditional("UNITY_EDITOR")]
        public static void LogDebug(string message)
        {
            if (!s_enableUnityEditorOnlyLogs || !s_enableVerboseLogging)
                return;

            string formattedMessage = FormatMessage($"[DEBUG] {message}", LogType.Log);
            
            UnityEngine.Debug.Log($"<color={COLOR_DEBUG}>{formattedMessage}</color>");
            
            if (s_enableFileLogging)
                WriteToFile(formattedMessage, LogType.Log);
        }
        #endregion

        #region 고급 로깅 메소드
        /// <summary>
        /// 예외 정보와 함께 에러 로그를 출력합니다.
        /// </summary>
        /// <param name="message">에러 메시지</param>
        /// <param name="exception">예외 객체</param>
        public static void LogException(string message, Exception exception)
        {
            string fullMessage = $"{message}\n예외: {exception?.Message}\n스택 트레이스:\n{exception?.StackTrace}";
            LogError(fullMessage);
        }

        /// <summary>
        /// 조건부 로그를 출력합니다.
        /// </summary>
        /// <param name="condition">조건</param>
        /// <param name="message">로그 메시지</param>
        /// <param name="logType">로그 타입</param>
        [Conditional("UNITY_EDITOR")]
        [Conditional("DEVELOPMENT_BUILD")]
        public static void LogIf(bool condition, string message, LogType logType = LogType.Log)
        {
            if (!condition)
                return;

            switch (logType)
            {
                case LogType.Log:
                    Log(message);
                    break;
                case LogType.Warning:
                    LogWarning(message);
                    break;
                case LogType.Error:
                    LogError(message);
                    break;
            }
        }

        /// <summary>
        /// 성공 메시지를 출력합니다.
        /// </summary>
        /// <param name="message">성공 메시지</param>
        [Conditional("UNITY_EDITOR")]
        [Conditional("DEVELOPMENT_BUILD")]
        public static void LogSuccess(string message)
        {
            Log($"✅ {message}");
        }

        /// <summary>
        /// 진행 상황을 출력합니다.
        /// </summary>
        /// <param name="message">진행 메시지</param>
        [Conditional("UNITY_EDITOR")]
        [Conditional("DEVELOPMENT_BUILD")]
        public static void LogProgress(string message)
        {
            Log($"🔄 {message}");
        }

        /// <summary>
        /// 시작 메시지를 출력합니다.
        /// </summary>
        /// <param name="message">시작 메시지</param>
        [Conditional("UNITY_EDITOR")]
        [Conditional("DEVELOPMENT_BUILD")]
        public static void LogStart(string message)
        {
            Log($"🚀 {message}");
        }

        /// <summary>
        /// 완료 메시지를 출력합니다.
        /// </summary>
        /// <param name="message">완료 메시지</param>
        [Conditional("UNITY_EDITOR")]
        [Conditional("DEVELOPMENT_BUILD")]
        public static void LogComplete(string message)
        {
            Log($"🎯 {message}");
        }
        #endregion

        #region 유틸리티 메소드
        /// <summary>
        /// 로그 메시지를 포맷팅합니다.
        /// </summary>
        /// <param name="message">원본 메시지</param>
        /// <param name="logType">로그 타입</param>
        /// <returns>포맷팅된 메시지</returns>
        private static string FormatMessage(string message, LogType logType)
        {
            string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
            string typePrefix = GetLogTypePrefix(logType);
            
            return $"{LOG_PREFIX} [{timestamp}] {typePrefix} {message}";
        }

        /// <summary>
        /// 로그 타입에 따른 접두사를 가져옵니다.
        /// </summary>
        /// <param name="logType">로그 타입</param>
        /// <returns>접두사 문자열</returns>
        private static string GetLogTypePrefix(LogType logType)
        {
            switch (logType)
            {
                case LogType.Error:
                    return "[ERROR]";
                case LogType.Assert:
                    return "[ASSERT]";
                case LogType.Warning:
                    return "[WARNING]";
                case LogType.Log:
                    return "[INFO]";
                case LogType.Exception:
                    return "[EXCEPTION]";
                default:
                    return "[UNKNOWN]";
            }
        }

        /// <summary>
        /// 로그를 파일에 저장합니다.
        /// </summary>
        /// <param name="message">로그 메시지</param>
        /// <param name="logType">로그 타입</param>
        private static void WriteToFile(string message, LogType logType)
        {
            try
            {
                string logEntry = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff}] {GetLogTypePrefix(logType)} {message}\n";
                File.AppendAllText(LOG_FILE_PATH, logEntry);
            }
            catch (Exception e)
            {
                // 파일 로깅 실패는 콘솔에만 출력
                UnityEngine.Debug.LogError($"파일 로깅 실패: {e.Message}");
            }
        }

        /// <summary>
        /// 로그 파일을 정리합니다.
        /// </summary>
        public static void ClearLogFile()
        {
            try
            {
                if (File.Exists(LOG_FILE_PATH))
                {
                    File.Delete(LOG_FILE_PATH);
                    Log("로그 파일이 정리되었습니다.");
                }
            }
            catch (Exception e)
            {
                LogError($"로그 파일 정리 실패: {e.Message}");
            }
        }

        /// <summary>
        /// 로그 파일 경로를 가져옵니다.
        /// </summary>
        /// <returns>로그 파일 경로</returns>
        public static string GetLogFilePath()
        {
            return LOG_FILE_PATH;
        }
        #endregion

        #region Unity Editor 전용 메소드
#if UNITY_EDITOR
        /// <summary>
        /// Unity Console 창을 정리합니다.
        /// </summary>
        [Conditional("UNITY_EDITOR")]
        public static void ClearConsole()
        {
            var assembly = System.Reflection.Assembly.GetAssembly(typeof(UnityEditor.Editor));
            var type = assembly.GetType("UnityEditor.LogEntries");
            var method = type.GetMethod("Clear");
            method.Invoke(new object(), null);
            
            Log("Unity Console이 정리되었습니다.");
        }

        /// <summary>
        /// Editor에서 진행률을 표시합니다.
        /// </summary>
        /// <param name="title">제목</param>
        /// <param name="info">정보</param>
        /// <param name="progress">진행률 (0~1)</param>
        [Conditional("UNITY_EDITOR")]
        public static void DisplayProgressBar(string title, string info, float progress)
        {
            UnityEditor.EditorUtility.DisplayProgressBar(title, info, progress);
        }

        /// <summary>
        /// 진행률 표시를 종료합니다.
        /// </summary>
        [Conditional("UNITY_EDITOR")]
        public static void ClearProgressBar()
        {
            UnityEditor.EditorUtility.ClearProgressBar();
        }
#endif
        #endregion
    }
} 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dannect Unity Toolkit Enums
액션 타입과 기타 열거형 정의
"""

from enum import Enum


class ActionType(Enum):
    """실행 가능한 액션 타입들 - Unity 패키지와 연동"""
    # 기본 Unity CLI 액션 (Unity 패키지 메소드와 매핑)
    ALL_TEST = "all_test"
    CREATE_BUTTON = "create_button"
    TEST_BUTTON = "test_button"
    DEBUG_POPUP = "debug_popup"
    CHECK_EVENTS = "check_events"
    PROJECT_INFO = "project_info"
    
    # 고급 빌드 및 자동화 액션
    BUILD_WEBGL = "build_webgl"
    BUILD_WEBGL_PARALLEL = "build_webgl_parallel"
    CLEAN_BUILDS = "clean_builds"
    PACKAGE_UPDATE = "package_update"
    PACKAGE_FORCE_UPDATE = "package_force_update"
    
    # Git 자동화 액션
    GIT_COMMIT = "git_commit"
    GIT_AUTO_BRANCH = "git_auto_branch"
    
    # Unity 배치 처리
    UNITY_BATCH = "unity_batch"
    UNITY_BATCH_PARALLEL = "unity_batch_parallel"
    
    # SystemManager 관련
    ADD_SYSTEM_METHOD = "add_system_method"
    
    # 유틸리티 액션
    CREATE_CONFIG = "create_config"
    CREATE_PROJECTS_FILE = "create_projects_file"
    SAVE_PROJECT_LIST = "save_project_list"


class WorkflowType(Enum):
    """사전 정의된 워크플로우들"""
    FULL_AUTOMATION = "full_automation"
    WEBGL_BUILD_WORKFLOW = "webgl_build_workflow"
    GIT_AUTOMATION_WORKFLOW = "git_automation_workflow"


class BuildTarget(Enum):
    """빌드 타겟 플랫폼"""
    WEBGL = "WebGL"
    WINDOWS = "StandaloneWindows64"
    MAC = "StandaloneOSX"
    LINUX = "StandaloneLinux64"
    ANDROID = "Android"
    IOS = "iOS"


class LogLevel(Enum):
    """로그 레벨"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class UnityVersion(Enum):
    """지원하는 Unity 버전"""
    UNITY_2022_3 = "2022.3"
    UNITY_2023_2 = "2023.2"
    UNITY_6 = "6000.0"


# Unity CLI 메소드 매핑 (Unity 패키지와 연동)
UNITY_CLI_METHODS = {
    ActionType.ALL_TEST: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_AllInOneRebuildButtonTest",
    ActionType.CREATE_BUTTON: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_CreateRebuildButton", 
    ActionType.TEST_BUTTON: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_TestRebuildButtonClick",
    ActionType.DEBUG_POPUP: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_DebugFindSuccessPop",
    ActionType.CHECK_EVENTS: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_CheckRebuildButtonEvents",
    ActionType.PROJECT_INFO: "Dannect.Unity.Toolkit.Editor.DannectToolkitMenuItems.CLI_TestCLIMode",
    ActionType.BUILD_WEBGL: "Dannect.Unity.Toolkit.Editor.DannectToolkitEditorCore.BuildWebGL"
}

# Unity Editor 기본 경로들
DEFAULT_UNITY_PATHS = [
    r"C:\Program Files\Unity\Hub\Editor",
    r"C:\Program Files (x86)\Unity\Hub\Editor", 
    r"D:\Unity\Hub\Editor",
    r"E:\Unity\Hub\Editor",
    r"D:\Unity",  # 직접 설치된 Unity
    r"C:\Unity",
    "/Applications/Unity/Hub/Editor"  # macOS
] 
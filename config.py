#!/usr/bin/env python3
"""
Android Pentesting Suite - Configuration
All constants, paths, and timeouts
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TIMEOUTS (in seconds)
# ═══════════════════════════════════════════════════════════════════════════════
ADB_TIMEOUT = 30
ADB_DEVICES_TIMEOUT = 10
EXTRACTION_TIMEOUT = 600  # 10 minutes for app data extraction
FRIDA_TIMEOUT = 60
BACKUP_RESTORE_TIMEOUT = 300  # 5 minutes
FRIDUMP_TIMEOUT = 300  # 5 minutes
COMMAND_TIMEOUT = 30

# ═══════════════════════════════════════════════════════════════════════════════
# DIRECTORIES
# ═══════════════════════════════════════════════════════════════════════════════
TOOLS_DIR = "./tools"
OUTPUT_DIR = "./output"
FRIDUMP_OUTPUT_DIR = "./output/fridump"
APKLEAKS_OUTPUT_DIR = "./output/apkleaks"
DECOMPILED_OUTPUT_DIR = "./output/decompiled"
APPDATA_OUTPUT_DIR = "./output/appdata"
OBJECTION_OUTPUT_DIR = "./output/objection"
BACKUP_OUTPUT_DIR = "./output/backup"
LOGCAT_OUTPUT_DIR = "./output"

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL PATHS (relative to TOOLS_DIR)
# ═══════════════════════════════════════════════════════════════════════════════
JADX_PATH = "jadx-1.5.2/bin/jadx"
JADX_PATH_WIN = "jadx-1.5.2/bin/jadx.bat"
FRIDUMP_SCRIPT = "fridump/fridump.py"
APK_COMPONENTS_INSPECTOR = "apk-components-inspector/apk-components-inspector.py"
FRIDA_SCRIPT_GEN = "frida-script-gen/frida-script-gen.py"
MOBAPP_STORAGE_INSPECTOR = "MobApp-Storage-Inspector.jar"
BURP_CERTIFICATE = "9a5ba575.0"
FRIDA_SERVER_DIR = "frida-server"

# ═══════════════════════════════════════════════════════════════════════════════
# ANDROID SDK PATHS
# ═══════════════════════════════════════════════════════════════════════════════
ANDROID_SDK_DIR = "android-sdk"
CMDLINE_TOOLS_DIR = "cmdline-tools/latest/bin"
AVD_MANAGER = "avdmanager.bat"
SDK_MANAGER = "sdkmanager.bat"
EMULATOR_PATH = "emulator/emulator.exe"

# ═══════════════════════════════════════════════════════════════════════════════
# DEVICE PATHS
# ═══════════════════════════════════════════════════════════════════════════════
DEVICE_FRIDA_SERVER_PATH = "/data/local/tmp/frida-server"
DEVICE_CERT_PATH = "/system/etc/security/cacerts/"
DEVICE_SDCARD = "/sdcard/"
DEVICE_DATA_DIR = "/data/data/"

# ═══════════════════════════════════════════════════════════════════════════════
# FRIDA SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
FRIDA_RELEASES_API = "https://api.github.com/repos/frida/frida/releases"
MAX_FRIDA_VERSIONS = 10
FRIDA_MAX_MEMORY_REGIONS = 50
FRIDA_MAX_REGION_SIZE = 20971520  # 20MB

# ═══════════════════════════════════════════════════════════════════════════════
# APK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
TRUFFLEHOG_CMD = "trufflehog"

# ═══════════════════════════════════════════════════════════════════════════════
# DEEP LINK SECURITY TESTING
# ═══════════════════════════════════════════════════════════════════════════════
DEEPLINK_OUTPUT_DIR = "./output/deeplink"
DEEPLINK_TEST_TIMEOUT = 5  # seconds per test

# Deep Link Test Categories and Payloads
DEEPLINK_TEST_PAYLOADS = {
    "open_redirect": [
        ("url_param", "?url=https://evil.com"),
        ("redirect_param", "?redirect=https://evil.com"),
        ("next_param", "?next=//evil.com"),
        ("callback_param", "?callback=https://evil.com"),
        ("return_param", "?return_url=https://evil.com"),
        ("goto_param", "?goto=https://evil.com"),
        ("dest_param", "?dest=https://evil.com"),
        ("target_param", "?target=https://evil.com"),
    ],
    "xss_injection": [
        ("js_alert", "?url=javascript:alert(1)"),
        ("js_document", "?page=javascript:alert(document.domain)"),
        ("html_img", "?content=<img src=x onerror=alert(1)>"),
        ("html_script", "?data=<script>alert(1)</script>"),
        ("encoded_js", "?url=javascript%3Aalert(1)"),
    ],
    "path_traversal": [
        ("basic_traversal", "?path=../../../etc/passwd"),
        ("double_dot", "?file=....//....//etc/passwd"),
        ("encoded_traversal", "?path=%2e%2e%2f%2e%2e%2fetc/passwd"),
        ("null_byte", "?file=../../../etc/passwd%00.jpg"),
    ],
    "sql_injection": [
        ("basic_sqli", "?id=1' OR '1'='1"),
        ("union_sqli", "?id=1 UNION SELECT * FROM users--"),
        ("comment_sqli", "?q=test'--"),
        ("boolean_sqli", "?id=1 AND 1=1"),
    ],
    "auth_bypass": [
        ("admin_path", "/admin"),
        ("settings_path", "/settings"),
        ("debug_path", "/debug"),
        ("config_path", "/config"),
        ("internal_path", "/internal"),
        ("user_path", "/user?id=1"),
        ("profile_path", "/profile?admin=true"),
    ],
    "file_access": [
        ("file_scheme", "?url=file:///etc/passwd"),
        ("content_scheme", "?uri=content://com.app.provider/data"),
        ("data_dir", "?path=file:///data/data/"),
        ("shared_prefs", "?file=file:///data/data/{package}/shared_prefs/"),
    ],
    "intent_injection": [
        ("component_injection", "#Intent;component={package}/.DebugActivity;end"),
        ("selector_bypass", "#Intent;SEL;component={package}/.SecretActivity;end"),
        ("extra_bool", "#Intent;B.admin=true;end"),
        ("extra_string", "#Intent;S.token=malicious;end"),
        ("flag_grant_read", "#Intent;launchFlags=0x1;end"),
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# VERSION
# ═══════════════════════════════════════════════════════════════════════════════
VERSION = "2.5.0"
AUTHOR = "Jai"

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT VALIDATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
import os
import re

def validate_package_name(package: str) -> tuple[bool, str]:
    """
    Validate Android package name format.
    Returns (is_valid, error_message)
    """
    if not package:
        return False, "Package name cannot be empty"
    
    if len(package) > 255:
        return False, "Package name too long (max 255 chars)"
    
    # Android package name rules: lowercase, dots, underscores, numbers
    # Must have at least one dot, start with letter
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$'
    if not re.match(pattern, package):
        return False, "Invalid package format. Use: com.example.app"
    
    return True, ""


def validate_file_path(path: str, must_exist: bool = True, file_type: str = None) -> tuple[bool, str]:
    """
    Validate file path.
    Args:
        path: File path to validate
        must_exist: If True, checks file exists
        file_type: Expected extension (e.g., '.apk')
    Returns (is_valid, error_message)
    """
    if not path:
        return False, "File path cannot be empty"
    
    if len(path) > 500:
        return False, "File path too long"
    
    # Check for dangerous characters (command injection prevention)
    dangerous_chars = ['|', '&', ';', '$', '`', '>', '<', '\\n', '\\r']
    for char in dangerous_chars:
        if char in path:
            return False, f"Invalid character in path: {char}"
    
    if must_exist and not os.path.exists(path):
        return False, f"File not found: {path}"
    
    if file_type and not path.lower().endswith(file_type.lower()):
        return False, f"Expected {file_type} file, got: {path}"
    
    return True, ""


def validate_device_id(device_id: str) -> tuple[bool, str]:
    """
    Validate ADB device ID format.
    Returns (is_valid, error_message)
    """
    if not device_id:
        return True, ""  # Empty is OK (will auto-detect)
    
    if len(device_id) > 100:
        return False, "Device ID too long"
    
    # Allow emulator-5554, IP:port, or serial numbers
    pattern = r'^[a-zA-Z0-9._:\-]+$'
    if not re.match(pattern, device_id):
        return False, "Invalid device ID format"
    
    return True, ""


def validate_remote_path(path: str) -> tuple[bool, str]:
    """
    Validate Android device path.
    Returns (is_valid, error_message)
    """
    if not path:
        return False, "Remote path cannot be empty"
    
    if len(path) > 500:
        return False, "Path too long"
    
    # Must start with /
    if not path.startswith('/'):
        return False, "Android path must start with /"
    
    # Check for command injection characters
    dangerous_chars = ['|', '&', ';', '$', '`', '>', '<']
    for char in dangerous_chars:
        if char in path:
            return False, f"Invalid character in path: {char}"
    
    return True, ""


def validate_integer(value: str, min_val: int = None, max_val: int = None, default: int = None) -> tuple[bool, int, str]:
    """
    Validate and convert string to integer.
    Returns (is_valid, parsed_value, error_message)
    """
    if not value:
        if default is not None:
            return True, default, ""
        return False, 0, "Value cannot be empty"
    
    try:
        num = int(value)
    except ValueError:
        return False, 0, f"Invalid number: {value}"
    
    if min_val is not None and num < min_val:
        return False, 0, f"Value must be at least {min_val}"
    
    if max_val is not None and num > max_val:
        return False, 0, f"Value must be at most {max_val}"
    
    return True, num, ""


def validate_yes_no(value: str, default: bool = False) -> bool:
    """
    Validate yes/no input and return boolean.
    """
    if not value:
        return default
    return value.lower().strip() in ('y', 'yes', 'true', '1')


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing dangerous characters.
    """
    # Remove path separators and dangerous chars
    dangerous = ['/', '\\', '..', '|', '&', ';', '$', '`', '>', '<', '\n', '\r', '\0']
    result = filename
    for char in dangerous:
        result = result.replace(char, '_')
    return result[:255]  # Max filename length
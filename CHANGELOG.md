# Changelog

All notable changes to Android Pentesting Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.6.0] - 2026-01-08

### Added
- **🤖 AI Security Analyzer** - NEW FEATURE
  - AI-powered source code analysis for security vulnerabilities
  - Supports Ollama (local, free) and OpenAI API
  - Detects: hardcoded secrets, insecure crypto, SQL injection, WebView issues, etc.
  - Generates detailed reports with severity, CWE IDs, and recommendations
  - Auto-prioritizes security-relevant files (MainActivity, LoginActivity, etc.)
  - Export findings as JSON or text report
- New menu option `[30] AI Security Analyzer`
- New module `ai_analyzer.py` with `AISecurityAnalyzer` class

### Dependencies (optional)
- `requests` - For Ollama API (local)
- `openai` - For OpenAI API (cloud)

## [2.5.3] - 2026-01-08

### Added
- **Config Persistence** - Settings now saved between sessions
  - `SessionConfig` class stores user preferences to `.session_config.json`
  - Remembers: last APK path, last package name, device IP, output dir
  - Press Enter to reuse last value when prompted
- Shows saved settings on startup

### Changed
- `require_package_name()` now supports `config_key` for persistence
- `require_file_path()` now supports `config_key` for persistence
- Prompts show last used value in brackets: `Enter APK path [/last/path.apk]:`

## [2.5.2] - 2026-01-08

### Added
- Ctrl+C (KeyboardInterrupt) graceful handling - no more crashes
- `signal_handler()` for clean exit on interrupt
- `safe_input()` helper with empty check and interrupt handling
- `check_device_connection()` helper for device validation
- `require_package_name()` helper with validation
- `require_file_path()` helper with validation

### Changed
- Main loop now wrapped in try/except for stability
- Updated handlers to use new stability helpers
- Better error messages for missing device/invalid input

### Fixed
- Empty input handling in menu selection
- Keyboard interrupt now handled gracefully throughout
- Device connection errors no longer crash the app

## [2.5.1] - 2026-01-08

### Changed
- Refactored `main.py` into modular structure with 29 handler functions
- Added proper section headers and documentation
- Single source of truth for VERSION constant

### Added
- Progress bar for downloads (SDK, JADX, Frida server)
- Tab completion for file paths (requires readline/pyreadline3)

### Fixed
- sdkmanager/avdmanager detection on Windows (.bat extension)
- Duplicate print statements in Deep Link tester

### Removed
- Empty batch files (launch_pentest_emulator.bat, check_emulator_status.bat, setup_env.bat)

## [2.5.0] - 2026-01-07

### Added
- **Deep Link Security Tester (Option 29)**
  - Extract deep links from AndroidManifest.xml
  - 7 attack categories: Open Redirect, XSS, Path Traversal, SQLi, Auth Bypass, File Access, Intent Injection
  - Full Test Mode (with device) + Offline Analysis Mode (no device required)
  - Auto-discover decompiled manifest from common folder patterns
  - Auto-decompile APK using apktool if manifest not found
  - Risk assessment with severity ratings (HIGH/MEDIUM/LOW)
  - JSON reports + ADB shell script generation
  - Filters invalid `@string/` references and deduplicates findings

### Changed
- Updated menu to 30 options
- Improved input validation and error handling

## [2.0.0] - 2025-08-06

### Added
- Sensitive Strings/Secrets Finder (Option 25)
- Automated Backup/Restore (Option 26)
- App Repackaging Utility (Option 27)
- Automated Uninstall/Cleaner (Option 28)

### Fixed
- All menu options now have corresponding, fully implemented methods
- Improved error handling and user feedback

## [1.0.0] - 2025-01-01

### Added
- Initial release
- 24 core pentesting features
- Menu-driven interface
- ADB operations (install, uninstall, push, pull)
- Device management and emulator support
- APK analysis (APKTool, JADX, APKLeaks)
- Frida server setup and memory dumping
- Objection testing suite integration
- Burp Suite certificate installation

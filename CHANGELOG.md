# Changelog

All notable changes to Android Pentesting Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

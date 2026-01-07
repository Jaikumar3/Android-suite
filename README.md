# Android Pentesting Suite

**Author:** Jai  
**Version:** 2.5.0

## Overview

This suite automates Android app pentesting and reverse engineering tasks. It provides a menu-driven interface for installing tools, managing emulators, interacting with devices, and running common security tests.

## Features

The suite provides the following **30 features** via its menu:

1. **Install/verify tools (open installer):** Install or verify all required tools in the ./tools directory.
2. **Check emulator root status:** Check if connected emulator has root access and writable system partition.
3. **Setup emulator (Play Store + Root):** Guide to setup Android emulator with Play Store and root access.
4. **Get PID for package name:** Find the process ID for a given Android package name.
5. **Install APK via ADB:** Install an APK file to the connected Android device using ADB.
6. **Uninstall APK via ADB:** Uninstall an app from the device using its package name.
7. **Push file to device via ADB:** Copy a file from your computer to the Android device.
8. **Pull file from device via ADB:** Copy a file from the Android device to your computer.
9. **Collect device information:** Gather information about the connected Android device.
10. **Setup Frida server (interactive):** Interactive setup with version selection from GitHub releases.
11. **Stop Frida server on device:** Stop/kill the Frida server process on the device.
12. **Get process list:** List all running processes on the device.
13. **View/Save Logcat Output:** View or save the device's logcat output.
14. **List installed packages:** List all installed package names on the connected device.
15. **Dump app memory with fridump:** Dump running app memory using fridump and Frida (requires package name/PID).
16. **APKTool decompile APK:** Decompile an APK using APKTool.
17. **Run APKLeaks on APK:** Scan an APK for secrets using APKLeaks.
18. **Extract app data directory:** Extract the /data/data/<package> directory from the device (root required, 10min timeout with extension option).
19. **Run apk-components-inspector on APK:** Analyze APK components using apk-components-inspector.
20. **Run frida-script-gen (generate Frida scripts):** Generate Frida scripts using frida-script-gen tool.
21. **Run MobApp-Storage-Inspector on APK:** Analyze APK storage using MobApp-Storage-Inspector.jar.
22. **Setup Burp Suite CA certificate:** Install Burp Suite CA certificate to Android device/emulator for HTTPS interception.
23. **Objection Testing Suite:** Comprehensive Android app testing with Objection framework.
24. **Create/Launch AVD with Magisk+Xposed (root, writable):** Automate AVD creation and patching with Magisk and Xposed, with writable system and root.
25. **Sensitive Strings/Secrets Finder:** Scan APK or decompiled code for sensitive strings, secrets, and credentials.
26. **Automated Backup/Restore:** Backup and restore app data using ADB (root required for some apps).
27. **App Repackaging Utility:** Repackage APKs after modification for testing or bypassing protections.
28. **Automated Uninstall/Cleaner:** Uninstall app and optionally clean up related files and data.
29. **Deep Link Security Tester:** Test deep links for Open Redirect, XSS, Path Traversal, SQL Injection, Auth Bypass, and Intent Injection vulnerabilities.
30. **Exit:** Exit the Android Suite.

## Deep Link Security Tester (Option 29)

### Features
- **Extract deep links** from AndroidManifest.xml (auto-discovers decompiled folder or auto-decompiles APK)
- **7 payload categories** with 35+ test cases:
  - Open Redirect (8 payloads)
  - XSS Injection (5 payloads)
  - Path Traversal (4 payloads)
  - SQL Injection (4 payloads)
  - Auth Bypass (7 payloads)
  - File Access (4 payloads)
  - Intent Injection (5 payloads)
- **Two testing modes:**
  - **Full Test Mode** - Requires device/emulator, executes ADB commands, analyzes logcat for vulnerabilities
  - **Offline Analysis Mode** - No device required, generates reconnaissance report with ADB commands for manual testing
- **Auto-discovery** - Finds decompiled AndroidManifest.xml automatically
- **Auto-decompile** - Runs apktool if no manifest found
- **Risk assessment** - Categorizes findings by severity (HIGH/MEDIUM/LOW)
- **Output** - JSON reports + shell scripts with ADB test commands

### Usage
```python
from android_pentest import AndroidPentester
p = AndroidPentester()

# Offline mode - just APK path (auto-discovers/decompiles manifest)
p.run_deeplink_offline_analysis(apk_path=r'path\to\app.apk')

# Full test mode - requires connected device
p.run_deeplink_security_test(apk_path=r'path\to\app.apk')
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Jaikumar3/Android-suite.git
cd Android-suite

# Install Python dependencies
pip install -r requirements.txt

# Run the tool
python main.py
```

### First Run
1. Select **Option 1** to install/verify all required tools
2. Connect your Android device or start an emulator
3. Select any option (2-29) to start pentesting

## Installer Options

When you select "Install/verify tools" from the menu, you’ll see these options:

1. **Standard installation:** Python packages + Android SDK
2. **Install Android Studio Command Line Tools**
3. **Install Android Emulator with AVD**
4. **Install full Android Studio IDE**
5. **Full installation (everything)**
6. **Verify existing installation**
7. **Default installer**
8. **Recommended installation (best-practice setup)**

The recommended installation sets up the most common tools and a preconfigured Android 12L (Sv2) x86_64 AVD with Google APIs.

## Tool List

- **Android SDK, Emulator, AVD**
- **Frida, Objection, APKTool, JADX, APKLeaks**
- **MobApp-Storage-Inspector, Quark-Engine, APKiD**
- **Burp Suite CA certificate automation**
- **Magisk + Xposed for rooted/writable emulators**

## Usage Examples

- **Check emulator root status**
- **Install/uninstall APKs via ADB**
- **Extract app data directory**
- **Run Frida/Objection tests**
- **Decompile APKs and scan for secrets**
- **Install Burp Suite CA certificate for HTTPS interception**

## Requirements

- Windows, macOS, or Linux
- Python 3.8+
- Java 17+ (for MobApp-Storage-Inspector)
- Android SDK tools (installed via suite)

## Troubleshooting

- If color output is missing, ensure `colorama` is installed (`pip install colorama`).
- For Java-based tools, install Java 17+ from [Adoptium](https://adoptium.net/).
- For Frida/Objection, ensure device is rooted or use an emulator.

## Contributing

Pull requests and suggestions are welcome!

## License

MIT License

## Changelog

### [2.5.0] - 2026-01-07
- **NEW:** Deep Link Security Tester (Option 29)
  - Extract deep links from AndroidManifest.xml
  - 7 attack categories: Open Redirect, XSS, Path Traversal, SQLi, Auth Bypass, File Access, Intent Injection
  - Full Test Mode (with device) + Offline Analysis Mode (no device required)
  - Auto-discover decompiled manifest from common folder patterns
  - Auto-decompile APK using apktool if manifest not found
  - Risk assessment with severity ratings (HIGH/MEDIUM/LOW)
  - JSON reports + ADB shell script generation
  - Filters invalid `@string/` references and deduplicates findings
- Updated menu to 30 options
- Improved input validation and error handling

### [2.0.0] - 2025-08-06
- Added features 25-28:
  - Sensitive Strings/Secrets Finder
  - Automated Backup/Restore
  - App Repackaging Utility
  - Automated Uninstall/Cleaner
- Fixed: All menu options now have corresponding, fully implemented methods
- Improved error handling and user feedback

---

**For more details, see the in-app help menu or comments in `main.py` and `installer.py`.**

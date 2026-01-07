# Streamlined Android Pentesting Tools Installer

The installer has been reorganized into **2 simple options** for easy setup:

## 🚀 Quick Start

### Option 1: Install All Tools (Recommended)
```bash
python installer.py --all-tools
```
**Installs everything in one shot:**
- Python packages (requests, colorama, lxml, beautifulsoup4, frida-tools, objection, androguard, adb-shell)
- Android SDK Platform Tools (ADB)
- Reverse Engineering Tools (JADX, apk-components-inspector)
- Pentesting Tools (APKTool, APKLeaks, APKiD, Quark-Engine, MobApp-Storage-Inspector)
- Additional analysis tools

### Option 2: Install Emulator Only
```bash
python installer.py --emulator
```
**Installs Android Emulator setup:**
- Android SDK CLI Tools
- Android Emulator
- Pre-configured pentesting AVDs (Android 12L Sv2)
- Optimized settings for pentesting

## 🔍 Verification
```bash
python installer.py --verify-only
```
Check what's already installed and working.

## 📁 Custom Tools Directory
```bash
python installer.py --all-tools --tools-dir /path/to/custom/tools
```

## 🎯 What's New

**Before:** 12+ confusing options (--minimal, --standard, --full, --frida-only, --android-studio, --android-emulator, --android-studio-full, --pentest-tools, --reverse-engineering, --recommended, etc.)

**Now:** Just **2 main options**:
1. `--all-tools` - Complete pentesting setup
2. `--emulator` - Emulator-only setup

**Benefits:**
- ✅ Simplified decision-making
- ✅ Faster setup (6-step process with clear progress)
- ✅ All tools in one shot
- ✅ Better error handling
- ✅ Automatic dependency resolution

## 📋 Installation Progress

When you run `--all-tools`, you'll see:
```
Step 1/5: Installing Python packages...
Step 2/5: Installing Android SDK tools...
Step 3/5: Installing reverse engineering tools...
Step 4/5: Installing pentesting tools...
Step 5/5: Installing additional tools...
```

## 🛠️ Post-Installation

After successful installation:
1. Run `setup_env.bat` (Windows) or `setup_env.sh` (Unix) to configure environment
2. Use `python main.py` to access the Android Pentesting Suite
3. All 24 menu options will be fully functional
4. **Note:** Frida server installation is handled through Option 14 in the main menu

## 🎁 Bonus: Option 19 Fixed!

The `apk-components-inspector` (Option 19) is now fully functional with proper dependency management including the missing `requests` package.

## 📝 Important Notes

- **Frida Server Installation:** Frida server binaries and related tools (fridump, frida-script-gen) are installed through **Option 14** in the main menu (`python main.py`), not through the installer
- **Dynamic Analysis Tools:** Use the main menu for Frida server setup and dynamic analysis tool installation
- **Static Analysis:** The installer focuses on static analysis tools and basic setup

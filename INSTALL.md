# Android Pentesting Tools - Installation Guide

## Quick Installation

### Option 1: Standard Installation (Recommended)
```bash
python installer.py --standard
```
**Includes:**
- Python packages (requests, colorama, lxml, beautifulsoup4, frida-tools, objection)
- Android SDK Platform Tools (ADB, Fastboot)
- JADX decompiler

### Option 2: Full Installation
```bash
python installer.py --full
```
**Includes everything from Standard plus:**
- Frida server binaries for all Android architectures
- Additional tools: fridump, APKiD, Quark-Engine
- All optional components

### Option 3: Minimal Installation
```bash
python installer.py --minimal
```
**Includes only:**
- Essential Python packages (requests, colorama)
- Use when you have existing Android tools

### Option 4: Frida-Only Installation
```bash
python installer.py --frida-only
```
**Includes:**
- frida-tools and objection
- Frida server binaries for Android devices

## Post-Installation

### 1. Set Up Environment
Run the generated environment script:
```bash
# Windows
setup_env.bat

# Linux/macOS
./setup_env.sh
```

### 2. Verify Installation
```bash
python installer.py --verify-only
```

### 3. Start Using the Tool
```bash
python main.py --apk your_app.apk --name com.example.app --install-deps
```

## Manual Installation Alternative

If you prefer manual setup:

```bash
# Install Python packages
pip install -r requirements.txt

# Download Android SDK Platform Tools manually
# From: https://developer.android.com/studio/releases/platform-tools

# Download JADX manually  
# From: https://github.com/skylot/jadx/releases

# Add tools to your system PATH
```

## Troubleshooting

### Common Issues

**ADB not found:**
- Ensure Android SDK Platform Tools are installed
- Add platform-tools directory to PATH
- Run `adb version` to verify

**Frida connection issues:**
- Ensure USB debugging is enabled on device
- Check device is connected: `adb devices`
- Push frida-server to device manually if needed

**Permission errors:**
- Run installer with appropriate permissions
- On Linux/macOS: `chmod +x setup_env.sh`

**Python package conflicts:**
- Use virtual environment: `python -m venv android_pentest`
- Activate: `android_pentest\Scripts\activate` (Windows) or `source android_pentest/bin/activate` (Linux/macOS)
- Then run installer

### Getting Help

1. Check installation report: `installation_report.json`
2. Verify tools: `python installer.py --verify-only`
3. Check system PATH includes tool directories
4. Ensure Android device has USB debugging enabled

## Tool Locations

After installation, tools are located in:
- `./tools/platform-tools/` - ADB and Fastboot
- `./tools/jadx-*/bin/` - JADX decompiler
- `./tools/frida-server/` - Frida server binaries
- `./tools/fridump/` - Memory dumping tool
- System Python packages - Frida tools, Objection, etc.

## Environment Variables

The installer creates scripts that set:
- PATH includes platform-tools and JADX
- TOOLS_DIR points to tools installation directory

Make these permanent by adding to your shell profile (.bashrc, .zshrc, etc.)

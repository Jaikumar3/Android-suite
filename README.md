
# Android Suite 

A menu-driven Python tool to automate common Android application and device pentesting tasks. Designed for security professionals, researchers, and enthusiasts, it centralizes device interaction, APK analysis, Frida integration, and more into a single, easy-to-use interface.

## Features

- **Install/verify tools**: One-click setup for all required tools (ADB, APKTool, Frida, APKLeaks, fridump, etc.)
- **Get PID for package name**: Find the process ID for any installed app
- **Install/Uninstall APK via ADB**: Quickly install or remove APKs
- **Push/Pull files via ADB**: Transfer files between your computer and the device
- **Collect device information**: Gather device model, OS, root status, and more
- **Setup/Stop Frida server**: Automate Frida server deployment and management (with version checks)
- **Get process list**: List all running processes on the device
- **View/Save Logcat Output**: Fetch and save device logs, with filtering and line limits
- **List installed packages**: List all package names on the device
- **Dump APK with fridump**: Memory dump of an app using Frida and fridump
- **APKTool decompile APK**: Decompile APKs for static analysis
- **Run APKLeaks on APK**: Scan APKs for secrets and sensitive data
- **Extract app data directory**: Pull `/data/data/<package>` (root required)
- **Colorful, user-friendly menu**: All output is colorized for clarity (if `colorama` is installed)
- **Help and input validation**: Built-in help, error handling, and input checks

## Requirements

- Python 3.7+
- [ADB](https://developer.android.com/studio/command-line/adb) (Android Debug Bridge)
- [colorama](https://pypi.org/project/colorama/) (optional, for color output)
- Internet connection (for installer to fetch tools)

## Setup

1. **Clone or download this repository**
2. (Optional) Create a Python virtual environment:
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```
3. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the installer to fetch all tools:**
   ```sh
   python main.py
   # Then select option 1: Install/verify tools
   ```

## Usage

Run the main menu:
```sh
python main.py
```

You will see a colorized menu with 17 options. Select a number to perform the corresponding action. Use 'h' for help, 'b' to return, or '0'/'17' to exit.

### Example Menu
```
[  1]  Install/verify tools (open installer)
[  2]  Get PID for package name
[  3]  Install APK via ADB
[  4]  Uninstall APK via ADB
[  5]  Push file to device via ADB
[  6]  Pull file from device via ADB
[  7]  Collect device information
[  8]  Setup Frida server (optional)
[  9]  Stop Frida server on device
[ 10]  Get process list
[ 11]  View/Save Logcat Output
[ 12]  List installed packages
[ 13]  Dump APK with fridump
[ 14]  APKTool decompile APK
[ 15]  Run APKLeaks on APK
[ 16]  Extract app data directory
[ 17]  Exit
```

## Notes
- All command logic is in `android_pentest.py`; `main.py` is menu/UI only.
- The installer will fetch and set up all required tools in the `tools/` directory.
- Frida server version is checked to match the host Frida tools exactly.
- Most features work with any connected Android device (root required for some options).
- Output is colorized if `colorama` is installed.

## Troubleshooting
- If a tool is missing or fails to install, rerun the installer (option 1).
- For Frida features, ensure your device is rooted and USB debugging is enabled.
- For APK analysis, provide the full path to the APK file when prompted.

## Contributing
Pull requests and suggestions are welcome! Please open an issue for bugs or feature requests.

## License
MIT License

```


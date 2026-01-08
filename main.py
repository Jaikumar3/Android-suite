#!/usr/bin/env python3
"""
Android Pentesting Automation Script
Main entry point for the automation tool

Author: Jai
Version: 2.5.0
"""

# =============================================================================
# IMPORTS
# =============================================================================

import sys
import os
import argparse
import subprocess

# Local imports
from android_pentest import AndroidPentester
import config

# =============================================================================
# OPTIONAL IMPORTS (graceful degradation)
# =============================================================================

# Colorama for colored output
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False

# Readline for tab completion
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    try:
        import pyreadline3 as readline
        READLINE_AVAILABLE = True
    except ImportError:
        READLINE_AVAILABLE = False

# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = "2.5.0"
AUTHOR = "Jai"

MENU_OPTIONS = [
    ("Install/verify tools (open installer)", "Install or verify all required tools in the ./tools directory."),
    ("Check emulator root status", "Check if connected emulator has root access and writable system partition."),
    ("Setup emulator (Play Store + Root)", "Guide to setup Android emulator with Play Store and root access."),
    ("Get PID for package name", "Find the process ID for a given Android package name."),
    ("Install APK via ADB", "Install an APK file to the connected Android device using ADB."),
    ("Uninstall APK via ADB", "Uninstall an app from the device using its package name."),
    ("Push file to device via ADB", "Copy a file from your computer to the Android device."),
    ("Pull file from device via ADB", "Copy a file from the Android device to your computer."),
    ("Collect device information", "Gather information about the connected Android device."),
    ("Setup Frida server (interactive)", "Interactive setup with version selection from GitHub releases."),
    ("Stop Frida server on device", "Stop/kill the Frida server process on the device."),
    ("Get process list", "List all running processes on the device."),
    ("View/Save Logcat Output", "View or save the device's logcat output."),
    ("List installed packages", "List all installed package names on the connected device."),
    ("Dump app memory with fridump", "Dump running app memory using fridump and Frida (requires package name/PID)."),
    ("APKTool decompile APK", "Decompile an APK using APKTool."),
    ("Run APKLeaks on APK", "Scan an APK for secrets using APKLeaks."),
    ("Extract app data directory", "Extract the /data/data/<package> directory from the device (root required)."),
    ("Run apk-components-inspector on APK", "Analyze APK components using apk-components-inspector."),
    ("Run frida-script-gen (generate Frida scripts)", "Generate Frida scripts using frida-script-gen tool."),
    ("Run MobApp-Storage-Inspector on APK", "Analyze APK storage using MobApp-Storage-Inspector.jar."),
    ("Setup Burp Suite CA certificate", "Install Burp Suite CA certificate for HTTPS interception."),
    ("Objection Testing Suite", "Comprehensive Android app testing with Objection framework."),
    ("Create/Launch AVD with Magisk+Xposed", "Automate AVD creation with Magisk and Xposed."),
    ("Sensitive Strings/Secrets Finder", "Scan APK or decompiled code for sensitive strings."),
    ("Automated Backup/Restore", "Backup and restore app data using ADB."),
    ("App Repackaging Utility", "Repackage APKs after modification."),
    ("Automated Uninstall/Cleaner", "Uninstall app and clean up related files."),
    ("Deep Link Security Tester", "Test deep links for security vulnerabilities."),
    ("Exit", "Exit the Android Suite."),
]

# =============================================================================
# COLOR HELPERS
# =============================================================================

class Colors:
    """Color constants for terminal output"""
    
    def __init__(self):
        if COLOR_ENABLED:
            self.GREEN = Fore.GREEN
            self.CYAN = Fore.CYAN
            self.YELLOW = Fore.YELLOW
            self.RED = Fore.RED
            self.WHITE = Fore.WHITE
            self.RESET = Style.RESET_ALL
        else:
            self.GREEN = ''
            self.CYAN = ''
            self.YELLOW = ''
            self.RED = ''
            self.WHITE = ''
            self.RESET = ''

# Global colors instance
colors = Colors()

# =============================================================================
# TAB COMPLETION
# =============================================================================

class PathCompleter:
    """Tab completion for file paths and common inputs"""
    
    def __init__(self):
        self.matches = []
        self.completion_type = 'path'
    
    def set_type(self, completion_type):
        """Set completion type: 'path', 'package', or 'menu'"""
        self.completion_type = completion_type
    
    def complete(self, text, state):
        """Main completion function called by readline"""
        if state == 0:
            if self.completion_type == 'path':
                self.matches = self._path_complete(text)
            elif self.completion_type == 'package':
                self.matches = self._package_complete(text)
            elif self.completion_type == 'menu':
                self.matches = self._menu_complete(text)
            else:
                self.matches = []
        
        try:
            return self.matches[state]
        except IndexError:
            return None
    
    def _path_complete(self, text):
        """Complete file paths"""
        import glob
        if not text:
            text = './'
        if text.startswith('~'):
            text = os.path.expanduser(text)
        if os.path.isdir(text) and not text.endswith(os.sep):
            text += os.sep
        matches = glob.glob(text + '*')
        return [m + os.sep if os.path.isdir(m) else m for m in matches]
    
    def _package_complete(self, text):
        """Complete package names with common prefixes"""
        prefixes = ['com.', 'org.', 'io.', 'net.', 'app.',
                    'com.android.', 'com.google.', 'com.example.']
        return [p for p in prefixes if p.startswith(text)]
    
    def _menu_complete(self, text):
        """Complete menu options"""
        options = [str(i) for i in range(1, 31)] + ['b', 'h', '0']
        return [o for o in options if o.startswith(text)]


def setup_tab_completion():
    """Initialize tab completion if readline is available"""
    if not READLINE_AVAILABLE:
        return None
    completer = PathCompleter()
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \t\n;')
    return completer

# =============================================================================
# UI HELPERS
# =============================================================================

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print application banner"""
    print(f"""
{colors.GREEN}======================================
Android Suite
Author: {AUTHOR}
Version: {VERSION:<10}
======================================{colors.RESET}
    """)


def print_menu():
    """Print main menu options"""
    print("")
    for idx, (option, _) in enumerate(MENU_OPTIONS, 1):
        print(f"{colors.CYAN}[{idx:>2}]{colors.RESET}  {colors.WHITE}{option}{colors.RESET}")
    print(f"{colors.CYAN}[ b]{colors.RESET}  {colors.WHITE}Back to main menu{colors.RESET}")
    print(f"{colors.CYAN}[ h]{colors.RESET}  {colors.WHITE}Help - Show detailed descriptions{colors.RESET}")
    print(f"{colors.CYAN}[ 0]{colors.RESET}  {colors.WHITE}Exit Android Suite{colors.RESET}")
    print("")


def get_help_text():
    """Generate help text with all menu options"""
    help_text = """
Help - Android Suite Menu Options:
----------------------------------
NAVIGATION:
  [1-30] Select a menu option to execute
  [  b ] Back to main menu (or exit current submenu)
  [  h ] Show this help message
  [  0 ] Exit Android Suite completely

MENU OPTIONS:
"""
    for idx, (option, desc) in enumerate(MENU_OPTIONS, 1):
        help_text += f"[ {idx:<2}] {option:<40} - {desc}\n"
    help_text += "\nTIP: Press Tab for file path completion.\n"
    return help_text


def get_input(prompt):
    """Get user input with colored prompt"""
    return input(f"{colors.YELLOW}{prompt}{colors.RESET}").strip()


def print_success(message):
    """Print success message in green"""
    print(f"{colors.GREEN}{message}{colors.RESET}")


def print_error(message):
    """Print error message in red"""
    print(f"{colors.RED}{message}{colors.RESET}")


def print_warning(message):
    """Print warning message in yellow"""
    print(f"{colors.YELLOW}{message}{colors.RESET}")


def print_info(message):
    """Print info message in cyan"""
    print(f"{colors.CYAN}{message}{colors.RESET}")


def pause(message="Press Enter to continue..."):
    """Pause and wait for user input"""
    input(f"{colors.YELLOW}{message}{colors.RESET}")

# =============================================================================
# MENU HANDLERS
# =============================================================================

def handle_option_1():
    """Handle: Install/verify tools"""
    print_warning("\nAndroid Suite Installer:")
    print_info("The installer has been streamlined for better user experience.")
    print(f"{colors.CYAN}1.{colors.RESET} Install all tools (recommended)")
    print(f"{colors.CYAN}2.{colors.RESET} Install emulator only")
    print(f"{colors.CYAN}3.{colors.RESET} Verify existing installation")
    print(f"{colors.CYAN}b.{colors.RESET} Back to main menu")
    
    choice = get_input("\nSelect installation option [1-3] or 'b' to go back: ").lower()
    
    if choice == 'b':
        return
    
    os.makedirs("tools", exist_ok=True)
    print_warning("Starting installation. This may take several minutes...")
    
    if choice == "1":
        subprocess.run([sys.executable, "installer.py", "--all-tools"], check=False)
    elif choice == "2":
        subprocess.run([sys.executable, "installer.py", "--emulator"], check=False)
    elif choice == "3":
        subprocess.run([sys.executable, "installer.py", "--verify-only"], check=False)
    else:
        print_error("Invalid choice. Returning to main menu...")


def handle_option_2():
    """Handle: Check emulator root status"""
    print_warning("\nChecking emulator root status...")
    device_id = get_input("Enter device ID (optional, will auto-detect): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    
    is_emulator, has_root, is_writable, message = pentester.check_emulator_root_status()
    
    print_info("\nEmulator Status:")
    print(message)
    
    if is_emulator and has_root and is_writable:
        print_success("\n✓ Perfect! Emulator is ready for pentesting.")
    elif is_emulator and has_root:
        print_warning("\n! Almost ready. Run 'adb remount' to enable system writes.")
    elif is_emulator:
        print_warning("\n! Root access needed. Start emulator with -writable-system flag.")
    else:
        print_error("\n! Physical device detected. Limited pentesting capabilities.")


def handle_option_3():
    """Handle: Setup emulator with Play Store + Root"""
    print_warning("\nSetting up Android Emulator with Play Store + Root...")
    pentester = AndroidPentester(apk_path=None)
    pentester._setup_adb_connection()
    pentester.setup_emulator_with_playstore_and_root()


def handle_option_4():
    """Handle: Get PID for package name"""
    package = get_input("Enter package name (e.g. com.example.app): ")
    valid, err = config.validate_package_name(package)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, app_name=package, device_id=device_id)
    pentester._setup_adb_connection()
    matches = pentester.get_pid_for_package(package)
    
    if matches:
        for pid, proc_name in matches:
            print_success(f"PID for {package}: {pid} (process: {proc_name})")
    else:
        print_warning(f"No running process found for package: {package}")


def handle_option_5():
    """Handle: Install APK via ADB"""
    apk_path = get_input("Enter APK file path to install: ")
    valid, err = config.validate_file_path(apk_path, must_exist=True, file_type='.apk')
    if not valid:
        print_error(f"[!] {err}")
        return
    
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=apk_path, device_id=device_id)
    pentester._setup_adb_connection()
    result = pentester.adb_install_apk(apk_path, device_id=device_id)
    
    if result:
        print_success("Install result: Success")
    else:
        print_error("Install result: Failed")


def handle_option_6():
    """Handle: Uninstall APK via ADB"""
    package = get_input("Enter package name to uninstall: ")
    valid, err = config.validate_package_name(package)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, app_name=package, device_id=device_id)
    pentester._setup_adb_connection()
    result = pentester.adb_uninstall_apk(package, device_id=device_id)
    
    if result:
        print_success("Uninstall result: Success")
    else:
        print_error("Uninstall result: Failed")


def handle_option_7():
    """Handle: Push file to device"""
    local_path = get_input("Enter local file path to push: ")
    valid, err = config.validate_file_path(local_path, must_exist=True)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    remote_path = get_input("Enter remote path on device: ")
    valid, err = config.validate_remote_path(remote_path)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    result = pentester.adb_push_file(local_path, remote_path, device_id=device_id)
    
    if result:
        print_success("Push result: Success")
    else:
        print_error("Push result: Failed")


def handle_option_8():
    """Handle: Pull file from device"""
    remote_path = get_input("Enter remote file path on device to pull: ")
    valid, err = config.validate_remote_path(remote_path)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    local_path = get_input("Enter local destination path: ")
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    result = pentester.adb_pull_file(remote_path, local_path, device_id=device_id)
    
    if result:
        print_success("Pull result: Success")
    else:
        print_error("Pull result: Failed")


def handle_option_9():
    """Handle: Collect device information"""
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    info = pentester._collect_device_info()
    
    if not info:
        print_error("No device information could be collected.")
    else:
        print_success("Device info:")
        for k, v in info.items():
            print(f"{colors.CYAN}{k}: {colors.WHITE}{v}{colors.RESET}")


def handle_option_10():
    """Handle: Setup Frida server (interactive)"""
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    
    if not pentester._setup_adb_connection():
        print_error("Failed to connect to Android device. Please check device connection.")
        return
    
    result = pentester.setup_frida_server_interactive()
    
    if result:
        print_success("✅ Frida server setup completed successfully!")
    else:
        print_error("❌ Frida server setup failed.")
        print_warning("💡 Tips for troubleshooting:")
        print("   • Ensure device is rooted or use an emulator")
        print("   • Check internet connection for downloading Frida server")
        print("   • Verify device architecture compatibility")


def handle_option_11():
    """Handle: Stop Frida server"""
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    pentester.menu_stop_frida_server()


def handle_option_12():
    """Handle: Get process list"""
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    procs = pentester.get_process_list()
    
    if not procs:
        print_warning("No running processes found.")
    else:
        for proc in procs:
            print_success(f"PID: {proc['pid']}, Name: {proc['name']}")


def handle_option_13():
    """Handle: View/Save Logcat Output"""
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    
    filter_tag = get_input("Enter logcat filter tag (optional): ") or None
    lines_input = get_input("How many log lines to fetch? [default 200]: ")
    
    valid, lines, err = config.validate_integer(lines_input, min_val=1, max_val=10000, default=200)
    if not valid:
        print_warning(f"[!] {err}, using default 200")
        lines = 200
    
    save_path = get_input("Enter file path to save logcat (leave blank for ./output/logcat.txt): ") or None
    if save_path is None:
        os.makedirs("output", exist_ok=True)
        save_path = "output/logcat.txt"
    
    pentester.get_logcat(filter_tag=filter_tag, save_to_file=save_path, lines=lines)
    print_success(f"Logcat output saved to {save_path}")


def handle_option_14():
    """Handle: List installed packages"""
    device_id = get_input("Enter device ID (optional): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    success, packages, message = pentester.list_installed_packages(device_id=device_id)
    
    if success:
        print_success(f"\n{message}")
        print_success("\nInstalled packages:")
        for i, pkg in enumerate(packages, 1):
            print_info(f"{i:3d}. {pkg}")
    else:
        print_error(message)


def handle_option_15():
    """Handle: Dump app memory with fridump"""
    print_info("[i] Fridump will dump memory from a running app process.")
    print_info("[i] Make sure the target app is running on the device.")
    
    device_id = get_input("Enter device ID (optional): ") or None
    package = get_input("Enter package name (required): ")
    
    valid, err = config.validate_package_name(package)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    pentester = AndroidPentester(app_name=package, device_id=device_id)
    pentester._setup_adb_connection()
    pentester._setup_frida_server_optional()
    
    output_dir = get_input("Enter output directory (leave blank for ./output/fridump): ") or 'output/fridump'
    os.makedirs(output_dir, exist_ok=True)
    
    print_info("[i] Fridump options:")
    strings_mode = config.validate_yes_no(get_input("Extract strings from memory dumps? (y/N): "))
    read_only = config.validate_yes_no(get_input("Include read-only memory regions? (y/N): "))
    
    print_info(f"[i] Running fridump on package: {package}")
    success, message = pentester.run_fridump(output_dir=output_dir, strings_mode=strings_mode, read_only=read_only)
    
    if success:
        print_success(message)
    else:
        print_error(message)
    
    pause()


def handle_option_16():
    """Handle: APKTool decompile APK"""
    apk_path = get_input("Enter APK file path to decompile: ")
    valid, err = config.validate_file_path(apk_path, must_exist=True, file_type='.apk')
    if not valid:
        print_error(f"[!] {err}")
        return
    
    output_dir = get_input("Enter output directory [leave blank for ./output/decompiled]: ") or 'output/decompiled'
    os.makedirs(output_dir, exist_ok=True)
    
    pentester = AndroidPentester(apk_path=apk_path)
    
    # APKTool
    print_warning("Running APKTool...")
    apktool_success, stdout, stderr, message = pentester.run_apktool(apk_path, output_dir=output_dir)
    if apktool_success:
        print_success(f"APKTool decompilation complete. Output in {output_dir}")
    else:
        print_error("APKTool decompilation failed.")
    
    # JADX
    jadx_dir = os.path.join(output_dir, "jadx")
    print_warning("Running JADX...")
    success, stdout, stderr, message = pentester.run_jadx_decompile(apk_path, output_dir=jadx_dir)
    if success:
        print_success(message)
    else:
        print_error(message)


def handle_option_17():
    """Handle: Run APKLeaks on APK"""
    apk_path = get_input("Enter APK file path to scan: ")
    valid, err = config.validate_file_path(apk_path, must_exist=True, file_type='.apk')
    if not valid:
        print_error(f"[!] {err}")
        return
    
    output_path = get_input("Enter output file [leave blank for ./output/apkleaks/report.txt]: ") or 'output/apkleaks/report.txt'
    if output_path.endswith(os.sep) or not os.path.splitext(output_path)[1]:
        output_path = os.path.join(output_path, 'report.txt')
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = ["apkleaks", "-f", apk_path, "-o", output_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print_success(f"APKLeaks scan complete. Output in {output_path}")
        if result.stdout:
            print_info(f"--- APKLeaks STDOUT ---\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print_error(f"APKLeaks scan failed: {e}")


def handle_option_18():
    """Handle: Extract app data directory"""
    package = get_input("Enter package name to extract data for: ")
    valid, err = config.validate_package_name(package)
    if not valid:
        print_error(f"[!] {err}")
        return
    
    device_id = get_input("Enter device ID (optional): ") or None
    dest_dir = get_input("Enter local destination directory (leave blank for ./output/appdata): ") or "output/appdata"
    use_compression = config.validate_yes_no(get_input("Use compression for large data? (y/N): "))
    
    os.makedirs(dest_dir, exist_ok=True)
    
    pentester = AndroidPentester(apk_path=None, app_name=package, device_id=device_id)
    pentester._setup_adb_connection()
    result, message = pentester.extract_app_data_directory(package, dest_dir, device_id=device_id, use_compression=use_compression)
    
    if result:
        print_success(message)
    else:
        print_error(message)


def handle_option_19():
    """Handle: Run apk-components-inspector"""
    apk_path = get_input("Enter APK file path to analyze: ")
    valid, err = config.validate_file_path(apk_path, must_exist=True, file_type='.apk')
    if not valid:
        print_error(f"[!] {err}")
        return
    
    print_warning("Running apk-components-inspector...")
    pentester = AndroidPentester(apk_path=apk_path)
    success, stdout, stderr, message = pentester.run_apk_components_inspector(apk_path)
    
    print_info("--- apk-components-inspector STDOUT ---")
    print(stdout if stdout else f"{colors.YELLOW}[No stdout output]{colors.RESET}")
    print_info("--- apk-components-inspector STDERR ---")
    print(stderr if stderr else f"{colors.YELLOW}[No stderr output]{colors.RESET}")
    
    if success:
        print_success(message)
    else:
        print_error(message)


def handle_option_20():
    """Handle: Run frida-script-gen"""
    apk_path = get_input("Enter APK file path (required): ")
    if not apk_path or not os.path.exists(apk_path):
        print_error("[!] APK file not found.")
        return
    
    output_file = get_input("Enter output file (leave blank if not needed): ") or None
    extra_args = get_input("Enter extra arguments (space separated, leave blank if none): ")
    extra_args_list = extra_args.split() if extra_args else None
    
    print_warning("Running frida-script-gen...")
    pentester = AndroidPentester(apk_path=apk_path)
    success, stdout, stderr, message = pentester.run_frida_script_gen(apk_path, output_file, extra_args_list)
    
    if success:
        if stdout:
            print_success(stdout)
        print_success(message)
    else:
        print_error(message)
        if stderr:
            print_error(stderr)


def handle_option_21():
    """Handle: Run MobApp-Storage-Inspector"""
    print_warning("Launching MobApp-Storage-Inspector GUI...")
    apk_path = get_input("Enter APK file path (required): ")
    valid, err = config.validate_file_path(apk_path, must_exist=True, file_type='.apk')
    if not valid:
        print_error(f"[!] {err}")
        return
    
    pentester = AndroidPentester(apk_path=apk_path)
    success, stdout, stderr, message = pentester.run_mobapp_storage_inspector(apk_path)
    
    if success:
        print_success(message)
    else:
        print_error(message)


def handle_option_22():
    """Handle: Setup Burp Suite CA certificate"""
    print_warning("\nBurp Suite CA Certificate Setup")
    print_info("This will install the Burp Suite CA certificate on your device/emulator.")
    
    device_id = get_input("Enter device ID (optional): ") or None
    cert_path = get_input("Enter path to Burp CA certificate (leave blank to use default ./tools/burp_cert.pem): ") or None
    
    pentester = AndroidPentester(apk_path=None, device_id=device_id)
    pentester._setup_adb_connection()
    
    result = pentester.setup_burp_certificate(cert_path=cert_path, device_id=device_id)
    if result:
        print_success("✅ Burp Suite CA certificate installed successfully!")
    else:
        print_error("❌ Failed to install Burp Suite CA certificate.")


def handle_option_23():
    """Handle: Objection Testing Suite"""
    print_warning("\nObjection Testing Suite")
    
    try:
        from objection_module import ObjectionTester
        
        package = get_input("Enter package name to test: ")
        valid, err = config.validate_package_name(package)
        if not valid:
            print_error(f"[!] {err}")
            return
        
        device_id = get_input("Enter device ID (optional): ") or None
        
        objection_tester = ObjectionTester(package_name=package, device_id=device_id)
        objection_tester.run_menu()
        
    except ImportError:
        print_error("[!] Could not import objection_module. Make sure objection_module.py exists.")
    except Exception as e:
        print_error(f"[!] Error initializing Objection tester: {str(e)}")


def handle_option_24():
    """Handle: Create/Launch AVD with Magisk+Xposed"""
    print_warning("\nLaunching AVD with Magisk and Xposed (root, writable system)...")
    
    try:
        import avd_magisk_xposed
        avd_magisk_xposed.create_avd_with_magisk_xposed()
        print_success("AVD launch script executed. Check emulator window for progress.")
    except Exception as e:
        print_error(f"Error running avd_magisk_xposed: {e}")
    
    pause()


def handle_option_25():
    """Handle: Sensitive Strings/Secrets Finder"""
    print_warning("\nSensitive Strings/Secrets Finder")
    
    apk_path = get_input("Enter APK path (or leave blank to use last set path): ") or None
    
    pentester = AndroidPentester(apk_path=apk_path)
    pentester._setup_adb_connection()
    
    results = pentester.find_sensitive_strings()
    
    if results:
        print_success("Sensitive strings/secrets found:")
        for r in results:
            print_info(r)
    else:
        print_warning("No sensitive strings or secrets found.")
    
    pause()


def handle_option_26():
    """Handle: Automated Backup/Restore"""
    print_warning("\nAutomated Backup/Restore")
    
    package = get_input("Enter package name to backup/restore: ")
    
    pentester = AndroidPentester(apk_path=None)
    pentester._setup_adb_connection()
    
    print(f"{colors.CYAN}1.{colors.RESET} Backup app data")
    print(f"{colors.CYAN}2.{colors.RESET} Restore app data")
    print(f"{colors.CYAN}b.{colors.RESET} Back to main menu")
    
    choice = get_input("Select option [1-2] or 'b': ").lower()
    
    if choice == '1':
        backup_path = get_input("Enter backup output path (default: ./output/backup.ab): ") or "./output/backup.ab"
        pentester.adb_backup_app(package, backup_path)
    elif choice == '2':
        backup_path = get_input("Enter backup file path to restore: ")
        pentester.adb_restore_app(package, backup_path)
    
    pause()


def handle_option_27():
    """Handle: App Repackaging Utility"""
    print_warning("\nApp Repackaging Utility")
    
    apk_path = get_input("Enter APK path to repackage: ")
    output_path = get_input("Enter output path (default: ./output/repackaged.apk): ") or "./output/repackaged.apk"
    
    pentester = AndroidPentester(apk_path=apk_path)
    pentester.repackage_apk(output_path)
    
    pause()


def handle_option_28():
    """Handle: Automated Uninstall/Cleaner"""
    print_warning("\nAutomated Uninstall/Cleaner")
    
    package = get_input("Enter package name to uninstall and clean: ")
    
    pentester = AndroidPentester(apk_path=None)
    pentester._setup_adb_connection()
    pentester.uninstall_app_and_clean(package)
    
    pause()


def handle_option_29():
    """Handle: Deep Link Security Tester"""
    print_warning("\nDeep Link Security Tester")
    print_info("Based on HackTricks, Oversecured & 8ksec Research")
    
    print(f"\n{colors.WHITE}This tool tests deep links for:{colors.RESET}")
    print("  • Open Redirect vulnerabilities")
    print("  • XSS/JavaScript Injection")
    print("  • Path Traversal attacks")
    print("  • SQL Injection")
    print("  • Authentication Bypass")
    print("  • Intent Injection (component hijacking)")
    print("  • File/Content Provider access")
    
    print_info("\nSelect Mode:")
    print(f"  {colors.GREEN}1.{colors.RESET} Full Test (requires device/emulator)")
    print(f"  {colors.GREEN}2.{colors.RESET} Offline Analysis (no device needed)")
    print(f"  {colors.GREEN}b.{colors.RESET} Back to main menu")
    
    mode_choice = get_input("\nSelect mode [1-2] or 'b': ").lower()
    
    if mode_choice == 'b':
        return
    
    offline_mode = (mode_choice == '2')
    
    if offline_mode:
        print_info("\n[OFFLINE MODE] Extract & analyze deep links without device")
    else:
        print_info("\n[FULL TEST MODE] Will execute tests on connected device")
    
    print_info("\nInput options:")
    print("  1. APK file path (will extract manifest)")
    print("  2. Decompiled manifest path")
    print("  3. Both APK and manifest")
    
    apk_path = get_input("\nEnter APK path (or press Enter to skip): ") or None
    if apk_path:
        valid, err = config.validate_file_path(apk_path, must_exist=True, file_type='.apk')
        if not valid:
            print_error(f"[!] {err}")
            apk_path = None
    
    manifest_path = get_input("Enter AndroidManifest.xml path (or press Enter to auto-detect): ") or None
    if manifest_path:
        valid, err = config.validate_file_path(manifest_path, must_exist=True)
        if not valid:
            print_error(f"[!] {err}")
            manifest_path = None
    
    package_name = get_input("Enter package name (optional, for intent tests): ") or None
    
    if not apk_path and not manifest_path:
        print_error("[!] Please provide either an APK path or manifest path")
        pause()
        return
    
    pentester = AndroidPentester(apk_path=apk_path)
    
    if offline_mode:
        print_success("\nStarting Offline Deep Link Analysis...")
        results = pentester.run_deeplink_offline_analysis(
            apk_path=apk_path,
            package_name=package_name,
            manifest_path=manifest_path
        )
    else:
        print_success("\nStarting Deep Link Security Test...")
        pentester._setup_adb_connection()
        results = pentester.run_deeplink_security_test(
            apk_path=apk_path,
            package_name=package_name,
            manifest_path=manifest_path
        )
        
        # Offer manual testing
        if results.get('deep_links'):
            manual_test = get_input("\nTest a specific deep link manually? (y/n): ").lower()
            if manual_test == 'y':
                print_info("\nAvailable deep links:")
                for i, link in enumerate(results['deep_links'], 1):
                    scheme = link.get('scheme', '')
                    host = link.get('host', '')
                    path = link.get('path', '')
                    uri = f"{scheme}://{host}{path}" if host else f"{scheme}://{path}"
                    print(f"  [{i}] {uri}")
                
                custom_uri = get_input("\nEnter custom deep link URI to test: ")
                if custom_uri:
                    print(f"[*] Testing: {custom_uri}")
                    test_result = pentester.execute_deeplink_test(custom_uri)
                    print(f"[*] Result: {'Success' if test_result['success'] else 'Failed'}")
                    print(f"[*] Response: {test_result.get('response', 'N/A')[:200]}")
                    if test_result.get('indicators'):
                        print(f"[*] Indicators: {', '.join(test_result['indicators'])}")
    
    pause()


# =============================================================================
# MAIN LOOP
# =============================================================================

def main():
    """Main application entry point"""
    clear_screen()
    
    # Initialize tab completion
    completer = setup_tab_completion()
    if completer and READLINE_AVAILABLE:
        print("[+] Tab completion enabled for file paths")
    
    print_banner()
    help_text = get_help_text()
    
    # Menu handler mapping
    handlers = {
        1: handle_option_1,
        2: handle_option_2,
        3: handle_option_3,
        4: handle_option_4,
        5: handle_option_5,
        6: handle_option_6,
        7: handle_option_7,
        8: handle_option_8,
        9: handle_option_9,
        10: handle_option_10,
        11: handle_option_11,
        12: handle_option_12,
        13: handle_option_13,
        14: handle_option_14,
        15: handle_option_15,
        16: handle_option_16,
        17: handle_option_17,
        18: handle_option_18,
        19: handle_option_19,
        20: handle_option_20,
        21: handle_option_21,
        22: handle_option_22,
        23: handle_option_23,
        24: handle_option_24,
        25: handle_option_25,
        26: handle_option_26,
        27: handle_option_27,
        28: handle_option_28,
        29: handle_option_29,
        30: lambda: sys.exit(0),
    }
    
    while True:
        print_menu()
        choice = get_input("Select an option [1-30], 'b' to return, or 'h' for help: ").lower()
        
        # Handle special commands
        if choice in ("h", "help"):
            print_success(help_text)
            pause("Press Enter to return to the menu...")
            continue
        
        if choice == "b":
            continue
        
        if choice == '0':
            print("Exiting.")
            sys.exit(0)
        
        # Validate numeric choice
        if not (choice.isdigit() and 1 <= int(choice) <= len(MENU_OPTIONS)):
            print_error(f"Invalid option. Please select a valid option (1-{len(MENU_OPTIONS)}), 'b', or 'h'.")
            pause()
            continue
        
        # Execute handler
        choice_num = int(choice)
        try:
            handler = handlers.get(choice_num)
            if handler:
                handler()
        except Exception as e:
            print_error(f"An error occurred: {e}")
            pause()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()

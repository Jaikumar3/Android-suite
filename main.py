#!/usr/bin/env python3
"""
Android Pentesting Automation Script
Main entry point for the automation tool
"""


import sys
import os
import argparse
from android_pentest import AndroidPentester
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False

VERSION = "2.5.0"

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
    ("Extract app data directory", "Extract the /data/data/<package> directory from the device (root required, 10min timeout with extension option)."),
    ("Run apk-components-inspector on APK", "Analyze APK components using apk-components-inspector."),
    ("Run frida-script-gen (generate Frida scripts)", "Generate Frida scripts using frida-script-gen tool."),
    ("Run MobApp-Storage-Inspector on APK", "Analyze APK storage using MobApp-Storage-Inspector.jar."),
    ("Setup Burp Suite CA certificate", "Install Burp Suite CA certificate to Android device/emulator for HTTPS interception."),
    ("Objection Testing Suite", "Comprehensive Android app testing with Objection framework."),
    ("Create/Launch AVD with Magisk+Xposed (root, writable)", "Automate AVD creation and patching with Magisk and Xposed, with writable system and root."),
    ("Sensitive Strings/Secrets Finder", "Scan APK or decompiled code for sensitive strings, secrets, and credentials."),
    ("Automated Backup/Restore", "Backup and restore app data using ADB (root required for some apps)."),
    ("App Repackaging Utility", "Repackage APKs after modification for testing or bypassing protections."),
    ("Automated Uninstall/Cleaner", "Uninstall app and optionally clean up related files and data."),
    ("Exit", "Exit the Android Suite."),
]


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Define color variables at the top level for global use
    color_green = Fore.GREEN if COLOR_ENABLED else ''
    color_cyan = Fore.CYAN if COLOR_ENABLED else ''
    color_yellow = Fore.YELLOW if COLOR_ENABLED else ''
    color_red = Fore.RED if COLOR_ENABLED else ''
    color_white = Fore.WHITE if COLOR_ENABLED else ''
    color_reset = Style.RESET_ALL if COLOR_ENABLED else ''
    
    banner = f"""
{color_green}======================================
Android Suite
Author: Jai
Version: {VERSION:<10}
======================================{color_reset}
    """
    print(banner)
    help_text = """
Help - Android Suite Menu Options:
----------------------------------
NAVIGATION:
  [1-24] Select a menu option to execute
  [  b ] Back to main menu (or exit current submenu)
  [  h ] Show this help message
  [  0 ] Exit Android Suite completely

MENU OPTIONS:
"""
    for idx, (option, desc) in enumerate(MENU_OPTIONS, 1):
        help_text += f"[ {idx:<2}] {option:<40} - {desc}\n"
    help_text += "\nTIP: Most submenus support 'b' to go back to the previous menu level.\n"

    while True:
        # Print menu
        print("")
        for idx, (option, _) in enumerate(MENU_OPTIONS, 1):
            if COLOR_ENABLED:
                print(f"{color_cyan}[{idx:>2}]{color_reset}  {color_white}{option:<32}{color_reset}")
            else:
                print(f"[{idx:>2}]  {option:<32}")
        if COLOR_ENABLED:
            print(f"{color_cyan}[ b]{color_reset}  {color_white}Back to main menu{color_reset}")
            print(f"{color_cyan}[ h]{color_reset}  {color_white}Help - Show detailed descriptions{color_reset}")
            print(f"{color_cyan}[ 0]{color_reset}  {color_white}Exit Android Suite{color_reset}")
        else:
            print(f"[ b]  Back to main menu")
            print(f"[ h]  Help - Show detailed descriptions")
            print(f"[ 0]  Exit Android Suite")
        print("")
        if COLOR_ENABLED:
            choice = input(f"{Fore.YELLOW}Select an option [1-28], 'b' to return, or 'h' for help: {Style.RESET_ALL}").strip().lower()
        else:
            choice = input(f"Select an option [1-28], 'b' to return, or 'h' for help: ").strip().lower()

        if choice in ("h", "help"):
            if COLOR_ENABLED:
                print(f"{Fore.GREEN}{help_text}{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to return to the menu...{Style.RESET_ALL}")
            else:
                print(help_text)
                input("Press Enter to return to the menu...")
            continue
        if choice == "b":
            continue
        if choice == '0':
            print("Exiting.")
            sys.exit(0)
        if not (choice.isdigit() and 1 <= int(choice) <= len(MENU_OPTIONS)):
            color_red = Fore.RED if COLOR_ENABLED else ''
            color_yellow = Fore.YELLOW if COLOR_ENABLED else ''
            color_reset = Style.RESET_ALL if COLOR_ENABLED else ''
            print(f"{color_red}Invalid option. Please select a valid option (1-{len(MENU_OPTIONS)}), 'b', or 'h'.{color_reset}")
            input(f"{color_yellow}Press Enter to continue...{color_reset}")
            continue
        # Convert to int for option handling
        choice_num = int(choice)
        try:
            if choice_num == 1:
                print(f"\n{color_yellow}Android Suite Installer:{color_reset}")
                print(f"{color_cyan}The installer has been streamlined for better user experience.{color_reset}")
                print(f"{color_cyan}1.{color_reset} Install all tools (recommended)")
                print(f"{color_cyan}2.{color_reset} Install emulator only") 
                print(f"{color_cyan}3.{color_reset} Verify existing installation")
                print(f"{color_cyan}b.{color_reset} Back to main menu")

                install_choice = input(f"\n{color_yellow}Select installation option [1-3] or 'b' to go back: {color_reset}").strip().lower()

                if install_choice == 'b':
                    continue

                import subprocess
                os.makedirs("tools", exist_ok=True)

                print(f"{color_yellow}Starting installation. This may take several minutes...{color_reset}")
                if install_choice == "1":
                    subprocess.run([sys.executable, "installer.py", "--all-tools"], check=False)
                elif install_choice == "2":
                    subprocess.run([sys.executable, "installer.py", "--emulator"], check=False)
                elif install_choice == "3":
                    subprocess.run([sys.executable, "installer.py", "--verify"], check=False)
                else:
                    print(f"{color_red}Invalid choice. Returning to main menu...{color_reset}")
                    continue
            elif choice_num == 2:
                print(f"\n{color_yellow}Checking emulator root status...{color_reset}")
                device_id = input("Enter device ID (optional, will auto-detect): ").strip() or None
                pentester = AndroidPentester(apk_path=None, device_id=device_id)
                pentester._setup_adb_connection()
                is_emulator, has_root, is_writable, message = pentester.check_emulator_root_status()
                print(f"\n{color_cyan}Emulator Status:{color_reset}")
                print(message)
                if is_emulator and has_root and is_writable:
                    print(f"\n{color_green}✓ Perfect! Emulator is ready for pentesting.{color_reset}")
                elif is_emulator and has_root:
                    print(f"\n{color_yellow}! Almost ready. Run 'adb remount' to enable system writes.{color_reset}")
                elif is_emulator:
                    print(f"\n{color_yellow}! Root access needed. Start emulator with -writable-system flag.{color_reset}")
                else:
                    print(f"\n{color_red}! Physical device detected. Limited pentesting capabilities.{color_reset}")
            elif choice_num == 3:
                print(f"\n{color_yellow}Setting up Android Emulator with Play Store + Root...{color_reset}")
                pentester = AndroidPentester(apk_path=None)
                pentester._setup_adb_connection()
                pentester.setup_emulator_with_playstore_and_root()
            elif choice_num == 4:
                package = input("Enter package name (e.g. com.example.app): ").strip()
                if not package:
                    print(f"{color_yellow}No package name entered.{color_reset}")
                    continue
                device_id = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=package, device_id=device_id)
                pentester._setup_adb_connection()
                matches = pentester.get_pid_for_package(package)
                if matches:
                    for pid, proc_name in matches:
                        print(f"{color_green}PID for {package}: {pid} (process: {proc_name}){color_reset}")
                else:
                    print(f"{color_yellow}No running process found for package: {package}{color_reset}")
            elif choice_num == 5:
                apk_path = input("Enter APK file path to install: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not apk_path or not os.path.exists(apk_path):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                    continue
                pentester = AndroidPentester(apk_path=apk_path, app_name=None, device_id=device_id)
                pentester._setup_adb_connection()
                result = pentester.adb_install_apk(apk_path, device_id=device_id)
                print(f"{color_green if result else color_red}Install result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 6:
                package = input("Enter package name to uninstall: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not package:
                    print(f"{color_yellow}[!] No package name entered.{color_reset}")
                    continue
                pentester = AndroidPentester(apk_path=None, app_name=package, device_id=device_id)
                pentester._setup_adb_connection()
                result = pentester.adb_uninstall_apk(package, device_id=device_id)
                print(f"{color_green if result else color_red}Uninstall result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 7:
                local_path = input("Enter local file path to push: ").strip()
                remote_path = input("Enter remote path on device: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not local_path or not os.path.exists(local_path):
                    print(f"{color_red}[!] Local file not found.{color_reset}")
                    continue
                if not remote_path:
                    print(f"{color_yellow}[!] No remote path entered.{color_reset}")
                    continue
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device_id)
                pentester._setup_adb_connection()
                result = pentester.adb_push_file(local_path, remote_path, device_id=device_id)
                print(f"{color_green if result else color_red}Push result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 8:
                remote_path = input("Enter remote file path on device to pull: ").strip()
                local_path = input("Enter local destination path: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not remote_path:
                    print(f"{color_yellow}[!] No remote path entered.{color_reset}")
                    continue
                if not local_path:
                    print(f"{color_yellow}[!] No local destination path entered.{color_reset}")
                    continue
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device_id)
                pentester._setup_adb_connection()
                result = pentester.adb_pull_file(remote_path, local_path, device_id=device_id)
                print(f"{color_green if result else color_red}Pull result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 9:
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._setup_adb_connection()
                info = pentester._collect_device_info()
                if not info:
                    print(f"{color_red}No device information could be collected.{color_reset}")
                else:
                    print(f"{color_green}Device info:{color_reset}")
                    for k, v in info.items():
                        print(f"{color_cyan}{k}: {color_white}{v}{color_reset}")
            elif choice_num == 10:
                # Setup Frida server with interactive version selection
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                
                if not pentester._setup_adb_connection():
                    print(f"{color_red}Failed to connect to Android device. Please check device connection.{color_reset}")
                    continue
                
                result = pentester.setup_frida_server_interactive()
                if result:
                    print(f"{color_green}✅ Frida server setup completed successfully!{color_reset}")
                else:
                    print(f"{color_red}❌ Frida server setup failed.{color_reset}")
                    print(f"{color_yellow}💡 Tips for troubleshooting:{color_reset}")
                    print("   • Ensure device is rooted or use an emulator")
                    print("   • Check internet connection for downloading Frida server")
                    print("   • Verify device architecture compatibility")
                    print("   • Try a different Frida version")
            elif choice_num == 11:
                # Stop Frida server on device
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._setup_adb_connection()
                pentester.menu_stop_frida_server()
            elif choice_num == 12:
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._setup_adb_connection()
                procs = pentester.get_process_list()
                if not procs:
                    print(f"{color_yellow}No running processes found.{color_reset}")
                else:
                    for proc in procs:
                        print(f"{color_green}PID: {proc['pid']}, Name: {proc['name']}{color_reset}")
            elif choice_num == 13:
                # View/Save Logcat Output
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._setup_adb_connection()
                filter_tag = input("Enter logcat filter tag (optional): ").strip() or None
                try:
                    lines = int(input("How many log lines to fetch? [default 200]: ").strip() or "200")
                except ValueError:
                    lines = 200
                save_path = input("Enter file path to save logcat output (leave blank to use ./output/logcat.txt or print to screen): ").strip() or None
                if save_path is None:
                    os.makedirs("output", exist_ok=True)
                    save_path = "output/logcat.txt"
                pentester.get_logcat(filter_tag=filter_tag, save_to_file=save_path, lines=lines)
                print(f"{color_green}Logcat output saved to {save_path}{color_reset}")
            elif choice_num == 14:
                # List installed packages
                device_id = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device_id)
                success, packages, message = pentester.list_installed_packages(device_id=device_id)
                
                if success:
                    print(f"\n{color_green}{message}{color_reset}")
                    print(f"\n{color_green}Installed packages:{color_reset}")
                    for i, pkg in enumerate(packages, 1):
                        print(f"{color_cyan}{i:3d}. {pkg}{color_reset}")
                else:
                    print(f"{color_red}{message}{color_reset}")
            elif choice_num == 15:
                # Dump app memory with fridump
                print(f"{color_cyan}[i] Fridump will dump memory from a running app process.{color_reset}")
                print(f"{color_cyan}[i] Make sure the target app is running on the device.{color_reset}")
                device = input("Enter device ID (optional): ").strip() or None
                name = input("Enter package name (required): ").strip()
                if not name:
                    print(f"{color_yellow}[!] Package name is required for fridump.{color_reset}")
                    continue
                pentester = AndroidPentester(app_name=name, device_id=device)
                pentester._setup_adb_connection()
                pentester._setup_frida_server_optional()
                output_dir = input("Enter output directory for fridump (leave blank for ./output/fridump): ").strip() or 'output/fridump'
                os.makedirs(output_dir, exist_ok=True)
                print(f"{color_cyan}[i] Running fridump on package: {name}{color_reset}")
                pentester.run_fridump(output_dir=output_dir)
                print(f"{color_green}Fridump completed. Output in {output_dir}{color_reset}")
            elif choice_num == 16:
                # APKTool and JADX decompile APK
                apk = input("Enter APK file path to decompile: ").strip()
                output_dir = input("Enter output directory for decompilation [leave blank for ./output/decompiled]: ").strip() or 'output/decompiled'
                if not apk or not os.path.exists(apk):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                    continue
                os.makedirs(output_dir, exist_ok=True)
                # Create pentester instance for APKTool
                pentester = AndroidPentester(apk_path=apk, app_name=None, device_id=None)
                # APKTool decompilation
                print(f"{color_yellow}Running APKTool...{color_reset}")
                apktool_success, stdout, stderr, message = pentester.run_apktool(apk, output_dir=output_dir)
                if apktool_success:
                    print(f"{color_green}APKTool decompilation complete. Output in {output_dir}{color_reset}")
                else:
                    print(f"{color_red}APKTool decompilation failed.{color_reset}")
                # JADX decompilation (delegated to android_pentest)
                jadx_dir = os.path.join(output_dir, "jadx")
                print(f"{color_yellow}Running JADX...{color_reset}")
                success, stdout, stderr, message = pentester.run_jadx_decompile(apk, output_dir=jadx_dir)
                if success:
                    print(f"{color_green}{message}{color_reset}")
                else:
                    print(f"{color_red}{message}{color_reset}")
                    if stderr:
                        print(f"{color_red}{stderr}{color_reset}")
            elif choice_num == 17:
                # Run APKLeaks on APK
                apk = input("Enter APK file path to scan: ").strip()
                output_path = input("Enter output file for apkleaks [leave blank for ./output/apkleaks/report.txt]: ").strip() or 'output/apkleaks/report.txt'
                # If user enters a directory, append report.txt
                if output_path.endswith(os.sep) or (not os.path.splitext(output_path)[1]):
                    output_path = os.path.join(output_path, 'report.txt')
                output_dir = os.path.dirname(output_path)
                if not apk or not os.path.exists(apk):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                else:
                    os.makedirs(output_dir, exist_ok=True)
                    import subprocess
                    cmd = ["apkleaks", "-f", apk, "-o", output_path]
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                        print(f"{color_green}APKLeaks scan complete. Output in {output_path}{color_reset}")
                        if result.stdout:
                            print(f"{color_cyan}--- APKLeaks STDOUT ---{color_reset}\n{result.stdout}")
                        if result.stderr:
                            print(f"{color_yellow}--- APKLeaks STDERR ---{color_reset}\n{result.stderr}")
                    except subprocess.CalledProcessError as e:
                        print(f"{color_red}APKLeaks scan failed: {e}{color_reset}")
                        if e.stdout:
                            print(f"{color_cyan}--- APKLeaks STDOUT ---{color_reset}\n{e.stdout}")
                        if e.stderr:
                            print(f"{color_yellow}--- APKLeaks STDERR ---{color_reset}\n{e.stderr}")
            elif choice_num == 18:
                # Extract app data directory
                package = input("Enter package name to extract data for: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                dest_dir = input("Enter local destination directory (leave blank for ./output/appdata): ").strip() or "output/appdata"
                use_compression = input("Use compression for large data? (y/N): ").strip().lower() == 'y'
                if not package:
                    print(f"{color_yellow}[!] No package name entered.{color_reset}")
                    continue
                os.makedirs(dest_dir, exist_ok=True)
                pentester = AndroidPentester(apk_path=None, app_name=package, device_id=device_id)
                pentester._setup_adb_connection()
                result, message = pentester.extract_app_data_directory(package, dest_dir, device_id=device_id, use_compression=use_compression)
                color = color_green if result else color_red
                print(f"{color}{message}{color_reset}")

            elif choice_num == 19:
                # Run apk-components-inspector on APK
                apk = input("Enter APK file path to analyze: ").strip()
                if not apk or not os.path.exists(apk):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                    continue
                print(f"{color_yellow}Running apk-components-inspector...{color_reset}")
                pentester = AndroidPentester(apk_path=apk, app_name=None, device_id=None)
                success, stdout, stderr, message = pentester.run_apk_components_inspector(apk)
                # Always print both stdout and stderr, even if empty, with clear labels
                print(f"{color_cyan}--- apk-components-inspector STDOUT ---{color_reset}")
                print(stdout if stdout else f"{color_yellow}[No stdout output]{color_reset}")
                print(f"{color_cyan}--- apk-components-inspector STDERR ---{color_reset}")
                print(stderr if stderr else f"{color_yellow}[No stderr output]{color_reset}")
                # Print message and success/failure
                if success:
                    print(f"{color_green}{message}{color_reset}")
                else:
                    print(f"{color_red}{message}{color_reset}")

            elif choice_num == 20:
                # Run frida-script-gen
                apk_path = input("Enter APK file path (required): ").strip()
                if not apk_path or not os.path.exists(apk_path):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                    continue
                output_file = input("Enter output file for frida-script-gen (leave blank if not needed): ").strip() or None
                extra_args = input("Enter any extra arguments for frida-script-gen (space separated, leave blank if none): ").strip()
                extra_args_list = extra_args.split() if extra_args else None
                print(f"{color_yellow}Running frida-script-gen...{color_reset}")
                pentester = AndroidPentester(apk_path=apk_path, app_name=None, device_id=None)
                success, stdout, stderr, message = pentester.run_frida_script_gen(apk_path, output_file, extra_args_list)
                if success:
                    if stdout:
                        print(f"{color_green}{stdout}{color_reset}")
                    print(f"{color_green}{message}{color_reset}")
                else:
                    print(f"{color_red}{message}{color_reset}")
                    if stderr:
                        print(f"{color_red}{stderr}{color_reset}")
            elif choice_num == 21:
                # Run MobApp-Storage-Inspector GUI using AndroidPentester class
                print(f"{color_yellow}Launching MobApp-Storage-Inspector GUI...{color_reset}")
                print(f"{color_cyan}Note: This is a GUI application that will run independently.{color_reset}")
                print(f"{color_cyan}You can continue using this tool while the GUI runs in the background.{color_reset}")
                
                pentester = AndroidPentester(apk_path=None)
                success, stdout, stderr, message = pentester.run_mobapp_storage_inspector()
                
                if success:
                    print(f"{color_green}{message}{color_reset}")
                    print(f"{color_green}💡 The GUI should now be open. You can analyze APKs using the interface.{color_reset}")
                    print(f"{color_yellow}💡 To close the GUI, use the application's exit button or close the window.{color_reset}")
                else:
                    print(f"{color_red}{message}{color_reset}")
                    if stderr:
                        print(f"{color_red}{stderr}{color_reset}")
                    print(f"{color_yellow}💡 If Java issues persist, ensure Java 17+ is installed from: https://adoptium.net/{color_reset}")
            elif choice_num == 22:
                # Setup Burp Suite CA certificate
                print(f"{color_yellow}Setting up Burp Suite CA certificate...{color_reset}")
                device_id = input("Enter device ID (optional, will auto-detect): ").strip() or None
                cert_path = input("Enter path to Burp certificate (DER format, optional - will guide if not provided): ").strip() or None
                
                pentester = AndroidPentester(apk_path=None, device_id=device_id)
                pentester._setup_adb_connection()
                
                success = pentester.setup_burp_certificate(burp_cert_path=cert_path, device_id=device_id)
                
                if success:
                    print(f"{color_green}[+] Burp certificate setup completed successfully!{color_reset}")
                    print(f"{color_cyan}[*] Configure your device proxy settings to use Burp Suite for traffic interception.{color_reset}")
                else:
                    print(f"{color_red}[!] Burp certificate setup failed. Check the output above for details.{color_reset}")
                    
            elif choice_num == 23:
                # Objection Testing Suite
                print(f"{color_yellow}Starting Objection Testing Suite...{color_reset}")
                
                # Get target information
                print(f"{color_cyan}Target Selection:{color_reset}")
                print(f"{color_cyan}1.{color_reset} Package name (e.g., com.example.app)")
                print(f"{color_cyan}2.{color_reset} Process ID (PID)")
                print(f"{color_cyan}b.{color_reset} Back to main menu")
                
                target_choice = input(f"\n{color_yellow}Select target type [1-2] or 'b' to go back: {color_reset}").strip().lower()
                
                if target_choice == 'b':
                    continue
                
                package_name = None
                process_id = None
                
                if target_choice == "1":
                    package_name = input("Enter package name (e.g., com.example.app): ").strip()
                    if not package_name:
                        print(f"{color_red}[!] No package name entered.{color_reset}")
                        continue
                elif target_choice == "2":
                    try:
                        process_id = int(input("Enter process ID (PID): ").strip())
                    except ValueError:
                        print(f"{color_red}[!] Invalid PID entered.{color_reset}")
                        continue
                else:
                    print(f"{color_red}[!] Invalid choice.{color_reset}")
                    continue
                
                device_id = input("Enter device ID (optional, will auto-detect): ").strip() or None
                
                # Import and initialize Objection module
                try:
                    from objection_module import ObjectionTester
                    
                    objection_tester = ObjectionTester(
                        package_name=package_name,
                        process_id=process_id,
                        device_id=device_id
                    )
                    
                    # Check if Objection is available
                    available, message = objection_tester.check_objection_available()
                    if not available:
                        print(f"{color_red}[!] Objection not available: {message}{color_reset}")
                        continue
                        
                    # Verify target is running
                    if package_name or process_id:
                        running, message = objection_tester.verify_target_running()
                        if not running:
                            print(f"{color_red}[!] Target not running: {message}{color_reset}")
                            response = input("Continue anyway? (y/N): ").strip().lower()
                            if response != 'y':
                                continue
                    
                    # Run Objection menu system
                    objection_menu_running = True
                    while objection_menu_running:
                        objection_tester.display_main_menu()
                        
                        try:
                            obj_choice = input(f"{color_yellow}Select an option [1-9] or 'b' to return: {color_reset}").strip().lower()
                            
                            if obj_choice == 'b':
                                objection_menu_running = False
                                continue
                                
                            if not obj_choice.isdigit() or not (1 <= int(obj_choice) <= 9):
                                print(f"{color_red}Invalid option. Please select 1-9 or 'b'.{color_reset}")
                                input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                continue
                                
                            obj_choice_num = int(obj_choice)
                            
                            if obj_choice_num == 1:
                                # Security Bypasses
                                bypass_menu_running = True
                                while bypass_menu_running:
                                    objection_tester.display_security_bypasses_menu()
                                    bypass_choice = input(f"{color_yellow}Select bypass option [1-5] or 'b': {color_reset}").strip().lower()
                                    
                                    if bypass_choice == 'b':
                                        bypass_menu_running = False
                                        continue
                                        
                                    if bypass_choice == '1':
                                        success, output_file, stdout, stderr = objection_tester.run_root_detection_bypass()
                                        print(f"{color_green if success else color_red}Root detection bypass {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif bypass_choice == '2':
                                        success, output_file, stdout, stderr = objection_tester.run_ssl_pinning_bypass()
                                        print(f"{color_green if success else color_red}SSL pinning bypass {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif bypass_choice == '3':
                                        success, output_file, stdout, stderr = objection_tester.run_anti_debugging_bypass()
                                        print(f"{color_green if success else color_red}Anti-debugging bypass {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif bypass_choice == '4':
                                        success, output_file, stdout, stderr = objection_tester.run_biometric_bypass()
                                        print(f"{color_green if success else color_red}Biometric bypass {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif bypass_choice == '5':
                                        results = objection_tester.run_all_security_bypasses()
                                        summary = objection_tester.get_test_summary(results)
                                        print(f"{color_cyan}{summary}{color_reset}")
                                    else:
                                        print(f"{color_red}Invalid option.{color_reset}")
                                        
                                    if bypass_choice != 'b':
                                        input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                        
                            elif obj_choice_num == 2:
                                # Data Exploration
                                data_menu_running = True
                                while data_menu_running:
                                    objection_tester.display_data_exploration_menu()
                                    data_choice = input(f"{color_yellow}Select data exploration option [1-5] or 'b': {color_reset}").strip().lower()
                                    
                                    if data_choice == 'b':
                                        data_menu_running = False
                                        continue
                                        
                                    if data_choice == '1':
                                        success, output_file, stdout, stderr = objection_tester.run_filesystem_scan()
                                        print(f"{color_green if success else color_red}Filesystem scan {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif data_choice == '2':
                                        success, output_file, stdout, stderr = objection_tester.run_database_analysis()
                                        print(f"{color_green if success else color_red}Database analysis {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif data_choice == '3':
                                        success, output_file, stdout, stderr = objection_tester.run_shared_preferences_scan()
                                        print(f"{color_green if success else color_red}Shared preferences scan {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif data_choice == '4':
                                        success, output_file, stdout, stderr = objection_tester.run_keystore_analysis()
                                        print(f"{color_green if success else color_red}Keystore analysis {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif data_choice == '5':
                                        results = objection_tester.run_data_leakage_check()
                                        summary = objection_tester.get_test_summary(results)
                                        print(f"{color_cyan}{summary}{color_reset}")
                                    else:
                                        print(f"{color_red}Invalid option.{color_reset}")
                                        
                                    if data_choice != 'b':
                                        input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                        
                            elif obj_choice_num == 3:
                                # Runtime Analysis
                                runtime_menu_running = True
                                while runtime_menu_running:
                                    objection_tester.display_runtime_analysis_menu()
                                    runtime_choice = input(f"{color_yellow}Select runtime analysis option [1-4] or 'b': {color_reset}").strip().lower()
                                    
                                    if runtime_choice == 'b':
                                        runtime_menu_running = False
                                        continue
                                        
                                    if runtime_choice == '1':
                                        success, output_file, stdout, stderr = objection_tester.run_class_enumeration()
                                        print(f"{color_green if success else color_red}Class enumeration {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif runtime_choice == '2':
                                        class_name = input("Enter class name (optional, leave blank for all): ").strip() or None
                                        success, output_file, stdout, stderr = objection_tester.run_method_enumeration(class_name)
                                        print(f"{color_green if success else color_red}Method enumeration {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif runtime_choice == '3':
                                        success, output_file, stdout, stderr = objection_tester.run_intent_monitoring()
                                        print(f"{color_green if success else color_red}Intent monitoring {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif runtime_choice == '4':
                                        success, output_file, stdout, stderr = objection_tester.run_memory_analysis()
                                        print(f"{color_green if success else color_red}Memory analysis {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    else:
                                        print(f"{color_red}Invalid option.{color_reset}")
                                        
                                    if runtime_choice != 'b':
                                        input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                        
                            elif obj_choice_num == 4:
                                # Network Monitoring
                                print(f"{color_yellow}Starting HTTP monitoring...{color_reset}")
                                success, output_file, stdout, stderr = objection_tester.run_http_monitoring()
                                print(f"{color_green if success else color_red}HTTP monitoring {'started' if success else 'failed'}: {output_file}{color_reset}")
                                input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                
                            elif obj_choice_num == 5:
                                # Application Information
                                print(f"{color_yellow}Getting application information...{color_reset}")
                                tests = [
                                    ("Activities", objection_tester.run_activities_enumeration),
                                    ("Services", objection_tester.run_services_enumeration),
                                    ("Permissions", objection_tester.run_permissions_analysis),
                                    ("Package Info", objection_tester.run_package_info)
                                ]
                                
                                results = []
                                for name, func in tests:
                                    print(f"  [*] Getting {name}...")
                                    success, output_file, stdout, stderr = func()
                                    results.append((name, success, output_file))
                                    
                                summary = objection_tester.get_test_summary(results)
                                print(f"{color_cyan}{summary}{color_reset}")
                                input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                
                            elif obj_choice_num == 6:
                                print(f"{color_yellow}Dynamic manipulation features coming soon...{color_reset}")
                                input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                
                            elif obj_choice_num == 7:
                                print(f"{color_yellow}Advanced testing features coming soon...{color_reset}")
                                input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                
                            elif obj_choice_num == 8:
                                # Quick Common Tests
                                quick_menu_running = True
                                while quick_menu_running:
                                    objection_tester.display_quick_tests_menu()
                                    quick_choice = input(f"{color_yellow}Select quick test option [1-4] or 'b': {color_reset}").strip().lower()
                                    
                                    if quick_choice == 'b':
                                        quick_menu_running = False
                                        continue
                                        
                                    if quick_choice == '1':
                                        results = objection_tester.run_basic_security_assessment()
                                        summary = objection_tester.get_test_summary(results)
                                        print(f"{color_cyan}{summary}{color_reset}")
                                    elif quick_choice == '2':
                                        results = objection_tester.run_data_leakage_check()
                                        summary = objection_tester.get_test_summary(results)
                                        print(f"{color_cyan}{summary}{color_reset}")
                                    elif quick_choice == '3':
                                        success, output_file, stdout, stderr = objection_tester._execute_objection_command("env", "quick_tests", "environment_info", "Get environment information")
                                        print(f"{color_green if success else color_red}Environment info {'completed' if success else 'failed'}: {output_file}{color_reset}")
                                    elif quick_choice == '4':
                                        print(f"{color_yellow}Running complete package analysis...{color_reset}")
                                        all_tests = [
                                            objection_tester.run_basic_security_assessment(),
                                            objection_tester.run_data_leakage_check()
                                        ]
                                        all_results = []
                                        for test_results in all_tests:
                                            all_results.extend(test_results)
                                        summary = objection_tester.get_test_summary(all_results)
                                        print(f"{color_cyan}{summary}{color_reset}")
                                    else:
                                        print(f"{color_red}Invalid option.{color_reset}")
                                        
                                    if quick_choice != 'b':
                                        input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                        
                            elif obj_choice_num == 9:
                                # Verify Target & Setup
                                print(f"{color_yellow}Verifying target and setup...{color_reset}")
                                
                                available, message = objection_tester.check_objection_available()
                                print(f"Objection Status: {color_green if available else color_red}{message}{color_reset}")
                                
                                if package_name or process_id:
                                    running, message = objection_tester.verify_target_running()
                                    print(f"Target Status: {color_green if running else color_red}{message}{color_reset}")
                                    
                                print(f"Output Directory: {color_cyan}{objection_tester.app_output_dir}{color_reset}")
                                input(f"{color_yellow}Press Enter to continue...{color_reset}")
                                
                        except Exception as e:
                            print(f"{color_red}Error in Objection menu: {str(e)}{color_reset}")
                            input(f"{color_yellow}Press Enter to continue...{color_reset}")
                    
                except ImportError:
                    print(f"{color_red}[!] Could not import objection_module. Make sure objection_module.py exists.{color_reset}")
                except Exception as e:
                    print(f"{color_red}[!] Error initializing Objection tester: {str(e)}{color_reset}")
                    


            elif choice_num == 24:
                # New option: Create/Launch AVD with Magisk+Xposed
                print(f"\n{color_yellow}Launching AVD with Magisk and Xposed (root, writable system)...{color_reset}")
                try:
                    import avd_magisk_xposed
                    avd_magisk_xposed.create_avd_with_magisk_xposed()
                    print(f"{color_green}AVD launch script executed. Check emulator window for progress.{color_reset}")
                except Exception as e:
                    print(f"{color_red}Error running avd_magisk_xposed: {e}{color_reset}")
                input(f"{color_yellow}Press Enter to continue...{color_reset}")

            elif choice_num == 25:
                # Sensitive Strings/Secrets Finder
                print(f"\n{color_yellow}Sensitive Strings/Secrets Finder{color_reset}")
                apk_path = input("Enter APK path (or leave blank to use last set path): ").strip() or None
                pentester = AndroidPentester(apk_path=apk_path)
                pentester._setup_adb_connection()
                results = pentester.find_sensitive_strings()
                if results:
                    print(f"{color_green}Sensitive strings/secrets found:{color_reset}")
                    for r in results:
                        print(f"{color_cyan}{r}{color_reset}")
                else:
                    print(f"{color_yellow}No sensitive strings or secrets found.{color_reset}")
                input(f"{color_yellow}Press Enter to continue...{color_reset}")

            elif choice_num == 26:
                # Automated Backup/Restore
                print(f"\n{color_yellow}Automated Backup/Restore{color_reset}")
                package = input("Enter package name to backup/restore: ").strip()
                pentester = AndroidPentester(apk_path=None)
                pentester._setup_adb_connection()
                print(f"{color_cyan}1.{color_reset} Backup app data\n{color_cyan}2.{color_reset} Restore app data\n{color_cyan}b.{color_reset} Back to main menu")
                br_choice = input("Select option [1-2] or 'b': ").strip().lower()
                if br_choice == '1':
                    backup_path = input("Enter backup output path (default: ./output/backup.ab): ").strip() or "./output/backup.ab"
                    pentester.adb_backup_app(package, backup_path)
                elif br_choice == '2':
                    backup_path = input("Enter backup file path to restore: ").strip()
                    pentester.adb_restore_app(package, backup_path)
                elif br_choice == 'b':
                    pass
                else:
                    print(f"{color_red}Invalid choice.{color_reset}")
                input(f"{color_yellow}Press Enter to continue...{color_reset}")

            elif choice_num == 27:
                # App Repackaging Utility
                print(f"\n{color_yellow}App Repackaging Utility{color_reset}")
                apk_path = input("Enter APK path to repackage: ").strip()
                output_path = input("Enter output path for repackaged APK (default: ./output/repackaged.apk): ").strip() or "./output/repackaged.apk"
                pentester = AndroidPentester(apk_path=apk_path)
                pentester.repackage_apk(output_path)
                input(f"{color_yellow}Press Enter to continue...{color_reset}")

            elif choice_num == 28:
                # Automated Uninstall/Cleaner
                print(f"\n{color_yellow}Automated Uninstall/Cleaner{color_reset}")
                package = input("Enter package name to uninstall and clean: ").strip()
                pentester = AndroidPentester(apk_path=None)
                pentester._setup_adb_connection()
                pentester.uninstall_app_and_clean(package)
                input(f"{color_yellow}Press Enter to continue...{color_reset}")

            elif choice_num == 29:
                print(f"{color_green}Exiting.{color_reset}")
                sys.exit(0)

        except Exception as e:
            if COLOR_ENABLED:
                print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            else:
                print(f"An error occurred: {e}")
                input("Press Enter to continue...")

        # Allow exit with '0' as well for user convenience
        if choice == '0':
            print("Exiting.")
            sys.exit(0)

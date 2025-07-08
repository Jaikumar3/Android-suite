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

VERSION = "1.0.0"

MENU_OPTIONS = [
    ("Install/verify tools (open installer)", "Install or verify all required tools in the ./tools directory."),
    ("Get PID for package name", "Find the process ID for a given Android package name."),
    ("Install APK via ADB", "Install an APK file to the connected Android device using ADB."),
    ("Uninstall APK via ADB", "Uninstall an app from the device using its package name."),
    ("Push file to device via ADB", "Copy a file from your computer to the Android device."),
    ("Pull file from device via ADB", "Copy a file from the Android device to your computer."),
    ("Collect device information", "Gather information about the connected Android device."),
    ("Setup Frida server (optional)", "Set up the Frida server on the device for dynamic analysis."),
    ("Stop Frida server on device", "Stop/kill the Frida server process on the device."),
    ("Get process list", "List all running processes on the device."),
    ("View/Save Logcat Output", "View or save the device's logcat output."),
    ("List installed packages", "List all installed package names on the connected device."),
    ("Dump APK with fridump", "Dump an APK's memory using fridump and Frida."),
    ("APKTool decompile APK", "Decompile an APK using APKTool."),
    ("Run APKLeaks on APK", "Scan an APK for secrets using APKLeaks."),
    ("Extract app data directory", "Extract the /data/data/<package> directory from the device (root required)."),
    ("Exit", "Exit the Android Suite."),
]


if __name__ == "__main__":
    from android_pentest import adb_install_apk, adb_uninstall_apk, adb_push_file, adb_pull_file, get_pid_for_package, run_apktool, run_apkleaks
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{Fore.GREEN if COLOR_ENABLED else ''}╔══════════════════════════════════════╗
║         Android Suite                ║
║         Author: Jai                  ║
║        Version: {VERSION:<10}           ║
╚══════════════════════════════════════╝{Style.RESET_ALL if COLOR_ENABLED else ''}
    """
    print(banner)
    help_text = """
Help - Android Suite Menu Options:
----------------------------------
"""
    for idx, (option, desc) in enumerate(MENU_OPTIONS, 1):
        if idx < 14:
            help_text += f"[ {idx:<2}] {option:<35} - {desc}\n"
        else:
            help_text += f"[ {chr(96+idx)} ] {option:<35} - {desc}\n"
    help_text += "[ b ] Back to main menu\n"

    while True:
        # Print menu
        print("")
        for idx, (option, _) in enumerate(MENU_OPTIONS, 1):
            if COLOR_ENABLED:
                print(f"{Fore.CYAN}[ {idx:>2}]{Style.RESET_ALL}  {Fore.WHITE}{option:<32}{Style.RESET_ALL}")
            else:
                print(f"[ {idx:>2}]  {option:<32}")
        if COLOR_ENABLED:
            print(f"{Fore.CYAN}[  b]{Style.RESET_ALL}  {Fore.WHITE}Back to main menu{Style.RESET_ALL}")
        else:
            print(f"[  b]  Back to main menu")
        print("")
        if COLOR_ENABLED:
            choice = input(f"{Fore.YELLOW}Select an option [1-17], 'b' to return, or 'h' for help: {Style.RESET_ALL}").strip().lower()
        else:
            choice = input(f"Select an option [1-17], 'b' to return, or 'h' for help: ").strip().lower()

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
            color_green = Fore.GREEN if COLOR_ENABLED else ''
            color_cyan = Fore.CYAN if COLOR_ENABLED else ''
            color_yellow = Fore.YELLOW if COLOR_ENABLED else ''
            color_red = Fore.RED if COLOR_ENABLED else ''
            color_white = Fore.WHITE if COLOR_ENABLED else ''
            color_reset = Style.RESET_ALL if COLOR_ENABLED else ''
            if choice_num == 10:
                # Get process list
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._check_android_tools()
                pentester._setup_adb_connection()
                procs = pentester.get_process_list()
                if not procs:
                    print(f"{color_yellow}No running processes found.{color_reset}")
                else:
                    for proc in procs:
                        print(f"{color_green}PID: {proc['pid']}, Name: {proc['name']}{color_reset}")
            elif choice_num == 1:
                print(f"\n{color_yellow}Launching installer (default location)...{color_reset}")
                import subprocess
                os.makedirs("tools", exist_ok=True)
                subprocess.run([sys.executable, "installer.py", "--tools-dir", "tools"], check=False)
            elif choice_num == 2:
                package = input("Enter package name (e.g. com.example.app): ").strip()
                if not package:
                    print(f"{color_yellow}No package name entered.{color_reset}")
                    continue
                matches = get_pid_for_package(package)
                if matches:
                    for pid, proc_name in matches:
                        print(f"{color_green}PID for {package}: {pid} (process: {proc_name}){color_reset}")
                else:
                    print(f"{color_yellow}No running process found for package: {package}{color_reset}")
            elif choice_num == 3:
                apk_path = input("Enter APK file path to install: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not apk_path or not os.path.exists(apk_path):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                    continue
                result = adb_install_apk(apk_path, device_id=device_id)
                print(f"{color_green if result else color_red}Install result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 4:
                package = input("Enter package name to uninstall: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not package:
                    print(f"{color_yellow}[!] No package name entered.{color_reset}")
                    continue
                result = adb_uninstall_apk(package, device_id=device_id)
                print(f"{color_green if result else color_red}Uninstall result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 5:
                local_path = input("Enter local file path to push: ").strip()
                remote_path = input("Enter remote path on device: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not local_path or not os.path.exists(local_path):
                    print(f"{color_red}[!] Local file not found.{color_reset}")
                    continue
                if not remote_path:
                    print(f"{color_yellow}[!] No remote path entered.{color_reset}")
                    continue
                result = adb_push_file(local_path, remote_path, device_id=device_id)
                print(f"{color_green if result else color_red}Push result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 6:
                remote_path = input("Enter remote file path on device to pull: ").strip()
                local_path = input("Enter local destination path: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                if not remote_path:
                    print(f"{color_yellow}[!] No remote path entered.{color_reset}")
                    continue
                if not local_path:
                    print(f"{color_yellow}[!] No local destination path entered.{color_reset}")
                    continue
                result = adb_pull_file(remote_path, local_path, device_id=device_id)
                print(f"{color_green if result else color_red}Pull result: {'Success' if result else 'Failed'}{color_reset}")
            elif choice_num == 7:
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._check_android_tools()
                pentester._setup_adb_connection()
                info = pentester._collect_device_info()
                if not info:
                    print(f"{color_red}No device information could be collected.{color_reset}")
                else:
                    print(f"{color_green}Device info:{color_reset}")
                    for k, v in info.items():
                        print(f"{color_cyan}{k}: {color_white}{v}{color_reset}")
            elif choice_num == 8:
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._check_android_tools()
                pentester._setup_adb_connection()
                pentester._setup_frida_server_optional()
                print(f"{color_green}Frida server setup complete (if no errors above).{color_reset}")
            elif choice_num == 9:
                # Stop Frida server on device
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._check_android_tools()
                pentester._setup_adb_connection()
                pentester.menu_stop_frida_server()
            elif choice_num == 10:
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._check_android_tools()
                pentester._setup_adb_connection()
                procs = pentester.get_process_list()
                if not procs:
                    print(f"{color_yellow}No running processes found.{color_reset}")
                else:
                    for proc in procs:
                        print(f"{color_green}PID: {proc['pid']}, Name: {proc['name']}{color_reset}")
            elif choice_num == 11:
                # View/Save Logcat Output
                device = input("Enter device ID (optional): ").strip() or None
                pentester = AndroidPentester(apk_path=None, app_name=None, device_id=device)
                pentester._check_android_tools()
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
            elif choice_num == 12:
                # List installed packages
                device_id = input("Enter device ID (optional): ").strip() or None
                from android_pentest import list_installed_packages
                packages = list_installed_packages(device_id=device_id)
                if not packages:
                    print(f"{color_yellow}No packages found or device not connected.{color_reset}")
                else:
                    print(f"\n{color_green}Installed packages:{color_reset}")
                    for pkg in packages:
                        print(f"{color_cyan}{pkg}{color_reset}")
            elif choice_num == 13:
                # Dump APK with fridump
                apk = input("Enter APK file path: ").strip()
                device = input("Enter device ID (optional): ").strip() or None
                name = input("Enter package name (required): ").strip()
                if not apk or not os.path.exists(apk):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                    continue
                if not name:
                    print(f"{color_yellow}[!] Package name is required for fridump.{color_reset}")
                    continue
                pentester = AndroidPentester(apk_path=apk, app_name=name, device_id=device)
                pentester._check_android_tools()
                pentester._setup_adb_connection()
                pentester._setup_frida_server_optional()
                output_dir = input("Enter output directory for fridump (leave blank for ./output/fridump): ").strip() or 'output/fridump'
                os.makedirs(output_dir, exist_ok=True)
                pentester.run_fridump(output_dir=output_dir)
                print(f"{color_green}Fridump completed. Output in {output_dir}{color_reset}")
            elif choice_num == 14:
                # APKTool decompile APK
                apk = input("Enter APK file path to decompile: ").strip()
                output_dir = input("Enter output directory for apktool [leave blank for ./output/apktool]: ").strip() or 'output/apktool'
                if not apk or not os.path.exists(apk):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                else:
                    os.makedirs(output_dir, exist_ok=True)
                    run_apktool(apk, output_dir=output_dir)
                    print(f"{color_green}APKTool decompilation complete. Output in {output_dir}{color_reset}")
            elif choice_num == 15:
                # Run APKLeaks on APK
                apk = input("Enter APK file path to scan: ").strip()
                output_dir = input("Enter output directory for apkleaks [leave blank for ./output/apkleaks]: ").strip() or 'output/apkleaks'
                if not apk or not os.path.exists(apk):
                    print(f"{color_red}[!] APK file not found.{color_reset}")
                else:
                    os.makedirs(output_dir, exist_ok=True)
                    run_apkleaks(apk, output_dir=output_dir)
                    print(f"{color_green}APKLeaks scan complete. Output in {output_dir}{color_reset}")
            elif choice_num == 16:
                # Extract app data directory
                from android_pentest import extract_app_data_directory
                package = input("Enter package name to extract data for: ").strip()
                device_id = input("Enter device ID (optional): ").strip() or None
                dest_dir = input("Enter local destination directory (leave blank for ./output/appdata): ").strip() or "output/appdata"
                if not package:
                    print(f"{color_yellow}[!] No package name entered.{color_reset}")
                    continue
                os.makedirs(dest_dir, exist_ok=True)
                result, message = extract_app_data_directory(package, dest_dir, device_id=device_id)
                color = color_green if result else color_red
                print(f"{color}{message}{color_reset}")
            elif choice_num == 17:
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

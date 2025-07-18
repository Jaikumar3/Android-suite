#!/usr/bin/env python3
"""
Objection Testing Module for Android Pentesting
Comprehensive Objection-based testing suite with organized output
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class ObjectionTester:
    """Main class for Objection-based Android penetration testing"""
    
    def __init__(self, package_name=None, process_id=None, device_id=None, output_dir="./output/objection"):
        """
        Initialize the Objection Tester
        
        Args:
            package_name (str): Android package name (e.g., com.example.app)
            process_id (int): Process ID of running application
            device_id (str): Specific Android device ID
            output_dir (str): Directory for output files
        """
        self.package_name = package_name
        self.process_id = process_id
        self.device_id = device_id
        self.output_dir = Path(output_dir)
        self.session_active = False
        
        # Create output directory structure
        self._create_output_structure()
        
        # Objection command base
        self.objection_base_cmd = self._build_base_command()
        
    def _create_output_structure(self):
        """Create organized output directory structure"""
        if self.package_name:
            app_dir = self.output_dir / self.package_name
        elif self.process_id:
            app_dir = self.output_dir / f"pid_{self.process_id}"
        else:
            app_dir = self.output_dir / "unknown_app"
            
        # Create subdirectories for different test categories
        categories = [
            "security_bypasses",
            "data_exploration", 
            "runtime_analysis",
            "network_monitoring",
            "application_info",
            "dynamic_manipulation",
            "advanced_testing",
            "quick_tests",
            "session_logs"
        ]
        
        for category in categories:
            (app_dir / category).mkdir(parents=True, exist_ok=True)
            
        self.app_output_dir = app_dir
        
    def _build_base_command(self):
        """Build base objection command with device and target options"""
        cmd = ["objection"]
        
        # Add device serial if specified
        if self.device_id:
            cmd.extend(["-S", self.device_id])
            
        # Add target specification
        if self.package_name:
            cmd.extend(["-g", self.package_name])
        elif self.process_id:
            cmd.extend(["-g", str(self.process_id)])
            
        return cmd
        
    def _execute_objection_command(self, command, category, test_name, description=""):
        """
        Execute an objection command and save output to file
        
        Args:
            command (str): Objection command to execute
            category (str): Test category for file organization
            test_name (str): Name of the test for filename
            description (str): Test description for output header
        
        Returns:
            tuple: (success, output_file_path, stdout, stderr)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.app_output_dir / category / f"{test_name}_{timestamp}.txt"
        
        # Build full command
        full_cmd = self.objection_base_cmd + ["run", command]
        
        print(f"[*] Executing: {' '.join(full_cmd)}")
        print(f"[*] Output will be saved to: {output_file}")
        
        try:
            # Execute command
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            
            # Prepare output content
            output_content = self._format_output(
                command=command,
                description=description,
                timestamp=timestamp,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
                
            success = result.returncode == 0
            return success, str(output_file), result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 60 seconds"
            output_content = self._format_output(
                command=command,
                description=description,
                timestamp=timestamp,
                stdout="",
                stderr=error_msg,
                returncode=-1
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
                
            return False, str(output_file), "", error_msg
            
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            output_content = self._format_output(
                command=command,
                description=description,
                timestamp=timestamp,
                stdout="",
                stderr=error_msg,
                returncode=-1
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
                
            return False, str(output_file), "", error_msg
            
    def _format_output(self, command, description, timestamp, stdout, stderr, returncode):
        """Format output with header information"""
        header = f"""
{'='*80}
OBJECTION TESTING OUTPUT
{'='*80}
Timestamp: {timestamp}
Target: {self.package_name or f"PID {self.process_id}" or "Unknown"}
Device: {self.device_id or "Default"}
Command: {command}
Description: {description}
Return Code: {returncode}
{'='*80}

"""
        
        content = header
        
        if stdout:
            content += f"STDOUT:\n{'-'*40}\n{stdout}\n\n"
            
        if stderr:
            content += f"STDERR:\n{'-'*40}\n{stderr}\n\n"
            
        content += f"{'='*80}\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*80}\n"
        
        return content
        
    def check_objection_available(self):
        """Check if Objection is available and can connect to target"""
        try:
            # Check if objection is installed
            result = subprocess.run(["objection", "version"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, "Objection not found or not working"
                
            return True, "Objection is installed and available"
            
        except Exception as e:
            return False, f"Error checking Objection: {str(e)}"
            
    def check_frida_server_status(self):
        """Check if Frida server is running on the target device"""
        try:
            # Check if adb is available
            adb_cmd = ["adb"]
            if self.device_id:
                adb_cmd.extend(["-s", self.device_id])
            adb_cmd.extend(["shell", "ps | grep frida-server"])
            
            result = subprocess.run(adb_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "frida-server" in result.stdout:
                return True, "Frida server is running on device"
            else:
                return False, "Frida server is not running on device. Please start Frida server first."
                
        except Exception as e:
            return False, f"Error checking Frida server: {str(e)}"
            
    def check_device_connection(self):
        """Check if target device is connected and accessible"""
        try:
            # Check Android devices
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, "ADB not working or no devices connected"
                
            devices = []
            for line in result.stdout.split('\n'):
                if '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    devices.append(device_id)
                    
            if not devices:
                return False, "No Android devices connected"
                
            if self.device_id and self.device_id not in devices:
                return False, f"Specified device {self.device_id} not found. Available devices: {devices}"
                
            return True, f"Device connection OK. Available devices: {devices}"
            
        except Exception as e:
            return False, f"Error checking device connection: {str(e)}"
            
    def verify_target_running(self):
        """Verify target application is running"""
        if not self.package_name and not self.process_id:
            return False, "No target package or PID specified"
            
        try:
            # Use adb to check if app is running
            if self.package_name:
                cmd = ["adb"]
                if self.device_id:
                    cmd.extend(["-s", self.device_id])
                cmd.extend(["shell", "pidof", self.package_name])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and result.stdout.strip():
                    return True, f"Package {self.package_name} is running (PID: {result.stdout.strip()})"
                else:
                    return False, f"Package {self.package_name} is not running"
            else:
                # Check by PID
                cmd = ["adb"]
                if self.device_id:
                    cmd.extend(["-s", self.device_id])
                cmd.extend(["shell", "ps", "-p", str(self.process_id)])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and str(self.process_id) in result.stdout:
                    return True, f"Process {self.process_id} is running"
                else:
                    return False, f"Process {self.process_id} is not running"
                    
        except Exception as e:
            return False, f"Error verifying target: {str(e)}"

    def run_system_diagnostics(self):
        """Run comprehensive system diagnostics for Objection testing"""
        print("\n" + "="*60)
        print("🔍 OBJECTION SYSTEM DIAGNOSTICS")
        print("="*60)
        
        # Check 1: Objection installation
        print("\n[1/6] Checking Objection installation...")
        objection_ok, objection_msg = self.check_objection_available()
        print(f"    {'✅' if objection_ok else '❌'} {objection_msg}")
        
        # Check 2: Device connection
        print("\n[2/6] Checking device connection...")
        device_ok, device_msg = self.check_device_connection()
        print(f"    {'✅' if device_ok else '❌'} {device_msg}")
        
        # Check 3: Frida server status
        print("\n[3/6] Checking Frida server status...")
        frida_ok, frida_msg = self.check_frida_server_status()
        print(f"    {'✅' if frida_ok else '❌'} {frida_msg}")
        
        # Check 4: Target application
        print("\n[4/6] Checking target application...")
        if self.package_name or self.process_id:
            target_ok, target_msg = self.verify_target_running()
            print(f"    {'✅' if target_ok else '❌'} {target_msg}")
        else:
            print(f"    ⚠️  No target specified (package name or PID)")
            target_ok = False
        
        # Check 5: Output directories
        print("\n[5/6] Checking output directories...")
        try:
            if self.app_output_dir.exists():
                print(f"    ✅ Output directory ready: {self.app_output_dir}")
                output_ok = True
            else:
                print(f"    ⚠️  Output directory will be created: {self.app_output_dir}")
                output_ok = True
        except Exception as e:
            print(f"    ❌ Output directory error: {str(e)}")
            output_ok = False
        
        # Check 6: Overall readiness
        print("\n[6/6] Overall system readiness...")
        all_ok = objection_ok and device_ok and frida_ok and target_ok and output_ok
        
        if all_ok:
            print("    ✅ All systems ready for Objection testing!")
            return True
        else:
            print("    ❌ Some issues found. Please resolve them before testing.")
            
            # Provide solutions
            print("\n💡 SOLUTIONS:")
            if not objection_ok:
                print("    • Install Objection: pip install objection")
            if not device_ok:
                print("    • Connect Android device/emulator and enable USB debugging")
                print("    • Run: adb devices")
            if not frida_ok:
                print("    • Start Frida server on device:")
                print("      - Download frida-server for your device architecture")
                print("      - Push to device: adb push frida-server /data/local/tmp/")
                print("      - Make executable: adb shell chmod 755 /data/local/tmp/frida-server")
                print("      - Run as root: adb shell su -c '/data/local/tmp/frida-server &'")
            if not target_ok:
                print("    • Specify a valid package name or PID")
                print("    • Make sure the target app is running")
            
            return False
            
        print("="*60)

    # =================== SECURITY BYPASSES ===================
    
    def run_root_detection_bypass(self):
        """Bypass root detection mechanisms"""
        return self._execute_objection_command(
            "android root disable",
            "security_bypasses",
            "root_detection_bypass",
            "Disable root detection mechanisms in the application"
        )
        
    def run_ssl_pinning_bypass(self):
        """Bypass SSL certificate pinning"""
        return self._execute_objection_command(
            "android sslpinning disable",
            "security_bypasses", 
            "ssl_pinning_bypass",
            "Disable SSL certificate pinning to allow traffic interception"
        )
        
    def run_anti_debugging_bypass(self):
        """Bypass anti-debugging protection"""
        return self._execute_objection_command(
            "android hooking disable",
            "security_bypasses",
            "anti_debugging_bypass", 
            "Disable anti-debugging protection mechanisms"
        )
        
    def run_biometric_bypass(self):
        """Bypass biometric authentication"""
        return self._execute_objection_command(
            "android biometrics disable",
            "security_bypasses",
            "biometric_bypass",
            "Bypass fingerprint and face authentication"
        )
        
    def run_all_security_bypasses(self):
        """Run all security bypass tests"""
        results = []
        bypasses = [
            ("Root Detection", self.run_root_detection_bypass),
            ("SSL Pinning", self.run_ssl_pinning_bypass), 
            ("Anti-Debugging", self.run_anti_debugging_bypass),
            ("Biometric Auth", self.run_biometric_bypass)
        ]
        
        for name, func in bypasses:
            print(f"\n[*] Running {name} bypass...")
            success, output_file, stdout, stderr = func()
            results.append((name, success, output_file))
            
        return results

    # =================== DATA EXPLORATION ===================
    
    def run_filesystem_scan(self):
        """Scan for readable/writable directories"""
        return self._execute_objection_command(
            "android filesystem readable",
            "data_exploration",
            "filesystem_scan",
            "Scan for readable and writable directories in the application"
        )
        
    def run_database_analysis(self):
        """Analyze SQLite databases"""
        return self._execute_objection_command(
            "sqlite list",
            "data_exploration",
            "database_analysis",
            "List and analyze SQLite databases used by the application"
        )
        
    def run_shared_preferences_scan(self):
        """Scan shared preferences"""
        return self._execute_objection_command(
            "android preferences list",
            "data_exploration",
            "shared_preferences_scan",
            "List all shared preference files and their contents"
        )
        
    def run_keystore_analysis(self):
        """Analyze Android keystore"""
        return self._execute_objection_command(
            "android keystore list",
            "data_exploration",
            "keystore_analysis",
            "Analyze Android keystore entries and certificates"
        )

    # =================== RUNTIME ANALYSIS ===================
    
    def run_class_enumeration(self):
        """Enumerate loaded classes"""
        return self._execute_objection_command(
            "android hooking list classes",
            "runtime_analysis",
            "class_enumeration",
            "List all loaded classes in the application"
        )
        
    def run_method_enumeration(self, class_name=None):
        """Enumerate methods for a specific class"""
        if class_name:
            command = f"android hooking list methods {class_name}"
            description = f"List methods for class: {class_name}"
        else:
            command = "android hooking list methods"
            description = "List methods for all classes"
            
        return self._execute_objection_command(
            command,
            "runtime_analysis",
            "method_enumeration",
            description
        )
        
    def run_intent_monitoring(self):
        """Monitor application intents"""
        return self._execute_objection_command(
            "android intent monitor start",
            "runtime_analysis",
            "intent_monitoring",
            "Monitor and log application intents"
        )
        
    def run_memory_analysis(self):
        """Analyze loaded modules and memory"""
        return self._execute_objection_command(
            "memory list modules",
            "runtime_analysis",
            "memory_analysis",
            "List loaded modules and analyze memory usage"
        )

    # =================== NETWORK MONITORING ===================
    
    def run_http_monitoring(self):
        """Monitor HTTP/HTTPS traffic"""
        return self._execute_objection_command(
            "android http start",
            "network_monitoring",
            "http_monitoring",
            "Start monitoring HTTP/HTTPS traffic"
        )
        
    def run_proxy_configuration_check(self):
        """Check proxy configuration"""
        return self._execute_objection_command(
            "android proxy status",
            "network_monitoring",
            "proxy_configuration",
            "Check current proxy configuration and settings"
        )

    # =================== APPLICATION INFORMATION ===================
    
    def run_activities_enumeration(self):
        """List application activities"""
        return self._execute_objection_command(
            "android activities list",
            "application_info",
            "activities_enumeration",
            "List all application activities and their properties"
        )
        
    def run_services_enumeration(self):
        """List application services"""
        return self._execute_objection_command(
            "android services list",
            "application_info",
            "services_enumeration", 
            "List all application services and their status"
        )
        
    def run_permissions_analysis(self):
        """Analyze application permissions"""
        return self._execute_objection_command(
            "android permissions list",
            "application_info",
            "permissions_analysis",
            "Analyze application permissions and their usage"
        )
        
    def run_package_info(self):
        """Get detailed package information"""
        if self.package_name:
            command = f"android package info {self.package_name}"
        else:
            command = "android package info"
            
        return self._execute_objection_command(
            command,
            "application_info",
            "package_information",
            "Get detailed package information and metadata"
        )

    # =================== QUICK COMMON TESTS ===================
    
    def run_basic_security_assessment(self):
        """Run basic security assessment (combination of common tests)"""
        print("[*] Running Basic Security Assessment...")
        
        results = []
        tests = [
            ("Environment Info", lambda: self._execute_objection_command("env", "quick_tests", "environment_info", "Get environment information")),
            ("Root Status", lambda: self._execute_objection_command("android root status", "quick_tests", "root_status", "Check root status")),
            ("SSL Pinning Status", lambda: self._execute_objection_command("android sslpinning list", "quick_tests", "ssl_pinning_status", "Check SSL pinning implementation")),
            ("Activities", self.run_activities_enumeration),
            ("Permissions", self.run_permissions_analysis),
            ("Readable Directories", self.run_filesystem_scan)
        ]
        
        for name, func in tests:
            print(f"  [*] Running {name}...")
            try:
                success, output_file, stdout, stderr = func()
                results.append((name, success, output_file))
                if success:
                    print(f"  [+] {name} completed successfully")
                else:
                    print(f"  [!] {name} failed")
            except Exception as e:
                print(f"  [!] {name} error: {str(e)}")
                results.append((name, False, f"Error: {str(e)}"))
                
        return results
        
    def run_data_leakage_check(self):
        """Check for potential data leakage"""
        results = []
        tests = [
            ("Shared Preferences", self.run_shared_preferences_scan),
            ("Database Analysis", self.run_database_analysis),
            ("Filesystem Scan", self.run_filesystem_scan),
            ("Keystore Analysis", self.run_keystore_analysis)
        ]
        
        for name, func in tests:
            print(f"  [*] Checking {name}...")
            success, output_file, stdout, stderr = func()
            results.append((name, success, output_file))
            
        return results

    # =================== MENU SYSTEM ===================
    
    def display_main_menu(self):
        """Display main objection testing menu"""
        target_info = self.package_name or f"PID {self.process_id}" or "Unknown"
        
        print(f"""
╔══════════════════════════════════════╗
║           OBJECTION TESTING          ║
║         Target: {target_info:<20} ║
╚══════════════════════════════════════╝

[  1]  Security Bypasses              - Root, SSL, Anti-debug, Biometric bypasses
[  2]  Data Exploration               - Files, Databases, Preferences, Keystore  
[  3]  Runtime Analysis               - Method hooking, Intent monitoring, Memory
[  4]  Network Monitoring             - HTTP/HTTPS traffic, Proxy configuration
[  5]  Application Information        - Activities, Services, Permissions, Certificates
[  6]  Dynamic Manipulation           - Method modification, Code injection
[  7]  Advanced Testing               - Custom scripts, Specialized tests
[  8]  Quick Common Tests             - Most used pentesting commands
[  9]  Verify Target & Setup          - Check if target is running and accessible
[ 10]  System Diagnostics             - Complete system health check
[  b]  Back to main menu
""")

    def display_security_bypasses_menu(self):
        """Display enhanced security bypasses submenu"""
        print(f"""
╔══════════════════════════════════════╗
║         SECURITY BYPASSES            ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

ROOT DETECTION:
[  1]  Check Root Status              - Check current root detection status
[  2]  Root Detection Bypass          - Disable root detection mechanisms
[  3]  Simulate Root Environment      - Simulate root for testing

SSL/TLS SECURITY:
[  4]  Check SSL Pinning              - Check current SSL pinning implementation
[  5]  SSL Pinning Bypass             - Disable SSL certificate pinning
[  6]  SSL Kill Switch                - Disable all SSL pinning mechanisms
[  7]  Certificate Transparency Bypass - Bypass cert transparency checks

ANTI-DEBUGGING:
[  8]  Check Debugger Detection       - Check anti-debugging mechanisms
[  9]  Anti-Debugging Bypass          - Disable debugging protection
[ 10]  Frida Detection Bypass         - Bypass Frida detection
[ 11]  Hook Detection Bypass          - Bypass runtime hook detection

OTHER SECURITY:
[ 12]  Emulator Detection Check       - Check emulator detection mechanisms
[ 13]  Biometric Authentication Bypass - Bypass fingerprint/face auth
[ 14]  Run All Security Bypasses      - Execute all bypass techniques

[  b]  Back to Objection menu
""")

    def display_data_exploration_menu(self):
        """Display enhanced data exploration submenu"""
        print(f"""
╔══════════════════════════════════════╗
║         DATA EXPLORATION             ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

FILE SYSTEM:
[  1]  File System Scan               - Find readable/writable directories
[  2]  Detailed File Listing          - Detailed listing with permissions
[  3]  Find Sensitive Files           - Find keys, certificates, keystores
[  4]  Download Files                 - Download specific files from device
[  5]  Search File Contents           - Search for patterns in files

DATABASES:
[  6]  List Databases                 - List available SQLite databases
[  7]  Database Analysis              - Analyze SQLite databases
[  8]  Dump All Databases             - Synchronize and dump all database contents

PREFERENCES & STORAGE:
[  9]  Shared Preferences Scan        - Examine preference files
[ 10]  Dump Shared Preferences        - Dump all shared preferences with values
[ 11]  Keystore Analysis              - Analyze Android keystore
[ 12]  Dump Keystore Entries          - Dump keystore entries and certificates

QUICK ACTIONS:
[ 13]  Data Leakage Check             - Run all data exploration tests
[ 14]  Search for Passwords           - Search files for 'password' pattern
[ 15]  Search for Tokens              - Search files for 'token' pattern

[  b]  Back to Objection menu
""")

    def display_runtime_analysis_menu(self):
        """Display enhanced runtime analysis submenu"""
        print(f"""
╔══════════════════════════════════════╗
║         RUNTIME ANALYSIS             ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

CLASS & METHOD EXPLORATION:
[  1]  Class Enumeration              - List all loaded classes
[  2]  Method Enumeration             - List methods for classes
[  3]  Search Classes                 - Search classes by pattern (crypto, auth, etc.)
[  4]  Search Methods                 - Search methods by pattern (encrypt, login, etc.)

HOOKING & MONITORING:
[  5]  Hook Class Methods             - Hook all methods in specific class
[  6]  Hook Specific Method           - Hook individual method
[  7]  Intent Monitoring              - Monitor application intents
[  8]  Thread List                    - List active threads and jobs

MEMORY ANALYSIS:
[  9]  Memory Analysis                - Analyze loaded modules
[ 10]  Loaded Libraries               - List all loaded libraries
[ 11]  Heap Search                    - Search heap for instances
[ 12]  Memory Dump                    - Dump memory contents

QUICK SEARCHES:
[ 13]  Search Crypto Classes          - Find cryptography-related classes
[ 14]  Search Auth Methods            - Find authentication methods
[ 15]  Search Network Classes         - Find network-related classes

[  b]  Back to Objection menu
""")

    def display_quick_tests_menu(self):
        """Display enhanced quick tests submenu"""
        print(f"""
╔══════════════════════════════════════╗
║         QUICK COMMON TESTS           ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

ESSENTIAL SECURITY CHECKS:
[  1]  Basic Security Assessment      - Essential security checks
[  2]  Data Leakage Check             - Check for data exposure
[  3]  Common Vulnerability Scan      - Scan for common vulnerabilities

INFORMATION GATHERING:
[  4]  Environment Information        - Get app environment details
[  5]  Complete Package Analysis      - Comprehensive app analysis
[  6]  Security Configuration Review  - Review security configurations

PENETRATION TESTING QUICK WINS:
[  7]  Root + SSL Bypass Combo        - Quick bypass of root and SSL
[  8]  Data Extraction Bundle         - Extract all accessible data
[  9]  Runtime Manipulation Test      - Quick runtime manipulation tests

REPORTING:
[ 10]  Generate Quick Report          - Generate summary report
[ 11]  Export Findings                - Export findings to file
[ 12]  Security Score Assessment      - Get security score

[  b]  Back to Objection menu
""")

    def display_network_monitoring_menu(self):
        """Display enhanced network monitoring submenu"""
        print(f"""
╔══════════════════════════════════════╗
║       NETWORK MONITORING             ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

TRAFFIC MONITORING:
[  1]  HTTP/HTTPS Monitoring          - Monitor HTTP/HTTPS traffic
[  2]  Start HTTP Capture             - Start capturing HTTP/HTTPS traffic
[  3]  Stop HTTP Capture              - Stop capturing HTTP/HTTPS traffic
[  4]  Network Monitor                - Monitor active network connections

PROXY CONFIGURATION:
[  5]  Check Proxy Configuration      - Check current proxy settings
[  6]  Set Proxy (Burp)               - Set proxy to 127.0.0.1:8080
[  7]  Set Custom Proxy               - Set custom proxy configuration
[  8]  Clear Proxy                    - Clear proxy configuration

NETWORK INFORMATION:
[  9]  Network Interfaces             - List network interfaces
[ 10]  SSL/TLS Configuration          - Check SSL/TLS configuration
[ 11]  Certificate Information        - Get certificate details

[  b]  Back to Objection menu
""")

    def display_application_info_menu(self):
        """Display enhanced application information submenu"""
        print(f"""
╔══════════════════════════════════════╗
║      APPLICATION INFORMATION         ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

COMPONENTS:
[  1]  Activities Enumeration         - List application activities
[  2]  Services Enumeration           - List application services
[  3]  Content Providers              - List content providers
[  4]  Broadcast Receivers            - List broadcast receivers
[  5]  Intent Filters                 - List intent filters

PERMISSIONS & SECURITY:
[  6]  Permissions Analysis           - Analyze application permissions
[  7]  Package Information            - Get detailed package information
[  8]  Application Signature          - Get application signature info

ENVIRONMENT:
[  9]  Application Environment        - Get app environment variables
[ 10]  Device Information             - Get detailed device information
[ 11]  Loaded Libraries               - List loaded libraries and modules

[  b]  Back to Objection menu
""")

    def display_dynamic_manipulation_menu(self):
        """Display dynamic manipulation submenu"""
        print(f"""
╔══════════════════════════════════════╗
║      DYNAMIC MANIPULATION           ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

METHOD MANIPULATION:
[  1]  Override Method Return         - Override method to return specific value
[  2]  Hook and Modify Method         - Hook method and modify behavior
[  3]  Bypass Method Execution        - Skip method execution entirely

APPLICATION CONTROL:
[  4]  Spawn Application              - Spawn app with Frida injection
[  5]  Kill Application               - Terminate application
[  6]  Restart with Hooks             - Restart app with pre-configured hooks

MEMORY MANIPULATION:
[  7]  Memory Dump                    - Dump memory contents
[  8]  Memory Search & Replace        - Search and replace memory values
[  9]  Module Injection               - Inject custom modules

ADVANCED:
[ 10]  Custom Script Execution        - Execute custom Frida scripts
[ 11]  Runtime Code Injection         - Inject code at runtime
[ 12]  Class Modification             - Modify class definitions

[  b]  Back to Objection menu
""")

    def display_advanced_testing_menu(self):
        """Display advanced testing submenu"""
        print(f"""
╔══════════════════════════════════════╗
║        ADVANCED TESTING              ║
║         Target: {self.package_name or f"PID {self.process_id}" or "Unknown":<20} ║
╚══════════════════════════════════════╝

SPECIALIZED TESTS:
[  1]  OWASP Mobile Top 10            - Run OWASP mobile security tests
[  2]  Cryptography Analysis          - Analyze crypto implementations
[  3]  Authentication Bypass Tests    - Test authentication mechanisms
[  4]  Session Management Tests       - Test session handling

CUSTOM SCRIPTS:
[  5]  Load Custom Frida Script       - Load and execute custom script
[  6]  Execute JavaScript Code        - Execute custom JavaScript
[  7]  Python Integration             - Run Python-based tests

COMPLIANCE TESTING:
[  8]  PCI DSS Mobile Tests           - Payment card industry tests
[  9]  GDPR Privacy Tests             - Data protection compliance
[ 10]  Banking Security Tests         - Financial app security tests

AUTOMATION:
[ 11]  Automated Vulnerability Scan   - Comprehensive vulnerability scan
[ 12]  Generate Security Report       - Create detailed security report
[ 13]  Export Test Results            - Export results in various formats

[  b]  Back to Objection menu
""")

    def get_test_summary(self, results):
        """Generate summary of test results"""
        total_tests = len(results)
        successful_tests = sum(1 for _, success, _ in results if success)
        failed_tests = total_tests - successful_tests
        
        summary = f"""
╔══════════════════════════════════════╗
║            TEST SUMMARY              ║
╚══════════════════════════════════════╝

Total Tests Run: {total_tests}
Successful: {successful_tests}
Failed: {failed_tests}
Success Rate: {(successful_tests/total_tests*100):.1f}%

Output Directory: {self.app_output_dir}

Test Results:
"""
        
        for name, success, output_file in results:
            status = "[+]" if success else "[!]"
            summary += f"{status} {name:<30} -> {output_file}\n"
            
        return summary

    # =================== ENHANCED SECURITY BYPASSES ===================
    
    def run_root_detection_check(self):
        """Check current root detection status"""
        return self._execute_objection_command(
            "android root status",
            "security_bypasses",
            "root_detection_check",
            "Check current root detection status"
        )
    
    def run_root_detection_simulate(self):
        """Simulate root environment"""
        return self._execute_objection_command(
            "android root simulate",
            "security_bypasses",
            "root_simulation",
            "Simulate root environment for testing"
        )
    
    def run_ssl_pinning_check(self):
        """Check SSL pinning implementation"""
        return self._execute_objection_command(
            "android sslpinning list",
            "security_bypasses",
            "ssl_pinning_check",
            "Check current SSL pinning implementation"
        )
    
    def run_ssl_kill_switch(self):
        """Enable SSL kill switch"""
        return self._execute_objection_command(
            "android sslpinning disable --all",
            "security_bypasses",
            "ssl_kill_switch",
            "Disable all SSL pinning mechanisms"
        )
    
    def run_certificate_transparency_bypass(self):
        """Bypass certificate transparency checks"""
        return self._execute_objection_command(
            "android certificate_transparency disable",
            "security_bypasses",
            "cert_transparency_bypass",
            "Bypass certificate transparency validation"
        )
    
    def run_debugger_detection_check(self):
        """Check anti-debugging mechanisms"""
        return self._execute_objection_command(
            "android anti_debugging list",
            "security_bypasses",
            "debugger_detection_check",
            "Check anti-debugging mechanisms in place"
        )
    
    def run_frida_detection_bypass(self):
        """Bypass Frida detection"""
        return self._execute_objection_command(
            "android frida_detection disable",
            "security_bypasses",
            "frida_detection_bypass",
            "Bypass Frida detection mechanisms"
        )
    
    def run_emulator_detection_check(self):
        """Check emulator detection"""
        return self._execute_objection_command(
            "android emulator status",
            "security_bypasses",
            "emulator_detection_check",
            "Check emulator detection mechanisms"
        )
    
    def run_hook_detection_bypass(self):
        """Bypass hook detection"""
        return self._execute_objection_command(
            "android hook_detection disable",
            "security_bypasses",
            "hook_detection_bypass",
            "Bypass runtime hook detection"
        )

    # =================== ENHANCED DATA EXPLORATION ===================
    
    def run_file_listing_detailed(self):
        """Detailed file system listing"""
        return self._execute_objection_command(
            "file ls -la",
            "data_exploration",
            "file_listing_detailed",
            "Detailed file system listing with permissions"
        )
    
    def run_find_sensitive_files(self):
        """Find sensitive files by pattern"""
        return self._execute_objection_command(
            "file find . -name '*.key' -o -name '*.p12' -o -name '*.jks' -o -name '*.keystore'",
            "data_exploration",
            "find_sensitive_files",
            "Find sensitive files (keys, certificates, keystores)"
        )
    
    def run_database_dump_all(self):
        """Dump all database contents"""
        return self._execute_objection_command(
            "sqlite sync",
            "data_exploration",
            "database_dump_all",
            "Synchronize and dump all database contents"
        )
    
    def run_shared_prefs_dump(self):
        """Dump shared preferences"""
        return self._execute_objection_command(
            "android preferences list --verbose",
            "data_exploration",
            "shared_prefs_dump",
            "Dump all shared preferences with values"
        )
    
    def run_keystore_dump(self):
        """Dump keystore entries"""
        return self._execute_objection_command(
            "android keystore list --verbose",
            "data_exploration",
            "keystore_dump",
            "Dump keystore entries and certificates"
        )
    
    def run_file_download(self, file_path=None):
        """Download specific file from device"""
        if not file_path:
            file_path = "/data/data/" + (self.package_name or "unknown") + "/shared_prefs"
        return self._execute_objection_command(
            f"file download {file_path}",
            "data_exploration",
            "file_download",
            f"Download file: {file_path}"
        )
    
    def run_grep_search(self, pattern="password"):
        """Search for patterns in files"""
        return self._execute_objection_command(
            f"file grep {pattern}",
            "data_exploration",
            f"grep_search_{pattern}",
            f"Search for pattern: {pattern}"
        )

    # =================== ENHANCED RUNTIME ANALYSIS ===================
    
    def run_class_search(self, pattern="crypto"):
        """Search for classes by pattern"""
        return self._execute_objection_command(
            f"android hooking search classes {pattern}",
            "runtime_analysis",
            f"class_search_{pattern}",
            f"Search classes containing: {pattern}"
        )
    
    def run_method_search(self, pattern="encrypt"):
        """Search for methods by pattern"""
        return self._execute_objection_command(
            f"android hooking search methods {pattern}",
            "runtime_analysis",
            f"method_search_{pattern}",
            f"Search methods containing: {pattern}"
        )
    
    def run_hook_class(self, class_name):
        """Hook specific class methods"""
        return self._execute_objection_command(
            f"android hooking watch class {class_name}",
            "runtime_analysis",
            f"hook_class_{class_name.replace('.', '_')}",
            f"Hook all methods in class: {class_name}"
        )
    
    def run_hook_method(self, class_name, method_name):
        """Hook specific method"""
        return self._execute_objection_command(
            f"android hooking watch method {class_name}.{method_name}",
            "runtime_analysis",
            f"hook_method_{class_name.replace('.', '_')}_{method_name}",
            f"Hook method: {class_name}.{method_name}"
        )
    
    def run_heap_search(self, pattern="String"):
        """Search heap for instances"""
        return self._execute_objection_command(
            f"android heap search instances {pattern}",
            "runtime_analysis",
            f"heap_search_{pattern}",
            f"Search heap for instances of: {pattern}"
        )
    
    def run_loaded_libraries(self):
        """List loaded libraries"""
        return self._execute_objection_command(
            "memory list modules",
            "runtime_analysis",
            "loaded_libraries",
            "List all loaded libraries and modules"
        )
    
    def run_thread_list(self):
        """List active threads"""
        return self._execute_objection_command(
            "jobs list",
            "runtime_analysis",
            "thread_list",
            "List active threads and jobs"
        )

    # =================== ENHANCED NETWORK MONITORING ===================
    
    def run_network_interfaces(self):
        """List network interfaces"""
        return self._execute_objection_command(
            "android network interfaces",
            "network_monitoring",
            "network_interfaces",
            "List network interfaces and configuration"
        )
    
    def run_http_capture_start(self):
        """Start HTTP traffic capture"""
        return self._execute_objection_command(
            "android http capture start",
            "network_monitoring",
            "http_capture_start",
            "Start capturing HTTP/HTTPS traffic"
        )
    
    def run_http_capture_stop(self):
        """Stop HTTP traffic capture"""
        return self._execute_objection_command(
            "android http capture stop",
            "network_monitoring",
            "http_capture_stop",
            "Stop capturing HTTP/HTTPS traffic"
        )
    
    def run_proxy_set(self, proxy_host="127.0.0.1", proxy_port="8080"):
        """Set proxy configuration"""
        return self._execute_objection_command(
            f"android proxy set {proxy_host} {proxy_port}",
            "network_monitoring",
            "proxy_set",
            f"Set proxy to {proxy_host}:{proxy_port}"
        )
    
    def run_proxy_clear(self):
        """Clear proxy configuration"""
        return self._execute_objection_command(
            "android proxy clear",
            "network_monitoring",
            "proxy_clear",
            "Clear proxy configuration"
        )
    
    def run_network_monitor(self):
        """Monitor network connections"""
        return self._execute_objection_command(
            "android network monitor",
            "network_monitoring",
            "network_monitor",
            "Monitor active network connections"
        )

    # =================== ENHANCED APPLICATION INFORMATION ===================
    
    def run_app_environment(self):
        """Get application environment"""
        return self._execute_objection_command(
            "env",
            "application_info",
            "app_environment",
            "Get application environment variables"
        )
    
    def run_device_info(self):
        """Get device information"""
        return self._execute_objection_command(
            "android device info",
            "application_info",
            "device_info",
            "Get detailed device information"
        )
    
    def run_app_signature(self):
        """Get application signature"""
        return self._execute_objection_command(
            "android signature info",
            "application_info",
            "app_signature",
            "Get application signature information"
        )
    
    def run_providers_list(self):
        """List content providers"""
        return self._execute_objection_command(
            "android providers list",
            "application_info",
            "providers_list",
            "List content providers"
        )
    
    def run_receivers_list(self):
        """List broadcast receivers"""
        return self._execute_objection_command(
            "android receivers list",
            "application_info",
            "receivers_list",
            "List broadcast receivers"
        )
    
    def run_intent_filters(self):
        """List intent filters"""
        return self._execute_objection_command(
            "android intent filters",
            "application_info",
            "intent_filters",
            "List intent filters"
        )

    # =================== ENHANCED DYNAMIC MANIPULATION ===================
    
    def run_method_override(self, class_name, method_name, return_value="true"):
        """Override method return value"""
        return self._execute_objection_command(
            f"android hooking set return_value {class_name}.{method_name} {return_value}",
            "dynamic_manipulation",
            f"method_override_{class_name.replace('.', '_')}_{method_name}",
            f"Override {class_name}.{method_name} to return {return_value}"
        )
    
    def run_spawn_app(self):
        """Spawn application with Frida"""
        if self.package_name:
            return self._execute_objection_command(
                f"android spawn {self.package_name}",
                "dynamic_manipulation",
                "spawn_app",
                f"Spawn application: {self.package_name}"
            )
        return False, "No package name specified", "", "Package name required"
    
    def run_kill_app(self):
        """Kill application"""
        if self.package_name:
            return self._execute_objection_command(
                f"android kill {self.package_name}",
                "dynamic_manipulation",
                "kill_app",
                f"Kill application: {self.package_name}"
            )
        return False, "No package name specified", "", "Package name required"
    
    def run_memory_dump(self, module_name=None):
        """Dump memory contents"""
        if module_name:
            command = f"memory dump {module_name}"
            description = f"Dump memory for module: {module_name}"
        else:
            command = "memory dump all"
            description = "Dump all accessible memory"
        
        return self._execute_objection_command(
            command,
            "dynamic_manipulation",
            "memory_dump",
            description
        )

    # =================== MENU HANDLERS ===================
    
    def handle_security_bypasses_menu(self):
        """Handle security bypasses menu interactions"""
        while True:
            self.display_security_bypasses_menu()
            choice = input("\n🔐 Select security bypass option: ").strip()
            
            if choice == 'b':
                break
            elif choice == '1':
                success, output_file, stdout, stderr = self.run_root_detection_check()
                print(f"✅ Root status check completed. Output: {output_file}")
            elif choice == '2':
                success, output_file, stdout, stderr = self.run_root_detection_bypass()
                print(f"✅ Root bypass completed. Output: {output_file}")
            elif choice == '3':
                success, output_file, stdout, stderr = self.run_root_detection_simulate()
                print(f"✅ Root simulation completed. Output: {output_file}")
            elif choice == '4':
                success, output_file, stdout, stderr = self.run_ssl_pinning_check()
                print(f"✅ SSL pinning check completed. Output: {output_file}")
            elif choice == '5':
                success, output_file, stdout, stderr = self.run_ssl_pinning_bypass()
                print(f"✅ SSL pinning bypass completed. Output: {output_file}")
            elif choice == '6':
                success, output_file, stdout, stderr = self.run_ssl_kill_switch()
                print(f"✅ SSL kill switch completed. Output: {output_file}")
            elif choice == '7':
                success, output_file, stdout, stderr = self.run_certificate_transparency_bypass()
                print(f"✅ Certificate transparency bypass completed. Output: {output_file}")
            elif choice == '8':
                success, output_file, stdout, stderr = self.run_debugger_detection_check()
                print(f"✅ Debugger detection check completed. Output: {output_file}")
            elif choice == '9':
                success, output_file, stdout, stderr = self.run_anti_debugging_bypass()
                print(f"✅ Anti-debugging bypass completed. Output: {output_file}")
            elif choice == '10':
                success, output_file, stdout, stderr = self.run_frida_detection_bypass()
                print(f"✅ Frida detection bypass completed. Output: {output_file}")
            elif choice == '11':
                success, output_file, stdout, stderr = self.run_hook_detection_bypass()
                print(f"✅ Hook detection bypass completed. Output: {output_file}")
            elif choice == '12':
                success, output_file, stdout, stderr = self.run_emulator_detection_check()
                print(f"✅ Emulator detection check completed. Output: {output_file}")
            elif choice == '13':
                success, output_file, stdout, stderr = self.run_biometric_bypass()
                print(f"✅ Biometric bypass completed. Output: {output_file}")
            elif choice == '14':
                results = self.run_all_security_bypasses()
                summary = self.get_test_summary(results)
                print(summary)
            else:
                print("❌ Invalid option")
            
            input("\n⏸️  Press Enter to continue...")

    def handle_data_exploration_menu(self):
        """Handle data exploration menu interactions"""
        while True:
            self.display_data_exploration_menu()
            choice = input("\n📂 Select data exploration option: ").strip()
            
            if choice == 'b':
                break
            elif choice == '1':
                success, output_file, stdout, stderr = self.run_filesystem_scan()
                print(f"✅ File system scan completed. Output: {output_file}")
            elif choice == '2':
                success, output_file, stdout, stderr = self.run_file_listing_detailed()
                print(f"✅ Detailed file listing completed. Output: {output_file}")
            elif choice == '3':
                success, output_file, stdout, stderr = self.run_find_sensitive_files()
                print(f"✅ Sensitive files search completed. Output: {output_file}")
            elif choice == '4':
                file_path = input("Enter file path to download (or press Enter for default): ").strip()
                success, output_file, stdout, stderr = self.run_file_download(file_path if file_path else None)
                print(f"✅ File download completed. Output: {output_file}")
            elif choice == '5':
                pattern = input("Enter search pattern (default: password): ").strip()
                success, output_file, stdout, stderr = self.run_grep_search(pattern if pattern else "password")
                print(f"✅ File content search completed. Output: {output_file}")
            elif choice == '6':
                success, output_file, stdout, stderr = self.run_database_analysis()
                print(f"✅ Database listing completed. Output: {output_file}")
            elif choice == '7':
                success, output_file, stdout, stderr = self.run_database_analysis()
                print(f"✅ Database analysis completed. Output: {output_file}")
            elif choice == '8':
                success, output_file, stdout, stderr = self.run_database_dump_all()
                print(f"✅ Database dump completed. Output: {output_file}")
            elif choice == '9':
                success, output_file, stdout, stderr = self.run_shared_preferences_scan()
                print(f"✅ Shared preferences scan completed. Output: {output_file}")
            elif choice == '10':
                success, output_file, stdout, stderr = self.run_shared_prefs_dump()
                print(f"✅ Shared preferences dump completed. Output: {output_file}")
            elif choice == '11':
                success, output_file, stdout, stderr = self.run_keystore_analysis()
                print(f"✅ Keystore analysis completed. Output: {output_file}")
            elif choice == '12':
                success, output_file, stdout, stderr = self.run_keystore_dump()
                print(f"✅ Keystore dump completed. Output: {output_file}")
            elif choice == '13':
                results = self.run_data_leakage_check()
                summary = self.get_test_summary(results)
                print(summary)
            elif choice == '14':
                success, output_file, stdout, stderr = self.run_grep_search("password")
                print(f"✅ Password search completed. Output: {output_file}")
            elif choice == '15':
                success, output_file, stdout, stderr = self.run_grep_search("token")
                print(f"✅ Token search completed. Output: {output_file}")
            else:
                print("❌ Invalid option")
            
            input("\n⏸️  Press Enter to continue...")

    def handle_runtime_analysis_menu(self):
        """Handle runtime analysis menu interactions"""
        while True:
            self.display_runtime_analysis_menu()
            choice = input("\n⚡ Select runtime analysis option: ").strip()
            
            if choice == 'b':
                break
            elif choice == '1':
                success, output_file, stdout, stderr = self.run_class_enumeration()
                print(f"✅ Class enumeration completed. Output: {output_file}")
            elif choice == '2':
                class_name = input("Enter class name (or press Enter for all): ").strip()
                success, output_file, stdout, stderr = self.run_method_enumeration(class_name if class_name else None)
                print(f"✅ Method enumeration completed. Output: {output_file}")
            elif choice == '3':
                pattern = input("Enter class search pattern (default: crypto): ").strip()
                success, output_file, stdout, stderr = self.run_class_search(pattern if pattern else "crypto")
                print(f"✅ Class search completed. Output: {output_file}")
            elif choice == '4':
                pattern = input("Enter method search pattern (default: encrypt): ").strip()
                success, output_file, stdout, stderr = self.run_method_search(pattern if pattern else "encrypt")
                print(f"✅ Method search completed. Output: {output_file}")
            elif choice == '5':
                class_name = input("Enter class name to hook: ").strip()
                if class_name:
                    success, output_file, stdout, stderr = self.run_hook_class(class_name)
                    print(f"✅ Class hooking completed. Output: {output_file}")
                else:
                    print("❌ Class name required")
            elif choice == '6':
                class_name = input("Enter class name: ").strip()
                method_name = input("Enter method name: ").strip()
                if class_name and method_name:
                    success, output_file, stdout, stderr = self.run_hook_method(class_name, method_name)
                    print(f"✅ Method hooking completed. Output: {output_file}")
                else:
                    print("❌ Both class and method names required")
            elif choice == '7':
                success, output_file, stdout, stderr = self.run_intent_monitoring()
                print(f"✅ Intent monitoring started. Output: {output_file}")
            elif choice == '8':
                success, output_file, stdout, stderr = self.run_thread_list()
                print(f"✅ Thread list completed. Output: {output_file}")
            elif choice == '9':
                success, output_file, stdout, stderr = self.run_memory_analysis()
                print(f"✅ Memory analysis completed. Output: {output_file}")
            elif choice == '10':
                success, output_file, stdout, stderr = self.run_loaded_libraries()
                print(f"✅ Library listing completed. Output: {output_file}")
            elif choice == '11':
                pattern = input("Enter heap search pattern (default: String): ").strip()
                success, output_file, stdout, stderr = self.run_heap_search(pattern if pattern else "String")
                print(f"✅ Heap search completed. Output: {output_file}")
            elif choice == '12':
                module_name = input("Enter module name (or press Enter for all): ").strip()
                success, output_file, stdout, stderr = self.run_memory_dump(module_name if module_name else None)
                print(f"✅ Memory dump completed. Output: {output_file}")
            elif choice == '13':
                success, output_file, stdout, stderr = self.run_class_search("crypto")
                print(f"✅ Crypto class search completed. Output: {output_file}")
            elif choice == '14':
                success, output_file, stdout, stderr = self.run_method_search("auth")
                print(f"✅ Auth method search completed. Output: {output_file}")
            elif choice == '15':
                success, output_file, stdout, stderr = self.run_class_search("network")
                print(f"✅ Network class search completed. Output: {output_file}")
            else:
                print("❌ Invalid option")
            
            input("\n⏸️  Press Enter to continue...")

    def handle_main_objection_menu(self):
        """Main objection menu handler with all sub-menus"""
        while True:
            self.display_main_menu()
            choice = input("\n🔍 Select objection testing option: ").strip()
            
            if choice == 'b':
                break
            elif choice == '1':
                self.handle_security_bypasses_menu()
            elif choice == '2':
                self.handle_data_exploration_menu()
            elif choice == '3':
                self.handle_runtime_analysis_menu()
            elif choice == '4':
                # Network monitoring menu handler
                print("🌐 Network Monitoring - Coming soon with detailed sub-options!")
                input("\n⏸️  Press Enter to continue...")
            elif choice == '5':
                # Application info menu handler  
                print("📱 Application Information - Coming soon with detailed sub-options!")
                input("\n⏸️  Press Enter to continue...")
            elif choice == '6':
                # Dynamic manipulation menu handler
                print("⚡ Dynamic Manipulation - Coming soon with detailed sub-options!")
                input("\n⏸️  Press Enter to continue...")
            elif choice == '7':
                # Advanced testing menu handler
                print("🔬 Advanced Testing - Coming soon with detailed sub-options!")
                input("\n⏸️  Press Enter to continue...")
            elif choice == '8':
                # Quick tests menu handler
                print("⚡ Quick Tests - Running basic security assessment...")
                results = self.run_basic_security_assessment()
                summary = self.get_test_summary(results)
                print(summary)
                input("\n⏸️  Press Enter to continue...")
            elif choice == '9':
                running, message = self.verify_target_running()
                print(f"🎯 Target verification: {'✅' if running else '❌'} {message}")
                input("\n⏸️  Press Enter to continue...")
            elif choice == '10':
                self.run_system_diagnostics()
                input("\n⏸️  Press Enter to continue...")
            else:
                print("❌ Invalid option")

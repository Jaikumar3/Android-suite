#!/usr/bin/env python3
"""
Android Pentesting Tools Installer
Separate installation script with various options for setting up the environment
"""

import os
import sys
import subprocess
import platform
import shutil
import json
import time
import requests
from pathlib import Path
import zipfile
import tarfile

class AndroidPentestInstaller:
    def install_apktool(self):
        """Install apktool (downloads jar/bat for Windows, jar/sh for Unix)."""
        self.log_status("Installing apktool...")
        apktool_dir = self.tools_dir / "apktool"
        apktool_dir.mkdir(exist_ok=True)
        if self.system == "windows":
            apktool_url = "https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool_2.9.3.jar"
            wrapper_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat"
            jar_path = apktool_dir / "apktool.jar"
            bat_path = apktool_dir / "apktool.bat"
            # Download jar
            try:
                self.log_status(f"Downloading apktool jar from {apktool_url}...")
                r = requests.get(apktool_url)
                r.raise_for_status()
                with open(jar_path, 'wb') as f:
                    f.write(r.content)
                self.log_status("✓ apktool.jar downloaded", "SUCCESS")
                # Download bat
                self.log_status(f"Downloading apktool.bat from {wrapper_url}...")
                r = requests.get(wrapper_url)
                r.raise_for_status()
                with open(bat_path, 'wb') as f:
                    f.write(r.content)
                self.log_status("✓ apktool.bat downloaded", "SUCCESS")
            except Exception as e:
                self.log_status(f"Failed to download apktool: {e}", "ERROR")
                return False
        else:
            apktool_url = "https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool_2.9.3.jar"
            wrapper_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool"
            jar_path = apktool_dir / "apktool.jar"
            sh_path = apktool_dir / "apktool"
            try:
                self.log_status(f"Downloading apktool jar from {apktool_url}...")
                r = requests.get(apktool_url)
                r.raise_for_status()
                with open(jar_path, 'wb') as f:
                    f.write(r.content)
                self.log_status("✓ apktool.jar downloaded", "SUCCESS")
                # Download shell script
                self.log_status(f"Downloading apktool script from {wrapper_url}...")
                r = requests.get(wrapper_url)
                r.raise_for_status()
                with open(sh_path, 'wb') as f:
                    f.write(r.content)
                os.chmod(sh_path, 0o755)
                self.log_status("✓ apktool script downloaded", "SUCCESS")
            except Exception as e:
                self.log_status(f"Failed to download apktool: {e}", "ERROR")
                return False
        self.log_status(f"Add {apktool_dir} to your PATH or use full path to run apktool.", "INFO")
        return True

    def install_apkleaks(self):
        """Install apkleaks via pip."""
        self.log_status("Installing apkleaks (pip)...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "apkleaks", "--upgrade"
            ], check=True, capture_output=True, text=True)
            self.log_status("✓ apkleaks installed", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log_status(f"✗ Failed to install apkleaks: {e.stderr}", "ERROR")
            return False
    """Installer class for Android pentesting tools and dependencies"""
    
    def __init__(self, tools_dir="./tools"):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(exist_ok=True)
        
        # Installation status tracking
        self.installation_log = []
        
        # Platform-specific executable extensions
        self.exe_ext = ".exe" if self.system == "windows" else ""
        
    def log_status(self, message, status="INFO"):
        """Log installation status"""
        log_entry = f"[{status}] {message}"
        self.installation_log.append(log_entry)
        print(log_entry)
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        self.log_status("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            self.log_status("Python 3.6+ required. Current version: {}.{}.{}".format(
                version.major, version.minor, version.micro), "ERROR")
            return False
        
        self.log_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        return True
    
    def install_python_packages(self, packages=None):
        """Install Python packages"""
        if packages is None:
            packages = [
                "requests>=2.25.1",
                "colorama>=0.4.4", 
                "lxml>=4.6.3",
                "beautifulsoup4>=4.9.3",
                "frida-tools>=12.0.0",
                "objection>=1.9.0",
                "androguard>=3.4.0",
                "python-adb>=3.2.0"
            ]
        
        self.log_status("Installing Python packages...")
        
        failed_packages = []
        for package in packages:
            try:
                self.log_status(f"Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package, "--upgrade"
                ], check=True, capture_output=True, text=True)
                self.log_status(f"✓ {package} installed successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log_status(f"✗ Failed to install {package}: {e.stderr}", "ERROR")
                failed_packages.append(package)
        
        if failed_packages:
            self.log_status(f"Failed to install: {', '.join(failed_packages)}", "WARNING")
            return False
        
        return True
    
    def install_android_sdk_tools(self):
        """Install Android SDK Platform Tools"""
        self.log_status("Installing Android SDK Platform Tools...")
        
        # Check if ADB is already available
        if shutil.which("adb"):
            self.log_status("ADB already available in PATH", "SUCCESS")
            return True
        
        # Download URLs for different platforms
        download_urls = {
            "windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
            "darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip", 
            "linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
        }
        
        if self.system not in download_urls:
            self.log_status(f"Unsupported platform: {self.system}", "ERROR")
            return False
        
        try:
            # Download platform tools
            url = download_urls[self.system]
            filename = f"platform-tools-{self.system}.zip"
            filepath = self.tools_dir / filename
            
            self.log_status(f"Downloading from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract platform tools
            self.log_status("Extracting platform tools...")
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(self.tools_dir)
            
            # Set executable permissions on Unix systems
            if self.system in ['linux', 'darwin']:
                platform_tools_dir = self.tools_dir / "platform-tools"
                for tool in ['adb', 'fastboot']:
                    tool_path = platform_tools_dir / tool
                    if tool_path.exists():
                        os.chmod(tool_path, 0o755)
            
            self.log_status("✓ Android SDK Platform Tools installed", "SUCCESS")
            self.log_status(f"Add to PATH: {self.tools_dir / 'platform-tools'}", "INFO")
            
            # Clean up
            filepath.unlink()
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install Android SDK Tools: {e}", "ERROR")
            return False
    
    def install_jadx(self):
        """Install JADX decompiler"""
        self.log_status("Installing JADX...")
        
        if shutil.which("jadx"):
            self.log_status("JADX already available in PATH", "SUCCESS")
            return True
        
        try:
            # Get latest release info from GitHub
            api_url = "https://api.github.com/repos/skylot/jadx/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            
            release_data = response.json()
            
            # Find appropriate download asset
            asset_patterns = {
                "windows": "jadx-{version}.zip",
                "linux": "jadx-{version}.zip",
                "darwin": "jadx-{version}.zip"
            }
            
            version = release_data['tag_name'].lstrip('v')
            pattern = asset_patterns.get(self.system)
            
            if not pattern:
                self.log_status(f"JADX not available for {self.system}", "WARNING")
                return False
            
            expected_name = pattern.format(version=version)
            download_url = None
            
            for asset in release_data['assets']:
                if asset['name'] == expected_name:
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                self.log_status("Could not find JADX download URL", "ERROR")
                return False
            
            # Download JADX
            filename = f"jadx-{version}.zip"
            filepath = self.tools_dir / filename
            
            self.log_status(f"Downloading JADX {version}...")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract JADX
            jadx_dir = self.tools_dir / f"jadx-{version}"
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(jadx_dir)
            
            # Set executable permissions
            if self.system in ['linux', 'darwin']:
                for script in ['jadx', 'jadx-gui']:
                    script_path = jadx_dir / "bin" / script
                    if script_path.exists():
                        os.chmod(script_path, 0o755)
            
            self.log_status("✓ JADX installed successfully", "SUCCESS")
            self.log_status(f"Add to PATH: {jadx_dir / 'bin'}", "INFO")
            
            # Clean up
            filepath.unlink()
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install JADX: {e}", "ERROR")
            return False
    
    def install_frida_server_files(self):
        """Download Frida server binaries for different architectures"""
        self.log_status("Downloading Frida server binaries...")
        
        try:
            # Get latest Frida release
            api_url = "https://api.github.com/repos/frida/frida/releases/latest"
            response = requests.get(api_url)
            response.raise_for_status()
            
            release_data = response.json()
            version = release_data['tag_name']
            
            # Common Android architectures
            architectures = [
                "android-arm",
                "android-arm64", 
                "android-x86",
                "android-x86_64"
            ]
            
            frida_dir = self.tools_dir / "frida-server"
            frida_dir.mkdir(exist_ok=True)
            
            for arch in architectures:
                asset_name = f"frida-server-{version}-{arch}.xz"
                download_url = None
                
                # Find download URL
                for asset in release_data['assets']:
                    if asset['name'] == asset_name:
                        download_url = asset['browser_download_url']
                        break
                
                if not download_url:
                    self.log_status(f"Frida server not found for {arch}", "WARNING")
                    continue
                
                # Download
                self.log_status(f"Downloading Frida server for {arch}...")
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                compressed_file = frida_dir / asset_name
                with open(compressed_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract
                import lzma
                extracted_file = frida_dir / f"frida-server-{arch}"
                with lzma.open(compressed_file, 'rb') as f_in:
                    with open(extracted_file, 'wb') as f_out:
                        f_out.write(f_in.read())
                
                # Set executable permissions
                if self.system in ['linux', 'darwin']:
                    os.chmod(extracted_file, 0o755)
                
                # Clean up compressed file
                compressed_file.unlink()
                
                self.log_status(f"✓ Frida server downloaded for {arch}", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_status(f"Failed to download Frida servers: {e}", "ERROR")
            return False
    
    def install_additional_tools(self):
        """Install additional pentesting tools"""
        self.log_status("Installing additional tools...")
        try:
            # Install fridump (git clone)
            self._install_git_tool({
                "name": "fridump",
                "type": "git",
                "url": "https://github.com/Nightbringer21/fridump",
                "description": "Memory dumping tool for Frida"
            })
        except Exception as e:
            self.log_status(f"Exception during fridump install: {e}", "ERROR")
        try:
            # Install APKiD (pip)
            self._install_pip_tool({
                "name": "APKiD",
                "type": "pip",
                "package": "apkid",
                "description": "Android Application Identifier"
            })
        except Exception as e:
            self.log_status(f"Exception during APKiD install: {e}", "ERROR")
        try:
            # Install Quark-Engine (pip)
            self._install_pip_tool({
                "name": "Quark-Engine",
                "type": "pip",
                "package": "quark-engine",
                "description": "Android malware analysis tool"
            })
        except Exception as e:
            self.log_status(f"Exception during Quark-Engine install: {e}", "ERROR")
        try:
            # Install apktool
            self.install_apktool()
        except Exception as e:
            self.log_status(f"Exception during apktool install: {e}", "ERROR")
        try:
            # Install apkleaks
            self.install_apkleaks()
        except Exception as e:
            self.log_status(f"Exception during apkleaks install: {e}", "ERROR")
        return True
    
    def _install_git_tool(self, tool):
        """Install tool from Git repository"""
        tool_dir = self.tools_dir / tool["name"]
        
        if tool_dir.exists():
            self.log_status(f"{tool['name']} already exists", "INFO")
            return
        
        # Check if Git is available
        if not shutil.which("git"):
            self.log_status("Git not found. Please install Git to download additional tools", "ERROR")
            return
        
        self.log_status(f"Cloning {tool['name']}...")
        try:
            result = subprocess.run([
                "git", "clone", tool["url"], str(tool_dir)
            ], check=True, capture_output=True, text=True)
            self.log_status(f"✓ {tool['name']} installed", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log_status(f"✗ Failed to clone {tool['name']}: {e.stderr}", "ERROR")
    
    def _install_pip_tool(self, tool):
        """Install tool via pip"""
        self.log_status(f"Installing {tool['name']}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", tool["package"]
            ], check=True, capture_output=True, text=True)
            self.log_status(f"✓ {tool['name']} installed", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log_status(f"✗ Failed to install {tool['name']}: {e.stderr}", "ERROR")
    
    def create_environment_script(self):
        """Create environment setup script"""
        self.log_status("Creating environment setup script...")
        
        if self.system == "windows":
            # Find actual JADX directory for Windows
            jadx_dirs = list(self.tools_dir.glob("jadx-*"))
            jadx_path = ""
            if jadx_dirs:
                jadx_path = f"set PATH={jadx_dirs[0]}\\bin;%PATH%"
            
            script_content = f"""@echo off
REM Android Pentesting Environment Setup
echo Setting up Android Pentesting Environment...

REM Add tools to PATH
set TOOLS_DIR={self.tools_dir.absolute()}
set PATH=%TOOLS_DIR%\\platform-tools;%PATH%
{jadx_path}

echo Environment setup complete!
echo.
echo Available tools:
echo - ADB: adb
echo - Fastboot: fastboot  
echo - JADX: jadx
echo - Frida: frida
echo - Objection: objection
echo.
echo To make permanent, add the following directories to your system PATH:
echo %TOOLS_DIR%\\platform-tools
if exist "%TOOLS_DIR%\\jadx-*" echo %TOOLS_DIR%\\jadx-*\\bin
"""
            script_file = "setup_env.bat"
        else:
            script_content = f"""#!/bin/bash
# Android Pentesting Environment Setup
echo "Setting up Android Pentesting Environment..."

# Add tools to PATH
export TOOLS_DIR="{self.tools_dir.absolute()}"
export PATH="$TOOLS_DIR/platform-tools:$PATH"

# Add JADX to PATH if it exists
for jadx_dir in "$TOOLS_DIR"/jadx-*/; do
    if [ -d "$jadx_dir/bin" ]; then
        export PATH="$jadx_dir/bin:$PATH"
        break
    fi
done

echo "Environment setup complete!"
echo ""
echo "Available tools:"
echo "- ADB: adb"
echo "- Fastboot: fastboot"
echo "- JADX: jadx" 
echo "- Frida: frida"
echo "- Objection: objection"
echo ""
echo "To make permanent, add the following to your ~/.bashrc or ~/.zshrc:"
echo "export PATH=\\"$TOOLS_DIR/platform-tools:\$PATH\\""
echo "export PATH=\\"$TOOLS_DIR/jadx-*/bin:\$PATH\\""
"""
            script_file = "setup_env.sh"
        
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        if self.system in ['linux', 'darwin']:
            os.chmod(script_file, 0o755)
        
        self.log_status(f"✓ Environment script created: {script_file}", "SUCCESS")
    
    def verify_installation(self):
        """Verify that tools are properly installed"""
        self.log_status("Verifying installation...")
        
        # Platform-specific tool commands
        tools_to_check = [
            ("python", "Python", ["--version"]),
            ("pip", "Pip", ["--version"]),
            ("adb", "Android Debug Bridge", ["version"]),
            ("frida", "Frida", ["--version"]),
            ("objection", "Objection", ["--version"])
        ]
        
        verification_results = {}
        
        for tool_cmd, tool_name, version_args in tools_to_check:
            try:
                # Check if tool exists in PATH first
                if not shutil.which(tool_cmd):
                    verification_results[tool_name] = "✗ Not found in PATH"
                    self.log_status(f"✗ {tool_name} not found in PATH", "ERROR")
                    continue
                
                # Try to run the tool with version flag
                cmd = [tool_cmd] + version_args
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # Extract version info if available
                    version_info = result.stdout.strip().split('\n')[0] if result.stdout.strip() else "Available"
                    verification_results[tool_name] = f"✓ {version_info}"
                    self.log_status(f"✓ {tool_name} is available: {version_info}", "SUCCESS")
                else:
                    verification_results[tool_name] = "✗ Not working properly"
                    self.log_status(f"✗ {tool_name} not working properly", "ERROR")
                    
            except subprocess.TimeoutExpired:
                verification_results[tool_name] = "✗ Command timeout"
                self.log_status(f"✗ {tool_name} command timed out", "ERROR")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                verification_results[tool_name] = "✗ Command failed"
                self.log_status(f"✗ {tool_name} command failed: {e}", "ERROR")
        
        return verification_results
    
    def save_installation_report(self):
        """Save installation report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": self.system,
            "architecture": self.architecture,
            "installation_log": self.installation_log,
            "tools_directory": str(self.tools_dir.absolute())
        }
        
        report_file = "installation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_status(f"Installation report saved: {report_file}", "SUCCESS")
    
    def check_system_requirements(self):
        """Check system requirements and dependencies"""
        self.log_status("Checking system requirements...")
        
        # Check for essential system tools
        required_tools = []
        
        if self.system == "windows":
            # Windows-specific checks
            required_tools = [
                ("powershell", "PowerShell", "Required for some operations"),
                ("where", "Where command", "Required for finding executables")
            ]
        else:
            # Unix-specific checks
            required_tools = [
                ("which", "Which command", "Required for finding executables"),
                ("curl", "Curl", "Required for downloads (alternative to requests)"),
                ("unzip", "Unzip", "Required for extracting archives")
            ]
        
        missing_tools = []
        for tool_cmd, tool_name, description in required_tools:
            if not shutil.which(tool_cmd):
                missing_tools.append((tool_name, description))
                self.log_status(f"✗ {tool_name} not found", "WARNING")
            else:
                self.log_status(f"✓ {tool_name} available", "SUCCESS")
        
        if missing_tools:
            self.log_status("Some system tools are missing but installation can continue", "WARNING")
            for tool_name, description in missing_tools:
                self.log_status(f"  Missing: {tool_name} - {description}", "INFO")
        
        return len(missing_tools) == 0
    
    def get_platform_specific_path(self, tool_name):
        """Get platform-specific executable path"""
        if self.system == "windows":
            # Check common Windows installation paths
            common_paths = [
                Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
                Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
                Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))),
                Path(os.path.expanduser('~\\AppData\\Roaming'))
            ]
            
            for base_path in common_paths:
                tool_path = base_path / tool_name / f"{tool_name}.exe"
                if tool_path.exists():
                    return str(tool_path)
        
        return shutil.which(tool_name)

def main():
    """Main installation function with options"""
    import argparse
    import time
    
    parser = argparse.ArgumentParser(
        description="Android Pentesting Tools Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Installation Options:
  --minimal         Install only essential Python packages
  --standard        Install Python packages + Android SDK tools (default)
  --full           Install everything including additional tools
  --frida-only     Install only Frida-related tools
  --verify-only    Only verify existing installations

Examples:
  python installer.py --standard
  python installer.py --full
  python installer.py --frida-only
  python installer.py --verify-only
        """
    )
    
    parser.add_argument('--minimal', action='store_true',
                      help='Install only essential Python packages')
    parser.add_argument('--standard', action='store_true', default=True,
                      help='Install Python packages + Android SDK tools (default)')
    parser.add_argument('--full', action='store_true',
                      help='Install everything including additional tools')
    parser.add_argument('--frida-only', action='store_true',
                      help='Install only Frida-related tools')
    parser.add_argument('--verify-only', action='store_true',
                      help='Only verify existing installations')
    parser.add_argument('--tools-dir', default='./tools',
                      help='Directory to install tools (default: ./tools)')
    
    args = parser.parse_args()
    
    # Initialize installer with custom tools directory if provided
    installer = AndroidPentestInstaller(tools_dir=args.tools_dir)
    
    print(f"{'='*60}")
    print("ANDROID PENTESTING TOOLS INSTALLER")
    print(f"{'='*60}")
    print(f"System: {installer.system}")
    print(f"Architecture: {installer.architecture}")
    print(f"Tools Directory: {installer.tools_dir}")
    print(f"{'='*60}")
    
    # Check Python version first
    if not installer.check_python_version():
        sys.exit(1)
    
    success = True
    
    if args.verify_only:
        # Only verify installations
        results = installer.verify_installation()
        print(f"\n{'='*60}")
        print("VERIFICATION COMPLETE")
        print(f"{'='*60}")
        for tool, status in results.items():
            print(f"{tool}: {status}")
    
    elif args.minimal:
        # Minimal installation
        essential_packages = [
            "requests>=2.25.1",
            "colorama>=0.4.4"
        ]
        success = installer.install_python_packages(essential_packages)
    
    elif args.frida_only:
        # Frida-only installation
        frida_packages = [
            "frida-tools>=12.0.0",
            "objection>=1.9.0"
        ]
        success = installer.install_python_packages(frida_packages)
        if success:
            success = installer.install_frida_server_files()
    
    elif args.full:
        # Full installation
        py_success = installer.install_python_packages()
        sdk_success = installer.install_android_sdk_tools() if py_success else False
        jadx_success = installer.install_jadx() if sdk_success else False
        frida_success = installer.install_frida_server_files() if jadx_success else False
        # Always attempt additional tools, even if previous steps failed
        add_success = installer.install_additional_tools()
        success = py_success and sdk_success and jadx_success and frida_success and add_success
    else:
        # Standard installation (default) - now includes additional tools (apktool, fridump, etc.)
        py_success = installer.install_python_packages()
        sdk_success = installer.install_android_sdk_tools() if py_success else False
        jadx_success = installer.install_jadx() if sdk_success else False
        # Always attempt additional tools, even if previous steps failed
        add_success = installer.install_additional_tools()
        success = py_success and sdk_success and jadx_success and add_success
    
    # Create environment setup script
    if success and not args.verify_only:
        installer.create_environment_script()
    
    # Verify installation
    if not args.verify_only:
        verification_results = installer.verify_installation()
    
    # Save report
    installer.save_installation_report()
    
    print(f"\n{'='*60}")
    if success:
        print("INSTALLATION COMPLETED SUCCESSFULLY")
        if not args.verify_only:
            print(f"Run setup_env.{'bat' if installer.system == 'windows' else 'sh'} to configure your environment")
    else:
        print("INSTALLATION COMPLETED WITH ERRORS")
        print("Check the installation report for details")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

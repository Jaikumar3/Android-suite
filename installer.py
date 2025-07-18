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
    def install_jadx_cli(self):
        """Download latest JADX CLI release and add to tools directory."""
        self.log_status("Installing JADX CLI ...")
        import zipfile
        import urllib.request
        api_url = "https://api.github.com/repos/skylot/jadx/releases/latest"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            release_data = response.json()
            version = release_data['tag_name'].lstrip('v')
            # Find the CLI asset (zip)
            cli_asset = None
            for asset in release_data['assets']:
                if asset['name'].endswith('.zip') and 'cli' in asset['name']:
                    cli_asset = asset
                    break
            if not cli_asset:
                # fallback: use the main zip
                for asset in release_data['assets']:
                    if asset['name'].endswith('.zip'):
                        cli_asset = asset
                        break
            if not cli_asset:
                self.log_status("Could not find JADX CLI zip in latest release.", "ERROR")
                return False
            download_url = cli_asset['browser_download_url']
            zip_path = self.tools_dir / cli_asset['name']
            extract_dir = self.tools_dir / f"jadx-cli-{version}"
            if extract_dir.exists():
                self.log_status(f"JADX CLI {version} already present.", "INFO")
                return True
            self.log_status(f"Downloading JADX CLI from {download_url} ...")
            urllib.request.urlretrieve(download_url, zip_path)
            self.log_status("✓ JADX CLI zip downloaded", "SUCCESS")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            self.log_status("✓ JADX CLI extracted", "SUCCESS")
            zip_path.unlink()
            self.log_status(f"Add {extract_dir / 'bin'} to your PATH or use full path to run jadx-cli.", "INFO")
            return True
        except Exception as e:
            self.log_status(f"Failed to download/extract JADX CLI: {e}", "ERROR")
            return False
    def install_frida_script_gen(self):
        """
        Clone and set up frida-script-gen in tools directory.
        """
        repo_url = "https://github.com/thecybersandeep/frida-script-gen"
        tool_dir = self.tools_dir / "frida-script-gen"
        if tool_dir.exists():
            self.log_status("frida-script-gen already present.", "INFO")
            return True
        try:
            self.log_status("Cloning frida-script-gen ...")
            subprocess.run(["git", "clone", repo_url, str(tool_dir)], check=True)
            self.log_status("✓ frida-script-gen cloned successfully.", "SUCCESS")
            return True
        except Exception as e:
            self.log_status(f"Failed to clone frida-script-gen: {e}", "ERROR")
            return False
    def install_apk_components_inspector(self):
        """Clone apk-components-inspector and set up its venv and dependencies"""
        self.log_status("Installing apk-components-inspector ...")
        import subprocess
        import sys
        tool_dir = self.tools_dir / "apk-components-inspector"
        if tool_dir.exists():
            self.log_status("apk-components-inspector already present.", "INFO")
            return True
        try:
            # Clone repo
            self.log_status("Cloning apk-components-inspector ...")
            subprocess.run(["git", "clone", "https://github.com/thecybersandeep/apk-components-inspector", str(tool_dir)], check=True)
            # Create venv
            venv_dir = tool_dir / "venv"
            self.log_status("Creating venv for apk-components-inspector ...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            # Install dependencies
            pip_path = venv_dir / "bin" / "pip" if os.name != "nt" else venv_dir / "Scripts" / "pip.exe"
            self.log_status("Installing dependencies: androguard==3.3.5 rich ...")
            subprocess.run([str(pip_path), "install", "androguard==3.3.5", "rich"], check=True)
            self.log_status("✓ apk-components-inspector installed and ready", "SUCCESS")
            return True
        except Exception as e:
            self.log_status(f"Failed to install apk-components-inspector: {e}", "ERROR")
            return False
    def install_jadx_1_5_2(self):
        """Download JADX 1.5.2 zip and extract to tools directory"""
        self.log_status("Installing JADX 1.5.2 ...")
        import zipfile
        jadx_url = "https://github.com/skylot/jadx/releases/download/v1.5.2/jadx-1.5.2.zip"
        zip_path = self.tools_dir / "jadx-1.5.2.zip"
        extract_dir = self.tools_dir / "jadx-1.5.2"
        if extract_dir.exists():
            self.log_status("JADX 1.5.2 already present.", "INFO")
            return True
        try:
            self.log_status(f"Downloading JADX 1.5.2 from {jadx_url} ...")
            import urllib.request
            urllib.request.urlretrieve(jadx_url, zip_path)
            self.log_status("✓ JADX 1.5.2 zip downloaded", "SUCCESS")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            self.log_status("✓ JADX 1.5.2 extracted", "SUCCESS")
            zip_path.unlink()
            return True
        except Exception as e:
            self.log_status(f"Failed to download/extract JADX 1.5.2: {e}", "ERROR")
            return False
    def install_mobapp_storage_inspector(self):
        """Download MobApp-Storage-Inspector.jar to tools directory"""
        self.log_status("Installing MobApp-Storage-Inspector...")
        jar_path = self.tools_dir / "MobApp-Storage-Inspector.jar"
        url = "https://github.com/thecybersandeep/mobapp-storage-inspector/releases/download/v1.0.0/MobApp-Storage-Inspector.jar"
        if not jar_path.exists():
            try:
                import urllib.request
                self.log_status(f"Downloading MobApp-Storage-Inspector from {url} ...")
                urllib.request.urlretrieve(url, jar_path)
                self.log_status("✓ MobApp-Storage-Inspector.jar downloaded", "SUCCESS")
            except Exception as e:
                self.log_status(f"Failed to download MobApp-Storage-Inspector: {e}", "ERROR")
        else:
            self.log_status("MobApp-Storage-Inspector already present.", "INFO")
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
                for tool in ['adb']:
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
            
            # Common Android architectures (x86/x86_64 only for recommended install)
            architectures = [
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
            # Install apk-components-inspector (git clone + venv + pip)
            self.install_apk_components_inspector()
        except Exception as e:
            self.log_status(f"Exception during apk-components-inspector install: {e}", "ERROR")
        try:
            # Install JADX 1.5.2 (zip download)
            self.install_jadx_1_5_2()
        except Exception as e:
            self.log_status(f"Exception during JADX 1.5.2 install: {e}", "ERROR")
        try:
            # Install MobApp-Storage-Inspector (jar download)
            self.install_mobapp_storage_inspector()
        except Exception as e:
            self.log_status(f"Exception during MobApp-Storage-Inspector install: {e}", "ERROR")
        try:
            # Install frida-script-gen (git clone)
            self.install_frida_script_gen()
        except Exception as e:
            self.log_status(f"Exception during frida-script-gen install: {e}", "ERROR")
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
echo "- JADX: jadx" 
echo "- Frida: frida"
echo "- Objection: objection"
echo ""
echo "To make permanent, add the following to your ~/.bashrc or ~/.zshrc:"
echo "export PATH=\\"$TOOLS_DIR/platform-tools:\\$PATH\\""
echo "export PATH=\\"$TOOLS_DIR/jadx-*/bin:\\$PATH\\""
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
        
        # Core tools that should always be available
        core_tools = [
            ("python", "Python", ["--version"]),
            ("pip", "Pip", ["--version"])
        ]
        
        # Android/pentesting tools (may not be installed depending on options)
        optional_tools = [
            ("adb", "Android Debug Bridge", ["--version"]),  # ADB supports both --version and version
            ("frida", "Frida", ["--version"]),
            ("objection", "Objection", ["version"]),  # Objection uses 'version' without dashes
            ("java", "Java", ["-version"]),  # Java uses single dash -version
            ("git", "Git", ["--version"]),  # Git version check
            ("jadx", "JADX", ["--version"]),  # JADX decompiler
            ("apktool", "APKTool", ["--version"]),  # APKTool
            ("sdkmanager", "Android SDK Manager", ["--version"])  # SDK Manager
        ]
        
        # Platform-specific tool commands
        tools_to_check = core_tools + optional_tools
        
        verification_results = {}
        
        for tool_cmd, tool_name, version_args in tools_to_check:
            try:
                # Check if tool exists in PATH first
                if not shutil.which(tool_cmd):
                    if (tool_cmd, tool_name, version_args) in core_tools:
                        verification_results[tool_name] = "✗ Not found in PATH"
                        self.log_status(f"✗ {tool_name} not found in PATH", "ERROR")
                    else:
                        verification_results[tool_name] = "- Not installed (optional)"
                        self.log_status(f"- {tool_name} not installed (optional)", "INFO")
                    continue
                
                # Try to run the tool with version flag
                cmd = [tool_cmd] + version_args
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # Extract version info if available (check both stdout and stderr for Java)
                    output = result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
                    version_info = output.split('\n')[0] if output else "Available"
                    verification_results[tool_name] = f"✓ {version_info}"
                    self.log_status(f"✓ {tool_name} is available: {version_info}", "SUCCESS")
                else:
                    # Special case for Java which outputs to stderr but returns 0
                    if tool_cmd == "java" and result.stderr.strip():
                        version_info = result.stderr.strip().split('\n')[0]
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

    def install_android_studio_cli(self):
        """Install Android Studio Command Line Tools and SDK Manager"""
        self.log_status("Installing Android Studio Command Line Tools...")
        
        # Check if SDK Manager is already available
        if shutil.which("sdkmanager") or shutil.which("sdkmanager.bat"):
            self.log_status("Android SDK Manager already available", "SUCCESS")
            return True
        
        # Download URLs for command line tools
        download_urls = {
            "windows": "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip",
            "darwin": "https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip",
            "linux": "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
        }
        
        if self.system not in download_urls:
            self.log_status(f"Unsupported platform: {self.system}", "ERROR")
            return False
        
        try:
            # Create Android SDK directory
            android_sdk_dir = self.tools_dir / "android-sdk"
            android_sdk_dir.mkdir(exist_ok=True)
            
            # Download command line tools
            url = download_urls[self.system]
            filename = f"commandlinetools-{self.system}.zip"
            filepath = self.tools_dir / filename
            
            self.log_status(f"Downloading Android SDK Command Line Tools...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading Android Studio: {percent:.1f}%", end='', flush=True)
            print()  # New line after download
            
            # Extract command line tools
            self.log_status("Extracting command line tools...")
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(android_sdk_dir)
            
            # Move cmdline-tools to proper location
            cmdline_tools_src = android_sdk_dir / "cmdline-tools"
            cmdline_tools_dst = android_sdk_dir / "cmdline-tools" / "latest"
            
            if cmdline_tools_src.exists() and not cmdline_tools_dst.exists():
                try:
                    # Create the nested structure
                    cmdline_tools_dst.parent.mkdir(exist_ok=True)
                    
                    # Windows-safe approach: copy then delete instead of rename
                    if self.system == "windows":
                        import shutil as sh
                        # Create latest directory
                        cmdline_tools_dst.mkdir(exist_ok=True)
                        # Copy all contents from cmdline-tools to cmdline-tools/latest
                        for item in cmdline_tools_src.iterdir():
                            if item.name != "latest":  # Don't copy the latest dir we just created
                                dest_item = cmdline_tools_dst / item.name
                                if item.is_dir():
                                    sh.copytree(item, dest_item, dirs_exist_ok=True)
                                else:
                                    sh.copy2(item, dest_item)
                        # Remove original files (keep the cmdline-tools directory structure)
                        for item in cmdline_tools_src.iterdir():
                            if item.name != "latest":
                                if item.is_dir():
                                    sh.rmtree(item)
                                else:
                                    item.unlink()
                    else:
                        # Unix approach: use rename
                        temp_dir = android_sdk_dir / "temp_cmdline"
                        cmdline_tools_src.rename(temp_dir)
                        cmdline_tools_dst.parent.mkdir(exist_ok=True)
                        temp_dir.rename(cmdline_tools_dst)
                        
                except Exception as e:
                    self.log_status(f"Warning: Failed to reorganize cmdline-tools structure: {e}", "WARNING")
                    self.log_status("Continuing with existing structure...", "INFO")
                    # Fallback: use the original structure
                    cmdline_tools_dst = cmdline_tools_src
            
            # Set executable permissions on Unix systems
            if self.system in ['linux', 'darwin']:
                for tool in ['sdkmanager', 'avdmanager']:
                    tool_path = cmdline_tools_dst / "bin" / tool
                    if tool_path.exists():
                        os.chmod(tool_path, 0o755)
            
            self.log_status("✓ Android SDK Command Line Tools installed", "SUCCESS")
            self.log_status(f"SDK Location: {android_sdk_dir}", "INFO")
            self.log_status(f"Add to PATH: {cmdline_tools_dst / 'bin'}", "INFO")
            
            # Set environment variables
            self._set_android_env_vars(android_sdk_dir)
            
            # Clean up
            filepath.unlink()
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install Android SDK Command Line Tools: {e}", "ERROR")
            return False

    def install_android_emulator(self):
        """Install Android Emulator and create a basic AVD (emulator only, no other tools)"""
        self.log_status("Installing Android Emulator...")
        
        android_sdk_dir = self.tools_dir / "android-sdk"
        if not android_sdk_dir.exists():
            self.log_status("Android SDK not found. Please install Android SDK first using --android-studio", "ERROR")
            return False
        
        try:
            # Set environment variables
            self._set_android_env_vars(android_sdk_dir)
            
            # Find sdkmanager
            sdkmanager_cmd = self._find_sdkmanager(android_sdk_dir)
            if not sdkmanager_cmd:
                self.log_status("SDK Manager not found. Please install Android SDK first using --android-studio", "ERROR")
                return False
            
            self.log_status("Installing emulator and system images...")
            
            # Accept licenses first
            self.log_status("Accepting Android SDK licenses...")
            license_process = subprocess.Popen(
                [sdkmanager_cmd, "--licenses"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._get_android_env()
            )
            # Send 'y' for all license prompts
            stdout, stderr = license_process.communicate(input='y\n' * 10)
            
            # Install required packages for pentesting emulator (emulator-specific only)
            packages = [
                "emulator",
                "platforms;android-32",  # Android 12L (Sv2)
                "system-images;android-32;google_apis;x86_64",  # Android 12L (Sv2) with Google APIs
                "build-tools;32.0.0"
            ]
            
            for package in packages:
                self.log_status(f"Installing {package}...")
                result = subprocess.run(
                    [sdkmanager_cmd, package],
                    capture_output=True,
                    text=True,
                    env=self._get_android_env()
                )
                if result.returncode != 0:
                    self.log_status(f"Warning: Failed to install {package}: {result.stderr}", "WARNING")
            
            # Create multiple AVDs for different pentesting scenarios
            self.log_status("Creating Android Virtual Devices for pentesting...")
            avdmanager_cmd = self._find_avdmanager(android_sdk_dir)
            if avdmanager_cmd:
                # Create Android 12L (Sv2) AVD for pentesting
                self.log_status("Creating Android 12L (Sv2) AVD for pentesting...")
                avd_result_32 = subprocess.run([
                    avdmanager_cmd, "create", "avd",
                    "--name", "Android_API_32_Sv2_Pentest",
                    "--package", "system-images;android-32;google_apis;x86_64",
                    "--device", "pixel_4"
                ], capture_output=True, text=True, input="no\n", env=self._get_android_env())
                
                if avd_result_32.returncode == 0:
                    self.log_status("✓ Android 12L (Sv2) Pentest AVD created: Android_API_32_Sv2_Pentest", "SUCCESS")
                    self._configure_pentest_avd("Android_API_32_Sv2_Pentest")
                else:
                    self.log_status(f"Warning: Android 12L (Sv2) AVD creation failed: {avd_result_32.stderr}", "WARNING")
            
            self.log_status("✓ Android Emulator installation completed", "SUCCESS")
            self.log_status("PENTESTING EMULATOR USAGE:", "INFO")
            self.log_status("For best pentesting experience:", "INFO")
            self.log_status("  1. Start with writable system: emulator -avd Android_API_30_Pentest -writable-system", "INFO")
            self.log_status("  2. Or start normally: emulator -avd Android_API_30_Pentest", "INFO")
            self.log_status("  3. Root access: adb root (after emulator starts)", "INFO")
            self.log_status("  4. Remount system: adb remount", "INFO")
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install Android Emulator: {e}", "ERROR")
            return False

    def install_emulator_only(self):
        """Install Android Emulator and AVD setup only (no other tools)"""
        self.log_status("Installing Android Emulator only...")
        
        # First ensure we have Android SDK CLI tools
        if not self.install_android_studio_cli():
            return False
        
        # Then install emulator
        return self.install_android_emulator()

    def install_pentesting_tools_only(self):
        """Install only pentesting tools (APKTool, APKLeaks, MobApp-Storage-Inspector, etc.)"""
        self.log_status("Installing pentesting tools...")
        
        try:
            # Install APKTool
            self.install_apktool()
            
            # Install APKLeaks
            self.install_apkleaks()
            
            # Install MobApp-Storage-Inspector
            self.install_mobapp_storage_inspector()
            
            # Install APKiD
            self._install_pip_tool({
                "name": "APKiD",
                "type": "pip",
                "package": "apkid",
                "description": "Android Application Identifier"
            })
            
            # Install Quark-Engine
            self._install_pip_tool({
                "name": "Quark-Engine",
                "type": "pip",
                "package": "quark-engine",
                "description": "Android malware analysis tool"
            })
            
            self.log_status("✓ Pentesting tools installation completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install pentesting tools: {e}", "ERROR")
            return False

    def install_reverse_engineering_tools_only(self):
        """Install only reverse engineering tools (JADX, fridump, apk-components-inspector)"""
        self.log_status("Installing reverse engineering tools...")
        
        try:
            # Install JADX
            self.install_jadx()
            
            # Install JADX 1.5.2 (specific version)
            self.install_jadx_1_5_2()
            
            # Install fridump
            self._install_git_tool({
                "name": "fridump",
                "type": "git",
                "url": "https://github.com/Nightbringer21/fridump",
                "description": "Memory dumping tool for Frida"
            })
            
            # Install apk-components-inspector
            self.install_apk_components_inspector()
            
            # Install frida-script-gen
            self.install_frida_script_gen()
            
            self.log_status("✓ Reverse engineering tools installation completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install reverse engineering tools: {e}", "ERROR")
            return False

    def install_frida_tools_only(self):
        """Install only Frida-related tools (Frida + Objection + Frida server files)"""
        self.log_status("Installing Frida tools only...")
        
        try:
            # Install Frida Python packages
            frida_packages = [
                "frida-tools>=12.0.0",
                "objection>=1.9.0"
            ]
            
            if not self.install_python_packages(frida_packages):
                return False
            
            # Install Frida server files for different architectures
            if not self.install_frida_server_files():
                return False
            
            # Install fridump (Frida-based memory dumping)
            self._install_git_tool({
                "name": "fridump",
                "type": "git",
                "url": "https://github.com/Nightbringer21/fridump",
                "description": "Memory dumping tool for Frida"
            })
            
            # Install frida-script-gen
            self.install_frida_script_gen()
            
            self.log_status("✓ Frida tools installation completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_status(f"Failed to install Frida tools: {e}", "ERROR")
            return False

    def _set_android_env_vars(self, android_sdk_dir):
        """Set Android SDK environment variables"""
        import os
        os.environ['ANDROID_SDK_ROOT'] = str(android_sdk_dir)
        os.environ['ANDROID_HOME'] = str(android_sdk_dir)
        # Add SDK tools to PATH for current session
        sdk_tools_path = str(android_sdk_dir / "cmdline-tools" / "latest" / "bin")
        platform_tools_path = str(android_sdk_dir / "platform-tools")
        current_path = os.environ.get('PATH', '')
        if sdk_tools_path not in current_path:
            os.environ['PATH'] = f"{sdk_tools_path}{os.pathsep}{current_path}"
        if platform_tools_path not in current_path:
            os.environ['PATH'] = f"{platform_tools_path}{os.pathsep}{os.environ['PATH']}"

    def _get_android_env(self):
        """Get environment with Android SDK variables set"""
        env = os.environ.copy()
        android_sdk_dir = self.tools_dir / "android-sdk"
        if android_sdk_dir.exists():
            env['ANDROID_SDK_ROOT'] = str(android_sdk_dir)
            env['ANDROID_HOME'] = str(android_sdk_dir)
            # Add Java 24 to PATH if available
            java_home = os.environ.get('JAVA_HOME')
            if java_home:
                env['JAVA_HOME'] = java_home
                env['PATH'] = f"{java_home}{os.sep}bin{os.pathsep}{env.get('PATH', '')}"
        return env

    def _find_sdkmanager(self, android_sdk_dir):
        """Find sdkmanager executable"""
        possible_paths = [
            android_sdk_dir / "cmdline-tools" / "latest" / "bin" / f"sdkmanager{self.exe_ext}",
            android_sdk_dir / "cmdline-tools" / "bin" / f"sdkmanager{self.exe_ext}",
            android_sdk_dir / "tools" / "bin" / f"sdkmanager{self.exe_ext}"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # Check in PATH
        return shutil.which(f"sdkmanager{self.exe_ext}")

    def _find_avdmanager(self, android_sdk_dir):
        """Find avdmanager executable"""
        possible_paths = [
            android_sdk_dir / "cmdline-tools" / "latest" / "bin" / f"avdmanager{self.exe_ext}",
            android_sdk_dir / "cmdline-tools" / "bin" / f"avdmanager{self.exe_ext}",
            android_sdk_dir / "tools" / "bin" / f"avdmanager{self.exe_ext}"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # Check in PATH
        return shutil.which(f"avdmanager{self.exe_ext}")

    def _configure_pentest_avd(self, avd_name):
        """Configure AVD for pentesting with optimized settings"""
        try:
            # Get AVD directory
            if self.system == "windows":
                avd_home = Path(os.environ.get('USERPROFILE', '~')) / ".android" / "avd"
            else:
                avd_home = Path.home() / ".android" / "avd"
            
            avd_config_file = avd_home / f"{avd_name}.avd" / "config.ini"
            
            if avd_config_file.exists():
                self.log_status(f"Configuring AVD {avd_name} for pentesting...")
                
                # Read existing config
                with open(avd_config_file, 'r') as f:
                    config = f.read()
                
                # Add/modify pentesting-specific settings
                pentest_settings = [
                    "hw.ramSize=4096",  # More RAM for better performance
                    "vm.heapSize=512",  # Larger heap size
                    "hw.keyboard=yes",  # Hardware keyboard support
                    "hw.gpu.enabled=yes",  # GPU acceleration
                    "hw.gpu.mode=auto",  # Auto GPU mode
                    "showDeviceFrame=no",  # No device frame for better visibility
                    "skin.dynamic=yes"  # Dynamic skin sizing
                ]
                
                # Update or add settings
                config_lines = config.strip().split('\n')
                updated_config = []
                
                for setting in pentest_settings:
                    key = setting.split('=')[0]
                    found = False
                    for i, line in enumerate(config_lines):
                        if line.startswith(f"{key}="):
                            config_lines[i] = setting
                            found = True
                            break
                    if not found:
                        config_lines.append(setting)
                
                # Write updated config
                with open(avd_config_file, 'w') as f:
                    f.write('\n'.join(config_lines))
                
                self.log_status(f"✓ AVD {avd_name} configured for pentesting", "SUCCESS")
            
        except Exception as e:
            self.log_status(f"Warning: Failed to configure AVD {avd_name}: {e}", "WARNING")

    def install_full_android_studio(self):
        """Install full Android Studio IDE"""
        self.log_status("Installing full Android Studio IDE...")
        
        if self.system == "windows":
            # For Windows, download the installer
            download_url = "https://redirector.gvt1.com/edgedl/android/studio/install/2024.1.1.12/android-studio-2024.1.1.12-windows.exe"
            installer_file = self.tools_dir / "android-studio-installer.exe"
            
            try:
                self.log_status("Downloading Android Studio installer...")
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                with open(installer_file, 'wb') as f:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading Android Studio: {percent:.1f}%", end='', flush=True)
                print()  # New line after download
                
                self.log_status("✓ Android Studio installer downloaded", "SUCCESS")
                self.log_status(f"Please run the installer manually: {installer_file}", "INFO")
                self.log_status("Follow the installation wizard to complete Android Studio setup", "INFO")
                return True
                
            except Exception as e:
                self.log_status(f"Failed to download Android Studio: {e}", "ERROR")
                return False
        
        elif self.system == "linux":
            # For Linux, download the tar.gz
            download_url = "https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.1.1.12/android-studio-2024.1.1.12-linux.tar.gz"
            archive_file = self.tools_dir / "android-studio-linux.tar.gz"
            
            try:
                self.log_status("Downloading Android Studio for Linux...")
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                with open(archive_file, 'wb') as f:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading Android Studio: {percent:.1f}%", end='', flush=True)
                print()  # New line after download
                
                # Extract Android Studio
                self.log_status("Extracting Android Studio...")
                with tarfile.open(archive_file, 'r:gz') as tar:
                    tar.extractall(self.tools_dir)
                
                self.log_status("✓ Android Studio installed", "SUCCESS")
                self.log_status(f"Launch with: {self.tools_dir / 'android-studio' / 'bin' / 'studio.sh'}", "INFO")
                
                # Clean up
                archive_file.unlink()
                return True
                
            except Exception as e:
                self.log_status(f"Failed to install Android Studio: {e}", "ERROR")
                return False
        
        elif self.system == "darwin":
            # For macOS, download the dmg
            download_url = "https://redirector.gvt1.com/edgedl/android/studio/install/2024.1.1.12/android-studio-2024.1.1.12-mac.dmg"
            dmg_file = self.tools_dir / "android-studio-mac.dmg"
            
            try:
                self.log_status("Downloading Android Studio for macOS...")
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                with open(dmg_file, 'wb') as f:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading Android Studio: {percent:.1f}%", end='', flush=True)
                print()  # New line after download
                
                self.log_status("✓ Android Studio DMG downloaded", "SUCCESS")
                self.log_status(f"Please mount and install manually: {dmg_file}", "INFO")
                return True
                
            except Exception as e:
                self.log_status(f"Failed to download Android Studio: {e}", "ERROR")
                return False
        
        else:
            self.log_status(f"Unsupported platform for Android Studio: {self.system}", "ERROR")
            return False

    def install_recommended(self):
        """
        Install recommended setup: Android SDK CLI, Emulator, Android 12L (Sv2) x86_64 AVD, and core pentesting tools.
        """
        self.log_status("Starting recommended installation ...", "INFO")
        # 1. Install Android SDK CLI tools
        if not self.install_android_studio_cli():
            self.log_status("Failed to install Android SDK CLI tools.", "ERROR")
            return False
        # 2. Install Emulator and create recommended AVD
        if not self.install_android_emulator():
            self.log_status("Failed to install Android Emulator and AVD.", "ERROR")
            return False
        # 3. Install core pentesting tools
        pentest_success = self.install_pentesting_tools_only()
        # 4. Install reverse engineering tools
        reverse_success = self.install_reverse_engineering_tools_only()
        # 5. Install Frida tools
        frida_success = self.install_frida_tools_only()
        # 6. Create environment setup script
        self.create_environment_script()
        # 7. Verify installation
        self.verify_installation()
        # 8. Save installation report
        self.save_installation_report()
        # Log summary
        if pentest_success and reverse_success and frida_success:
            self.log_status("✓ Recommended installation completed successfully.", "SUCCESS")
            return True
        else:
            self.log_status("Recommended installation completed with some errors. Check log for details.", "WARNING")
            return False
    # ...existing code...
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
  --frida-only     Install only Frida-related tools (Frida + Objection)
  --android-studio Install Android Studio Command Line Tools only
  --android-emulator Install Android Emulator with AVD only (no other tools)
  --android-studio-full Install full Android Studio IDE
  --pentest-tools  Install pentesting tools (APKTool, APKLeaks, MobApp-Storage-Inspector, etc.)
  --reverse-engineering Install reverse engineering tools (JADX, fridump, apk-components-inspector)
  --verify-only    Only verify existing installations

Examples:
  python installer.py --standard
  python installer.py --full
  python installer.py --android-studio
  python installer.py --android-emulator
  python installer.py --android-studio-full
  python installer.py --frida-only
  python installer.py --pentest-tools
  python installer.py --reverse-engineering
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
                      help='Install only Frida-related tools (Frida + Objection)')
    parser.add_argument('--android-studio', action='store_true',
                      help='Install Android Studio Command Line Tools only')
    parser.add_argument('--android-emulator', action='store_true',
                      help='Install Android Emulator with AVD only (no other tools)')
    parser.add_argument('--android-studio-full', action='store_true',
                      help='Install full Android Studio IDE')
    parser.add_argument('--pentest-tools', action='store_true',
                      help='Install pentesting tools (APKTool, APKLeaks, MobApp-Storage-Inspector, etc.)')
    parser.add_argument('--reverse-engineering', action='store_true',
                      help='Install reverse engineering tools (JADX, fridump, apk-components-inspector)')
    parser.add_argument('--verify-only', action='store_true',
                      help='Only verify existing installations')
    parser.add_argument('--recommended', action='store_true',
                      help='Run recommended installation (Android SDK CLI, Emulator, Android 12L (Sv2) x86_64 AVD, core pentesting tools, reverse engineering tools, Frida tools, environment script, verification, and report)')
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
    
    elif args.recommended:
        # Recommended installation
        success = installer.install_recommended()
    elif args.android_studio:
        # Install Android Studio Command Line Tools only
        success = installer.install_android_studio_cli()
    
    elif args.android_emulator:
        # Install Android Emulator with AVD only (no other tools)
        success = installer.install_emulator_only()
    
    elif args.android_studio_full:
        # Install full Android Studio IDE
        success = installer.install_full_android_studio()
    
    elif args.frida_only:
        # Install only Frida-related tools (Frida + Objection + Frida server)
        success = installer.install_frida_tools_only()
    
    elif args.pentest_tools:
        # Install only pentesting tools (APKTool, APKLeaks, MobApp-Storage-Inspector, etc.)
        success = installer.install_pentesting_tools_only()
    
    elif args.reverse_engineering:
        # Install only reverse engineering tools (JADX, fridump, apk-components-inspector)
        success = installer.install_reverse_engineering_tools_only()
    
    elif args.minimal:
        # Minimal installation - only essential Python packages
        essential_packages = [
            "requests>=2.25.1",
            "colorama>=0.4.4"
        ]
        success = installer.install_python_packages(essential_packages)
    
    elif args.full:
        # Full installation - everything
        py_success = installer.install_python_packages()
        sdk_success = installer.install_android_sdk_tools() if py_success else False
        jadx_success = installer.install_jadx() if sdk_success else False
        frida_success = installer.install_frida_server_files() if jadx_success else False
        # Always attempt additional tools, even if previous steps failed
        add_success = installer.install_additional_tools()
        success = py_success and sdk_success and jadx_success and frida_success and add_success
    else:
        # Standard installation (default) - Python packages + Android SDK tools only
        py_success = installer.install_python_packages()
        sdk_success = installer.install_android_sdk_tools() if py_success else False
        success = py_success and sdk_success
    
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

"""
Automated AVD creation and patching with Magisk and Xposed, with writable system and root.
"""
import os
import subprocess
import sys

def print_status(msg):
    print(f"[AVD-Magisk-Xposed] {msg}")

def create_avd_with_magisk_xposed(avd_name="Android_API_30_Pentest", api_level=30, device_profile="pixel", force_recreate=False):
    """
    Creates an AVD, patches it with Magisk and Xposed, and enables writable system/root.
    """
    # 1. Create AVD if not exists
    avdmanager = os.path.join("tools", "android-sdk", "cmdline-tools", "latest", "bin", "avdmanager.bat")
    sdkmanager = os.path.join("tools", "android-sdk", "cmdline-tools", "latest", "bin", "sdkmanager.bat")
    emulator = os.path.join("tools", "android-sdk", "emulator", "emulator.exe")
    avd_path = os.path.expanduser(os.path.join("~", ".android", "avd", f"{avd_name}.avd"))
    if force_recreate or not os.path.exists(avd_path):
        print_status(f"Creating AVD {avd_name} (API {api_level})...")
        subprocess.run([sdkmanager, f"system-images;android-{api_level};google_apis;x86_64"], check=True)
        subprocess.run([avdmanager, "create", "avd", "-n", avd_name, "-k", f"system-images;android-{api_level};google_apis;x86_64", "-d", device_profile, "--force"], check=True)
    else:
        print_status(f"AVD {avd_name} already exists.")
    # 2. Patch with Magisk (auto-download and patch system image)
    print_status("Checking for latest Magisk release...")
    import urllib.request, zipfile, shutil, json
    magisk_dir = os.path.join("tools", "magisk")
    magisk_zip = os.path.join("tools", "Magisk-latest.zip")
    # Fetch latest Magisk release ZIP URL from GitHub API
    api_url = "https://api.github.com/repos/topjohnwu/Magisk/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as resp:
            release = json.load(resp)
            zip_url = None
            for asset in release.get("assets", []):
                name = asset["name"].lower()
                # Only match the main Magisk ZIP, not APK or images
                if name.endswith(".zip") and "magisk" in name and not name.endswith(".apk") and not name.endswith(".img.zip"):
                    zip_url = asset["browser_download_url"]
                    break
            if not zip_url:
                print_status("[ERROR] Could not find Magisk ZIP in latest release assets. Asset list:")
                for asset in release.get("assets", []):
                    print_status(f"  - {asset['name']}")
                return
            if not os.path.exists(magisk_zip):
                print_status(f"Downloading Magisk from {zip_url} ...")
                urllib.request.urlretrieve(zip_url, magisk_zip)
    except Exception as e:
        print_status(f"[ERROR] Failed to fetch/download Magisk: {e}")
        print_status("[INFO] Please manually download Magisk and place it in tools/ directory.")
        return
    except Exception as e:
        print_status(f"[ERROR] Failed to fetch Magisk release: {e}")
        return
    if not os.path.exists(magisk_dir):
        print_status("Extracting Magisk...")
        with zipfile.ZipFile(magisk_zip, 'r') as zip_ref:
            zip_ref.extractall(magisk_dir)
    # Find system image
    avd_home = os.path.expanduser(os.path.join("~", ".android", "avd"))
    avd_img_dir = os.path.join(avd_home, f"{avd_name}.avd")
    system_img = os.path.join(avd_img_dir, "system.img")
    super_img = os.path.join(avd_img_dir, "super.img")
    patched_img = os.path.join(avd_img_dir, "system_magisk.img")
    magiskboot = None
    # Find magiskboot binary
    for root, dirs, files in os.walk(magisk_dir):
        for f in files:
            if f.startswith("magiskboot") and (f.endswith(".exe") or not f.endswith(".so")):
                magiskboot = os.path.join(root, f)
                break
    if not magiskboot:
        print_status("[ERROR] magiskboot binary not found in Magisk zip. Aborting Magisk patch.")
    else:
        # Patch system.img (or super.img if exists)
        img_to_patch = system_img if os.path.exists(system_img) else super_img if os.path.exists(super_img) else None
        if not img_to_patch:
            print_status("[ERROR] No system.img or super.img found in AVD directory. Cannot patch with Magisk.")
        else:
            print_status(f"Patching {os.path.basename(img_to_patch)} with Magisk...")
            # Copy image to working file
            shutil.copy2(img_to_patch, patched_img)
            # Run magiskboot to patch
            patch_cmd = [magiskboot, "patch", patched_img]
            try:
                subprocess.run(patch_cmd, check=True)
                # Replace original image with patched one
                shutil.move(patched_img, img_to_patch)
                print_status(f"Magisk patch successful! Patched image: {img_to_patch}")
            except Exception as e:
                print_status(f"[ERROR] Magisk patch failed: {e}")
    # 3. Patch with Xposed (requires xposed-patch-avd script or manual patch)
    print_status("[INFO] Xposed patching is not automated. Please patch manually if needed.")
    # 4. Launch emulator with writable system
    print_status("Launching emulator with writable system/root...")
    launch_cmd = [emulator, "-avd", avd_name, "-writable-system", "-no-audio", "-gpu", "host", "-no-snapshot-load", "-no-metrics"]
    subprocess.Popen(launch_cmd)
    print_status("Emulator launched. Please wait for full boot, then verify root and Magisk via adb shell.")
    print_status("If you have pre-patched or manually patched system images, place them in the AVD directory before launch.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create and launch AVD with Magisk and Xposed.")
    parser.add_argument("--name", default="Android_API_30_Pentest", help="AVD name")
    parser.add_argument("--api", type=int, default=30, help="API level (default: 30)")
    parser.add_argument("--device", default="pixel", help="Device profile (default: pixel)")
    parser.add_argument("--force", action="store_true", help="Force recreate AVD")
    args = parser.parse_args()
    create_avd_with_magisk_xposed(avd_name=args.name, api_level=args.api, device_profile=args.device, force_recreate=args.force)

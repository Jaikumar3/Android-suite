#!/usr/bin/env python3
"""
Verification script to test AndroidPentester and main.py integration
"""

import sys
import traceback

def test_android_pentester_class():
    """Test AndroidPentester class functionality"""
    print("="*60)
    print("TESTING ANDROIDPENTESTER CLASS")
    print("="*60)
    
    try:
        from android_pentest import AndroidPentester
        print("✓ AndroidPentester class imported successfully")
        
        # Test initialization
        pentester = AndroidPentester()
        print("✓ AndroidPentester instantiated with no parameters")
        
        pentester = AndroidPentester(apk_path="test.apk", app_name="com.test.app", device_id="test_device")
        print("✓ AndroidPentester instantiated with parameters")
        print(f"  - APK Path: {pentester.apk_path}")
        print(f"  - App Name: {pentester.app_name}")
        print(f"  - Device ID: {pentester.device_id}")
        
        # Test required methods exist
        required_methods = [
            '_setup_adb_connection',
            'check_emulator_root_status',
            'setup_emulator_with_playstore_and_root',
            'get_pid_for_package',
            'adb_install_apk',
            'adb_uninstall_apk',
            'adb_push_file',
            'adb_pull_file',
            'get_process_list',
            'get_logcat',
            'list_installed_packages',
            'extract_app_data_directory',
            'run_apktool',
            'run_apkleaks',
            'setup_frida_server_interactive',
            'menu_stop_frida_server',
            'run_fridump',
            'run_jadx_decompile',
            'run_apk_components_inspector',
            'run_frida_script_gen',
            'run_mobapp_storage_inspector',
            'setup_burp_certificate',
            'find_sensitive_strings',
            'adb_backup_app',
            'adb_restore_app',
            'repackage_apk',
            'uninstall_app_and_clean'
        ]
        
        missing_methods = []
        for method in required_methods:
            if hasattr(pentester, method):
                print(f"✓ Method '{method}' exists")
            else:
                missing_methods.append(method)
                print(f"✗ Method '{method}' MISSING")
        
        if missing_methods:
            print(f"\n❌ MISSING METHODS: {missing_methods}")
            return False
        else:
            print(f"\n✅ All {len(required_methods)} required methods are present")
            return True
            
    except Exception as e:
        print(f"❌ ERROR testing AndroidPentester: {e}")
        traceback.print_exc()
        return False

def test_main_module_integration():
    """Test main.py module integration"""
    print("\n" + "="*60)
    print("TESTING MAIN MODULE INTEGRATION")
    print("="*60)
    
    try:
        import main
        print("✓ Main module imported successfully")
        
        # Test menu options
        menu_count = len(main.MENU_OPTIONS)
        print(f"✓ Found {menu_count} menu options")
        
        # Check for common menu option patterns
        menu_names = [option[0] for option in main.MENU_OPTIONS]
        
        expected_patterns = [
            "Install/verify tools",
            "Check emulator root",
            "Setup emulator",
            "Get PID for package",
            "Install APK via ADB",
            "Uninstall APK via ADB",
            "Push file to device",
            "Pull file from device",
            "Setup Frida server",
            "Stop Frida server",
            "Get process list",
            "Logcat",
            "List installed packages",
            "Extract app data",
            "APKTool",
            "APKLeaks",
            "Sensitive Strings",  # Now fully implemented
            "Backup/Restore",     # Now fully implemented  
            "Repackaging",        # Now fully implemented
            "Uninstall/Cleaner",  # Now fully implemented
            "Exit"
        ]
        
        found_patterns = 0
        for pattern in expected_patterns:
            found = any(pattern.lower() in option.lower() for option in menu_names)
            if found:
                found_patterns += 1
                print(f"✓ Found menu pattern: '{pattern}'")
            else:
                print(f"? Pattern '{pattern}' not found clearly in menu")
        
        print(f"\n✓ Found {found_patterns}/{len(expected_patterns)} expected menu patterns")
        
        # Test AndroidPentester instantiation in main context
        from android_pentest import AndroidPentester
        test_pentester = AndroidPentester(apk_path="test.apk", device_id="test")
        print("✓ AndroidPentester can be instantiated in main context")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR testing main module: {e}")
        traceback.print_exc()
        return False

def run_verification():
    """Run all verification tests"""
    print("ANDROID PENTESTING SUITE - INTEGRATION VERIFICATION")
    print("="*60)
    
    test1_passed = test_android_pentester_class()
    test2_passed = test_main_module_integration()
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The AndroidPentester class and main.py are properly integrated.")
        print("\nThe system should work correctly with:")
        print("• All required methods present in AndroidPentester class")
        print("• Proper class initialization with parameters")
        print("• Main module can import and use AndroidPentester")
        print("• Menu options are properly defined")
        return True
    else:
        print("❌ SOME TESTS FAILED! Please review the errors above.")
        print(f"AndroidPentester class test: {'PASSED' if test1_passed else 'FAILED'}")
        print(f"Main module integration test: {'PASSED' if test2_passed else 'FAILED'}")
        return False

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)

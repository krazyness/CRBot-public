#!/usr/bin/env python3
"""
ADB Setup Script for CRBot

This script helps you set up ADB connection with BlueStacks for the CRBot project.
"""

import subprocess
import os
import time
import shutil
from ppadb.client import Client as AdbClient

def find_adb_executable():
    """Find adb.exe in common locations"""
    # Common locations for Android SDK platform-tools
    common_paths = [
        # Check if adb is in PATH
        shutil.which("adb"),
        # BlueStacks sometimes includes its own ADB
        "C:/Program Files/BlueStacks_nxt/HD-Adb.exe",
        "C:/Program Files/BlueStacks/HD-Adb.exe",
        "C:/Program Files (x86)/BlueStacks/HD-Adb.exe",
    ]
    
    for path in common_paths:
        if path and os.path.exists(path):
            print(f"Found ADB at: {path}")
            return path
    
    # If not found, try to use adb from PATH
    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Using ADB from PATH")
            return "adb"
    except FileNotFoundError:
        pass
    
    return None

def check_adb_installed():
    """Check if ADB is installed and accessible"""
    adb_path = find_adb_executable()
    
    if not adb_path:
        print("✗ ADB is not installed or not found")
        print("\nPlease install ADB:")
        print("1. Download Android SDK Platform Tools from:")
        print("   https://developer.android.com/studio/releases/platform-tools")
        print("2. Extract to a folder (e.g., C:/Android/Sdk/platform-tools/)")
        print("3. Add the platform-tools directory to your PATH, or")
        print("4. Place adb.exe in your project directory")
        return False, None
    
    try:
        result = subprocess.run([adb_path, 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ADB is installed and accessible")
            version_line = result.stdout.split('\n')[0]
            print(f"ADB version: {version_line}")
            return True, adb_path
        else:
            print("✗ ADB command failed")
            return False, adb_path
    except Exception as e:
        print(f"✗ Error running ADB: {e}")
        return False, adb_path

def check_adb_server():
    """Check if ADB server is running"""
    try:
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()
        print(f"✓ ADB server is running, found {len(devices)} device(s)")
        return True, devices
    except Exception as e:
        print(f"✗ ADB server connection failed: {e}")
        return False, []

def start_adb_server(adb_path="adb"):
    """Start ADB server using specified ADB executable"""
    try:
        print("Starting ADB server...")
        result = subprocess.run([adb_path, 'start-server'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ ADB server started successfully")
            time.sleep(2)  # Give server time to start
            return True
        else:
            print(f"✗ Failed to start ADB server: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ ADB server start timed out")
        return False
    except Exception as e:
        print(f"✗ Error starting ADB server: {e}")
        return False

def connect_bluestacks(adb_path="adb"):
    """Connect to BlueStacks via ADB"""
    print("\nConnecting to BlueStacks...")
    
    # Common BlueStacks ADB ports
    ports = [5555, 5557, 5559, 5561]
    
    for port in ports:
        try:
            result = subprocess.run([adb_path, 'connect', f'127.0.0.1:{port}'], 
                                  capture_output=True, text=True)
            if 'connected' in result.stdout.lower():
                print(f"✓ Connected to BlueStacks on port {port}")
                return True
        except Exception as e:
            print(f"Failed to connect on port {port}: {e}")
    
    print("✗ Could not connect to BlueStacks")
    print("\nTroubleshooting:")
    print("1. Make sure BlueStacks is running")
    print("2. Enable ADB in BlueStacks settings:")
    print("   Settings > Advanced > Android Debug Bridge > Enable")
    print("3. Restart BlueStacks after enabling ADB")
    return False

def list_devices():
    """List connected ADB devices"""
    try:
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()
        
        if not devices:
            print("No devices connected")
            return
            
        print(f"\nConnected devices ({len(devices)}):")
        for i, device in enumerate(devices):
            print(f"  {i+1}. {device.serial}")
            
            # Get device info
            try:
                model = device.shell("getprop ro.product.model").strip()
                android_version = device.shell("getprop ro.build.version.release").strip()
                resolution = device.shell("wm size").strip()
                print(f"     Model: {model}")
                print(f"     Android: {android_version}")
                print(f"     Resolution: {resolution}")
            except Exception as e:
                print(f"     Could not get device info: {e}")
                
    except Exception as e:
        print(f"Error listing devices: {e}")

def test_screenshot():
    """Test taking a screenshot"""
    try:
        from Actions import Actions
        print("\nTesting screenshot functionality...")
        
        actions = Actions()
        if actions.device:
            screenshot = actions._take_screenshot()
            if screenshot:
                test_path = "screenshots/test_screenshot.png"
                screenshot.save(test_path)
                print(f"✓ Screenshot saved to {test_path}")
                return True
            else:
                print("✗ Failed to take screenshot")
                return False
        else:
            print("✗ No device connected")
            return False
    except Exception as e:
        print(f"✗ Screenshot test failed: {e}")
        return False

def ensure_adb_ready():
    """Ensure ADB is ready for use. Returns True if ready, False otherwise."""
    # Check ADB installation and get path
    adb_available, adb_path = check_adb_installed()
    if not adb_available:
        return False
    
    # Check/start ADB server
    server_running, devices = check_adb_server()
    if not server_running:
        print("Starting ADB server...")
        if not start_adb_server(adb_path):
            return False
        time.sleep(2)
        server_running, devices = check_adb_server()
    
    # Connect to BlueStacks if no devices found
    if not devices:
        print("No devices connected. Attempting to connect to BlueStacks...")
        if connect_bluestacks(adb_path):
            time.sleep(2)
            server_running, devices = check_adb_server()
            return len(devices) > 0
    
    return len(devices) > 0

def main():
    print("CRBot ADB Setup Script")
    print("=" * 30)
    
    # Check ADB installation and get path
    adb_available, adb_path = check_adb_installed()
    if not adb_available:
        return
    
    # Check/start ADB server
    server_running, devices = check_adb_server()
    if not server_running:
        print("Starting ADB server...")
        if not start_adb_server(adb_path):
            return
        time.sleep(2)
        server_running, devices = check_adb_server()
    
    # Connect to BlueStacks if no devices found
    if not devices:
        print("\nNo devices connected. Attempting to connect to BlueStacks...")
        if connect_bluestacks(adb_path):
            time.sleep(2)
            server_running, devices = check_adb_server()
    
    # List devices
    list_devices()
    
    # Test screenshot
    if devices:
        test_screenshot()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Make sure BlueStacks is running with Clash Royale open")
    print("2. Adjust the device coordinates in Actions.py if needed")
    print("3. Run train.py to start the bot")

if __name__ == "__main__":
    main()

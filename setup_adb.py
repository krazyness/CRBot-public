#!/usr/bin/env python3
"""
ADB Setup Script for CRBot

This script helps you set up ADB connection with BlueStacks for the CRBot project.
"""

import subprocess
import os
import time
from ppadb.client import Client as AdbClient

def check_adb_installed():
    """Check if ADB is installed and accessible"""
    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ADB is installed and accessible")
            print(f"ADB version: {result.stdout.split()[4]}")
            return True
        else:
            print("✗ ADB command failed")
            return False
    except FileNotFoundError:
        print("✗ ADB is not installed or not in PATH")
        return False

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

def start_adb_server():
    """Start ADB server"""
    try:
        subprocess.run(['adb', 'start-server'], check=True)
        print("✓ ADB server started")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start ADB server: {e}")
        return False

def connect_bluestacks():
    """Connect to BlueStacks via ADB"""
    print("\nConnecting to BlueStacks...")
    
    # Common BlueStacks ADB ports
    ports = [5555, 5557, 5559, 5561]
    
    for port in ports:
        try:
            result = subprocess.run(['adb', 'connect', f'127.0.0.1:{port}'], 
                                  capture_output=True, text=True)
            if 'connected' in result.stdout.lower():
                print(f"✓ Connected to BlueStacks on port {port}")
                return True
        except Exception as e:
            print(f"Failed to connect on port {port}: {e}")
    
    print("✗ Could not connect to BlueStacks")
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
                test_path = "test_screenshot.png"
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

def main():
    print("CRBot ADB Setup Script")
    print("=" * 30)
    
    # Check ADB installation
    if not check_adb_installed():
        print("\nPlease install ADB:")
        print("1. Download Android SDK Platform Tools")
        print("2. Add the platform-tools directory to your PATH")
        print("3. Run this script again")
        return
    
    # Check/start ADB server
    server_running, devices = check_adb_server()
    if not server_running:
        print("Starting ADB server...")
        if not start_adb_server():
            return
        time.sleep(2)
        server_running, devices = check_adb_server()
    
    # Connect to BlueStacks if no devices found
    if not devices:
        print("\nNo devices connected. Attempting to connect to BlueStacks...")
        if connect_bluestacks():
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

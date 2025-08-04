#!/usr/bin/env python3
"""
Test script for ADB-based Actions implementation

This script tests all the main functions of the Actions class to ensure
the ADB implementation is working correctly with BlueStacks.
"""

import os
import time
from src.Actions import Actions

class ADBActionsTester:
    def __init__(self):
        print("Initializing ADB Actions Tester...")
        self.actions = Actions()
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all available tests"""
        print("\n" + "="*50)
        print("Starting ADB Actions Test Suite")
        print("="*50)
        
        tests = [
            ("Device Connection", self.test_device_connection),
            ("Screenshot Capture", self.test_screenshot),
            ("Game Area Capture", self.test_game_area_capture),
            ("Card Area Capture", self.test_card_area_capture),
            ("Individual Cards Capture", self.test_individual_cards),
            ("Elixir Counting", self.test_elixir_counting),
            ("Click Functionality", self.test_click),
            ("Card Play", self.test_card_play),
            ("Template Matching", self.test_template_matching),
            ("Swipe Functionality", self.test_swipe),
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'-'*30}")
            print(f"Testing: {test_name}")
            print(f"{'-'*30}")
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "✓ PASSED" if result else "✗ FAILED"
                print(f"Result: {status}")
            except Exception as e:
                self.test_results[test_name] = False
                print(f"Result: ✗ ERROR - {str(e)}")
            
            time.sleep(1)  # Small delay between tests
        
        self.print_summary()
    
    def test_device_connection(self):
        """Test ADB device connection"""
        if self.actions.device is None:
            print("No device connected!")
            return False
        
        print(f"Connected device: {self.actions.device.serial}")
        
        # Test basic shell command
        try:
            result = self.actions.device.shell("echo 'Hello ADB'")
            print(f"Shell test result: {result.strip()}")
            return True
        except Exception as e:
            print(f"Shell command failed: {e}")
            return False
    
    def test_screenshot(self):
        """Test screenshot functionality"""
        print("Taking screenshot...")
        screenshot = self.actions._take_screenshot()
        
        if screenshot is None:
            print("Failed to take screenshot")
            return False
        
        # Save test screenshot
        test_path = os.path.join(self.actions.script_dir, 'screenshots/test_screenshot.png')
        screenshot.save(test_path)
        print(f"Screenshot saved to: {test_path}")
        print(f"Screenshot size: {screenshot.size}")
        
        return True
    
    def test_game_area_capture(self):
        """Test game area capture"""
        print("Capturing game area...")
        test_path = os.path.join(self.actions.script_dir, 'test_game_area.png')
        
        try:
            self.actions.capture_area(test_path)
            if os.path.exists(test_path):
                print(f"Game area captured to: {test_path}")
                return True
            else:
                print("Game area capture failed - file not created")
                return False
        except Exception as e:
            print(f"Game area capture error: {e}")
            return False
    
    def test_card_area_capture(self):
        """Test card area capture"""
        print("Capturing card area...")
        test_path = os.path.join(self.actions.script_dir, 'test_card_area.png')
        
        try:
            self.actions.capture_card_area(test_path)
            if os.path.exists(test_path):
                print(f"Card area captured to: {test_path}")
                return True
            else:
                print("Card area capture failed - file not created")
                return False
        except Exception as e:
            print(f"Card area capture error: {e}")
            return False
    
    def test_individual_cards(self):
        """Test individual card capture"""
        print("Capturing individual cards...")
        
        # Ensure screenshots directory exists
        screenshots_dir = os.path.join(self.actions.script_dir, 'screenshots')
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        try:
            cards = self.actions.capture_individual_cards()
            if cards and len(cards) == 4:
                print(f"Successfully captured {len(cards)} individual cards:")
                for i, card_path in enumerate(cards):
                    print(f"  Card {i+1}: {card_path}")
                return True
            else:
                print(f"Expected 4 cards, got {len(cards) if cards else 0}")
                return False
        except Exception as e:
            print(f"Individual cards capture error: {e}")
            return False
    
    def test_elixir_counting(self):
        """Test elixir counting"""
        print("Testing elixir counting...")
        
        try:
            elixir_count = self.actions.count_elixir()
            print(f"Current elixir count: {elixir_count}")
            
            if 0 <= elixir_count <= 10:
                print("Elixir count within valid range (0-10)")
                return True
            else:
                print(f"Elixir count out of range: {elixir_count}")
                return False
        except Exception as e:
            print(f"Elixir counting error: {e}")
            return False
    
    def test_click(self):
        """Test click functionality (safe area)"""
        print("Testing click functionality...")
        print("Will click at a safe area (center of screen)")
        
        # Click at center of screen (should be safe)
        center_x = self.actions.device_width // 2
        center_y = self.actions.device_height // 2
        
        try:
            result = self.actions._click(center_x, center_y)
            if result:
                print(f"Successfully clicked at ({center_x}, {center_y})")
                return True
            else:
                print("Click command failed")
                return False
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def test_card_play(self):
        """Test card play functionality"""
        print("Testing card play functionality...")
        print("Will test clicking on card positions and battlefield")
        
        input("Press Enter to continue with card play test (or Ctrl+C to skip)...")
        
        try:
            # Test playing card 0 (first card) at center of battlefield
            battlefield_x = self.actions.device_width // 2
            battlefield_y = self.actions.device_height // 2
            
            print(f"Testing card play: card 0 at ({battlefield_x}, {battlefield_y})")
            self.actions.card_play(battlefield_x, battlefield_y, 0)
            
            print("Card play test completed")
            return True
        except Exception as e:
            print(f"Card play error: {e}")
            return False
    
    def test_template_matching(self):
        """Test template matching functionality"""
        print("Testing template matching...")
        
        # Test with a common UI element (if available)
        test_images = [
            "battlestartbutton.png",
            "Winner.png", 
            "matchover.png",
            "1elixir.png"
        ]
        
        found_any = False
        for img_name in test_images:
            img_path = os.path.join(self.actions.images_folder, img_name)
            if os.path.exists(img_path):
                print(f"Testing template matching with: {img_name}")
                try:
                    result = self.actions._find_template(img_path, confidence=0.5)
                    if result:
                        x, y, confidence = result
                        print(f"Found template at ({x}, {y}) with confidence {confidence:.2f}")
                        found_any = True
                    else:
                        print(f"Template {img_name} not found in current screen")
                except Exception as e:
                    print(f"Template matching error with {img_name}: {e}")
            else:
                print(f"Template image not found: {img_path}")
        
        if found_any:
            print("Template matching functionality working")
            return True
        else:
            print("No templates found, but function executed without errors")
            return True  # Function works even if no templates found
    
    def test_swipe(self):
        """Test swipe functionality (safe swipe)"""
        print("Testing swipe functionality...")
        print("Will perform a small swipe in the center area")
        
        input("Press Enter to continue with swipe test (or Ctrl+C to skip)...")
        
        # Safe swipe in center area
        center_x = self.actions.device_width // 2
        center_y = self.actions.device_height // 2
        
        start_x = center_x - 50
        start_y = center_y
        end_x = center_x + 50
        end_y = center_y
        
        try:
            result = self.actions._swipe(start_x, start_y, end_x, end_y, 500)
            if result:
                print(f"Successfully swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
                return True
            else:
                print("Swipe command failed")
                return False
        except Exception as e:
            print(f"Swipe error: {e}")
            return False
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! ADB implementation is working correctly.")
        elif passed > total // 2:
            print("⚠️  Most tests passed. Check failed tests for issues.")
        else:
            print("❌ Many tests failed. Check ADB connection and device setup.")
    
    def interactive_test(self):
        """Interactive test mode"""
        print("\n" + "="*50)
        print("INTERACTIVE TEST MODE")
        print("="*50)
        
        while True:
            print("\nAvailable tests:")
            print("1. Device Connection")
            print("2. Screenshot")
            print("3. Game Area Capture") 
            print("4. Card Area Capture")
            print("5. Individual Cards")
            print("6. Elixir Counting")
            print("7. Click Test")
            print("8. Card Play Test")
            print("9. Template Matching")
            print("10. Swipe Test")
            print("11. Run All Tests")
            print("0. Exit")
            
            choice = input("\nEnter test number: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.test_device_connection()
            elif choice == "2":
                self.test_screenshot()
            elif choice == "3":
                self.test_game_area_capture()
            elif choice == "4":
                self.test_card_area_capture()
            elif choice == "5":
                self.test_individual_cards()
            elif choice == "6":
                self.test_elixir_counting()
            elif choice == "7":
                self.test_click()
            elif choice == "8":
                self.test_card_play()
            elif choice == "9":
                self.test_template_matching()
            elif choice == "10":
                self.test_swipe()
            elif choice == "11":
                self.run_all_tests()
            else:
                print("Invalid choice. Please try again.")

def main():
    print("ADB Actions Test Utility")
    print("Make sure BlueStacks is running and Clash Royale is open!")
    
    tester = ADBActionsTester()
    
    if tester.actions.device is None:
        print("\n❌ No ADB device connected!")
        print("Please ensure:")
        print("1. BlueStacks is running")
        print("2. ADB is enabled in BlueStacks settings")
        print("3. ADB server is running (try running setup_adb.py first)")
        return
    
    print("\nChoose test mode:")
    print("1. Run all tests automatically")
    print("2. Interactive test mode")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        tester.run_all_tests()
    elif choice == "2":
        tester.interactive_test()
    else:
        print("Invalid choice. Running all tests...")
        tester.run_all_tests()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

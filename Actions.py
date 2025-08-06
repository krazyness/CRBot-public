from ppadb.client import Client as AdbClient
import io
from PIL import Image
import cv2
import numpy as np
import os
from datetime import datetime
import time
import platform

from utils import take_screenshot, timing_decorator

class Actions:
    def __init__(self):
        self.os_type = platform.system()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.images_folder = os.path.join(self.script_dir, 'main_images')

        # Initialize ADB connection
        self.adb_client = AdbClient(host="127.0.0.1", port=5037)
        self.device = None
        self._connect_device()

        # BlueStacks default resolution (you may need to adjust based on your setup)
        self.device_width = 1080
        self.device_height = 1920
        
        # Define game area coordinates in device space (not screen space)
        # These need to be adjusted based on your BlueStacks resolution and Clash Royale layout
        self.TOP_LEFT_X = 0
        self.TOP_LEFT_Y = 0
        
        self.BOTTOM_RIGHT_X = self.device_width
        self.BOTTOM_RIGHT_Y = self.device_height
        self.FIELD_AREA = (self.TOP_LEFT_X, self.TOP_LEFT_Y, self.BOTTOM_RIGHT_X, self.BOTTOM_RIGHT_Y)
    
        self.WIDTH = self.device_height
        self.HEIGHT = self.device_height
        
        # Card bar coordinates in device space
        self.CARD_BAR_X = 237
        self.CARD_BAR_Y = 1590
        self.CARD_BAR_WIDTH = 820
        self.CARD_BAR_HEIGHT = 250

    def _connect_device(self):
        """Connect to the BlueStacks ADB device"""
        try:
            devices = self.adb_client.devices()
            if not devices:
                print("No ADB devices found. Make sure BlueStacks is running and ADB is enabled.")
                print("Run setup_adb.py first to configure ADB connection.")
                return False
             
            # Usually BlueStacks appears as the first device, but you might need to select the right one
            self.device = devices[0]
            print("Successfully connected to ADB device: ", self.device.serial)
            return True
        except Exception as e:
            print(f"Failed to connect to ADB device: {e}")
            print("Run setup_adb.py first to configure ADB connection.")
            return False

    @timing_decorator
    def _take_screenshot(self):
        """Take a screenshot using ADB"""
        if not self.device:
            print("No device connected")
            return None
        try:
            screen = take_screenshot(self.device.serial)
            
            # screen.save(os.path.join(self.script_dir, 'screenshots', 'current.png'))
            
            return screen
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None

    def _click(self, x, y):
        """Click at coordinates using ADB"""
        if not self.device:
            print("No device connected")
            return False
        
        try:
            self.device.shell(f"input touchscreen swipe {x} {y} {x} {y} 300")
            return True
        except Exception as e:
            print(f"Failed to click at ({x}, {y}): {e}")
            return False

    def _swipe(self, x1, y1, x2, y2, duration=500):
        """Swipe from (x1,y1) to (x2,y2) using ADB"""
        if not self.device:
            print("No device connected")
            return False
        
        try:
            self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
            return True
        except Exception as e:
            print(f"Failed to swipe: {e}")
            return False

    def capture_area(self, save_path):
        """Capture screenshot of game area using ADB"""
        screenshot = self._take_screenshot()
        if screenshot:
            # Crop to game area
            cropped = screenshot.crop((self.TOP_LEFT_X, self.TOP_LEFT_Y, self.BOTTOM_RIGHT_X, self.BOTTOM_RIGHT_Y))
            cropped.save(save_path)
        else:
            print("Failed to capture screenshot")

    def capture_card_area(self, save_path):
        """Capture screenshot of card area using ADB"""
        screenshot = self._take_screenshot()
        if screenshot:
            # Crop to card bar area
            cropped = screenshot.crop((
                self.CARD_BAR_X, 
                self.CARD_BAR_Y, 
                self.CARD_BAR_X + self.CARD_BAR_WIDTH, 
                self.CARD_BAR_Y + self.CARD_BAR_HEIGHT
            ))
            cropped.save(save_path)
        else:
            print("Failed to capture card area screenshot")

    @timing_decorator
    def capture_individual_cards(self):
        """Capture and split card bar into individual card images using ADB"""
        screenshot = self._take_screenshot()
        if not screenshot:
            print("Failed to capture screenshot for individual cards")
            return []
            
        # Crop to card bar area
        card_bar = screenshot.crop((
            self.CARD_BAR_X, 
            self.CARD_BAR_Y, 
            self.CARD_BAR_X + self.CARD_BAR_WIDTH, 
            self.CARD_BAR_Y + self.CARD_BAR_HEIGHT
        ))
        
        # Calculate individual card widths
        card_width = self.CARD_BAR_WIDTH // 4
        cards = []
        
        # Split into 4 individual card images
        for i in range(4):
            left = i * card_width
            card_img = card_bar.crop((left, 0, left + card_width, self.CARD_BAR_HEIGHT))
            save_path = os.path.join(self.script_dir, 'screenshots', f"card_{i+1}.png")
            card_img.save(save_path)
            cards.append(save_path)
        
        return cards

    @timing_decorator
    def count_elixir(self):
        """Count elixir using ADB screenshot analysis"""
        screenshot = self._take_screenshot()
        if not screenshot:
            print("Failed to capture screenshot for elixir counting")
            return 0
            
        # Convert PIL image to numpy array for OpenCV processing
        screenshot_np = np.array(screenshot)
        
        # Define elixir bar region in device coordinates (you may need to adjust these)
        elixir_y = 1860  # Approximate Y coordinate of elixir bar
        elixir_start_x = 355  # Start X coordinate
        elixir_end_x = 1050    # End X coordinate  
        elixir_spacing = 65   # Spacing between elixir icons
        
        target = (225, 128, 229)  # Target purple color for elixir
        tolerance = 80
        count = 0
        
        # Check each elixir position
        for x in range(elixir_start_x, elixir_end_x, elixir_spacing):
            if x < screenshot_np.shape[1] and elixir_y < screenshot_np.shape[0]:
                # Get pixel color at elixir position (convert from RGB to BGR for OpenCV)
                b, g, r = screenshot_np[elixir_y, x][:3]  # OpenCV uses BGR format
                
                # Check if color matches elixir color within tolerance
                if (abs(r - target[0]) <= tolerance and 
                    abs(g - target[1]) <= tolerance and 
                    abs(b - target[2]) <= tolerance):
                    count += 1
                    
        return min(count, 10)  # Cap at 10 elixir

    def _find_template(self, template_path, confidence=0.8, region=None):
        """Find template image in screenshot using OpenCV template matching"""
        screenshot = self._take_screenshot()
        if not screenshot:
            return None
            
        # Convert PIL to OpenCV format
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Crop to region if specified
        if region:
            x, y, w, h = region
            screenshot_cv = screenshot_cv[y:y+h, x:x+w]
            offset_x, offset_y = x, y
        else:
            offset_x, offset_y = 0, 0
            
        # Load template
        template = cv2.imread(template_path)
        if template is None:
            print(f"Could not load template: {template_path}")
            return None
            
        # Perform template matching
        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)        
        if max_val >= confidence:
            # Return center coordinates with offset
            template_h, template_w = template.shape[:2]
            center_x = max_loc[0] + template_w // 2 + offset_x
            center_y = max_loc[1] + template_h // 2 + offset_y
            return (center_x, center_y, max_val)
       
        return None

    def card_play(self, x, y, card_index):
        """Play a card using ADB commands"""
        print(f"Playing card {card_index} at position ({x}, {y})")
        if card_index in range(4):  # Valid card indices are 0-3
            # Calculate card position in the deck
            card_width = self.CARD_BAR_WIDTH // 4
            card_center_x = self.CARD_BAR_X + (card_index * card_width) + (card_width // 2)
            card_center_y = self.CARD_BAR_Y + (self.CARD_BAR_HEIGHT // 2)
            
            print(f"Clicking on card {card_index} at deck position ({card_center_x}, {card_center_y})")
            self._click(card_center_x, card_center_y)
            time.sleep(0.2)
            
            if y > 1440:
                y = 1440
            if x > 1070:
                x = 1070
                
            print(f"Placing card at battlefield position ({x}, {y})")
            self._click(x, y)
        else:
            print(f"Invalid card index: {card_index} (must be 0-3)")

    def click_battle_start(self):
        """Find and click the battle start button using ADB and template matching"""
        button_image = os.path.join(self.images_folder, "battlestartbutton.png")
        confidences = [0.8, 0.7, 0.6, 0.5]  # Try multiple confidence levels

        # Define the region for the battle button in device coordinates
        battle_button_region = (300, 1350, 480, 300)  # Adjust based on your device resolution

        while True:
            for confidence in confidences:
                print(f"Looking for battle start button (confidence: {confidence})")
                result = self._find_template(button_image, confidence, battle_button_region)
                if result:
                    x, y, match_confidence = result
                    print(f"Found battle button at ({x}, {y}) with confidence {match_confidence}")
                    self._click(x, y)
                    time.sleep(2)
                    return

            # If button not found, click to clear screens
            self.click_ok_button()  # Click OK button if any popups appear

            print("Button not found, clicking to clear screens...")
            self._click(640, 200)  # Center-ish click in device coordinates
            time.sleep(1)

    @timing_decorator
    def detect_game_end(self):
        """Detect game end using ADB and template matching"""
        try:
            winner_img = os.path.join(self.images_folder, "Winner.png")
            confidences = [0.8, 0.7, 0.6]

            # Define winner detection region in device coordinates
            winner_region = (0, 0, self.WIDTH, self.HEIGHT)  # Adjust based on your device resolution

            for confidence in confidences:
                # print(f"\nTrying detection with confidence: {confidence}")
                
                result = self._find_template(winner_img, confidence, winner_region)
                if result:
                    x, y, match_confidence = result
                    print(f"Found 'Winner' at ({x}, {y}) with confidence {match_confidence}")
                    
                    # Determine if victory or defeat based on position
                    result_type = "victory" if y > 300 else "defeat"  # Adjust threshold based on device
                    print(f"Game result: {result_type}")
                    time.sleep(5)
                    
                    self.click_ok_button()

                    return result_type
        except Exception as e:
            print(f"Error in game end detection: {str(e)}")
        return None

    def click_ok_button(self):
        """Click the OK button to close popups"""
        ok_button_image = os.path.join(self.images_folder, "okbutton.png")
        confidences = [0.8, 0.6, 0.4]

        # Define the region for the OK button in device coordinates
        ok_button_region = (0, self.HEIGHT / 2, self.WIDTH, self.HEIGHT)
        for confidence in confidences:
            print(f"Looking for OK button (confidence: {confidence})")
            result = self._find_template(ok_button_image, confidence, ok_button_region)
            if result:
                x, y, match_confidence = result
                print(f"Found OK button at ({x}, {y}) with confidence {match_confidence}")
                self._click(x, y)
                time.sleep(2)
                return
    
    @timing_decorator
    def detect_match_over(self):
        """Detect match over using ADB and template matching"""
        matchover_img = os.path.join(self.images_folder, "matchover.png")
        confidences = [0.8, 0.6, 0.4]
        
        # Define the region where the matchover image appears in device coordinates
        region = (100, 570, 900, 200)  # Adjust based on your device resolution
        
        for confidence in confidences:
            result = self._find_template(matchover_img, confidence, region)
            if result:
                print("Match over detected!")
                return True
                
        return False
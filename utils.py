from functools import wraps
import subprocess
import time
from PIL import Image
from setup_adb import find_adb_executable

ADB_PATH = find_adb_executable()

def timing_decorator(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        # Use class logger if available, otherwise fall back to print
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"[Performance] {func.__name__:<25} took {execution_time:.4f} seconds")
        else:
            print(f"[Performance] {func.__name__:<25} took {execution_time:.4f} seconds")

        return result
    return wrapper

def take_screenshot(device_id=None):
    """Take screenshot from specified device or the default device"""
    # Build the command
    cmd = [ADB_PATH]
    
    # Add device selection if specified
    if device_id:
        cmd.extend(["-s", device_id])
    else:
        cmd.append("-d")  # Default to the only connected USB device
    
    # Add other command parameters    
    cmd.extend([
        "exec-out",
        "screencap"
    ])
    timeout = 2

    screenshot_proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        timeout=timeout,
        bufsize=-1
    )
    
    try:
        # Parse the header (first 12 bytes) from the raw binary data
        w = int.from_bytes(screenshot_proc.stdout[0:4], byteorder='little')
        h = int.from_bytes(screenshot_proc.stdout[4:8], byteorder='little')
        f = int.from_bytes(screenshot_proc.stdout[8:12], byteorder='little')
        
        # print(f"Image dimensions: {w}x{h}, format: {f}")
        
        # Extract the actual image data (skip the 12-byte header)
        raw_bytes = screenshot_proc.stdout[12:]
        
        # Create a PIL Image from the raw bytes
        if f == 1:  # RGBA_8888 format (most common on Android)
            image = Image.frombuffer('RGBA', (w, h), raw_bytes, 'raw', 'RGBA', 0, 1)
        else:
            print(f"Unsupported format: {f}")
            return None
        
        # # Save the image
        # device_suffix = f"_{device_id}" if device_id else ""
        # output_path = f"screenshot{device_suffix}.png"
        # image.save(output_path)
        # print(f"Screenshot saved to {output_path}")
        
        # # Optionally display some information about the image
        # print(f"Image size: {image.width}x{image.height}")
        # print(f"Image format: {image.mode}")
        # print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
        
        return image
        
    except Exception as e:
        print(f"Error processing screenshot: {e}")
        return None

if __name__ == "__main__":
    take_screenshot('emulator-5554')  # Example device ID, replace with actual if needed
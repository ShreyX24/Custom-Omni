from pathlib import Path
from uuid import uuid4
import pyautogui
from PIL import Image, ImageDraw
from io import BytesIO
from .base import BaseAnthropicTool, ToolError

OUTPUT_DIR = "./tmp/outputs"

def get_screenshot(resize: bool = False, target_width: int = 1920, target_height: int = 1080):
    """Capture screenshot directly from local system with cursor overlay"""
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"screenshot_{uuid4().hex}.png"
    
    try:
        # Use pyautogui to capture the screen
        screenshot = pyautogui.screenshot()
        
        # Add cursor to the screenshot
        cursor_x, cursor_y = pyautogui.position()
        draw = ImageDraw.Draw(screenshot)
        
        # Draw a visible cursor (circle with crosshair)
        cursor_radius = 10
        draw.ellipse((cursor_x - cursor_radius, cursor_y - cursor_radius, 
                      cursor_x + cursor_radius, cursor_y + cursor_radius), 
                     outline='red', width=2)
        
        # Add crosshair
        draw.line((cursor_x - cursor_radius * 2, cursor_y, cursor_x + cursor_radius * 2, cursor_y), 
                  fill='red', width=1)
        draw.line((cursor_x, cursor_y - cursor_radius * 2, cursor_x, cursor_y + cursor_radius * 2), 
                  fill='red', width=1)
        
        # Resize if needed
        if resize and screenshot.size != (target_width, target_height):
            screenshot = screenshot.resize((target_width, target_height))
            
        screenshot.save(path)
        return screenshot, path
    except Exception as e:
        raise ToolError(f"Failed to capture screenshot: {str(e)}")
import base64
import time
from enum import StrEnum
from typing import Literal, TypedDict

import pyautogui
from PIL import Image

from anthropic.types.beta import BetaToolComputerUse20241022Param

from .base import BaseAnthropicTool, ToolError, ToolResult
from .screen_capture import get_screenshot

OUTPUT_DIR = "./tmp/outputs"

TYPING_DELAY_MS = 12
TYPING_GROUP_SIZE = 50

Action = Literal[
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "screenshot",
    "cursor_position",
    "hover",
    "wait",
    "scroll_up",
    "scroll_down"
]


class Resolution(TypedDict):
    width: int
    height: int


class ScalingSource(StrEnum):
    COMPUTER = "computer"
    API = "api"


class ComputerToolOptions(TypedDict):
    display_height_px: int
    display_width_px: int
    display_number: int | None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]

class ComputerTool(BaseAnthropicTool):
    """
    A tool that allows the agent to interact with the screen, keyboard, and mouse of the local computer.
    """

    name: Literal["computer"] = "computer"
    api_type: Literal["computer_20241022"] = "computer_20241022"
    width: int
    height: int
    display_num: int | None

    _screenshot_delay = 2.0
    _scaling_enabled = True

    @property
    def options(self) -> ComputerToolOptions:
        width, height = self.scale_coordinates(
            ScalingSource.COMPUTER, self.width, self.height
        )
        return {
            "display_width_px": width,
            "display_height_px": height,
            "display_number": self.display_num,
        }

    def to_params(self) -> BetaToolComputerUse20241022Param:
        return {"name": self.name, "type": self.api_type, **self.options}

    def __init__(self, is_scaling: bool = False):
        super().__init__()

        # Initialize screen and mouse settings
        self.display_num = None
        self.offset_x = 0
        self.offset_y = 0
        self.is_scaling = is_scaling
        # Get the current screen resolution
        self.width, self.height = self.get_screen_size()
        print(f"screen size: {self.width}, {self.height}")

        # Map for key conversion
        self.key_conversion = {"Page_Down": "pagedown",
                              "Page_Up": "pageup",
                              "Super_L": "win",
                              "Escape": "esc"}

    async def __call__(
        self,
        *,
        action: Action,
        text: str | None = None,
        coordinate: tuple[int, int] | None = None,
        **kwargs,
    ):
        print(f"action: {action}, text: {text}, coordinate: {coordinate}, is_scaling: {self.is_scaling}")
        
        # Mouse movement and drag actions
        if action in ("mouse_move", "left_click_drag"):
            if coordinate is None:
                raise ToolError(f"coordinate is required for {action}")
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
                raise ToolError(f"{coordinate} must be a tuple of length 2")
            if not all(isinstance(i, int) for i in coordinate):
                raise ToolError(f"{coordinate} must be a tuple of integers")
            
            if self.is_scaling:
                x, y = self.scale_coordinates(
                    ScalingSource.API, coordinate[0], coordinate[1]
                )
            else:
                x, y = coordinate

            if action == "mouse_move":
                pyautogui.moveTo(x, y)
                return ToolResult(output=f"Moved mouse to ({x}, {y})")
            elif action == "left_click_drag":
                current_x, current_y = pyautogui.position()
                pyautogui.dragTo(x, y, duration=0.5)
                return ToolResult(output=f"Dragged mouse from ({current_x}, {current_y}) to ({x}, {y})")

        # Keyboard input actions
        if action in ("key", "type"):
            if text is None:
                raise ToolError(f"text is required for {action}")
            if coordinate is not None:
                raise ToolError(f"coordinate is not accepted for {action}")
            if not isinstance(text, str):
                raise ToolError(output=f"{text} must be a string")

            if action == "key":
                # Handle key combinations
                keys = text.split('+')
                for key in keys:
                    key = self.key_conversion.get(key.strip(), key.strip())
                    key = key.lower()
                    pyautogui.keyDown(key)  # Press down each key
                for key in reversed(keys):
                    key = self.key_conversion.get(key.strip(), key.strip())
                    key = key.lower()
                    pyautogui.keyUp(key)    # Release each key in reverse order
                return ToolResult(output=f"Pressed keys: {text}")
            
            elif action == "type":
                # default click before type to ensure focus
                pyautogui.click()
                pyautogui.write(text, interval=TYPING_DELAY_MS / 1000)
                pyautogui.press('enter')
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(output=text, base64_image=screenshot_base64)

        # Mouse click and screenshot actions
        if action in (
            "left_click",
            "right_click",
            "double_click",
            "middle_click",
            "screenshot",
            "cursor_position",
            "hover",
        ):
            if text is not None:
                raise ToolError(f"text is not accepted for {action}")
            
            # For click actions that require coordinates
            if action in ("left_click", "right_click", "double_click", "middle_click", "hover") and coordinate is not None:
                if self.is_scaling:
                    x, y = self.scale_coordinates(
                        ScalingSource.API, coordinate[0], coordinate[1]
                    )
                else:
                    x, y = coordinate
                
                # Move to coordinate first
                pyautogui.moveTo(x, y)

            if action == "screenshot":
                return await self.screenshot()
            elif action == "cursor_position":
                x, y = pyautogui.position()
                if self.is_scaling:
                    x, y = self.scale_coordinates(ScalingSource.COMPUTER, x, y)
                return ToolResult(output=f"X={x},Y={y}")
            elif action == "left_click":
                pyautogui.click()
            elif action == "right_click":
                pyautogui.rightClick()
            elif action == "middle_click":
                pyautogui.middleClick()
            elif action == "double_click":
                pyautogui.doubleClick()
            elif action == "hover":
                # Already moved to position, just need to wait briefly
                time.sleep(0.5)
            
            # If we've performed a mouse action, capture what happened and return
            if action != "cursor_position":
                screenshot_base64 = (await self.screenshot()).base64_image
                return ToolResult(output=f"Performed {action}", base64_image=screenshot_base64)
            
        # Scroll actions
        if action in ("scroll_up", "scroll_down"):
            if action == "scroll_up":
                pyautogui.scroll(100)  # Positive for up
            elif action == "scroll_down":
                pyautogui.scroll(-100)  # Negative for down
                
            screenshot_base64 = (await self.screenshot()).base64_image
            return ToolResult(output=f"Performed {action}", base64_image=screenshot_base64)
            
        # Wait action
        if action == "wait":
            time.sleep(1)
            return ToolResult(output=f"Performed {action}")
            
        raise ToolError(f"Invalid action: {action}")

    async def screenshot(self):
        """Capture a screenshot of the local desktop"""
        screenshot, path = get_screenshot()
        time.sleep(0.7)  # Brief delay to allow UI to update if needed
        return ToolResult(base64_image=base64.b64encode(path.read_bytes()).decode())

    def scale_coordinates(self, source: ScalingSource, x: int, y: int):
        """Convert between raw and scaled coordinates if needed"""
        if not self._scaling_enabled:
            return x, y
            
        # In a real implementation, you might need to scale between
        # different coordinate systems, but for now we'll just pass through
        return x, y

    def get_screen_size(self):
        """Get the current screen resolution"""
        screen_width, screen_height = pyautogui.size()
        return screen_width, screen_height
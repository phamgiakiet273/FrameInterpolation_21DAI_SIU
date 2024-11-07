import numpy as np
import win32gui, win32ui, win32con
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
import cv2

class WindowCapture:
    def __init__(self, window_name):
        # Set process DPI awareness
        windll.user32.SetProcessDPIAware()

        # Find the window handle
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception(f'Window not found: {window_name}')

        # Get window metrics and calculate cropped region
        self.update_window_metrics()

    def update_window_metrics(self):
        # Get the outer window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.full_width = window_rect[2] - window_rect[0]
        self.full_height = window_rect[3] - window_rect[1]

        # Get the client area size (content area without borders)
        client_rect = win32gui.GetClientRect(self.hwnd)
        client_width = client_rect[2]
        client_height = client_rect[3]

        # Calculate border and title bar sizes
        self.border_pixels = (self.full_width - client_width) // 2
        self.titlebar_pixels = self.full_height - client_height - self.border_pixels

        # Set cropped width, height, and offsets to account for borders
        self.w = client_width
        self.h = client_height
        self.cropped_x = self.border_pixels
        self.cropped_y = self.titlebar_pixels

    def get_screenshot(self):
        try:
            # Get window DC
            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()

            # Create bitmap object
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.full_width, self.full_height)
            cDC.SelectObject(dataBitMap)

            # Capture the window contents
            windll.user32.PrintWindow(self.hwnd, cDC.GetSafeHdc(), 2)

            # Convert to numpy array
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.frombuffer(signedIntsArray, dtype='uint8')
            img.shape = (self.full_height, self.full_width, 4)

            # Free resources
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            # Convert from BGRA to BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Crop out the borders and title bar
            img = img[self.cropped_y:self.cropped_y + self.h, self.cropped_x:self.cropped_x + self.w]

            return img

        except Exception as e:
            print(f"Screenshot failed: {str(e)}")
            return None

    def get_window_info(self):
        """Get detailed information about the target window"""
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            client_rect = win32gui.GetClientRect(self.hwnd)
            class_name = win32gui.GetClassName(self.hwnd)
            window_text = win32gui.GetWindowText(self.hwnd)
            
            print(f"\nWindow Information:")
            print(f"Handle: {hex(self.hwnd)}")
            print(f"Title: '{window_text}'")
            print(f"Class: {class_name}")
            print(f"Window Rect: {rect}")
            print(f"Client Rect: {client_rect}")
            print(f"Dimensions (cropped): {self.w}x{self.h}")

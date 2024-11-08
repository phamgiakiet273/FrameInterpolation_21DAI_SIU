import cv2 as cv
import numpy as np
import win32gui
from time import time
from windowcapture import WindowCapture

def list_window_names():
    window_names = []  # List to store window names

    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:  # Skip if the window name is an empty string
                window_names.append(window_text)  

    win32gui.EnumWindows(winEnumHandler, None) 
    return window_names  

def capture_and_display(app_name, exp=1):
    # Initialize the WindowCapture class with the provided app_name
    wincap = WindowCapture(app_name)

    # Print detailed information about the target window
    wincap.get_window_info()

    print("\nStarting capture loop...")
    print("Press 'q' to quit")
    print("Press 'r' to reset window size")
    print("You can now resize the window using mouse")

    # Create a named window that's resizable
    cv.namedWindow('App Display', cv.WINDOW_NORMAL)

    # Set initial window size to match the game's dimensions
    initial_width = wincap.w
    initial_height = wincap.h
    cv.resizeWindow('App Display', initial_width, initial_height)

    loop_time = time()
    while True:
        # Get screenshot
        screenshot = wincap.get_screenshot()
        
        # Check if screenshot was successful
        if screenshot is not None and screenshot.size > 0:
            """# interpolatedScreenshot = Interpolate(screenshot) <- Add code to do interpolation
            if img0.shape[2] == 4 and screenshot.shape[2] == 3: # code to convert if different channel, add img0 before use
                screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2BGRA)
            elif img0.shape[2] == 3 and screenshot.shape[2] == 4:
                screenshot = cv.cvtColor(screenshot, cv.COLOR_BGRA2BGR)"""

            # Display the screenshot
            cv.imshow('App Display', screenshot)
        else:
            print("Failed to capture screenshot")

        # Calculate and display FPS
        current_time = time()
        fps = 1 / (current_time - loop_time)
        loop_time = current_time
        print(f'FPS: {fps:.2f}', end='\r')

        # Handle keyboard input
        key = cv.waitKey(1)
        if key == ord('q'):
            cv.destroyAllWindows()
            break
        elif key == ord('r'):
            # Reset window size to original dimensions
            cv.resizeWindow('App Display', initial_width, initial_height)

    print('\nDone.')

# Example usage
window_list = list_window_names()
print(window_list)
capture_and_display('BlueStacks App Player')

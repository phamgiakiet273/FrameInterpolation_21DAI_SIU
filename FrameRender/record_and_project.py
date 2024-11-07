import cv2 as cv
import numpy as np
from time import time
from windowcapture import WindowCapture

# Initialize the WindowCapture class
# example: BlueStacks App Player | Into the Breach
window_name = 'BlueStacks App Player'  # Change this to match exactly your window name
wincap = WindowCapture(window_name)

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
        """interpolatedScreenshot = Interpolate(screenshot) <- Add code to do interpolation"""
        if img0.shape[2] == 4 and screenshot.shape[2] == 3: # code to convert if different channel, add img0 b4 use
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2BGRA)
        elif img0.shape[2] == 3 and screenshot.shape[2] == 4:
            screenshot = cv.cvtColor(screenshot, cv.COLOR_BGRA2BGR)

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
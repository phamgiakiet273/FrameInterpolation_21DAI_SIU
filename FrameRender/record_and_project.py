import cv2 as cv
import win32gui
from time import time, sleep
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

def measure_app_fps(window_name, duration=3):
    """Measure the average FPS of the target application over a specified duration."""
    wincap = WindowCapture(window_name)
    frames_captured = 0
    start_time = time()

    while time() - start_time < duration:
        screenshot = wincap.get_screenshot()
        if screenshot is not None:
            frames_captured += 1

    # Calculate FPS and round to 30, 45, or 60
    avg_fps = frames_captured / duration
    if avg_fps < 37.5:
        target_fps = 30
    elif avg_fps < 52.5:
        target_fps = 45
    else:
        target_fps = 60

    print(f"\nMeasured FPS: {avg_fps:.2f}, Rounding to Target FPS: {target_fps}")
    return target_fps

def capture_and_display(app_name, exp=1):
    # Measure the app's FPS and set target delay for capture rate
    target_fps = measure_app_fps(app_name)
    capture_interval = 1 / target_fps  # Time between frames

    wincap = WindowCapture(app_name)

    print("\nStarting capture loop...")
    cv.namedWindow('App Display', cv.WINDOW_NORMAL)

    initial_width, initial_height = wincap.w, wincap.h
    cv.resizeWindow('App Display', initial_width, initial_height)

    while True:
        start_time = time()

        # Get screenshot
        screenshot = wincap.get_screenshot()
        if screenshot is not None and screenshot.size > 0:
            # Display the screenshot
            """# interpolatedScreenshot = Interpolate(screenshot) <- Add code to do interpolation
            if img0.shape[2] == 4 and screenshot.shape[2] == 3: 
                screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2BGRA)
            elif img0.shape[2] == 3 and screenshot.shape[2] == 4:
                screenshot = cv.cvtColor(screenshot, cv.COLOR_BGRA2BGR)"""

            cv.imshow('App Display', screenshot)
        else:
            print("Failed to capture screenshot")

        # Handle keyboard input
        key = cv.waitKey(1)
        if key == ord('q'):
            cv.destroyAllWindows()
            break
        elif key == ord('r'):
            cv.resizeWindow('App Display', initial_width, initial_height)

        # Maintain capture rate by sleeping for the remaining interval time
        elapsed = time() - start_time
        if elapsed < capture_interval:
            sleep(capture_interval - elapsed)

    print('\nDone.')

# Example usage
window_list = list_window_names()
print(window_list)
capture_and_display('Into The Breach')

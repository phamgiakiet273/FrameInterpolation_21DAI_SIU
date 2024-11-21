import cv2
import win32gui
from time import time
from subprocess import Popen, PIPE
from windowcapture import WindowCapture

OUTPUT_FILE = r"C:\Users\F14_TOMCAT\Downloads\GIAO_TRINH\ComputerVision\FrameInterpolation_21DAI_SIU\FrameRender\output.flv"

def list_window_names():
    """Lists all visible window names."""
    window_names = []

    def win_enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:
                window_names.append(window_text)

    win32gui.EnumWindows(win_enum_handler, None)
    return window_names

def measure_app_fps(window_name, duration=3):
    """Measures the average FPS of the target application."""
    wincap = WindowCapture(window_name)
    frames_captured = 0
    start_time = time()

    while time() - start_time < duration:
        screenshot = wincap.get_screenshot()
        if screenshot is not None:
            frames_captured += 1

    avg_fps = frames_captured / duration
    if avg_fps < 28:
        target_fps = 15
    elif avg_fps < 43:
        target_fps = 30
    elif avg_fps < 58:
        target_fps = 45
    else:
        target_fps = 60

    print(f"Measured FPS: {avg_fps:.2f}, Rounding to Target FPS: {target_fps}")
    return target_fps

def capture_and_stream(app_name):
    """Captures frames from the target app and streams/saves using FFmpeg."""
    actual_target_fps = measure_app_fps(app_name)
    capture_interval = int(1000 / actual_target_fps)  # Convert FPS to milliseconds
    wincap = WindowCapture(app_name)

    # Launch FFmpeg as a subprocess with optimized settings
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{wincap.w}x{wincap.h}",
        "-r", str(actual_target_fps),  # Keep original target FPS for output
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",  # Optimize for low-latency
        "-pix_fmt", "yuv420p",
        "-bufsize", "512k",  # Smaller buffer size
        "-probesize", "32",  # Reduce probe size
        "-f", "flv",
        OUTPUT_FILE
    ]

    ffmpeg_process = Popen(ffmpeg_cmd, stdin=PIPE)

    print(f"Starting capture and stream... (Capture target: {actual_target_fps} FPS)")

    try:
        while True:
            start_time = time()

            frame = wincap.get_screenshot()
            if frame is not None:
                # Write the raw frame data to FFmpeg's stdin
                ffmpeg_process.stdin.write(frame.tobytes())
            else:
                print("Failed to capture frame.")

            # Enforce consistent frame capture interval
            elapsed = time() - start_time
            remaining_time = capture_interval - (elapsed * 1000)
            if remaining_time > 0:
                cv2.waitKey(int(remaining_time))  # Wait for the remaining time in milliseconds

    except KeyboardInterrupt:
        print("\nCapture interrupted by user.")
    finally:
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        print("Capture and stream ended.")

if __name__ == "__main__":
    window_list = list_window_names()
    print("Available Windows:")
    for i, window_name in enumerate(window_list, start=1):
        print(f"{i}: {window_name}")

    target_window_index = int(input("Select the window index: ")) - 1
    app_name = window_list[target_window_index]

    capture_and_stream(app_name)
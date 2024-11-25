import win32gui
import math
from time import time, perf_counter
from subprocess import Popen, PIPE
from windowcapture import WindowCapture

OUTPUT_FILE = "C:/Users/F14_TOMCAT/Downloads/GIAO_TRINH/ComputerVision/FrameInterpolation_21DAI_SIU/FrameRender/output.flv"

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
    start_time = perf_counter()  # High-precision timer

    while perf_counter() - start_time < duration:
        screenshot = wincap.get_screenshot()
        if screenshot is not None:
            frames_captured += 1

    elapsed_time = perf_counter() - start_time  # Calculate exact elapsed time
    avg_fps = frames_captured / elapsed_time if elapsed_time > 0 else 0  # Avoid divide-by-zero
    target_fps = math.floor(avg_fps)

    print(f"Measured FPS: {avg_fps:.2f}, Rounding to Target FPS: {target_fps}")
    return target_fps

def capture_and_stream(app_name, FPS=0):
    """Captures frames from the target app and streams/saves using FFmpeg."""
    actual_target_fps = measure_app_fps(app_name)
    wincap = WindowCapture(app_name)

    # Launch FFmpeg as a subprocess with optimized settings
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-s", f"{wincap.w}x{wincap.h}",
        "-r", str(FPS) if FPS > 0 else str(actual_target_fps), 
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",  # Optimize for low-latency
        "-bufsize", "512K",
        #"-pix_fmt", "yuv420p",
        #"-max_delay", "0",  
        "-bf", "0", 
        "-f", "flv",
        OUTPUT_FILE
    ]

    ffmpeg_process = Popen(ffmpeg_cmd, stdin=PIPE)

    print(f"Starting capture and stream...")

    try:
        loop_time = time()
        fps_list = []
        start_time = time()

        while True:
            if FPS == 0 and time() - start_time >= 5:
                break

            frame = wincap.get_screenshot()
            if frame is not None:
                # Write the raw frame data to FFmpeg's stdin
                ffmpeg_process.stdin.write(frame.tobytes())
            else:
                print("Failed to capture frame.")
                continue

            # Append Recording FPS to list
            current_time = time()
            fps = 1 / (current_time - loop_time)
            fps_list.append(fps)
            loop_time = current_time
            print(f'FPS: {fps:.2f}', end='\r')

    except KeyboardInterrupt:
        if FPS > 0:
            print("\nCapture interrupted by user.")
    finally:
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        print("Capture and stream ended.")

    # Calc recording FPS
    #avgRecordFPS = sum(fps_list) / loop_count if loop_count > 0 else 0 <= Outlier effected
    fps_list.sort()
    middle_index = len(fps_list) // 2
    if len(fps_list) % 2 == 0:
        # If even number of elements, take the average of the two middle values
        medianRecordFPS = (fps_list[middle_index - 1] + fps_list[middle_index]) / 2
    else:
        # If odd number of elements, take the middle value
        medianRecordFPS = fps_list[middle_index]

    return math.floor(medianRecordFPS)

if __name__ == "__main__":
    window_list = list_window_names()
    print("Available Windows:")
    for i, window_name in enumerate(window_list, start=1):
        print(f"{i}: {window_name}")

    target_window_index = int(input("Select the window index: ")) - 1
    app_name = window_list[target_window_index]

    # dummy loop to calc Recording FPS
    FPS = capture_and_stream(app_name, 0)
    print('\nRecording FPS = ' + str(FPS) + '\n')
    # real loop
    capture_and_stream(app_name, FPS)
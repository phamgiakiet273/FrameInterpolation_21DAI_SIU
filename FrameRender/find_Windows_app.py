import win32gui

def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:  # Skip if the window name is an empty string
                print(f"Window title: '{window_text}'")

    win32gui.EnumWindows(winEnumHandler, None)

list_window_names()

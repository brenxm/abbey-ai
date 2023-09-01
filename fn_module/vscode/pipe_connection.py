import pygetwindow as gw
import pyautogui
import win32file
import pywintypes
import re


# Wait for the pipe to become available
def request(request_type):
    window_title = gw.getWindowsWithTitle(pyautogui.getActiveWindow().title)
    pipe_code_match = re.search(r'\s-\s(.*?)\s-\s', window_title[0].title)
    
    PIPE_NAME = f'\\\\.\\pipe\\{pipe_code_match.group(1)}'
    
    while True:
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0, None,
                win32file.OPEN_EXISTING,
                0, None)
            break
        except pywintypes.error as e:
            if e.args[0] == 2: # File not found error
                continue
            raise

    # Connect and receive the message

    message_to_send = request_type.encode('utf-8')
    win32file.WriteFile(handle, message_to_send)

    _, data = win32file.ReadFile(handle, 10000)
    win32file.CloseHandle(handle)
    
    return data.decode('utf-8')

import win32file
import pywintypes


# Wait for the pipe to become available
def request(requestType):
    PIPE_NAME = f'\\.\pipe\{requestType}'
    
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

    message_to_send = b"getActiveCode"
    win32file.WriteFile(handle, message_to_send)

    _, data = win32file.ReadFile(handle, 2000) # Read up to 64 bytes
    win32file.CloseHandle(handle)
    
    return data.decode('utf-8')

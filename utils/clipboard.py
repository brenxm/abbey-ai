import pyperclip

def get_copied_text(max_length=10000):
    copied_text = pyperclip.paste()
    
    # Check if the copied text is a reasonable length
    if len(copied_text) > max_length:
        print("The copied data is too large and might not be text.")
        return None
    
    return f"copied text: {copied_text}."

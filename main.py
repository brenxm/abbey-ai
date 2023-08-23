from function_interface import FunctionsInterface
from abbey import AbbeyAI
from tts import TextToSpeech
from stt import VoiceInput
from audioplayer import AudioPlayer
from threading import Lock
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication
import subprocess
from gui.blackboard import MainWindow
import pygetwindow as gw
import pyautogui

input_type = "press_to_speak"  # press to speak or voice activated
queue_lock = Lock()
audio_queue = []
tts_queue = []

audio_player = AudioPlayer(tts_queue)
tts = TextToSpeech(tts_queue, audio_player)
voice_input = VoiceInput(audio_player)
abbey = AbbeyAI(tts_queue, None, audio_player, tts)
fn_interface = FunctionsInterface()

abbey.set_personality("You are my AI assistant named Abbey. You respond with direct to the point, elaborated but straight to point answer.")

abbey.set_name("Abbey")


def get_active_window_title():
    window = gw.getWindowsWithTitle(pyautogui.getActiveWindow().title)
    
    if window:
        return window[0].title.lower()
    return None


def handle_prompt(prompt_input):
    
    # Result 1 or 2
    route_code = abbey.prompt_router(prompt_input)

    if route_code == '1':
        result_obj = abbey.general_prompt(prompt_input)
        
    elif route_code == '2':
        window = get_active_window_title()
        if "visual studio code" in window:
            fn_interface.load('vscode')
            
        result_obj = abbey.function_prompt(prompt_input, fn_interface.functions)
        print(result_obj)
        
    else:
        print(route_code)
        print('hallucinated response')
        return

    if result_obj["stream"]:
        # Start convertion of the text generated from openai, arg is an audio player function
        
        print(result_obj)
        # Add to user's prompt to chat history
        
        abbey.memory.add_chat_history("user", prompt_input)
        print(f'added users prompt input to history')
        # Full response message is returned after all chunks are read
        full_message = abbey.stream_result(result_obj["content"], tts.convert, audio_player.listen)
        
        # Add openai full response to chat history
        abbey.memory.add_chat_history("assistant", full_message)
        
        
    else:
        print("didn't get an object")
    return True
        

# Init/listen to keystroke event
voice_input.init(handle_prompt)




def show_blackboard():
    subprocess.run(['python', 'gui/blackboard.py'], stdout=subprocess.PIPE)
    
#show_blackboard()
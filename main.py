from abbey import AbbeyAI
from tts import TextToSpeech
from stt import VoiceInput
from audioplayer import AudioPlayer
from threading import Lock
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication
import time
import threading
import subprocess
from gui.blackboard import MainWindow

input_type = "press_to_speak"  # press to speak or voice activated
queue_lock = Lock()
audio_queue = []
tts_queue = []

ai_name = "Abbey"

audio_player = AudioPlayer(tts_queue)
tts = TextToSpeech(tts_queue, audio_player)
voice_input = VoiceInput(audio_player)
abbey = AbbeyAI(tts_queue, ai_name, None, audio_player, tts)


def handle_prompt(text):
    result_obj = abbey.prompt(text) # returns a chunk or full response

    if result_obj["stream"]:
        # Start convertion of the text generated from openai, arg is an audio player function
        tts.start(audio_player.listen)
        
        # Add to user's prompt to chat history
        abbey.memory.add_chat_history("user", text)
        
        # Full response message is returned after all chunks are read
        full_message = abbey.stream_result(result_obj["content"])
        
        # Add openai full response to chat history
        abbey.memory.add_chat_history("assistant", full_message)
        
        # End audio converstion
        tts.end()
        
     
    else:
        print("didn't get an object")
    return True
        
    
# voice_input.init(handle_prompt)




def show_blackboard():
    subprocess.run(['python', 'gui/blackboard.py'], stdout=subprocess.PIPE)
    
#show_blackboard()
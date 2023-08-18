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

audio_player = AudioPlayer(tts_queue)
tts = TextToSpeech(tts_queue, audio_player)
voice_input = VoiceInput(audio_player)
abbey = AbbeyAI(tts_queue, None, audio_player, tts)

abbey.set_personality("You are my AI assistant name Abbey. You speak like a human being, an asshole, sassy, loofy but coherent, elaborates and straight to the point. Try to limit your response to few sentence as possible. You can also have the capabilities to access my personal data such as notes, reminders and task as well as my computer system. You can do task such as review code from VS code, make script, invoke a termnial prompt and etc. No need to end response with questions like 'If you need more questions, feel freet to ask.'")

abbey.set_name("Abbey")


def handle_prompt(text):
    result_obj = abbey.prompt(text) # returns a chunk or full response

    if result_obj["stream"]:
        # Start convertion of the text generated from openai, arg is an audio player function
        
        print(result_obj)
        # Add to user's prompt to chat history
        abbey.memory.add_chat_history("user", text)
        
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
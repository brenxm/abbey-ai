from abbey import AbbeyAI
from tts import TextToSpeech
from stt import VoiceInput
from audioplayer import AudioPlayer
from threading import Lock
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication
import sys
import time
import threading
import subprocess
from pynput import keyboard
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

# Initialized to their own thread
#voice_input_thread = VoiceInputThread(voice_input, abbey.prompt)

#voice_input_thread.start()

input_thread = threading.Thread(target=voice_input.init, args=(abbey.prompt,))
input_thread.start()

def show_blackboard():
    subprocess.run(['python', 'gui/blackboard.py'], stdout=subprocess.PIPE)
    
show_blackboard()
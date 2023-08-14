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

# Current way to initialize the program
input_thread = threading.Thread(target=voice_input.init, args=(abbey.prompt,))
input_thread.start()

def show_blackboard():
    subprocess.run(['python', 'gui/blackboard.py'], stdout=subprocess.PIPE)
    
#show_blackboard()
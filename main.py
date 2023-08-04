from abbey import AbbeyAI
from tts import TextToSpeech
from stt import VoiceInput
from audioplayer import AudioPlayer
from threading import Lock
import time
from PyQt6.QtWidgets import QApplication
import sys
from blackboard import MainWindow
from pynput import keyboard



input_type = "press_to_speak"  # press to speak or voice activated
queue_lock = Lock()
audio_queue = []
tts_queue = []

ai_name = "Abbey"

audio_player = AudioPlayer(tts_queue)
tts = TextToSpeech(tts_queue, audio_player)
voice_input = VoiceInput(audio_player)
abbey = AbbeyAI(tts_queue, ai_name, None, audio_player, tts)


voice_input.init(abbey.prompt)


import speech_recognition as sr
import pyaudio
from pynput import keyboard
import time
import os
import io
import openai
import tempfile
import librosa

from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class VoiceInput():
    def __init__(self, audio_player, voice_trigger = False):
        self.voice_trigger = voice_trigger
        self.recognizer = sr.Recognizer()
        self._keyboard_listening = False
        self.audio_player = audio_player
    
    
    def init(self, fn):
        if not self.voice_trigger:
            self._init_keyboard_listeners()
        
        # waiting for key strokes
        while True:
            
            while self._keyboard_listening:
                text = self._start_record()
                fn(text)
                # Wait until the audio player and tts is completed
                while  self.audio_player.is_playing or len(self.audio_player.queue) > 0:
                    time.sleep(0.3)
                    print('still waiting')
                self._init_keyboard_listeners()
                
            time.sleep(0.3)
                
     
    def _init_keyboard_listeners(self):
        def onpress(key):
            try:
                if key == key.f20:
                    self._keyboard_listening = True
            except:
                pass
            
        def onrelease(key):
            try:
                if key == key.f20:
                    print('rlease q')
                    self._keyboard_listening = False
                    return False
            except:
                pass
                
        listener = keyboard.Listener(on_press=onpress, on_release=onrelease)
        listener.start()

    
    def _detect_noise(threshold=300, buffer_length=10):
        p = pyaudio.PyAudio()
        buffer = []
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        print("Listening for noise...")
        
        while True:
            data = stream.read(1024)
            values = [int.from_bytes(data[i:i+2], 'little', signed=True) for i in range(0, len(data), 2)]
            
            if max(values) > threshold:
                print("Noise detected")
                break
                
            if len(buffer) > buffer_length:
                buffer.pop(0)
                
        stream.stop_stream()
        stream.close()
        p.terminate()
        return b"".join(buffer)
    

    def _start_record(self, timeout=None, phrase_time_limit=None, buffer=None):
        with sr.Microphone() as source:
            print("Please say something")
            try:
                # Capture audio from the microphone
                audio_data = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                # Add buffer if needed
                audio_data = sr.AudioData(buffer + audio_data.get_wav_data(), 44100, 2) if buffer else audio_data
              
                # Write the audio data to a temporary WAV file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(audio_data.get_wav_data())
                    temp_path = temp_file.name

                # Open the temporary WAV file
                with open(temp_path, "rb") as audio_file:
                    # Transcribe the audio using OpenAI's service
                    transcript = openai.Audio.transcribe("whisper-1", audio_file)

                # Remove the temporary file
                os.remove(temp_path)

                text = transcript['text']

                print(text)
                if self.voice_trigger and ("abby" in text.lower() or "abbey" in text.lower()):
                    return text
                else:
                    return text
            except:
                print('Not a good read, try again')


                
                
        

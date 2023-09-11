from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput import keyboard
import speech_recognition as sr
import pyaudio
import time
import os
import openai
import tempfile
import re
import threading
import traceback

class VoiceInput():
    def __init__(self, audio_player, voice_trigger = False):
        self.voice_trigger = voice_trigger
        self.recognizer = sr.Recognizer()
        self._keyboard_listening = False
        self.audio_player = audio_player
        self.listening = True
        self.low_volume = 0.1
        self.original_volume = 1
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        self.volume_controller = cast(self.interface, POINTER(IAudioEndpointVolume))
        self.saving_volume = True
        self.whisper_thread_open = False
        self.transcribed_text = ""
        self.audio_data_queue = []
        self.recording_audio = False
    
    
    def init(self, fn):
        if not self.voice_trigger:
            self._init_keyboard_listeners()
            
        self.listening = True
        
        # waiting for key strokes
        while self.listening:
            
            while self._keyboard_listening:
                print('stuck here help')
                text = self._start_record()
                # If whisper not a valid synthesize
                if not text:
                    self._init_keyboard_listeners()
                    break
                
                print(f"{text} - it's a good read, sending to prompt")
                fn(text)
                # Wait until the audio player and tts is completed
                while  self.audio_player.is_playing or len(self.audio_player.queue) > 0:
                    time.sleep(0.3)
                    print('still waiting')
                self._init_keyboard_listeners()
                
            time.sleep(0.05)
            
            
                
     
    def _init_keyboard_listeners(self):
        def onpress(key):
            try:
                if key == key.f20:
                    self._keyboard_listening = True
                    if self.saving_volume:
                        self.original_volume = self.volume_controller.GetMasterVolumeLevelScalar()
                        print(self.original_volume)
                        self.volume_controller.SetMasterVolumeLevelScalar(self.low_volume, None)
                        self.saving_volume = False
                    
            except:
                pass
            
        def onrelease(key):
            try:
                if key == key.f20:
                    print('rlease q')
                    self._keyboard_listening = False
                    self.saving_volume = True
                    print('returend')
                    return False
            except:
                pass
                print('failed')
                
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
    
    def _start_record(self, timeout=1000, phrase_time_limit=None, buffer=None):
        with sr.Microphone() as source:
            print("Please say something")
            audio_data = ""
            try:
                # Capture audio from the microphone
                while self._keyboard_listening:
                    try:
                        audio_data = self.recognizer.listen(source, timeout=1)
                    except:
                        continue
                    if audio_data:
                        # Add buffer if needed
                        self.audio_data_queue.append(audio_data)
                        audio_data = ""
                        
                        if not self.whisper_thread_open:
                            transcribe_thread = threading.Thread(target=self.whisper_transcribe)
                            transcribe_thread.start()
                            
                print("up to here")            
                if audio_data:
                    # Add buffer if needed
                    self.audio_data_queue.append(audio_data)
                    audio_data = ""
                    
                    if not self.whisper_thread_open:
                        transcribe_thread = threading.Thread(target=self.whisper_transcribe)
                        transcribe_thread.start()
                
                
                # Wait until transcribing is finish
                while self.whisper_thread_open:
                    time.sleep(0.05)
                    pass
                
                # Ensure that transcripted text is valid
                
                
                self.volume_controller.SetMasterVolumeLevelScalar(self.original_volume, None)
                result_text = self.transcribed_text
                
                audio_data = ""
                self.transcribed_text = ""
                self.recording_audio = False
                return result_text
            
            except Exception as e:
                print(f"FAILED: {e}")
                print(f"ERROR TYPE: {type(e).__name__}")
                print("ERROR TRACEBACK:")
                traceback.print_tb(e.__traceback__)
                print(f"ERROR ARGS: {e.args}")
                print('Not a good read, try again')
                
                if self.transcribed_text:
                    result_test = self.transcribed_text
                    self.transcribed_text = ""
                    return result_test
                
                
    def whisper_transcribe(self):
        # Write the audio data to a temporary WAV file
        print("received audio data, transcribing now.")
        self.whisper_thread_open = True
        audio_data = self.audio_data_queue.pop(0)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data.get_wav_data())
            temp_path = temp_file.name

        # Open the temporary WAV file
        with open(temp_path, "rb") as audio_file:
            # Transcribe the audio using OpenAI's service
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        # Remove the temporary file
        os.remove(temp_path)

        self.transcribed_text += f" {transcript['text']}"
        
        if len(self.audio_data_queue) > 0:
            self.whisper_transcribe()
            
        else:
            print("ending transcribing")
            print(transcript["text"])
            self.whisper_thread_open = False
            
    
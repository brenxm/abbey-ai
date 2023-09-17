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
    def __init__(self, audio_player, voice_trigger=False):
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
        self.audio_chunks = []

        with sr.Microphone() as mic:
            self.SAMPLE_RATE = mic.SAMPLE_RATE
            self.SAMPLE_WIDTH = mic.SAMPLE_WIDTH

    def init(self, fn):
        if not self.voice_trigger:
            self._init_keyboard_listeners()

        self.listening = True

        while self.listening:
            while self._keyboard_listening:
                print('Listening...')
                text = self._start_record()

                if not text:
                    self._init_keyboard_listeners()
                    break

                print(f"{text} - it's a good read, sending to prompt")
                fn(text)

                while self.audio_player.is_playing or len(self.audio_player.queue) > 0:
                    time.sleep(0.3)
                    print('still waiting')

                self._init_keyboard_listeners()

            time.sleep(0.05)

    def _init_keyboard_listeners(self):
        def onpress(key):
            try:
                if key == keyboard.Key.f20:
                    self._keyboard_listening = True
                    if self.saving_volume:
                        self.original_volume = self.volume_controller.GetMasterVolumeLevelScalar()
                        self.volume_controller.SetMasterVolumeLevelScalar(self.low_volume, None)
                        self.saving_volume = False
            except:
                pass

        def onrelease(key):
            try:
                if key == keyboard.Key.f20:
                    self._keyboard_listening = False
                    self.saving_volume = True
                    return False
            except:
                pass

        listener = keyboard.Listener(on_press=onpress, on_release=onrelease)
        listener.start()

    def _start_record(self, buffer_size=1024):

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=buffer_size)

        silence_start_time = None

        while self._keyboard_listening:
            audio_chunk = stream.read(1024)
            
            # Convert audio chunk to integers for volume analysis
            values = [int.from_bytes(audio_chunk[i:i+2], 'little', signed=True) for i in range(0, len(audio_chunk), 2)]

            # Check for silence
            if max(values) < 300: # Silence threshold
                if silence_start_time is None:
                    silence_start_time = time.time()
                elif time.time() - silence_start_time > 1.5: # Timeout time
                    print('silent detected')
                    if len(self.audio_chunks) >= 300:
                        self.data_to_queue()
            else:
                self.audio_chunks.append(audio_chunk)
                silence_start_time = None

        # Ensure to process data when stopped recording
        if len(self.audio_chunks) >= 20:
            self.data_to_queue()

        stream.stop_stream()
        stream.close()
        p.terminate()
        
        self.volume_controller.SetMasterVolumeLevelScalar(self.original_volume, None)
        temp_text = self.transcribed_text
        self.transcribed_text = ""
        return temp_text


    def whisper_transcribe(self):
        print("Received audio data, transcribing now.")
        self.whisper_thread_open = True

        audio_data = self.audio_data_queue.pop(0)
        
        # Create an AudioData object from the raw data
        audio_obj = sr.AudioData(audio_data, self.SAMPLE_RATE, self.SAMPLE_WIDTH)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            # Write WAV data to the temp file
            temp_file.write(audio_obj.get_wav_data())
            temp_path = temp_file.name

        with open(temp_path, "rb") as audio_file:
            # Ensure that the file is not empty
            if os.path.getsize(temp_path) > 0:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
            else:
                print("The audio file is empty.")

        os.remove(temp_path)
        self.transcribed_text += f" {transcript['text']}"
        print(transcript["text"])

        if len(self.audio_data_queue) > 0:
            self.whisper_transcribe()
        else: 
            self.whisper_thread_open = False

    def data_to_queue(self):
        print(len(self.audio_chunks))
        audio_data = b''.join(self.audio_chunks)
        self.audio_chunks.clear()
        self.audio_data_queue.append(audio_data)
        self.whisper_transcribe()

    

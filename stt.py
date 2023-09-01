from pynput import keyboard
import speech_recognition as sr
import pyaudio
import time
import os
import openai
import tempfile
import re


class VoiceInput():
    def __init__(self, audio_player, voice_trigger = False):
        self.voice_trigger = voice_trigger
        self.recognizer = sr.Recognizer()
        self._keyboard_listening = False
        self.audio_player = audio_player
        self.listening = True
    
    
    def init(self, fn):
        if not self.voice_trigger:
            self._init_keyboard_listeners()
            
        self.listening = True
        
        # waiting for key strokes
        while self.listening:
            
            while self._keyboard_listening:
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
    

    def _start_record(self, timeout=1000, phrase_time_limit=None, buffer=None):
        with sr.Microphone() as source:
            print("Please say something")
            try:
                # Capture audio from the microphone
                while self._keyboard_listening:
                    audio_data = self.recognizer.listen(source)

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

                # Ensure that transcripted text is valid
                # Failed transcript normally just contains '.' (dot) and spaces
                match = re.search(r'[a-zA-Z]', text)
                if not match:
                    return None
                
                
                if self.voice_trigger and ("abby" in text.lower() or "abbey" in text.lower()):
                    return text
                else:
                    return text
            except:
                print('Not a good read, try again')
                
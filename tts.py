from google.cloud import texttospeech
from datetime import datetime
import os
import threading
import wavio
import time




# abbey languge_code = en-US, name = en-US-Studio-O
# gemma language_code = fil-PH
class TextToSpeech():
    def __init__(self, text_queue, audio_player):
        self.text_queue = text_queue # per element is string to be converted
        self.is_converting = True
        # init client
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code= "en-US",
            name= "en-US-Studio-O"
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            pitch=0,
            speaking_rate=1
        )
        self.audio_player = audio_player
        
    def load_to_queue(self, text):
        print("loaded")
        self.text_queue.append(text)
        
    def end(self):
        self.is_converting = False
        
    def start(self):
        self.is_converting = True
        converting_thread = threading.Thread(target=self.converting)
        converting_thread.start()
        
    def converting(self):
        print('started converting')
        bigkas = 0
        while True:
            if len(self.text_queue) > 0:
                text = self.text_queue.pop(0)
                    
                input_text = texttospeech.SynthesisInput(
                    text=text
                )
                
                response = self.client.synthesize_speech(
                    input=input_text,
                    voice=self.voice,
                    audio_config=self.audio_config
                )
                
                
                self.audio_player.load_to_queue(response.audio_content)
                print('converted audio')
                    
            else:
                if not self.is_converting and len(self.text_queue) <= 0:
                    break
                
            time.sleep(0.1)
                
        print('ended converting')
        
    
    def _next_filename(self, directory, prefix="", extension=".txt"):
        # Get the list of existing files
        files = os.listdir(directory)
        
        # Find the next available number
        number = 1
        while True:
            filename = f"{prefix}{str(number).zfill(3)}{extension}"
            if filename not in files:
                break
            number += 1

        return os.path.join(directory, filename)
            

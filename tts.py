from google.cloud import texttospeech
from datetime import datetime
import os
import threading

# abbey languge_code = en-US, name = en-US-Studio-O
# gemma language_code = fil-PH
class TextToSpeech():
    def __init__(self, text_queue, audio_player):
        self.text_queue = text_queue # per element is string to be converted
        self.is_converting = False
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
        
    def convert(self, text, cb_play_audio):
        self.text_queue.append(text)
        if not self.is_converting:
            converting_thread = threading.Thread(target=self._converting, args=(cb_play_audio,))
            converting_thread.start()
        
    def _converting(self, cb_play_audio):
        self.is_converting = True
        text = self.text_queue.pop(0)
        
        if text == "__open_blackboard__":
            self.audio_player.load_to_queue("__open_blackboard__")
        
        else:  
            text = text.replace("`", "").replace("'", "").replace('"', "")

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
            cb_play_audio()
        
        if len(self.text_queue) > 0:
            self._converting(cb_play_audio)
            
        else:
            self.is_converting = False 
        
    
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


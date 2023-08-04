import os
from tts_and_player_interface import Interface
import re
import openai
import threading
from tts import TextToSpeech
from audioplayer import AudioPlayer
from dotenv import load_dotenv
load_dotenv()

class AbbeyAI():
    def __init__(self, text_queue, name, blackboard, audio_player, tts, model="gpt-3.5-turbo", stream=True):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.chat_completion = openai.ChatCompletion
        self.model = model
        self.stream = True
        self.text_queue = text_queue
        self.name = name
        self.blackboard = blackboard
        self.audio_player = audio_player
        self.tts =  tts
        
    '''    
    def prompt(self, prompt):
        self.busy = True
        prompt_thread = threading.Thread(target=self._prompt, args=(prompt,))
        prompt_thread.start()
    '''
        
        
    def prompt(self, prompt):
        if not prompt:
            return
        
        messages = [
            {
            "role": "system", "content": f"You are an assistant and your name is {self.name}. You answer with straight to the point. Format your response to readable by voice type, remember, I can only hear not see. Respoinse must be at least 3 sentences" 
            },
            {
                "role": "user", "content": prompt
            }
        ]
        response = self.chat_completion.create(
            messages=messages,
            model=self.model,
            stream=self.stream
        )
        
        self.tts.start()
        self.audio_player.listen()
        
        sentence = ""
        full_response = ""
        pattern = r"[a-zA-Z][.?!]$"
        for chunk in response:
            try:
                chunk_text = chunk["choices"][0]["delta"]["content"]
                full_response += chunk_text
                sentence += chunk_text
                match = re.search(pattern, sentence)
                
                if match:
                    self.text_queue.append(sentence)
                    print(sentence)
                    sentence = ""
            
            except:
                pass
            
        print("finished abbey")
        self.tts.end()
        self.audio_player.stop()
            


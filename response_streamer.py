from audioplayer import AudioPlayer
from tts import TextToSpeech
import traceback
import re
import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
import threading

class ResponseStreamer():
    def __init__(self, wrapper_parser, response, tts, audio_player):
        self.wrapper_parser = wrapper_parser
        self.response = response
        self.wrapper_parsing = False
        self.parsing_fn = None
        self.tts = tts
        self.audio_player = audio_player
        self.sentence_pattern = r'[\D]{2,}[!\.\?](?<!\!)'
        self.wrapper_tag = '@@@'
        self.parsing_tag = False
        self.parsing_openai_tag = False
        self.send_fn = wrapper_parser
        
    def start(self):

        sentence = ""
        full_message = ""
        parsing = False
        
        try:
            for chunk in self.response:
                chunk = chunk["choices"][0]["delta"]["content"]
                sentence += chunk
                full_message += chunk

                sentence_match = re.search(self.sentence_pattern, sentence)

                # Toggles parsing mode
                if chunk == "@@@":
                    parsing = not parsing
                    if sentence:
                        self.play_audio(sentence)
                        sentence = ""
                    continue

                elif parsing:
                    for fn in self.send_fn:
                        fn(chunk)
                        sentence = ""
                        continue

                elif sentence_match:
                    self.play_audio(sentence)
                    sentence = ""
                    continue
            

        except Exception as e:
            '''
            print(f"ERROR DUDE: {e}")
            print(f"ERROR TYPE: {type(e).__name__}")
            print("ERROR TRACEBACK:")
            traceback.print_tb(e.__traceback__)
            print(f"ERROR ARGS: {e.args}")
            '''
            print(f"SENTENCES ENDING {sentence}")
            if sentence:
                self.play_audio(sentence)
            
        return full_message
    

    def play_audio(self, text):
        self.tts.convert(text, self.audio_player.listen)

    

def quick_prompt_response(system_prompt, tone=True):
    quick_prompt_thread = threading.Thread(target=(_quick_prompt_respones), args=(system_prompt, tone))
    quick_prompt_thread.start()

def _quick_prompt_respones(system_prompt, tone=True):
    tts_queue = []
    text_queue = []

    tone_str = "You are an assistant named Summer. You answer with brief, succint and concise responses. Address me as 'boss' or 'sir' similar to Tony Stark's personal AI named Jarvis. "

    audio_player = AudioPlayer(tts_queue)
    converter = TextToSpeech(text_queue, audio_player)

    messages = []

    if tone:
        messages.append({
            "role": 'system', "content": tone_str
        })

    if isinstance(system_prompt, str):
        messages=[
            {"role": "system", "content": f"{system_prompt}"}
        ]
    
    elif isinstance(system_prompt, list):
        for prompt in system_prompt:
            messages.append(
                prompt
            )
     
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages,
        stream = True
    )
    sentence = ""
    full_message = ""
    for chunk in response:
        try:
            chunk = chunk["choices"][0]["delta"]["content"]
            sentence += chunk
            full_message += chunk
            
            sentence_match = re.search(r'[\D]{2,}[!\.\?](?<!\!)', sentence)
            if sentence_match:
                converter.convert(sentence, audio_player.listen)
                sentence = ""
        except:
            if sentence:
                converter.convert(sentence, audio_player.listen)
            print(full_message)
            pass



import os
from tts_and_player_interface import Interface
import re
import openai
import threading
from dynamic_memory import AIMemory
from tts import TextToSpeech
from audioplayer import AudioPlayer
from dotenv import load_dotenv
load_dotenv()

class AbbeyAI():
    def __init__(self, text_queue, name, blackboard, audio_player, tts, model="gpt-3.5-turbo-0613", stream=True):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.stream = True
        self.text_queue = text_queue
        self.name = name
        self.blackboard = blackboard
        self.audio_player = audio_player
        self.tts =  tts
        self.memory = AIMemory()
        self.personality = "You are my AI assistant name Abbey or Abby. You are classy, sassy, and loofy but intelligent"
        
        
    def prompt(self, prompt):
        if not prompt:
            return
        
        response_code = self._prompt_router(prompt)
        
        if response_code == "1":
            self._general_prompt(prompt)
        
        elif response_code == "2":
            self._function_prompt(prompt)
        
        else:
            print('Response code error')
    
    
    def _prompt_router(self, prompt):
        
        response = openai.ChatCompletion.create(
            temperature=0,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"respond with '2', if the prompt pertains about creating, deleting, reading, updating files such as notes, reminders, tasks, VS code, highlighted code in VS code, invoking command line. And '1' if it's about casual talks, orgeneral questions codes or file that does not file accessing or function calls. Response should only be either '1' or '2'. And this is the prompt, '{prompt}'" }
            ],
        )
        
        response_code = response["choices"][0]["message"]["content"]
        
        return response_code
            
            
    def _general_prompt(self, prompt):
            messages = [
            {
            "role": "system", "content": f"{self.personality} Format your response to readable by voice type, remember, I can only hear not see. Response must be at least 3 sentences" 
            },
            {
              "role": "system", "content": f"Your chat history: {self.memory.chat_history}"  
            },
            {
                "role": "user", "content": prompt
            }
            ]
        
        
            functions = [
                {
                    "name": "clear_history",
                    "description": "Clears chat history of AI assistant(you) and user.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
            
            response = openai.ChatCompletion.create(
                messages=messages,
                functions=functions,
                model=self.model,
                stream=True
            )
            self.tts.start()
            self.audio_player.listen()
            self.memory.add_chat_history("user", prompt)
            response_message = self._stream(response)
            self.memory.add_chat_history("assistant", response_message)
            self.audio_player.stop()
            self.tts.end()
            
    def _function_prompt(self, prompt):
        
        messages = [
            {"role": "system", "content": f"{self.personality} Format your response to readable by voice type, remember, I can only hear not see. Response must be at least 3 sentences"},
            {"role": "system", "content": "You have the access of my system files, personal data and you can run functions"},
            {"role": "system", "content": "If you need to call a function, only call the function that was provided."},
            {"role": "user", "content": prompt}
        ]
        
        functions = [
            {
                "name": "clear_history",
                "description": "clear or delete our chat (conversation) history.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = messages,
            functions = functions
        )
        
        print(response)
        
        response_message = response["choices"][0]["message"]
        
        # Check wether response is a function call
        if response_message.get("function_call"):
            
            available_fn = {
                "clear_history": self.memory.clear
            }
            
            fn_name = response_message["function_call"]["name"]
            fn = available_fn[fn_name]
            
            messages.append(response_message),
            messages.append({
                "role": "function",
                "name": fn_name,
                "content": fn()
            })
            
            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages = messages,
                stream=True
            )
            
            self.audio_player.listen()
            self.tts.start()
            self._stream(second_response)
            self.tts.end()
            self.audio_player.stop()
        
        
    def _stream(self, response):
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
        
        return full_response
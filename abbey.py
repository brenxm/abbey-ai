import os
import re
import openai
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
        self.personality = "You are my AI assistant name Abbey or Abby. You speak like a human being, an asshole, sassy, loofy but coherent, elaborates and straight to the point. Try to limit your response to few sentence as possible. You can also have the capabilities to access my personal data such as notes, reminders and task as well as my computer system. You can do task such as review code from VS code, make script, invoke a termnial prompt and etc. No need to end response with questions like 'If you need more questions, feel freet to ask.'"
        
        
    def prompt(self, prompt_input):
        '''
        Returns an object with properties
        stream: bool - if this is a streamed response else a full response
        content: chunk or full response - generated response from prompt call
        '''
        if not prompt_input:
            return
        
        response_code = self._prompt_router(prompt_input)
        
        if response_code == "1":
            return self._general_prompt(prompt_input)
        
        elif response_code == "2":
            return self._function_prompt(prompt_input)
        
        else:
            print('Response code error')
    
    
    def _prompt_router(self, prompt):
        
        response = openai.ChatCompletion.create(
            temperature=0,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"respond with '2', if the prompt pertains about creating, deleting, reading, updating files such as notes, reminders, tasks, VS code, highlighted code in VS code, invoking command line. And '1' if it's about casual talks, orgeneral questions codes or file that does not need a file accessing or calling any functions. Response should only be either '1' or '2'. And this is the prompt, '{prompt}'" }
            ],
        )
        
        response_code = response["choices"][0]["message"]["content"]
        
        return response_code
            
            
    def _general_prompt(self, prompt):
        '''
        Return the chunks of the stream
        '''
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
        
        return {
            "stream": True,
            "content": response
        }
        
            
    def _function_prompt(self, prompt):
        '''
        Executes a function then return the full response
        '''
        
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
            
            
            return {
                "stream": True,
                "content": second_response
            }
        
    def stream_result(self, response):
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
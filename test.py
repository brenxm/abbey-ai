from fn_module.vscode.vscode_module import get_vscode
from dotenv import load_dotenv
import json
import openai
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class PromptRequest():
    def __init__(self, model):
        self.model=model,
        self.messages = []
    
    def prompt(self, prompt):
        
        self.messages.append(
            {
                "role": "user", 
                "content": prompt
            }
        )
        
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages = self.messages,
            stream = True
        )
        
        return response
    
    def add_message(self, prompt_msg_obj):
        print(f'added:{prompt_msg_obj}')
        
        system_prompt = {
            "role": prompt_msg_obj["role"],
            "content": prompt_msg_obj["content"]
        }
        
        self.messages.append(system_prompt)
        
        
        
    def clear_message(self):
        self.messages = []